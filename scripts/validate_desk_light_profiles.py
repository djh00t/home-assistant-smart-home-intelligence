#!/usr/bin/env python3
"""Validate the desk-light profile slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/desk_light_profiles.yaml",
    ROOT / "docs/contracts/desk-light-profiles.md",
    ROOT / "src/smart_home_presence_intelligence/desk_light_profiles.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing desk-light profile files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/desk_light_profiles.yaml").read_text(encoding="utf-8")
    for needle in (
        "room_id",
        "assigned_person",
        "assignment_source",
        "confidence",
        "desk_profiles",
        "room_gamma_only_resolution: true",
        "assignment_required_for_resolution: true",
        "should_apply_marks_planning_only: true",
        "person_targeted_automations: false",
        "preserve_room_context: true",
        "preserve_assigned_person: true",
        "preserve_assignment_source: true",
        "preserve_confidence: true",
    ):
        if needle not in text:
            raise SystemExit(f"desk_light_profiles.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.desk_light_profiles import resolve_desk_light_profile  # noqa: WPS433

    room_gamma_plan = resolve_desk_light_profile(
        {
            "room_id": "room_gamma",
            "assigned_person": "Sel",
            "assignment_source": "face+tracker",
            "confidence": 0.93,
            "desk_profiles": {"Sel": "sel_desk"},
        }
    )
    if room_gamma_plan["desk_light_profile"] != "sel_desk":
        raise SystemExit("room_gamma desk-light profile should resolve for the assigned person")
    if not room_gamma_plan["should_apply"]:
        raise SystemExit("room_gamma desk-light profile should be applied when mapped")

    no_op_plan = resolve_desk_light_profile(
        {
            "room_id": "room_epsilon",
            "assigned_person": "Sel",
            "assignment_source": "occupancy_fallback",
            "confidence": 0.7,
            "desk_profiles": {"Sel": "sel_desk"},
        }
    )
    if no_op_plan["desk_light_profile"] is not None:
        raise SystemExit("non-room_gamma rooms should not resolve a desk-light profile")
    if no_op_plan["should_apply"]:
        raise SystemExit("non-room_gamma rooms should not apply desk-light profiles")

    missing_profile_plan = resolve_desk_light_profile(
        {
            "room_id": "room_gamma",
            "assigned_person": "Sam",
            "assignment_source": "face",
            "confidence": 0.81,
            "desk_profiles": {"Sel": "sel_desk"},
        }
    )
    if missing_profile_plan["desk_light_profile"] is not None:
        raise SystemExit("unmapped people should not resolve a desk-light profile")
    if missing_profile_plan["should_apply"]:
        raise SystemExit("unmapped people should not apply desk-light profiles")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_desk_light_profiles.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Desk-light profile check passed"
        if sys.argv[1] == "check"
        else "Desk-light profile quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
