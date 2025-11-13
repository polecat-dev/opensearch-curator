# Convert Index to Remote Storage Action

## Overview

The `convert_index_to_remote` action converts existing local OpenSearch indices to **remote-backed storage**. Remote-backed storage automatically backs up index segments and translogs to remote repositories (S3, GCS, Azure Blob Storage, etc.), providing enhanced durability and disaster recovery capabilities.

**Added in:** OpenSearch Curator 1.0 (OpenSearch 3.x compatible)

## Requirements

### Cluster Configuration

Your OpenSearch cluster **must** be configured with remote store repositories before using this action:

```yaml
# In opensearch.yml on all nodes:
node.attr.remote_store.segment.repository: my-segment-repo
node.attr.remote_store.translog.repository: my-translog-repo

# Segment repository configuration
node.attr.remote_store.repository.my-segment-repo.type: s3
node.attr.remote_store.repository.my-segment-repo.settings.bucket: my-bucket
node.attr.remote_store.repository.my-segment-repo.settings.base_path: segments/
node.attr.remote_store.repository.my-segment-repo.settings.region: us-east-1

# Translog repository configuration
node.attr.remote_store.repository.my-translog-repo.type: s3
node.attr.remote_store.repository.my-translog-repo.settings.bucket: my-bucket
node.attr.remote_store.repository.my-translog-repo.settings.base_path: translogs/
node.attr.remote_store.repository.my-translog-repo.settings.region: us-east-1
```

See [OpenSearch Remote Store Documentation](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/) for detailed setup instructions.

### Prerequisites

1. **OpenSearch 2.15+** (remote store migration support)
2. **Snapshot repository** registered and accessible
3. **Remote store repositories** configured on all nodes
4. **Sufficient storage** in remote repositories
5. **Network connectivity** to remote storage backends

## How It Works

The action performs a **four-step conversion process**:

### Step 1: Create/Verify Snapshot

- **New Snapshot**: Creates a snapshot containing all selected indices
- **Existing Snapshot**: Verifies an existing snapshot contains required indices
- Ensures data is safely backed up before conversion

### Step 2: Restore as Remote Indices

- Restores indices from snapshot with remote storage configuration
- Indices are renamed with a suffix (default: `_remote`)
- OpenSearch automatically applies remote store settings to restored indices

### Step 3: Create Aliases (Optional)

- Creates aliases with original index names pointing to remote indices
- Enables seamless application cutover (no code changes needed)
- Can use custom alias names for single-index conversions

### Step 4: Delete Original Indices (Optional)

- Deletes old local indices after verification
- Includes safety checks:
  - Verifies remote indices exist
  - Compares document counts
  - Ensures aliases are created (if enabled)
- **Disabled by default** - must explicitly enable with `delete_after: True`

## Configuration Options

### Required Options

| Option | Type | Description |
|--------|------|-------------|
| `repository` | string | Snapshot repository name (must be registered) |
| `snapshot_name` | string | Snapshot name (supports date math like `%Y%m%d`) |

### Snapshot Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `use_existing_snapshot` | boolean | `False` | Use existing snapshot instead of creating new one |
| `ignore_unavailable` | boolean | `False` | Ignore unavailable shards/indices |
| `partial` | boolean | `False` | Allow partial snapshots/restores |
| `wait_for_completion` | boolean | `True` | Wait for operations to complete |
| `wait_interval` | integer | `9` | Seconds between completion checks |
| `max_wait` | integer | `-1` | Max seconds to wait (-1 = no limit) |
| `skip_repo_fs_check` | boolean | `False` | Skip repository filesystem validation |

### Remote Storage Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `remote_store_repository` | string | (same as `repository`) | Remote store repo name |
| `remote_index_suffix` | string | `_remote` | Suffix appended to index names |

### Alias Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `create_alias` | boolean | `True` | Create aliases with original index names |
| `alias_name` | string | (original index name) | Custom alias name (single index only) |

### Deletion Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `delete_after` | boolean | `False` | Delete original indices after conversion |
| `verify_availability` | boolean | `True` | Verify remote indices before deletion |

## Usage Examples

### Example 1: Safe Conversion (No Deletion)

Convert indices to remote storage but keep originals:

```yaml
actions:
  1:
    action: convert_index_to_remote
    description: Safe conversion - keep originals for comparison
    options:
      repository: my-repo
      snapshot_name: 'conversion-%Y%m%d'
      remote_index_suffix: '_remote'
      create_alias: False  # Avoid alias conflicts
      delete_after: False  # Keep originals
      wait_for_completion: True
      disable_action: False
    filters:
    - filtertype: pattern
      kind: prefix
      value: logs-
```

