"""Deterministic helpers for room-to-person assignment plans."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class IdentitySignal:
    """Normalized identity evidence for one candidate person."""

    person_id: str
    confidence: float


def _normalize_identity_signal(signal: Mapping[str, Any] | None) -> IdentitySignal | None:
    """Return a typed identity signal when the payload is complete enough to use."""

    if not signal:
        return None

    person_id = signal.get("person_id")
    confidence = signal.get("confidence")
    if not isinstance(person_id, str) or not person_id:
        return None
    if not isinstance(confidence, (int, float)):
        return None
    return IdentitySignal(person_id=person_id, confidence=float(confidence))


def _is_known_occupant(person_id: str, occupied_humans: object) -> bool:
    """Return True when the person is in the current occupied humans collection."""

    return person_id in occupied_humans


def _single_occupied_person(occupied_humans: object) -> str | None:
    """Return the only occupant when the collection contains exactly one person."""

    if isinstance(occupied_humans, (set, frozenset)):
        if len(occupied_humans) != 1:
            return None
        return sorted(occupied_humans)[0]
    if isinstance(occupied_humans, (list, tuple)):
        if len(occupied_humans) != 1:
            return None
        only_person = occupied_humans[0]
        return only_person if isinstance(only_person, str) else None
    return None


def assign_person_to_room(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Build a canonical room assignment plan from occupancy and identity hints."""

    room_id = snapshot["room_id"]
    occupied_humans = snapshot["occupied_humans"]
    face_signal = _normalize_identity_signal(snapshot.get("face_identity"))
    tracker_signal = _normalize_identity_signal(snapshot.get("tracker_identity"))

    assigned_person: str | None = None
    assignment_source = "none"
    confidence: float | None = None

    if (
        face_signal
        and tracker_signal
        and face_signal.person_id == tracker_signal.person_id
        and _is_known_occupant(face_signal.person_id, occupied_humans)
    ):
        assigned_person = face_signal.person_id
        assignment_source = "face+tracker"
        confidence = max(face_signal.confidence, tracker_signal.confidence)
    elif face_signal and _is_known_occupant(face_signal.person_id, occupied_humans):
        assigned_person = face_signal.person_id
        assignment_source = "face"
        confidence = face_signal.confidence
    elif tracker_signal and _is_known_occupant(tracker_signal.person_id, occupied_humans):
        assigned_person = tracker_signal.person_id
        assignment_source = "tracker"
        confidence = tracker_signal.confidence
    else:
        fallback_person = _single_occupied_person(occupied_humans)
        if fallback_person is not None:
            assigned_person = fallback_person
            assignment_source = "occupancy_fallback"
            confidence = 0.7

    return {
        "room_id": room_id,
        "occupied_humans": occupied_humans,
        "assigned_person": assigned_person,
        "assignment_source": assignment_source,
        "confidence": confidence,
    }
