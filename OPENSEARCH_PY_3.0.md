# opensearch-py 3.0.0 Integration Guide

## Why opensearch-py 3.0.0?

We're using **opensearch-py 3.0.0** (latest major version) for several key reasons:

### ✅ Key Benefits

1. **Full OpenSearch 3.x Support**
   - Native support for OpenSearch 3.2.0 (our target)
   - All new OpenSearch 3.x APIs available
   - Backward compatible with OpenSearch 2.x

2. **Improved Type Hints**
   - Better IDE autocomplete
   - Stronger type safety
   - Easier debugging

3. **Enhanced Security**
   - Updated AWS SigV4 authentication
   - Better SSL/TLS handling
   - Improved certificate validation

4. **Better Async Support**
   - Enhanced async/await patterns
   - More efficient connection pooling
   - Improved performance for high-throughput scenarios

5. **Active Maintenance**
   - Latest bug fixes
   - Security patches
   - Active community support

## Version Requirements

```toml
[project.dependencies]
opensearch-py = ">=3.0.0,<4.0.0"
```

**Reasoning:**
- `>=3.0.0` - Use 3.0.0 or newer (gets latest features and fixes)
- `<4.0.0` - Stay within v3.x (avoid breaking changes when v4 is released)

## Compatibility Matrix

| opensearch-py Version | OpenSearch Version | Python Version | Status |
|----------------------|-------------------|----------------|--------|
| 3.0.0+ | 2.0 - 3.x | 3.7+ | ✅ Recommended |
| 2.x | 1.x - 2.x | 3.6+ | ⚠️ Older |
| 1.x | 1.x | 3.6+ | ❌ Legacy |

## Installation

### Basic Installation

```bash
pip install "opensearch-py>=3.0.0,<4.0.0"
```

### With All Dependencies for opensearch_client

```bash
# Install opensearch-py 3.0.0+
pip install "opensearch-py>=3.0.0,<4.0.0"

# Install additional dependencies needed by opensearch_client module
pip install dotmap cryptography pyyaml voluptuous ecs-logging tiered-debug elastic-transport
```

### Development Installation (with testing tools)

```bash
pip install "opensearch-py>=3.0.0,<4.0.0" pytest pytest-cov black mypy ruff
```

## Usage Examples

### Basic Connection (opensearch-py 3.0.0)

```python
from opensearchpy import OpenSearch

# Simple connection
client = OpenSearch(
    hosts=['localhost:9200'],
    use_ssl=False,
    verify_certs=False
)

# Get cluster info
info = client.info()
print(f"Connected to: {info['version']['distribution']} {info['version']['number']}")
```

### With Authentication

```python
from opensearchpy import OpenSearch

# Basic auth
client = OpenSearch(
    hosts=['https://localhost:9200'],
    http_auth=('admin', 'admin'),
    use_ssl=True,
    verify_certs=True,
    ca_certs='/path/to/ca.pem'
)

# AWS SigV4 (for OpenSearch Service)
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
import boto3

credentials = boto3.Session().get_credentials()
auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    'us-east-1',
    'es',
    session_token=credentials.token
)

client = OpenSearch(
    hosts=[{'host': 'search-domain.us-east-1.es.amazonaws.com', 'port': 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
```

### Using with opensearch_client Builder

```python
from opensearch_client import Builder

# Configuration for opensearch-py 3.0.0
config = {
    'opensearch': {
        'client': {
            'hosts': ['https://localhost:9200'],
            'http_auth': ('admin', 'admin'),
            'use_ssl': True,
            'verify_certs': True,
            'ca_certs': '/path/to/ca.pem'
        },
        'other_settings': {
            'cluster_manager_only': False,
            'skip_version_test': False
        }
    }
}

# Build client (uses opensearch-py 3.0.0 under the hood)
builder = Builder(configdict=config, autoconnect=True)
client = builder.client

# Use the client
print(client.cluster.health())
```

## API Differences from elasticsearch8

### Import Changes

```python
# OLD (elasticsearch8)
from elasticsearch8 import Elasticsearch
from elasticsearch8.exceptions import NotFoundError, TransportError

# NEW (opensearch-py 3.0.0)
from opensearchpy import OpenSearch
from opensearchpy.exceptions import NotFoundError, TransportError
```

### Client Instantiation

```python
# OLD
client = Elasticsearch(**kwargs)

# NEW
client = OpenSearch(**kwargs)
```

### Connection Parameters

Most parameters are compatible, but some differences:

