"""Arrival-zone setup contract helpers for phase 0."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import yaml


DRIVEWAY_ZONE_ID = "zone_alpha"
INVALID_ZONE_MESSAGE = f"unsupported arrival zone: expected '{DRIVEWAY_ZONE_ID}'"
SETUP_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "contracts" / "driveway_zone_setup.yaml"
)


_DEFAULT_DIRECTION_MAP = {
    "enter": "arrival",
    "entered": "arrival",
    "in": "arrival",
    "exit": "departure",
    "exited": "departure",
    "out": "departure",
    "stay": "stationary",
    "stationary": "stationary",
}


def _read_setup_payload(path: Path) -> dict[str, Any]:
    """Read the arrival-zone setup contract from YAML."""

    with path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("arrival-zone setup contract must be a mapping")
    return payload


def load_driveway_zone_setup(path: Path | None = None) -> dict[str, Any]:
    """
    Load arrival-zone setup contract defaults.

    The optional ``path`` argument is accepted for forward compatibility with future
    contract loaders and test wiring.
    """

    contract_path = path or SETUP_PATH
    payload = _read_setup_payload(contract_path)
    return deepcopy(payload)


def resolve_driveway_zone(zone_id: str) -> dict[str, Any]:
    """
    Return the canonical arrival-zone setup.

    Raises:
        ValueError: when the zone_id is not the canonical arrival-zone id.
    """

    setup = load_driveway_zone_setup()
    normalized_zone_id = zone_id.strip().lower()
    canonical_zone = setup.get("zone", {}).get("canonical_room_id")
    if canonical_zone is not None and normalized_zone_id != str(canonical_zone):
        raise ValueError(INVALID_ZONE_MESSAGE)
    if normalized_zone_id != DRIVEWAY_ZONE_ID:
        raise ValueError(INVALID_ZONE_MESSAGE)
    return setup


def normalize_driveway_direction(direction: str | None) -> str:
    """Normalize arrival-zone direction semantics for planning and routing."""

    if direction is None:
        return "stationary"

    raw_direction = str(direction).strip().lower()
    setup = load_driveway_zone_setup()
    mapping = setup.get("direction", {}).get("raw_direction_map", {})
    normalized = mapping.get(raw_direction, "stationary")
    return str(normalized)


def validate_driveway_reference(event: Mapping[str, Any]) -> bool:
    """
    Validate the arrival-zone reference in a setup-facing payload.

    Returns False when room_id is missing or not canonical.
    """

    room_id = event.get("room_id") or event.get("room") or event.get("zone_id")
    if room_id is None:
        return False

    normalized_room_id = str(room_id).strip().lower()
    return normalized_room_id == DRIVEWAY_ZONE_ID
