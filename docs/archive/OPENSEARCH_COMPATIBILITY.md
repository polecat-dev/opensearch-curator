# OpenSearch 3.2.0 Compatibility Plan

## Executive Summary

This document outlines the technical approach for adapting Elasticsearch Curator v8.0.21 to work with OpenSearch 3.2.0.

### Key Changes Required

1. **Replace Elasticsearch Python client** (`elasticsearch8`) with OpenSearch client (`opensearch-py`)
2. **Replace or fork `es_client` wrapper library** with OpenSearch-compatible version
3. **Update version detection logic** to recognize OpenSearch version format
4. **Modify configuration schema** from `elasticsearch:` to `opensearch:` keys
5. **Validate API compatibility** for all 16 action types
6. **Update terminology** (master → cluster_manager, etc.)

---

## 1. Dependency Replacement Strategy

### Current Dependencies

```toml
# From pyproject.toml
[project.dependencies]
es_client = "8.17.5"      # Wrapper library (uses elasticsearch8 internally)
click = ">=8.1.0"         # CLI framework - KEEP
PyYAML = ">=6.0"          # YAML parsing - KEEP
voluptuous = ">=0.14.1"   # Schema validation - KEEP
certifi = ">=2023.11.17"  # SSL certs - KEEP
six = ">=1.16.0"          # Python 2/3 compat - CONSIDER REMOVING
```

### Proposed OpenSearch Dependencies

```toml
[project.dependencies]
opensearch-py = ">=3.0.0,<4.0.0"  # Official OpenSearch Python client v3.0.0+
click = ">=8.1.0"
PyYAML = ">=6.0"
voluptuous = ">=0.14.1"
certifi = ">=2023.11.17"

# Additional dependencies for opensearch_client module
dotmap = "*"              # Configuration handling
cryptography = "*"        # Secure storage
tiered-debug = "*"        # Debug utilities
ecs-logging = "*"         # ECS log formatting
elastic-transport = "*"   # Transport layer (shared with opensearch-py)
```

---

## 2. Import Replacement Map

### Direct Client Imports

| Current Import | OpenSearch Replacement | Files Affected |
|----------------|------------------------|----------------|
| `from elasticsearch8 import Elasticsearch` | `from opensearchpy import OpenSearch` | `curator/helpers/testers.py` |
| `from elasticsearch8 import ApiError` | `from opensearchpy.exceptions import ApiError` | `curator/repomgrcli.py` |
| `from elasticsearch8 import NotFoundError` | `from opensearchpy.exceptions import NotFoundError` | 4 files |
| `from elasticsearch8.exceptions import TransportError` | `from opensearchpy.exceptions import TransportError` | `curator/indexlist.py` |
| `from elasticsearch8.exceptions import GeneralAvailabilityWarning` | `from opensearchpy.exceptions import GeneralAvailabilityWarning` | `curator/helpers/waiters.py` |
| `from elasticsearch8 import exceptions as es8exc` | `from opensearchpy import exceptions as os_exc` | `curator/helpers/getters.py` |

### es_client Wrapper Imports

| Current Import | Action Required |
|----------------|-----------------|
| `from es_client.builder import Builder` | Fork or reimplement |
| `from es_client.helpers.config import *` | Fork or reimplement |
| `from es_client.helpers.schemacheck import SchemaCheck` | Fork or reimplement |
| `from es_client.helpers.utils import ensure_list, prune_nones` | Fork or reimplement |
| `from es_client.helpers.logging import configure_logging` | Fork or reimplement |
| `from es_client.defaults import *` | Fork or reimplement |

**Total Files Using es_client:** 30+ matches across codebase

---

## 3. API Compatibility Analysis

### Fully Compatible Operations

These OpenSearch APIs are identical or nearly identical to Elasticsearch:

#### Index Operations
```python
# All compatible
client.indices.get(index="myindex")
client.indices.delete(index="myindex")
client.indices.close(index="myindex")
client.indices.open(index="myindex")
client.indices.exists(index="myindex")
client.indices.stats(index="myindex")
```

#### Cluster Operations
```python
# Compatible
client.cluster.health()
client.cluster.state()
client.cluster.stats()

# Compatible with parameter rename
# OLD: master_timeout
# NEW: cluster_manager_timeout (OpenSearch also accepts master_timeout for backward compat)
client.cluster.health(cluster_manager_timeout="30s")
```

