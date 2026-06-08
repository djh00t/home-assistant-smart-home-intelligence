#!/usr/bin/env python3
"""Validate the person-room assignment slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/person_room_assignment.yaml",
    ROOT / "docs/contracts/person-room-assignment.md",
    ROOT / "src/smart_home_presence_intelligence/person_room_assignment.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing person-room assignment files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/person_room_assignment.yaml").read_text(encoding="utf-8")
    for needle in (
        "occupied_humans",
        "face+tracker",
        "occupancy_fallback",
        "face_tracker_agreement_requires_occupant_match: true",
        "single_occupant_fallback_allowed: true",
        "occupancy_fallback_confidence: 0.7",
        "person_targeted_automations: false",
    ):
        if needle not in text:
            raise SystemExit(f"person_room_assignment.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.person_room_assignment import assign_person_to_room  # noqa: WPS433

    agreed_plan = assign_person_to_room(
        {
            "room_id": "bedroom_spare",
            "occupied_humans": ["sel", "sam"],
            "face_identity": {"person_id": "sel", "confidence": 0.93},
            "tracker_identity": {"person_id": "sel", "confidence": 0.81},
        }
    )
    if agreed_plan["assigned_person"] != "sel":
        raise SystemExit("face+tracker agreement should assign matching occupant")
    if agreed_plan["assignment_source"] != "face+tracker":
        raise SystemExit("face+tracker agreement should use the combined source")
    if agreed_plan["confidence"] != 0.93:
        raise SystemExit("face+tracker agreement should keep the highest confidence")

    fallback_plan = assign_person_to_room(
        {
            "room_id": "kitchen",
            "occupied_humans": ["sam"],
        }
    )
    if fallback_plan["assigned_person"] != "sam":
        raise SystemExit("single occupant should be used for occupancy fallback")
    if fallback_plan["assignment_source"] != "occupancy_fallback":
        raise SystemExit("single occupant should use the fallback source")
    if fallback_plan["confidence"] != 0.7:
        raise SystemExit("single occupant fallback should use the low-confidence plan")

    ambiguous_plan = assign_person_to_room(
        {
            "room_id": "lounge_room",
            "occupied_humans": ["sel", "sam"],
            "tracker_identity": {"person_id": "alex", "confidence": 0.88},
        }
    )
    if ambiguous_plan["assigned_person"] is not None:
        raise SystemExit("non-occupant identity should not assign a person")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_person_room_assignment.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Person-room assignment check passed"
        if sys.argv[1] == "check"
        else "Person-room assignment quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
