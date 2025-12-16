"""Forcemerge action class"""

import logging
from time import sleep

# pylint: disable=import-error
from curator.exceptions import MissingArgument
from curator.helpers.testers import verify_index_list
from curator.helpers.tasks import (
    get_conflicting_indices,
    get_tasks_for_action,
    format_running_tasks,
)
from curator.helpers.utils import report_failure, show_dry_run


def _batch_indices(indices, batch_size):
    """
    Split a list of indices into batches of the specified size.

    :param indices: List of index names
    :param batch_size: Maximum number of indices per batch

    :type indices: list
    :type batch_size: int

    :returns: Generator yielding lists of indices
    :rtype: generator
    """
    for i in range(0, len(indices), batch_size):
        yield indices[i:i + batch_size]


class ForceMerge:
    """ForceMerge Action Class"""

    def __init__(
        self,
        ilo,
        max_num_segments=None,
        delay=0,
        batch_size=None,
        skip_if_running=False,
        wait_for_completion=True,
        wait_interval=9,
        max_wait=-1,
    ):
        """
        :param ilo: An IndexList Object
        :param max_num_segments: Number of segments per shard to forceMerge
        :param delay: Number of seconds to delay between forceMerge operations
        :param batch_size: Number of indices to process per forcemerge request.
            If None, indices are processed one at a time (default behavior).
            Setting this groups indices into batches for more efficient processing,
            but may cause issues on some OpenSearch versions with large batches.
        :param skip_if_running: If True, check for running forcemerge tasks and
            skip indices that already have forcemerge operations in progress.
        :param wait_for_completion: Wait for the forcemerge operation to complete
            before returning. If False, the forcemerge will run asynchronously
            and return a task_id immediately.
        :param wait_interval: Seconds to wait between completion checks when
            ``wait_for_completion`` is True.
        :param max_wait: Maximum number of seconds to wait for completion. A value
            of ``-1`` means wait indefinitely.

        :type ilo: :py:class:`~.curator.indexlist.IndexList`
        :type max_num_segments: int
        :type delay: int
        :type batch_size: int
        :type skip_if_running: bool
        :type wait_for_completion: bool
        :type wait_interval: int
        :type max_wait: int
        """
        verify_index_list(ilo)
        if not max_num_segments:
            raise MissingArgument('Missing value for "max_num_segments"')
        #: The :py:class:`~.curator.indexlist.IndexList` object passed from
        #: param ``ilo``
        self.index_list = ilo
        #: The :py:class:`~.opensearchpy.OpenSearch` client object derived from
        #: :py:attr:`index_list`
        self.client = ilo.client
        #: Object attribute that gets the value of param ``max_num_segments``.
        self.max_num_segments = max_num_segments
        #: Object attribute that gets the value of param ``delay``.
        self.delay = delay
        #: Object attribute that gets the value of param ``batch_size``.
        self.batch_size = batch_size
        #: Object attribute that gets the value of param ``skip_if_running``.
        self.skip_if_running = skip_if_running
        #: Object attribute that gets the value of param ``wait_for_completion``.
        self.wfc = wait_for_completion
        #: Object attribute that gets the value of param ``wait_interval``.
        self.wait_interval = wait_interval
        #: Object attribute that gets the value of param ``max_wait``.
        self.max_wait = max_wait
        self.loggit = logging.getLogger('curator.actions.forcemerge')

    def _filter_running_tasks(self):
        """
        Filter out indices that already have forcemerge tasks running.
        
        Returns the list of indices that were skipped due to running tasks.
        """
        if not self.skip_if_running:
            return []

        self.loggit.info('Checking for running forcemerge tasks...')
        
        # First check if any forcemerge tasks are running at all
        running_tasks = get_tasks_for_action(self.client, 'forcemerge')
        
        if not running_tasks:
            self.loggit.info('No running forcemerge tasks found.')
            return []

        self.loggit.info(
            'Found %d running forcemerge task(s):\n%s',
            len(running_tasks),
            format_running_tasks(running_tasks)
        )

        # Find which of our target indices have running tasks
        conflicting = get_conflicting_indices(
            self.client, 'forcemerge', self.index_list.indices
        )

        if conflicting:
            self.loggit.warning(
                'Skipping %d indices with running forcemerge tasks: %s',
                len(conflicting),
                sorted(conflicting)
            )
            # Remove conflicting indices from the list
            for idx in conflicting:
                if idx in self.index_list.indices:
                    self.index_list.indices.remove(idx)

        return list(conflicting)

    def do_dry_run(self):
        """Log what the output would be, but take no action."""
        show_dry_run(
            self.index_list,
            'forcemerge',
            max_num_segments=self.max_num_segments,
            delay=self.delay,
            batch_size=self.batch_size,
            skip_if_running=self.skip_if_running,
            wait_for_completion=self.wfc,
            wait_interval=self.wait_interval,
            max_wait=self.max_wait,
        )

    def _do_forcemerge(self, indices):
        """
        Execute forcemerge operation for the given indices.

        :param indices: Comma-separated string of index names or a single index name
        :type indices: str
        :returns: task_id if wait_for_completion is False, None otherwise
        :rtype: str or None
        """
        # Use wait_for_completion=False to get task_id for async operations
        # The OpenSearch forcemerge API returns a task object when wait_for_completion=False
        response = self.client.indices.forcemerge(
            index=indices,
            max_num_segments=self.max_num_segments,
            wait_for_completion=self.wfc,
        )

        if not self.wfc:
            # When wait_for_completion=False, response contains task info
            # Response format: {'task': 'node_id:task_id'}
            task_id = response.get('task')
            if task_id:
                self.loggit.info(
                    'ForceMerge task started with task_id: %s. '
                    'Use the Tasks API to check status.', task_id
                )
            return task_id
        return None

    def do_action(self):
        """
        :py:meth:`~.opensearchpy.client.IndicesClient.forcemerge` indices in
        :py:attr:`index_list`

        If :py:attr:`batch_size` is set, indices are processed in batches.
        Otherwise, indices are processed one at a time (default behavior).

        If :py:attr:`skip_if_running` is True, indices with already running
        forcemerge tasks will be filtered out before processing.

        If :py:attr:`wfc` (wait_for_completion) is False, the forcemerge will
        run asynchronously and task_ids will be logged for each operation.
        """
        self.index_list.filter_closed()
        self.index_list.filter_forceMerged(max_num_segments=self.max_num_segments)

        # Check for running tasks and filter out conflicting indices
        skipped_indices = self._filter_running_tasks()

        self.index_list.empty_list_check()
        msg = (
            f'forceMerging {len(self.index_list.indices)} '
            f'selected indices: {self.index_list.indices}'
        )
        if skipped_indices:
            msg += f' (skipped {len(skipped_indices)} indices with running tasks)'
        if not self.wfc:
            msg += ' (async mode - will not wait for completion)'
        self.loggit.info(msg)

        task_ids = []
        try:
            if self.batch_size:
                # Process indices in batches
                index_batches = list(_batch_indices(
                    self.index_list.indices,
                    self.batch_size
                ))
                total_batches = len(index_batches)
                for batch_num, batch in enumerate(index_batches, 1):
                    msg = (
                        f'forceMerging batch {batch_num}/{total_batches} '
                        f'({len(batch)} indices) to {self.max_num_segments} '
                        f'segments per shard.'
                    )
                    if self.wfc:
                        msg += ' Please wait...'
                    self.loggit.info(msg)
                    self.loggit.debug('Batch %s indices: %s', batch_num, batch)

                    task_id = self._do_forcemerge(','.join(batch))
                    if task_id:
                        task_ids.append(task_id)

                    # Apply delay between batches, but not after the last one
                    if self.delay > 0 and batch_num < total_batches:
                        self.loggit.info(
                            'Pausing for %s seconds before next batch...', self.delay
                        )
                        sleep(self.delay)
            else:
                # Default behavior: process indices one at a time
                for index_name in self.index_list.indices:
                    msg = (
                        f'forceMerging index {index_name} to {self.max_num_segments} '
                        f'segments per shard.'
                    )
                    if self.wfc:
                        msg += ' Please wait...'
                    self.loggit.info(msg)

                    task_id = self._do_forcemerge(index_name)
                    if task_id:
                        task_ids.append(task_id)

                    if self.delay > 0:
                        self.loggit.info(
                            'Pausing for %s seconds before continuing...', self.delay
                        )
                        sleep(self.delay)

            # Log summary of async tasks if any
            if task_ids:
                self.loggit.info(
                    'Started %d async forcemerge task(s). Task IDs: %s',
                    len(task_ids), task_ids
                )
        # pylint: disable=broad-except
        except Exception as err:
            report_failure(err)
