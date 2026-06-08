"""Color scene routing helpers for phase 1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ColorLightingProfile:
    """Room-specific color and white light groups."""

    room_id: str
    supports_color: bool
    color_groups: tuple[str, ...]
    white_groups: tuple[str, ...]


def should_sync_color_scene(requested_scene_type: str, profile: ColorLightingProfile) -> bool:
    """Return True when a scene request should target color-capable lights."""

    return requested_scene_type == "color" and profile.supports_color and bool(profile.color_groups)


def select_color_groups(profile: ColorLightingProfile) -> tuple[str, ...]:
    """Return the target groups for a color scene."""

    if not profile.supports_color:
        return ()
    return profile.color_groups


def build_color_sync_plan(
    profile: ColorLightingProfile,
    *,
    requested_scene_type: str,
) -> dict[str, object]:
    """Build the color-sync routing plan for a room."""

    if not should_sync_color_scene(requested_scene_type, profile):
        return {
            "room_id": profile.room_id,
            "sync_color": False,
            "target_groups": (),
            "white_groups": profile.white_groups,
        }

    return {
        "room_id": profile.room_id,
        "sync_color": True,
        "target_groups": select_color_groups(profile),
        "white_groups": profile.white_groups,
    }
