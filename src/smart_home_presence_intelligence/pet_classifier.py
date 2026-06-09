"""Pet detection classifier helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping
from uuid import uuid4

from .anpr_service_and_event import build_opaque_identifier


PET_LABELS = ("cat", "dog", "pet")
PET_EVENT_SOURCE = "frigate"
OPAQUE_EVENT_ID_RE = re.compile(r"^[a-z_]+::sha256:[0-9a-f]{64}$")


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

    fallback_event_id = build_opaque_identifier(
        "pet_event",
        {
            "nonce": uuid4().hex,
            "source": normalized.get("source", PET_EVENT_SOURCE),
            "ts": normalized.get("ts", "1970-01-01T00:00:00Z"),
        },
    )
    supplied_event_id = normalized.get("event_id")
    if isinstance(supplied_event_id, str) and OPAQUE_EVENT_ID_RE.fullmatch(
        supplied_event_id.strip()
    ):
        event_id = supplied_event_id.strip()
    else:
        event_id = fallback_event_id

    return {
        "event_id": event_id,
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
