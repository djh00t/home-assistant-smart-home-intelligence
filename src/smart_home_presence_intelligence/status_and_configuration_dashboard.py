"""Operational status and configuration dashboard helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

import yaml

from .presence_bridge import CANONICAL_TOPIC, DEAD_LETTER_TOPIC


STATUS_CONFIGURATION_DASHBOARD_SOURCE = "status_and_configuration_dashboard"
STATUS_CONFIGURATION_DASHBOARD_RECORD_TYPE = "status_configuration_dashboard"
STATUS_CONFIGURATION_DASHBOARD_RECORD_NAME = "status_and_configuration_dashboard"
STATUS_CONFIGURATION_DASHBOARD_STATUS = "ready"
STATUS_CONFIGURATION_DASHBOARD_RETENTION_DAYS = 90
DEFAULT_TS = "1970-01-01T00:00:00Z"

ROOM_INVENTORY_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "inventory" / "rooms.yaml"
)


def _read_room_inventory(path: Path | None = None) -> dict[str, Any]:
    """Read the canonical room inventory contract."""

    inventory_path = path or ROOM_INVENTORY_PATH
    with inventory_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("room inventory contract must be a mapping")
    return payload


def _normalize_ts(value: Any) -> str:
    if value is None:
        return DEFAULT_TS
    text = str(value).strip()
    return text or DEFAULT_TS


def _runtime_snapshot(runtime_or_snapshot: Any) -> dict[str, Any]:
    """Return a defensive runtime snapshot regardless of the caller input shape."""

    if isinstance(runtime_or_snapshot, Mapping):
        return dict(runtime_or_snapshot)

    snapshot_method = getattr(runtime_or_snapshot, "snapshot", None)
    if callable(snapshot_method):
        snapshot = snapshot_method()
        if not isinstance(snapshot, Mapping):
            raise ValueError("runtime snapshot must be a mapping")
        return dict(snapshot)

    raise TypeError("runtime must provide snapshot() or be a mapping")


def _room_entries(path: Path | None = None) -> list[dict[str, Any]]:
    """Return canonical rooms followed by external zones."""

    payload = _read_room_inventory(path)
    ordered: list[dict[str, Any]] = []
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
            if not normalized_room:
                continue
            ordered.append({**entry, "room_id": normalized_room})

    if not ordered:
        raise ValueError("room inventory has no canonical rooms configured")
    return ordered


def _room_activity_snapshot(
    runtime_or_snapshot: Any,
    room_id: str,
    room_entry: Mapping[str, Any],
) -> dict[str, Any]:
    runtime_policy_snapshot = getattr(runtime_or_snapshot, "room_policy_snapshot", None)
    if callable(runtime_policy_snapshot):
        return dict(runtime_policy_snapshot(room_id))

    snapshot = _runtime_snapshot(runtime_or_snapshot)
    room_activity = snapshot.get("room_activity", {})
    room = room_activity.get(room_id, {}) if isinstance(room_activity, Mapping) else {}
    return {
        "room_id": room_id,
        "house_mode": snapshot.get("house_mode", "empty"),
        "supports_lighting": bool(room_entry.get("supports_lighting", False)),
        "supports_color": False,
        "white_scene": "none",
        "color_sync_enabled": False,
        "manual_override_minutes": 0,
        "person_only_actions": False,
        "pet_only_actions": False,
        "occupancy_state": room.get("state", "idle"),
        "human_count": int(room.get("human_count", 0) or 0),
        "pet_count": int(room.get("pet_count", 0) or 0),
        "vehicle_count": int(room.get("vehicle_count", 0) or 0),
        "last_seen": str(room.get("last_seen", "")),
    }


def _build_room_cards(
    runtime_or_snapshot: Any, room_entries: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    snapshot = _runtime_snapshot(runtime_or_snapshot)
    room_activity = snapshot.get("room_activity", {})
    if not isinstance(room_activity, Mapping):
        room_activity = {}

    cards: list[dict[str, Any]] = []
    for entry in room_entries:
        room_id = entry["room_id"]
        details = _room_activity_snapshot(runtime_or_snapshot, room_id, entry)
        current = room_activity.get(room_id, {}) if isinstance(room_activity, Mapping) else {}
        card = {
            "room_id": room_id,
            "display_name": entry.get("display_name", room_id.replace("_", " ").title()),
            "room_type": entry.get("room_type", "room"),
            "supports_occupancy": bool(entry.get("supports_occupancy", False)),
            "supports_lighting": bool(entry.get("supports_lighting", False)),
            "source_priority": list(entry.get("source_priority", []))
            if isinstance(entry.get("source_priority", []), list)
            else [],
            "state": str(current.get("state", details.get("occupancy_state", "idle"))),
            "human_count": int(details.get("human_count", 0) or 0),
            "pet_count": int(details.get("pet_count", 0) or 0),
            "vehicle_count": int(details.get("vehicle_count", 0) or 0),
            "last_event_type": str(current.get("last_event_type", "")),
            "last_source": str(current.get("last_source", "")),
            "last_confidence": float(current.get("last_confidence", 0.0) or 0.0),
            "last_seen": str(details.get("last_seen", current.get("last_seen", ""))),
            "house_mode": str(details.get("house_mode", snapshot.get("house_mode", "empty"))),
            "supports_color": bool(details.get("supports_color", False)),
            "white_scene": str(details.get("white_scene", "none")),
            "color_sync_enabled": bool(details.get("color_sync_enabled", False)),
            "manual_override_minutes": int(details.get("manual_override_minutes", 0) or 0),
            "person_only_actions": bool(details.get("person_only_actions", False)),
            "pet_only_actions": bool(details.get("pet_only_actions", False)),
        }
        cards.append(card)

    return cards


def _build_config_snapshot(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    settings = snapshot.get("settings", {})
    if not isinstance(settings, Mapping):
        settings = {}

    return {
        "mqtt_topic_prefix": str(settings.get("mqtt_topic_prefix", "")),
        "room_inventory_path": str(settings.get("room_inventory_path", "")),
        "room_capabilities_path": str(settings.get("room_capabilities_path", "")),
        "retention_days": int(settings.get("retention_days", STATUS_CONFIGURATION_DASHBOARD_RETENTION_DAYS) or STATUS_CONFIGURATION_DASHBOARD_RETENTION_DAYS),
        "enable_diagnostics": bool(settings.get("enable_diagnostics", True)),
        "canonical_topic": CANONICAL_TOPIC,
        "dead_letter_topic": DEAD_LETTER_TOPIC,
    }


def _build_status_cards(snapshot: Mapping[str, Any], config_snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "key": "bridge",
            "title": "Bridge",
            "icon": "mdi:network-strength-4",
            "status": str(snapshot.get("bridge_health", "unknown")),
            "values": {
                "bridge_last_topic": str(snapshot.get("bridge_last_topic", "")),
                "bridge_last_error": str(snapshot.get("bridge_last_error", "")),
            },
        },
        {
            "key": "occupancy",
            "title": "Occupancy",
            "icon": "mdi:home-account",
            "status": str(snapshot.get("house_mode", "empty")),
            "values": {
                "total_humans_present": int(snapshot.get("total_humans_present", 0) or 0),
                "total_pets_present": int(snapshot.get("total_pets_present", 0) or 0),
                "override_enabled": bool(snapshot.get("override_enabled", False)),
                "override_reason": str(snapshot.get("override_reason", "")),
            },
        },
        {
            "key": "retention",
            "title": "Retention",
            "icon": "mdi:archive-clock",
            "status": str(snapshot.get("retention_audit_status", "not_run")),
            "values": {
                "retention_audit_message": str(snapshot.get("retention_audit_message", "")),
                "retention_days": int(config_snapshot.get("retention_days", STATUS_CONFIGURATION_DASHBOARD_RETENTION_DAYS)),
            },
        },
    ]


def _build_action_cards() -> list[dict[str, Any]]:
    return [
        {
            "key": "publish_test_event",
            "title": "Publish test event",
            "service": "smart_home_presence_intelligence.publish_test_event",
            "icon": "mdi:send",
            "description": "Inject a synthetic event through the MQTT bridge.",
            "example": {
                "source": "tracker",
                "room": "lounge_room",
                "type": "state_change",
            },
        },
        {
            "key": "reload_contracts",
            "title": "Reload contracts",
            "service": "smart_home_presence_intelligence.reload_contracts",
            "icon": "mdi:reload",
            "description": "Refresh the room inventory, capability catalog, and runtime snapshot.",
        },
        {
            "key": "set_override",
            "title": "Set override",
            "service": "smart_home_presence_intelligence.set_override",
            "icon": "mdi:hand-back-right",
            "description": "Toggle the operator override path without mutating the config flow.",
            "example": {
                "enabled": True,
                "reason": "family activity",
            },
        },
        {
            "key": "run_retention_audit",
            "title": "Run retention audit",
            "service": "smart_home_presence_intelligence.run_retention_audit",
            "icon": "mdi:shield-check",
            "description": "Produce the redacted retention audit summary.",
        },
    ]


def _build_jetson_cards(config_snapshot: Mapping[str, Any]) -> list[dict[str, Any]]:
    prefix = str(config_snapshot.get("mqtt_topic_prefix", "ha/presence"))
    return [
        {
            "key": "jetson_stack",
            "title": "Jetson Xavier edge stack",
            "icon": "mdi:chip",
            "values": {
                "expected_stack": "Frigate + MQTT bridge",
                "canonical_topic": str(config_snapshot.get("canonical_topic", CANONICAL_TOPIC)),
                "dead_letter_topic": str(config_snapshot.get("dead_letter_topic", DEAD_LETTER_TOPIC)),
                "mqtt_topic_prefix": prefix,
            },
        },
        {
            "key": "jetson_checks",
            "title": "Connection checks",
            "icon": "mdi:check-network",
            "values": {
                "broker_reachable": True,
                "publisher_role": "Jetson or adjacent bridge publishes canonical events",
                "home_assistant_role": "Consumes the canonical MQTT topic and shows status entities",
            },
        },
    ]


def _dashboard_id(payload: Mapping[str, Any]) -> str:
    fragment = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return f"{STATUS_CONFIGURATION_DASHBOARD_SOURCE}::{fragment}"


def build_status_and_configuration_dashboard(
    runtime_or_snapshot: Any,
    ts: str | None = None,
    room_inventory_path: Path | None = None,
) -> dict[str, Any]:
    """Build an immutable status and configuration dashboard model."""

    snapshot = _runtime_snapshot(runtime_or_snapshot)
    room_entries = _room_entries(room_inventory_path)
    room_cards = _build_room_cards(runtime_or_snapshot, room_entries)
    config_snapshot = _build_config_snapshot(snapshot)
    status_cards = _build_status_cards(snapshot, config_snapshot)
    action_cards = _build_action_cards()
    jetson_cards = _build_jetson_cards(config_snapshot)

    sections = [
        {
            "key": "overview",
            "title": "Overview",
            "cards": status_cards,
        },
        {
            "key": "configuration",
            "title": "Configuration",
            "cards": [config_snapshot],
        },
        {
            "key": "actions",
            "title": "Actions",
            "cards": action_cards,
        },
        {
            "key": "jetson",
            "title": "Jetson Xavier",
            "cards": jetson_cards,
        },
        {
            "key": "rooms",
            "title": "Rooms",
            "cards": room_cards,
        },
    ]

    summary = {
        "room_count": len(room_cards),
        "occupied_room_count": sum(1 for card in room_cards if card["state"] != "idle"),
        "lighting_room_count": sum(1 for card in room_cards if card["supports_lighting"]),
        "bridge_health": str(snapshot.get("bridge_health", "unknown")),
        "house_mode": str(snapshot.get("house_mode", "empty")),
        "override_enabled": bool(snapshot.get("override_enabled", False)),
        "retention_audit_status": str(snapshot.get("retention_audit_status", "not_run")),
        "mqtt_topic_prefix": config_snapshot["mqtt_topic_prefix"],
    }

    dashboard_ts = ts or snapshot.get("refreshed_at") or snapshot.get("ts") or DEFAULT_TS

    return {
        "dashboard_id": _dashboard_id(
            {
                "config_snapshot": config_snapshot,
                "room_cards": room_cards,
                "sections": sections,
                "summary": summary,
            }
        ),
        "source": STATUS_CONFIGURATION_DASHBOARD_SOURCE,
        "dashboard_record_type": STATUS_CONFIGURATION_DASHBOARD_RECORD_TYPE,
        "record_name": STATUS_CONFIGURATION_DASHBOARD_RECORD_NAME,
        "dashboard_status": STATUS_CONFIGURATION_DASHBOARD_STATUS,
        "tabs": [section["key"] for section in sections],
        "sections": sections,
        "summary": summary,
        "config_snapshot": config_snapshot,
        "action_cards": action_cards,
        "jetson_cards": jetson_cards,
        "room_cards": room_cards,
        "immutable": True,
        "retention": {
            "days": STATUS_CONFIGURATION_DASHBOARD_RETENTION_DAYS,
            "immutable": True,
        },
        "ts": _normalize_ts(dashboard_ts),
    }
