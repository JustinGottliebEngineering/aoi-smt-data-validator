from __future__ import annotations

import argparse
import sys
from pathlib import Path

from aoi_validator.bom_parser import (
    BOMParseError,
    parse_bom,
)
from aoi_validator.placement_parser import (
    PlacementParseError,
    parse_placements,
)
from aoi_validator.report import (
    build_report_data,
    format_text_report,
    write_json_report,
    write_text_report,
)
from aoi_validator.validator import (
    validate_bom_against_placements,
)


def build_argument_parser() -> argparse.ArgumentParser:
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Validate fictional AOI and SMT BOM and "
            "placement data."
        )
    )

    parser.add_argument(
        "bom",
        type=Path,
        help="Path to the BOM CSV file.",
    )

    parser.add_argument(
        "placements",
        type=Path,
        help="Path to the placement CSV file.",
    )

    parser.add_argument(
        "--text-report",
        type=Path,
        help="Optional output path for a text report.",
    )

    parser.add_argument(
        "--json-report",
        type=Path,
        help="Optional output path for a JSON report.",
    )

    return parser


def main() -> int:
    """Run BOM and placement validation."""

    parser = build_argument_parser()
    args = parser.parse_args()

    try:
        bom_result = parse_bom(args.bom)
        placement_result = parse_placements(
            args.placements
        )
    except (
        BOMParseError,
        PlacementParseError,
    ) as exc:
        print(
            f"Unable to process input files: {exc}",
            file=sys.stderr,
        )
        return 2

    validation_result = (
        validate_bom_against_placements(
            bom_result,
            placement_result,
        )
    )

    report_data = build_report_data(
        bom_result,
        placement_result,
        validation_result,
    )

    print(format_text_report(report_data))

    if args.text_report:
        output_path = write_text_report(
            report_data,
            args.text_report,
        )
        print(f"\nText report written to: {output_path}")

    if args.json_report:
        output_path = write_json_report(
            report_data,
            args.json_report,
        )
        print(f"JSON report written to: {output_path}")

    return 0 if validation_result.is_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())