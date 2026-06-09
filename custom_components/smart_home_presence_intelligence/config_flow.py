"""Config flow for the smart home presence intelligence integration."""

from __future__ import annotations

from typing import Any

from .const import (
    CONF_ENABLE_DIAGNOSTICS,
    CONF_MQTT_TOPIC_PREFIX,
    CONF_RETENTION_DAYS,
    CONF_ROOM_INVENTORY_PATH,
    DEFAULT_ENABLE_DIAGNOSTICS,
    DEFAULT_MQTT_TOPIC_PREFIX,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_ROOM_INVENTORY_PATH,
    DOMAIN,
    NAME,
)

try:  # pragma: no cover - Home Assistant is not installed in local repo checks.
    import voluptuous as vol
    from homeassistant import config_entries
    from homeassistant.data_entry_flow import FlowResult
except ImportError:  # pragma: no cover
    vol = None  # type: ignore[assignment]
    config_entries = object()  # type: ignore[assignment]
    FlowResult = dict[str, Any]  # type: ignore[assignment]


def _schema(defaults: dict[str, Any] | None = None) -> Any:
    """Build the user configuration schema."""

    defaults = defaults or {}
    if vol is None:
        return defaults
    return vol.Schema(
        {
            vol.Required(
                CONF_MQTT_TOPIC_PREFIX,
                default=defaults.get(CONF_MQTT_TOPIC_PREFIX, DEFAULT_MQTT_TOPIC_PREFIX),
            ): str,
            vol.Required(
                CONF_ROOM_INVENTORY_PATH,
                default=defaults.get(CONF_ROOM_INVENTORY_PATH, DEFAULT_ROOM_INVENTORY_PATH),
            ): str,
            vol.Required(
                CONF_RETENTION_DAYS,
                default=defaults.get(CONF_RETENTION_DAYS, DEFAULT_RETENTION_DAYS),
            ): int,
            vol.Required(
                CONF_ENABLE_DIAGNOSTICS,
                default=defaults.get(CONF_ENABLE_DIAGNOSTICS, DEFAULT_ENABLE_DIAGNOSTICS),
            ): bool,
        }
    )


if hasattr(config_entries, "ConfigFlow"):

    class SmartHomePresenceConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
        """Handle the initial config flow for the integration."""

        VERSION = 1

        async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
            """Handle the user-intro step."""

            if user_input is not None:
                return self.async_create_entry(title=NAME, data={}, options=user_input)

            return self.async_show_form(step_id="user", data_schema=_schema())


    class SmartHomePresenceOptionsFlow(config_entries.OptionsFlow):  # type: ignore[misc]
        """Handle options updates for an existing config entry."""

        def __init__(self, config_entry: Any) -> None:
            self._config_entry = config_entry

        async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
            """Present the options form."""

            if user_input is not None:
                return self.async_create_entry(title="", data=user_input)

            defaults = dict(self._config_entry.options)
            return self.async_show_form(step_id="init", data_schema=_schema(defaults))


    async def async_get_options_flow(config_entry: Any) -> SmartHomePresenceOptionsFlow:
        """Return the options flow handler."""

        return SmartHomePresenceOptionsFlow(config_entry)

