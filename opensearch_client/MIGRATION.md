# es_client → opensearch_client Migration Guide

## What We Copied

Successfully copied `es_client` v8.19.5 from https://github.com/untergeek/es_client

**Files copied:** 17 Python files  
**Location:** `opensearch_client/` directory  
**License:** Apache 2.0 (preserved as `LICENSE.es_client`)

### Directory Structure

```
opensearch_client/
├── builder.py              # Main client builder (core logic)
├── cli_example.py          # CLI example code
├── commands.py             # Command utilities
├── config.py               # Configuration handling
├── debug.py                # Debug utilities
├── defaults.py             # Default settings and schemas
├── exceptions.py           # Custom exceptions
├── logging.py              # Logging configuration
├── schemacheck.py          # Schema validation
├── utils.py                # Utility functions
├── __init__.py             # Package initialization
├── py.typed                # Type hints marker
├── helpers/                # Helper modules
│   ├── config.py           # Config helpers
│   ├── logging.py          # Logging helpers
│   ├── schemacheck.py      # Schema check helpers
│   ├── utils.py            # Utility helpers
│   └── __init__.py
├── LICENSE.es_client       # Original Apache 2.0 license
├── README.md               # Migration guide (this info)
└── README_ORIGINAL.rst     # Original README for reference
```

## Migration Requirements

### Files Needing Changes

| File | Priority | elasticsearch8 References | Notes |
|------|----------|---------------------------|-------|
| `builder.py` | 🔴 HIGH | 7 occurrences | Core client creation |
| `config.py` | 🔴 HIGH | 2 occurrences | Client validation |
| `utils.py` | ⚠️ MEDIUM | 2 occurrences | Type hints, utilities |
| `logging.py` | ⚠️ MEDIUM | 2 occurrences | Logger names |
| `cli_example.py` | ✅ LOW | 1 occurrence | Example code |
| `defaults.py` | ✅ LOW | 3 occurrences | Documentation only |
| `helpers/config.py` | ✅ LOW | 1 occurrence | Commented out |
| `helpers/logging.py` | ✅ LOW | 2 occurrences | Commented out |
| `helpers/utils.py` | ✅ LOW | 1 occurrence | Commented out |

**Total:** 24 references to `elasticsearch8` across 9 files

### Import Replacements

#### Direct Imports
```python
# OLD
import elasticsearch8
from elasticsearch8 import Elasticsearch
from elasticsearch8.exceptions import BadRequestError, NotFoundError

# NEW  
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.exceptions import BadRequestError, NotFoundError
```

#### Client Instantiation
```python
# OLD
client = elasticsearch8.Elasticsearch(**client_args)

# NEW
client = opensearchpy.OpenSearch(**client_args)
```

#### Type Hints
```python
# OLD
def function(client: Elasticsearch) -> None:
    ...

# NEW
def function(client: OpenSearch) -> None:
    ...
```

#### Logger Names
```python
# OLD
logging.getLogger("elasticsearch8.trace")

# NEW
logging.getLogger("opensearch.trace")
# Or check what opensearch-py uses - might be "opensearch" or "opensearchpy"
```

## Step-by-Step Migration Plan

### Phase 1: Core Files (Week 1)

#### 1.1 Update `builder.py`

**Current imports:**
```python
import elasticsearch8
```

**Changes needed:**
- Replace import statement
- Update client instantiation (line ~745)
- Update type hints in docstrings
- Test client creation

**Priority:** 🔴 CRITICAL - This is the core of the library

#### 1.2 Update `config.py`

**Current imports:**
```python
from elasticsearch8 import Elasticsearch
```

**Changes needed:**
- Replace import
- Update type hints
- Verify configuration validation works with OpenSearch

**Priority:** 🔴 CRITICAL - Required for config validation

#### 1.3 Update `utils.py`

**Current imports:**
```python
from elasticsearch8 import Elasticsearch
```

**Changes needed:**
- Replace import
- Update type hints
- Test utility functions

**Priority:** ⚠️ MEDIUM - Support functions

### Phase 2: Supporting Files (Week 1)

#### 2.1 Update `logging.py`

**Changes needed:**
- Update logger name from `elasticsearch8.trace` to `opensearch.trace`
- Verify logging configuration works

**Priority:** ⚠️ MEDIUM - Important for debugging

#### 2.2 Update `cli_example.py`

**Changes needed:**
- Replace exception imports
- Update example code
- Can be simplified or removed if not needed

**Priority:** ✅ LOW - Example code only

#### 2.3 Update `defaults.py`

**Changes needed:**
- Update docstring references to Elasticsearch
- Change to OpenSearch in documentation

**Priority:** ✅ LOW - Documentation only

### Phase 3: Package Updates (Week 1)

#### 3.1 Update `__init__.py`

