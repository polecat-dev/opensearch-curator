# Test Certificates

This directory stores **development-only** certificates that are required by the
`docker-compose.test.yml` stack when OpenSearch security is enabled. All
artifacts are generated on-demand so that no private keys are committed to the
repository.

```
certs/
├── README.md               # This file
└── generated/              # Auto-generated TLS assets (gitignored)
    ├── ca/                 # Custom root CA
    ├── http/               # HTTP layer certificate chain
    └── transport/          # Node-to-node transport certificate chain
```

## Generating Certificates

Run the helper once per workstation (or whenever you need to rotate keys):

```bash
python scripts/generate_test_certs.py
```

Key facts:

- Uses `openssl` under the hood – make sure it is on your `PATH`.
- Creates a password-protected CA key, encrypted HTTP/transport keys, full chain
  PEMs, and a PKCS#12 bundle for the HTTP endpoint.
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

`docker-compose.test.yml` automatically mounts `certs/generated/` inside the
containers, so make sure this directory exists before bringing the stack up.

> **Important:** All generated files stay on your machine and are ignored by
> Git. Do **not** copy them into commits or production deployments.
