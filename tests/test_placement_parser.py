from pathlib import Path

import pytest

from aoi_validator.placement_parser import (
    PlacementParseError,
    parse_placements,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA = PROJECT_ROOT / "sample_data"


def test_parse_placements_reads_valid_data() -> None:
    result = parse_placements(
        SAMPLE_DATA / "demo_placements.csv"
    )

    assert result.is_valid
    assert result.errors == []
    assert len(result.placements) == 8

    resistor = result.placements["R1"]

    assert resistor.part_id == "RES-10K-0603"
    assert resistor.footprint == "0603"
    assert resistor.side == "TOP"
    assert resistor.x_mm == 12.5
    assert resistor.y_mm == 18.25
    assert resistor.rotation_deg == 0.0


def test_parse_placements_accepts_bottom_side() -> None:
    result = parse_placements(
        SAMPLE_DATA / "demo_placements.csv"
    )

    resistor = result.placements["R3"]

    assert resistor.side == "BOTTOM"
    assert resistor.rotation_deg == 180.0


def test_parse_placements_normalizes_rotation() -> None:
    result = parse_placements(
        SAMPLE_DATA / "demo_placements.csv"
    )

    capacitor = result.placements["C2"]

    assert capacitor.rotation_deg == 0.0
    assert any(
        "normalized to 0 degrees" in warning
        for warning in result.warnings
    )


def test_parse_placements_rejects_invalid_side(
    tmp_path: Path,
) -> None:
    placement_file = tmp_path / "invalid_side.csv"

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                (
                    "R1,RES-10K-0603,0603,LEFT,"
                    "12.5,18.25,0"
                ),
            ]
        ),
        encoding="utf-8",
    )

    result = parse_placements(placement_file)

    assert not result.is_valid
    assert any(
        "side must be TOP or BOTTOM" in error
        for error in result.errors
    )


def test_parse_placements_rejects_duplicate_reference(
    tmp_path: Path,
) -> None:
    placement_file = tmp_path / "duplicate.csv"

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                (
                    "R1,RES-10K-0603,0603,TOP,"
                    "12.5,18.25,0"
                ),
                (
                    "R1,RES-10K-0603,0603,BOTTOM,"
                    "25.0,30.0,180"
                ),
            ]
        ),
        encoding="utf-8",
    )

    result = parse_placements(placement_file)

    assert not result.is_valid
    assert any(
        "duplicate placement" in error
        for error in result.errors
    )


def test_parse_placements_rejects_missing_coordinates(
    tmp_path: Path,
) -> None:
    placement_file = tmp_path / "missing_coordinate.csv"

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                "R1,RES-10K-0603,0603,TOP,,18.25,0",
            ]
        ),
        encoding="utf-8",
    )

    result = parse_placements(placement_file)

    assert not result.is_valid
    assert any(
        "x_mm is blank" in error
        for error in result.errors
    )


def test_parse_placements_rejects_non_numeric_rotation(
    tmp_path: Path,
) -> None:
    placement_file = tmp_path / "invalid_rotation.csv"

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                (
                    "R1,RES-10K-0603,0603,TOP,"
                    "12.5,18.25,NORTH"
                ),
            ]
        ),
        encoding="utf-8",
    )

    result = parse_placements(placement_file)

    assert not result.is_valid
    assert any(
        "rotation_deg must be numeric" in error
        for error in result.errors
    )


def test_parse_placements_rejects_missing_columns(
    tmp_path: Path,
) -> None:
    placement_file = tmp_path / "missing_columns.csv"

    placement_file.write_text(
        "\n".join(
            [
                "reference,part_id,side",
                "R1,RES-10K-0603,TOP",
            ]
        ),
        encoding="utf-8",
    )

    with pytest.raises(PlacementParseError):
        parse_placements(placement_file)