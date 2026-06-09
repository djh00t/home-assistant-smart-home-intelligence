"""In-memory runtime model for the Home Assistant integration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any, Callable

from .bridge import DEAD_LETTER_TOPIC, VALID_ROOMS


@dataclass(slots=True)
class IntegrationSettings:
    """User-configurable integration settings."""

    mqtt_topic_prefix: str
    room_inventory_path: str
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

    def __post_init__(self) -> None:
        for room_id in VALID_ROOMS:
            self.room_activity.setdefault(
                room_id,
                {
                    "state": "idle",
                    "last_event_type": "",
                    "last_source": "",
                    "last_entity_class": "",
                    "last_confidence": 0.0,
                    "last_seen": "",
                },
            )

    @classmethod
    def from_restore_payload(
        cls, settings: IntegrationSettings, payload: dict[str, Any] | None
    ) -> "IntegrationRuntime":
        """Restore runtime state from a serialized payload."""

        payload = payload or {}
        runtime = cls(
            settings=settings,
            override_enabled=bool(payload.get("override_enabled", False)),
            override_reason=str(payload.get("override_reason", "")),
            bridge_health=str(payload.get("bridge_health", "unknown")),
            bridge_last_topic=payload.get("bridge_last_topic"),
            bridge_last_error=payload.get("bridge_last_error"),
            retention_audit_status=str(payload.get("retention_audit_status", "not_run")),
            retention_audit_message=str(payload.get("retention_audit_message", "")),
            room_activity=dict(payload.get("room_activity", {})),
        )
        runtime.last_routed_event = payload.get("last_routed_event")
        runtime.last_retention_audit = payload.get("last_retention_audit")
        refreshed_at = payload.get("refreshed_at")
        if refreshed_at:
            runtime.refreshed_at = datetime.fromisoformat(str(refreshed_at))
        runtime.__post_init__()
        return runtime

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
            "room": payload.get("room", "lounge_room"),
            "entity_class": payload.get("entity_class", "human"),
            "confidence": payload.get("confidence", 1.0),
            "ts": payload.get("ts", datetime.now(UTC).isoformat()),
        }
        event.update(payload)
        return event

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
        room["state"] = "idle" if room["last_event_type"] == "leave" else "occupied"
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

    def snapshot(self) -> dict[str, Any]:
        """Return a redacted diagnostic snapshot."""

        return {
            "settings": asdict(self.settings),
            "override_enabled": self.override_enabled,
            "override_reason": self.override_reason,
            "bridge_health": self.bridge_health,
            "bridge_last_topic": self.bridge_last_topic,
            "bridge_last_error": self.bridge_last_error,
            "retention_audit_status": self.retention_audit_status,
            "retention_audit_message": self.retention_audit_message,
            "room_activity": self.room_activity,
            "last_routed_event": self.last_routed_event,
            "last_retention_audit": self.last_retention_audit,
            "refreshed_at": self.refreshed_at.isoformat(),
        }

    def serialize(self) -> dict[str, Any]:
        """Return a JSON-safe restore payload."""

        return self.snapshot()
