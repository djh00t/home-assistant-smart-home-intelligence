"""Canonical ANPR driveway vehicle service helpers."""

from __future__ import annotations

import re
from typing import Any, Mapping

from .driveway_zone_setup import (
    DRIVEWAY_ZONE_ID,
    normalize_driveway_direction,
    validate_driveway_reference,
)


ANPR_SOURCE = "anpr"
ANPR_ENTITY_CLASS = "vehicle"
UNKNOWN_VEHICLE_TYPE = "unknown"
DEFAULT_TS = "1970-01-01T00:00:00Z"
DEFAULT_EVENT_TYPE = "stay"
EVENT_TYPE_BY_DIRECTION = {
    "arrival": "enter",
    "departure": "leave",
    "stationary": DEFAULT_EVENT_TYPE,
}

ALLOWED_VEHICLE_TYPES = {"car", "truck", "motorcycle"}


def normalize_anpr_plate(plate: Any) -> str:
    """Return an uppercase plate value with separators removed."""

    if not isinstance(plate, str):
        raise ValueError("plate must be a string")

    normalized = re.sub(r"[^0-9A-Za-z]", "", plate.upper())
    if not normalized:
        raise ValueError("plate must contain at least one alphanumeric character")
    return normalized


def normalize_plate_confidence(confidence: Any) -> float:
    """Normalize and validate a plate confidence score."""

    if not isinstance(confidence, (int, float)):
        raise ValueError(f"plate_confidence must be a number: {confidence!r}")

    normalized = float(confidence)
    if not 0.0 <= normalized <= 1.0:
        raise ValueError(f"plate_confidence must be between 0 and 1: {confidence!r}")
    return normalized


def normalize_vehicle_type(vehicle_type: Any) -> str:
    """Normalize optional vehicle type into canonical enum vocabulary."""

    if not vehicle_type:
        return UNKNOWN_VEHICLE_TYPE

    normalized = str(vehicle_type).strip().lower()
    if normalized in ALLOWED_VEHICLE_TYPES:
        return normalized
    return UNKNOWN_VEHICLE_TYPE


def normalize_anpr_direction(direction: Any) -> str:
    """Normalize driveway direction using driveway setup rules."""

    if direction is None:
        return "stationary"
    return normalize_driveway_direction(str(direction))


def _extract_room(snapshot: Mapping[str, Any]) -> str:
    room = snapshot.get("room_id") or snapshot.get("room") or snapshot.get("zone_id")
    if room is None:
        raise ValueError("snapshot missing room id")
    return str(room).strip().lower()


def build_anpr_vehicle_event(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Build a canonical driveway vehicle event from an ANPR snapshot."""

    room = _extract_room(snapshot)
    if room != DRIVEWAY_ZONE_ID:
        if not validate_driveway_reference(snapshot):
            raise ValueError(f"non-driveway ANPR payload rejected: {room}")

    plate = normalize_anpr_plate(snapshot.get("plate", snapshot.get("plate_text")))
    plate_confidence = normalize_plate_confidence(
        snapshot.get("plate_confidence", snapshot.get("plate_confidence_score", 0.0))
    )
    camera = snapshot.get("camera")
    if not camera:
        raise ValueError("snapshot missing camera")

    direction = normalize_anpr_direction(snapshot.get("direction"))
    vehicle_type = normalize_vehicle_type(snapshot.get("vehicle_type"))

    return {
        "event_id": str(snapshot.get("event_id", f"anpr::{room}::{plate}")),
        "source": ANPR_SOURCE,
        "type": EVENT_TYPE_BY_DIRECTION.get(direction, DEFAULT_EVENT_TYPE),
        "room": room,
        "entity_class": ANPR_ENTITY_CLASS,
        "confidence": plate_confidence,
        "camera": str(camera),
        "vehicle": {
            "plate": plate,
            "plate_confidence": plate_confidence,
            "vehicle_type": vehicle_type,
        },
        "ts": str(snapshot.get("ts", DEFAULT_TS)),
    }
