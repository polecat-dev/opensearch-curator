# GitHub Actions CI/CD

This directory contains GitHub Actions workflows for automated testing, code quality checks, and releases.

## Workflows

### 🧪 test.yml - Integration Tests

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Test Matrix:**
- **Python versions:** 3.8, 3.9, 3.10, 3.11, 3.12
- **OpenSearch versions:** 2.11.1, 3.0.0, 3.1.0, 3.2.0

**Services:**
- OpenSearch (single-node, security disabled, path.repo=/tmp)
- LocalStack (for S3 repository testing)

**Steps:**
1. Set up Python environment
2. Install dependencies
3. Wait for OpenSearch to be healthy
4. Run integration tests (183 tests)
5. Generate coverage report (Python 3.12 + OpenSearch 3.2.0 only)
6. Upload to Codecov

**Environment Variables:**
- `TEST_ES_SERVER=https://localhost:19200`
- `TEST_S3_BUCKET=curator-test-bucket`
- `TEST_S3_ENDPOINT=http://localhost:4566`
- `AWS_ACCESS_KEY_ID=test`
- `AWS_SECRET_ACCESS_KEY=test`

**Expected Duration:** ~5-10 minutes per matrix job

---

### 🔍 lint.yml - Code Quality

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

**Checks:**
1. **Black** - Code formatting (strict)
2. **Ruff** - Fast Python linter (continue on error)
3. **MyPy** - Type checking (continue on error)
4. **Pylint** - Code quality analysis (informational)
5. **Bandit** - Security scanner (continue on error)

**Artifacts:**
- `bandit-security-report.json` - Security scan results

**Expected Duration:** ~2-3 minutes

---

### 🚀 build.yml - Build & Release

**Triggers:**
- Git tags matching `v*.*.*` (e.g., v1.0.0)
- Manual workflow dispatch

**Jobs:**

#### 1. build-wheel
- Build Python wheel and source distribution
- Verify installation
- Upload as artifact

#### 2. build-binary
- Build standalone binary using cx_Freeze (Docker)
- Extract binary from Docker container
- Upload as artifact

#### 3. build-docker
- Build multi-platform Docker image (amd64, arm64)
- Tag with version, major.minor, latest
- Push to Docker Hub (on release tags)

#### 4. publish-pypi
- Publish wheel to PyPI (on release tags only)
- Uses `PYPI_API_TOKEN` secret

#### 5. create-release
- Create GitHub Release
- Attach wheel, binary, and Docker image info
- Auto-generate release notes

**Required Secrets:**
- `DOCKERHUB_USERNAME` - Docker Hub username
- `DOCKERHUB_TOKEN` - Docker Hub access token
- `PYPI_API_TOKEN` - PyPI API token for publishing

**Expected Duration:** ~10-15 minutes total

---

## Setup Instructions

### 1. Enable GitHub Actions

GitHub Actions is enabled by default for public repositories. For private repos:
1. Go to repository Settings → Actions → General
2. Enable "Allow all actions and reusable workflows"

### 2. Configure Secrets

Add the following secrets in repository Settings → Secrets and variables → Actions:

| Secret Name | Description | Required For |
|-------------|-------------|--------------|
| `DOCKERHUB_USERNAME` | Docker Hub username | build.yml |
| `DOCKERHUB_TOKEN` | Docker Hub access token | build.yml |
| `PYPI_API_TOKEN` | PyPI API token | build.yml (publish) |
| `CODECOV_TOKEN` | Codecov upload token | test.yml (optional) |

### 3. First Run

After pushing these workflows:

```bash
# Verify workflows are recognized
gh workflow list

# Trigger a test run manually
gh workflow run test.yml

# View run status
gh run list
```

---

## Monitoring

### View Workflow Status

**In GitHub UI:**
- Navigate to repository → Actions tab
- Click on workflow name to see runs
- Click on run to see job details

**Using GitHub CLI:**
```bash
# List recent runs
gh run list

# View specific run
gh run view <run-id>

# Watch run in real-time
gh run watch
```

