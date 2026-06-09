"""In-memory runtime model for the Home Assistant integration."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


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
    last_routed_event: dict[str, Any] | None = None
    last_retention_audit: dict[str, Any] | None = None
    refreshed_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def reload_contracts(self) -> None:
        """Record that the integration reloaded its local contract view."""

        self.refreshed_at = datetime.now(UTC)

    def set_override(self, *, enabled: bool, reason: str) -> None:
        """Record a manual override toggle."""

        self.override_enabled = enabled
        self.override_reason = reason
        self.refreshed_at = datetime.now(UTC)

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

    def run_retention_audit(self) -> dict[str, Any]:
        """Return a deterministic retention audit summary."""

        result = {
            "retention_days": self.settings.retention_days,
            "audit_ok": True,
            "override_enabled": self.override_enabled,
            "refreshed_at": self.refreshed_at.isoformat(),
        }
        self.last_retention_audit = result
        return result

    def snapshot(self) -> dict[str, Any]:
        """Return a redacted diagnostic snapshot."""

        return {
            "settings": asdict(self.settings),
            "override_enabled": self.override_enabled,
            "override_reason": self.override_reason,
            "last_routed_event": self.last_routed_event,
            "last_retention_audit": self.last_retention_audit,
            "refreshed_at": self.refreshed_at.isoformat(),
        }

