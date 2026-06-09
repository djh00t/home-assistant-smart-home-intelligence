"""Normalize raw presence events into the canonical MQTT contract."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
import re
from typing import Any, Mapping


CANONICAL_TOPIC = "ha/presence/event"
DEAD_LETTER_TOPIC = "ha/presence/event/dlq"
SOURCE_ALIASES = {"mwave": "mmwave"}
ROOM_ALIASES: dict[str, str] = {}
REQUIRED_FIELDS = (
    "event_id",
    "source",
    "type",
    "room",
    "entity_class",
    "confidence",
    "ts",
)
ALLOWED_EVENT_FIELDS = (
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
)
ALLOWED_VEHICLE_FIELDS = (
    "plate_ref",
    "plate_confidence",
    "vehicle_type",
)
ALLOWED_CONTEXT_FIELDS = (
    "with_pram",
    "with_face_match",
    "is_owner_plate",
    "lighting_blocked",
)
VALID_SOURCES = ("frigate", "mmwave", "motion", "face", "anpr", "tracker")
VALID_ROOMS = (
    "room_alpha",
    "room_beta",
    "room_gamma",
    "room_delta",
    "room_zeta",
    "zone_alpha",
    "zone_beta",
    "zone_gamma",
    "room_epsilon",
)
OPAQUE_REF_RE = re.compile(r"^[a-z_]+::sha256:[0-9a-f]{64}$")
OPAQUE_EVENT_ID_RE = re.compile(r"^[a-z_]+::sha256:[0-9a-f]{64}$")


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

    normalized = _filter_allowed_event_fields(event)
    if "source" in normalized:
        normalized["source"] = normalize_source(str(normalized["source"]))
    if "room" in normalized:
        normalized["room"] = normalize_room(str(normalized["room"]))
    return normalized


def _build_opaque_identifier(prefix: str, value: str) -> str:
    canonical_payload = json.dumps({"value": value}, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(canonical_payload.encode("utf-8")).hexdigest()
    return f"{prefix}::sha256:{digest}"


def _normalize_person_ref(value: Any) -> str | None:
    return _normalize_opaque_ref("resident", value, allow_unknown=True)


def _normalize_tracker_ref(value: Any) -> str | None:
    return _normalize_opaque_ref("tracker", value)


def _normalize_plate_ref(value: Any) -> str | None:
    return _normalize_opaque_ref("plate", value)


def _normalize_event_id(value: Any) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None
    if OPAQUE_EVENT_ID_RE.fullmatch(normalized):
        return normalized
    return _build_opaque_identifier("presence_event", normalized)


def _normalize_opaque_ref(
    prefix: str,
    value: Any,
    *,
    allow_unknown: bool = False,
) -> str | None:
    if value is None:
        return None

    normalized = str(value).strip()
    if not normalized:
        return None
    if allow_unknown and normalized == "unknown":
        return normalized
    if OPAQUE_REF_RE.fullmatch(normalized):
        return normalized
    return _build_opaque_identifier(prefix, normalized)


def _filter_allowed_event_fields(event: Mapping[str, Any]) -> dict[str, Any]:
    """Project an event down to the documented outbound contract fields."""

    filtered: dict[str, Any] = {}
    person_ref = _normalize_person_ref(event.get("person_ref", event.get("person_id")))
    tracker_ref = _normalize_tracker_ref(event.get("tracker_ref", event.get("track_id")))
    for field in ALLOWED_EVENT_FIELDS:
        if field == "event_id":
            event_id = _normalize_event_id(event.get("event_id"))
            if event_id is not None:
                filtered[field] = event_id
            continue
        if field == "person_ref":
            if person_ref is not None:
                filtered[field] = person_ref
            continue
        if field == "tracker_ref":
            if tracker_ref is not None:
                filtered[field] = tracker_ref
            continue
        if field == "vehicle":
            vehicle = event.get(field)
            if isinstance(vehicle, Mapping):
                normalized_vehicle: dict[str, Any] = {}
                plate_ref = _normalize_plate_ref(vehicle.get("plate_ref", vehicle.get("plate")))
                if plate_ref is not None:
                    normalized_vehicle["plate_ref"] = plate_ref
                for key in ALLOWED_VEHICLE_FIELDS:
                    if key == "plate_ref" or key not in vehicle:
                        continue
                    normalized_vehicle[key] = deepcopy(vehicle[key])
                if normalized_vehicle:
                    filtered[field] = normalized_vehicle
            continue
        if field not in event:
            continue
        if field == "context":
            context = event[field]
            if isinstance(context, Mapping):
                filtered[field] = {
                    key: deepcopy(context[key])
                    for key in ALLOWED_CONTEXT_FIELDS
                    if key in context
                }
            continue
        filtered[field] = deepcopy(event[field])
    return filtered


def route_presence_event(event: Mapping[str, Any]) -> dict[str, Any]:
    """Route a raw event to the canonical topic or the dead-letter topic."""

    errors = validate_presence_event(event)
    if errors:
        return {
            "topic": DEAD_LETTER_TOPIC,
            "errors": errors,
            "payload": _filter_allowed_event_fields(event),
        }

    return {
        "topic": CANONICAL_TOPIC,
        "event": normalize_presence_event(event),
    }