**Changes needed:**
```python
# Current
__version__ = "8.19.4"
__description__ = "Elasticsearch Client builder, complete with schema validation"
__url__ = "https://github.com/untergeek/es_client"
__keywords__ = ["elasticsearch", "client", "connect", "command-line"]

# New
__version__ = "1.0.0"  # Fresh start for OpenSearch
__description__ = "OpenSearch Client builder, complete with schema validation"
__url__ = "https://github.com/polecat-dev/opensearch-curator"
__keywords__ = ["opensearch", "client", "connect", "command-line"]
```

**Also update:**
- Copyright year
- Author attribution (keep original + add yours)
- Package exports

### Phase 4: Testing (Week 1-2)

#### 4.1 Unit Tests

Create test file: `tests/test_opensearch_client.py`

```python
import pytest
from opensearchpy import OpenSearch
from opensearch_client import Builder

def test_basic_connection():
    """Test basic OpenSearch connection"""
    config = {
        'opensearch': {
            'client': {
                'hosts': ['http://localhost:9200']
            }
        }
    }
    builder = Builder(configdict=config)
    assert builder.client is not None
    assert isinstance(builder.client, OpenSearch)

def test_client_info():
    """Test client info retrieval"""
    config = {
        'opensearch': {
            'client': {
                'hosts': ['http://localhost:9200']
            }
        }
    }
    builder = Builder(configdict=config)
    info = builder.client.info()
    assert 'version' in info
    assert info['version']['distribution'] == 'opensearch'
```

#### 4.2 Integration Tests

Test against real OpenSearch instance:

```bash
# Start OpenSearch
docker run -d -p 9200:9200 -p 9600:9600 \
  -e "discovery.type=single-node" \
  -e "DISABLE_SECURITY_PLUGIN=true" \
  opensearchproject/opensearch:3.2.0

# Run tests
pytest tests/test_opensearch_client.py -v
```

## Configuration Schema Updates

### Old (Elasticsearch)
```yaml
elasticsearch:
  client:
    hosts: http://localhost:9200
    # ... other options
```

### New (OpenSearch)
```yaml
opensearch:
  client:
    hosts: http://localhost:9200
    # ... other options
```

**Note:** The `Builder` class will need to accept `opensearch` key instead of `elasticsearch`.

## Compatibility Considerations

### What Works Identically

✅ Connection parameters (hosts, ports)  
✅ SSL/TLS configuration  
✅ Basic authentication  
✅ Request timeouts  
✅ Connection pooling  

### What Needs Validation

⚠️ Cloud authentication (ES Cloud ID vs OpenSearch Service)  
⚠️ API key authentication format  
⚠️ AWS SigV4 authentication  
⚠️ Logger trace naming  

### What's Different

🔴 Client class name: `Elasticsearch` → `OpenSearch`  
🔴 Package name: `elasticsearch8` → `opensearchpy`  
🔴 Some configuration parameter names  

## Verification Checklist

After migration, verify:

- [ ] `import opensearch_client` works
- [ ] `Builder` class can be instantiated
- [ ] Client connection succeeds
- [ ] `client.info()` returns OpenSearch info
- [ ] Configuration validation works
- [ ] Schema checking works
- [ ] Logging functions correctly
- [ ] No references to `elasticsearch8` remain
- [ ] All type hints updated
- [ ] All docstrings updated

## Next Integration Steps

Once `opensearch_client/` is migrated:

1. **Update curator imports**
   ```python
   # OLD
   from es_client.builder import Builder
   from es_client.helpers.config import config_from_cli_args
   
   # NEW
   from opensearch_client.builder import Builder
   from opensearch_client.helpers.config import config_from_cli_args
   ```

2. **Update configuration keys**
   - Change `elasticsearch:` → `opensearch:` in YAML
   - Update CLI argument names
   - Update help text

3. **Test with curator**
   ```bash
   curator --config examples/curator.yml show_indices
   ```

## Timeline

**Week 1:**
- Days 1-2: Migrate core files (builder.py, config.py, utils.py)
- Days 3-4: Migrate supporting files (logging.py, defaults.py, etc.)
- Day 5: Update package metadata (__init__.py)

**Week 2:**
- Days 1-2: Write and run unit tests
- Days 3-4: Integration testing with OpenSearch 3.2.0
- Day 5: Fix any issues found during testing

**Total:** ~2 weeks for complete migration and testing

## Success Criteria

✅ All tests pass  
✅ Zero `elasticsearch8` references remain  
✅ Client connects to OpenSearch 3.2.0  
✅ Configuration validation works  
✅ Logging works correctly  
✅ Ready to integrate with curator  

---

**Status:** 🟡 **Ready to begin migration**  
**Next Step:** Start with `builder.py` - the core client building logic  
**Estimated Effort:** 1-2 weeks
