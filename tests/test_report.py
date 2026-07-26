import json
from pathlib import Path

from aoi_validator.bom_parser import parse_bom
from aoi_validator.placement_parser import parse_placements
from aoi_validator.report import (
    build_report_data,
    format_text_report,
    write_json_report,
    write_text_report,
)
from aoi_validator.validator import (
    validate_bom_against_placements,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DATA = PROJECT_ROOT / "sample_data"


def build_sample_report() -> dict:
    bom_result = parse_bom(
        SAMPLE_DATA / "demo_bom.csv"
    )
    placement_result = parse_placements(
        SAMPLE_DATA / "demo_placements.csv"
    )
    validation_result = (
        validate_bom_against_placements(
            bom_result,
            placement_result,
        )
    )

    return build_report_data(
        bom_result,
        placement_result,
        validation_result,
    )


def test_build_report_data_contains_summary() -> None:
    report = build_sample_report()

    assert report["status"] == "PASS"
    assert report["summary"]["unique_bom_parts"] == 5
    assert report["summary"]["total_bom_references"] == 8
    assert report["summary"]["total_placements"] == 8
    assert report["summary"]["matched_references"] == 8
    assert report["summary"]["top_side_placements"] == 6
    assert report["summary"]["bottom_side_placements"] == 2


def test_format_text_report_contains_status() -> None:
    report = build_sample_report()
    text = format_text_report(report)

    assert "AOI / SMT DATA VALIDATION REPORT" in text
    assert "Overall Status:          PASS" in text
    assert "Unique BOM Parts:       5" in text
    assert "Bottom-Side Placements: 2" in text


def test_write_text_report(
    tmp_path: Path,
) -> None:
    report = build_sample_report()
    output_path = tmp_path / "report.txt"

    result_path = write_text_report(
        report,
        output_path,
    )

    assert result_path == output_path
    assert output_path.exists()
    assert "Overall Status" in output_path.read_text(
        encoding="utf-8"
    )


def test_write_json_report(
    tmp_path: Path,
) -> None:
    report = build_sample_report()
    output_path = tmp_path / "report.json"

    result_path = write_json_report(
        report,
        output_path,
    )

    assert result_path == output_path
    assert output_path.exists()

    loaded = json.loads(
        output_path.read_text(encoding="utf-8")
    )

    assert loaded["status"] == "PASS"
    assert loaded["summary"]["matched_references"] == 8