#### Snapshot Operations
```python
# Fully compatible
client.snapshot.create(repository="backup", snapshot="snap1", body={...})
client.snapshot.delete(repository="backup", snapshot="snap1")
client.snapshot.get(repository="backup", snapshot="snap1")
client.snapshot.restore(repository="backup", snapshot="snap1", body={...})

# Repository operations
client.snapshot.create_repository(repository="backup", body={...})
client.snapshot.delete_repository(repository="backup")
client.snapshot.get_repository(repository="backup")
```

### Needs Validation

#### Index Templates
```python
# OpenSearch supports composable templates but syntax may differ slightly
client.indices.put_index_template(name="template1", body={...})

# Test carefully with:
# - Component templates
# - Template priorities
# - Data streams (if used)
```

#### Allocation Rules
```python
# Allocation filtering may have different attribute names
# Elasticsearch: require/include/exclude with node attributes
# OpenSearch: Similar but validate attribute naming

client.cluster.put_settings(body={
    "transient": {
        "cluster.routing.allocation.require._tier": "data_hot"  # ES-specific
    }
})

# OpenSearch equivalent - verify attribute names
```

#### Reindex
```python
# Basic reindex compatible
client.reindex(body={
    "source": {"index": "source_idx"},
    "dest": {"index": "dest_idx"}
})

# Test edge cases:
# - Remote reindex
# - Script-based reindex
# - Throttling parameters
```

### Incompatible Features (Remove or Stub)

#### ILM (Index Lifecycle Management)
```python
# Elasticsearch only - NO OPENSEARCH EQUIVALENT
client.ilm.put_lifecycle(policy="mypolicy", body={...})
client.ilm.explain_lifecycle(index="myindex")

# OpenSearch has ISM (Index State Management) instead
# Different API structure:
client.index_management.put_policy(policy_id="mypolicy", body={...})
```

**Action:** Remove ILM references or build ISM support in future version.

#### Data Tiers
```python
# cold2frozen.py uses Elasticsearch data tier system
# OpenSearch doesn't have frozen tier concept
# Action: Remove cold2frozen.py or stub with deprecation warning
```

#### X-Pack Features
```python
# Any X-Pack specific calls need replacement with Security Plugin equivalents
# Examples:
# - License checking
# - Security realms
# - Watcher (alerting)

# OpenSearch alternatives:
# - Alerting Plugin
# - Security Plugin APIs
```

---

## 4. Client Initialization Changes

### Current (Elasticsearch)

From `examples/curator.yml`:
```yaml
elasticsearch:
  client:
    hosts: https://10.11.12.13:9200
    cloud_id:
    bearer_auth:
    request_timeout: 60
    verify_certs:
    ca_certs:
    client_cert:
    client_key:
  other_settings:
    master_only: false
    skip_version_test: false
    username:
    password:
    api_key:
      id:
      api_key:
```

### Proposed (OpenSearch)

```yaml
opensearch:
  client:
    hosts: 
      - https://10.11.12.13:9200
    # OpenSearch-specific options
    use_ssl: true
    verify_certs: true
    ca_certs: /path/to/ca.pem
    client_cert: /path/to/client.pem
    client_key: /path/to/client-key.pem
    ssl_assert_hostname: false
    ssl_show_warn: false
    timeout: 60
    # Note: cloud_id not applicable to OpenSearch
  other_settings:
    cluster_manager_only: false  # Renamed from master_only
    skip_version_test: false
  auth:
    # Basic auth
    http_auth:
      username: admin
      password: admin
    # Or AWS Sigv4 (for OpenSearch Service)
    aws_auth:
      region: us-east-1
      service: es  # Still 'es' for OpenSearch Service
```

### Code Changes

Current initialization in `curator/cli.py`:
```python
from opensearch_client.builder import Builder

client = Builder(configdict=config['opensearch']).client
```

