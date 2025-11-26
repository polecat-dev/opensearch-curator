#!/usr/bin/env python3
"""Confirm TLS/auth settings against the local OpenSearch test cluster."""

from __future__ import annotations

import os
from pathlib import Path

from opensearchpy import OpenSearch

DEFAULT_SERVER = "https://localhost:19200"
DEFAULT_CA = Path("certs/generated/ca/root-ca.pem")


def env(name: str, default: str | None = None) -> str | None:
    return os.environ.get(name, default)


def main() -> None:
    server = env("TEST_ES_SERVER", DEFAULT_SERVER)
    username = env("TEST_ES_USERNAME", "admin")
    password = env("TEST_ES_PASSWORD") or env("OPENSEARCH_INITIAL_ADMIN_PASSWORD")
    ca_path = Path(env("TEST_ES_CA_CERT", str(DEFAULT_CA)))
    verify = ca_path.exists()

    client = OpenSearch(
        [server],
        http_auth=(username, password) if password else None,
        verify_certs=verify,
        ca_certs=str(ca_path) if verify else None,
    )

    info = client.info()
    print("Connection successful!")
    print(f"Cluster: {info['cluster_name']}")
    print(f"Version: {info['version']['number']}")


if __name__ == "__main__":
    main()
