"""Diagnostics support for the integration."""

from __future__ import annotations

from typing import Any

from . import runtime_snapshot
from .const import DOMAIN


async def async_get_config_entry_diagnostics(hass: Any, entry: Any) -> dict[str, Any]:
    """Return a redacted diagnostics payload."""

    return {
        DOMAIN: runtime_snapshot(hass, entry.entry_id),
    }

