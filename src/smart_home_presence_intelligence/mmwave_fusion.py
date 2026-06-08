"""MmWave and Frigate room fusion helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass

from .room_fsm import RoomSnapshot, evaluate_room_state


@dataclass(frozen=True, slots=True)
class MmWaveFusionSnapshot:
    """Minimal inputs used by the fusion template."""

    room_id: str
    mmwave_active: bool
    frigate_track_present: bool
    sleeping: bool = False
    bed_motion_only: bool = False


def fused_room_state(snapshot: MmWaveFusionSnapshot) -> dict[str, object]:
    """Return the fused room state for a snapshot."""

    humans_present = 1 if snapshot.mmwave_active or snapshot.frigate_track_present else 0
    room_snapshot = RoomSnapshot(
        room_id=snapshot.room_id,
        humans_present=humans_present,
        pets_present=0,
        sleeping=snapshot.sleeping,
        bed_motion_only=snapshot.bed_motion_only,
    )
    occupancy_mode = evaluate_room_state(room_snapshot)

    if snapshot.mmwave_active and snapshot.frigate_track_present:
        confidence = 0.95
        primary_source = "mmwave+frigate"
    elif snapshot.mmwave_active:
        confidence = 0.9
        primary_source = "mmwave"
    elif snapshot.frigate_track_present:
        confidence = 0.65
        primary_source = "frigate"
    else:
        confidence = 0.0
        primary_source = "none"

    return {
        "room_id": snapshot.room_id,
        "occupancy_mode": occupancy_mode,
        "room_mode": occupancy_mode,
        "primary_source": primary_source,
        "confidence": confidence,
    }


def should_keep_room_present(snapshot: MmWaveFusionSnapshot) -> bool:
    """Return True when the fused signal should keep the room occupied."""

    return snapshot.mmwave_active or snapshot.frigate_track_present
