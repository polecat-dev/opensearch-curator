# Test Certificates

This directory stores **development-only** certificates that are required by the
`test-environments/compose/docker-compose.test.yml` stack when OpenSearch security is enabled. All
artifacts are generated on-demand so that no private keys are committed to the
repository.

- `README.md` – this file
- `generated/` (gitignored)
  - `ca/` – custom root CA
  - `http/` – HTTP layer certificate chain
  - `transport/` – node-to-node transport certificate chain

## Generating Certificates

Run the helper once per workstation (or whenever you need to rotate keys):

```bash
python scripts/generate_test_certs.py
```

Key facts:

- Uses `openssl` under the hood – make sure it is on your `PATH`.
- Creates a password-protected CA key, encrypted HTTP/transport keys, full chain
  PEMs, and PKCS#12 bundles for both HTTP and transport endpoints.
- Defaults can be customised with `--password`, `--output`, `--http-cn`, and
  related CLI options (`-h` shows them all).
- The script guarantees separate keys/certs for transport and HTTP so that HTTP
  can later be swapped with a publicly signed certificate without touching
  transport security.

After running the script you should export/update the following environment
variables (usually in `.env`):

```dotenv
TEST_ES_SERVER=https://localhost:19200
TEST_ES_CA_CERT=certs/generated/ca/root-ca.pem
OPENSEARCH_TEST_SSL_PASSWORD=curatorssl
OPENSEARCH_INITIAL_ADMIN_PASSWORD=MyStrongPassword123!
```

`test-environments/compose/docker-compose.test.yml` automatically mounts `certs/generated/` inside the
containers, so make sure this directory exists before bringing the stack up.

> **Important:** All generated files stay on your machine and are ignored by
> Git. Do **not** copy them into commits or production deployments.

## Verifying Generated Files

Every run automatically validates the private keys, certificates, chains, and
PKCS#12 bundles using `openssl`. You can re-run the verification step at any
time without regenerating assets:

```bash
python scripts/generate_test_certs.py --verify-only -p curatorssl
```

Use `-p` if you changed the default password; otherwise the value stored in
`manifest.json` is used automatically. The verifier checks:

- Each encrypted private key can be opened with the supplied password.
- HTTP/transport certificates are well-formed and signed by the custom CA.
- PKCS#12 bundles contain the expected material.
