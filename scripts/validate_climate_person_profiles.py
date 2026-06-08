#!/usr/bin/env python3
"""Validate the climate-person profile slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/climate_person_profiles.yaml",
    ROOT / "docs/contracts/climate-person-profiles.md",
    ROOT / "src/smart_home_presence_intelligence/climate_person_profiles.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing climate-person profile files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/climate_person_profiles.yaml").read_text(encoding="utf-8")
    for needle in (
        "room_id",
        "assigned_person",
        "assignment_source",
        "confidence",
        "climate_profiles",
        "assignment_required_for_resolution: true",
        "mapping_required_for_apply: true",
        "should_apply_marks_planning_only: true",
        "person_targeted_automations: false",
        "preserve_room_context: true",
        "preserve_assigned_person: true",
        "preserve_assignment_source: true",
        "preserve_confidence: true",
        "preserve_climate_profiles: true",
    ):
        if needle not in text:
            raise SystemExit(f"climate_person_profiles.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.climate_person_profiles import resolve_climate_person_profile  # noqa: WPS433

    resolved_plan = resolve_climate_person_profile(
        {
            "room_id": "living_room",
            "assigned_person": "Sel",
            "assignment_source": "face+tracker",
            "confidence": 0.93,
            "climate_profiles": {"Sel": "cool_evening"},
        }
    )
    if resolved_plan["climate_profile"] != "cool_evening":
        raise SystemExit("mapped person should resolve a climate profile")
    if not resolved_plan["should_apply"]:
        raise SystemExit("mapped person should apply the climate profile")

    no_assignment_plan = resolve_climate_person_profile(
        {
            "room_id": "kitchen",
            "assigned_person": None,
            "assignment_source": "occupancy_fallback",
            "confidence": 0.7,
            "climate_profiles": {"Sel": "cool_evening"},
        }
    )
    if no_assignment_plan["climate_profile"] is not None:
        raise SystemExit("unassigned rooms should not resolve a climate profile")
    if no_assignment_plan["should_apply"]:
        raise SystemExit("unassigned rooms should not apply climate profiles")

    missing_profile_plan = resolve_climate_person_profile(
        {
            "room_id": "office",
            "assigned_person": "Sam",
            "assignment_source": "face",
            "confidence": 0.81,
            "climate_profiles": {"Sel": "cool_evening"},
        }
    )
    if missing_profile_plan["climate_profile"] is not None:
        raise SystemExit("unmapped people should not resolve a climate profile")
    if missing_profile_plan["should_apply"]:
        raise SystemExit("unmapped people should not apply climate profiles")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_climate_person_profiles.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Climate-person profile check passed"
        if sys.argv[1] == "check"
        else "Climate-person profile quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