**Result:**
- Original: `logs-2024-01-15` (unchanged)
- Remote: `logs-2024-01-15_remote` (new)

### Example 2: Full Conversion with Aliases

Convert with seamless cutover using aliases:

```yaml
actions:
  1:
    action: convert_index_to_remote
    description: Full conversion with aliases
    options:
      repository: my-repo
      snapshot_name: 'migration-%Y%m%d'
      remote_index_suffix: '_remote'
      create_alias: True  # Create aliases
      delete_after: True  # Delete after verification
      verify_availability: True
      wait_for_completion: True
      disable_action: False
    filters:
    - filtertype: pattern
      kind: prefix
      value: logs-
```

**Result:**
- Original: `logs-2024-01-15` → **DELETED**
- Remote: `logs-2024-01-15_remote`
- Alias: `logs-2024-01-15` → `logs-2024-01-15_remote`

Applications continue using `logs-2024-01-15` transparently!

### Example 3: Use Existing Snapshot

Convert using an existing backup:

```yaml
actions:
  1:
    action: convert_index_to_remote
    description: Use existing snapshot
    options:
      repository: my-repo
      snapshot_name: 'backup-2024-01-15'
      use_existing_snapshot: True  # Don't create new snapshot
      remote_index_suffix: '_remote'
      create_alias: True
      delete_after: False
      disable_action: False
    filters:
    - filtertype: pattern
      kind: exact
      value: important-index
```

### Example 4: Production Migration

Full production conversion with all safety features:

```yaml
actions:
  1:
    action: convert_index_to_remote
    description: Production migration with safety checks
    options:
      repository: prod-snapshot-repo
      snapshot_name: 'prod-migration-%Y%m%d-%H%M'
      use_existing_snapshot: False
      remote_index_suffix: '_remote'
      create_alias: True
      delete_after: True  # Enable after testing!
      verify_availability: True  # Always verify
      ignore_unavailable: False  # Fail on any issue
      partial: False  # Require complete operations
      wait_for_completion: True
      wait_interval: 15
      max_wait: 3600  # 1 hour timeout
      skip_repo_fs_check: False
      disable_action: False
    filters:
    - filtertype: age
      source: creation_date
      direction: older
      unit: days
      unit_count: 30
```

## CLI Usage

The action is also available via `curator_cli`:

```bash
curator_cli --host localhost:9200 convert_index_to_remote \
    --repository my-repo \
    --snapshot_name 'conversion-%Y%m%d' \
    --remote_index_suffix _remote \
    --create_alias \
    --delete_after \
    --verify_availability \
    --filter_list '[
        {"filtertype":"pattern","kind":"prefix","value":"logs-"},
        {"filtertype":"age","source":"creation_date","direction":"older","unit":"days","unit_count":7}
    ]'
```

## Safety Considerations

### ⚠️ IMPORTANT: Test Before Production

1. **Test on Non-Production Cluster First**
   - Validate the conversion process
   - Verify performance characteristics
   - Ensure applications work with remote indices

2. **Start Without Deletion**
   - Set `delete_after: False` initially
   - Manually verify remote indices
   - Test application functionality
   - Only enable deletion after successful validation

3. **Enable All Safety Checks**
   - Keep `verify_availability: True`
   - Set `ignore_unavailable: False`
   - Set `partial: False`
   - Use `wait_for_completion: True`

### Verification Steps

The action automatically performs these checks when `verify_availability: True`:

1. ✅ Remote index exists in cluster
2. ✅ Document count matches original index
3. ✅ Index is available (green/yellow status)
4. ✅ Aliases created successfully (if enabled)

**Only after ALL checks pass** will it delete the original index.

### Rollback Procedure

If issues occur, you can restore from the snapshot:

```yaml
actions:
  1:
    action: restore
    description: Rollback conversion
    options:
      repository: my-repo
      snapshot: 'conversion-2024-01-15'
      rename_pattern: '(.+)_remote'
      rename_replacement: '$1'
      wait_for_completion: True
    filters:
    - filtertype: pattern
      kind: suffix
      value: _remote
```

## Performance Considerations

### Snapshot Creation Time

