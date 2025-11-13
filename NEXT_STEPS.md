# OpenSearch Curator - Next Steps

**Date:** November 13, 2025  
**Current Status:** ✅ Migration Complete - 183/183 Tests Passing (100%)

---

## 🎯 Immediate Priorities

### 1. CI/CD Setup (HIGHEST PRIORITY)

**Goal:** Automated testing on every commit

**Tasks:**
1. Create `.github/workflows/test.yml`
   - Test matrix: Python 3.8-3.12 × OpenSearch 2.11, 3.0, 3.1, 3.2
   - Run integration tests against Docker OpenSearch
   - Upload coverage reports

2. Create `.github/workflows/lint.yml`
   - Run black, ruff, pylint, mypy
   - Enforce code quality standards

3. Create `.github/workflows/build.yml`
   - Build binary with cx_Freeze
   - Test Docker image builds
   - Validate package installation

**Expected Duration:** 2-3 days

**Reference:**
- See AGENTS.md section 6.7 for GitHub Actions examples
- Current CI: Only docs-build.yml (minimal)

---

### 2. Release Preparation (HIGH PRIORITY)

**Goal:** Prepare for v1.0.0 release

**Tasks:**
1. **Version Update**
   - Current: `curator/_version.py` shows 8.0.21
   - Update to: 1.0.0 (fresh start for OpenSearch fork)
   - Update all references in docs

2. **Changelog Creation**
   - Create CHANGELOG.md
   - Document migration from Elasticsearch Curator
   - List all 8 API fixes
   - Note new ConvertIndexToRemote action

3. **Release Notes**
   - Highlight OpenSearch 3.2.0 compatibility
   - List supported OpenSearch versions (2.0+)
   - Migration guide from Elasticsearch Curator
   - Breaking changes (if any)

4. **License Review**
   - Current: Apache 2.0 (from Elastic)
   - Add fork notice
   - Update copyright year
   - Verify es_client license compliance

**Expected Duration:** 1 week

---

### 3. Repository Cleanup (MEDIUM PRIORITY)

**Goal:** Remove redundant documentation, organize files

**Cleanup Tasks:**

#### Documentation Consolidation
Many overlapping documentation files exist. Consolidate to reduce confusion:

**KEEP (Primary Docs):**
- ✅ `README.rst` - Main project README
- ✅ `README_FIRST.md` - Quick start conventions (with links)
- ✅ `AGENTS.md` - Strategic analysis & migration complete
- ✅ `TESTING.md` - Comprehensive testing guide
- ✅ `OPENSEARCH_API_FIXES.md` - API compatibility reference
- ✅ `MIGRATION_PROGRESS.md` - Updated with 100% completion
- ✅ `CONTRIBUTING.md` - Contribution guidelines
- ✅ `LICENSE` - Apache 2.0 license

**CONSOLIDATE OR ARCHIVE:**
- 🔄 `OPENSEARCH_COMPATIBILITY.md` - Merge into OPENSEARCH_API_FIXES.md
- 🔄 `OPENSEARCH_PY_3.0.md` - Merge into OPENSEARCH_API_FIXES.md
- 🔄 `OPENSEARCH_CLIENT_MIGRATION_STATUS.md` - Merge into MIGRATION_PROGRESS.md
- 🔄 `INTEGRATION_TEST_RESULTS.md` - Outdated, info now in TESTING.md
- 🔄 `RECENT_UPDATES.md` - Outdated, info now in MIGRATION_PROGRESS.md
- 🔄 `QUICKSTART.md` - Merge into README.rst or README_FIRST.md
- 🔄 `README_OPENSEARCH.md` - Duplicate info, merge into main README.rst
- 🔄 `CONVERT_INDEX_TO_REMOTE_SUMMARY.md` - Move to docs/ or examples/
- 🔄 `DOCKER_TESTING.md` - Merge into TESTING.md
- 🔄 `MIGRATION_CHECKLIST.md` - Archive or remove (migration complete)
- 🔄 `DEVELOPMENT_CONVENTIONS.md` - Merge into CONTRIBUTING.md

**REMOVE (Temporary/Redundant):**
- ❌ `test_builder.py` - Temporary test file (root directory)
- ❌ `test_connection.py` - Temporary test file (root directory)
- ❌ `load_env.py` - Already in scripts/ or handled by run_tests.ps1

**CREATE NEW DIRECTORY:**
```
docs/migration/
  ├── ELASTICSEARCH_TO_OPENSEARCH.md (consolidation of migration docs)
  └── API_CHANGES.md (from OPENSEARCH_API_FIXES.md)
```

