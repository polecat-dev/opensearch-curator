# OpenSearch Curator - Project Summary

## What We Have

This repository contains a complete copy of **Elasticsearch Curator v8.0.21**, ready to be adapted for OpenSearch 3.2.0 compatibility.

### Repository Contents

- **362 files** copied from https://github.com/elastic/curator (tag: v8.0.21)
- Complete Python package structure with all source code
- Tests (unit and integration)
- Documentation (Sphinx-based)
- Examples and configuration templates
- Build system (Hatch/hatchling)
- Docker build files (cx_Freeze-based binary builder)

---

## Key Analysis Documents Created

I've created three comprehensive planning documents to guide the OpenSearch migration:

### 1. `AGENTS.md` - Strategic Analysis & Future Directions

**Purpose:** High-level strategic planning and architectural overview

**Key Sections:**
- Complete repository structure map
- Technology stack inventory (Hatch, pytest, black, mypy, ruff, Sphinx)
- Elasticsearch integration analysis (30+ import points identified)
- CI/CD infrastructure assessment
- Migration strategy for OpenSearch 3.2.0
- Risk assessment (high/medium/low risk components)
- Development roadmap (10-week timeline)
- Key decision points (naming, versioning, backward compatibility)

**Size:** 14 sections, ~650 lines

### 2. `MIGRATION_CHECKLIST.md` - Quick Reference Guide

**Purpose:** Practical checklist for developers doing the migration work

**Key Sections:**
- Critical dependencies to replace (elasticsearch8 → opensearch-py)
- File-by-file change requirements (38 files marked by risk level)
- Configuration changes (YAML structure updates)
- Testing strategy with Docker setup
- CI/CD options (GitHub Actions, GitLab CI, or manual)
- Documentation update list
- Known issues & gotchas (ILM, data tiers, terminology changes)
- Quick start commands

**Size:** Comprehensive task list with code examples

### 3. `OPENSEARCH_COMPATIBILITY.md` - Technical Specification

**Purpose:** Deep technical details for implementation

