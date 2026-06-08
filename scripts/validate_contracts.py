#!/usr/bin/env python3
"""Validate the phase 0 contract bundle."""

from __future__ import annotations

from json import loads
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    ROOT / "config/inventory/rooms.yaml",
    ROOT / "config/inventory/room_capabilities.yaml",
    ROOT / "config/contracts/mqtt_topics.yaml",
    ROOT / "config/contracts/presence_bridge.yaml",
    ROOT / "config/contracts/room_fsm.yaml",
    ROOT / "config/contracts/dwell_reset.yaml",
    ROOT / "config/contracts/presence_event.schema.json",
    ROOT / "config/policies/retention.yaml",
    ROOT / "docs/contracts/phase0-foundation.md",
    ROOT / "docs/contracts/mqtt-presence-bridge.md",
    ROOT / "docs/contracts/room-fsm-template.md",
    ROOT / "docs/contracts/dwell-reset-automation.md",
]
REQUIRED_ROOMS = [
    "hall",
    "kitchen",
    "living_room",
    "office",
    "master_bedroom",
    "driveway",
]
REQUIRED_CAPABILITY_LINES = [
    "room_id: hall",
    "room_id: kitchen",
    "room_id: living_room",
    "room_id: office",
    "room_id: master_bedroom",
    "room_id: driveway",
    "supports_lighting: true",
    "supports_lighting: false",
    "supports_color: true",
    "supports_color: false",
]
REQUIRED_TOPICS = [
    "ha/presence/event",
    "ha/presence/event/dlq",
]
REQUIRED_BRIDGE_LINES = [
    "canonical_topic: ha/presence/event",
    "dead_letter_topic: ha/presence/event/dlq",
    "mwave: mmwave",
    "bedroom_master: master_bedroom",
]
REQUIRED_FSM_LINES = [
    "empty",
    "humans_only",
    "pets_only",
    "mixed",
    "sleeping",
    "bed_motion_only",
]
REQUIRED_DWELL_LINES = [
    "motion",
    "mmwave",
    "frigate",
    "restart_timer",
    "dim",
    "off",
]
REQUIRED_RETENTION_LINES = [
    "event_records: 90",
    "room_state_history: 90",
    "person_vehicle_links: 90",
    "face_plate_audit: 90",
    "media_metadata: 90",
    "foreign_plate_person_alerts: 90",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        print("Missing required contract files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_rooms() -> None:
    text = (ROOT / "config/inventory/rooms.yaml").read_text(encoding="utf-8")
    missing = [room for room in REQUIRED_ROOMS if f"room_id: {room}" not in text]
    if missing:
        print("Missing required room ids:")
        for room in missing:
            print(room)
        raise SystemExit(1)


def validate_capabilities() -> None:
    text = (ROOT / "config/inventory/room_capabilities.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_CAPABILITY_LINES if line not in text]
    if missing:
        print("Missing required room capability entries:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_topics() -> None:
    text = (ROOT / "config/contracts/mqtt_topics.yaml").read_text(encoding="utf-8")
    missing = [topic for topic in REQUIRED_TOPICS if topic not in text]
    if missing:
        print("Missing required MQTT topics:")
        for topic in missing:
            print(topic)
        raise SystemExit(1)


def validate_bridge_contract() -> None:
    text = (ROOT / "config/contracts/presence_bridge.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_BRIDGE_LINES if line not in text]
    if missing:
        print("Missing bridge contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_room_fsm_contract() -> None:
    text = (ROOT / "config/contracts/room_fsm.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_FSM_LINES if line not in text]
    if missing:
        print("Missing room FSM lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_dwell_contract() -> None:
    text = (ROOT / "config/contracts/dwell_reset.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_DWELL_LINES if line not in text]
    if missing:
        print("Missing dwell reset contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_schema() -> None:
    schema_path = ROOT / "config/contracts/presence_event.schema.json"
    schema = loads(schema_path.read_text(encoding="utf-8"))

    required_keys = {
        "event_id",
        "source",
        "type",
        "room",
        "entity_class",
        "confidence",
        "ts",
    }
    if set(schema.get("required", [])) != required_keys:
        raise SystemExit("presence_event.schema.json has unexpected required keys")

    properties = schema.get("properties", {})
    source_enum = properties.get("source", {}).get("enum", [])
    type_enum = properties.get("type", {}).get("enum", [])
    room_enum = properties.get("room", {}).get("enum", [])
    entity_class_enum = properties.get("entity_class", {}).get("enum", [])

    if source_enum != ["frigate", "mmwave", "motion", "face", "anpr", "tracker"]:
        raise SystemExit("presence_event.schema.json has unexpected source enum")
    if type_enum != ["enter", "leave", "stay", "state_change", "confidence"]:
        raise SystemExit("presence_event.schema.json has unexpected type enum")
    if entity_class_enum != ["human", "pet", "vehicle"]:
        raise SystemExit("presence_event.schema.json has unexpected entity_class enum")
    if room_enum != REQUIRED_ROOMS:
        raise SystemExit("presence_event.schema.json has unexpected room enum")

    if schema.get("additionalProperties") is not False:
        raise SystemExit("presence_event.schema.json must forbid additionalProperties")


def validate_retention() -> None:
    text = (ROOT / "config/policies/retention.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_RETENTION_LINES if line not in text]
    if missing:
        print("Missing retention requirements:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_contracts.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_rooms()
    validate_capabilities()
    validate_topics()
    validate_bridge_contract()
    validate_room_fsm_contract()
    validate_dwell_contract()
    validate_schema()
    validate_retention()

    print(
        "Phase 0 contract bundle check passed"
        if sys.argv[1] == "check"
        else "Phase 0 contract bundle quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
