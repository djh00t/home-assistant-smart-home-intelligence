#!/usr/bin/env python3
"""Validate the room presence FSM slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FSM_FILES = [
    ROOT / "config/contracts/room_fsm.yaml",
    ROOT / "docs/contracts/room-fsm-template.md",
    ROOT / "src/smart_home_presence_intelligence/room_fsm.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FSM_FILES if not path.exists()]
    if missing:
        print("Missing room FSM files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/room_fsm.yaml").read_text(encoding="utf-8")
    for needle in (
        "sleeping",
        "bed_motion_only",
        "humans_only",
        "pets_only",
        "mixed",
    ):
        if needle not in text:
            raise SystemExit(f"room_fsm.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.room_fsm import RoomSnapshot, advance_room_state, evaluate_room_state  # noqa: E501, WPS433

    if evaluate_room_state(RoomSnapshot("room_delta", 1, 0)) != "humans_only":
        raise SystemExit("humans_only state failed")
    if evaluate_room_state(RoomSnapshot("room_epsilon", 0, 1)) != "pets_only":
        raise SystemExit("pets_only state failed")
    if evaluate_room_state(RoomSnapshot("room_delta", 1, 1)) != "mixed":
        raise SystemExit("mixed state failed")
    if evaluate_room_state(RoomSnapshot("room_alpha", 1, 0, sleeping=True)) != "sleeping":
        raise SystemExit("sleeping state failed")
    if evaluate_room_state(RoomSnapshot("room_alpha", 1, 0, sleeping=True, bed_motion_only=True)) != "bed_motion_only":
        raise SystemExit("bed_motion_only state failed")
    if advance_room_state(
        "sleeping", RoomSnapshot("room_alpha", 1, 0, sleeping=True, bed_motion_only=True)
    ) != "bed_motion_only":
        raise SystemExit("bed_motion_only transition failed")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_room_fsm.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Room FSM check passed"
        if sys.argv[1] == "check"
        else "Room FSM quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
