#!/usr/bin/env python3
"""Validate the vehicle-person linking slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/vehicle_person_linking.yaml",
    ROOT / "docs/contracts/vehicle-person-linking.md",
    ROOT / "src/smart_home_presence_intelligence/vehicle_person_linking.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing vehicle-person linking files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/vehicle_person_linking.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "behavior: deterministic_linking",
        "no_vehicle_person_actioning",
        "no_garage_door_actuation",
        "plate_confidence_threshold: 0.8",
        "face_match_confidence_threshold: 0.75",
        "vehicle_arrival",
        "vehicle_departure",
    ):
        if needle not in text:
            raise SystemExit(
                f"vehicle_person_linking.yaml missing required text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.vehicle_person_linking import (  # noqa: E501
        LINKING_SOURCE,
        VEHICLE_ARRIVAL_EVENT,
        VEHICLE_DEPARTURE_EVENT,
        PLATE_CONFIDENCE_THRESHOLD,
        FACE_MATCH_CONFIDENCE_THRESHOLD,
        build_vehicle_person_linked_event,
    )

    arrival_event = build_vehicle_person_linked_event(
        {
            "room_id": "driveway",
            "person_id": "sel",
            "plate": "ab c-12",
            "plate_confidence": 0.86,
            "face_match_confidence": 0.84,
            "direction": "enter",
            "camera": "frigate_driveway",
            "event_id": "link-1",
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if arrival_event["source"] != LINKING_SOURCE:
        raise SystemExit("linked event should use vehicle-person linking source")
    if arrival_event["type"] != VEHICLE_ARRIVAL_EVENT:
        raise SystemExit("arrival direction should map to vehicle_arrival")
    if arrival_event["room"] != "driveway":
        raise SystemExit("room should be driveway")
    if arrival_event["person_id"] != "sel":
        raise SystemExit("person_id should be preserved")
    if arrival_event["vehicle"]["plate"] != "ABC12":
        raise SystemExit("plate should be canonicalized")
    if arrival_event["confidence"] != 0.84:
        raise SystemExit("linked confidence should be the minimum evidence confidence")
    if arrival_event["vehicle"]["plate_confidence"] != 0.86:
        raise SystemExit("vehicle plate confidence should be preserved")
    if arrival_event["vehicle"]["face_match_confidence"] != 0.84:
        raise SystemExit("face match confidence should be preserved")

    departure_event = build_vehicle_person_linked_event(
        {
            "room_id": "driveway",
            "person_id": "sel",
            "plate": "xy z-9",
            "plate_confidence": 1.0,
            "face_match_confidence": 0.9,
            "direction": "exit",
            "camera": "frigate_driveway",
        }
    )
    if departure_event["type"] != VEHICLE_DEPARTURE_EVENT:
        raise SystemExit("departure direction should map to vehicle_departure")

    if PLATE_CONFIDENCE_THRESHOLD != 0.8:
        raise SystemExit("plate confidence threshold should be explicit")
    if FACE_MATCH_CONFIDENCE_THRESHOLD != 0.75:
        raise SystemExit("face-match confidence threshold should be explicit")

    try:
        build_vehicle_person_linked_event(
            {
                "room_id": "hall",
                "person_id": "sel",
                "plate": "ABC123",
                "plate_confidence": 0.9,
                "face_match_confidence": 0.9,
                "direction": "enter",
                "camera": "frigate_driveway",
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("non-driveway payload should be rejected")

    try:
        build_vehicle_person_linked_event(
            {
                "room_id": "driveway",
                "person_id": "sel",
                "plate": "ABC123",
                "plate_confidence": 0.79,
                "face_match_confidence": 0.9,
                "direction": "enter",
                "camera": "frigate_driveway",
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("low plate confidence should be rejected")

    try:
        build_vehicle_person_linked_event(
            {
                "room_id": "driveway",
                "person_id": "sel",
                "plate": "ABC123",
                "plate_confidence": 0.9,
                "face_match_confidence": 0.74,
                "direction": "enter",
                "camera": "frigate_driveway",
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("low face confidence should be rejected")

    try:
        build_vehicle_person_linked_event(
            {
                "room_id": "driveway",
                "person_id": "sel",
                "plate": "ABC123",
                "plate_confidence": 0.9,
                "face_match_confidence": 0.9,
                "direction": "stay",
                "camera": "frigate_driveway",
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("non-arrival/departure direction should be rejected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_vehicle_person_linking.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Vehicle-person linking check passed"
        if sys.argv[1] == "check"
        else "Vehicle-person linking quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
