"""Normalize raw presence events into the canonical MQTT contract."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping


CANONICAL_TOPIC = "ha/presence/event"
DEAD_LETTER_TOPIC = "ha/presence/event/dlq"
SOURCE_ALIASES = {"mwave": "mmwave"}
ROOM_ALIASES = {
    "hall": "lounge_room",
    "living_room": "lounge_room",
    "office": "bedroom_spare",
    "master_bedroom": "bedroom_master",
}
REQUIRED_FIELDS = (
    "event_id",
    "source",
    "type",
    "room",
    "entity_class",
    "confidence",
    "ts",
)
VALID_SOURCES = ("frigate", "mmwave", "motion", "face", "anpr", "tracker")
VALID_ROOMS = (
    "bedroom_master",
    "bedroom_max",
    "bedroom_spare",
    "lounge_room",
    "garage",
    "driveway",
    "backyard_shed",
    "backyard_deck",
    "kitchen",
)


def normalize_source(source: str) -> str:
    """Return the canonical source token for a raw upstream source."""

    return SOURCE_ALIASES.get(source, source)


def normalize_room(room: str) -> str:
    """Return the canonical room token for a raw upstream room value."""

    normalized = room.strip().lower().replace(" - ", "_").replace("-", "_").replace(" ", "_")
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return ROOM_ALIASES.get(normalized, normalized)


def validate_presence_event(event: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a raw presence event payload."""

    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        value = event.get(field)
        if value is None or value == "":
            errors.append(f"missing required field: {field}")

    source = normalize_source(str(event.get("source", "")))
    room = normalize_room(str(event.get("room", "")))
    if source not in VALID_SOURCES:
        errors.append(f"unsupported source: {event.get('source')}")
    if room not in VALID_ROOMS:
        errors.append(f"unsupported room: {event.get('room')}")

    return errors


def normalize_presence_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize raw event aliases into the canonical bridge payload."""

    normalized = deepcopy(dict(event))
    if "source" in normalized:
        normalized["source"] = normalize_source(str(normalized["source"]))
    if "room" in normalized:
        normalized["room"] = normalize_room(str(normalized["room"]))
    return normalized


def route_presence_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Route a raw event to the canonical topic or the dead-letter topic."""

    errors = validate_presence_event(event)
    if errors:
        return {
            "topic": DEAD_LETTER_TOPIC,
            "errors": errors,
            "payload": deepcopy(dict(event)),
        }

    return {
        "topic": CANONICAL_TOPIC,
        "event": normalize_presence_event(event),
    }

