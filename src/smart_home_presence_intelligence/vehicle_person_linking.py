"""Deterministic arrival-zone vehicle-person linking helpers."""

from __future__ import annotations

import hashlib
from typing import Any, Mapping

from .anpr_service_and_event import (
    normalize_anpr_direction,
    normalize_anpr_plate,
    normalize_plate_confidence,
)
from .driveway_zone_setup import validate_driveway_reference


LINKING_SOURCE = "vehicle_person_linking"
LINKING_ENTITY_CLASS = "vehicle"
DEFAULT_TS = "1970-01-01T00:00:00Z"
FALLBACK_EVENT_ID_PREFIX = "vehicle_link"
FALLBACK_EVENT_ID_DIGEST_LENGTH = 20
VEHICLE_ARRIVAL_EVENT = "vehicle_arrival"
VEHICLE_DEPARTURE_EVENT = "vehicle_departure"
PLATE_CONFIDENCE_THRESHOLD = 0.8
FACE_MATCH_CONFIDENCE_THRESHOLD = 0.75
LINK_EVENT_TYPES = {
    "arrival": VEHICLE_ARRIVAL_EVENT,
    "departure": VEHICLE_DEPARTURE_EVENT,
}


def _normalize_room(snapshot: Mapping[str, Any]) -> str:
    room = snapshot.get("room_id") or snapshot.get("room") or snapshot.get("zone_id")
    if room is None:
        raise ValueError("snapshot missing room context")
    room_text = str(room).strip().lower()
    if not room_text:
        raise ValueError("room context cannot be empty")
    if not validate_driveway_reference(snapshot):
        raise ValueError(f"non-zone_alpha linking payload rejected: {room_text}")
    return room_text


def _normalize_person_id(snapshot: Mapping[str, Any]) -> str:
    person_id = snapshot.get("person_id")
    if not isinstance(person_id, str):
        raise ValueError("snapshot missing or invalid person_id")
    person_id_text = person_id.strip()
    if not person_id_text:
        raise ValueError("person_id cannot be empty")
    return person_id_text


def _normalize_camera(snapshot: Mapping[str, Any]) -> str:
    camera = snapshot.get("camera")
    if not isinstance(camera, str):
        raise ValueError("snapshot missing or invalid camera")
    camera_text = camera.strip()
    if not camera_text:
        raise ValueError("camera cannot be empty")
    return camera_text


def _normalize_face_match_confidence(snapshot: Mapping[str, Any]) -> float:
    confidence = snapshot.get("face_match_confidence")
    if not isinstance(confidence, (int, float)):
        raise ValueError("face_match_confidence must be a number")
    confidence_value = float(confidence)
    if not 0.0 <= confidence_value <= 1.0:
        raise ValueError(
            f"face_match_confidence must be between 0.0 and 1.0: {confidence_value!r}"
        )
    return confidence_value


def _to_event_id(
    room: str,
    person_id: str,
    plate: str,
    camera: str,
    event_type: str,
    ts: str,
    plate_confidence: float,
    face_match_confidence: float,
) -> str:
    digest_input = "\x1f".join(
        (
            room,
            person_id,
            plate,
            camera,
            event_type,
            ts,
            f"{plate_confidence:.6f}",
            f"{face_match_confidence:.6f}",
        )
    )
    digest = hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[
        :FALLBACK_EVENT_ID_DIGEST_LENGTH
    ]
    return f"{FALLBACK_EVENT_ID_PREFIX}::{digest}"


def _link_direction_event_type(direction: str) -> str:
    event_type = LINK_EVENT_TYPES.get(direction)
    if event_type is None:
        raise ValueError(
            f"non-arrival/departure snapshot direction rejected: {direction}"
        )
    return event_type


def build_vehicle_person_linked_event(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Build a canonical linked vehicle-person planning event from zone_alpha evidence."""

    room = _normalize_room(snapshot)
    person_id = _normalize_person_id(snapshot)
    camera = _normalize_camera(snapshot)
    plate = normalize_anpr_plate(
        snapshot.get("plate", snapshot.get("plate_text"))
    )
    plate_confidence = normalize_plate_confidence(
        snapshot.get("plate_confidence")
    )
    face_match_confidence = _normalize_face_match_confidence(snapshot)

    if plate_confidence < PLATE_CONFIDENCE_THRESHOLD:
        raise ValueError(
            f"plate_confidence below threshold {PLATE_CONFIDENCE_THRESHOLD}: {plate_confidence!r}"
        )
    if face_match_confidence < FACE_MATCH_CONFIDENCE_THRESHOLD:
        raise ValueError(
            f"face_match_confidence below threshold {FACE_MATCH_CONFIDENCE_THRESHOLD}: {face_match_confidence!r}"
        )

    direction = normalize_anpr_direction(snapshot.get("direction"))
    event_type = _link_direction_event_type(direction)
    linked_confidence = min(plate_confidence, face_match_confidence)
    ts = str(snapshot.get("ts", DEFAULT_TS))
    event_id = str(
        snapshot.get(
            "event_id",
            _to_event_id(
                room,
                person_id,
                plate,
                camera,
                event_type,
                ts,
                plate_confidence,
                face_match_confidence,
            ),
        )
    )

    return {
        "event_id": event_id,
        "source": LINKING_SOURCE,
        "type": event_type,
        "room": room,
        "person_id": person_id,
        "entity_class": LINKING_ENTITY_CLASS,
        "confidence": linked_confidence,
        "camera": camera,
        "vehicle": {
            "plate": plate,
            "plate_confidence": plate_confidence,
            "face_match_confidence": face_match_confidence,
        },
        "ts": ts,
    }
