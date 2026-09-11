from pathlib import Path

from alphamap_open.validate import validate_directory


SAMPLE = Path("data/sample/v1")


def test_sample_and_manifest_are_valid() -> None:
    counts = validate_directory(SAMPLE, check_manifest=True)
    assert counts["entities.csv"] == 6
    assert counts["events.csv"] == 14
    assert counts["observations.csv"] == 18
