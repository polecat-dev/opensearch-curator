"""Convert Index to Remote Storage Action Class"""

import logging
import time
from curator.helpers.date_ops import parse_datemath, parse_date_pattern
from curator.helpers.getters import get_indices
from curator.helpers.testers import (
    repository_exists,
    snapshot_running,
    verify_index_list,
    verify_repository,
)
from curator.helpers.utils import report_failure, to_csv
from curator.helpers.waiters import wait_for_it
from curator.exceptions import (
    ActionError,
    FailedExecution,
    MissingArgument,
    SnapshotInProgress,
)

# pylint: disable=broad-except,too-many-instance-attributes,too-many-arguments,too-many-locals


class ConvertIndexToRemote:
    """
    Convert Index to Remote Storage Action Class

    This action converts existing local indices to remote-backed storage by:
    1. Creating/verifying a snapshot containing the index
    2. Restoring the index with remote_store settings
    3. Optionally creating an alias pointing to the new remote index
    4. Optionally deleting the old local index (with safety checks)

    Remote-backed storage in OpenSearch provides durability by automatically
    backing up segments and translogs to remote storage (S3, GCS, etc.).

    See: https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/
    """

    def __init__(
        self,
        ilo,
        repository=None,
        snapshot_name=None,
        use_existing_snapshot=False,
        snapshot_per_index=False,
        remote_store_repository=None,
        remote_index_suffix='_remote',
        create_alias=True,
        alias_name=None,
        delete_after=False,
        verify_availability=True,
        ignore_unavailable=False,
        partial=False,
        wait_for_completion=True,
        wait_interval=9,
        max_wait=-1,
        skip_repo_fs_check=True,
    ):
        """
        :param ilo: An IndexList Object containing indices to convert
        :param repository: Snapshot repository name for backup/restore operations
        :param snapshot_name: Name for the snapshot. Supports date math. If
            use_existing_snapshot=True, this should be an existing snapshot name.
            If snapshot_per_index=True, this is used as a prefix and the index
            name is appended (e.g., 'backup_' becomes 'backup_myindex').
        :param use_existing_snapshot: Use an existing snapshot instead of creating
            a new one. The snapshot must contain all indices in the IndexList.
        :param snapshot_per_index: Create a separate snapshot for each index,
            naming it using the snapshot_name as prefix and index name as suffix.
            (default: False - creates one snapshot with all indices)
        :param remote_store_repository: The remote store repository configured in
            the cluster (from node.attr.remote_store.segment.repository). If None,
            will attempt to use the same repository as snapshots.
        :param remote_index_suffix: Suffix to append to index names when creating
            the remote version (default: '_remote')
        :param create_alias: Create an alias with the original index name pointing
            to the new remote index (default: True)
        :param alias_name: Custom alias name. If None, uses original index name.
        :param delete_after: Delete the old local index after successful remote
            index creation and verification (default: False)
        :param verify_availability: Verify the remote index is available and has
            the same document count before deleting the old index (default: True)
        :param ignore_unavailable: Ignore unavailable shards/indices during snapshot
        :param partial: Allow partial snapshots/restores
        :param wait_for_completion: Wait for operations to complete before returning
        :param wait_interval: Seconds to wait between completion checks
        :param max_wait: Maximum seconds to wait_for_completion (-1 = no limit)
        :param skip_repo_fs_check: Skip repository filesystem validation

        :type ilo: :py:class:`~.curator.indexlist.IndexList`
        :type repository: str
        :type snapshot_name: str
        :type use_existing_snapshot: bool
        :type snapshot_per_index: bool
        :type remote_store_repository: str
        :type remote_index_suffix: str
        :type create_alias: bool
        :type alias_name: str
        :type delete_after: bool
        :type verify_availability: bool
        :type ignore_unavailable: bool
        :type partial: bool
        :type wait_for_completion: bool
        :type wait_interval: int
        :type max_wait: int
        :type skip_repo_fs_check: bool
        """
        verify_index_list(ilo)
        ilo.empty_list_check()

        if not repository:
            raise MissingArgument('No value for "repository" provided.')

        if not repository_exists(ilo.client, repository=repository):
            raise ActionError(
                f'Cannot use missing repository: {repository}. '
                f'Repository must exist and be registered with the cluster.'
            )

        if not snapshot_name:
            raise MissingArgument('No value for "snapshot_name" provided.')

        self.loggit = logging.getLogger('curator.actions.convert_index_to_remote')

        #: The IndexList object
        self.index_list = ilo
        #: The OpenSearch client
        self.client = ilo.client
        #: Snapshot repository name
        self.repository = repository
        #: Remote store repository (for remote-backed storage)
        self.remote_store_repository = remote_store_repository or repository
        #: Parsed snapshot name with date math rendered
        self.snapshot_name = parse_datemath(
            self.client, parse_date_pattern(snapshot_name)
        )
        #: Whether to use existing snapshot
        self.use_existing_snapshot = use_existing_snapshot
        #: Whether to create separate snapshot per index
        self.snapshot_per_index = snapshot_per_index
        #: Suffix for remote index names
        self.remote_index_suffix = remote_index_suffix
        #: Whether to create alias
        self.create_alias = create_alias
        #: Custom alias name
        self.alias_name = alias_name
        #: Whether to delete old index after conversion
        self.delete_after = delete_after
        #: Whether to verify availability before deletion
        self.verify_availability = verify_availability
        #: Ignore unavailable shards
        self.ignore_unavailable = ignore_unavailable
        #: Allow partial operations
        self.partial = partial
        #: Wait for completion
        self.wait_for_completion = wait_for_completion
        #: Wait interval in seconds
        self.wait_interval = wait_interval
        #: Maximum wait time
        self.max_wait = max_wait
        #: Skip repository FS check
        self.skip_repo_fs_check = skip_repo_fs_check

        # Internal state tracking
        self.snapshot_state = None
        self.remote_indices = {}  # Maps original_index -> remote_index
        self.created_aliases = {}  # Maps alias_name -> remote_index
        self.index_snapshots = (
            {}
        )  # Maps original_index -> snapshot_name (for snapshot_per_index)

        self.loggit.debug('ConvertIndexToRemote initialized')
        self.loggit.debug('Repository: %s', self.repository)
        self.loggit.debug('Remote store repository: %s', self.remote_store_repository)
        self.loggit.debug('Snapshot name: %s', self.snapshot_name)
        self.loggit.debug('Indices to convert: %s', ilo.indices)

    def _create_snapshot(self):
        """Create a snapshot of the indices if not using existing snapshot"""
        if self.use_existing_snapshot:
            self.loggit.info(
                'Using existing snapshot: %s from repository %s',
                self.snapshot_name,
                self.repository,
            )
            return self._verify_existing_snapshot()

        if not self.skip_repo_fs_check:
            verify_repository(self.client, self.repository)

        if snapshot_running(self.client):
            raise SnapshotInProgress(
                'Cannot create snapshot while another snapshot is in progress.'
            )

        if self.snapshot_per_index:
            return self._create_snapshots_per_index()
        else:
            return self._create_single_snapshot()

    def _create_single_snapshot(self):
        """Create a single snapshot containing all indices"""
        self.loggit.info(
            'Creating snapshot %s in repository %s',
            self.snapshot_name,
            self.repository,
        )

        # Map all indices to the same snapshot
        for index_name in self.index_list.indices:
            self.index_snapshots[index_name] = self.snapshot_name

        try:
            # OpenSearch-py 3.0 changed API: params moved to body dict, wait_for_completion to params
            self.client.snapshot.create(
                repository=self.repository,
                snapshot=self.snapshot_name,
                body={
                    'ignore_unavailable': self.ignore_unavailable,
                    'include_global_state': False,  # Don't need global state for index conversion
                    'indices': self.index_list.indices,
                    'partial': self.partial,
                },
                params={'wait_for_completion': 'false'},
            )

            if self.wait_for_completion:
                self.loggit.info('Waiting for snapshot to complete...')
                wait_for_it(
                    self.client,
                    'snapshot',
                    snapshot=self.snapshot_name,
                    repository=self.repository,
                    wait_interval=self.wait_interval,
                    max_wait=self.max_wait,
                )
                return self._get_snapshot_state()
            else:
                self.loggit.warning(
                    'wait_for_completion=False. Snapshot may not be ready. '
                    'Verify manually before proceeding.'
                )
                return None

        except Exception as err:
            self.loggit.error('Failed to create snapshot: %s', err)
            raise

    def _create_snapshots_per_index(self):
        """Create a separate snapshot for each index, named using the index name"""
        self.loggit.info(
            'Creating separate snapshots for %d indices in repository %s',
            len(self.index_list.indices),
            self.repository,
        )

        snapshot_results = []

        for index_name in self.index_list.indices:
            # Build snapshot name: prefix + index_name
            # If snapshot_name ends with a separator like '-' or '_', use it directly
            # Otherwise, add an underscore separator
            if self.snapshot_name.endswith(('-', '_')):
                index_snapshot_name = f'{self.snapshot_name}{index_name}'
            else:
                index_snapshot_name = f'{self.snapshot_name}_{index_name}'

            self.index_snapshots[index_name] = index_snapshot_name

            self.loggit.info(
                'Creating snapshot %s for index %s',
                index_snapshot_name,
                index_name,
            )

            try:
                # Wait for any running snapshot to complete before starting next
                if snapshot_running(self.client):
                    self.loggit.info('Waiting for previous snapshot to complete...')
                    # Simple wait loop for running snapshots
                    max_attempts = 60  # 10 minutes max
                    for _ in range(max_attempts):
                        if not snapshot_running(self.client):
                            break
                        time.sleep(10)
                    else:
                        raise SnapshotInProgress(
                            'Timed out waiting for previous snapshot to complete'
                        )

                self.client.snapshot.create(
                    repository=self.repository,
                    snapshot=index_snapshot_name,
                    body={
                        'ignore_unavailable': self.ignore_unavailable,
                        'include_global_state': False,
                        'indices': [index_name],
                        'partial': self.partial,
                    },
                    params={'wait_for_completion': 'false'},
                )

                if self.wait_for_completion:
                    self.loggit.info(
                        'Waiting for snapshot %s to complete...', index_snapshot_name
                    )
                    wait_for_it(
                        self.client,
                        'snapshot',
                        snapshot=index_snapshot_name,
                        repository=self.repository,
                        wait_interval=self.wait_interval,
                        max_wait=self.max_wait,
                    )

                    # Get and verify snapshot state
                    snapshot_info = self.client.snapshot.get(
                        repository=self.repository, snapshot=index_snapshot_name
                    )['snapshots'][0]

                    state = snapshot_info['state']
                    if state == 'SUCCESS':
                        self.loggit.info(
                            'Snapshot %s completed successfully', index_snapshot_name
                        )
                    elif state == 'PARTIAL' and self.partial:
                        self.loggit.warning(
                            'Snapshot %s is PARTIAL, continuing because partial=True',
                            index_snapshot_name,
                        )
                    else:
                        raise ActionError(
                            f'Snapshot {index_snapshot_name} failed with state: {state}'
                        )

                    snapshot_results.append(snapshot_info)

            except Exception as err:
                self.loggit.error(
                    'Failed to create snapshot for index %s: %s', index_name, err
                )
                raise

        self.loggit.info('Successfully created %d snapshots', len(self.index_snapshots))
        return snapshot_results

    def _verify_existing_snapshot(self):
        """Verify that existing snapshot contains all required indices"""
        try:
            snapshot_info = self.client.snapshot.get(
                repository=self.repository, snapshot=self.snapshot_name
            )['snapshots'][0]

            snapshot_indices = set(snapshot_info['indices'])
            required_indices = set(self.index_list.indices)

            missing = required_indices - snapshot_indices
            if missing:
                raise ActionError(
                    f'Snapshot {self.snapshot_name} does not contain all required '
                    f'indices. Missing: {missing}'
                )

            state = snapshot_info['state']
            if state != 'SUCCESS':
                if state == 'PARTIAL' and self.partial:
                    self.loggit.warning(
                        'Snapshot %s is in PARTIAL state. Proceeding anyway '
                        'because partial=True',
                        self.snapshot_name,
                    )
                else:
                    raise ActionError(
                        f'Snapshot {self.snapshot_name} is not in SUCCESS state. '
                        f'Current state: {state}'
                    )

            self.loggit.info(
                'Verified existing snapshot %s contains all required indices',
                self.snapshot_name,
            )

            # Map all indices to this snapshot
            for index_name in self.index_list.indices:
                self.index_snapshots[index_name] = self.snapshot_name

            return snapshot_info

        except Exception as err:
            self.loggit.error('Failed to verify existing snapshot: %s', err)
            raise

    def _get_snapshot_state(self):
        """Get the current state of the snapshot"""
        try:
            snapshot_info = self.client.snapshot.get(
                repository=self.repository, snapshot=self.snapshot_name
            )['snapshots'][0]

            self.snapshot_state = snapshot_info['state']
            self.loggit.debug(
                'Snapshot %s state: %s', self.snapshot_name, self.snapshot_state
            )

            if self.snapshot_state == 'SUCCESS':
                self.loggit.info(
                    'Snapshot %s completed successfully', self.snapshot_name
                )
            elif self.snapshot_state == 'FAILED':
                raise ActionError(f'Snapshot {self.snapshot_name} failed')
            else:
                self.loggit.warning(
                    'Snapshot %s in state: %s', self.snapshot_name, self.snapshot_state
                )

            return snapshot_info

        except Exception as err:
            self.loggit.error('Failed to get snapshot state: %s', err)
            raise

    def _restore_as_remote(self):
        """
        Restore indices from snapshot with remote_store configuration

        Uses the storage_type='remote_snapshot' parameter to tell OpenSearch
        to restore the index as a remote-backed index. The cluster must have
        remote repositories configured (segment and translog repositories).
        """
        if self.snapshot_per_index:
            self.loggit.info(
                'Restoring indices as remote-backed from individual snapshots'
            )
        else:
            self.loggit.info(
                'Restoring indices as remote-backed from snapshot %s',
                self.snapshot_name,
            )

        if not self.skip_repo_fs_check:
            verify_repository(self.client, self.repository)

        if snapshot_running(self.client):
            raise SnapshotInProgress('Cannot restore while a snapshot is in progress.')

        for original_index in self.index_list.indices:
            remote_index = f'{original_index}{self.remote_index_suffix}'
            self.remote_indices[original_index] = remote_index

            # Get the snapshot name for this index (may differ in snapshot_per_index mode)
            snapshot_for_index = self.index_snapshots.get(
                original_index, self.snapshot_name
            )

            self.loggit.info(
                'Restoring %s as remote index %s (from snapshot: %s)',
                original_index,
                remote_index,
                snapshot_for_index,
            )

            try:
                # Restore with rename pattern to create the remote version
                # OpenSearch-py 3.0 changed API: params go in body dict
                restore_body = {
                    'indices': [original_index],
                    'ignore_unavailable': self.ignore_unavailable,
                    'include_aliases': False,  # We'll create aliases separately
                    'include_global_state': False,
                    'partial': self.partial,
                    'rename_pattern': f'^{original_index}$',
                    'rename_replacement': remote_index,
                }

                # Add storage_type parameter if remote_store_repository is specified
                # This parameter REQUIRES a cluster with remote store enabled at creation time
                if self.remote_store_repository:
                    restore_body['storage_type'] = 'remote_snapshot'
                    self.loggit.debug(
                        'Using storage_type=remote_snapshot for remote-backed index'
                    )

                self.client.snapshot.restore(
                    repository=self.repository,
                    snapshot=snapshot_for_index,
                    body=restore_body,
                    params={'wait_for_completion': 'false'},
                )

                self.loggit.debug(
                    'Restore initiated for %s -> %s', original_index, remote_index
                )

            except Exception as err:
                self.loggit.error(
                    'Failed to restore %s as remote index: %s', original_index, err
                )
                raise

        if self.wait_for_completion:
            self.loggit.info('Waiting for restore to complete...')
            # Wait for all remote indices to be available
            wait_for_it(
                self.client,
                'restore',
                index_list=list(self.remote_indices.values()),
                wait_interval=self.wait_interval,
                max_wait=self.max_wait,
            )
            self._verify_remote_indices()
        else:
            self.loggit.warning(
                'wait_for_completion=False. Remote indices may not be ready. '
                'Verify manually before proceeding.'
            )

    def _verify_remote_indices(self):
        """Verify that remote indices were created successfully"""
        all_indices = get_indices(self.client)
        missing = []

        for original_index, remote_index in self.remote_indices.items():
            if remote_index not in all_indices:
                missing.append(remote_index)
                self.loggit.error('Remote index not found: %s', remote_index)
            else:
                self.loggit.info('Verified remote index exists: %s', remote_index)

                # Check document count if verify_availability is enabled
                if self.verify_availability:
                    self._verify_document_count(original_index, remote_index)

        if missing:
            raise FailedExecution(f'Failed to create remote indices: {missing}')

        self.loggit.info('All remote indices verified successfully')

    def _verify_document_count(self, original_index, remote_index):
        """Verify document count matches between original and remote index"""
        try:
            # Check if original index still exists
            all_indices = get_indices(self.client)
            if original_index not in all_indices:
                self.loggit.warning(
                    'Original index %s no longer exists, skipping document count check',
                    original_index,
                )
                return

            # Get document counts
            original_stats = self.client.indices.stats(
                index=original_index, params={'metric': 'docs'}
            )
            remote_stats = self.client.indices.stats(
                index=remote_index, params={'metric': 'docs'}
            )

            # Check if indices are in the response
            if original_index not in original_stats.get('indices', {}):
                self.loggit.warning(
                    'Original index %s not found in stats response, skipping count check',
                    original_index,
                )
                return

            if remote_index not in remote_stats.get('indices', {}):
                self.loggit.warning(
                    'Remote index %s not found in stats response (may have no allocated shards). '
                    'Skipping document count verification.',
                    remote_index,
                )
                return

            original_count = original_stats['indices'][original_index]['total']['docs'][
                'count'
            ]
            remote_count = remote_stats['indices'][remote_index]['total']['docs'][
                'count'
            ]

            if original_count != remote_count:
                raise ActionError(
                    f'Document count mismatch for {original_index}: '
                    f'original={original_count}, remote={remote_count}'
                )

            self.loggit.info(
                'Document count verified for %s: %s documents',
                original_index,
                original_count,
            )

        except Exception as err:
            self.loggit.error('Failed to verify document count: %s', err)
            raise

    def _create_aliases(self):
        """Create aliases pointing to the remote indices"""
        if not self.create_alias:
            self.loggit.debug('Alias creation disabled, skipping')
            return

        self.loggit.info('Creating aliases for remote indices')

        actions = []
        for original_index, remote_index in self.remote_indices.items():
            # Determine alias name
            if self.alias_name:
                # Use custom alias name (only works if converting single index)
                if len(self.remote_indices) > 1:
                    raise ActionError(
                        'Custom alias_name can only be used when converting a single index'
                    )
                alias = self.alias_name
            else:
                # Use original index name as alias
                alias = original_index

            # Check if alias or index with that name already exists
            all_indices = get_indices(self.client)
            if alias in all_indices:
                if alias == original_index and not self.delete_after:
                    self.loggit.warning(
                        'Cannot create alias %s because original index still exists. '
                        'Set delete_after=True to remove it.',
                        alias,
                    )
                    continue
                else:
                    self.loggit.warning(
                        'Index with name %s already exists, cannot create alias',
                        alias,
                    )
                    continue

            actions.append({'add': {'index': remote_index, 'alias': alias}})
            self.created_aliases[alias] = remote_index
            self.loggit.debug('Will create alias: %s -> %s', alias, remote_index)

        if actions:
            try:
                self.client.indices.update_aliases(body={'actions': actions})
                self.loggit.info('Created %s aliases', len(actions))
                for alias, index in self.created_aliases.items():
                    self.loggit.info('Alias created: %s -> %s', alias, index)
            except Exception as err:
                self.loggit.error('Failed to create aliases: %s', err)
                raise
        else:
            self.loggit.info('No aliases created')

    def _delete_old_indices(self):
        """Delete the original local indices after verification"""
        if not self.delete_after:
            self.loggit.debug('Index deletion disabled, skipping')
            return

        self.loggit.info('Deleting original local indices')

        # Final verification before deletion
        if self.verify_availability:
            self.loggit.info('Performing final verification before deletion')
            self._verify_remote_indices()

        # Build list of indices to delete
        to_delete = []
        for original_index in self.index_list.indices:
            all_indices = get_indices(self.client)
            if original_index in all_indices:
                to_delete.append(original_index)
            else:
                self.loggit.warning(
                    'Original index %s no longer exists, skipping deletion',
                    original_index,
                )

        if not to_delete:
            self.loggit.info('No indices to delete')
            return

        # Delete indices
        try:
            self.loggit.warning(
                'Deleting %s original indices: %s',
                len(to_delete),
                to_delete,
            )
            self.client.indices.delete(index=to_csv(to_delete))

            # Verify deletion
            time.sleep(2)  # Brief wait for deletion to propagate
            all_indices = get_indices(self.client)
            still_exists = [idx for idx in to_delete if idx in all_indices]

            if still_exists:
                raise FailedExecution(f'Failed to delete some indices: {still_exists}')

            self.loggit.info('Successfully deleted original indices: %s', to_delete)

        except Exception as err:
            self.loggit.error('Failed to delete old indices: %s', err)
            raise

    def do_dry_run(self):
        """Log what the output would be, but take no action"""
        self.loggit.info('DRY-RUN MODE. No changes will be made.')
        self.loggit.info('DRY-RUN: Would convert indices to remote storage:')
        self.loggit.info('  Repository: %s', self.repository)
        self.loggit.info('  Remote store repository: %s', self.remote_store_repository)
        self.loggit.info('  Snapshot name pattern: %s', self.snapshot_name)
        self.loggit.info('  Use existing snapshot: %s', self.use_existing_snapshot)
        self.loggit.info('  Snapshot per index: %s', self.snapshot_per_index)

        for original_index in self.index_list.indices:
            remote_index = f'{original_index}{self.remote_index_suffix}'

            # Compute snapshot name for this index
            if self.snapshot_per_index:
                if self.snapshot_name.endswith(('-', '_')):
                    snapshot_for_index = f'{self.snapshot_name}{original_index}'
                else:
                    snapshot_for_index = f'{self.snapshot_name}_{original_index}'
            else:
                snapshot_for_index = self.snapshot_name

            self.loggit.info(
                'DRY-RUN: %s -> %s (snapshot: %s)',
                original_index,
                remote_index,
                snapshot_for_index,
            )

            if self.create_alias:
                alias = self.alias_name or original_index
                self.loggit.info('  Would create alias: %s -> %s', alias, remote_index)

            if self.delete_after:
                self.loggit.info('  Would delete original index: %s', original_index)

    def do_action(self):
        """
        Execute the full remote index conversion process:
        1. Create/verify snapshot
        2. Restore as remote indices
        3. Create aliases (optional)
        4. Delete old indices (optional, with verification)
        """
        self.loggit.info(
            'Starting conversion of %s indices to remote storage',
            len(self.index_list.indices),
        )

        try:
            # Step 1: Create or verify snapshot
            self.loggit.info('Step 1/4: Creating/verifying snapshot')
            self._create_snapshot()

            # Step 2: Restore as remote indices
            self.loggit.info('Step 2/4: Restoring indices with remote storage')
            self._restore_as_remote()

            # Step 3: Create aliases
            self.loggit.info('Step 3/4: Creating aliases')
            self._create_aliases()

            # Step 4: Delete old indices (optional)
            if self.delete_after:
                self.loggit.info('Step 4/4: Deleting original indices')
                self._delete_old_indices()
            else:
                self.loggit.info('Step 4/4: Skipping deletion (delete_after=False)')

            self.loggit.info(
                'Successfully converted %s indices to remote storage',
                len(self.remote_indices),
            )

            # Report final status
            for original_index, remote_index in self.remote_indices.items():
                alias = self.created_aliases.get(
                    self.alias_name or original_index, '(none)'
                )
                status = 'deleted' if self.delete_after else 'retained'
                self.loggit.info(
                    'Conversion complete: %s -> %s (alias: %s, original: %s)',
                    original_index,
                    remote_index,
                    alias,
                    status,
                )

        except Exception as err:
            self.loggit.error('Failed to convert indices to remote storage: %s', err)
            report_failure(err)
