"""Deterministic desk-light profile helpers for phase 0."""

from __future__ import annotations

from typing import Any, Mapping


def _desk_profile_for_person(person_id: str, desk_profiles: object) -> str | None:
    """Return the mapped desk-light profile for a person when available."""

    if not isinstance(desk_profiles, Mapping):
        return None

    profile = desk_profiles.get(person_id)
    if not isinstance(profile, str) or not profile:
        return None
    return profile


def resolve_desk_light_profile(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve the desk-light profile plan for a person-room assignment snapshot."""

    room_id = snapshot["room_id"]
    assigned_person = snapshot.get("assigned_person")
    assignment_source = snapshot.get("assignment_source")
    confidence = snapshot.get("confidence")
    desk_profiles = snapshot.get("desk_profiles")

    desk_light_profile = None
    should_apply = False

    if room_id == "bedroom_spare" and isinstance(assigned_person, str) and assigned_person:
        desk_light_profile = _desk_profile_for_person(assigned_person, desk_profiles)
        should_apply = desk_light_profile is not None

    return {
        "room_id": room_id,
        "assigned_person": assigned_person,
        "assignment_source": assignment_source,
        "confidence": confidence,
        "desk_profiles": desk_profiles,
        "desk_light_profile": desk_light_profile,
        "should_apply": should_apply,
    }

