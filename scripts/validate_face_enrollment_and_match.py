#!/usr/bin/env python3
"""Validate the face enrollment and match canonicalization slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/face_enrollment_and_match.yaml",
    ROOT / "docs/contracts/face-enrollment-and-match.md",
    ROOT / "src/smart_home_presence_intelligence/face_enrollment_and_match.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing face enrollment and match files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/face_enrollment_and_match.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "canonicalization_only",
        "backlog_boundary:",
        "no_vehicle_person_linking",
        "no_camera_only_unlock_actions",
        "no_door_or_lock_actuation",
        "no_face_match_as_only_unlock_signal",
        "deterministic_threshold: 0.75",
        "retention_days: 90",
        "source: face",
        "entity_class: human",
        "room_reference_required: true",
        "output_event_type: confidence",
    ):
        if needle not in text:
            raise SystemExit(
                f"face_enrollment_and_match.yaml missing required text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.face_enrollment_and_match import (  # noqa: E501
        FACE_MATCH_THRESHOLD,
        build_face_enrollment_record,
        build_face_match_event,
        FACE_ENROLLMENT_RECORD_RETENTION_DAYS,
    )

    record = build_face_enrollment_record(
        {
            "person_id": "sel",
            "room": "bedroom_spare",
            "camera": "cam_lounge_room_front",
            "face_signature": "sig_abc123",
            "source": "face",
            "recorded_at": "2026-06-08T09:00:00Z",
        }
    )
    if record["person_id"] != "sel":
        raise SystemExit("enrollment should preserve person_id")
    if record["room"] != "bedroom_spare":
        raise SystemExit("enrollment should preserve room")
    if record["camera"] != "cam_lounge_room_front":
        raise SystemExit("enrollment should preserve camera")
    retention = record.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 90:
        raise SystemExit("enrollment should include retention metadata with 90 days")

    if FACE_ENROLLMENT_RECORD_RETENTION_DAYS != 90:
        raise SystemExit("retention constant should be 90 days")

    event = build_face_match_event(
        {
            "person_id": "sel",
            "room": "bedroom_spare",
            "camera": "cam_lounge_room_front",
            "face_match_confidence": 0.84,
            "event_id": "match-123",
            "track_id": "track-1",
            "ts": "2026-06-08T09:01:00Z",
        }
    )
    if event["source"] != "face":
        raise SystemExit("face match event should use face source")
    if event["entity_class"] != "human":
        raise SystemExit("face match event should use human entity class")
    if event["room"] != "bedroom_spare":
        raise SystemExit("face match event should preserve room")
    if event["person_id"] != "sel":
        raise SystemExit("face match event should preserve person_id")
    if event["confidence"] != 0.84:
        raise SystemExit("face match event should preserve confidence")
    if event["context"].get("with_face_match") is not True:
        raise SystemExit("face match event should indicate with_face_match context")

    try:
        build_face_match_event(
            {
                "person_id": "sel",
                "room": "bedroom_spare",
                "camera": "cam_lounge_room_front",
                "face_match_confidence": FACE_MATCH_THRESHOLD - 0.01,
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("below-threshold face match should be rejected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_face_enrollment_and_match.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Face enrollment and match check passed"
        if sys.argv[1] == "check"
        else "Face enrollment and match quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
