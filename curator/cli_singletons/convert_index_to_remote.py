"""Convert Index To Remote Storage Singleton"""

import click
from curator.cli_singletons.object_class import CLIAction
from curator.cli_singletons.utils import validate_filter_json


# pylint: disable=line-too-long,too-many-arguments
@click.command()
@click.option(
    '--search_pattern', type=str, default='*', help='OpenSearch Index Search Pattern'
)
@click.option(
    '--repository',
    type=str,
    required=True,
    help='Snapshot repository for backup/restore operations',
)
@click.option(
    '--snapshot_name',
    type=str,
    help='Snapshot name (supports date math)',
    show_default=True,
    default='curator-remote-conversion-%Y%m%d%H%M%S',
)
@click.option(
    '--use_existing_snapshot',
    is_flag=True,
    show_default=True,
    help='Use existing snapshot instead of creating new one',
)
@click.option(
    '--remote_store_repository',
    type=str,
    help='Remote store repository name. If not specified, uses same as --repository',
)
@click.option(
    '--remote_index_suffix',
    type=str,
    default='_remote',
    show_default=True,
    help='Suffix to append to index names for remote versions',
)
@click.option(
    '--create_alias/--no-create_alias',
    default=True,
    show_default=True,
    help='Create alias with original index name pointing to remote index',
)
@click.option(
    '--alias_name',
    type=str,
    help='Custom alias name (only for single index conversion)',
)
@click.option(
    '--delete_after/--no-delete_after',
    default=False,
    show_default=True,
    help='Delete original local index after successful remote conversion',
)
@click.option(
    '--verify_availability/--no-verify_availability',
    default=True,
    show_default=True,
    help='Verify remote index availability and document count before deletion',
)
@click.option(
    '--ignore_unavailable',
    is_flag=True,
    show_default=True,
    help='Ignore unavailable shards/indices during snapshot/restore',
)
@click.option(
    '--partial',
    is_flag=True,
    show_default=True,
    help='Allow partial snapshots/restores',
)
@click.option(
    '--wait_for_completion/--no-wait_for_completion',
    default=True,
    show_default=True,
    help='Wait for snapshot and restore operations to complete',
)
@click.option(
    '--wait_interval',
    default=9,
    type=int,
    show_default=True,
    help='Seconds to wait between completion checks',
)
@click.option(
    '--max_wait',
    default=-1,
    type=int,
    show_default=True,
    help='Maximum seconds to wait for completion (-1 = no limit)',
)
@click.option(
    '--skip_repo_fs_check',
    is_flag=True,
    show_default=True,
    help='Skip repository filesystem access validation',
)
@click.option(
    '--ignore_empty_list',
    is_flag=True,
    help='Do not raise exception if there are no actionable indices',
)
@click.option(
    '--allow_ilm_indices/--no-allow_ilm_indices',
    help='Allow Curator to operate on Index Lifecycle Management monitored indices',
    default=False,
    show_default=True,
)
@click.option(
    '--include_hidden/--no-include_hidden',
    help='Allow Curator to operate on hidden indices (and data_streams)',
    default=False,
    show_default=True,
)
@click.option(
    '--filter_list',
    callback=validate_filter_json,
    help='JSON array of filters selecting indices to convert',
    required=True,
)
@click.pass_context
def convert_index_to_remote(
    ctx,
    search_pattern,
    repository,
    snapshot_name,
    use_existing_snapshot,
    remote_store_repository,
    remote_index_suffix,
    create_alias,
    alias_name,
    delete_after,
    verify_availability,
    ignore_unavailable,
    partial,
    wait_for_completion,
    wait_interval,
    max_wait,
    skip_repo_fs_check,
    ignore_empty_list,
    allow_ilm_indices,
    include_hidden,
    filter_list,
):
    """
    Convert local indices to remote-backed storage.

    This command performs the following steps:

    1. Creates or uses an existing snapshot of the selected indices

    2. Restores the indices with storage_type='remote_snapshot' to enable
       remote-backed storage (requires cluster with remote repositories configured)

    3. Optionally creates aliases pointing to the new remote indices

    4. Optionally deletes the original local indices (with safety checks)

    Remote-backed storage provides durability by automatically backing up
    segments and translogs to remote storage (S3, GCS, Azure Blob, etc.).

    Example:

        curator_cli --host localhost:9200 convert_index_to_remote \\
            --repository my-repo \\
            --remote_index_suffix _remote \\
            --create_alias \\
            --delete_after \\
            --filter_list '[{"filtertype":"pattern","kind":"prefix","value":"logs-"}]'

    This will:
    - Find all indices matching "logs-*"
    - Create snapshot in "my-repo"
    - Restore as "logs-*_remote" with remote storage
    - Create alias "logs-*" pointing to "logs-*_remote"
    - Delete original "logs-*" indices after verification

    See: https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/
    """
    manual_options = {
        'repository': repository,
        'snapshot_name': snapshot_name,
        'use_existing_snapshot': use_existing_snapshot,
        'remote_store_repository': remote_store_repository,
        'remote_index_suffix': remote_index_suffix,
        'create_alias': create_alias,
        'alias_name': alias_name,
        'delete_after': delete_after,
        'verify_availability': verify_availability,
        'ignore_unavailable': ignore_unavailable,
        'partial': partial,
        'wait_for_completion': wait_for_completion,
        'wait_interval': wait_interval,
        'max_wait': max_wait,
        'skip_repo_fs_check': skip_repo_fs_check,
        'ignore_empty_list': ignore_empty_list,
        'allow_ilm_indices': allow_ilm_indices,
    }

    # Invoke command with proper action name
    action = CLIAction(
        'convert_index_to_remote',
        ctx.obj['config']['client'],
        manual_options,
        filter_list,
        search_pattern,
        include_hidden=include_hidden,
    )
    action.do_singleton_action(dry_run=ctx.obj['dry_run'])