Proposed OpenSearch version:
```python
from opensearchpy import OpenSearch

def build_opensearch_client(config):
    """Build OpenSearch client from configuration dictionary"""
    client_config = config['opensearch']['client']
    auth_config = config['opensearch'].get('auth', {})
    
    # Extract connection parameters
    hosts = client_config.get('hosts', ['localhost:9200'])
    use_ssl = client_config.get('use_ssl', False)
    verify_certs = client_config.get('verify_certs', True)
    ca_certs = client_config.get('ca_certs')
    
    # Build authentication
    http_auth = None
    if 'http_auth' in auth_config:
        http_auth = (
            auth_config['http_auth']['username'],
            auth_config['http_auth']['password']
        )
    
    # Create client
    client = OpenSearch(
        hosts=hosts,
        http_auth=http_auth,
        use_ssl=use_ssl,
        verify_certs=verify_certs,
        ca_certs=ca_certs,
        ssl_assert_hostname=client_config.get('ssl_assert_hostname', True),
        ssl_show_warn=client_config.get('ssl_show_warn', True),
        timeout=client_config.get('timeout', 60),
    )
    
    return client
```

---

## 5. Version Detection Changes

### Current Logic

From `curator/defaults/settings.py`:
```python
VERSION_MIN = (7, 14, 0)  # Minimum Elasticsearch version
VERSION_MAX = (8, 99, 99)  # Maximum Elasticsearch version
```

Elsewhere in code (location TBD):
```python
# Likely something like:
version_string = client.info()['version']['number']
# Returns: "8.0.1" for Elasticsearch

version_tuple = tuple(int(x) for x in version_string.split('.'))
if version_tuple < VERSION_MIN or version_tuple > VERSION_MAX:
    raise VersionError(f"Unsupported version: {version_string}")
```

### OpenSearch Version Format

OpenSearch versions look like:
```json
{
  "name": "opensearch-node1",
  "cluster_name": "opensearch-cluster",
  "version": {
    "distribution": "opensearch",
    "number": "3.2.0",
    "build_type": "tar",
    "build_hash": "...",
    "build_date": "...",
    "build_snapshot": false,
    "lucene_version": "9.12.0",
    "minimum_wire_compatibility_version": "2.0.0",
    "minimum_index_compatibility_version": "2.0.0"
  }
}
```

### Proposed Changes

```python
# curator/defaults/settings.py
VERSION_MIN = (2, 0, 0)   # Minimum OpenSearch version (2.0+)
VERSION_MAX = (3, 99, 99) # Maximum OpenSearch version (3.x)

# curator/helpers/version.py (new file)
def get_version_info(client):
    """
    Get version information from OpenSearch cluster.
    
    Returns:
        dict: {
            'distribution': 'opensearch',
            'number': '3.2.0',
            'tuple': (3, 2, 0)
        }
    """
    info = client.info()
    version_info = info.get('version', {})
    
    # Check if this is OpenSearch (not Elasticsearch)
    distribution = version_info.get('distribution', 'unknown')
    if distribution != 'opensearch':
        raise UnsupportedDistributionError(
            f"Expected OpenSearch, but found: {distribution}"
        )
    
    version_string = version_info.get('number', '0.0.0')
    version_tuple = tuple(int(x) for x in version_string.split('.'))
    
    return {
        'distribution': distribution,
        'number': version_string,
        'tuple': version_tuple
    }

def validate_version(client, skip_version_test=False):
    """Validate OpenSearch version against supported range."""
    if skip_version_test:
        logger.warning("Skipping version validation (skip_version_test=True)")
        return True
    
    version_info = get_version_info(client)
    version = version_info['tuple']
    
    if version < VERSION_MIN:
        raise VersionError(
            f"OpenSearch {version_info['number']} is too old. "
            f"Minimum supported version: {'.'.join(map(str, VERSION_MIN))}"
        )
    
    if version > VERSION_MAX:
        logger.warning(
            f"OpenSearch {version_info['number']} is newer than tested version. "
            f"Maximum tested version: {'.'.join(map(str, VERSION_MAX))}"
        )
    
    return True
```

---

## 6. Terminology Updates

### Search & Replace Operations

| Old Term | New Term | Context |
|----------|----------|---------|
| `master_timeout` | `cluster_manager_timeout` | API parameters |
| `master_only` | `cluster_manager_only` | Configuration |
| `master node` | `cluster manager node` | Documentation |
| `Elasticsearch` | `OpenSearch` | Everywhere |
| `elasticsearch` | `opensearch` | Code/config keys |

