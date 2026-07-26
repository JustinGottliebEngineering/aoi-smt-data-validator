from pathlib import Path

import pytest

from aoi_validator.bom_parser import BOMParseError, parse_bom


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA = PROJECT_ROOT / "sample_data"


def test_parse_bom_groups_references_by_part_id() -> None:
    result = parse_bom(SAMPLE_DATA / "demo_bom.csv")

    assert result.is_valid
    assert result.errors == []

    resistor = result.parts["RES-10K-0603"]

    assert resistor.quantity == 3
    assert resistor.references == ["R1", "R2", "R3"]
    assert resistor.description == "10K Ohm Resistor"
    assert resistor.footprint == "0603"


def test_parse_bom_detects_conflicting_footprints(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "conflicting_bom.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference,description,footprint",
                "RES-10K,R1,10K Resistor,0603",
                "RES-10K,R2,10K Resistor,0805",
            ]
        ),
        encoding="utf-8",
    )

    result = parse_bom(bom_file)

    assert not result.is_valid
    assert any(
        "conflicting footprints" in error
        for error in result.errors
    )


def test_parse_bom_detects_reference_assigned_to_two_parts(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "duplicate_reference.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference,description,footprint",
                "RES-10K,R1,10K Resistor,0603",
                "RES-1K,R1,1K Resistor,0603",
            ]
        ),
        encoding="utf-8",
    )

    result = parse_bom(bom_file)

    assert not result.is_valid
    assert any(
        "assigned to both" in error
        for error in result.errors
    )


def test_parse_bom_rejects_missing_columns(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "missing_columns.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference",
                "RES-10K,R1",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(BOMParseError):
        parse_bom(bom_file)