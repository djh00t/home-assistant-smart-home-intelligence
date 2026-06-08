#!/usr/bin/env python3
"""Validate the mmWave fusion slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/mmwave_fusion.yaml",
    ROOT / "docs/contracts/mmwave-fusion-rule.md",
    ROOT / "src/smart_home_presence_intelligence/mmwave_fusion.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing mmWave fusion files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/mmwave_fusion.yaml").read_text(encoding="utf-8")
    for needle in (
        "mmwave",
        "frigate",
        "mmwave_takes_priority_for_room_presence: true",
        "frigate_provides_continuity_only: true",
        "fused_room_state_drives_room_automation: true",
    ):
        if needle not in text:
            raise SystemExit(f"mmwave_fusion.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.mmwave_fusion import MmWaveFusionSnapshot, fused_room_state, should_keep_room_present  # noqa: E501, WPS433

    both = MmWaveFusionSnapshot("hall", True, True)
    mmwave_only = MmWaveFusionSnapshot("hall", True, False)
    frigate_only = MmWaveFusionSnapshot("hall", False, True)
    none = MmWaveFusionSnapshot("hall", False, False)
    sleeping = MmWaveFusionSnapshot("master_bedroom", True, True, sleeping=True)
    bed_motion = MmWaveFusionSnapshot("master_bedroom", True, True, sleeping=True, bed_motion_only=True)

    if fused_room_state(both)["confidence"] != 0.95:
        raise SystemExit("mmwave+frigate confidence failed")
    if fused_room_state(mmwave_only)["primary_source"] != "mmwave":
        raise SystemExit("mmwave-only fusion failed")
    if fused_room_state(frigate_only)["primary_source"] != "frigate":
        raise SystemExit("frigate-only fusion failed")
    if fused_room_state(none)["occupancy_mode"] != "empty":
        raise SystemExit("empty fusion failed")
    if fused_room_state(sleeping)["room_mode"] != "sleeping":
        raise SystemExit("sleeping fusion failed")
    if fused_room_state(bed_motion)["room_mode"] != "bed_motion_only":
        raise SystemExit("bed motion fusion failed")
    if not should_keep_room_present(frigate_only):
        raise SystemExit("frigate continuity should keep room present")
    if should_keep_room_present(none):
        raise SystemExit("empty room should not stay present")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_mmwave_fusion.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "MmWave fusion check passed"
        if sys.argv[1] == "check"
        else "MmWave fusion quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
