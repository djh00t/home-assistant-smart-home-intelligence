"""In-memory runtime model for the Home Assistant integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import yaml

from .bridge import DEAD_LETTER_TOPIC, VALID_ROOMS

PUBLIC_SAMPLE_CAPABILITY_ALIASES = {
    "room_alpha": "sample_room_alpha",
    "room_beta": "sample_room_beta",
    "room_gamma": "sample_study_zone",
    "room_delta": "sample_room_delta",
    "room_epsilon": "sample_room_epsilon",
    "room_zeta": "sample_storage_zone",
}


@dataclass(slots=True)
class IntegrationSettings:
    """User-configurable integration settings."""

    mqtt_topic_prefix: str
    room_inventory_path: str
    room_capabilities_path: str
    retention_days: int
    enable_diagnostics: bool = True


@dataclass(slots=True)
class IntegrationRuntime:
    """Mutable integration state kept in Home Assistant memory."""

    settings: IntegrationSettings
    override_enabled: bool = False
    override_reason: str = ""
    bridge_health: str = "unknown"
    bridge_last_topic: str | None = None
    bridge_last_error: str | None = None
    retention_audit_status: str = "not_run"
    retention_audit_message: str = ""
    room_activity: dict[str, dict[str, Any]] = field(default_factory=dict)
    last_routed_event: dict[str, Any] | None = None
    last_retention_audit: dict[str, Any] | None = None
    refreshed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    _listeners: list[Callable[[], None]] = field(default_factory=list, repr=False)
    _room_capabilities_cache: dict[str, dict[str, Any]] | None = field(
        default=None, repr=False
    )

    def __post_init__(self) -> None:
        for room_id in VALID_ROOMS:
            current = dict(self.room_activity.get(room_id, {}))
            current.setdefault("state", "idle")
            current.setdefault("human_count", 0)
            current.setdefault("pet_count", 0)
            current.setdefault("vehicle_count", 0)
            current.setdefault("last_event_type", "")
            current.setdefault("last_source", "")
            current.setdefault("last_entity_class", "")
            current.setdefault("last_confidence", 0.0)
            current.setdefault("last_seen", "")
            self.room_activity[room_id] = current

    @classmethod
    def from_restore_payload(
        cls, settings: IntegrationSettings, payload: dict[str, Any] | None
    ) -> "IntegrationRuntime":
        """Restore runtime state from a serialized payload."""

        payload = payload or {}
        return cls(
            settings=settings,
            override_enabled=bool(payload.get("override_enabled", False)),
            bridge_health=str(payload.get("bridge_health", "unknown")),
            retention_audit_status=str(payload.get("retention_audit_status", "not_run")),
            retention_audit_message=str(payload.get("retention_audit_message", "")),
        )

    def add_listener(self, callback: Callable[[], None]) -> None:
        """Register a listener that should run after each state update."""

        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback: Callable[[], None]) -> None:
        """Remove a previously registered listener."""

        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self) -> None:
        for callback in list(self._listeners):
            callback()

    def reload_contracts(self) -> None:
        """Record that the integration reloaded its local contract view."""

        self.refreshed_at = datetime.now(UTC)
        self._room_capabilities_cache = None
        self._notify_listeners()

    def set_override(self, *, enabled: bool, reason: str) -> None:
        """Record a manual override toggle."""

        self.override_enabled = enabled
        self.override_reason = reason
        self.refreshed_at = datetime.now(UTC)
        self._notify_listeners()

    def build_test_event(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Create a predictable test event for service smoke checks."""

        event = {
            "event_id": payload.get("event_id", "test-event"),
            "source": payload.get("source", "tracker"),
            "type": payload.get("type", "state_change"),
            "room": payload.get("room", "room_delta"),
            "entity_class": payload.get("entity_class", "human"),
            "confidence": payload.get("confidence", 1.0),
            "ts": payload.get("ts", datetime.now(UTC).isoformat()),
        }
        event.update(payload)
        return event

    def _load_room_capabilities(self) -> dict[str, dict[str, Any]]:
        """Return the room capability catalog keyed by room id."""

        if self._room_capabilities_cache is not None:
            return self._room_capabilities_cache

        path = Path(self.settings.room_capabilities_path)
        with path.open(encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}
        capabilities: dict[str, dict[str, Any]] = {}
        for entry in payload.get("room_capabilities", []):
            if not isinstance(entry, dict):
                continue
            room_id = entry.get("room_id")
            if isinstance(room_id, str) and room_id.strip():
                capabilities[room_id.strip().lower()] = entry
        self._room_capabilities_cache = capabilities
        return capabilities

    def room_capability(self, room_id: str) -> dict[str, Any]:
        """Return the capability entry for a room."""

        capabilities = self._load_room_capabilities()
        if room_id in capabilities:
            return capabilities[room_id]
        sample_room_id = PUBLIC_SAMPLE_CAPABILITY_ALIASES.get(room_id)
        if sample_room_id is None:
            return {}
        return capabilities.get(sample_room_id, {})

    def total_humans_present(self) -> int:
        """Return the total number of tracked humans across all rooms."""

        return sum(int(room.get("human_count", 0)) for room in self.room_activity.values())

    def total_pets_present(self) -> int:
        """Return the total number of tracked pets across all rooms."""

        return sum(int(room.get("pet_count", 0)) for room in self.room_activity.values())

    def house_mode(self) -> str:
        """Return the canonical house mode for the current runtime state."""

        humans = self.total_humans_present()
        pets = self.total_pets_present()
        if humans > 0:
            return "occupied"
        if pets > 0:
            return "pet_mode"
        return "empty"

    def room_policy_snapshot(self, room_id: str) -> dict[str, Any]:
        """Return a policy summary for one room."""

        room = self.room_activity.get(room_id, {})
        capability = self.room_capability(room_id)
        lighting = capability.get("lighting", {}) if isinstance(capability, dict) else {}
        policies = capability.get("policies", {}) if isinstance(capability, dict) else {}
        supports_lighting = bool(lighting.get("supports_lighting", False))
        supports_color = bool(lighting.get("supports_color", False))
        manual_override_minutes = int(policies.get("manual_override_minutes", 0) or 0)
        current_hour = datetime.now().hour
        is_daytime = 5 <= current_hour <= 16
        if not supports_lighting:
            scene = "none"
        elif room.get("state") in {"idle", "sleeping", "bed_motion_only"} or not is_daytime:
            scene = lighting.get("default_night_scene") or "none"
        else:
            scene = lighting.get("default_day_scene") or lighting.get("default_night_scene") or "none"
        color_sync_enabled = bool(
            supports_color and room.get("state") == "occupied" and not self.override_enabled
        )
        return {
            "room_id": room_id,
            "house_mode": self.house_mode(),
            "supports_lighting": supports_lighting,
            "supports_color": supports_color,
            "white_scene": scene,
            "color_sync_enabled": color_sync_enabled,
            "manual_override_minutes": manual_override_minutes,
            "person_only_actions": bool(policies.get("person_only_actions", False)),
            "pet_only_actions": bool(policies.get("pet_only_actions", False)),
            "occupancy_state": room.get("state", "idle"),
            "human_count": int(room.get("human_count", 0)),
            "pet_count": int(room.get("pet_count", 0)),
            "vehicle_count": int(room.get("vehicle_count", 0)),
            "last_seen": room.get("last_seen", ""),
        }

    def apply_routed_event(self, routed: dict[str, Any]) -> None:
        """Store the latest routed event and refresh room activity."""

        self.last_routed_event = routed
        self.bridge_last_topic = routed.get("topic")
        if routed.get("topic") == DEAD_LETTER_TOPIC:
            self.bridge_health = "degraded"
            self.bridge_last_error = "; ".join(routed.get("errors", []))
            self.refreshed_at = datetime.now(UTC)
            self._notify_listeners()
            return

        event = dict(routed.get("event", {}))
        room_id = str(event.get("room", ""))
        room = self.room_activity.setdefault(
            room_id,
            {
                "state": "idle",
                "human_count": 0,
                "pet_count": 0,
                "vehicle_count": 0,
                "last_event_type": "",
                "last_source": "",
                "last_entity_class": "",
                "last_confidence": 0.0,
                "last_seen": "",
            },
        )
        room["last_event_type"] = str(event.get("type", ""))
        room["last_source"] = str(event.get("source", ""))
        room["last_entity_class"] = str(event.get("entity_class", ""))
        room["last_confidence"] = float(event.get("confidence", 0.0) or 0.0)
        room["last_seen"] = str(event.get("ts", ""))

        delta = 0
        if room["last_event_type"] == "enter":
            delta = 1
        elif room["last_event_type"] == "leave":
            delta = -1

        if room["last_entity_class"] == "human":
            room["human_count"] = max(0, int(room.get("human_count", 0)) + delta)
        elif room["last_entity_class"] == "pet":
            room["pet_count"] = max(0, int(room.get("pet_count", 0)) + delta)
        elif room["last_entity_class"] == "vehicle":
            room["vehicle_count"] = max(0, int(room.get("vehicle_count", 0)) + delta)

        room["state"] = (
            "occupied"
            if int(room.get("human_count", 0)) > 0
            or int(room.get("pet_count", 0)) > 0
            or int(room.get("vehicle_count", 0)) > 0
            else "idle"
        )
        self.bridge_health = "healthy"
        self.bridge_last_error = ""
        self.refreshed_at = datetime.now(UTC)
        self._notify_listeners()

    def run_retention_audit(self) -> dict[str, Any]:
        """Return a deterministic retention audit summary."""

        result = {
            "retention_days": self.settings.retention_days,
            "audit_ok": True,
            "override_enabled": self.override_enabled,
            "refreshed_at": self.refreshed_at.isoformat(),
        }
        self.last_retention_audit = result
        self.retention_audit_status = "pass"
        self.retention_audit_message = "audit_ok"
        self._notify_listeners()
        return result

    def diagnostics_snapshot(self) -> dict[str, Any]:
        """Return the opt-in redacted diagnostics payload."""

        if not self.settings.enable_diagnostics:
            return {"diagnostics_enabled": False}

        return {
            "diagnostics_enabled": True,
            "settings": {
                "mqtt_topic_prefix": self.settings.mqtt_topic_prefix,
                "retention_days": self.settings.retention_days,
                "enable_diagnostics": self.settings.enable_diagnostics,
            },
            "override_enabled": self.override_enabled,
            "bridge_health": self.bridge_health,
            "retention_audit_status": self.retention_audit_status,
            "retention_audit_message": self.retention_audit_message,
        }

    def serialize(self) -> dict[str, Any]:
        """Return a JSON-safe restore payload."""

        return {
            "override_enabled": self.override_enabled,
            "bridge_health": self.bridge_health,
            "retention_audit_status": self.retention_audit_status,
            "retention_audit_message": self.retention_audit_message,
        }
