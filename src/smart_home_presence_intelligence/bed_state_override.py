"""Bed-state override helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass


BED_STATES = ("awake", "sleeping", "bed_motion_only")


@dataclass(frozen=True, slots=True)
class BedStateSnapshot:
    """Minimal bed-state inputs used by the override template."""

    room_id: str
    in_bed: bool
    bed_motion_active: bool
    exit_event: bool = False


def resolve_bed_state(snapshot: BedStateSnapshot) -> str:
    """Return the canonical bed-state for a snapshot."""

    if snapshot.exit_event:
        return "awake"
    if snapshot.room_id == "bedroom_master" and snapshot.in_bed and snapshot.bed_motion_active:
        return "bed_motion_only"
    if snapshot.room_id == "bedroom_master" and snapshot.in_bed:
        return "sleeping"
    return "awake"


def should_suppress_wake_scene(snapshot: BedStateSnapshot) -> bool:
    """Return True when wake scenes should stay suppressed."""

    return resolve_bed_state(snapshot) in {"sleeping", "bed_motion_only"}


def build_bed_override(snapshot: BedStateSnapshot) -> dict[str, object]:
    """Build the bed-state override routing plan."""

    state = resolve_bed_state(snapshot)
    return {
        "room_id": snapshot.room_id,
        "state": state,
        "suppress_wake_scene": should_suppress_wake_scene(snapshot),
    }
