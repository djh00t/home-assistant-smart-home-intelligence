#!/usr/bin/env python3
"""Validate the adaptive white-lighting slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/white_lighting.yaml",
    ROOT / "docs/contracts/adaptive-white-lighting.md",
    ROOT / "src/smart_home_presence_intelligence/white_lighting.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing white-lighting files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/white_lighting.yaml").read_text(encoding="utf-8")
    for needle in (
        "manual_override_suppresses_auto_on: true",
        "bed_motion_only_never_full_brightens: true",
        "preserve_hue_temperature_policy: true",
        "morning",
        "day",
        "evening",
        "night",
    ):
        if needle not in text:
            raise SystemExit(f"white_lighting.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.white_lighting import (  # noqa: WPS433
        WhiteLightingProfile,
        circadian_period,
        select_white_scene,
        should_apply_white_lights,
        should_full_brighten,
    )

    profile = WhiteLightingProfile(
        room_id="room_delta",
        day_scene="room_delta_day",
        evening_scene="room_delta_evening",
        night_scene="room_delta_night",
        white_groups=("room_delta_ceiling",),
    )

    if circadian_period(6) != "morning":
        raise SystemExit("morning period failed")
    if circadian_period(13) != "day":
        raise SystemExit("day period failed")
    if circadian_period(18) != "evening":
        raise SystemExit("evening period failed")
    if circadian_period(22) != "night":
        raise SystemExit("night period failed")

    if select_white_scene(profile, hour=13, room_mode="humans_only") != "room_delta_day":
        raise SystemExit("day scene selection failed")
    if select_white_scene(profile, hour=18, room_mode="humans_only") != "room_delta_evening":
        raise SystemExit("evening scene selection failed")
    if select_white_scene(profile, hour=22, room_mode="humans_only") != "room_delta_night":
        raise SystemExit("night scene selection failed")
    if select_white_scene(profile, hour=13, room_mode="bed_motion_only") is not None:
        raise SystemExit("bed_motion_only should suppress auto-on")
    if select_white_scene(profile, hour=13, room_mode="humans_only", manual_override_active=True) is not None:
        raise SystemExit("manual override should suppress auto-on")
    if not should_apply_white_lights("humans_only"):
        raise SystemExit("humans_only should apply white lights")
    if should_apply_white_lights("sleeping"):
        raise SystemExit("sleeping should not apply white lights")
    if should_full_brighten("bed_motion_only"):
        raise SystemExit("bed_motion_only should not full brighten")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_white_lighting.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "White lighting check passed"
        if sys.argv[1] == "check"
        else "White lighting quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
