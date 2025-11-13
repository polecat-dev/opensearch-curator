# OpenSearch Curator Documentation

Welcome to the OpenSearch Curator documentation!

## 📚 Documentation Structure

```
docs/
├── README.md                    # This file - documentation index
├── STATUS.md                    # Current project status
├── NEXT_STEPS.md               # Roadmap and next priorities
├── CHANGELOG.md                # Release notes (symlink to ../CHANGELOG.md)
├── CONVERT_INDEX_TO_REMOTE.md  # ConvertIndexToRemote action guide
├── dev/                        # Development documentation
│   ├── AGENTS.md               # Strategic analysis & migration overview
│   ├── MIGRATION_PROGRESS.md   # Migration status (100% complete)
│   ├── OPENSEARCH_API_FIXES.md # API compatibility fixes (8 fixes)
│   ├── SESSION_SUMMARY.md      # Implementation session details
│   └── TESTING.md              # Comprehensive testing guide
└── archive/                    # Archived/legacy documentation
    └── [11 archived files]
```

---

## 🎯 Quick Navigation

### For New Users
- **Getting Started:** See main [README.rst](../README.rst)
- **Configuration Examples:** See [examples/](../examples/) directory
- **Quick Start:** See [README_FIRST.md](../README_FIRST.md) for conventions

### For Developers
- **Testing Guide:** [dev/TESTING.md](dev/TESTING.md) - How to run and debug tests
- **API Fixes:** [dev/OPENSEARCH_API_FIXES.md](dev/OPENSEARCH_API_FIXES.md) - OpenSearch-py 3.0 compatibility
- **Migration Story:** [dev/MIGRATION_PROGRESS.md](dev/MIGRATION_PROGRESS.md) - Complete migration history

### For Contributors
- **Contributing Guide:** [../CONTRIBUTING.md](../CONTRIBUTING.md)
- **Code Conventions:** [README_FIRST.md](../README_FIRST.md)
- **CI/CD Workflows:** [../.github/workflows/README.md](../.github/workflows/README.md)

### For Release Managers
- **Current Status:** [STATUS.md](STATUS.md) - Quick overview
- **Next Steps:** [NEXT_STEPS.md](NEXT_STEPS.md) - Release roadmap
- **Changelog:** [../CHANGELOG.md](../CHANGELOG.md) - Release notes

---

## 📖 Documentation by Topic

### Core Functionality

#### Actions
- **ConvertIndexToRemote:** [CONVERT_INDEX_TO_REMOTE.md](CONVERT_INDEX_TO_REMOTE.md)
- **All Actions:** See [../examples/actions/](../examples/actions/)

#### Configuration
- **YAML Examples:** [../examples/](../examples/)
- **Environment Setup:** [dev/TESTING.md#environment-setup](dev/TESTING.md)

### Development

#### Testing
- **Comprehensive Guide:** [dev/TESTING.md](dev/TESTING.md)
  - Running tests locally
  - Test infrastructure (Docker, LocalStack)
  - Common issues and solutions
  - Debugging strategies
  - CI/CD integration

#### API Compatibility
- **OpenSearch-py 3.0 Fixes:** [dev/OPENSEARCH_API_FIXES.md](dev/OPENSEARCH_API_FIXES.md)
  - 8 API compatibility fixes
  - Migration from elasticsearch8
  - Test environment requirements

#### Migration
- **Progress & History:** [dev/MIGRATION_PROGRESS.md](dev/MIGRATION_PROGRESS.md)
  - Phase 1: Dependency replacement
  - Phase 2: Testing & validation
  - Phase 3: API fixes
  - Phase 4: Documentation

### Project Management

#### Strategic Overview
- **AGENTS.md:** [dev/AGENTS.md](dev/AGENTS.md)
  - Repository structure analysis
  - Technology stack evaluation
  - Migration feasibility assessment
  - Timeline and milestones

#### Implementation Details
- **Session Summary:** [dev/SESSION_SUMMARY.md](dev/SESSION_SUMMARY.md)
  - What was accomplished
  - Files changed
  - Test results
  - Next actions

---

## 🚀 Quick Start Paths

### Path 1: I want to use OpenSearch Curator
1. Read [../README.rst](../README.rst) for overview
2. Check [../examples/](../examples/) for configuration examples
3. Review [STATUS.md](STATUS.md) for compatibility info

### Path 2: I want to run tests
1. Start with [dev/TESTING.md](dev/TESTING.md)
2. Follow the Quick Start section
3. Use `.\run_tests.ps1` (Windows) or `make test` (Linux/Mac)

### Path 3: I want to contribute
1. Read [../CONTRIBUTING.md](../CONTRIBUTING.md)
2. Check [README_FIRST.md](../README_FIRST.md) for conventions
3. Review [dev/TESTING.md](dev/TESTING.md) for testing requirements
4. See [../.github/workflows/README.md](../.github/workflows/README.md) for CI/CD

### Path 4: I want to understand the migration
1. Start with [dev/MIGRATION_PROGRESS.md](dev/MIGRATION_PROGRESS.md)
2. Review [dev/OPENSEARCH_API_FIXES.md](dev/OPENSEARCH_API_FIXES.md)
3. See [dev/AGENTS.md](dev/AGENTS.md) for strategic overview

### Path 5: I'm preparing a release
1. Check [STATUS.md](STATUS.md) for current state
2. Review [NEXT_STEPS.md](NEXT_STEPS.md) for roadmap
3. Update [../CHANGELOG.md](../CHANGELOG.md)
4. Follow release process in [../.github/workflows/README.md](../.github/workflows/README.md)

---

## 📊 Current Project Status

**Version:** 1.0.0  
**Migration:** ✅ 100% Complete  
**Tests:** ✅ 183/183 Passing (100%)  
**OpenSearch Compatibility:** 2.0+ (tested against 3.2.0)  
**Python Version:** 3.8+

See [STATUS.md](STATUS.md) for detailed status.

---

## 🔗 External Resources

- **GitHub Repository:** https://github.com/polecat-dev/opensearch-curator
- **Issue Tracker:** https://github.com/polecat-dev/opensearch-curator/issues
- **CI/CD Workflows:** https://github.com/polecat-dev/opensearch-curator/actions
- **Original Elasticsearch Curator:** https://github.com/elastic/curator

---

## 📝 Archive

Legacy and consolidated documentation has been moved to [archive/](archive/):
- OPENSEARCH_COMPATIBILITY.md
- OPENSEARCH_PY_3.0.md
- DOCKER_TESTING.md
- QUICKSTART.md
- README_OPENSEARCH.md
- CONVERT_INDEX_TO_REMOTE_SUMMARY.md
- DEVELOPMENT_CONVENTIONS.md
- And more...

These files contain historical information that has been consolidated into current documentation.

---

**Last Updated:** November 13, 2025  
**Maintainer:** Development Team
