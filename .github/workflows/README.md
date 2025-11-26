# GitHub Actions CI/CD

This directory contains the workflows that keep OpenSearch Curator tested, linted, packaged, and released.

## Workflow Overview

| Workflow | Purpose | Trigger |
| -------- | ------- | ------- |
| `test.yml` | Unit suites (`tests/unit` and `opensearch_client/tests/unit`) on Python 3.8/3.11/3.12 with coverage on 3.12 | Push/PR to `main` & `develop`, manual dispatch |
| `integration.yml` | Full integration run with real OpenSearch + LocalStack (3.3.0 every time, optional 2.11.1) | Weekly schedule, release tags, manual dispatch |
| `lint.yml` | Formatting, linting, typing, and Bandit security scan | Push/PR to `main` & `develop`, manual dispatch |
| `build.yml` | Wheels, cx_Freeze binaries, Docker images, and PyPI publish | Tag pushes (`v*.*.*`) or manual |
| `release.yml` | Version bump + tagging + GitHub Release helper | Manual dispatch with `version` input |

## test.yml – Fast Unit Suite

- Runs on every push/PR.
- Matrix: Python 3.8, 3.11, and 3.12.
- Executes `pytest tests/unit` and `pytest opensearch_client/tests/unit`.
- Uploads coverage from the Python 3.12 job via Codecov.
- No Docker services are started, so the workflow finishes quickly.

## integration.yml – Full Environment Tests

- Starts OpenSearch (`opensearchproject/opensearch`) and LocalStack using the same Docker Compose settings we ship in `test-environments/compose/`.
- Always tests against OpenSearch **3.3.0** (`latest` job).
- Optionally tests against **2.11.1** (`legacy` job). The legacy job runs automatically on release tags and the weekly schedule; when dispatching manually you can toggle it with `run-legacy=true`.
- Runs `pytest tests/integration/` with the same env vars we use locally (`TEST_ES_SERVER`, `TEST_S3_BUCKET`, etc.).
- Uploads coverage for the latest OpenSearch job so release builds still have integration coverage data.
- Suggested usage before releases:
  ```bash
  gh workflow run integration.yml                 # latest OpenSearch only
  gh workflow run integration.yml -f run-legacy=true  # include OpenSearch 2.11.1
  ```

## lint.yml – Code Quality

Two jobs run independently:
1. **lint** – installs Black, Ruff, MyPy, and Pylint and runs each tool (Pylint is non-blocking via `--exit-zero`).
2. **security** – runs `bandit[toml]` across `curator/` and `opensearch_client/`, uploading `bandit-report.json` as an artifact.

## build.yml – Packaging & Publishing

Triggered by semantic tags (`vX.Y.Z`) or manual dispatch.
- Builds wheels/sdists (`python -m build` + `hatch build`).
- Creates cx_Freeze binaries inside Docker and uploads them as artifacts.
- Builds/pushes multi-architecture Docker images (`polecat/opensearch-curator`).
- Publishes wheels to PyPI when credentials are present.
- Generates a GitHub Release attaching the artifacts.

## release.yml – Version + Release Helper

Manual workflow with required `version` input.
1. Runs `.github/scripts/bump_version.py` to update `curator/_version.py` and `opensearch_client/__init__.py`.
2. Installs the project, runs the `opensearch_client` unit suite, and builds wheels.
3. Commits the bump, pushes to the repo, and creates/updates the `vX.Y.Z` tag.
4. Creates a GitHub Release and uploads build artifacts. The pushed tag triggers `build.yml` automatically.

## Secrets

| Secret | Workflows | Purpose |
| ------ | --------- | ------- |
| `DOCKERHUB_USERNAME` / `DOCKERHUB_TOKEN` | build.yml | Push Docker images |
| `PYPI_API_TOKEN` | build.yml | Publish wheels/sdists |
| `CODECOV_TOKEN` (optional) | test.yml & integration.yml | Upload coverage when the repo is private |

## Local Validation Tips

- Use [`act`](https://github.com/nektos/act) for quick syntax checks: `act -j unit` or `act -j latest`.
- Lint workflow files with [`actionlint`](https://github.com/rhysd/actionlint) before committing (`actionlint .github/workflows/*.yml`).
- Cancel older runs in the Actions UI to keep queues short. For integration runs, prefer `gh workflow run integration.yml` so you can choose when the heavy jobs execute.

_Last updated: November 27, 2025._
