from pathlib import Path

from aoi_validator.bom_parser import parse_bom
from aoi_validator.placement_parser import parse_placements
from aoi_validator.validator import (
    validate_bom_against_placements,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA = PROJECT_ROOT / "sample_data"


def test_validator_accepts_matching_bom_and_placements() -> None:
    bom_result = parse_bom(
        SAMPLE_DATA / "demo_bom.csv"
    )
    placement_result = parse_placements(
        SAMPLE_DATA / "demo_placements.csv"
    )

    result = validate_bom_against_placements(
        bom_result,
        placement_result,
    )

    assert result.is_valid
    assert result.errors == []
    assert result.matched_count == 8
    assert result.matched_references == [
        "C1",
        "C2",
        "D1",
        "J1",
        "R1",
        "R2",
        "R3",
        "U1",
    ]


def test_validator_detects_bom_reference_missing_from_placements(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "bom.csv"
    placement_file = tmp_path / "placements.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference,description,footprint",
                "RES-10K,R1,10K Resistor,0603",
                "RES-10K,R2,10K Resistor,0603",
            ]
        ),
        encoding="utf-8",
    )

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                "R1,RES-10K,0603,TOP,10.0,20.0,0",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_bom_against_placements(
        parse_bom(bom_file),
        parse_placements(placement_file),
    )

    assert not result.is_valid
    assert any(
        "R2" in error
        and "missing from the placement data" in error
        for error in result.errors
    )


def test_validator_detects_placement_reference_missing_from_bom(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "bom.csv"
    placement_file = tmp_path / "placements.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference,description,footprint",
                "RES-10K,R1,10K Resistor,0603",
            ]
        ),
        encoding="utf-8",
    )

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                "R1,RES-10K,0603,TOP,10.0,20.0,0",
                "R2,RES-10K,0603,TOP,15.0,20.0,0",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_bom_against_placements(
        parse_bom(bom_file),
        parse_placements(placement_file),
    )

    assert not result.is_valid
    assert any(
        "R2" in error
        and "not listed in the BOM" in error
        for error in result.errors
    )


def test_validator_detects_part_id_mismatch(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "bom.csv"
    placement_file = tmp_path / "placements.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference,description,footprint",
                "RES-10K,R1,10K Resistor,0603",
            ]
        ),
        encoding="utf-8",
    )

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                "R1,RES-1K,0603,TOP,10.0,20.0,0",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_bom_against_placements(
        parse_bom(bom_file),
        parse_placements(placement_file),
    )

    assert not result.is_valid
    assert any(
        "R1" in error
        and "RES-1K" in error
        and "RES-10K" in error
        for error in result.errors
    )


def test_validator_detects_footprint_mismatch(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "bom.csv"
    placement_file = tmp_path / "placements.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference,description,footprint",
                "RES-10K,R1,10K Resistor,0603",
            ]
        ),
        encoding="utf-8",
    )

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                "R1,RES-10K,0805,TOP,10.0,20.0,0",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_bom_against_placements(
        parse_bom(bom_file),
        parse_placements(placement_file),
    )

    assert not result.is_valid
    assert any(
        "R1" in error
        and "0805" in error
        and "0603" in error
        for error in result.errors
    )


def test_validator_includes_parser_errors(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "bom.csv"
    placement_file = tmp_path / "placements.csv"

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

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                "R1,RES-10K,0603,TOP,10.0,20.0,0",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_bom_against_placements(
        parse_bom(bom_file),
        parse_placements(placement_file),
    )

    assert not result.is_valid
    assert any(
        error.startswith("BOM parser:")
        for error in result.errors
    )


def test_validator_warns_when_placement_footprint_is_blank(
    tmp_path: Path,
) -> None:
    bom_file = tmp_path / "bom.csv"
    placement_file = tmp_path / "placements.csv"

    bom_file.write_text(
        "\n".join(
            [
                "part_id,reference,description,footprint",
                "RES-10K,R1,10K Resistor,0603",
            ]
        ),
        encoding="utf-8",
    )

    placement_file.write_text(
        "\n".join(
            [
                (
                    "reference,part_id,footprint,side,"
                    "x_mm,y_mm,rotation_deg"
                ),
                "R1,RES-10K,,TOP,10.0,20.0,0",
            ]
        ),
        encoding="utf-8",
    )

    result = validate_bom_against_placements(
        parse_bom(bom_file),
        parse_placements(placement_file),
    )

    assert result.is_valid
    assert any(
        "placement footprint is blank" in warning
        for warning in result.warnings
    )