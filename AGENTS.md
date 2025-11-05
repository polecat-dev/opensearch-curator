# OpenSearch Curator - Strategic Analysis & Migration Plan

**Version:** Based on Elasticsearch Curator v8.0.21  
**Target:** OpenSearch 3.2.0 Compatibility  
**Date:** Generated for Planning & Development Roadmap

---

## 1. Current Repository Structure

### 1.1 Core Architecture

The repository follows a modular Python package structure:

```
opensearch-curator/
├── curator/                    # Main package
│   ├── actions/                # Action implementations (16 files)
│   │   ├── alias.py
│   │   ├── allocation.py
│   │   ├── close.py
│   │   ├── cluster_routing.py
│   │   ├── cold2frozen.py
│   │   ├── create_index.py
│   │   ├── delete_indices.py
│   │   ├── forcemerge.py
│   │   ├── index_settings.py
│   │   ├── open.py
│   │   ├── reindex.py
│   │   ├── replicas.py
│   │   ├── rollover.py
│   │   ├── shrink.py
│   │   ├── snapshot.py
│   │   └── __init__.py
│   ├── cli_singletons/         # Individual CLI commands
│   ├── defaults/               # Default settings and schemas
│   │   └── settings.py         # VERSION_MIN, VERSION_MAX constants
│   ├── helpers/                # Utility functions (6 files)
│   │   ├── date_ops.py
│   │   ├── getters.py
│   │   ├── testers.py
│   │   ├── utils.py
│   │   ├── waiters.py
│   │   └── __init__.py
│   ├── validators/             # Schema validators
│   │   ├── actions.py
│   │   ├── filter_functions.py
│   │   └── ...
│   ├── __init__.py             # Package exports
│   ├── _version.py             # Version: 8.0.21
│   ├── cli.py                  # Main CLI interface
│   ├── classdef.py             # Base classes
│   ├── exceptions.py           # Custom exceptions
│   ├── indexlist.py            # Index management
│   ├── repomgrcli.py           # Repository manager CLI
│   ├── singletons.py           # Singleton utilities
│   └── snapshotlist.py         # Snapshot management
├── tests/
│   ├── unit/                   # Unit tests
│   └── integration/            # Integration tests
├── docs/                       # Sphinx documentation
├── examples/                   # YAML configuration examples
│   ├── curator.yml             # Main config example
│   └── actions/                # Action YAML examples
├── docker_test/                # Docker testing scripts
├── pyproject.toml              # Build & dependency config
├── Dockerfile                  # cx_Freeze binary builder
├── pytest.ini                  # pytest configuration
├── mypy.ini                    # Type checking config
└── README.rst                  # Project README
```

### 1.2 Entry Points

Three command-line tools are defined in `pyproject.toml`:

1. **`curator`** - Main index/snapshot management tool
2. **`curator_cli`** - Single-action CLI interface
3. **`es_repo_mgr`** - Repository management CLI

---

## 2. Technology Stack & Tools

### 2.1 Build System

- **Hatch / Hatchling** (modern Python project manager)
  - Defined in `pyproject.toml` under `[build-system]`
  - Replaces legacy `setup.py` with declarative config
  - Build command: `hatch build`
  - Test runner: Uses test matrix for Python 3.8-3.12

### 2.2 Core Dependencies

| Dependency | Version | Purpose | Migration Impact |
|------------|---------|---------|------------------|
| `es_client` | 8.17.5 | **Elasticsearch client wrapper** | **🔴 REPLACE** with OpenSearch equivalent |
| `elasticsearch8` | * | Official Elasticsearch Python client | **🔴 REPLACE** with `opensearch-py` |
| `click` | >=8.1.0 | CLI framework | ✅ Keep as-is |
| `PyYAML` | >=6.0 | YAML parsing | ✅ Keep as-is |
| `voluptuous` | >=0.14.1 | Schema validation | ✅ Keep as-is |
| `certifi` | >=2023.11.17 | SSL certificates | ✅ Keep as-is |
| `six` | >=1.16.0 | Python 2/3 compatibility | ⚠️ Consider removing (Python 3.8+ only) |

