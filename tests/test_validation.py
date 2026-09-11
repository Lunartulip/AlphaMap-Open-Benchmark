import shutil
from pathlib import Path

import pytest

from alphamap_open.validate import ValidationError, validate_directory


SAMPLE = Path("data/sample/v1")


def test_sample_and_manifest_are_valid() -> None:
    counts = validate_directory(SAMPLE, check_manifest=True)
    assert counts["entities.csv"] == 6
    assert counts["events.csv"] == 12
    assert counts["observations.csv"] == 15
    assert counts["coverage.csv"] == 11


def test_invalid_temporal_order_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "data" / "sample" / "v1"
    shutil.copytree(SAMPLE, target)
    contract = tmp_path / "contracts" / "v1"
    contract.mkdir(parents=True)
    shutil.copy(
        Path("contracts/v1/datapackage.json"),
        contract / "datapackage.json",
    )
    events = (target / "events.csv").read_text(encoding="utf-8")
    events = events.replace(
        "2023-08-24T13:30:00Z",
        "2023-08-22T13:30:00Z",
        1,
    )
    (target / "events.csv").write_text(events, encoding="utf-8")
    with pytest.raises(ValidationError, match="published <= available <= tradable"):
        validate_directory(target)


def test_manifest_detects_content_change(tmp_path: Path) -> None:
    target = tmp_path / "data" / "sample" / "v1"
    shutil.copytree(SAMPLE, target)
    contract = tmp_path / "contracts" / "v1"
    contract.mkdir(parents=True)
    shutil.copy(
        Path("contracts/v1/datapackage.json"),
        contract / "datapackage.json",
    )
    with (target / "entities.csv").open("a", encoding="utf-8") as handle:
        handle.write("ENTITY_X,Example Inc.,US,test\n")
    with pytest.raises(ValidationError):
        validate_directory(target, check_manifest=True)
