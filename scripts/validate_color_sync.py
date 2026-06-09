#!/usr/bin/env python3
"""Validate the color-sync slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/color_sync.yaml",
    ROOT / "docs/contracts/color-sync-for-color-lights.md",
    ROOT / "src/smart_home_presence_intelligence/color_sync.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing color-sync files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/color_sync.yaml").read_text(encoding="utf-8")
    for needle in (
        "color_scenes_only_target_color_capable_groups: true",
        "white_only_rooms_skip_color_sync: true",
        "preserve_white_lighting_for_color_scene_requests: true",
    ):
        if needle not in text:
            raise SystemExit(f"color_sync.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.color_sync import ColorLightingProfile, build_color_sync_plan, select_color_groups, should_sync_color_scene  # noqa: E501, WPS433

    room_gamma = ColorLightingProfile(
        room_id="room_gamma",
        supports_color=True,
        color_groups=("room_gamma_desk",),
        white_groups=("room_gamma_ceiling",),
    )
    room_delta = ColorLightingProfile(
        room_id="room_delta",
        supports_color=False,
        color_groups=(),
        white_groups=("room_delta_ceiling",),
    )

    if not should_sync_color_scene("color", room_gamma):
        raise SystemExit("room_gamma should sync color scenes")
    if should_sync_color_scene("white", room_gamma):
        raise SystemExit("white scene should not trigger color sync")
    if should_sync_color_scene("color", room_delta):
        raise SystemExit("room_delta should not sync color scenes")
    if select_color_groups(room_delta) != ():
        raise SystemExit("white-only room should not expose color groups")

    room_gamma_plan = build_color_sync_plan(room_gamma, requested_scene_type="color")
    if not room_gamma_plan["sync_color"] or room_gamma_plan["target_groups"] != ("room_gamma_desk",):
        raise SystemExit("room_gamma color sync plan failed")

    room_delta_plan = build_color_sync_plan(room_delta, requested_scene_type="color")
    if room_delta_plan["sync_color"] or room_delta_plan["target_groups"] != ():
        raise SystemExit("room_delta should not build a color sync plan")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_color_sync.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Color sync check passed"
        if sys.argv[1] == "check"
        else "Color sync quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