### 2.3 Development Tools

| Tool | Version | Purpose |
|------|---------|---------|
| `pytest` | >=7.2.1 | Unit testing framework |
| `pytest-cov` | * | Code coverage reporting |
| `black` | >=24.3.0 | Code formatter |
| `mypy` | >=1.8.0 | Static type checker |
| `ruff` | >=0.5.1 | Fast Python linter |
| `pylint` | >=3.1.0 | Code quality analyzer |

### 2.4 Documentation Tools

- **Sphinx** >=5.3.0 - Documentation generator
- **sphinx_rtd_theme** - Read the Docs theme
- Current docs hosted at: `https://www.elastic.co/guide/en/elasticsearch/client/curator`

### 2.5 Binary Build System

- **cx_Freeze** - Creates standalone binary executables
- Used in `Dockerfile` to build Alpine Linux binaries
- Platform-dependent architecture handling via `alpine4docker.sh`

---

## 3. Elasticsearch Integration Points

### 3.1 Direct `elasticsearch8` Imports

Found in multiple files (requires full replacement):

```python
# curator/repomgrcli.py
from elasticsearch8 import ApiError, NotFoundError

# curator/indexlist.py
from elasticsearch8.exceptions import NotFoundError, TransportError

# curator/helpers/testers.py
from elasticsearch8 import Elasticsearch
from elasticsearch8.exceptions import NotFoundError

# curator/helpers/getters.py
from elasticsearch8 import exceptions as es8exc

# curator/helpers/date_ops.py
from elasticsearch8.exceptions import NotFoundError

# curator/helpers/waiters.py
from elasticsearch8.exceptions import GeneralAvailabilityWarning
```

### 3.2 `es_client` Library Usage

Extensive use throughout codebase:

```python
# Configuration & Setup
from es_client.helpers.config import (
    config_from_cli_args,
    generate_configdict,
    cli_opts
)
from es_client.builder import Builder
from es_client.helpers.logging import configure_logging

# Schema Validation
from es_client.helpers.schemacheck import SchemaCheck, password_filter

# Utilities
from es_client.helpers.utils import (
    ensure_list,
    option_wrapper,
    prune_nones
)

# Defaults
from es_client.defaults import LOGGING_SETTINGS, SHOW_OPTION, OPTION_DEFAULTS
```

### 3.3 Version Constraints

In `curator/defaults/settings.py`:

```python
VERSION_MIN = (7, 14, 0)  # Minimum Elasticsearch version
VERSION_MAX = (8, 99, 99)  # Maximum Elasticsearch version
```

**Migration Note:** OpenSearch versioning diverged from Elasticsearch at v7.10.2. OpenSearch 3.x is completely independent.

### 3.4 Client Initialization Pattern

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
    # ... other SSL options
  other_settings:
    master_only:
    skip_version_test:
    username:
    password:
    api_key:
      id:
      api_key:
