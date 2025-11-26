# GitHub Actions CI/CD

This directory contains the workflows that keep OpenSearch Curator tested, linted, packaged, and released.

## Workflow Overview

| Workflow | Purpose | Trigger |
| -------- | ------- | ------- |
| `test.yml` | Matrixed integration + `opensearch_client` unit tests, coverage upload | Push/PR to `main` or `develop`, manual dispatch |
| `lint.yml` | Formatting, linting, typing, and Bandit security scan | Push/PR to `main` or `develop`, manual dispatch |
| `build.yml` | Build wheels, cx_Freeze binaries, Docker images, publish artifacts | Tag pushes matching `v*.*.*`, manual dispatch |
| `release.yml` | Version bump, tagging, GitHub Release creation | Manual dispatch with `version` input |

## test.yml

- Runs on Ubuntu with services for OpenSearch (`opensearchproject/opensearch`) and LocalStack (S3).
- Matrix: Python 3.8-3.12 x OpenSearch 2.11.1/3.0.0/3.1.0/3.2.0.
- Environment variables used by pytest:
  - `TEST_ES_SERVER=http://localhost:9200`
  - `TEST_S3_BUCKET=curator-test-bucket`
  - `TEST_S3_ENDPOINT=http://localhost:4566`
  - `AWS_ACCESS_KEY_ID=test`, `AWS_SECRET_ACCESS_KEY=test`
- Steps:
  1. Install dependencies (`pip install -e . pytest pytest-cov boto3`).
  2. Wait for OpenSearch health to turn green and confirm `path.repo` is set.
  3. Run integration tests (`pytest tests/integration/`).
  4. Re-run with coverage (Python 3.12 + OpenSearch 3.2.0) and upload to Codecov (`coverage.xml`).
  5. Run `opensearch_client/tests/unit` on their own matrix.
  6. Emit a short summary block for the Actions run view.

## lint.yml

Two jobs run independently:

1. **lint** - installs the project plus `black`, `ruff`, `mypy`, `pylint` and executes:
   - `black --check`
   - `ruff check`
   - `mypy`
   - `pylint` (non-blocking via `--exit-zero`)
2. **security** - installs `bandit[toml]`, scans `curator/` and `opensearch_client/`, and uploads `bandit-report.json` as an artifact.

## build.yml

Triggered by semver tags (`vX.Y.Z`) or manual dispatch.

Jobs:
- **build-wheel** - builds wheels/sdists with `python -m build` and `hatch build`, verifies by installing, and uploads `dist/` as `python-package`.
- **build-binary** - uses the Dockerfile to run cx_Freeze, extracts `/curator` binaries, and uploads them.
- **build-docker** - builds/pushes multi-arch Docker images (`polecat/opensearch-curator`) using Buildx + `docker/metadata-action` for tags.
- **publish-pypi** - downloads the `python-package` artifact and publishes to PyPI (needs `PYPI_API_TOKEN`).
- **create-release** - downloads artifacts and creates a GitHub Release attaching wheels/binaries.

## release.yml

Manual workflow (`workflow_dispatch`) with required `version` input (e.g., `1.1.0`).

Steps:
1. Run `.github/scripts/bump_version.py` to update `curator/_version.py` and `opensearch_client/__init__.py`.
2. Install the project, run `opensearch_client/tests/unit` as a smoke test, and build distributions.
3. Commit the bump (`Release vX.Y.Z`), push to `origin`, and create/update tag `vX.Y.Z`.
4. Create a GitHub Release and upload the artifacts. The pushed tag automatically triggers `build.yml` for Docker/cx_Freeze.

## Required Secrets

| Secret | Used By | Purpose |
| ------ | ------- | ------- |
| `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` | build.yml | Push Docker images |
| `PYPI_API_TOKEN` | build.yml | Publish wheels/sdists |
| `CODECOV_TOKEN` (optional) | test.yml | Upload coverage when the repo is private |

## Local Validation Tips

- Use [`act`](https://github.com/nektos/act) to smoke-test workflow changes (`act -j test`).
- Lint workflow files with [`actionlint`](https://github.com/rhysd/actionlint) before committing.
- Keep an eye on concurrency by canceling older runs when new pushes arrive (`Actions settings > Workflow concurrency`).

_Last updated: November 26, 2025._
