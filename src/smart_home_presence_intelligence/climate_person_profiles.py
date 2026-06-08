"""Deterministic climate-person profile helpers for phase 0."""

from __future__ import annotations

from typing import Any, Mapping


def _climate_profile_for_person(person_id: str, climate_profiles: object) -> str | None:
    """Return the mapped climate profile for a person when available."""

    if not isinstance(climate_profiles, Mapping):
        return None

    profile = climate_profiles.get(person_id)
    if not isinstance(profile, str) or not profile:
        return None
    return profile


def resolve_climate_person_profile(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    """Resolve the climate profile plan for a person-room assignment snapshot."""

    room_id = snapshot["room_id"]
    assigned_person = snapshot.get("assigned_person")
    assignment_source = snapshot.get("assignment_source")
    confidence = snapshot.get("confidence")
    climate_profiles = snapshot.get("climate_profiles")

    climate_profile = None
    should_apply = False

    if isinstance(assigned_person, str) and assigned_person:
        climate_profile = _climate_profile_for_person(assigned_person, climate_profiles)
        should_apply = climate_profile is not None

    return {
        "room_id": room_id,
        "assigned_person": assigned_person,
        "assignment_source": assignment_source,
        "confidence": confidence,
        "climate_profiles": climate_profiles,
        "climate_profile": climate_profile,
        "should_apply": should_apply,
    }