```

This configuration structure is specific to `es_client` wrapper and needs OpenSearch adaptation.

---

## 4. CI/CD Infrastructure

### 4.1 Current GitHub Actions

Located in `.github/workflows/`:

- **`docs-build.yml`** - Builds documentation (likely for ReadTheDocs)
- **`docs-cleanup.yml`** - Cleans up old docs
- ⚠️ **Note:** No `test.yml` found in repository (may have been removed or in different branch)

### 4.2 Docker Build System

`Dockerfile` uses multi-stage build:

1. **Builder stage** - Python 3.12.9 Alpine 3.21
   - Installs build tools (gcc, musl-dev, openssl-dev, patchelf)
   - Runs `cxfreeze build` to create frozen binary
   - Uses `alpine4docker.sh` for platform-specific linking

2. **Runtime stage** - Minimal Alpine
   - Copies frozen binary from builder
   - Runs as `nobody:nobody` user
   - Entry point: `/curator/curator`

### 4.3 Testing Configuration

**`pytest.ini`:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**`mypy.ini`:**
- Type checking enabled
- Strict mode configurations

### 4.4 ReadTheDocs Integration

`.readthedocs.yaml` present (exact config not yet examined)

---

## 5. Current Elasticsearch Version Support

From `README.rst` and code analysis:

- **Elasticsearch 7.14.0 - 7.17.x** - Full support
- **Elasticsearch 8.x** - Full support (all 8.x versions)
- Uses `es_client` library v8.17.5
- Client configuration has migrated to nested `elasticsearch.client` structure

---

## 6. Migration Strategy for OpenSearch 3.2.0

### 6.1 Phase 1: Dependency Replacement (CRITICAL)

#### Replace `elasticsearch8` with `opensearch-py`

**Current imports to replace:**

| Current | OpenSearch Equivalent |
|---------|----------------------|
| `elasticsearch8` | `opensearchpy` or `opensearch` |
| `elasticsearch8.Elasticsearch` | `opensearchpy.OpenSearch` |
| `elasticsearch8.exceptions.NotFoundError` | `opensearchpy.exceptions.NotFoundError` |
| `elasticsearch8.exceptions.TransportError` | `opensearchpy.exceptions.TransportError` |
| `elasticsearch8.exceptions.ApiError` | `opensearchpy.exceptions.ApiError` |

**Files requiring changes:**
- `curator/repomgrcli.py`
- `curator/indexlist.py`
- `curator/helpers/testers.py`
- `curator/helpers/getters.py`
- `curator/helpers/date_ops.py`
- `curator/helpers/waiters.py`

#### Replace or Fork `es_client`

**✅ DECISION MADE: Copied `es_client` v8.19.5 to `opensearch_client/`**

We've copied the `es_client` library source code (17 files) into our project as `opensearch_client/`:
- Source: https://github.com/untergeek/es_client v8.19.5
- Location: `opensearch_client/` in this repository
- License: Apache 2.0 (preserved in `LICENSE.es_client`)

**Migration Required:**
- Replace `elasticsearch8` imports with `opensearchpy` (24 occurrences)
- Update client instantiation: `Elasticsearch()` → `OpenSearch()`
- Update exception imports
- Update logger names (`elasticsearch8.trace` → `opensearch.trace`)
- See `opensearch_client/README.md` for detailed migration tasks

#### Update `pyproject.toml`

```toml
[project]
name = "opensearch-curator"  # Rename from elasticsearch-curator
dependencies = [
    "opensearch-py>=3.0.0,<4.0.0",  # Replace elasticsearch8 (use v3.0.0+)
    "click>=8.1.0",
    "PyYAML>=6.0",
    "voluptuous>=0.14.1",
    "certifi>=2023.11.17",
    # opensearch_client is now bundled, no external dependency needed
]
```

### 6.2 Phase 2: Version Validation Updates

#### Update Version Constants

In `curator/defaults/settings.py`:

```python
# Old Elasticsearch versions
# VERSION_MIN = (7, 14, 0)
# VERSION_MAX = (8, 99, 99)

