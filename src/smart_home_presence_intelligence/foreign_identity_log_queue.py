"""Planning-only foreign identity queue helpers."""

from __future__ import annotations

from typing import Any, Mapping

from .anpr_service_and_event import build_opaque_identifier, normalize_anpr_plate


FOREIGN_IDENTITY_LOG_QUEUE_SOURCE = "foreign_identity_log_queue"
FOREIGN_IDENTITY_QUEUE_RECORD_TYPE = "foreign_identity_alert"
FOREIGN_IDENTITY_QUEUE_RECORD_NAME = "foreign_identity_log"
FOREIGN_IDENTITY_QUEUE_REVIEW_STATUS = "queued"
FOREIGN_IDENTITY_QUEUE_RETENTION_DAYS = 90
FACE_MATCH_UNKNOWN_THRESHOLD = 0.75
IDENTITY_UNKNOWN_VALUES = {"unknown", "foreign", "unresolved"}
DEFAULT_TS = "1970-01-01T00:00:00Z"


def _normalize_room(snapshot: Mapping[str, Any]) -> str:
    room = snapshot.get("room_id") or snapshot.get("room") or snapshot.get("zone_id")
    if room is None:
        raise ValueError("snapshot missing room_id")
    room_text = str(room).strip().lower()
    if not room_text:
        raise ValueError("room_id cannot be empty")
    return room_text


def _normalize_camera(snapshot: Mapping[str, Any]) -> str:
    camera = snapshot.get("camera")
    if not isinstance(camera, str):
        raise ValueError("snapshot missing or invalid camera")
    camera_text = camera.strip()
    if not camera_text:
        raise ValueError("camera cannot be empty")
    return camera_text


def _normalize_plate(snapshot: Mapping[str, Any]) -> str | None:
    plate = snapshot.get("plate")
    if plate is None:
        return None
    if not isinstance(plate, str):
        raise ValueError("plate must be a string when provided")
    return normalize_anpr_plate(plate)


def _normalize_person_id(snapshot: Mapping[str, Any]) -> str | None:
    person_id = snapshot.get("person_id")
    if person_id is None:
        return None
    if not isinstance(person_id, str):
        raise ValueError("person_id must be a string when provided")
    person_text = person_id.strip()
    if not person_text:
        return None
    return person_text


def _normalize_identity_status(snapshot: Mapping[str, Any]) -> str | None:
    status = snapshot.get("identity_status")
    if status is None:
        return None
    if not isinstance(status, str):
        raise ValueError("identity_status must be a string when provided")
    normalized = status.strip().lower()
    if not normalized:
        return None
    if normalized not in {"foreign", "unknown", "known"}:
        raise ValueError(f"invalid identity_status: {status!r}")
    return normalized


def _normalize_face_match_confidence(snapshot: Mapping[str, Any]) -> float | None:
    confidence = snapshot.get("face_match_confidence")
    if confidence is None:
        return None
    if not isinstance(confidence, (int, float)):
        raise ValueError("face_match_confidence must be a number when provided")
    confidence_value = float(confidence)
    if not 0.0 <= confidence_value <= 1.0:
        raise ValueError(
            f"face_match_confidence must be between 0.0 and 1.0: {confidence_value!r}"
        )
    return confidence_value


def _has_identity_inputs(snapshot: Mapping[str, Any]) -> bool:
    return any(
        key in snapshot
        for key in ("plate", "face_match_confidence", "person_id", "identity_status")
    )


def _is_unknown_or_foreign_identity(snapshot: Mapping[str, Any]) -> bool:
    person_id = _normalize_person_id(snapshot)
    face_match_confidence = _normalize_face_match_confidence(snapshot)
    status = _normalize_identity_status(snapshot)

    if status in {"foreign", "unknown"}:
        return True

    if person_id is None:
        return True

    if person_id.strip().lower() in IDENTITY_UNKNOWN_VALUES:
        return True

    if status == "known":
        return False

    if (
        face_match_confidence is not None
        and face_match_confidence < FACE_MATCH_UNKNOWN_THRESHOLD
    ):
        return True

    return False


def _queue_record_id(room: str, camera: str, evidence: dict[str, Any]) -> str:
    return build_opaque_identifier(
        f"{FOREIGN_IDENTITY_LOG_QUEUE_SOURCE}::{room}::{camera}",
        evidence,
    )


def build_foreign_identity_queue_record(
    snapshot: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Build immutable foreign-identity queue record when unknown identity is detected."""

    if not _has_identity_inputs(snapshot):
        raise ValueError(
            "snapshot must include plate, face_match_confidence, person_id, or identity_status"
        )

    room = _normalize_room(snapshot)
    camera = _normalize_camera(snapshot)
    plate = _normalize_plate(snapshot)
    person_id = _normalize_person_id(snapshot)
    face_match_confidence = _normalize_face_match_confidence(snapshot)
    identity_status = _normalize_identity_status(snapshot)

    if not _is_unknown_or_foreign_identity(snapshot):
        return None

    identity = {}
    if plate is not None:
        identity["plate_present"] = True
    if person_id is not None:
        identity["person_present"] = True
    if face_match_confidence is not None:
        identity["face_match_confidence"] = face_match_confidence
    if identity_status is not None:
        identity["identity_status"] = identity_status

    return {
        "queue_id": _queue_record_id(room, camera, identity),
        "source": FOREIGN_IDENTITY_LOG_QUEUE_SOURCE,
        "queue_record_type": FOREIGN_IDENTITY_QUEUE_RECORD_TYPE,
        "record_name": FOREIGN_IDENTITY_QUEUE_RECORD_NAME,
        "review_status": FOREIGN_IDENTITY_QUEUE_REVIEW_STATUS,
        "room": room,
        "camera": camera,
        "identity": identity,
        "immutable": True,
        "retention": {
            "days": FOREIGN_IDENTITY_QUEUE_RETENTION_DAYS,
            "immutable": True,
        },
        "ts": str(snapshot.get("ts", DEFAULT_TS)),
    }
