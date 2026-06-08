"""Person tracker integration helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Any


TRACKER_SOURCES = ("mobile_app", "ble", "geofencing")
TRACKER_STATES = ("home", "not_home", "arriving", "leaving")


@dataclass(frozen=True, slots=True)
class TrackerSignal:
    """Minimal tracker input used by the integration template."""

    tracker_id: str
    person_id: str
    source: str
    state: str
    confidence: float


def normalize_tracker_signal(signal: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize a tracker signal into the canonical payload shape."""

    normalized = dict(signal)
    if normalized.get("source") not in TRACKER_SOURCES:
        raise ValueError(f"unsupported tracker source: {normalized.get('source')}")
    if normalized.get("state") not in TRACKER_STATES:
        raise ValueError(f"unsupported tracker state: {normalized.get('state')}")
    return normalized


def build_tracker_presence_event(signal: Mapping[str, Any]) -> dict[str, Any]:
    """Build a canonical presence event from a tracker signal."""

    normalized = normalize_tracker_signal(signal)
    return {
        "event_id": normalized.get("event_id", f"tracker::{normalized['tracker_id']}::{normalized['state']}"),
        "source": "tracker",
        "type": "state_change" if normalized["state"] in {"arriving", "leaving"} else "confidence",
        "room": normalized.get("room", "house"),
        "entity_class": "human",
        "person_id": normalized["person_id"],
        "confidence": normalized["confidence"],
        "track_id": normalized["tracker_id"],
        "context": {
            "tracker_state": normalized["state"],
            "tracker_source": normalized["source"],
        },
        "ts": normalized.get("ts", "1970-01-01T00:00:00Z"),
    }
