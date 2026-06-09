"""Sensors for the smart home presence intelligence integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .bridge import VALID_ROOMS
from .const import DOMAIN

try:  # pragma: no cover - HA runtime only
    from homeassistant.components.sensor import SensorEntity
except ImportError:  # pragma: no cover
    class SensorEntity:  # type: ignore[too-many-ancestors]
        """Fallback sensor entity used for local validation."""


@dataclass(slots=True)
class RuntimeSensorSpec:
    """Specification for a runtime-backed sensor."""

    key: str
    name: str
    icon: str
    value_getter: Callable[[Any], Any]


ROOM_SENSOR_SPECS = [
    RuntimeSensorSpec(
        key=f"room_{room_id}_state",
        name=f"{room_id.replace('_', ' ').title()} State",
        icon="mdi:home-floor-0",
        value_getter=lambda runtime, room_id=room_id: runtime.room_activity.get(room_id, {}).get(
            "state", "idle"
        ),
    )
    for room_id in VALID_ROOMS
]

RUNTIME_SENSOR_SPECS = [
    RuntimeSensorSpec(
        key="bridge_health",
        name="Bridge Health",
        icon="mdi:network-strength-4",
        value_getter=lambda runtime: runtime.bridge_health,
    ),
    RuntimeSensorSpec(
        key="bridge_last_topic",
        name="Bridge Last Topic",
        icon="mdi:swap-horizontal",
        value_getter=lambda runtime: runtime.bridge_last_topic or "unknown",
    ),
    RuntimeSensorSpec(
        key="mqtt_topic_prefix",
        name="MQTT Topic Prefix",
        icon="mdi:mqtt",
        value_getter=lambda runtime: runtime.settings.mqtt_topic_prefix,
    ),
    RuntimeSensorSpec(
        key="retention_days",
        name="Retention Days",
        icon="mdi:archive-clock",
        value_getter=lambda runtime: runtime.settings.retention_days,
    ),
    RuntimeSensorSpec(
        key="retention_audit_status",
        name="Retention Audit Status",
        icon="mdi:shield-check",
        value_getter=lambda runtime: runtime.retention_audit_status,
    ),
]


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Any) -> None:
    """Add runtime-backed sensors for a config entry."""

    runtime = hass.data[DOMAIN][entry.entry_id]
    entities = [
        RuntimeSensor(runtime=runtime, entry_id=entry.entry_id, spec=spec)
        for spec in [*ROOM_SENSOR_SPECS, *RUNTIME_SENSOR_SPECS]
    ]
    async_add_entities(entities)


class RuntimeSensor(SensorEntity):  # type: ignore[misc]
    """Runtime-backed sensor with automatic state refresh."""

    def __init__(self, runtime: Any, entry_id: str, spec: RuntimeSensorSpec) -> None:
        self._runtime = runtime
        self._entry_id = entry_id
        self._spec = spec
        self._unsubscribe: Callable[[], None] | None = None

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self._spec.key}_{self._entry_id}"

    @property
    def name(self) -> str:
        return self._spec.name

    @property
    def icon(self) -> str:
        return self._spec.icon

    @property
    def native_value(self) -> Any:
        return self._spec.value_getter(self._runtime)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        if self._spec.key.startswith("room_"):
            return {}
        return {
            "bridge_health": self._runtime.bridge_health,
            "override_enabled": self._runtime.override_enabled,
            "refresh_time": self._runtime.refreshed_at.isoformat(),
        }

    async def async_added_to_hass(self) -> None:
        self._unsubscribe = self._runtime.add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsubscribe is not None:
            self._runtime.remove_listener(self.async_write_ha_state)
            self._unsubscribe = None
