"""House mode helpers for phase 0 pet-only occupancy."""

from __future__ import annotations

from dataclasses import dataclass


HOUSE_MODES = ("empty", "pet_mode", "occupied")


@dataclass(frozen=True, slots=True)
class HouseModeSnapshot:
    """Minimal inputs for house mode selection."""

    humans_present: int
    pets_present: int


def select_house_mode(snapshot: HouseModeSnapshot) -> str:
    """Return the canonical house mode for a snapshot."""

    if snapshot.humans_present > 0:
        return "occupied"
    if snapshot.pets_present > 0:
        return "pet_mode"
    return "empty"


def should_allow_pathway_lighting(snapshot: HouseModeSnapshot) -> bool:
    """Return True when pet-only pathway lighting may remain active."""

    return select_house_mode(snapshot) == "pet_mode"


def build_house_mode_plan(snapshot: HouseModeSnapshot) -> dict[str, object]:
    """Build the house-mode routing plan."""

    mode = select_house_mode(snapshot)
    return {
        "mode": mode,
        "pathway_lighting_allowed": should_allow_pathway_lighting(snapshot),
    }
