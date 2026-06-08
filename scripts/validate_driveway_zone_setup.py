#!/usr/bin/env python3
"""Validate the driveway zone setup slice."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/driveway_zone_setup.yaml",
    ROOT / "docs/contracts/driveway-zone-setup.md",
    ROOT / "src/smart_home_presence_intelligence/driveway_zone_setup.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing driveway zone setup files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/driveway_zone_setup.yaml").read_text(encoding="utf-8")
    for needle in (
        "zone_id: driveway",
        "canonical_room_id: driveway",
        "canonical_source_priority:",
        "- anpr",
        "- frigate",
        "- face",
        "canonical_inbound: arrival",
        "canonical_outbound: departure",
        "canonical_resident: stationary",
        "canonical_room_reference_required: true",
        "behavior_scope: setup_planning_only",
    ):
        if needle not in text:
            raise SystemExit(f"driveway_zone_setup.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.driveway_zone_setup import (  # noqa: E501
        DRIVEWAY_ZONE_ID,
        load_driveway_zone_setup,
        normalize_driveway_direction,
        resolve_driveway_zone,
        validate_driveway_reference,
    )

    setup = load_driveway_zone_setup()
    zone = setup.get("zone", {})
    if zone.get("room_id") != DRIVEWAY_ZONE_ID:
        raise SystemExit("setup room_id must be driveway")
    if zone.get("canonical_room_id") != DRIVEWAY_ZONE_ID:
        raise SystemExit("setup canonical_room_id must be driveway")

    resolve_driveway_zone(DRIVEWAY_ZONE_ID)
    try:
        resolve_driveway_zone("driveway_zone")
    except ValueError:
        pass
    else:  # pragma: no cover - explicit defensive branch
        raise SystemExit("non-canonical driveway zone should fail resolution")

    if normalize_driveway_direction("enter") != "arrival":
        raise SystemExit("enter direction should normalize to arrival")
    if normalize_driveway_direction("exit") != "departure":
        raise SystemExit("exit direction should normalize to departure")
    if normalize_driveway_direction("unknown") != "stationary":
        raise SystemExit("unknown direction should normalize to stationary")

    if not validate_driveway_reference({"room": "driveway"}):
        raise SystemExit("canonical driveway reference should validate")
    if validate_driveway_reference({"room_id": "garage"}):
        raise SystemExit("non-driveway reference should not validate")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_driveway_zone_setup.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Driveway zone setup check passed"
        if sys.argv[1] == "check"
        else "Driveway zone setup quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