#### Scripts Organization
- ✅ Keep: `run_tests.ps1`, `run_curator.py`, `run_es_repo_mgr.py`, `run_singleton.py`
- 🔄 Move to scripts/: `post4docker.py`, `alpine4docker.sh`
- 🔄 Document purpose of each script in scripts/README.md

---

### 4. Code Quality Improvements (MEDIUM PRIORITY)

**Goal:** Clean up technical debt

**Tasks:**
1. **Remove six library**
   - Currently used for Python 2/3 compatibility
   - Python 3.8+ only, no longer needed
   - Find and replace all `six.*` usage

2. **Type Hints**
   - Add comprehensive type hints
   - Run mypy with strict mode
   - Document any remaining type: ignore

3. **Docstring Updates**
   - Change "Elasticsearch" → "OpenSearch" in docstrings
   - Update examples in docstrings
   - Ensure all public APIs documented

4. **Code Comments**
   - Review inline comments for Elasticsearch references
   - Update technical comments with OpenSearch terminology

**Expected Duration:** 1-2 weeks

---

### 5. Multi-Version Testing (MEDIUM PRIORITY)

**Goal:** Validate against multiple OpenSearch versions

**Tasks:**
1. **Test Matrix Setup**
   - OpenSearch 2.11 (last 2.x)
   - OpenSearch 3.0 (first 3.x)
   - OpenSearch 3.1
   - OpenSearch 3.2 (current)

2. **Feature Validation**
   - Document which features work on which versions
   - Test ConvertIndexToRemote (3.x only?)
   - Test snapshot/restore across versions

3. **Compatibility Matrix**
   - Create table in README.rst
   - Document minimum versions for each action
   - Note any version-specific behavior

**Expected Duration:** 3-4 days

---

### 6. Community & Distribution (LOW PRIORITY)

**Goal:** Prepare for open-source distribution

**Tasks:**
1. **PyPI Publication**
   - Register `opensearch-curator` package name
   - Configure hatch publishing
   - Test with TestPyPI first
   - Publish v1.0.0 to production PyPI

2. **Docker Hub**
   - Create opensearch-curator Docker image
   - Multi-arch support (amd64, arm64)
   - Automated builds on release tags
   - Published to Docker Hub or GHCR

3. **GitHub Repository**
   - Finalize repository description
   - Add topics/tags (opensearch, python, index-management)
   - Configure GitHub Pages for docs
   - Add shields/badges (tests, coverage, PyPI version)

4. **Community Engagement**
   - Announce on OpenSearch forums
   - Submit to awesome-opensearch list
   - Create discussion board for issues
   - Set up contributing guidelines

**Expected Duration:** 1-2 weeks

---

## 📋 Suggested Task Order

### Week 1: CI/CD & Cleanup
- [ ] Day 1-2: Set up GitHub Actions workflows
- [ ] Day 3-4: Repository documentation cleanup
- [ ] Day 5: Run full test suite in CI, validate

### Week 2: Release Prep
- [ ] Day 1-2: Update version, create CHANGELOG.md
- [ ] Day 3-4: Multi-version testing (OpenSearch 2.11, 3.0, 3.1, 3.2)
- [ ] Day 5: Write release notes, prepare v1.0.0-rc1

### Week 3: Quality & Documentation
- [ ] Day 1-3: Code quality improvements (six removal, type hints)
- [ ] Day 4-5: Docstring and comment updates

### Week 4: Release & Distribution
- [ ] Day 1-2: Release v1.0.0-rc1, gather feedback
- [ ] Day 3-4: Fix any issues, prepare v1.0.0 stable
- [ ] Day 5: Publish to PyPI, Docker Hub, announce

---

## 🔍 Open Questions

1. **Package Name:** Confirm `opensearch-curator` is available on PyPI
2. **Docker Registry:** Docker Hub vs GitHub Container Registry?
3. **Documentation Hosting:** ReadTheDocs vs GitHub Pages?
4. **OpenSearch Versions:** Which versions to officially support? (2.0+?)
5. **Security Testing:** Need security scanning in CI?
6. **License Fork Notice:** Exact wording for fork from Elasticsearch Curator?

---

## 📚 References

- **Testing Guide:** TESTING.md
- **API Fixes:** OPENSEARCH_API_FIXES.md
- **Strategic Overview:** AGENTS.md
- **Migration Status:** MIGRATION_PROGRESS.md
- **Quick Conventions:** README_FIRST.md

---

**Maintainer:** Development Team  
**Last Updated:** November 13, 2025  
**Status:** Ready for CI/CD and Release Preparation
