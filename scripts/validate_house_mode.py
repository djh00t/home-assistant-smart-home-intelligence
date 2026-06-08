#!/usr/bin/env python3
"""Validate the house mode slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/house_mode.yaml",
    ROOT / "docs/contracts/empty-house-with-pet-mode-switch.md",
    ROOT / "src/smart_home_presence_intelligence/house_mode.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing house mode files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/house_mode.yaml").read_text(encoding="utf-8")
    for needle in (
        "empty",
        "pet_mode",
        "occupied",
        "pets_only_selects_pet_mode: true",
        "humans_present_forces_occupied: true",
        "pet_mode_may_keep_pathway_lighting: true",
    ):
        if needle not in text:
            raise SystemExit(f"house_mode.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.house_mode import HouseModeSnapshot, build_house_mode_plan, select_house_mode, should_allow_pathway_lighting  # noqa: E501, WPS433

    empty = HouseModeSnapshot(0, 0)
    pet_mode = HouseModeSnapshot(0, 1)
    occupied = HouseModeSnapshot(1, 1)

    if select_house_mode(empty) != "empty":
        raise SystemExit("empty mode failed")
    if select_house_mode(pet_mode) != "pet_mode":
        raise SystemExit("pet_mode selection failed")
    if select_house_mode(occupied) != "occupied":
        raise SystemExit("occupied selection failed")
    if not should_allow_pathway_lighting(pet_mode):
        raise SystemExit("pet_mode should allow pathway lighting")
    if should_allow_pathway_lighting(empty):
        raise SystemExit("empty house should not allow pathway lighting")
    plan = build_house_mode_plan(pet_mode)
    if plan["mode"] != "pet_mode" or not plan["pathway_lighting_allowed"]:
        raise SystemExit("house mode plan failed")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_house_mode.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "House mode check passed"
        if sys.argv[1] == "check"
        else "House mode quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
