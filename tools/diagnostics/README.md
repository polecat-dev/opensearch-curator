# Diagnostics

Small utility scripts that help verify configuration and connectivity without
touching the main Curator code:

- `test_config.py` – dumps the current `test-environments/local-runner/curator.yml`
  file and ensures `opensearch_client` can build a config + client from it.
- `test_connection.py` – pings the default test cluster using the credentials
  defined in `.env` (falls back to the documented defaults).

Both scripts assume they are executed from the repository root:

```bash
python tools/diagnostics/test_config.py
python tools/diagnostics/test_connection.py
```

Feel free to drop additional one-off diagnostics here instead of cluttering the
repository root.
