from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from aoi_validator.bom_parser import BOMParseResult
from aoi_validator.placement_parser import PlacementParseResult
from aoi_validator.validator import ValidationResult


def build_report_data(
    bom_result: BOMParseResult,
    placement_result: PlacementParseResult,
    validation_result: ValidationResult,
) -> dict[str, Any]:
    """Build a structured report from parsed and validated data."""

    total_bom_references = sum(
        part.quantity
        for part in bom_result.parts.values()
    )

    top_count = sum(
        1
        for placement in placement_result.placements.values()
        if placement.side == "TOP"
    )

    bottom_count = sum(
        1
        for placement in placement_result.placements.values()
        if placement.side == "BOTTOM"
    )

    parts = []

    for part_id in sorted(bom_result.parts):
        part = bom_result.parts[part_id]

        parts.append(
            {
                "part_id": part.part_id,
                "description": part.description,
                "footprint": part.footprint,
                "quantity": part.quantity,
                "references": part.references,
            }
        )

    placements = []

    for reference in sorted(placement_result.placements):
        placement = placement_result.placements[reference]
        placements.append(asdict(placement))

    return {
        "status": (
            "PASS"
            if validation_result.is_valid
            else "FAIL"
        ),
        "summary": {
            "unique_bom_parts": len(bom_result.parts),
            "total_bom_references": total_bom_references,
            "total_placements": len(
                placement_result.placements
            ),
            "matched_references": (
                validation_result.matched_count
            ),
            "top_side_placements": top_count,
            "bottom_side_placements": bottom_count,
            "error_count": len(validation_result.errors),
            "warning_count": len(
                validation_result.warnings
            ),
        },
        "errors": validation_result.errors,
        "warnings": validation_result.warnings,
        "parts": parts,
        "placements": placements,
    }


def format_text_report(
    report_data: dict[str, Any],
) -> str:
    """Format structured report data as readable text."""

    summary = report_data["summary"]

    lines = [
        "=" * 68,
        "AOI / SMT DATA VALIDATION REPORT",
        "=" * 68,
        "",
        f"Overall Status:          {report_data['status']}",
        "",
        "SUMMARY",
        "-" * 68,
        (
            "Unique BOM Parts:       "
            f"{summary['unique_bom_parts']}"
        ),
        (
            "Total BOM References:   "
            f"{summary['total_bom_references']}"
        ),
        (
            "Total Placements:       "
            f"{summary['total_placements']}"
        ),
        (
            "Matched References:     "
            f"{summary['matched_references']}"
        ),
        (
            "Top-Side Placements:    "
            f"{summary['top_side_placements']}"
        ),
        (
            "Bottom-Side Placements: "
            f"{summary['bottom_side_placements']}"
        ),
        (
            "Errors:                 "
            f"{summary['error_count']}"
        ),
        (
            "Warnings:               "
            f"{summary['warning_count']}"
        ),
        "",
    ]

    lines.append("ERRORS")
    lines.append("-" * 68)

    if report_data["errors"]:
        for index, error in enumerate(
            report_data["errors"],
            start=1,
        ):
            lines.append(f"{index}. {error}")
    else:
        lines.append("None")

    lines.append("")
    lines.append("WARNINGS")
    lines.append("-" * 68)

    if report_data["warnings"]:
        for index, warning in enumerate(
            report_data["warnings"],
            start=1,
        ):
            lines.append(f"{index}. {warning}")
    else:
        lines.append("None")

    lines.append("")
    lines.append("BOM PARTS")
    lines.append("-" * 68)

    for part in report_data["parts"]:
        references = ", ".join(part["references"])

        lines.append(
            f"{part['part_id']} | "
            f"Qty: {part['quantity']} | "
            f"Footprint: {part['footprint'] or '<blank>'}"
        )
        lines.append(
            f"  Description: "
            f"{part['description'] or '<blank>'}"
        )
        lines.append(
            f"  References: {references}"
        )

    lines.append("")
    lines.append("PLACEMENTS")
    lines.append("-" * 68)

    for placement in report_data["placements"]:
        lines.append(
            f"{placement['reference']} | "
            f"{placement['part_id']} | "
            f"{placement['side']} | "
            f"X={placement['x_mm']:.3f} mm | "
            f"Y={placement['y_mm']:.3f} mm | "
            f"Rotation={placement['rotation_deg']:g} deg"
        )

    lines.append("")
    lines.append("=" * 68)

    return "\n".join(lines)


def write_text_report(
    report_data: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write a readable text report to disk."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        format_text_report(report_data),
        encoding="utf-8",
    )

    return path


def write_json_report(
    report_data: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Write structured report data as formatted JSON."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            report_data,
            indent=2,
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    return path