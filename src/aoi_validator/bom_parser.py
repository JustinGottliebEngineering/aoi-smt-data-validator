from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path


class BOMParseError(Exception):
    """Raised when a BOM file cannot be parsed correctly."""


@dataclass
class BOMPart:
    """Normalized BOM data for one unique part ID."""

    part_id: str
    description: str
    footprint: str
    references: list[str] = field(default_factory=list)

    @property
    def quantity(self) -> int:
        return len(self.references)


@dataclass
class BOMParseResult:
    """Result returned after parsing and validating a BOM."""

    parts: dict[str, BOMPart]
    warnings: list[str]
    errors: list[str]

    @property
    def is_valid(self) -> bool:
        return not self.errors


REQUIRED_COLUMNS = {
    "part_id",
    "reference",
    "description",
    "footprint",
}


def normalize_text(value: str | None) -> str:
    """Trim surrounding whitespace from a CSV value."""

    return (value or "").strip()


def normalize_part_id(value: str | None) -> str:
    """Normalize part IDs for reliable grouping."""

    return normalize_text(value).upper()


def normalize_reference(value: str | None) -> str:
    """Normalize a component reference designator."""

    return normalize_text(value).upper()


def parse_bom(csv_path: str | Path) -> BOMParseResult:
    """
    Parse a BOM CSV and group all references that use the same part ID.

    Expected columns:
        part_id
        reference
        description
        footprint
    """

    path = Path(csv_path)

    if not path.exists():
        raise BOMParseError(f"BOM file does not exist: {path}")

    if not path.is_file():
        raise BOMParseError(f"BOM path is not a file: {path}")

    parts: dict[str, BOMPart] = {}
    warnings: list[str] = []
    errors: list[str] = []
    seen_references: dict[str, str] = {}

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)

            if reader.fieldnames is None:
                raise BOMParseError("BOM file does not contain a header row.")

            normalized_headers = {
                normalize_text(header).lower()
                for header in reader.fieldnames
                if header is not None
            }

            missing_columns = REQUIRED_COLUMNS - normalized_headers

            if missing_columns:
                missing_list = ", ".join(sorted(missing_columns))
                raise BOMParseError(
                    f"BOM is missing required columns: {missing_list}"
                )

            for row_number, raw_row in enumerate(reader, start=2):
                row = {
                    normalize_text(key).lower(): normalize_text(value)
                    for key, value in raw_row.items()
                    if key is not None
                }

                part_id = normalize_part_id(row.get("part_id"))
                reference = normalize_reference(row.get("reference"))
                description = normalize_text(row.get("description"))
                footprint = normalize_text(row.get("footprint"))

                if not part_id:
                    errors.append(
                        f"Row {row_number}: part_id is blank."
                    )
                    continue

                if not reference:
                    errors.append(
                        f"Row {row_number}: reference is blank for part "
                        f"{part_id}."
                    )
                    continue

                if reference in seen_references:
                    previous_part_id = seen_references[reference]

                    if previous_part_id == part_id:
                        warnings.append(
                            f"Row {row_number}: duplicate reference "
                            f"{reference} for part {part_id}."
                        )
                    else:
                        errors.append(
                            f"Row {row_number}: reference {reference} is "
                            f"assigned to both {previous_part_id} and "
                            f"{part_id}."
                        )

                    continue

                seen_references[reference] = part_id

                existing_part = parts.get(part_id)

                if existing_part is None:
                    parts[part_id] = BOMPart(
                        part_id=part_id,
                        description=description,
                        footprint=footprint,
                        references=[reference],
                    )
                    continue

                if (
                    description
                    and existing_part.description
                    and description.casefold()
                    != existing_part.description.casefold()
                ):
                    errors.append(
                        f"Row {row_number}: conflicting descriptions for "
                        f"part {part_id}: "
                        f"'{existing_part.description}' and "
                        f"'{description}'."
                    )

                if (
                    footprint
                    and existing_part.footprint
                    and footprint.casefold()
                    != existing_part.footprint.casefold()
                ):
                    errors.append(
                        f"Row {row_number}: conflicting footprints for "
                        f"part {part_id}: "
                        f"'{existing_part.footprint}' and "
                        f"'{footprint}'."
                    )

                if not existing_part.description and description:
                    existing_part.description = description

                if not existing_part.footprint and footprint:
                    existing_part.footprint = footprint

                existing_part.references.append(reference)

    except UnicodeDecodeError as exc:
        raise BOMParseError(
            f"BOM file is not valid UTF-8 text: {path}"
        ) from exc
    except csv.Error as exc:
        raise BOMParseError(
            f"Unable to parse BOM CSV: {exc}"
        ) from exc
    except OSError as exc:
        raise BOMParseError(
            f"Unable to read BOM file: {exc}"
        ) from exc

    for part in parts.values():
        part.references.sort()

        if not part.description:
            warnings.append(
                f"Part {part.part_id} does not have a description."
            )

        if not part.footprint:
            warnings.append(
                f"Part {part.part_id} does not have a footprint."
            )

    return BOMParseResult(
        parts=parts,
        warnings=warnings,
        errors=errors,
    )