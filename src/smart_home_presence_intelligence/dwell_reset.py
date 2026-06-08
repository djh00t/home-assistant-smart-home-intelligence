"""Dwell timer restart helpers for phase 1."""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Mapping, Any


TRIGGER_SOURCES = ("motion", "mmwave", "frigate")
TRIGGER_EVENTS = ("enter", "stay", "state_change")


@dataclass(frozen=True, slots=True)
class DwellTimer:
    """Minimal dwell timer state used by the template."""

    room_id: str
    duration_seconds: int
    remaining_seconds: int
    restart_count: int = 0


def should_restart_dwell(event: Mapping[str, Any]) -> bool:
    """Return True when a raw event should restart a dwell timer."""

    source = str(event.get("source", ""))
    event_type = str(event.get("type", ""))
    return source in TRIGGER_SOURCES and event_type in TRIGGER_EVENTS


def restart_dwell_timer(timer: DwellTimer, event: Mapping[str, Any]) -> DwellTimer:
    """Restart a dwell timer when the triggering conditions are met."""

    if not should_restart_dwell(event):
        return timer
    return replace(
        timer,
        remaining_seconds=timer.duration_seconds,
        restart_count=timer.restart_count + 1,
    )
