"""Face enrollment and face-match canonicalization helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


FACE_SOURCE = "face"
FACE_ENTITY_CLASS = "human"
FACE_MATCH_TYPE = "confidence"
FACE_MATCH_THRESHOLD = 0.75
FACE_ENROLLMENT_RECORD_RETENTION_DAYS = 90
DEFAULT_TS = "1970-01-01T00:00:00Z"
DEFAULT_ENROLLMENT_ID_PREFIX = "face-enrollment"
DEFAULT_MATCH_EVENT_ID_PREFIX = "face-match"


@dataclass(frozen=True, slots=True)
class FaceMatchResult:
    """Normalized face match result used for event construction."""

    person_id: str
    room: str
    camera: str
    confidence: float


def _normalize_room(snapshot: Mapping[str, Any], *, require: bool = True) -> str:
    room = (
        snapshot.get("room")
        or snapshot.get("room_id")
        or snapshot.get("zone_id")
        or snapshot.get("zone")
    )
    if room is None:
        if require:
            raise ValueError("snapshot missing room context")
        return ""
    room_text = str(room).strip().lower()
    if not room_text:
        raise ValueError("snapshot room context cannot be empty")
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


def _normalize_source(snapshot: Mapping[str, Any]) -> str:
    source = snapshot.get("source")
    if not source:
        return FACE_SOURCE
    source_text = str(source).strip().lower()
    if source_text not in {"face", FACE_SOURCE}:
        raise ValueError(f"unsupported face source: {source_text}")
    return source_text


def _normalize_face_signature(snapshot: Mapping[str, Any]) -> str:
    face_signature = snapshot.get("face_signature")
    if not isinstance(face_signature, str):
        raise ValueError("snapshot missing or invalid face_signature")
    signature = face_signature.strip()
    if not signature:
        raise ValueError("face_signature cannot be empty")
    return signature


def _normalize_confidence(value: Any) -> float:
    if not isinstance(value, (int, float)):
        raise ValueError(f"face confidence must be numeric: {value!r}")
    confidence = float(value)
    if not 0.0 <= confidence <= 1.0:
        raise ValueError(f"face confidence must be between 0.0 and 1.0: {confidence!r}")
    return confidence


def _parse_timestamp(snapshot: Mapping[str, Any], field_name: str) -> str:
    timestamp = snapshot.get(field_name) or snapshot.get("ts")
    if timestamp is None:
        return DEFAULT_TS
    return str(timestamp)


def _to_event_id(prefix: str, room: str, person_id: str) -> str:
    return f"{prefix}::{room}::{person_id}"


def build_face_enrollment_record(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Build a deterministic face-enrollment record for local evidence retention."""

    person_id = _normalize_person_id(snapshot)
    room = _normalize_room(snapshot)
    camera = _normalize_camera(snapshot)
    _normalize_face_signature(snapshot)
    source = _normalize_source(snapshot)
    recorded_at = _parse_timestamp(snapshot, "recorded_at")
    face_signature = snapshot.get("face_signature")

    enrollment_id = str(
        snapshot.get("enrollment_id", _to_event_id(DEFAULT_ENROLLMENT_ID_PREFIX, room, person_id))
    )

    return {
        "enrollment_id": enrollment_id,
        "person_id": person_id,
        "room": room,
        "camera": camera,
        "source": source,
        "face_signature": str(face_signature),
        "recorded_at": recorded_at,
        "retention": {
            "days": FACE_ENROLLMENT_RECORD_RETENTION_DAYS,
            "record_type": "face_enrollment",
        },
    }


def build_face_match_event(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Build a canonical face-only match presence event."""

    room = _normalize_room(snapshot)
    person_id = _normalize_person_id(snapshot)
    camera = _normalize_camera(snapshot)
    source = _normalize_source(snapshot)
    confidence = _normalize_confidence(
        snapshot.get("face_match_confidence", snapshot.get("confidence"))
    )

    if confidence < FACE_MATCH_THRESHOLD:
        raise ValueError(
            f"face match below threshold {FACE_MATCH_THRESHOLD}: {confidence!r}"
        )

    normalized = FaceMatchResult(
        person_id=person_id,
        room=room,
        camera=camera,
        confidence=confidence,
    )

    return {
        "event_id": str(snapshot.get("event_id", _to_event_id(DEFAULT_MATCH_EVENT_ID_PREFIX, room, person_id))),
        "source": source,
        "type": FACE_MATCH_TYPE,
        "room": normalized.room,
        "entity_class": FACE_ENTITY_CLASS,
        "person_id": normalized.person_id,
        "confidence": normalized.confidence,
        "camera": normalized.camera,
        "context": {
            "with_face_match": True,
        },
        "ts": str(snapshot.get("ts", DEFAULT_TS)),
    }
