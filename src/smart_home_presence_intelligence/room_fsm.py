"""Room presence state machine helpers for phase 0."""

from __future__ import annotations

from dataclasses import dataclass


ROOM_STATES = (
    "empty",
    "humans_only",
    "pets_only",
    "mixed",
    "sleeping",
    "bed_motion_only",
)


@dataclass(frozen=True, slots=True)
class RoomSnapshot:
    """Minimal room state inputs used by the template."""

    room_id: str
    humans_present: int
    pets_present: int
    sleeping: bool = False
    bed_motion_only: bool = False


def evaluate_room_state(snapshot: RoomSnapshot) -> str:
    """Return the canonical room state for a snapshot."""

    if snapshot.room_id == "master_bedroom" and snapshot.sleeping:
        if snapshot.bed_motion_only:
            return "bed_motion_only"
        return "sleeping"

    if snapshot.humans_present > 0 and snapshot.pets_present > 0:
        return "mixed"
    if snapshot.humans_present > 0:
        return "humans_only"
    if snapshot.pets_present > 0:
        return "pets_only"
    return "empty"


def advance_room_state(current_state: str, snapshot: RoomSnapshot) -> str:
    """Return the next room state for a given snapshot."""

    next_state = evaluate_room_state(snapshot)
    if current_state == "sleeping" and snapshot.room_id == "master_bedroom" and snapshot.bed_motion_only:
        return "bed_motion_only"
    if current_state == "bed_motion_only" and snapshot.room_id == "master_bedroom" and snapshot.sleeping:
        return "sleeping"
    return next_state
