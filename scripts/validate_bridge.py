#!/usr/bin/env python3
"""Validate the MQTT presence bridge slice."""

from __future__ import annotations

import sys
from pathlib import Path


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
        "hall: lounge_room",
        "living_room: lounge_room",
        "office: bedroom_spare",
        "master_bedroom: bedroom_master",
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

    normalized = normalize_presence_event(
        {"source": "mwave", "room": "master_bedroom", "event_id": "1"}
    )
    if normalized["source"] != "mmwave":
        raise SystemExit("source alias normalization failed")
    if normalized["room"] != "bedroom_master":
        raise SystemExit("room alias normalization failed")

    backyard = normalize_presence_event(
        {"source": "motion", "room": "backyard - shed", "event_id": "2"}
    )
    if backyard["room"] != "backyard_shed":
        raise SystemExit("backyard room normalization failed")

    errors = validate_presence_event(
        {
            "source": "frigate",
            "room": "lounge_room",
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
            "room": "lounge_room",
            "entity_class": "human",
            "confidence": 0.8,
            "ts": "2026-06-07T12:00:00+10:00",
        }
    )
    if routed["topic"] != CANONICAL_TOPIC:
        raise SystemExit("canonical routing failed")

    dlq = route_presence_event(
        {
            "source": "frigate",
            "room": "lounge_room",
            "type": "enter",
            "entity_class": "human",
            "confidence": 0.8,
            "ts": "2026-06-07T12:00:00+10:00",
        }
    )
    if dlq["topic"] != DEAD_LETTER_TOPIC:
        raise SystemExit("dead-letter routing failed")
    if not dlq["errors"]:
        raise SystemExit("dead-letter routing did not report errors")


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
