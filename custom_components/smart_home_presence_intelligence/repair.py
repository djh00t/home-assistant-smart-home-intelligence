"""Repair issues for the integration."""

from __future__ import annotations

from typing import Any

try:  # pragma: no cover - Home Assistant is not installed locally.
    from homeassistant.components.repairs import RepairsFlow, RepairsIssueSeverity
except ImportError:  # pragma: no cover
    RepairsFlow = object  # type: ignore[assignment]
    RepairsIssueSeverity = object  # type: ignore[assignment]


class ContractMismatchRepairFlow:  # pragma: no cover - HA runtime only
    """Expose a repair issue when runtime contracts drift from the repo bundle."""

    severity = getattr(RepairsIssueSeverity, "WARNING", "warning")

    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> dict[str, Any]:
        """Report a simple repair summary."""

        return {
            "type": "create_issue",
            "severity": self.severity,
            "translation_key": "contract_mismatch",
            "data": self.data,
        }

