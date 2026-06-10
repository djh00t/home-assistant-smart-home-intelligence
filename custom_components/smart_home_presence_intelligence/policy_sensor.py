"""Room policy sensors for the smart home presence intelligence integration."""

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
class PolicySensorSpec:
    """Specification for a room-policy sensor."""

    key: str
    name: str
    icon: str
    value_getter: Callable[[Any], Any]


def _room_policy_specs(room_id: str) -> list[PolicySensorSpec]:
    return [
        PolicySensorSpec(
            key=f"room_{room_id}_white_scene",
            name=f"{room_id.replace('_', ' ').title()} White Scene",
            icon="mdi:lightbulb-on",
            value_getter=lambda runtime, room_id=room_id: runtime.room_policy_snapshot(room_id)[
                "white_scene"
            ],
        ),
        PolicySensorSpec(
            key=f"room_{room_id}_color_sync",
            name=f"{room_id.replace('_', ' ').title()} Color Sync",
            icon="mdi:palette",
            value_getter=lambda runtime, room_id=room_id: runtime.room_policy_snapshot(room_id)[
                "color_sync_enabled"
            ],
        ),
        PolicySensorSpec(
            key=f"room_{room_id}_house_mode",
            name=f"{room_id.replace('_', ' ').title()} House Mode",
            icon="mdi:home-group",
            value_getter=lambda runtime, room_id=room_id: runtime.room_policy_snapshot(room_id)[
                "house_mode"
            ],
        ),
    ]


RUNTIME_POLICY_SPECS = [
    PolicySensorSpec(
        key="house_mode",
        name="House Mode",
        icon="mdi:home-account",
        value_getter=lambda runtime: runtime.house_mode(),
    ),
    PolicySensorSpec(
        key="total_humans_present",
        name="Total Humans Present",
        icon="mdi:account-group",
        value_getter=lambda runtime: runtime.total_humans_present(),
    ),
    PolicySensorSpec(
        key="total_pets_present",
        name="Total Pets Present",
        icon="mdi:dog",
        value_getter=lambda runtime: runtime.total_pets_present(),
    ),
]


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Any) -> None:
    """Add room-policy sensors for a config entry."""

    runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(build_policy_sensor_entities(runtime=runtime, entry_id=entry.entry_id))


def build_policy_sensor_entities(runtime: Any, entry_id: str) -> list["RoomPolicySensor"]:
    """Build room-policy entities for registration on Home Assistant's sensor platform."""

    specs = [*RUNTIME_POLICY_SPECS]
    for room_id in VALID_ROOMS:
        specs.extend(_room_policy_specs(room_id))
    return [RoomPolicySensor(runtime=runtime, entry_id=entry_id, spec=spec) for spec in specs]


class RoomPolicySensor(SensorEntity):  # type: ignore[misc]
    """Runtime-backed room policy sensor."""

    def __init__(self, runtime: Any, entry_id: str, spec: PolicySensorSpec) -> None:
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
            room_id = self._spec.key.removeprefix("room_").rsplit("_", 2)[0]
            return self._runtime.room_policy_snapshot(room_id)
        return {
            "bridge_health": self._runtime.bridge_health,
            "refresh_time": self._runtime.refreshed_at.isoformat(),
            "supported_rooms": list(VALID_ROOMS),
        }

    async def async_added_to_hass(self) -> None:
        self._unsubscribe = self._runtime.add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsubscribe is not None:
            self._runtime.remove_listener(self.async_write_ha_state)
            self._unsubscribe = None
