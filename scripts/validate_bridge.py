#!/usr/bin/env python3
"""Validate the MQTT presence bridge slice."""

from __future__ import annotations

import sys
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
BRIDGE_FILES = [
    ROOT / "config/contracts/presence_bridge.yaml",
    ROOT / "docs/contracts/mqtt-presence-bridge.md",
    ROOT / "src/smart_home_presence_intelligence/presence_bridge.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in BRIDGE_FILES if not path.exists()]
    if missing:
        print("Missing bridge files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/presence_bridge.yaml").read_text(encoding="utf-8")
    for needle in (
        "canonical_topic: ha/presence/event",
        "dead_letter_topic: ha/presence/event/dlq",
        "mwave: mmwave",
        "room_aliases: {}",
        "outbound_allowed_fields:",
        "dead_letter_payload_policy: contract_field_subset",
        "event_id_policy: opaque_or_rekeyed",
        "resident_ids: opaque_sha256_ref",
        "tracker_ids: opaque_sha256_ref",
        "license_plates: opaque_sha256_ref",
    ):
        if needle not in text:
            raise SystemExit(f"presence_bridge.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.presence_bridge import (  # noqa: WPS433
        CANONICAL_TOPIC,
        DEAD_LETTER_TOPIC,
        normalize_presence_event,
        route_presence_event,
        validate_presence_event,
    )

    normalized = normalize_presence_event({"source": "mwave", "room": "room alpha", "event_id": "1"})
    if normalized["source"] != "mmwave":
        raise SystemExit("source alias normalization failed")
    if normalized["room"] != "room_alpha":
        raise SystemExit("room alias normalization failed")

    backyard = normalize_presence_event({"source": "motion", "room": "zone - beta", "event_id": "2"})
    if backyard["room"] != "zone_beta":
        raise SystemExit("backyard room normalization failed")

    errors = validate_presence_event(
        {
            "source": "frigate",
            "room": "room_delta",
            "type": "enter",
            "entity_class": "human",
            "confidence": 0.8,
            "ts": "2026-06-07T12:00:00+10:00",
        }
    )
    if "missing required field: event_id" not in errors:
        raise SystemExit("missing-field validation failed")

    routed = route_presence_event(
        {
            "event_id": "evt-1",
            "source": "frigate",
            "type": "enter",
            "room": "room_delta",
            "camera": "front_drive",
            "entity_class": "human",
            "person_id": "resident.alex",
            "confidence": 0.8,
            "track_id": "trk-123",
            "context": {"with_face_match": True, "raw_face_embedding": "drop-me"},
            "vehicle": {"plate": "ABC123", "owner_phone": "drop-me"},
            "ts": "2026-06-07T12:00:00+10:00",
            "debug_trace": {"unexpected": True},
        }
    )
    if routed["topic"] != CANONICAL_TOPIC:
        raise SystemExit("canonical routing failed")
    if set(routed["event"]) != {
        "event_id",
        "source",
        "type",
        "room",
        "camera",
        "entity_class",
        "person_ref",
        "confidence",
        "tracker_ref",
        "vehicle",
        "context",
        "ts",
    }:
        raise SystemExit("canonical routing did not enforce the outbound allowlist")
    if "debug_trace" in routed["event"]:
        raise SystemExit("canonical routing leaked an unexpected field")
    if routed["event"].get("context") != {"with_face_match": True}:
        raise SystemExit("canonical routing leaked unexpected nested context fields")
    if re.fullmatch(r"resident::sha256:[0-9a-f]{64}", routed["event"].get("person_ref", "")) is None:
        raise SystemExit("canonical routing should expose an opaque person_ref")
    if re.fullmatch(r"tracker::sha256:[0-9a-f]{64}", routed["event"].get("tracker_ref", "")) is None:
        raise SystemExit("canonical routing should expose an opaque tracker_ref")
    if routed["event"].get("vehicle", {}).get("plate_ref") is None:
        raise SystemExit("canonical routing should expose a plate_ref")
    if re.fullmatch(
        r"plate::sha256:[0-9a-f]{64}",
        routed["event"]["vehicle"]["plate_ref"],
    ) is None:
        raise SystemExit("canonical routing should expose an opaque plate_ref")
    if re.fullmatch(r"presence_event::sha256:[0-9a-f]{64}", routed["event"].get("event_id", "")) is None:
        raise SystemExit("canonical routing should re-key non-opaque event_id values")
    if routed["event"].get("vehicle") != {
        "plate_ref": routed["event"]["vehicle"]["plate_ref"],
        "vehicle_type": routed["event"]["vehicle"].get("vehicle_type"),
    } and routed["event"].get("vehicle") != {
        "plate_ref": routed["event"]["vehicle"]["plate_ref"],
    }:
        raise SystemExit("canonical routing leaked unexpected nested vehicle fields")
    if "resident.alex" in str(routed["event"]) or "trk-123" in str(routed["event"]) or "ABC123" in str(routed["event"]):
        raise SystemExit("canonical routing leaked raw identifiers")

    dlq = route_presence_event(
        {
            "source": "frigate",
            "room": "room_delta",
            "type": "enter",
            "entity_class": "human",
            "confidence": 0.8,
            "ts": "2026-06-07T12:00:00+10:00",
            "person_id": "resident.sam",
            "track_id": "trk-999",
            "raw_payload": {
                "event_id": "upstream-1",
                "camera": "front_drive",
                "sensitive_note": "keep out of dead letter payloads",
            },
            "context": {"lighting_blocked": True, "owner_phone": "keep-out"},
            "vehicle": {"plate": "XYZ123", "owner_phone": "keep-out"},
        }
    )
    if dlq["topic"] != DEAD_LETTER_TOPIC:
        raise SystemExit("dead-letter routing failed")
    if not dlq["errors"]:
        raise SystemExit("dead-letter routing did not report errors")
    if "raw_payload" in dlq["payload"]:
        raise SystemExit("dead-letter routing leaked the raw payload")
    if dlq["payload"].get("context") != {"lighting_blocked": True}:
        raise SystemExit("dead-letter routing leaked unexpected nested context fields")
    if re.fullmatch(r"resident::sha256:[0-9a-f]{64}", dlq["payload"].get("person_ref", "")) is None:
        raise SystemExit("dead-letter payload should expose an opaque person_ref")
    if re.fullmatch(r"tracker::sha256:[0-9a-f]{64}", dlq["payload"].get("tracker_ref", "")) is None:
        raise SystemExit("dead-letter payload should expose an opaque tracker_ref")
    if dlq["payload"].get("vehicle", {}).get("plate_ref") is None:
        raise SystemExit("dead-letter payload should expose a plate_ref")
    if re.fullmatch(
        r"plate::sha256:[0-9a-f]{64}",
        dlq["payload"]["vehicle"]["plate_ref"],
    ) is None:
        raise SystemExit("dead-letter payload should expose an opaque plate_ref")
    if "resident.sam" in str(dlq["payload"]) or "trk-999" in str(dlq["payload"]) or "XYZ123" in str(dlq["payload"]):
        raise SystemExit("dead-letter routing leaked raw identifiers")
    if dlq["payload"].get("event_id") is not None:
        raise SystemExit("dead-letter payload should omit event_id when the source payload did not supply one")

    toxic_event_id = route_presence_event(
        {
            "event_id": "resident.sam|trk-999|XYZ123",
            "source": "frigate",
            "type": "enter",
            "room": "room_delta",
            "entity_class": "human",
            "confidence": 0.8,
            "ts": "2026-06-07T12:00:00+10:00",
        }
    )
    if re.fullmatch(
        r"presence_event::sha256:[0-9a-f]{64}",
        toxic_event_id["event"].get("event_id", ""),
    ) is None:
        raise SystemExit("bridge should re-key raw caller-supplied event_id values")
    if "resident.sam" in toxic_event_id["event"]["event_id"] or "trk-999" in toxic_event_id["event"]["event_id"]:
        raise SystemExit("bridge event_id re-keying should remove raw identifiers")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_bridge.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "MQTT presence bridge check passed"
        if sys.argv[1] == "check"
        else "MQTT presence bridge quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