**Key Sections:**
- Complete dependency replacement map
- Import-by-import replacement guide
- API compatibility matrix (what works, what needs validation, what's incompatible)
- Client initialization code changes
- Version detection logic overhaul
- Terminology updates (master → cluster_manager)
- Testing strategy (unit, integration, manual)
- Build & release process
- 6-phase implementation plan
- Risk mitigation strategies

**Size:** 12 sections, detailed code examples throughout

---

## Current State Summary

### What Works Out of the Box
✅ Build system (Hatch) - no changes needed  
✅ CLI framework (Click) - no changes needed  
✅ YAML parsing - no changes needed  
✅ Schema validation (Voluptuous) - no changes needed  
✅ Testing framework (pytest) - minimal changes needed  
✅ Documentation tools (Sphinx) - minimal changes needed  

### What Needs Complete Replacement
🔴 `elasticsearch8` Python client → `opensearch-py`  
🔴 `es_client` wrapper library → Fork or custom implementation  
🔴 Configuration structure → `elasticsearch:` → `opensearch:`  
🔴 Version detection → OpenSearch versioning format  
🔴 Terminology → master → cluster_manager  

### What Can Be Removed
🗑️ ILM (Index Lifecycle Management) - Elasticsearch-specific  
🗑️ `cold2frozen.py` action - Data tier system doesn't exist in OpenSearch  
🗑️ X-Pack references - OpenSearch uses Security Plugin  
🗑️ `six` library - Python 2/3 compatibility no longer needed  

---

## Tools & Technologies Used

### Build & Package Management
- **Hatch** - Modern Python project manager (replaces setup.py)
- **hatchling** - Build backend
- **pyproject.toml** - Centralized configuration (PEP 518/621)

### Development Tools
- **pytest** >=7.2.1 - Testing framework
- **pytest-cov** - Code coverage
- **black** >=24.3.0 - Code formatter
- **mypy** >=1.8.0 - Static type checker
- **ruff** >=0.5.1 - Fast linter
- **pylint** >=3.1.0 - Code quality

### Documentation
- **Sphinx** >=5.3.0 - Documentation generator
- **sphinx_rtd_theme** - Read the Docs theme

### Binary Building
- **cx_Freeze** - Creates standalone executables
- **Docker** - Multi-stage Alpine builds

---

## CI/CD Status

### Current State
⚠️ **Minimal CI** - Only documentation workflows found:
- `.github/workflows/docs-build.yml` - Build docs
- `.github/workflows/docs-cleanup.yml` - Clean old docs
- No test workflow in repository (may have been removed)

### Recommendation
✅ **Replace with full CI/CD pipeline**

**Option 1: GitHub Actions** (Recommended)
- Free for public repositories
- Excellent OpenSearch support via Docker services
- Test matrix for Python 3.8-3.12 × OpenSearch 2.11-3.2
- Automated PyPI publishing on release
- Docker image builds

**Option 2: GitLab CI**
- Good if already using GitLab
- Similar capabilities to GitHub Actions

**Option 3: No CI**
- Manual testing only
- Suitable for small projects or personal use
- Delete `.github/workflows/` entirely

---

## OpenSearch Compatibility Plan

### What Works Identically

✅ **Index Operations** - All basic CRUD operations  
✅ **Snapshot/Restore** - Full compatibility  
✅ **Cluster Health** - API identical  
✅ **Close/Open Indices** - No changes needed  

### What Needs Validation

⚠️ **Index Templates** - Composable templates may differ slightly  
⚠️ **Allocation Rules** - Syntax validation needed  
⚠️ **Reindex** - Edge cases to test  
⚠️ **Force Merge** - Parameter validation  

### What's Incompatible

🔴 **ILM** - OpenSearch uses ISM (Index State Management) instead  
🔴 **Data Tiers** - cold2frozen concept doesn't exist  
🔴 **X-Pack** - Replace with OpenSearch Security Plugin  
🔴 **Frozen Indices** - Not in OpenSearch  

---

## Version Support

### Current (Elasticsearch)
- **Minimum:** Elasticsearch 7.14.0
- **Maximum:** Elasticsearch 8.99.99 (all 8.x versions)
- **Client:** elasticsearch8 (official Python client)

### Proposed (OpenSearch)
- **Minimum:** OpenSearch 2.0.0
- **Maximum:** OpenSearch 3.99.99 (all 3.x versions)
- **Client:** opensearch-py >=3.0.0 (official Python client v3.0.0+)
- **Target Version:** OpenSearch 3.2.0

**Note:** OpenSearch diverged from Elasticsearch after 7.10.2. Version numbers are completely independent. We're using opensearch-py 3.0.0+ for best compatibility and latest features.

---

## Timeline & Effort Estimate

### Total Time: 8-10 Weeks

**Phase 1: Preparation** (Week 1)
- Set up OpenSearch 3.2.0 environment
- Research opensearch-py API
- Decide on es_client replacement strategy

**Phase 2: Core Migration** (Week 2-3)
- Replace elasticsearch8 imports
- Update client initialization
- Modify version detection
- Update configuration schema

**Phase 3: Action Validation** (Week 4-5)
- Test all 16 actions
- Remove incompatible features
- Update API calls

**Phase 4: Testing** (Week 6-7)
- Unit tests
- Integration tests (multi-version)
- Performance testing

**Phase 5: Documentation** (Week 8)
- Update README and all docs
- Create migration guide
- Update examples

**Phase 6: Release** (Week 9-10)
- Set up CI/CD
- Build Docker image
- Publish to PyPI
- Tag v1.0.0

---

## Key Decision Points

### 1. Package Name
**Options:**
- `opensearch-curator` ← **Recommended** (clear, unambiguous)
- `curator-opensearch` (emphasizes Curator brand)
- `curator` (if official fork)

### 2. Starting Version
**Options:**
- `1.0.0` ← **Recommended** (fresh start, clear compatibility)
- `8.1.0` (continue from ES Curator)
- `3.0.0` (match OpenSearch major)

### 3. es_client Replacement
**Options:**
- **Option A:** Fork es_client library ← **Faster, less risk**
- **Option B:** Build custom wrapper ← **More control, more work**

Decision needed before starting Phase 2.

### 4. Backward Compatibility
**Options:**
- **Option A:** OpenSearch-only ← **Recommended** (simpler, clearer)
- **Option B:** Dual-mode (detect cluster type)
- **Option C:** Separate branches

### 5. CI/CD Platform
**Options:**
- **GitHub Actions** ← **Recommended** (free, excellent support)
- GitLab CI
- Self-hosted
- No CI (manual only)

---

## Next Steps

### Immediate Actions (This Week)

1. **Review Planning Documents**
   - Read `AGENTS.md` for strategic overview
   - Read `MIGRATION_CHECKLIST.md` for task list
   - Read `OPENSEARCH_COMPATIBILITY.md` for technical details

2. **Set Up Development Environment**
   ```bash
   # Install Hatch
   pip install hatch
   
   # Start OpenSearch 3.2.0 (Docker)
   docker run -d -p 9200:9200 -p 9600:9600 \
     -e "discovery.type=single-node" \
     -e "DISABLE_SECURITY_PLUGIN=true" \
     opensearchproject/opensearch:3.2.0
   
   # Verify OpenSearch is running
   curl http://localhost:9200
   ```

3. **Make Key Decisions**
   - Choose package name
   - Choose starting version
   - Decide on es_client replacement strategy
   - Choose CI/CD platform

4. **Create Development Branch**
   ```bash
   git checkout -b opensearch-migration
   ```

### First Development Task

**Start with:** Dependency replacement

1. Update `pyproject.toml`:
   ```toml
   [project]
   name = "opensearch-curator"
   version = "1.0.0"
   dependencies = [
       "opensearch-py>=3.0.0,<4.0.0",  # Use opensearch-py 3.0.0+
       "click>=8.1.0",
       "PyYAML>=6.0",
       "voluptuous>=0.14.1",
       "certifi>=2023.11.17",
   ]
   ```

2. Replace imports in `curator/helpers/testers.py`:
   ```python
   # OLD
   from elasticsearch8 import Elasticsearch
   
   # NEW
   from opensearchpy import OpenSearch
   ```

3. Test basic connection:
   ```python
   from opensearchpy import OpenSearch
   
   client = OpenSearch(
       hosts=['localhost:9200'],
       use_ssl=False,
   )
   
   print(client.info())
   ```

---

## Success Criteria

- [ ] Zero dependencies on elasticsearch8 or es_client
- [ ] All unit tests pass
- [ ] Integration tests pass on OpenSearch 2.11, 3.0, 3.2
- [ ] Python 3.8-3.12 compatibility verified
- [ ] All 16 actions work (except removed ones)
- [ ] Documentation complete and accurate
- [ ] CI/CD pipeline functional
- [ ] PyPI package published
- [ ] Docker image available

---

## Resources

### Documentation
- OpenSearch Docs: https://opensearch.org/docs/latest/
- opensearch-py Client: https://opensearch.org/docs/latest/clients/python/
- Original Curator: https://github.com/elastic/curator

### Code Repositories
- OpenSearch: https://github.com/opensearch-project/OpenSearch
- opensearch-py: https://github.com/opensearch-project/opensearch-py
- Original Curator: https://github.com/elastic/curator

### Community
- OpenSearch Forums: https://forum.opensearch.org/
- Slack: https://opensearch.org/slack.html

---

## Questions?

### Technical Questions
- Review `OPENSEARCH_COMPATIBILITY.md` for detailed technical guidance
- Check API compatibility matrix
- Test against local OpenSearch instance

### Process Questions
- Review `AGENTS.md` for strategic direction
- Check development roadmap
- Review risk assessment

### Implementation Questions
- Use `MIGRATION_CHECKLIST.md` as task guide
- Follow file-by-file change requirements
- Run suggested tests after each change

---

**Status:** ✅ **Planning Complete - Ready for Development**  
**Next Milestone:** Phase 1 - Preparation (Week 1)  
**Blocker:** Need decision on es_client replacement strategy  
**Owner:** Development Team
