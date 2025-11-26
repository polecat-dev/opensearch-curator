#!/usr/bin/env python3
"""Quick helper to inspect the local-runner Curator configuration."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from opensearch_client.config import get_client, get_config

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = REPO_ROOT / "test-environments" / "local-runner" / "curator.yml"


def banner(label: str) -> None:
    print(f"\n== {label} ==")


def load_file() -> None:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config not found at {CONFIG_PATH}")
    with CONFIG_PATH.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    banner("YAML contents")
    print(yaml.dump(data, default_flow_style=False))


def inspect_builder() -> None:
    banner("opensearch_client.get_config")
    cfg = get_config(configfile=str(CONFIG_PATH))
    print(f"type: {type(cfg)}")
    if hasattr(cfg, "opensearch"):
        print(json.dumps(cfg.opensearch.toDict(), indent=2))

    banner("opensearch_client.get_client")
    client = get_client(configfile=str(CONFIG_PATH))
    info = client.info()
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    load_file()
    inspect_builder()
