#!/usr/bin/env python3
"""Validate the pram walking-vs-driving classifier slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/pram_walking_vs_driving.yaml",
    ROOT / "docs/contracts/pram-walking-vs-driving.md",
    ROOT / "src/smart_home_presence_intelligence/pram_walking_vs_driving.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing pram walking-vs-driving files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/pram_walking_vs_driving.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "scope:",
        "deterministic_classification",
        "backlog_boundary:",
        "no_lock_or_unlock_behavior",
        "no_garage_door_actuation",
        "no_anpr_only_logic",
        "no_vehicle_person_linking",
        "vehicle_context_window_seconds: 90",
        "with_pram_false: not_pram",
        "with_pram_true_match_within_window: drive",
        "with_pram_true_no_match_or_stale: walk",
        "transport_mode",
        "not_pram",
    ):
        if needle not in text:
            raise SystemExit(
                f"pram_walking_vs_driving.yaml missing required text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.pram_walking_vs_driving import (  # noqa: E501
        DRIVING_CLASSIFICATION,
        NOT_PRAM_CLASSIFICATION,
        WALKING_CLASSIFICATION,
        classify_pram_transport,
        VEHICLE_CONTEXT_WINDOW_SECONDS,
    )

    walk = classify_pram_transport(
        {
            "person_id": "sel",
            "room_id": "driveway",
            "with_pram": True,
            "vehicle_context_age_seconds": 120,
        }
    )
    if walk["transport_mode"] != WALKING_CLASSIFICATION:
        raise SystemExit("pram snapshot with stale vehicle context should classify walk")
    if walk.get("room") != "driveway" or walk.get("person_id") != "sel":
        raise SystemExit("pram transport plan should preserve room and person when present")

    drive = classify_pram_transport(
        {
            "person_id": "sel",
            "room": "driveway",
            "with_pram": True,
            "vehicle_context_age_seconds": 30,
        }
    )
    if drive["transport_mode"] != DRIVING_CLASSIFICATION:
        raise SystemExit("pram snapshot with recent matching vehicle context should classify drive")

    not_pram = classify_pram_transport({"room": "kitchen", "with_pram": False})
    if not_pram["transport_mode"] != NOT_PRAM_CLASSIFICATION:
        raise SystemExit("non-pram snapshot should classify as not_pram")

    if not_pram["context"]["vehicle_context_age_seconds"] is not None:
        raise SystemExit("missing vehicle_context_age_seconds should be None in context")

    if VEHICLE_CONTEXT_WINDOW_SECONDS != 90:
        raise SystemExit("vehicle context window should be exactly 90 seconds")

    try:
        classify_pram_transport({"room_id": "lounge_room", "with_pram": "yes"})
    except ValueError:
        pass
    else:
        raise SystemExit("non-boolean with_pram should be rejected")

    try:
        classify_pram_transport(
            {
                "room_id": "lounge_room",
                "with_pram": True,
                "vehicle_context_age_seconds": "10",
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("non-numeric vehicle_context_age_seconds should be rejected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_pram_walking_vs_driving.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Pram walking-vs-driving check passed"
        if sys.argv[1] == "check"
        else "Pram walking-vs-driving quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
