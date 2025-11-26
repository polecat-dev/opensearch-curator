# OpenSearch Curator

[![Tests](https://github.com/polecat-dev/opensearch-curator/actions/workflows/test.yml/badge.svg)](https://github.com/polecat-dev/opensearch-curator/actions/workflows/test.yml)
[![Integration Matrix](https://github.com/polecat-dev/opensearch-curator/actions/workflows/integration.yml/badge.svg)](https://github.com/polecat-dev/opensearch-curator/actions/workflows/integration.yml)
[![Code Quality](https://github.com/polecat-dev/opensearch-curator/actions/workflows/lint.yml/badge.svg)](https://github.com/polecat-dev/opensearch-curator/actions/workflows/lint.yml)

OpenSearch Curator keeps OpenSearch clusters tidy. It ships a Click-based CLI, CLI singletons, and an API surface you can script against for recurring housekeeping tasks such as delete, snapshot, rollover, and remote store conversion.

## Highlights

- Supports OpenSearch 2.x and 3.x via `opensearch-py`
- Provides the `curator`, `curator_cli`, and `es_repo_mgr` entry points
- Runs full integration (183 tests) and `opensearch_client` unit suites in CI
- Includes a secure-by-default Docker test stack with custom CA + PKCS#12 tooling
- Uses Hatch/PEP-517 packaging plus automated release and build workflows

## Repository Layout

| Path | Description |
| ---- | ----------- |
| `curator/` | Main CLI implementation, actions, helpers |
| `opensearch_client/` | Embedded client builder used by Curator |
| `tests/` | Integration tests (require running OpenSearch) |
| `opensearch_client/tests/` | Fast unit tests for the embedded client |
| `test-environments/compose/` | Docker Compose stacks + security configuration |
| `test-environments/local-runner/` | Action recipes, `run-curator.sh`, data seeding scripts |
| `tools/diagnostics/` | Helper scripts for config and connectivity checks |
| `docs/` | Sphinx documentation source |

## Technology Stack

- Python 3.8-3.12
- Click-based CLI entrypoints (`curator`, `curator_cli`, `es_repo_mgr`)
- `opensearch-py` plus the in-repo `opensearch_client` builder
- Hatch for packaging, `python -m build` for wheels/sdists
- Pytest + pytest-cov + LocalStack/S3 integration tests
- Sphinx documentation (built locally or via GitHub Actions)

## Test & Coverage Strategy

Two workflows keep the project healthy:

1. `.github/workflows/test.yml` (fast) runs the Curator and `opensearch_client` unit suites on Python 3.8, 3.11, and 3.12. Coverage is uploaded from the Python 3.12 run on every push/PR.
2. `.github/workflows/integration.yml` (heavy) spins up real OpenSearch + LocalStack containers. It runs on release tags, a weekly schedule, or when triggered manually. The workflow always exercises OpenSearch 3.3.0 and can optionally include the legacy 2.11.1 job by dispatching with `run-legacy=true`.

   > ConvertIndexToRemote and other remote-store tests require OpenSearch 3.x. They are automatically skipped when the cluster reports a lower major version, which is why the legacy 2.11.1 run is optional.

Trigger the integration workflow manually:

```bash
gh workflow run integration.yml             # latest OpenSearch only
gh workflow run integration.yml -f run-legacy=true  # include OpenSearch 2.11.1
```

Run the same integration checks locally:

```bash
python -m pip install -e ".[test]"
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
pytest tests/integration/ -q
pytest opensearch_client/tests/unit -q
pytest tests/integration/ --cov=curator --cov-report=term
```

## Quick Start

```bash
git clone https://github.com/polecat-dev/opensearch-curator.git
cd opensearch-curator
python -m venv .venv && source .venv/bin/activate
python -m pip install -e .
python scripts/generate_test_certs.py
docker-compose -f test-environments/compose/docker-compose.test.yml up -d
python -m pytest tests/integration/ -q
```

PowerShell helpers (`run_tests.ps1`, `scripts/start-opensearch.ps1`) load the `.env` file automatically and default to `https://localhost:19200`.

## Packaging & Releases

- Manual builds: `python -m pip install build` then `python -m build`
- Automated releases: run the `Release` workflow (`.github/workflows/release.yml`) with the desired version (for example, `1.1.0`). The workflow bumps `curator/_version.py`, updates `opensearch_client/__init__.py`, creates a tag (`v1.1.0`), publishes tarball/wheel assets, and opens a GitHub Release.
- Tagged builds automatically trigger `build.yml`, which refreshes Docker images, standalone binaries, and PyPI uploads.

Install the published wheel on servers:

```bash
python -m pip install opensearch-curator==<version>
curator --version
```

## Documentation

Sphinx sources live in `docs/`. Build them locally:

```bash
python -m pip install -r docs/requirements.txt
sphinx-build -b html docs docs/_build/html
```

Rendered docs and API references are available in the repository (`docs/` folder) or via GitHub Pages if configured.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. Issues and feature requests are tracked on [GitHub Issues](https://github.com/polecat-dev/opensearch-curator/issues).
