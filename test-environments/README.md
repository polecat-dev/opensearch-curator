# Test Environments

All Docker and local-runner assets used during development and testing live in
this directory so the repository root stays focused on the Python code.

- `compose/`
  - `docker-compose.test.yml` - main OpenSearch + LocalStack stack
  - `docker-compose.secure.yml` - security-hardened variant
  - `init-security.sh`, `update_admin_password.sh` - helper scripts invoked by
    the secure compose file
- `local-runner/`
  - `curator.yml` - configuration template for local Curator runs
  - `run-curator.sh` - WSL helper that executes action files via the repo's
    `.venv-wsl` environment
  - `create-test-data.(sh|ps1)` - sample data loaders
  - `0X-*.yml` - curated action files used for manual smoke testing

> **⚠️ Demo credentials only**
>
> The secure Compose stack ships with intentionally weak defaults:
> `test-environments/compose/opensearch-security/internal_users.yml` contains
> bcrypt hashes for the documented demo passwords and
> `update_admin_password.sh` sets the admin account to a well-known string while
> the PKCS#12 bundles generated for TLS all reuse the `curatorssl` passphrase.
> Before exposing these assets outside of your workstation, regenerate the TLS
> material with `python scripts/generate_test_certs.py`, update every password
> via the security admin APIs (for example by re-running
> `update_admin_password.sh` with new hashes produced by `plugins/tools/hash.sh`
> inside the container), and rotate any `.p12` passphrases referenced by the
> Compose files.

See `docs/dev/TESTING.md` for the authoritative instructions on when to use
each environment and how these files tie into TLS assets and the rest of the
tooling.
