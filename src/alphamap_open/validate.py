from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable


class ValidationError(ValueError):
    """Raised when a release violates the published data contract."""


REQUIRED = {
    "entities.csv": ["entity_id", "legal_name", "domicile", "infrastructure_layer"],
    "security_mappings.csv": [
        "security_id", "entity_id", "ticker", "exchange", "currency", "valid_from", "valid_to"
    ],
    "sources.csv": [
        "source_id", "source_type", "publisher", "title", "url", "published_at",
        "publication_precision", "retrieved_at", "source_locator"
    ],
    "timestamp_policies.csv": [
        "timestamp_policy_id", "description", "availability_rule", "tradability_rule"
    ],
    "events.csv": [
        "event_id", "vintage_id", "subject_entity_id", "impact_entity_id", "security_id",
        "event_type", "evidence_stage", "direction", "claim_label", "published_at",
        "available_at", "tradable_from", "timestamp_policy_id", "alpha_feature_eligible",
        "source_id", "source_locator", "summary"
    ],
    "observations.csv": [
        "observation_id", "vintage_id", "event_id", "metric_name", "numeric_value",
        "text_value", "unit", "comparator", "period_start", "period_end", "as_of_date",
        "claim_label", "available_at", "source_id", "source_locator"
    ],
    "relationships.csv": [
        "relationship_id", "vintage_id", "from_entity_id", "to_entity_id",
        "relationship_type", "product", "valid_from", "valid_to", "confidence_tier",
        "alpha_feature_eligible", "source_id", "source_locator"
    ],
}

PRIMARY_KEYS = {
    "entities.csv": ["entity_id"],
    "security_mappings.csv": ["security_id", "valid_from"],
    "sources.csv": ["source_id"],
    "timestamp_policies.csv": ["timestamp_policy_id"],
    "events.csv": ["event_id", "vintage_id"],
    "observations.csv": ["observation_id", "vintage_id"],
    "relationships.csv": ["relationship_id", "vintage_id"],
}

ENUMS = {
    "direction": {"negative", "neutral", "positive"},
    "claim_label": {
        "reported_fact", "issuer_claim", "derived_value", "estimate",
        "relationship_assertion"
    },
    "publication_precision": {"exact", "date_only"},
    "alpha_feature_eligible": {"true", "false"},
    "confidence_tier": {"confirmed", "corroborated", "indicated"},
}


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _parse_time(value: str, context: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValidationError(f"{context}: invalid ISO-8601 timestamp {value!r}") from exc


def _require_columns(name: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise ValidationError(f"{name}: table must contain at least one row")
    missing = set(REQUIRED[name]) - set(rows[0])
    if missing:
        raise ValidationError(f"{name}: missing columns {sorted(missing)}")


def _unique(name: str, rows: list[dict[str, str]]) -> None:
    keys = PRIMARY_KEYS[name]
    values = [tuple(row[key] for key in keys) for row in rows]
    if len(values) != len(set(values)):
        raise ValidationError(f"{name}: duplicate primary key")


def _check_enums(name: str, rows: list[dict[str, str]]) -> None:
    for row_number, row in enumerate(rows, start=2):
        for field, allowed in ENUMS.items():
            if field in row and row[field] and row[field] not in allowed:
                raise ValidationError(
                    f"{name}:{row_number}: {field}={row[field]!r} is outside the contract"
                )


def _require_fk(
    rows: Iterable[dict[str, str]],
    field: str,
    valid: set[str],
    context: str,
) -> None:
    for row_number, row in enumerate(rows, start=2):
        if row[field] not in valid:
            raise ValidationError(
                f"{context}:{row_number}: {field}={row[field]!r} has no parent record"
            )


def _check_temporal(events: list[dict[str, str]]) -> None:
    for row_number, row in enumerate(events, start=2):
        published = _parse_time(row["published_at"], f"events.csv:{row_number}")
        available = _parse_time(row["available_at"], f"events.csv:{row_number}")
        tradable = _parse_time(row["tradable_from"], f"events.csv:{row_number}")
        if not published <= available <= tradable:
            raise ValidationError(
                f"events.csv:{row_number}: expected published <= available <= tradable"
            )


def _check_observations(rows: list[dict[str, str]]) -> None:
    for row_number, row in enumerate(rows, start=2):
        has_numeric = bool(row["numeric_value"])
        has_text = bool(row["text_value"])
        if has_numeric == has_text:
            raise ValidationError(
                f"observations.csv:{row_number}: populate exactly one value field"
            )
        if has_numeric:
            try:
                float(row["numeric_value"])
            except ValueError as exc:
                raise ValidationError(
                    f"observations.csv:{row_number}: numeric_value is not numeric"
                ) from exc


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check_manifest(root: Path, tables: dict[str, list[dict[str, str]]]) -> None:
    manifest = json.loads((root / "release_manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        name = item["path"]
        if name not in tables:
            raise ValidationError(f"manifest: unknown table {name}")
        if item["rows"] != len(tables[name]):
            raise ValidationError(f"manifest: row count mismatch for {name}")
        if item["sha256"] != _sha256(root / name):
            raise ValidationError(f"manifest: SHA-256 mismatch for {name}")


def validate_directory(root: Path, check_manifest: bool = False) -> dict[str, int]:
    tables = {name: _read(root / name) for name in REQUIRED}
    for name, rows in tables.items():
        _require_columns(name, rows)
        _unique(name, rows)
        _check_enums(name, rows)

    entity_ids = {row["entity_id"] for row in tables["entities.csv"]}
    security_ids = {row["security_id"] for row in tables["security_mappings.csv"]}
    source_ids = {row["source_id"] for row in tables["sources.csv"]}
    policy_ids = {
        row["timestamp_policy_id"] for row in tables["timestamp_policies.csv"]
    }
    event_ids = {row["event_id"] for row in tables["events.csv"]}

    _require_fk(tables["security_mappings.csv"], "entity_id", entity_ids, "security_mappings.csv")
    for field in ("subject_entity_id", "impact_entity_id"):
        _require_fk(tables["events.csv"], field, entity_ids, "events.csv")
    _require_fk(tables["events.csv"], "security_id", security_ids, "events.csv")
    _require_fk(tables["events.csv"], "source_id", source_ids, "events.csv")
    _require_fk(tables["events.csv"], "timestamp_policy_id", policy_ids, "events.csv")
    _require_fk(tables["observations.csv"], "event_id", event_ids, "observations.csv")
    _require_fk(tables["observations.csv"], "source_id", source_ids, "observations.csv")
    for field in ("from_entity_id", "to_entity_id"):
        _require_fk(tables["relationships.csv"], field, entity_ids, "relationships.csv")
    _require_fk(tables["relationships.csv"], "source_id", source_ids, "relationships.csv")

    _check_temporal(tables["events.csv"])
    _check_observations(tables["observations.csv"])
    if check_manifest:
        _check_manifest(root, tables)
    return {name: len(rows) for name, rows in tables.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an AlphaMap release")
    parser.add_argument("directory", type=Path)
    parser.add_argument("--manifest", action="store_true")
    args = parser.parse_args()
    counts = validate_directory(args.directory, args.manifest)
    print(json.dumps({"status": "valid", "rows": counts}, indent=2))


if __name__ == "__main__":
    main()
