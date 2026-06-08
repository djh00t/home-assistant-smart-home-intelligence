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

    bedroom_spare = ColorLightingProfile(
        room_id="bedroom_spare",
        supports_color=True,
        color_groups=("bedroom_spare_desk",),
        white_groups=("bedroom_spare_ceiling",),
    )
    lounge_room = ColorLightingProfile(
        room_id="lounge_room",
        supports_color=False,
        color_groups=(),
        white_groups=("lounge_room_ceiling",),
    )

    if not should_sync_color_scene("color", bedroom_spare):
        raise SystemExit("bedroom_spare should sync color scenes")
    if should_sync_color_scene("white", bedroom_spare):
        raise SystemExit("white scene should not trigger color sync")
    if should_sync_color_scene("color", lounge_room):
        raise SystemExit("lounge_room should not sync color scenes")
    if select_color_groups(lounge_room) != ():
        raise SystemExit("white-only room should not expose color groups")

    bedroom_spare_plan = build_color_sync_plan(bedroom_spare, requested_scene_type="color")
    if not bedroom_spare_plan["sync_color"] or bedroom_spare_plan["target_groups"] != ("bedroom_spare_desk",):
        raise SystemExit("bedroom_spare color sync plan failed")

    lounge_room_plan = build_color_sync_plan(lounge_room, requested_scene_type="color")
    if lounge_room_plan["sync_color"] or lounge_room_plan["target_groups"] != ():
        raise SystemExit("lounge_room should not build a color sync plan")


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
