# OpenSearch 3.2.0 Migration Checklist

Quick reference for migrating Elasticsearch Curator v8.0.21 to OpenSearch Curator.

## Critical Dependencies to Replace

### 1. Python Client Libraries

- [ ] Replace `elasticsearch8` with `opensearch-py`
  - Files affected: 7+ files across `curator/` directory
  - Imports to change:
    ```python
    # OLD
    from elasticsearch8 import Elasticsearch, ApiError, NotFoundError
    from elasticsearch8.exceptions import TransportError
    
    # NEW
    from opensearchpy import OpenSearch
    from opensearchpy.exceptions import NotFoundError, TransportError, ApiError
    ```

### 2. es_client Library

**Option A: Fork es_client**
- [ ] Clone `es_client` repository
- [ ] Rename to `opensearch_client`
- [ ] Replace all Elasticsearch API calls with OpenSearch equivalents
- [ ] Publish as separate package
- [ ] Update `pyproject.toml` dependency

**Option B: Build Custom Wrapper**
- [ ] Create `curator/opensearch_client/` module
- [ ] Implement same interface as `es_client.helpers`
- [ ] Direct OpenSearch integration

**Affected Imports:**
```python
from es_client.helpers.config import config_from_cli_args, generate_configdict
from es_client.builder import Builder
from es_client.helpers.schemacheck import SchemaCheck
from es_client.helpers.utils import ensure_list, prune_nones
from es_client.defaults import LOGGING_SETTINGS, OPTION_DEFAULTS
```

## Files Requiring Changes

### Core Files (High Priority)

```
✅ = Easy change
⚠️ = Moderate complexity
🔴 = High complexity/risk

✅ pyproject.toml                           # Update dependencies
⚠️ curator/__init__.py                      # Update docstring
✅ curator/_version.py                      # Version number
🔴 curator/cli.py                           # Client initialization
🔴 curator/repomgrcli.py                    # Repository manager
🔴 curator/singletons.py                    # Configuration helpers
⚠️ curator/indexlist.py                     # Index operations
⚠️ curator/snapshotlist.py                  # Snapshot operations
✅ curator/exceptions.py                    # Error messages
⚠️ curator/defaults/settings.py             # VERSION_MIN/MAX constants
```

### Helper Files

```
⚠️ curator/helpers/testers.py               # Client type checks
⚠️ curator/helpers/getters.py               # API getters
⚠️ curator/helpers/waiters.py               # Async waiters
✅ curator/helpers/date_ops.py              # Date utilities (minimal changes)
✅ curator/helpers/utils.py                 # Generic utilities
```

### Action Files (Test Each)

```
✅ curator/actions/close.py                 # Low risk
✅ curator/actions/open.py                  # Low risk
✅ curator/actions/delete_indices.py        # Low risk
⚠️ curator/actions/snapshot.py              # Test thoroughly
⚠️ curator/actions/allocation.py            # API syntax may differ
⚠️ curator/actions/replicas.py              # Test replication
⚠️ curator/actions/forcemerge.py            # Validate API
⚠️ curator/actions/reindex.py               # Validate reindex API
⚠️ curator/actions/shrink.py                # Test shrink operation
⚠️ curator/actions/rollover.py              # ISM considerations
🔴 curator/actions/cold2frozen.py           # Elasticsearch-specific (remove/stub)
✅ curator/actions/create_index.py          # Low risk
⚠️ curator/actions/index_settings.py        # Setting names may differ
⚠️ curator/actions/cluster_routing.py       # master → cluster_manager
⚠️ curator/actions/alias.py                 # Test alias operations
```

### Validator Files

```
⚠️ curator/validators/actions.py            # Schema validation
⚠️ curator/validators/filter_functions.py   # Filter schemas
```

## Configuration Changes

### 1. YAML Configuration Structure

```yaml
# OLD (Elasticsearch)
elasticsearch:
  client:
    hosts: https://localhost:9200
  other_settings:
    master_only: true

# NEW (OpenSearch)
opensearch:
  client:
    hosts: https://localhost:9200
  other_settings:
    cluster_manager_only: true  # Renamed from master_only
```

### 2. Version Constants

```python
# curator/defaults/settings.py

# OLD
VERSION_MIN = (7, 14, 0)
VERSION_MAX = (8, 99, 99)

# NEW
VERSION_MIN = (2, 0, 0)   # OpenSearch 2.0+
VERSION_MAX = (3, 99, 99) # Support OpenSearch 3.x
```

### 3. Documentation URL

```python
# OLD
CURATOR_DOCS = 'https://www.elastic.co/guide/en/elasticsearch/client/curator'

# NEW
CURATOR_DOCS = 'https://opensearch.org/docs/latest/tools/curator'
# Or your custom documentation site
```

## Testing Strategy

### 1. Local OpenSearch Setup

```bash
# Docker method (recommended)
docker run -d -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:3.2.0

# Verify
curl http://localhost:9200
```

### 2. Test Priority Order

1. **Connection & Version Detection**
   - [ ] Client initialization
   - [ ] Version checking
   - [ ] Cluster info retrieval

2. **Basic Index Operations**
   - [ ] List indices
   - [ ] Close index
   - [ ] Open index
   - [ ] Delete index

3. **Snapshot Operations**
   - [ ] Create repository
   - [ ] List repositories
   - [ ] Create snapshot
   - [ ] Delete snapshot
   - [ ] Restore snapshot

4. **Advanced Operations**
   - [ ] Force merge
   - [ ] Allocation
   - [ ] Replicas
   - [ ] Reindex
   - [ ] Shrink