# New OpenSearch versions
VERSION_MIN = (2, 0, 0)  # OpenSearch 2.0+
VERSION_MAX = (3, 99, 99)  # Support OpenSearch 3.x
```

#### Update Version Check Logic

Locate and update version checking code to:
1. Detect OpenSearch instead of Elasticsearch
2. Parse OpenSearch version format
3. Validate against OpenSearch compatibility matrix

### 6.3 Phase 3: API Compatibility Mapping

#### Identify Breaking Changes

OpenSearch diverged from Elasticsearch at 7.10.2. Key differences:

1. **API Endpoints:** Some endpoints renamed or restructured
2. **Security Plugin:** Different from Elasticsearch X-Pack
3. **Cluster Settings:** Some settings have different names
4. **Index Templates:** Composable templates work differently
5. **ILM Equivalent:** OpenSearch uses ISM (Index State Management)

#### Action-Specific Updates

Each action in `curator/actions/` needs audit:

- ✅ **Low Risk:** `close.py`, `open.py`, `delete_indices.py`
- ⚠️ **Medium Risk:** `allocation.py`, `replicas.py`, `snapshot.py`
- 🔴 **High Risk:** `cold2frozen.py` (Elasticsearch-specific tier concept)

### 6.4 Phase 4: Configuration Schema Updates

#### Update YAML Configuration Structure

Current `elasticsearch:` key → Change to `opensearch:`

```yaml
# OLD (Elasticsearch)
elasticsearch:
  client:
    hosts: https://...
  other_settings:
    master_only:

# NEW (OpenSearch)
opensearch:
  client:
    hosts: https://...
  other_settings:
    cluster_manager_only:  # OpenSearch renamed master → cluster_manager
