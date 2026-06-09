"""Binary sensors for the smart home presence intelligence integration."""

from __future__ import annotations

from typing import Any, Callable

from .const import DOMAIN

try:  # pragma: no cover - HA runtime only
    from homeassistant.components.binary_sensor import BinarySensorEntity
except ImportError:  # pragma: no cover
    class BinarySensorEntity:  # type: ignore[too-many-ancestors]
        """Fallback binary sensor entity used for local validation."""


async def async_setup_entry(hass: Any, entry: Any, async_add_entities: Any) -> None:
    """Add binary sensors for a config entry."""

    runtime = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            OverrideBinarySensor(runtime=runtime, entry_id=entry.entry_id),
            DiagnosticsBinarySensor(runtime=runtime, entry_id=entry.entry_id),
        ]
    )


class _RuntimeBinarySensor(BinarySensorEntity):  # type: ignore[misc]
    """Base class for runtime-backed binary sensors."""

    key = "runtime_binary_sensor"
    name = "Runtime Binary Sensor"
    icon = "mdi:toggle-switch"

    def __init__(self, runtime: Any, entry_id: str) -> None:
        self._runtime = runtime
        self._entry_id = entry_id
        self._unsubscribe: Callable[[], None] | None = None

    @property
    def unique_id(self) -> str:
        return f"{DOMAIN}_{self.key}_{self._entry_id}"

    @property
    def is_on(self) -> bool:
        return self._is_on()

    def _is_on(self) -> bool:
        raise NotImplementedError

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "refresh_time": self._runtime.refreshed_at.isoformat(),
            "bridge_health": self._runtime.bridge_health,
        }

    async def async_added_to_hass(self) -> None:
        self._unsubscribe = self._runtime.add_listener(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsubscribe is not None:
            self._runtime.remove_listener(self.async_write_ha_state)
            self._unsubscribe = None


class OverrideBinarySensor(_RuntimeBinarySensor):
    """Expose whether manual override is active."""

    key = "manual_override"
    name = "Manual Override Active"
    icon = "mdi:shield-alert"

    def _is_on(self) -> bool:
        return self._runtime.override_enabled


class DiagnosticsBinarySensor(_RuntimeBinarySensor):
    """Expose whether diagnostics are effectively enabled."""

    key = "diagnostics_enabled"
    name = "Diagnostics Enabled"
    icon = "mdi:heart-pulse"

    def _is_on(self) -> bool:
        return bool(self._runtime.settings.enable_diagnostics)
