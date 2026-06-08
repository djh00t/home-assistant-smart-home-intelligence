"""Deterministic pram walking-vs-driving transport classification."""

from __future__ import annotations

from typing import Any, Mapping


PRAM_WALKING_VS_DRIVING_SOURCE = "pram_walking_vs_driving"
WALKING_CLASSIFICATION = "walk"
DRIVING_CLASSIFICATION = "drive"
NOT_PRAM_CLASSIFICATION = "not_pram"
VEHICLE_CONTEXT_WINDOW_SECONDS = 90
DEFAULT_TS = "1970-01-01T00:00:00Z"


def _normalize_with_pram(snapshot: Mapping[str, Any]) -> bool:
    """Normalize and validate the with_pram flag."""

    with_pram = snapshot.get("with_pram")
    if not isinstance(with_pram, bool):
        raise ValueError("snapshot must include with_pram as boolean")
    return with_pram


def _normalize_room(snapshot: Mapping[str, Any]) -> str | None:
    """Normalize optional room context from a snapshot."""

    room = (
        snapshot.get("room_id")
        or snapshot.get("room")
        or snapshot.get("zone_id")
        or snapshot.get("zone")
    )
    if room is None:
        return None
    room_text = str(room).strip()
    if not room_text:
        raise ValueError("room context cannot be empty")
    return room_text


def _normalize_person_id(snapshot: Mapping[str, Any]) -> str | None:
    """Normalize optional person identity from a snapshot."""

    person_id = snapshot.get("person_id")
    if person_id is None:
        return None
    if not isinstance(person_id, str):
        raise ValueError("person_id must be a string when provided")
    person_id_text = person_id.strip()
    if not person_id_text:
        raise ValueError("person_id cannot be empty")
    return person_id_text


def _normalize_vehicle_context_age_seconds(
    snapshot: Mapping[str, Any],
) -> float | None:
    """Normalize optional vehicle context age from a snapshot."""

    raw_age = snapshot.get("vehicle_context_age_seconds")
    if raw_age is None:
        return None
    if not isinstance(raw_age, (int, float)):
        raise ValueError("vehicle_context_age_seconds must be numeric when provided")
    age_seconds = float(raw_age)
    if age_seconds < 0:
        raise ValueError("vehicle_context_age_seconds cannot be negative")
    return age_seconds


def _has_matching_vehicle_context_recently(
    vehicle_context_age_seconds: float | None,
) -> bool:
    """Return True when vehicle context exists inside the matching window."""

    return (
        vehicle_context_age_seconds is not None
        and vehicle_context_age_seconds <= VEHICLE_CONTEXT_WINDOW_SECONDS
    )


def classify_pram_transport(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Classify pram transport from snapshot recency context."""

    with_pram = _normalize_with_pram(snapshot)
    room = _normalize_room(snapshot)
    person_id = _normalize_person_id(snapshot)
    vehicle_context_age_seconds = _normalize_vehicle_context_age_seconds(snapshot)

    if with_pram and _has_matching_vehicle_context_recently(
        vehicle_context_age_seconds
    ):
        transport_mode = DRIVING_CLASSIFICATION
    elif with_pram:
        transport_mode = WALKING_CLASSIFICATION
    else:
        transport_mode = NOT_PRAM_CLASSIFICATION

    context = {
        "with_pram": with_pram,
        "vehicle_context_age_seconds": vehicle_context_age_seconds,
        "vehicle_context_window_seconds": VEHICLE_CONTEXT_WINDOW_SECONDS,
    }

    plan: dict[str, Any] = {
        "source": PRAM_WALKING_VS_DRIVING_SOURCE,
        "transport_mode": transport_mode,
        "context": context,
        "ts": str(snapshot.get("ts", DEFAULT_TS)),
    }
    if room is not None:
        plan["room"] = room
    if person_id is not None:
        plan["person_id"] = person_id
    return plan
