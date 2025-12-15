#!/usr/bin/env python3
"""Bump version strings in the places Hatch looks for."""

from __future__ import annotations

import re
import sys
from pathlib import Path


def update_file(path: Path, version: str) -> None:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(r"(?P<prefix>__version__\s*=\s*['\"])(?P<ver>[^'\"]+)(?P<suffix>['\"])")
    if not pattern.search(text):
        raise SystemExit(f"Could not find __version__ in {path}")
    text = pattern.sub(rf"\g<prefix>{version}\g<suffix>", text, count=1)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: bump_version.py <version>")
    version = sys.argv[1].strip()
    root = Path(__file__).resolve().parents[2]
    targets = [
        root / "curator" / "_version.py",
        root / "opensearch_client" / "__init__.py",
    ]
    for target in targets:
        update_file(target, version)
        print(f"Updated {target}")


if __name__ == "__main__":
    main()
