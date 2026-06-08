"""Pet detection classifier helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


PET_LABELS = ("cat", "dog", "pet")
PET_EVENT_SOURCE = "frigate"


@dataclass(frozen=True, slots=True)
class PetDetection:
    """Minimal pet detection input used by the classifier template."""

    room_id: str
    label: str
    confidence: float
    source: str = "frigate"
    ts: str = "1970-01-01T00:00:00Z"


def normalize_pet_detection(detection: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a raw pet detection into the classifier payload shape."""

    normalized = dict(detection)
    label = normalized.get("label") or normalized.get("pet_type") or normalized.get("class")
    if label not in PET_LABELS:
        raise ValueError(f"unsupported pet label: {label}")

    room = normalized.get("room") or normalized.get("room_id")
    if not room:
        raise ValueError("pet detection missing room context")

    confidence = normalized.get("confidence", normalized.get("score", 0.0))
    if not isinstance(confidence, (int, float)) or not 0.0 <= float(confidence) <= 1.0:
        raise ValueError(f"invalid pet confidence: {confidence}")

    return {
        "event_id": normalized.get("event_id", f"pet::{room}::{label}"),
        "label": label,
        "room": room,
        "confidence": float(confidence),
        "source": normalized.get("source", PET_EVENT_SOURCE),
        "ts": normalized.get("ts", "1970-01-01T00:00:00Z"),
    }


def build_pet_presence_event(detection: Mapping[str, Any]) -> dict[str, Any]:
    """Build a canonical pet presence event from a raw pet detection."""

    normalized = normalize_pet_detection(detection)
    return {
        "event_id": normalized["event_id"],
        "source": PET_EVENT_SOURCE,
        "type": "confidence",
        "room": normalized["room"],
        "entity_class": "pet",
        "confidence": normalized["confidence"],
        "ts": normalized["ts"],
    }