```

#### Update CLI Arguments

In `curator/cli.py` and `curator/repomgrcli.py`:
- Rename options containing "elasticsearch"
- Update help text and descriptions
- Maintain backward compatibility flag if needed

### 6.5 Phase 5: Documentation & Branding

#### Update All References

- `README.rst` - Change "Elasticsearch" → "OpenSearch"
- `curator/__init__.py` docstring
- All `docs/*.md` files
- Configuration examples in `examples/`
- Error messages in `curator/exceptions.py`

#### Update Documentation URLs

```python
# curator/defaults/settings.py
# OLD:
CURATOR_DOCS = 'https://www.elastic.co/guide/en/elasticsearch/client/curator'

# NEW:
CURATOR_DOCS = 'https://opensearch.org/docs/latest/tools/curator'
# Or custom domain if self-hosting
```

#### Update License & Copyright

Review `LICENSE` file:
- Current: Apache License 2.0, Copyright 2011–2024 Elasticsearch
- New: Maintain Apache 2.0, add fork notice and new copyright

### 6.6 Phase 6: Testing Strategy

#### Unit Tests

- Update `tests/unit/testvars.py` with OpenSearch test config
- Mock OpenSearch client responses instead of Elasticsearch
- Test version detection logic against OpenSearch 2.x and 3.x

#### Integration Tests

- Spin up OpenSearch 3.2.0 in Docker
- Run full test suite against real OpenSearch cluster
- Validate all 16 actions work correctly
- Test repository operations (snapshots/restore)

#### Test Matrix

Update `pyproject.toml` test matrix:

```toml
[[tool.hatch.envs.test.matrix]]
python = ["3.8", "3.9", "3.10", "3.11", "3.12"]
opensearch = ["2.11", "2.12", "3.0", "3.1", "3.2"]  # Instead of ES versions
```

### 6.7 Phase 7: CI/CD Replacement

#### Option 1: GitHub Actions (Recommended)

Create new workflows in `.github/workflows/`:

**`test.yml`:**
```yaml
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]
        opensearch-version: ["2.11", "3.2"]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Start OpenSearch
        run: |
          docker run -d -p 9200:9200 -p 9600:9600 \
            -e "discovery.type=single-node" \
            -e "DISABLE_SECURITY_PLUGIN=true" \
            opensearchproject/opensearch:${{ matrix.opensearch-version }}
      - name: Install dependencies
        run: |
          pip install hatch
          hatch env create
      - name: Run tests
        run: hatch run test:pytest
```

**`build.yml`:**
```yaml
name: Build & Publish
on:
  release:
    types: [created]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build with Hatch
        run: hatch build
      - name: Publish to PyPI
        run: hatch publish
        env:
          HATCH_INDEX_USER: __token__
          HATCH_INDEX_AUTH: ${{ secrets.PYPI_TOKEN }}
```

**`docker.yml`:**
```yaml
name: Docker Build
on:
  release:
    types: [created]
jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t opensearch-curator:latest .
      - name: Push to Docker Hub
        run: |
          echo ${{ secrets.DOCKERHUB_TOKEN }} | docker login -u ${{ secrets.DOCKERHUB_USER }} --password-stdin
          docker push opensearch-curator:latest
```

#### Option 2: GitLab CI

If using GitLab, create `.gitlab-ci.yml`:

```yaml
stages:
  - test
  - build
  - deploy

test:
  stage: test
  image: python:3.12
  services:
    - name: opensearchproject/opensearch:3.2.0
      alias: opensearch
  script:
    - pip install hatch
    - hatch run test:pytest
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.8", "3.9", "3.10", "3.11", "3.12"]
```

#### Option 3: Minimal (No CI)

If CI is not needed:
- Delete `.github/workflows/` entirely
- Remove `docs-build.yml` and `docs-cleanup.yml`
- Keep local testing with `hatch run test:pytest`
- Manual releases only

### 6.8 Phase 8: Docker Image Updates

Update `Dockerfile`:

```dockerfile
# Update comments and labels
LABEL org.opencontainers.image.title="OpenSearch Curator"
LABEL org.opencontainers.image.description="Index and snapshot management for OpenSearch"
LABEL org.opencontainers.image.source="https://github.com/YOUR_ORG/opensearch-curator"

# Rest of build process remains largely the same
# cx_Freeze binary building works identically
```

---

## 7. Breaking Changes & Risk Assessment

### 7.1 High-Risk Areas

| Component | Risk Level | Reason |
|-----------|------------|--------|
| `cold2frozen.py` | 🔴 HIGH | Uses Elasticsearch tier system (not in OpenSearch) |
| Version checking | 🔴 HIGH | OpenSearch version format differs |
| Security settings | 🔴 HIGH | X-Pack vs OpenSearch Security Plugin |
| ILM features | 🔴 HIGH | OpenSearch uses ISM instead of ILM |

### 7.2 Medium-Risk Areas

| Component | Risk Level | Reason |
|-----------|------------|--------|
| Snapshot operations | ⚠️ MEDIUM | API mostly compatible, test thoroughly |
| Index templates | ⚠️ MEDIUM | Composable templates may differ |
| Cluster settings | ⚠️ MEDIUM | Some renamed (master → cluster_manager) |
| Allocation rules | ⚠️ MEDIUM | Routing allocation syntax changes |

### 7.3 Low-Risk Areas

| Component | Risk Level | Reason |
|-----------|------------|--------|
| Basic CRUD | ✅ LOW | Core index operations unchanged |
| Close/Open | ✅ LOW | Fully compatible |
| Replication | ✅ LOW | Replica settings same |
| Date operations | ✅ LOW | Pure Python logic, no API calls |

---

## 8. Development Roadmap

### Milestone 1: Foundation (Week 1-2)
- [x] Copy Elasticsearch Curator v8.0.21 repository ✅
- [x] Analyze structure and create this document ✅
- [x] Copy `es_client` library v8.19.5 to `opensearch_client/` ✅
- [x] Migrate `opensearch_client/` to use `opensearch-py` instead of `elasticsearch8` ✅
- [ ] Test `opensearch_client` against OpenSearch 3.2.0
- [ ] Update `pyproject.toml` with OpenSearch dependencies
- [ ] Set up local OpenSearch 3.2.0 test environment

### Milestone 2: Core Migration (Week 3-4)
- [ ] Replace all `elasticsearch8` imports with `opensearch-py`
- [ ] Update client initialization in `cli.py` and `repomgrcli.py`
- [ ] Modify version checking logic in `defaults/settings.py`
- [ ] Update configuration schema (elasticsearch → opensearch)
- [ ] Test basic connection and cluster info retrieval

### Milestone 3: Action Validation (Week 5-6)
- [ ] Audit each action in `curator/actions/` for compatibility
- [ ] Remove or stub `cold2frozen.py` (Elasticsearch-specific)
- [ ] Update snapshot operations for OpenSearch API
- [ ] Validate index lifecycle operations
- [ ] Test allocation and replica management

### Milestone 4: Testing & QA (Week 7-8)
- [ ] Update unit tests with OpenSearch mocks
- [ ] Run integration tests against OpenSearch 2.11, 3.0, 3.2
- [ ] Fix breaking changes discovered during testing
- [ ] Performance testing with large index counts
- [ ] Security plugin authentication testing

### Milestone 5: Documentation (Week 9)
- [ ] Update README.rst with OpenSearch branding
- [ ] Rewrite configuration documentation
- [ ] Update all example YAML files
- [ ] Create migration guide from Elasticsearch Curator
- [ ] Update API documentation (Sphinx)

### Milestone 6: CI/CD & Release (Week 10)
- [ ] Implement GitHub Actions workflows (or chosen CI)
- [ ] Set up automated Docker builds
- [ ] Configure PyPI publishing
- [ ] Create release checklist
- [ ] Tag v1.0.0-opensearch

---

## 9. Key Decision Points

### 9.1 Naming Convention
**Decision Required:** Package name on PyPI?
- Option A: `opensearch-curator` (clear fork)
- Option B: `curator-opensearch` (emphasizes Curator brand)
- Option C: `curator` (if original maintainers transfer/fork officially)

**Recommendation:** `opensearch-curator` - Clear purpose, avoids confusion

### 9.2 Version Numbering
**Decision Required:** Starting version?
- Option A: `1.0.0` (fresh start for OpenSearch)
- Option B: `8.1.0` (continue from Elasticsearch Curator 8.0.21)
- Option C: `3.0.0` (match OpenSearch major version)

**Recommendation:** `1.0.0` - Signals new project with different compatibility

### 9.3 Backward Compatibility
**Decision Required:** Support Elasticsearch fallback?
- Option A: OpenSearch-only (clean break)
- Option B: Dual-mode (detect cluster type, use appropriate client)
- Option C: Separate branches (elastic-curator vs opensearch-curator)

**Recommendation:** Option A - Simpler maintenance, clearer purpose

### 9.4 ILM/ISM Handling
**Decision Required:** How to handle Elasticsearch ILM features?
- Option A: Remove ILM entirely
- Option B: Stub ILM with deprecation warnings
- Option C: Build ISM (Index State Management) integration

**Recommendation:** Option A for MVP, Option C for future enhancement

### 9.5 CI/CD Platform
**Decision Required:** Where to run automated testing?
- Option A: GitHub Actions (free for public repos)
- Option B: GitLab CI (if using GitLab)
- Option C: Self-hosted Jenkins/other
- Option D: No CI (manual testing only)

**Recommendation:** Option A (GitHub Actions) - Industry standard, free, excellent OpenSearch support

---

## 10. Resources & References

### 10.1 OpenSearch Documentation
- Main Docs: https://opensearch.org/docs/latest/
- Python Client: https://opensearch.org/docs/latest/clients/python/
- API Reference: https://opensearch.org/docs/latest/api-reference/
- ISM Plugin: https://opensearch.org/docs/latest/im-plugin/ism/index/

### 10.2 Migration Guides
- Elasticsearch to OpenSearch: https://opensearch.org/docs/latest/migration/
- Breaking Changes: https://opensearch.org/docs/latest/breaking-changes/

### 10.3 Python Client Libraries
- `opensearch-py`: https://github.com/opensearch-project/opensearch-py
- API Coverage: https://opensearch.org/docs/latest/clients/python/#api-coverage

### 10.4 Original Curator Resources
- GitHub Repo: https://github.com/elastic/curator
- Documentation: https://www.elastic.co/guide/en/elasticsearch/client/curator
- `es_client` Library: https://github.com/elastic/es_client

---

## 11. Next Steps & Action Items

### Immediate Actions (This Week)
1. ✅ **Document created** - This file captures strategic plan
2. **Set up OpenSearch 3.2.0 locally** - Docker or native install
3. **Research `es_client` library** - Determine fork feasibility
4. **Create fork decision document** - es_client vs custom wrapper
5. **Set up development environment** - Python 3.12, Hatch, pytest

### Short-term Goals (Next Month)
1. Complete dependency replacement (`elasticsearch8` → `opensearch-py`)
2. Update configuration schema and CLI
3. Validate basic operations against OpenSearch 3.2.0
4. Run smoke tests on core actions (delete, close, snapshot)
5. Document all API differences discovered

### Long-term Vision (3-6 Months)
1. Feature parity with Elasticsearch Curator for compatible features
2. ISM (Index State Management) integration
3. OpenSearch-specific features (e.g., cold storage, anomaly detection indices)
4. Community feedback and feature requests
5. Production-ready release with full test coverage

---

## 12. Questions & Unknowns

### Technical Unknowns
- [ ] Does `opensearch-py` have feature parity with `elasticsearch8`?
- [ ] Are all Curator actions compatible with OpenSearch APIs?
- [ ] Performance characteristics of OpenSearch 3.x vs Elasticsearch 8.x?
- [ ] Breaking changes between OpenSearch 2.x → 3.x?

### Process Unknowns
- [ ] Will this be an official fork or independent project?
- [ ] License considerations for forking Elastic-licensed code?
- [ ] PyPI package name availability?
- [ ] Community interest in OpenSearch Curator?

### Resolved Questions
- ✅ **Can CI be ditched?** YES - Current CI is minimal (docs-only), easily replaced
- ✅ **Is Hatch the right build tool?** YES - Modern, well-supported, already configured
- ✅ **Python version support?** 3.8-3.12 reasonable for OpenSearch 3.2.0

---

## 13. Maintenance Notes

### File Modification Tracking
**This document should be updated when:**
- Major architectural decisions are made
- Dependencies are changed or updated
- Migration phases are completed
- New risks or blockers are identified
- OpenSearch releases new major versions

### Version History
- **v1.0** - Initial analysis based on Elasticsearch Curator 8.0.21
- **v1.1** - (Future) Post-dependency replacement updates
- **v2.0** - (Future) Post-OpenSearch 3.2.0 validation

---

## 14. Conclusion

**Current State:** We have successfully copied the entire Elasticsearch Curator v8.0.21 repository and analyzed its structure, dependencies, and architecture.

**Migration Feasibility:** ✅ **HIGHLY FEASIBLE** - The codebase is well-structured with clear separation of concerns. The main challenge is systematic replacement of Elasticsearch client libraries with OpenSearch equivalents.

**Biggest Challenges:**
1. **Dependency Replacement** - `es_client` and `elasticsearch8` are deeply integrated
2. **Version Detection** - OpenSearch versioning differs from Elasticsearch
3. **Feature Gaps** - Some Elasticsearch-specific features (ILM, cold2frozen) don't have direct OpenSearch equivalents

**Recommended Approach:**
- **Phase 1 Priority:** Fork `es_client` library for OpenSearch compatibility
- **MVP Scope:** Core index management (open, close, delete, snapshot, restore)
- **Future Enhancements:** ISM integration, OpenSearch-specific optimizations

**Timeline Estimate:** 8-10 weeks for production-ready v1.0.0

**CI/CD Decision:** ✅ **YES, replace current CI** - GitHub Actions recommended for automated testing against multiple OpenSearch versions.

---

**Document Maintainer:** AI Agent / Development Team  
**Last Updated:** Initial Creation  
**Status:** 🟢 Active Planning Document