### 3. Test Environments

```
- [ ] OpenSearch 2.11 (latest 2.x)
- [ ] OpenSearch 3.0
- [ ] OpenSearch 3.1
- [ ] OpenSearch 3.2 (target version)
```

### 4. Python Version Testing

```
- [ ] Python 3.8
- [ ] Python 3.9
- [ ] Python 3.10
- [ ] Python 3.11
- [ ] Python 3.12
```

## CI/CD Setup (Replace Current)

### Option 1: GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
        opensearch-version: ["2.11", "3.2"]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Start OpenSearch ${{ matrix.opensearch-version }}
        run: |
          docker run -d -p 9200:9200 -p 9600:9600 \
            -e "discovery.type=single-node" \
            -e "DISABLE_SECURITY_PLUGIN=true" \
            opensearchproject/opensearch:${{ matrix.opensearch-version }}
          sleep 30  # Wait for OpenSearch to start
      - name: Install dependencies
        run: |
          pip install hatch
      - name: Run unit tests
        run: hatch run test:pytest tests/unit
      - name: Run integration tests
        run: hatch run test:pytest tests/integration
```

### Option 2: Manual Testing Only

- [ ] Delete `.github/workflows/` directory
- [ ] Add testing instructions to README
- [ ] Use local `pytest` runs

## Documentation Updates

### Files to Update

- [ ] `README.rst` - Change all "Elasticsearch" → "OpenSearch"
- [ ] `CONTRIBUTING.md` - Update contribution guidelines
- [ ] `docs/**/*.md` - Update all documentation
- [ ] `examples/curator.yml` - Update config example
- [ ] `examples/actions/*.yml` - Update action examples
- [ ] All docstrings in Python files

### Branding Changes

```python
# Search and replace across all files:
"Elasticsearch" → "OpenSearch"
"elasticsearch" → "opensearch"
"Elastic" → "OpenSearch Project"  # In appropriate contexts
```

## Build & Package Updates

### pyproject.toml

```toml
[project]
name = "opensearch-curator"
version = "1.0.0"  # Fresh start
description = "Tending your OpenSearch indices and snapshots"
dependencies = [
    "opensearch-py>=2.0.0,<3.0.0",
    "click>=8.1.0",
    "PyYAML>=6.0",
    "voluptuous>=0.14.1",
    "certifi>=2023.11.17",
]

[project.urls]
Homepage = "https://github.com/YOUR_ORG/opensearch-curator"
Documentation = "https://opensearch-curator.readthedocs.io"
Repository = "https://github.com/YOUR_ORG/opensearch-curator"
```

### Entry Points (Keep Same)

```toml
[project.scripts]
curator = "curator.cli:cli"
curator_cli = "curator.singletons:cli"
es_repo_mgr = "curator.repomgrcli:repo_mgr_cli"
# Note: Consider renaming es_repo_mgr → opensearch_repo_mgr
```

## Known Issues & Gotchas

### 1. Elasticsearch-Specific Features to Remove/Stub

- [ ] **ILM (Index Lifecycle Management)**
  - OpenSearch uses ISM (Index State Management) instead
  - Different API and configuration
  - Consider removing ILM references or building ISM support

- [ ] **Cold to Frozen Tier Migration** (`cold2frozen.py`)
  - Elasticsearch-specific data tier concept
  - No direct OpenSearch equivalent
  - **Action:** Remove or stub with deprecation warning

- [ ] **X-Pack Security**
  - OpenSearch uses Security Plugin (different config)
  - Authentication methods differ
  - Update security-related code

### 2. Terminology Changes

| Elasticsearch | OpenSearch |
|---------------|------------|
| master_only | cluster_manager_only |
| master_timeout | cluster_manager_timeout |
| X-Pack | Security Plugin |
| ILM | ISM |

### 3. API Compatibility Matrix

**Highly Compatible:**
- Index CRUD operations
- Snapshot/restore
- Cluster health
- Index templates (mostly)

**Needs Validation:**
- Allocation rules syntax
- Index settings names
- Cluster settings
- Snapshot repository types

**Not Compatible:**
- ILM-specific operations
- X-Pack features
- Data tier management
- Frozen indices

## Quick Start Commands

```bash
# 1. Install development dependencies
pip install hatch

# 2. Create development environment
hatch env create

# 3. Run unit tests
hatch run test:pytest tests/unit -v

# 4. Run integration tests (requires OpenSearch running)
hatch run test:pytest tests/integration -v

# 5. Run linting
hatch run lint:all

# 6. Format code
hatch run lint:fmt

# 7. Build package
hatch build

# 8. Install locally for testing
pip install -e .
```

## Success Criteria

- [ ] All unit tests pass against OpenSearch 3.2.0
- [ ] Integration tests validate all core actions
- [ ] No `elasticsearch8` or `es_client` imports remain
- [ ] Documentation fully updated
- [ ] CI pipeline runs successfully
- [ ] Docker image builds and runs
- [ ] PyPI package publishes successfully

## Timeline Estimate

- **Week 1-2:** Dependency replacement
- **Week 3-4:** Core functionality testing
- **Week 5-6:** Action validation
- **Week 7-8:** Integration testing
- **Week 9:** Documentation
- **Week 10:** Release preparation

**Total:** ~10 weeks to production-ready v1.0.0

---

**Next Step:** Begin with dependency replacement (replace `elasticsearch8` imports)

**Blocker Check:** Need to decide on `es_client` fork vs. custom wrapper approach before proceeding.
