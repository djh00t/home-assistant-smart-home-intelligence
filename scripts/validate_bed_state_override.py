#!/usr/bin/env python3
"""Validate the bed-state override slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/bed_state_override.yaml",
    ROOT / "docs/contracts/bed-state-override.md",
    ROOT / "src/smart_home_presence_intelligence/bed_state_override.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing bed-state override files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/bed_state_override.yaml").read_text(encoding="utf-8")
    for needle in (
        "awake",
        "sleeping",
        "bed_motion_only",
        "suppress_wake_scene_while_bed_motion_only: true",
        "suppress_wake_scene_while_sleeping: true",
        "clear_override_on_exit_event: true",
    ):
        if needle not in text:
            raise SystemExit(f"bed_state_override.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.bed_state_override import BedStateSnapshot, build_bed_override, resolve_bed_state, should_suppress_wake_scene  # noqa: E501, WPS433

    sleeping = BedStateSnapshot("master_bedroom", in_bed=True, bed_motion_active=False)
    motion = BedStateSnapshot("master_bedroom", in_bed=True, bed_motion_active=True)
    awake = BedStateSnapshot("master_bedroom", in_bed=False, bed_motion_active=False)
    exit_event = BedStateSnapshot("master_bedroom", in_bed=True, bed_motion_active=True, exit_event=True)

    if resolve_bed_state(sleeping) != "sleeping":
        raise SystemExit("sleeping state failed")
    if resolve_bed_state(motion) != "bed_motion_only":
        raise SystemExit("bed_motion_only state failed")
    if resolve_bed_state(awake) != "awake":
        raise SystemExit("awake state failed")
    if resolve_bed_state(exit_event) != "awake":
        raise SystemExit("exit event should clear override")
    if not should_suppress_wake_scene(sleeping):
        raise SystemExit("sleeping should suppress wake scene")
    if not should_suppress_wake_scene(motion):
        raise SystemExit("bed_motion_only should suppress wake scene")
    if should_suppress_wake_scene(awake):
        raise SystemExit("awake should not suppress wake scene")
    plan = build_bed_override(motion)
    if plan["state"] != "bed_motion_only" or not plan["suppress_wake_scene"]:
        raise SystemExit("bed override plan failed")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_bed_state_override.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Bed state override check passed"
        if sys.argv[1] == "check"
        else "Bed state override quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
