"""Person tracker integration helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Mapping, Any

from .anpr_service_and_event import build_opaque_identifier


TRACKER_SOURCES = ("mobile_app", "ble", "geofencing")
TRACKER_STATES = ("home", "not_home", "arriving", "leaving")
OPAQUE_EVENT_ID_RE = re.compile(r"^[a-z_]+::sha256:[0-9a-f]{64}$")


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
    event_type = "state_change" if normalized["state"] in {"arriving", "leaving"} else "confidence"
    ts = normalized.get("ts", "1970-01-01T00:00:00Z")
    fallback_event_id = build_opaque_identifier(
        "tracker_event",
        {
            "tracker_id": normalized["tracker_id"],
            "state": normalized["state"],
            "source": normalized["source"],
            "person_id": normalized["person_id"],
            "ts": ts,
        },
    )
    supplied_event_id = normalized.get("event_id")
    if isinstance(supplied_event_id, str) and OPAQUE_EVENT_ID_RE.fullmatch(
        supplied_event_id.strip()
    ):
        event_id = supplied_event_id.strip()
    else:
        event_id = fallback_event_id
    person_ref = (
        normalized["person_id"]
        if normalized["person_id"] == "unknown"
        else build_opaque_identifier("resident", {"value": normalized["person_id"]})
    )
    tracker_ref = build_opaque_identifier("tracker", {"value": normalized["tracker_id"]})
    return {
        "event_id": event_id,
        "source": "tracker",
        "type": event_type,
        "room": normalized.get("room", "house"),
        "entity_class": "human",
        "person_ref": person_ref,
        "confidence": normalized["confidence"],
        "tracker_ref": tracker_ref,
        "context": {
            "tracker_state": normalized["state"],
            "tracker_source": normalized["source"],
        },
        "ts": ts,
    }
