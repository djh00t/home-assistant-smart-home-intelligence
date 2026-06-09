"""Home Assistant integration for smart home presence intelligence."""

from __future__ import annotations

from typing import Any

from .bridge import CANONICAL_TOPIC, DEAD_LETTER_TOPIC, route_presence_event
from .const import (
    CONF_ENABLE_DIAGNOSTICS,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_RETENTION_DAYS,
    CONF_ROOM_CAPABILITIES_PATH,
    CONF_ROOM_INVENTORY_PATH,
    DEFAULT_ENABLE_DIAGNOSTICS,
    DEFAULT_MQTT_TOPIC_PREFIX,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_ROOM_CAPABILITIES_PATH,
    DEFAULT_ROOM_INVENTORY_PATH,
    DOMAIN,
    PLATFORMS,
    SERVICE_PUBLISH_TEST_EVENT,
    SERVICE_RELOAD_CONTRACTS,
    SERVICE_RUN_RETENTION_AUDIT,
    SERVICE_SET_OVERRIDE,
)
from .runtime import IntegrationRuntime, IntegrationSettings

try:  # Home Assistant is only available in the target runtime.
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant, ServiceCall
    from homeassistant.exceptions import HomeAssistantError
except ImportError:  # pragma: no cover - local repo validation fallback
    ConfigEntry = Any  # type: ignore[assignment]
    HomeAssistant = Any  # type: ignore[assignment]
    ServiceCall = Any  # type: ignore[assignment]

    class HomeAssistantError(Exception):
        """Fallback error used when Home Assistant is unavailable locally."""

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    """Set up the integration from YAML when Home Assistant loads the repository."""

    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up a config entry for the integration."""

    settings = IntegrationSettings(
        mqtt_topic_prefix=entry.options.get(
            CONF_MQTT_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX
        ),
        room_inventory_path=entry.options.get(
            CONF_ROOM_INVENTORY_PATH, DEFAULT_ROOM_INVENTORY_PATH
        ),
        room_capabilities_path=entry.options.get(
            CONF_ROOM_CAPABILITIES_PATH, DEFAULT_ROOM_CAPABILITIES_PATH
        ),
        retention_days=int(entry.options.get(CONF_RETENTION_DAYS, DEFAULT_RETENTION_DAYS)),
        enable_diagnostics=bool(
            entry.options.get(CONF_ENABLE_DIAGNOSTICS, DEFAULT_ENABLE_DIAGNOSTICS)
        ),
    )
    runtime = IntegrationRuntime.from_restore_payload(
        settings=settings,
        payload=entry.data.get("runtime_state"),
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = runtime
    if hasattr(entry, "runtime_data"):
        entry.runtime_data = runtime

    async def _publish_test_event(call: ServiceCall) -> None:
        event = runtime.build_test_event(dict(call.data))
        routed = route_presence_event(event)
        runtime.apply_routed_event(routed)
        _persist_runtime_state(hass, entry, runtime)

    async def _reload_contracts(call: ServiceCall) -> None:
        runtime.reload_contracts()
        _persist_runtime_state(hass, entry, runtime)

    async def _set_override(call: ServiceCall) -> None:
        runtime.set_override(
            enabled=bool(call.data.get("enabled", False)),
            reason=str(call.data.get("reason", "")).strip(),
        )
        _persist_runtime_state(hass, entry, runtime)

    async def _run_retention_audit(call: ServiceCall) -> None:
        runtime.last_retention_audit = runtime.run_retention_audit()
        _persist_runtime_state(hass, entry, runtime)

    _register_service(hass, SERVICE_PUBLISH_TEST_EVENT, _publish_test_event)
    _register_service(hass, SERVICE_RELOAD_CONTRACTS, _reload_contracts)
    _register_service(hass, SERVICE_SET_OVERRIDE, _set_override)
    _register_service(hass, SERVICE_RUN_RETENTION_AUDIT, _run_retention_audit)

    await hass.config_entries.async_forward_entry_setups(entry, list(PLATFORMS))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    runtime = hass.data.get(DOMAIN, {}).get(entry.entry_id)
    if isinstance(runtime, IntegrationRuntime):
        _persist_runtime_state(hass, entry, runtime)
    await hass.config_entries.async_unload_platforms(entry, list(PLATFORMS))
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if not hass.data.get(DOMAIN):
        hass.data.pop(DOMAIN, None)
    if hasattr(entry, "runtime_data"):
        entry.runtime_data = None
    return True


def _register_service(hass: HomeAssistant, name: str, handler: Any) -> None:
    """Register a service only once."""

    if hass.services.has_service(DOMAIN, name):
        return
    hass.services.async_register(DOMAIN, name, handler)


def runtime_snapshot(hass: HomeAssistant, entry_id: str) -> dict[str, Any]:
    """Return a redacted runtime snapshot for diagnostics."""

    runtime = hass.data[DOMAIN][entry_id]
    if not isinstance(runtime, IntegrationRuntime):
        raise HomeAssistantError("integration runtime unavailable")

    snapshot = runtime.snapshot()
    snapshot["canonical_topic"] = CANONICAL_TOPIC
    snapshot["dead_letter_topic"] = DEAD_LETTER_TOPIC
    return snapshot


def _persist_runtime_state(hass: HomeAssistant, entry: ConfigEntry, runtime: IntegrationRuntime) -> None:
    """Persist the current runtime state back onto the config entry."""

    if not hasattr(hass.config_entries, "async_update_entry"):
        return

    hass.config_entries.async_update_entry(
        entry,
        data={**dict(getattr(entry, "data", {})), "runtime_state": runtime.serialize()},
    )
