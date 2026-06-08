"""Planning-only anomaly and false-action dashboard helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping
import json

import yaml


ANOMALY_DASHBOARD_SOURCE = "anomaly_and_false_action_dashboard"
ANOMALY_DASHBOARD_RECORD_TYPE = "anomaly_false_action_dashboard"
ANOMALY_DASHBOARD_RECORD_NAME = "anomaly_and_false_action_dashboard"
ANOMALY_DASHBOARD_STATUS = "ready"
ANOMALY_DASHBOARD_RETENTION_DAYS = 90
DEFAULT_TS = "1970-01-01T00:00:00Z"
VALID_KINDS = {"anomaly", "false_action"}
VALID_SEVERITIES = {"low": 1, "medium": 2, "high": 3, "critical": 4}

ROOM_INVENTORY_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "inventory" / "rooms.yaml"
)


def _read_room_inventory(path: Path | None = None) -> dict[str, Any]:
    """Read and normalize the room inventory payload."""

    inventory_path = path or ROOM_INVENTORY_PATH
    with inventory_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("room inventory contract must be a mapping")
    return payload


def _load_canonical_room_order(path: Path | None = None) -> list[str]:
    payload = _read_room_inventory(path)
    ordered_rooms: list[str] = []

    for section in ("rooms", "external_zones"):
        entries = payload.get(section, [])
        if not isinstance(entries, list):
            raise ValueError(f"room inventory must define {section} as a list")
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            room_id = entry.get("room_id")
            if not isinstance(room_id, str):
                continue
            normalized_room = room_id.strip().lower()
            if normalized_room:
                ordered_rooms.append(normalized_room)

    if not ordered_rooms:
        raise ValueError("room inventory has no canonical rooms configured")
    return ordered_rooms


def _normalize_room(incident: Mapping[str, Any]) -> str:
    room = incident.get("room_id") or incident.get("room") or incident.get("zone_id")
    if room is None:
        raise ValueError("incident missing room_id/room/zone_id")
    room_text = str(room).strip().lower()
    if not room_text:
        raise ValueError("incident room_id/room/zone_id cannot be empty")
    return room_text


def _normalize_kind(incident: Mapping[str, Any]) -> str:
    kind = incident.get("kind")
    if not isinstance(kind, str):
        raise ValueError("incident missing or invalid kind")
    kind_text = kind.strip().lower()
    if kind_text not in VALID_KINDS:
        raise ValueError(f"invalid incident kind: {kind!r}")
    return kind_text


def _normalize_severity(incident: Mapping[str, Any]) -> str:
    severity = incident.get("severity")
    if not isinstance(severity, str):
        raise ValueError("incident missing or invalid severity")
    severity_text = severity.strip().lower()
    if severity_text not in VALID_SEVERITIES:
        raise ValueError(f"invalid incident severity: {severity!r}")
    return severity_text


def _normalize_category(incident: Mapping[str, Any]) -> str | None:
    category = incident.get("category")
    if category is None:
        return None
    if not isinstance(category, str):
        raise ValueError("category must be a string when provided")
    category_text = category.strip()
    if not category_text:
        return None
    return category_text


def _normalize_ts(incident: Mapping[str, Any]) -> str:
    return str(incident.get("ts", DEFAULT_TS))


def _severity_rank(severity: str) -> int:
    return VALID_SEVERITIES[severity]


def _severity_name(rank: int) -> str:
    for severity, severity_rank in VALID_SEVERITIES.items():
        if severity_rank == rank:
            return severity
    return "low"


def _dashboard_id(cards: list[dict[str, Any]], focus_room_id: str | None = None) -> str:
    payload = {
        "focus_room_id": focus_room_id,
        "room_cards": cards,
    }
    fragment = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"{ANOMALY_DASHBOARD_SOURCE}::{fragment}"


def _build_room_cards(
    incidents: Iterable[Mapping[str, Any]],
    room_order: list[str],
) -> list[dict[str, Any]]:
    room_order_index = {room: index for index, room in enumerate(room_order)}
    aggregates: dict[str, dict[str, Any]] = {}

    for incident in incidents:
        room = _normalize_room(incident)
        if room not in room_order_index:
            raise ValueError(f"incident references unknown room: {room}")

        kind = _normalize_kind(incident)
        severity = _normalize_severity(incident)
        category = _normalize_category(incident)
        ts = _normalize_ts(incident)

        aggregate = aggregates.setdefault(
            room,
            {
                "room": room,
                "incident_count": 0,
                "anomaly_count": 0,
                "false_action_count": 0,
                "_severity_rank": 0,
                "categories": set(),
                "latest_ts": ts,
            },
        )
        aggregate["incident_count"] += 1
        aggregate[f"{kind}_count"] += 1
        aggregate["_severity_rank"] = max(aggregate["_severity_rank"], _severity_rank(severity))
        aggregate["latest_ts"] = max(aggregate["latest_ts"], ts)
        if category is not None:
            aggregate["categories"].add(category)

    cards: list[dict[str, Any]] = []
    for room in sorted(aggregates, key=lambda value: room_order_index[value]):
        aggregate = aggregates[room]
        severity_rank = aggregate["_severity_rank"]
        peak_severity = _severity_name(severity_rank)
        card = {
            "room": room,
            "incident_count": aggregate["incident_count"],
            "anomaly_count": aggregate["anomaly_count"],
            "false_action_count": aggregate["false_action_count"],
            "peak_severity": peak_severity,
            "review_priority": peak_severity,
            "categories": sorted(aggregate["categories"]),
            "latest_ts": aggregate["latest_ts"],
        }
        cards.append(card)

    return cards


def build_anomaly_and_false_action_dashboard(
    incidents: Iterable[Mapping[str, Any]],
    focus_room_id: str | None = None,
    ts: str | None = None,
    room_inventory_path: Path | None = None,
) -> dict[str, Any] | None:
    """Build an immutable anomaly review dashboard for planning."""

    room_order = _load_canonical_room_order(room_inventory_path)
    cards = _build_room_cards(incidents, room_order)
    if not cards:
        return None

    focus_room = None
    if focus_room_id is not None:
        focus_room = focus_room_id.strip().lower()
        if not focus_room:
            raise ValueError("focus_room_id cannot be empty")
        if focus_room not in {card["room"] for card in cards}:
            raise ValueError(f"focus_room_id not available in anomaly dashboard: {focus_room}")

    summary = {
        "room_count": len(cards),
        "incident_count": sum(card["incident_count"] for card in cards),
        "anomaly_count": sum(card["anomaly_count"] for card in cards),
        "false_action_count": sum(card["false_action_count"] for card in cards),
        "critical_room_count": sum(1 for card in cards if card["peak_severity"] == "critical"),
        "review_rooms": [card["room"] for card in cards],
    }

    dashboard_ts = min(card["latest_ts"] for card in cards)
    if ts is not None:
        dashboard_ts = str(ts)

    return {
        "dashboard_id": _dashboard_id(cards, focus_room),
        "source": ANOMALY_DASHBOARD_SOURCE,
        "dashboard_record_type": ANOMALY_DASHBOARD_RECORD_TYPE,
        "record_name": ANOMALY_DASHBOARD_RECORD_NAME,
        "dashboard_status": ANOMALY_DASHBOARD_STATUS,
        "tabs": ["summary", "rooms", "anomalies", "false_actions"],
        "focus_room_id": focus_room,
        "room_cards": cards,
        "summary": summary,
        "immutable": True,
        "retention": {
            "days": ANOMALY_DASHBOARD_RETENTION_DAYS,
            "immutable": True,
        },
        "ts": dashboard_ts,
    }
