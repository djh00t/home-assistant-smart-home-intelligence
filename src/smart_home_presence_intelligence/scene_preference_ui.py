"""Planning-only scene preference dashboard helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json

import yaml

from .anpr_service_and_event import build_opaque_identifier


SCENE_PREFERENCE_UI_SOURCE = "scene_preference_ui"
SCENE_PREFERENCE_UI_RECORD_TYPE = "scene_preferences_dashboard"
SCENE_PREFERENCE_UI_RECORD_NAME = "scene_preference_ui"
SCENE_PREFERENCE_UI_STATUS = "ready"
SCENE_PREFERENCE_UI_RETENTION_DAYS = 90
DEFAULT_TS = "1970-01-01T00:00:00Z"

ROOM_CAPABILITIES_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "inventory"
    / "room_capabilities.yaml"
)


def _read_room_capabilities(path: Path | None = None) -> dict[str, Any]:
    """Read and normalize the room capability payload."""

    capabilities_path = path or ROOM_CAPABILITIES_PATH
    with capabilities_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("room capability contract must be a mapping")
    return payload


def _normalize_text_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    normalized = []
    for value in values:
        if isinstance(value, str):
            text = value.strip()
            if text:
                normalized.append(text)
    return sorted(normalized)


def _normalize_ts(payload: Mapping[str, Any] | None = None) -> str:
    if payload is None:
        return DEFAULT_TS
    ts = payload.get("ts", DEFAULT_TS)
    return str(ts)


def _build_room_cards(path: Path | None = None) -> list[dict[str, Any]]:
    payload = _read_room_capabilities(path)
    entries = payload.get("room_capabilities", [])
    if not isinstance(entries, list):
        raise ValueError("room capability contract must define room_capabilities as a list")

    cards: list[dict[str, Any]] = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue

        room_id = entry.get("room_id")
        lighting = entry.get("lighting", {})
        policies = entry.get("policies", {})
        if not isinstance(room_id, str) or not isinstance(lighting, dict) or not isinstance(policies, dict):
            continue

        if lighting.get("supports_lighting") is not True:
            continue

        normalized_room = room_id.strip().lower()
        if not normalized_room:
            continue

        supports_color = lighting.get("supports_color") is True
        available_controls = ["day_scene", "night_scene", "manual_override_minutes"]
        if supports_color:
            available_controls.append("color_scene_toggle")

        card = {
            "room": normalized_room,
            "supports_color": supports_color,
            "white_groups": _normalize_text_list(lighting.get("white_groups", [])),
            "color_groups": _normalize_text_list(lighting.get("color_groups", [])),
            "default_day_scene": lighting.get("default_day_scene"),
            "default_night_scene": lighting.get("default_night_scene"),
            "manual_override_minutes": policies.get("manual_override_minutes"),
            "person_only_actions": policies.get("person_only_actions") is True,
            "pet_only_actions": policies.get("pet_only_actions") is True,
            "available_controls": available_controls,
        }
        cards.append(card)

    cards.sort(key=lambda card: card["room"])
    return cards


def _dashboard_id(cards: list[dict[str, Any]], focus_room_id: str | None = None) -> str:
    payload = {
        "focus_room_id": focus_room_id,
        "room_cards": cards,
    }
    return build_opaque_identifier(SCENE_PREFERENCE_UI_SOURCE, payload)


def build_scene_preference_ui(
    focus_room_id: str | None = None,
    ts: str | None = None,
    capabilities_path: Path | None = None,
) -> dict[str, Any]:
    """Build an immutable scene preference dashboard model for planning."""

    cards = _build_room_cards(capabilities_path)
    if not cards:
        raise ValueError("room capabilities have no lighting rooms configured")

    if focus_room_id is not None:
        focus_room = focus_room_id.strip().lower()
        if not focus_room:
            raise ValueError("focus_room_id cannot be empty")
        if focus_room not in {card["room"] for card in cards}:
            raise ValueError(f"focus_room_id not available in scene preference UI: {focus_room}")
    else:
        focus_room = None

    summary = {
        "room_count": len(cards),
        "color_room_count": sum(1 for card in cards if card["supports_color"]),
        "white_only_room_count": sum(1 for card in cards if not card["supports_color"]),
        "supported_rooms": [card["room"] for card in cards],
    }

    return {
        "dashboard_id": _dashboard_id(cards, focus_room),
        "source": SCENE_PREFERENCE_UI_SOURCE,
        "ui_record_type": SCENE_PREFERENCE_UI_RECORD_TYPE,
        "record_name": SCENE_PREFERENCE_UI_RECORD_NAME,
        "ui_status": SCENE_PREFERENCE_UI_STATUS,
        "tabs": ["rooms", "overrides", "safety"],
        "focus_room_id": focus_room,
        "room_cards": cards,
        "summary": summary,
        "immutable": True,
        "retention": {
            "days": SCENE_PREFERENCE_UI_RETENTION_DAYS,
            "immutable": True,
        },
        "ts": _normalize_ts({"ts": ts} if ts is not None else None),
    }
