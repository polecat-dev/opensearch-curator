# OpenSearch Curator - Strategic Analysis & Migration Plan

**Lineage:** Forked from Elasticsearch Curator v8.0.21, rebuilt for OpenSearch
**Target Compatibility:** OpenSearch 2.x and 3.x (validated through 3.2.0)
**Focus Areas:** TLS-secured test environments, in-repo client builder, automated releases

---

## 1. Repository Snapshot

```
opensearch-curator/
|-- curator/                     # Core package (actions, helpers, validators)
|-- opensearch_client/           # Embedded client builder forked from es_client
|-- tests/                       # Integration cases (requires OpenSearch cluster)
|-- opensearch_client/tests/     # Fast unit suite for the builder
|-- test-environments/
|   |-- compose/                 # Docker Compose stacks + OpenSearch security config
|   |-- local-runner/            # Action recipes, run-curator.sh, data loaders
|-- scripts/                     # TLS tooling, diagnostics, helper automation
|-- tools/diagnostics/           # Cluster inspection helpers
|-- docs/                        # Sphinx sources (built locally / via Actions)
|-- README.md                    # Primary documentation surface
```

Additional notes:
- `test-environments/compose/opensearch-security/` contains transport and HTTP security configs separated per user request.
- TLS material (CA, node certs, PKCS#12 bundles) is generated under `certs/` via `scripts/generate_test_certs.py` and verified before Compose bootstraps.
- Local runner assets moved out of `examples/` to keep the repo root clean.

## 2. Technology Stack

| Area | Stack |
| ---- | ----- |
| Packaging | Hatch / hatchling, `python -m build`, cx_Freeze for binaries |
| Runtime deps | `opensearch-py>=3.0`, Click, PyYAML, Voluptuous, Certifi, Dotmap |
| Embedded builder | `opensearch_client/` (fork of es_client 8.19.5 retargeted to OpenSearch) |
| Tooling | Black, Ruff, MyPy, Pylint, Bandit, pytest, pytest-cov, LocalStack (S3) |
| Docs | Sphinx + `docs/requirements.txt` (no ReadTheDocs; publish via GitHub artifacts or Pages) |

## 3. OpenSearch Integration Status

- All direct `elasticsearch8` imports were replaced with `opensearchpy` equivalents.
- Version guards (`curator/defaults/settings.py`) enforce OpenSearch >= 2.0.0 and < 4.0.0.
- Config schema renamed to `opensearch.*` keys; CLI help text updated accordingly.
- TLS assets:
  - Custom CA with encrypted private key.
  - Separate HTTP and transport certificates, plus PKCS#12 keystores for each role.
  - Full-chain PEMs and `.p12` artifacts stored in `certs/generated/` (gitignored) and validated post-creation.
- Doc references, help text, and exceptions no longer mention Elasticsearch except when acknowledging the fork lineage.

## 4. CI/CD Overview

| Workflow | Purpose | Notes |
| -------- | ------- | ----- |
| `.github/workflows/test.yml` | Unit suites for Python 3.8/3.11/3.12 + `opensearch_client` tests with coverage on 3.12 | Runs fast (no Docker services) so every push/PR gets signal |
| `.github/workflows/integration.yml` | Full integration run with OpenSearch 3.3.0 (always) and optional 2.11.1 | Triggered weekly, on release tags, or manually (use `run-legacy=true` to include 2.11.1) |
| `.github/workflows/lint.yml` | Black, Ruff, MyPy, Pylint, Bandit | Lint and security jobs run in parallel |
| `.github/workflows/build.yml` | Wheels, cx_Freeze binary, Docker images, PyPI publish, GitHub Release assets | Triggered on `v*.*.*` tags or manual dispatch |
| `.github/workflows/release.yml` | Version bump + tagging + GitHub Release automation | Accepts a `version` input, commits, tags, and pushes before `build.yml` runs |

Secrets needed: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `PYPI_API_TOKEN`, optional `CODECOV_TOKEN`.

## 5. Supported OpenSearch Versions

- Integration suite currently exercises OpenSearch 2.11.1, 3.0.0, 3.1.0, and 3.2.0.
- Client shims allow any 3.x release thanks to semver `<4.0.0` constraint, but CI will be expanded as new versions ship.
- Legacy Elasticsearch compatibility has been removed to simplify maintenance; new issues should assume OpenSearch-only clusters.

## 6. Test Environments and TLS Tooling

1. **Certificate Generation**
   - `scripts/generate_test_certs.py` creates a dedicated CA, encrypted CA key, node certs per service, and PKCS#12 bundles.
   - `scripts/verify_test_certs.py` (added during TLS work) enumerates and validates every artifact under `certs/generated/`.
   - Transport and HTTP certs live in separate directories so HTTP can later swap to publicly issued certificates.
2. **Docker Compose stacks**
   - `test-environments/compose/docker-compose.test.yml` -> default CI/Dev stack (OpenSearch + LocalStack, security disabled).
   - `docker-compose.secure.yml` -> enables OpenSearch Security plugin, loads certs + security config, and uses the dedicated PKCS#12 files.
3. **Local runner**
   - `test-environments/local-runner/run-curator.sh` now resolves `repo_root` relative to the script directory so it works from anywhere (even when called inside WSL from `examples/local-test`).
   - Example action files (`01-*.yml` etc.) and data loader scripts reference the relocated config paths.

## 7. Documentation State

- `README.md` replaces the legacy `.rst` version and now documents technology choices, coverage, and CI badges.
- `.readthedocs.yaml` was removed; documentation is built locally with `sphinx-build -b html docs docs/_build/html` using `docs/requirements.txt`.
- Markdown references throughout the repo were updated to point to `README.md` (see Step 9 for remaining clean-up checklist).
- Developer-focused docs live under `docs/dev/` (including `TESTING.md`, `SESSION_SUMMARY.md`, and this file's duplicate) to keep guidance close to code.

## 8. Release and Packaging Flow

1. Trigger `release.yml` with the next semantic version.
2. Workflow bumps `curator/_version.py` and `opensearch_client/__init__.py`, commits, tags (`vX.Y.Z`), and pushes.
3. Tag fires `build.yml`, which:
   - Builds wheels/sdists (artifact `python-package`).
   - Runs cx_Freeze builder and extracts binaries.
   - Builds multi-arch Docker images (`polecat/opensearch-curator`) and publishes when credentials are available.
   - Publishes to PyPI via `pypa/gh-action-pypi-publish`.
4. `.github/workflows/README.md` documents the workflows for future maintainers.

## 9. Outstanding Follow-ups

| Area | Task |
| ---- | ---- |
| Tests | Expand integration coverage to OpenSearch 3.3.x once images are available. |
| Docs | Mirror the updated README content into `docs/reference` pages, ensure historical `.rst` files are either archived or refreshed. |
| Features | Evaluate ISM (Index State Management) parity for former ILM actions, determine fate of `cold2frozen.py`. |
| Tooling | Consider adding `actionlint` or `pre-commit` hooks for workflows and formatting. |

## 10. Risks and Mitigations

- **TLS drift:** Certificates live outside version control. Regenerate with `scripts/generate_test_certs.py` whenever SANs change and commit only the helper scripts.
- **OpenSearch API changes:** Track release notes for 3.x; integration matrix in CI should catch regressions early.
- **Dependency divergence:** `opensearch_client` fork must be kept in sync with upstream fixes. Document any patches in `opensearch_client/README_ORIGINAL.rst`.
- **Docs debt:** Some `docs/reference/*.md` files still reference legacy Elasticsearch examples. Prioritize cleanup before the next tagged release.

## 11. Resource Index

- `README.md` - user-facing overview, technology stack, CI badges.
- `test-environments/README.md` - explains Compose stacks and local runner assets.
- `docs/dev/TESTING.md` - canonical testing guide (ports, env vars, LocalStack usage).
- `.github/workflows/README.md` - CI/CD documentation.
- `OPENSEARCH_API_FIXES.md`, `TESTING.md`, `README_FIRST.md` - deep dives for developers.

## 12. Maintenance Notes

- Keep this document and `docs/dev/AGENTS.md` in sync whenever architecture or workflows change.
- Update the version history below when milestones land.

**Version History**
- **v2.0 (Nov 26, 2025):** Documentation refresh, TLS tooling completed, CI/CD stabilized around OpenSearch 3.2.0.
- **v1.0 (Nov 13, 2025):** Initial migration notes captured after forking from Elasticsearch Curator.