### Parameter Compatibility

Good news: OpenSearch accepts both `master_timeout` and `cluster_manager_timeout` for backward compatibility. However, we should use the new naming:

```python
# Works but deprecated
client.cluster.health(master_timeout="30s")

# Preferred for OpenSearch
client.cluster.health(cluster_manager_timeout="30s")
```

---

## 7. Testing Strategy

### Unit Test Updates

```python
# tests/unit/test_indexlist.py (example)

# OLD
from unittest.mock import Mock
from elasticsearch8 import Elasticsearch

def test_index_list_creation():
    mock_client = Mock(spec=Elasticsearch)
    # ... test code

# NEW
from unittest.mock import Mock
from opensearchpy import OpenSearch

def test_index_list_creation():
    mock_client = Mock(spec=OpenSearch)
    # ... test code (mostly unchanged)
```

### Integration Test Setup

```yaml
# .github/workflows/test.yml
name: Integration Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        opensearch-version:
          - "2.11.0"
          - "2.12.0"
          - "3.0.0"
          - "3.1.0"
          - "3.2.0"
        python-version:
          - "3.8"
          - "3.9"
          - "3.10"
          - "3.11"
          - "3.12"
    
    services:
      opensearch:
        image: opensearchproject/opensearch:${{ matrix.opensearch-version }}
        ports:
          - 9200:9200
          - 9600:9600
        env:
          discovery.type: single-node
          DISABLE_SECURITY_PLUGIN: true
          OPENSEARCH_JAVA_OPTS: "-Xms512m -Xmx512m"
        options: >-
          --health-cmd "curl -f http://localhost:9200/_cluster/health"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 10
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      
      - name: Install dependencies
        run: |
          pip install hatch
          hatch env create
      
      - name: Wait for OpenSearch
        run: |
          timeout 60 bash -c 'until curl -s http://localhost:9200; do sleep 2; done'
      
      - name: Run tests
        run: |
          hatch run test:pytest tests/ -v --cov=curator
        env:
          OPENSEARCH_HOST: localhost:9200
```

### Manual Testing Checklist

Create `tests/manual/test_opensearch.sh`:
```bash
#!/bin/bash
# Manual testing script for OpenSearch compatibility

set -e

OPENSEARCH_VERSION=${OPENSEARCH_VERSION:-3.2.0}
OPENSEARCH_HOST=${OPENSEARCH_HOST:-localhost:9200}

echo "Testing OpenSearch Curator against OpenSearch ${OPENSEARCH_VERSION}"

# Start OpenSearch in Docker if not running
if ! curl -s http://${OPENSEARCH_HOST} > /dev/null; then
    echo "Starting OpenSearch ${OPENSEARCH_VERSION}..."
    docker run -d --name opensearch-test \
        -p 9200:9200 -p 9600:9600 \
        -e "discovery.type=single-node" \
        -e "DISABLE_SECURITY_PLUGIN=true" \
        opensearchproject/opensearch:${OPENSEARCH_VERSION}
    
    # Wait for OpenSearch to be ready
    echo "Waiting for OpenSearch to be ready..."
    timeout 60 bash -c 'until curl -s http://localhost:9200/_cluster/health; do sleep 2; done'
fi

# Test 1: Connection
echo "Test 1: Connection"
curator --config examples/curator.yml show_indices

# Test 2: Create test index
echo "Test 2: Create test index"
curl -X PUT "http://${OPENSEARCH_HOST}/test-index-001"

# Test 3: Close index
echo "Test 3: Close index"
curator --config examples/curator.yml --dry-run close --filter_list '[{"filtertype":"pattern","kind":"prefix","value":"test-"}]'

# Test 4: Open index
echo "Test 4: Open index"  
curator --config examples/curator.yml open --filter_list '[{"filtertype":"pattern","kind":"prefix","value":"test-"}]'

# Test 5: Delete index
echo "Test 5: Delete index"
curator --config examples/curator.yml delete_indices --filter_list '[{"filtertype":"pattern","kind":"prefix","value":"test-"}]'

# Cleanup
docker stop opensearch-test && docker rm opensearch-test

echo "All tests passed!"
```

---

## 8. Build & Release Process

### Package Naming