- **Duration**: Depends on index size and network speed to remote storage
- **Impact**: Minimal (incremental snapshots are fast)
- **Tip**: Use `use_existing_snapshot: True` if you have recent backups

### Restore Time

- **Duration**: Depends on index size and remote storage I/O
- **Impact**: Indices unavailable during restore
- **Tip**: Process indices in batches during maintenance windows

### Storage Requirements

- **Snapshot Storage**: Full index size (compressed)
- **Remote Store**: Ongoing storage for segments/translogs
- **Tip**: Monitor remote storage costs and usage

### Network Bandwidth

- **Upload**: During snapshot creation
- **Download**: During restore
- **Ongoing**: Segment/translog uploads during indexing

## Troubleshooting

### "Repository not found"

**Cause**: Snapshot repository not registered

**Solution**:
```bash
# Register repository
curl -X PUT "localhost:9200/_snapshot/my-repo" -H 'Content-Type: application/json' -d'
{
  "type": "s3",
  "settings": {
    "bucket": "my-bucket",
    "region": "us-east-1"
  }
}'
```

### "Remote store not configured"

**Cause**: Cluster nodes don't have remote store repositories configured

**Solution**: Add remote store configuration to `opensearch.yml` and restart nodes

### "Document count mismatch"

**Cause**: Index modified during conversion, or restore incomplete

**Solution**:
- Ensure no writes during conversion (close index first)
- Set `wait_for_completion: True`
- Check OpenSearch logs for restore errors

### "Cannot create alias - index exists"

**Cause**: Original index still exists and conflicts with alias name

**Solution**:
- Set `delete_after: True` to remove originals
- Use `create_alias: False` to skip alias creation
- Manually delete original indices

## Advanced Usage

### Batch Processing

Process indices in groups to manage resource usage:

```yaml
actions:
  1:
    action: convert_index_to_remote
    description: Convert week 1 indices
    options:
      repository: my-repo
      snapshot_name: 'batch1-%Y%m%d'
      # ... other options ...
    filters:
    - filtertype: age
      source: creation_date
      direction: older
      unit: days
      unit_count: 7
    - filtertype: age
      source: creation_date
      direction: younger
      unit: days
      unit_count: 14

  2:
    action: convert_index_to_remote
    description: Convert week 2 indices
    options:
      repository: my-repo
      snapshot_name: 'batch2-%Y%m%d'
      # ... other options ...
    filters:
    - filtertype: age
      source: creation_date
      direction: older
      unit: days
      unit_count: 14
    - filtertype: age
      source: creation_date
      direction: younger
      unit: days
      unit_count: 21
```

### Custom Alias Names

For single-index conversions, use custom alias:

```yaml
actions:
  1:
    action: convert_index_to_remote
    description: Convert with custom alias
    options:
      repository: my-repo
      snapshot_name: 'custom-conversion'
      alias_name: 'production-index'  # Custom alias
      # ... other options ...
    filters:
    - filtertype: pattern
      kind: exact
      value: old-index-name
```

### Integration with Other Actions

Combine with other curator actions for complete workflows:

```yaml
actions:
  1:
    action: close
    description: Close indices before conversion
    # Prevents writes during conversion
    
  2:
    action: convert_index_to_remote
    description: Convert closed indices
    
  3:
    action: open
    description: Open remote indices (if needed)
```

## Monitoring

### Check Snapshot Status

```bash
curl -X GET "localhost:9200/_snapshot/my-repo/conversion-*/_status"
```

### Check Restore Status

```bash
curl -X GET "localhost:9200/_recovery?human&active_only=true"
```

### Verify Remote Index Configuration

```bash
curl -X GET "localhost:9200/logs-2024-01-15_remote/_settings?pretty"
```

## Related Actions

- **`snapshot`** - Create snapshots manually
- **`restore`** - Restore from snapshots
- **`alias`** - Manage index aliases
- **`delete_indices`** - Delete indices manually

## See Also

- [OpenSearch Remote Store Documentation](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/)
- [Migrating to Remote Storage](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/remote-store/migrating-to-remote/)
- [Snapshot and Restore](https://opensearch.org/docs/latest/opensearch/snapshots/snapshot-restore/)
- [Index Aliases](https://opensearch.org/docs/latest/opensearch/index-alias/)

## Version History

- **1.0.0** - Initial implementation for OpenSearch 3.x
  - Support for remote-backed storage conversion
  - Safe deletion with verification
  - Alias creation for seamless cutover
  - CLI and YAML configuration support
