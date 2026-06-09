#!/usr/bin/env python3
"""Validate the ANPR service and event planning slice."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/anpr_service_and_event.yaml",
    ROOT / "docs/contracts/anpr-service-and-event.md",
    ROOT / "src/smart_home_presence_intelligence/anpr_service_and_event.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing anpr service and event files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/anpr_service_and_event.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "scope:",
        "behavior: canonicalization_only",
        "canonical_room_id: zone_alpha",
        "source: anpr",
        "entity_class: vehicle",
        "room_reference_required: true",
        "plate_transform: uppercase_strip_separators",
        "fallback_event_id_mode: opaque_sha256_digest",
        "fallback_event_id_format: anpr_event::sha256:{event_digest}",
        "fallback_event_id_exposes_plate: false",
    ):
        if needle not in text:
            raise SystemExit(f"anpr_service_and_event.yaml missing {needle}")

    doc_text = (ROOT / "docs/contracts/anpr-service-and-event.md").read_text(
        encoding="utf-8"
    )
    for needle in (
        "opaque SHA-256 digest derived from canonical event evidence",
        "fallback `event_id` must not embed the raw or canonicalized license plate",
        "event_id stays deterministic without exposing plate-derived content",
    ):
        if needle not in doc_text:
            raise SystemExit(
                f"anpr-service-and-event.md missing required privacy text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.anpr_service_and_event import (  # noqa: E501, WPS433
        ANPR_SOURCE,
        ANPR_ENTITY_CLASS,
        build_anpr_vehicle_event,
        normalize_anpr_direction,
    )

    event = build_anpr_vehicle_event(
        {
            "room_id": "zone_alpha",
            "plate": "ab c-12-34",
            "plate_confidence": 0.86,
            "camera": "frigate_zone_alpha",
            "direction": "enter",
            "vehicle_type": "car",
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if event["source"] != ANPR_SOURCE:
        raise SystemExit("event should use ANPR as source")
    if event["entity_class"] != ANPR_ENTITY_CLASS:
        raise SystemExit("event should use vehicle entity class")
    if event["room"] != "zone_alpha":
        raise SystemExit("event room should be zone_alpha")
    if event["type"] != "enter":
        raise SystemExit("arrive direction should map to enter")
    if event["vehicle"]["plate"] != "ABC1234":
        raise SystemExit("plate should be uppercase and separator free")
    if event["vehicle"]["vehicle_type"] != "car":
        raise SystemExit("vehicle type should be preserved when known")
    if event["camera"] != "frigate_zone_alpha":
        raise SystemExit("camera context should be preserved")
    fallback_event_id = event["event_id"]
    if re.fullmatch(r"anpr_event::sha256:[0-9a-f]{64}", fallback_event_id) is None:
        raise SystemExit(
            "fallback event_id should use the opaque anpr_event::sha256:<64 hex> format"
        )
    expected_fallback_event_id = "anpr_event::sha256:" + hashlib.sha256(
        json.dumps(
            {
                "camera": "frigate_zone_alpha",
                "direction": "arrival",
                "plate": "ABC1234",
                "plate_confidence": 0.86,
                "room": "zone_alpha",
                "ts": "2026-06-08T10:00:00+10:00",
                "type": "enter",
                "vehicle_type": "car",
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    if fallback_event_id != expected_fallback_event_id:
        raise SystemExit("fallback event_id should use a deterministic sha256 digest")
    if "ABC1234" in fallback_event_id or "ab c-12-34" in fallback_event_id.lower():
        raise SystemExit("fallback event_id should not expose plate content")
    if event["vehicle"]["plate_confidence"] != 0.86:
        raise SystemExit("plate confidence should be preserved")

    if normalize_anpr_direction("exit") != "departure":
        raise SystemExit("exit should normalize to departure")
    if normalize_anpr_direction(None) != "stationary":
        raise SystemExit("missing direction should normalize to stationary")

    explicit_id_event = build_anpr_vehicle_event(
        {
            "room_id": "zone_alpha",
            "plate": "XYZ123",
            "plate_confidence": 0.75,
            "camera": "frigate_zone_alpha",
            "event_id": "external-event-1",
        }
    )
    if re.fullmatch(r"anpr_event::sha256:[0-9a-f]{64}", explicit_id_event["event_id"]) is None:
        raise SystemExit("explicit upstream event_id should be normalized to an opaque id")
    if "external-event-1" in explicit_id_event["event_id"]:
        raise SystemExit("explicit upstream event_id should not leak through unchanged")

    non_zone_alpha_event = {
        "room_id": "room_delta",
        "plate": "XYZ123",
        "plate_confidence": 0.75,
        "camera": "internal_cam",
    }
    try:
        build_anpr_vehicle_event(non_zone_alpha_event)
    except ValueError:
        pass
    else:
        raise SystemExit("non-zone_alpha room should be rejected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_anpr_service_and_event.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "ANPR service and event check passed"
        if sys.argv[1] == "check"
        else "ANPR service and event quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