### Badge URLs

Add these to README.rst:

```rst
.. image:: https://github.com/polecat-dev/opensearch-curator/workflows/Integration%20Tests/badge.svg
   :target: https://github.com/polecat-dev/opensearch-curator/actions/workflows/test.yml

.. image:: https://github.com/polecat-dev/opensearch-curator/workflows/Code%20Quality/badge.svg
   :target: https://github.com/polecat-dev/opensearch-curator/actions/workflows/lint.yml

.. image:: https://codecov.io/gh/polecat-dev/opensearch-curator/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/polecat-dev/opensearch-curator
```

---

## Troubleshooting

### Tests Fail in CI but Pass Locally

**Common causes:**
1. **Different OpenSearch version** - CI tests multiple versions
2. **Missing environment variables** - Check workflow env section
3. **Service not ready** - Increase health check retries
4. **Path differences** - Use relative paths, not absolute

**Solution:**
```bash
# Test locally with same services
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
.\run_tests.ps1 tests/integration/ -v
```

### Docker Build Fails

**Check:**
1. Dockerfile is valid: `docker build -t test .`
2. alpine4docker.sh is executable: `chmod +x scripts/alpine4docker.sh`
3. Required files exist in expected locations

### PyPI Publish Fails

**Verify:**
1. `PYPI_API_TOKEN` secret is set correctly
2. Package version doesn't already exist on PyPI
3. Build artifacts were created successfully

**Test with TestPyPI first:**
```yaml
- name: Publish to TestPyPI
  uses: pypa/gh-action-pypi-publish@release/v1
  with:
    password: ${{ secrets.TEST_PYPI_API_TOKEN }}
    repository-url: https://test.pypi.org/legacy/
```

---

## Local Testing

### Test the test workflow locally

Using [act](https://github.com/nektos/act):

```bash
# Install act
choco install act-cli  # Windows
brew install act       # macOS

# Run test workflow
act -j test

# Run specific job
act -j test -P ubuntu-latest=ghcr.io/catthehacker/ubuntu:act-latest
```

### Validate workflow syntax

```bash
# Install actionlint
choco install actionlint  # Windows
brew install actionlint   # macOS

# Lint all workflows
actionlint .github/workflows/*.yml
```

---

## Release Process

### 1. Prepare Release

```bash
# Update version
echo '__version__ = "1.0.0"' > curator/_version.py

# Update CHANGELOG.md
# - Move [Unreleased] items to [1.0.0]
# - Add release date

# Commit changes
git add curator/_version.py CHANGELOG.md
git commit -m "chore: Prepare v1.0.0 release"
git push
```

### 2. Create Release Tag

```bash
# Create annotated tag
git tag -a v1.0.0 -m "Release v1.0.0 - OpenSearch Curator"

# Push tag (triggers build.yml)
git push origin v1.0.0
```

### 3. Monitor Build

```bash
# Watch the release build
gh run watch

# Or view in browser
# https://github.com/polecat-dev/opensearch-curator/actions
```

### 4. Verify Release

After build.yml completes:

1. **GitHub Release** - Check https://github.com/polecat-dev/opensearch-curator/releases
2. **PyPI** - Check https://pypi.org/project/opensearch-curator/
3. **Docker Hub** - Check https://hub.docker.com/r/polecat/opensearch-curator

### 5. Announce

- Post to OpenSearch community forum
- Update project website/documentation
- Tweet/social media announcement

---

## Maintenance

### Update Dependencies

Dependabot is configured to auto-update GitHub Actions:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

### Workflow Optimization

**Reduce CI time:**
1. Use caching for dependencies
2. Run fast tests first (fail-fast)
3. Parallelize independent jobs
4. Use matrix strategy for multi-version testing

**Save costs:**
1. Skip redundant runs (skip [ci skip] commits)
2. Cancel in-progress runs when new commits pushed
3. Use smaller runners when possible

---

**Last Updated:** November 13, 2025  
**Maintainer:** Development Team
