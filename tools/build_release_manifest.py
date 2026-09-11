from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


TABLES = [
    "entities.csv",
    "security_mappings.csv",
    "sources.csv",
    "timestamp_policies.csv",
    "events.csv",
    "observations.csv",
    "relationships.csv",
]


def main() -> None:
    parser = argparse.ArgumentParser(description="Build an AlphaMap release manifest")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--version", required=True)
    parser.add_argument("--schema-version", default="1.0.0")
    args = parser.parse_args()

    files = []
    for name in TABLES:
        path = args.directory / name
        with path.open(newline="", encoding="utf-8") as handle:
            rows = sum(1 for _ in csv.DictReader(handle))
        files.append(
            {"path": name, "rows": rows, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        )
    manifest = {
        "dataset": "alphamap-open-benchmark",
        "version": args.version,
        "schema_version": args.schema_version,
        "released_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "files": files,
    }
    (args.directory / "release_manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
