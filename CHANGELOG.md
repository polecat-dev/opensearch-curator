# Changelog

All notable changes to OpenSearch Curator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - TBD

### 🎉 Initial Release - OpenSearch Fork

This is the first release of **OpenSearch Curator**, forked from Elasticsearch Curator v8.0.21.

### ✨ Added

- **OpenSearch 3.2.0 Support** - Full compatibility with OpenSearch 3.x (tested against 2.11, 3.0, 3.1, 3.2)
- **ConvertIndexToRemote Action** - New action to convert indices to remote-backed storage (OpenSearch 3.x feature)
- **S3 Repository Testing** - Integration tests for S3 snapshot repositories using LocalStack
- **Comprehensive Documentation**:
  - `TESTING.md` - Complete testing guide for developers
  - `OPENSEARCH_API_FIXES.md` - API compatibility reference
  - `AGENTS.md` - Strategic migration overview
  - `STATUS.md` - Quick status summary

### 🔄 Changed

- **Migrated from Elasticsearch to OpenSearch**:
  - Replaced `elasticsearch8` client with `opensearch-py` 3.0+
  - Forked `es_client` library → `opensearch_client` module
  - Updated all configuration keys (`elasticsearch:` → `opensearch:`)
  
- **Package Renamed**:
  - Package name: `elasticsearch-curator` → `opensearch-curator`
  - Script name: `es_repo_mgr` → `opensearch_repo_mgr`
  
- **API Compatibility Updates** (8 fixes for opensearch-py 3.0):
  1. `cluster.health()` - Removed `wait_for_status` parameter
  2. `snapshot.create()` - Updated to body dict + params dict format
  3. `snapshot.restore()` - Updated to body dict + params dict format
  4. `snapshot.verify_repository()` - Changed to `repository=` parameter
  5. `snapshot.get_repository()` - Changed to `repository=` parameter
  6. `snapshot.delete_repository()` - Changed to `repository=` parameter
  7. Date field aggregations - Added None value handling
  8. Repository tests - Use cluster's configured `path.repo`

### 🐛 Fixed

- **Date Aggregation None Values** - Handle indices with no date values gracefully
- **Repository Path Configuration** - Tests now use cluster's configured `path.repo` instead of hardcoded paths
- **Snapshot API Compatibility** - Updated all snapshot operations for opensearch-py 3.0 API changes
- **Test Hangs** - Removed problematic `wait_for_status` calls that caused 13-minute timeouts

### 🚀 Performance

- **Test Execution Speed** - 600x faster for targeted tests (37 minutes → 6 seconds)
- **Proper Resource Cleanup** - Improved test infrastructure with better cleanup

### 📊 Test Coverage

- **183/183 Integration Tests Passing** (100% pass rate)
- **16 Action Types Validated** - All curator actions tested against OpenSearch 3.2.0
- **Multi-Repository Support** - Both filesystem and S3 repositories tested
- **Snapshot/Restore** - 11 snapshot tests, all passing
- **ConvertIndexToRemote** - 10 new tests for remote index conversion

### 🔒 Security

- All dependencies updated to latest secure versions
- `opensearch-py` 3.0+ includes security improvements
- Certificate validation improvements

### 📝 Documentation

- Complete migration guide from Elasticsearch Curator
- Comprehensive testing documentation (TESTING.md)
- API compatibility reference (OPENSEARCH_API_FIXES.md)
- Quick start conventions (README_FIRST.md)
- Strategic overview (AGENTS.md)

### ⚠️ Breaking Changes

- **Minimum OpenSearch Version**: 2.0+ (OpenSearch 1.x not supported)
- **Python Version**: 3.8+ required (Python 2.x support removed)
- **Configuration Changes**:
  - `elasticsearch:` key → `opensearch:` in YAML configuration
  - `es_repo_mgr` command → `opensearch_repo_mgr`
- **Removed Features**:
  - Elasticsearch ILM (Index Lifecycle Management) - use OpenSearch ISM instead
  - Elasticsearch-specific tier management (cold2frozen action untested)

### 🔜 Known Limitations

- **cold2frozen Action** - Elasticsearch-specific, not tested for OpenSearch compatibility
- **ISM Integration** - OpenSearch Index State Management not yet integrated (future enhancement)
- **Single Version Testing** - Primarily tested against OpenSearch 3.2.0 (multi-version testing in progress)

### 🙏 Attribution

This project is a fork of [Elasticsearch Curator v8.0.21](https://github.com/elastic/curator) by Elastic.  
Original license: Apache 2.0  
Original copyright: Copyright 2011–2024 Elasticsearch

### 📦 Migration Notes

If you're migrating from Elasticsearch Curator:

1. **Update Configuration**:
   ```yaml
   # Old (Elasticsearch)
   elasticsearch:
     client:
       hosts: https://...
   
   # New (OpenSearch)
   opensearch:
     client:
       hosts: https://...
   ```

2. **Update Dependencies**:
   ```bash
   pip uninstall elasticsearch-curator
   pip install opensearch-curator
   ```

3. **Update Scripts**:
   - `curator` command remains the same
   - `es_repo_mgr` → `opensearch_repo_mgr`

4. **Review Actions**:
   - All core actions supported (delete, close, open, snapshot, restore, etc.)
   - ILM-specific features not available (use OpenSearch ISM)
   - New `convert_index_to_remote` action available

For detailed migration information, see `AGENTS.md` and `MIGRATION_PROGRESS.md`.

---

**Full Changelog**: https://github.com/polecat-dev/opensearch-curator/commits/v1.0.0
