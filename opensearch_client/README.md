# OpenSearch Client

This is an OpenSearch-compatible version of the `es_client` library, adapted from v8.19.5.

## Source

- **Original:** https://github.com/untergeek/es_client
- **Version:** v8.19.5
- **License:** Apache 2.0 (see LICENSE.es_client)
- **Original Author:** Aaron Mildenstein

## Purpose

This module provides a wrapper around the `opensearch-py` client library, offering:

- Configuration validation
- Schema checking
- Logging utilities
- CLI helpers
- Connection building

## Migration Status

**Status:** ✅ Core migration complete - Now uses `opensearch-py` 3.0.0 client

**Target:** `opensearch-py>=3.0.0,<4.0.0` (latest major version)

### Files Requiring Changes

The following files contain `elasticsearch8` imports that need to be replaced with `opensearch-py`:

1. **builder.py** (3 imports)
   - `import elasticsearch8` → `import opensearchpy`
   - Creates `elasticsearch8.Elasticsearch` client
   - Main client builder logic

2. **config.py** (2 imports)
   - `from elasticsearch8 import Elasticsearch`
   - Client validation logic

3. **utils.py** (2 imports)
   - `from elasticsearch8 import Elasticsearch`
   - Type hints and utilities

4. **cli_example.py** (1 import)
   - `from elasticsearch8.exceptions import BadRequestError, NotFoundError`
   - Example code (can be updated or removed)

5. **logging.py** (2 references)
   - `logging.getLogger("elasticsearch8.trace")`
   - Logger name needs update to `opensearch.trace` or similar

6. **defaults.py** (documentation only)
   - References to `elasticsearch8.Elasticsearch` in docstrings
   - Update documentation strings

### Migration Tasks

- [x] Replace all `elasticsearch8` imports with `opensearchpy` ✅
- [x] Update client instantiation: `elasticsearch8.Elasticsearch()` → `opensearchpy.OpenSearch()` ✅
- [x] Update exception imports: `elasticsearch8.exceptions.*` → `opensearchpy.exceptions.*` ✅
- [x] Update logger names: `elasticsearch8.trace` → `opensearch.trace` ✅
- [x] Update all docstrings referencing Elasticsearch ✅
- [ ] Test all functionality against OpenSearch 3.2.0
- [ ] Verify opensearch-py 3.0.0 compatibility

### Import Replacement Map

```python
# OLD (Elasticsearch)
import elasticsearch8
from elasticsearch8 import Elasticsearch
from elasticsearch8.exceptions import BadRequestError, NotFoundError

# NEW (OpenSearch)
import opensearchpy
from opensearchpy import OpenSearch
from opensearchpy.exceptions import BadRequestError, NotFoundError
```

### Class/Method Changes

```python
# OLD
client = elasticsearch8.Elasticsearch(**client_args)

# NEW
client = opensearchpy.OpenSearch(**client_args)
```

### Logger Changes

```python
# OLD
logging.getLogger("elasticsearch8.trace")

# NEW
logging.getLogger("opensearch.trace")  # Or keep as-is if opensearch-py uses same name
```

## Next Steps

1. Start with `builder.py` - the core client building logic
2. Update `config.py` - configuration validation
3. Update `utils.py` - utility functions
4. Update logging in `logging.py`
5. Update docstrings in `defaults.py`
6. Test against OpenSearch 3.2.0
7. Update `__init__.py` to reflect OpenSearch branding

## Testing

After migration, test:

1. **Basic Connection**
   ```python
   from opensearch_client import Builder
   config = {'opensearch': {'client': {'hosts': ['http://localhost:9200']}}}
   builder = Builder(configdict=config)
   print(builder.client.info())
   ```

2. **Schema Validation**
   - Test config validation works with OpenSearch parameters
   - Verify SSL/TLS options

3. **Logging**
   - Verify logging setup works correctly
   - Check trace logging

4. **CLI Integration**
   - Test with curator CLI
   - Verify all options work

## Compatibility Notes

### OpenSearch vs Elasticsearch Client Differences

Most parameters are compatible, but watch for:

1. **Connection Parameters**
   - OpenSearch uses `use_ssl` instead of some ES parameters
   - AWS signature authentication different

2. **API Methods**
   - Most APIs identical
   - Some ES-specific APIs don't exist in OpenSearch

3. **Cluster Manager vs Master**
   - OpenSearch renamed `master_timeout` → `cluster_manager_timeout`
   - Both are accepted for backward compatibility

## Version

- **Original es_client:** v8.19.4
- **OpenSearch Client:** v1.0.0
- **Target opensearch-py:** 3.0.0+

### opensearch-py 3.0.0 Changes

The 3.0.0 release of opensearch-py includes:
- Full support for OpenSearch 2.x and 3.x
- Improved type hints
- Better async support
- Enhanced security features
- API compatibility with OpenSearch 3.2.0

## License

Apache License 2.0 - See LICENSE.es_client for original copyright and LICENSE for this adaptation.