**Recommendation:** `opensearch-curator` on PyPI

```toml
[project]
name = "opensearch-curator"
version = "1.0.0"
description = "Curator for OpenSearch indices and snapshots"
authors = [
    {name = "Your Name or Organization", email = "your@email.com"}
]
```

### License Considerations

Original Curator is Apache License 2.0. When forking:

1. **Keep Apache License 2.0** (compatible with OpenSearch)
2. **Update LICENSE file**:
   ```
   Copyright 2011-2024 Elasticsearch B.V. (original work)
   Copyright 2024-present [Your Name/Org] (modifications for OpenSearch)
   
   Licensed under the Apache License, Version 2.0 (the "License");
   ...
   ```
3. **Add NOTICE file** documenting the fork
4. **Update README** with attribution

### Version Numbering Strategy

**Recommendation:** Start at 1.0.0 (semantic versioning)

- `1.0.0` - Initial OpenSearch-compatible release
- `1.1.0` - Minor features, backward compatible
- `1.2.0` - ISM integration (future)
- `2.0.0` - Breaking changes (if needed)

---

## 9. Implementation Phases

### Phase 1: Preparation (Week 1)
- [ ] Set up OpenSearch 3.2.0 locally
- [ ] Research `opensearch-py` API
- [ ] Decide on `es_client` fork vs. custom wrapper
- [ ] Create development branch

### Phase 2: Core Migration (Week 2-3)
- [ ] Replace all `elasticsearch8` imports
- [ ] Update client initialization
- [ ] Modify version detection
- [ ] Update configuration schema
- [ ] Test basic connection

### Phase 3: Action Validation (Week 4-5)
- [ ] Test each action individually
- [ ] Remove/stub incompatible features
- [ ] Update API calls as needed
- [ ] Validate error handling

### Phase 4: Testing (Week 6-7)
- [ ] Unit test updates
- [ ] Integration test setup
- [ ] Multi-version testing (OpenSearch 2.11, 3.0, 3.2)
- [ ] Performance testing

### Phase 5: Documentation (Week 8)
- [ ] Update README
- [ ] Update all docs
- [ ] Create migration guide
- [ ] Update examples

### Phase 6: Release (Week 9-10)
- [ ] Set up CI/CD
- [ ] Build Docker image
- [ ] Publish to PyPI
- [ ] Tag v1.0.0

---

## 10. Risk Mitigation

### High-Risk Items

1. **es_client fork complexity**
   - **Mitigation:** Start with minimal custom wrapper, expand as needed
   - **Fallback:** Direct `opensearch-py` usage without wrapper

2. **API incompatibilities**
   - **Mitigation:** Thorough testing against multiple OpenSearch versions
   - **Fallback:** Document unsupported features clearly

3. **Version detection edge cases**
   - **Mitigation:** Comprehensive version parsing tests
   - **Fallback:** `skip_version_test` configuration option

### Medium-Risk Items

1. **Configuration migration**
   - **Mitigation:** Support both `elasticsearch:` and `opensearch:` keys initially
   - **Deprecation:** Warn on `elasticsearch:` usage, remove in v2.0

2. **Authentication differences**
   - **Mitigation:** Test all auth methods (basic, API key, AWS SigV4)
   - **Documentation:** Clear examples for each method

---

## 11. Success Metrics

- [ ] All unit tests pass
- [ ] Integration tests pass on OpenSearch 2.11, 3.0, 3.1, 3.2
- [ ] Python 3.8-3.12 compatibility verified
- [ ] Zero dependencies on Elasticsearch packages
- [ ] Documentation complete and accurate
- [ ] CI/CD pipeline functional
- [ ] PyPI package published successfully

---

## 12. Future Enhancements (Post-v1.0)

### ISM Integration (v1.2 or v2.0)
- Build ISM policy management
- Replace removed ILM functionality
- Policy migration tools

### OpenSearch-Specific Features
- Anomaly detection index management
- Observability indices
- Security index handling

### Performance Optimizations
- Bulk operations for large index counts
- Parallel processing
- Connection pooling

---

**Document Status:** Technical specification ready for implementation  
**Next Action:** Begin Phase 1 (Preparation)  
**Owner:** Development team  
**Review Date:** After Phase 2 completion