```python
# opensearch-py 3.0.0 common parameters
OpenSearch(
    hosts=['localhost:9200'],           # Same
    http_auth=('user', 'pass'),         # Same
    use_ssl=True,                       # Same
    verify_certs=True,                  # Same
    ca_certs='/path/to/ca.pem',        # Same
    client_cert='/path/to/client.pem', # Same
    client_key='/path/to/key.pem',     # Same
    ssl_assert_hostname=False,          # Same
    ssl_show_warn=False,                # Same
    timeout=30,                         # Same
    max_retries=3,                      # Same
    retry_on_timeout=True               # Same
)
```

### Exception Handling

```python
from opensearchpy.exceptions import (
    NotFoundError,
    TransportError,
    ConnectionError,
    RequestError,
    AuthenticationException,
    AuthorizationException
)

try:
    client.indices.get(index='nonexistent')
except NotFoundError as e:
    print(f"Index not found: {e}")
except TransportError as e:
    print(f"Transport error: {e}")
```

## opensearch-py 3.0.0 Specific Features

### 1. Enhanced Type Hints

```python
from opensearchpy import OpenSearch
from typing import Dict, Any

def get_cluster_stats(client: OpenSearch) -> Dict[str, Any]:
    """IDE will provide full autocomplete for client methods"""
    return client.cluster.stats()
```

### 2. Better Async Support

```python
from opensearchpy import AsyncOpenSearch

async def async_search():
    client = AsyncOpenSearch(
        hosts=['localhost:9200'],
        use_ssl=False
    )
    
    response = await client.search(
        index='my-index',
        body={'query': {'match_all': {}}}
    )
    
    await client.close()
    return response
```

### 3. Connection Pooling

```python
client = OpenSearch(
    hosts=['localhost:9200'],
    pool_maxsize=10,            # Max connections in pool
    max_retries=3,              # Retry failed requests
    retry_on_timeout=True,      # Retry on timeout
    timeout=30                  # Request timeout
)
```

## Migration Checklist

When migrating from elasticsearch8 to opensearch-py 3.0.0:

- [x] Update imports: `elasticsearch8` → `opensearchpy`
- [x] Update class name: `Elasticsearch` → `OpenSearch`
- [x] Update exception imports
- [ ] Test all API calls (most are compatible)
- [ ] Verify SSL/TLS configuration
- [ ] Test authentication methods
- [ ] Validate connection pooling behavior
- [ ] Check async operations (if used)
- [ ] Update type hints in code
- [ ] Test against target OpenSearch version (3.2.0)

## Common Issues & Solutions

### Issue: Import Error

```python
# Error: ModuleNotFoundError: No module named 'opensearchpy'
# Solution:
pip install "opensearch-py>=3.0.0,<4.0.0"
```

### Issue: SSL Verification

```python
# Error: SSL certificate verification failed
# Solution: Either fix certificates or disable verification (dev only)
client = OpenSearch(
    hosts=['https://localhost:9200'],
    verify_certs=False,  # Only for development!
    ssl_show_warn=False
)
```

### Issue: Connection Refused

```python
# Error: ConnectionError: ConnectionRefusedError
# Solution: Check OpenSearch is running and accessible
import subprocess
subprocess.run(['curl', 'http://localhost:9200'])
```

## Testing Against OpenSearch 3.2.0

### Start OpenSearch 3.2.0

```bash
docker run -d \
  --name opensearch-test \
  -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:3.2.0
```

### Test Connection

```python
from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=['localhost:9200'],
    use_ssl=False
)

# Verify connection
info = client.info()
assert info['version']['distribution'] == 'opensearch'
assert info['version']['number'].startswith('3.2')
print("✅ Connected to OpenSearch 3.2.0!")

# Test basic operations
client.indices.create(index='test-index')
client.index(index='test-index', id='1', body={'field': 'value'})
doc = client.get(index='test-index', id='1')
print(f"✅ Document retrieved: {doc['_source']}")

client.indices.delete(index='test-index')
print("✅ All tests passed!")
```

## Resources

- **opensearch-py GitHub:** https://github.com/opensearch-project/opensearch-py
- **Documentation:** https://opensearch.org/docs/latest/clients/python/
- **Release Notes:** https://github.com/opensearch-project/opensearch-py/releases/tag/v3.0.0
- **API Reference:** https://opensearch-project.github.io/opensearch-py/

## Version History

| Date | Version | Notes |
|------|---------|-------|
| 2024-11-05 | 3.0.0 | Initial migration target |
| Future | 3.x | Track minor/patch updates |
| Future | 4.0.0 | Next major version (when released) |

---

**Status:** ✅ **Ready for Testing**  
**Target:** opensearch-py 3.0.0+  
**Compatibility:** OpenSearch 2.0 - 3.2.0+
