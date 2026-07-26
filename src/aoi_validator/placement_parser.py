from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path


class PlacementParseError(Exception):
    """Raised when placement data cannot be parsed correctly."""


@dataclass(frozen=True)
class Placement:
    """Normalized placement information for one component."""

    reference: str
    part_id: str
    footprint: str
    side: str
    x_mm: float
    y_mm: float
    rotation_deg: float


@dataclass
class PlacementParseResult:
    """Result returned after parsing placement data."""

    placements: dict[str, Placement]
    warnings: list[str]
    errors: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.errors


REQUIRED_COLUMNS = {
    "reference",
    "part_id",
    "footprint",
    "side",
    "x_mm",
    "y_mm",
    "rotation_deg",
}

VALID_SIDES = {"TOP", "BOTTOM"}


def normalize_text(value: str | None) -> str:
    """Trim surrounding whitespace from a CSV value."""

    return (value or "").strip()


def normalize_reference(value: str | None) -> str:
    """Normalize a component reference designator."""

    return normalize_text(value).upper()


def normalize_part_id(value: str | None) -> str:
    """Normalize a part ID."""

    return normalize_text(value).upper()


def normalize_side(value: str | None) -> str:
    """Normalize the board side."""

    return normalize_text(value).upper()


def parse_float(
    value: str | None,
    *,
    field_name: str,
    row_number: int,
    errors: list[str],
) -> float | None:
    """Parse a required floating-point value."""

    normalized = normalize_text(value)

    if not normalized:
        errors.append(
            f"Row {row_number}: {field_name} is blank."
        )
        return None

    try:
        return float(normalized)
    except ValueError:
        errors.append(
            f"Row {row_number}: {field_name} must be numeric; "
            f"received '{normalized}'."
        )
        return None


def normalize_rotation(rotation: float) -> float:
    """
    Normalize a rotation to the range 0 <= rotation < 360.

    Examples:
        360 becomes 0
        -90 becomes 270
        450 becomes 90
    """

    normalized = rotation % 360.0

    if normalized == -0.0:
        return 0.0

    return normalized


def parse_placements(
    csv_path: str | Path,
) -> PlacementParseResult:
    """
    Parse component-placement CSV data.

    Expected columns:
        reference
        part_id
        footprint
        side
        x_mm
        y_mm
        rotation_deg
    """

    path = Path(csv_path)

    if not path.exists():
        raise PlacementParseError(
            f"Placement file does not exist: {path}"
        )

    if not path.is_file():
        raise PlacementParseError(
            f"Placement path is not a file: {path}"
        )

    placements: dict[str, Placement] = {}
    warnings: list[str] = []
    errors: list[str] = []

    try:
        with path.open(
            "r",
            encoding="utf-8-sig",
            newline="",
        ) as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise PlacementParseError(
                    "Placement file does not contain a header row."
                )

            normalized_headers = {
                normalize_text(header).lower()
                for header in reader.fieldnames
                if header is not None
            }

            missing_columns = REQUIRED_COLUMNS - normalized_headers

            if missing_columns:
                missing_list = ", ".join(
                    sorted(missing_columns)
                )
                raise PlacementParseError(
                    "Placement file is missing required columns: "
                    f"{missing_list}"
                )

            for row_number, raw_row in enumerate(
                reader,
                start=2,
            ):
                row = {
                    normalize_text(key).lower(): normalize_text(
                        value
                    )
                    for key, value in raw_row.items()
                    if key is not None
                }

                reference = normalize_reference(
                    row.get("reference")
                )
                part_id = normalize_part_id(
                    row.get("part_id")
                )
                footprint = normalize_text(
                    row.get("footprint")
                )
                side = normalize_side(row.get("side"))

                if not reference:
                    errors.append(
                        f"Row {row_number}: reference is blank."
                    )

                if not part_id:
                    errors.append(
                        f"Row {row_number}: part_id is blank."
                    )

                if not footprint:
                    warnings.append(
                        f"Row {row_number}: footprint is blank "
                        f"for reference {reference or '<blank>'}."
                    )

                if not side:
                    errors.append(
                        f"Row {row_number}: side is blank."
                    )
                elif side not in VALID_SIDES:
                    errors.append(
                        f"Row {row_number}: side must be TOP or "
                        f"BOTTOM; received '{side}'."
                    )

                x_mm = parse_float(
                    row.get("x_mm"),
                    field_name="x_mm",
                    row_number=row_number,
                    errors=errors,
                )

                y_mm = parse_float(
                    row.get("y_mm"),
                    field_name="y_mm",
                    row_number=row_number,
                    errors=errors,
                )

                rotation_deg = parse_float(
                    row.get("rotation_deg"),
                    field_name="rotation_deg",
                    row_number=row_number,
                    errors=errors,
                )

                row_has_required_error = (
                    not reference
                    or not part_id
                    or side not in VALID_SIDES
                    or x_mm is None
                    or y_mm is None
                    or rotation_deg is None
                )

                if row_has_required_error:
                    continue

                if reference in placements:
                    existing = placements[reference]

                    errors.append(
                        f"Row {row_number}: duplicate placement "
                        f"for reference {reference}; it was already "
                        f"placed as part {existing.part_id} on "
                        f"{existing.side}."
                    )
                    continue

                normalized_rotation = normalize_rotation(
                    rotation_deg
                )

                if rotation_deg != normalized_rotation:
                    warnings.append(
                        f"Row {row_number}: rotation "
                        f"{rotation_deg:g} for {reference} was "
                        f"normalized to "
                        f"{normalized_rotation:g} degrees."
                    )

                placements[reference] = Placement(
                    reference=reference,
                    part_id=part_id,
                    footprint=footprint,
                    side=side,
                    x_mm=x_mm,
                    y_mm=y_mm,
                    rotation_deg=normalized_rotation,
                )

    except UnicodeDecodeError as exc:
        raise PlacementParseError(
            f"Placement file is not valid UTF-8 text: {path}"
        ) from exc
    except csv.Error as exc:
        raise PlacementParseError(
            f"Unable to parse placement CSV: {exc}"
        ) from exc
    except OSError as exc:
        raise PlacementParseError(
            f"Unable to read placement file: {exc}"
        ) from exc

    return PlacementParseResult(
        placements=placements,
        warnings=warnings,
        errors=errors,
    )