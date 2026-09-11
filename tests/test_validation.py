from pathlib import Path
from shutil import copy, copytree

import pytest

from alphamap_open.validate import ValidationError, validate_directory

SAMPLE = Path("data/sample/v1")


def _copy_release(tmp_path: Path) -> Path:
    target = tmp_path / "data" / "sample" / "v1"
    copytree(SAMPLE, target)
    copy(Path("datapackage.json"), tmp_path / "datapackage.json")
    protocol = tmp_path / "research"
    protocol.mkdir()
    copy(Path("research/protocol.json"), protocol / "protocol.json")
    return target


def test_sample_and_manifest_are_valid() -> None:
    counts = validate_directory(SAMPLE, check_manifest=True)
    assert counts["entities.csv"] == 6
    assert counts["events.csv"] == 12
    assert counts["observations.csv"] == 15
    assert counts["coverage.csv"] == 11


def test_invalid_temporal_order_is_rejected(tmp_path: Path) -> None:
    target = _copy_release(tmp_path)
    events = (target / "events.csv").read_text(encoding="utf-8")
    events = events.replace(
        "2023-08-24T13:30:00Z",
        "2023-08-22T13:30:00Z",
        1,
    )
    (target / "events.csv").write_text(events, encoding="utf-8")
    with pytest.raises(ValidationError, match="published <= available <= tradable"):
        validate_directory(target)


def test_timestamp_policy_must_match_source_basis(tmp_path: Path) -> None:
    target = _copy_release(tmp_path)
    events = (target / "events.csv").read_text(encoding="utf-8")
    events = events.replace("DATE_ONLY_NEXT_SESSION", "EXACT_PLUS_15M", 1)
    (target / "events.csv").write_text(events, encoding="utf-8")
    with pytest.raises(ValidationError, match="timestamp policy differs"):
        validate_directory(target)


def test_only_confirmed_relationships_are_feature_eligible(tmp_path: Path) -> None:
    target = _copy_release(tmp_path)
    relationships = (target / "relationships.csv").read_text(encoding="utf-8")
    relationships = relationships.replace(",confirmed,true,", ",probable,true,", 1)
    (target / "relationships.csv").write_text(relationships, encoding="utf-8")
    with pytest.raises(ValidationError, match="eligible edge must be confirmed"):
        validate_directory(target)


def test_manifest_detects_content_change(tmp_path: Path) -> None:
    target = _copy_release(tmp_path)
    with (target / "entities.csv").open("a", encoding="utf-8") as handle:
        handle.write("ENTITY_X,Example Inc.,US,test\n")
    with pytest.raises(ValidationError):
        validate_directory(target, check_manifest=True)
