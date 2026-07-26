from __future__ import annotations

from dataclasses import dataclass, field

from aoi_validator.bom_parser import BOMParseResult
from aoi_validator.placement_parser import PlacementParseResult


@dataclass
class ValidationResult:
    """Consolidated comparison of BOM and placement data."""

    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    matched_references: list[str] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True when no validation errors were found."""

        return not self.errors

    @property
    def matched_count(self) -> int:
        """Return the number of correctly matched references."""

        return len(self.matched_references)


def validate_bom_against_placements(
    bom_result: BOMParseResult,
    placement_result: PlacementParseResult,
) -> ValidationResult:
    """
    Compare parsed BOM data against parsed placement data.

    Validation includes:
    - Parser errors and warnings
    - BOM references missing from placement data
    - Placement references missing from the BOM
    - Part ID mismatches
    - Footprint mismatches
    """

    errors: list[str] = []
    warnings: list[str] = []
    matched_references: list[str] = []

    errors.extend(
        f"BOM parser: {message}"
        for message in bom_result.errors
    )
    errors.extend(
        f"Placement parser: {message}"
        for message in placement_result.errors
    )

    warnings.extend(
        f"BOM parser: {message}"
        for message in bom_result.warnings
    )
    warnings.extend(
        f"Placement parser: {message}"
        for message in placement_result.warnings
    )

    bom_references: dict[str, str] = {}

    for part_id, part in bom_result.parts.items():
        for reference in part.references:
            bom_references[reference] = part_id

    placement_references = set(
        placement_result.placements.keys()
    )
    expected_references = set(bom_references.keys())

    missing_from_placements = sorted(
        expected_references - placement_references
    )

    unexpected_placements = sorted(
        placement_references - expected_references
    )

    for reference in missing_from_placements:
        expected_part_id = bom_references[reference]

        errors.append(
            f"Reference {reference} is listed in the BOM as "
            f"part {expected_part_id} but is missing from the "
            f"placement data."
        )

    for reference in unexpected_placements:
        placement = placement_result.placements[reference]

        errors.append(
            f"Reference {reference} appears in the placement data "
            f"as part {placement.part_id} but is not listed in the BOM."
        )

    shared_references = sorted(
        expected_references & placement_references
    )

    for reference in shared_references:
        expected_part_id = bom_references[reference]
        bom_part = bom_result.parts[expected_part_id]
        placement = placement_result.placements[reference]

        reference_has_error = False

        if placement.part_id != expected_part_id:
            errors.append(
                f"Reference {reference} has part ID "
                f"{placement.part_id} in placement data but "
                f"{expected_part_id} in the BOM."
            )
            reference_has_error = True

        bom_footprint = bom_part.footprint.strip()
        placement_footprint = placement.footprint.strip()

        if (
            bom_footprint
            and placement_footprint
            and bom_footprint.casefold()
            != placement_footprint.casefold()
        ):
            errors.append(
                f"Reference {reference} has footprint "
                f"{placement_footprint} in placement data but "
                f"{bom_footprint} in the BOM."
            )
            reference_has_error = True

        elif bom_footprint and not placement_footprint:
            warnings.append(
                f"Reference {reference} has BOM footprint "
                f"{bom_footprint}, but the placement footprint "
                f"is blank."
            )

        elif placement_footprint and not bom_footprint:
            warnings.append(
                f"Reference {reference} has placement footprint "
                f"{placement_footprint}, but the BOM footprint "
                f"is blank."
            )

        if not reference_has_error:
            matched_references.append(reference)

    return ValidationResult(
        errors=errors,
        warnings=warnings,
        matched_references=matched_references,
    )