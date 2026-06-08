"""Adaptive white-lighting helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class WhiteLightingProfile:
    """Room-specific white-light policy inputs."""

    room_id: str
    day_scene: str
    evening_scene: str
    night_scene: str
    white_groups: tuple[str, ...]
    manual_override_minutes: int = 30


def circadian_period(hour: int) -> str:
    """Return the circadian period for a local hour."""

    if 5 <= hour <= 11:
        return "morning"
    if 12 <= hour <= 16:
        return "day"
    if 17 <= hour <= 20:
        return "evening"
    return "night"


def should_apply_white_lights(room_mode: str, manual_override_active: bool = False) -> bool:
    """Return True when the room should receive an automatic white-light update."""

    if manual_override_active:
        return False
    return room_mode not in {"sleeping", "bed_motion_only"}


def should_full_brighten(room_mode: str, manual_override_active: bool = False) -> bool:
    """Return True when the room may brighten to its active white scene."""

    return should_apply_white_lights(room_mode, manual_override_active)


def select_white_scene(
    profile: WhiteLightingProfile,
    *,
    hour: int,
    room_mode: str,
    manual_override_active: bool = False,
) -> str | None:
    """Select the white scene for a room based on the circadian period."""

    if not should_apply_white_lights(room_mode, manual_override_active):
        return None

    period = circadian_period(hour)
    if period in {"morning", "day"}:
        return profile.day_scene
    if period == "evening":
        return profile.evening_scene
    return profile.night_scene
