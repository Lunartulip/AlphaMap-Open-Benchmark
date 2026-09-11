from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import date, datetime
from pathlib import Path
from typing import Any


class ValidationError(ValueError):
    """Raised when a release violates the executable data contract."""


def _parse_date(value: str, context: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{context}: invalid ISO date {value!r}") from exc


def _parse_time(value: str, context: str) -> datetime:
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValidationError(f"{context}: invalid ISO datetime {value!r}") from exc
    if result.tzinfo is None:
        raise ValidationError(f"{context}: datetime must include a UTC offset")
    return result


def _read(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if reader.fieldnames is None:
        raise ValidationError(f"{path.name}: missing header")
    if any(None in row for row in rows):
        raise ValidationError(f"{path.name}: malformed row has extra fields")
    return reader.fieldnames, rows


def _contract(root: Path) -> dict[str, dict[str, Any]]:
    path = root.parents[2] / "datapackage.json"
    package = json.loads(path.read_text(encoding="utf-8"))
    if package.get("profile") != "tabular-data-package":
        raise ValidationError("contract: expected tabular-data-package profile")
    return {
        Path(resource["path"]).name: resource
        for resource in package["resources"]
    }


def _validate_field(value: str, field: dict[str, Any], context: str) -> None:
    constraints = field.get("constraints", {})
    if constraints.get("required") and value == "":
        raise ValidationError(f"{context}: required value is blank")
    if value == "":
        return
    kind = field.get("type", "string")
    try:
        if kind == "number":
            float(value)
        elif kind == "boolean" and value not in {"true", "false"}:
            raise ValueError
        elif kind == "date":
            date.fromisoformat(value)
        elif kind == "datetime":
            parsed = datetime.fromisoformat(value)
            if parsed.tzinfo is None:
                raise ValueError
    except ValueError as exc:
        raise ValidationError(f"{context}: invalid {kind} value {value!r}") from exc
    allowed = constraints.get("enum")
    if allowed and value not in allowed:
        raise ValidationError(f"{context}: value {value!r} is outside {allowed}")


def _validate_resource(
    name: str,
    resource: dict[str, Any],
    root: Path,
) -> list[dict[str, str]]:
    headers, rows = _read(root / name)
    fields = resource["schema"]["fields"]
    expected = [field["name"] for field in fields]
    if headers != expected:
        raise ValidationError(f"{name}: header differs from executable contract")
    if not rows:
        raise ValidationError(f"{name}: table must contain at least one row")
    for row_number, row in enumerate(rows, start=2):
        for field in fields:
            _validate_field(
                row[field["name"]],
                field,
                f"{name}:{row_number}:{field['name']}",
            )
    primary = resource["schema"]["primaryKey"]
    keys = [primary] if isinstance(primary, str) else primary
    values = [tuple(row[key] for key in keys) for row in rows]
    if len(values) != len(set(values)):
        raise ValidationError(f"{name}: duplicate primary key")
    return rows


def _require_fk(
    tables: dict[str, list[dict[str, str]]],
    table: str,
    field: str,
    parent_table: str,
    parent_field: str,
) -> None:
    parents = {row[parent_field] for row in tables[parent_table]}
    for row_number, row in enumerate(tables[table], start=2):
        if row[field] not in parents:
            raise ValidationError(
                f"{table}:{row_number}: {field}={row[field]!r} has no parent"
            )


def _temporal_and_semantic_checks(
    tables: dict[str, list[dict[str, str]]],
) -> None:
    securities = {row["security_id"]: row for row in tables["security_mappings.csv"]}
    sources = {row["source_id"]: row for row in tables["sources.csv"]}
    events = {row["event_id"]: row for row in tables["events.csv"]}

    for row_number, row in enumerate(tables["sources.csv"], start=2):
        published = _parse_time(row["published_at"], f"sources.csv:{row_number}")
        if (
            row["publication_precision"] == "date_only"
            and any((published.hour, published.minute, published.second))
        ):
            raise ValidationError(
                f"sources.csv:{row_number}: date_only timestamp must be midnight UTC"
            )
        if (
            row["publication_precision"] == "exact"
            and row["timestamp_basis"] != "wire_metadata"
        ):
            raise ValidationError(
                f"sources.csv:{row_number}: exact time requires wire metadata"
            )
        if not row["document_sha256"] and row["access_status"] != "verified_live":
            raise ValidationError(
                f"sources.csv:{row_number}: unhashed source must be verified live"
            )

    for row_number, row in enumerate(tables["events.csv"], start=2):
        published = _parse_time(row["published_at"], f"events.csv:{row_number}")
        available = _parse_time(row["available_at"], f"events.csv:{row_number}")
        tradable = _parse_time(row["tradable_from"], f"events.csv:{row_number}")
        if not published <= available <= tradable:
            raise ValidationError(
                f"events.csv:{row_number}: expected published <= available <= tradable"
            )
        source = sources[row["source_id"]]
        if row["published_at"] != source["published_at"]:
            raise ValidationError(
                f"events.csv:{row_number}: published_at differs from source"
            )
        expected_policy = (
            "DATE_ONLY_NEXT_SESSION"
            if source["publication_precision"] == "date_only"
            else "EXACT_PLUS_15M"
        )
        if row["timestamp_policy_id"] != expected_policy:
            raise ValidationError(
                f"events.csv:{row_number}: timestamp policy differs from source basis"
            )
        if (
            source["publication_precision"] == "date_only"
            and source["timestamp_basis"] != "reconstructed_conservative"
        ):
            raise ValidationError(
                f"events.csv:{row_number}: date-only source basis is inconsistent"
            )
        security = securities[row["security_id"]]
        event_day = tradable.date()
        if event_day < _parse_date(security["valid_from"], "security valid_from"):
            raise ValidationError(f"events.csv:{row_number}: security not yet valid")
        if security["valid_to"] and event_day > _parse_date(
            security["valid_to"], "security valid_to"
        ):
            raise ValidationError(f"events.csv:{row_number}: security no longer valid")

    for row_number, row in enumerate(tables["observations.csv"], start=2):
        if bool(row["numeric_value"]) == bool(row["text_value"]):
            raise ValidationError(
                f"observations.csv:{row_number}: populate exactly one value field"
            )
        if _parse_date(row["period_start"], "period_start") > _parse_date(
            row["period_end"], "period_end"
        ):
            raise ValidationError(
                f"observations.csv:{row_number}: period_start exceeds period_end"
            )
        event = events[row["event_id"]]
        for field in ("source_id", "claim_label", "available_at"):
            if row[field] != event[field]:
                raise ValidationError(
                    f"observations.csv:{row_number}: {field} differs from event"
                )

    for row_number, row in enumerate(tables["relationships.csv"], start=2):
        published = _parse_time(
            row["published_at"], f"relationships.csv:{row_number}"
        )
        available = _parse_time(
            row["available_at"], f"relationships.csv:{row_number}"
        )
        tradable = _parse_time(
            row["tradable_from"], f"relationships.csv:{row_number}"
        )
        if not published <= available <= tradable:
            raise ValidationError(
                f"relationships.csv:{row_number}: invalid knowledge-time order"
            )
        source = sources[row["source_id"]]
        if row["published_at"] != source["published_at"]:
            raise ValidationError(
                f"relationships.csv:{row_number}: published_at differs from source"
            )
        if row["valid_to"] and _parse_date(
            row["valid_from"], "valid_from"
        ) > _parse_date(row["valid_to"], "valid_to"):
            raise ValidationError(
                f"relationships.csv:{row_number}: invalid effective interval"
            )
        if (
            row["alpha_feature_eligible"] == "true"
            and row["confidence_tier"] != "confirmed"
        ):
            raise ValidationError(
                f"relationships.csv:{row_number}: eligible edge must be confirmed"
            )
        if (
            row["economic_exposure_known"] == "false"
            and row["weight_basis"] != "registered_uniform_topological"
        ):
            raise ValidationError(
                f"relationships.csv:{row_number}: non-economic weight is mislabeled"
            )


def _foreign_keys(
    tables: dict[str, list[dict[str, str]]],
    contract: dict[str, dict[str, Any]],
) -> None:
    resource_paths = {
        resource["name"]: path for path, resource in contract.items()
    }
    for table, resource in contract.items():
        for link in resource["schema"].get("foreignKeys", []):
            reference = link["reference"]
            _require_fk(
                tables,
                table,
                link["fields"],
                resource_paths[reference["resource"]],
                reference["fields"],
            )

def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _manifest(root: Path, tables: dict[str, list[dict[str, str]]]) -> None:
    payload = json.loads((root / "release_manifest.json").read_text(encoding="utf-8"))
    repository_root = root.parents[2]
    package = json.loads(
        (repository_root / "datapackage.json").read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (repository_root / "research" / "protocol.json").read_text(encoding="utf-8")
    )
    listed = {item["path"] for item in payload["files"]}
    if listed != set(tables):
        raise ValidationError("manifest: file inventory differs from contract")
    if payload.get("eligible_for_inference") is not False:
        raise ValidationError("manifest: audit sample must be non-inferential")
    if payload["version"] != package["version"]:
        raise ValidationError("manifest: package version mismatch")
    if payload["schema_version"] != package["custom"]["contract_version"]:
        raise ValidationError("manifest: contract version mismatch")
    if payload["protocol_id"] != protocol["protocol_id"]:
        raise ValidationError("manifest: protocol mismatch")
    cutoff = max(row["available_at"] for row in tables["events.csv"])
    if payload["knowledge_cutoff"] != cutoff:
        raise ValidationError("manifest: knowledge cutoff mismatch")
    for item in payload["files"]:
        name = item["path"]
        if item["rows"] != len(tables[name]):
            raise ValidationError(f"manifest: row count mismatch for {name}")
        if item["sha256"] != _sha256(root / name):
            raise ValidationError(f"manifest: SHA-256 mismatch for {name}")


def validate_directory(root: Path, check_manifest: bool = False) -> dict[str, int]:
    contract = _contract(root)
    tables = {
        name: _validate_resource(name, resource, root)
        for name, resource in contract.items()
    }
    _foreign_keys(tables, contract)
    _temporal_and_semantic_checks(tables)
    if check_manifest:
        _manifest(root, tables)
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
