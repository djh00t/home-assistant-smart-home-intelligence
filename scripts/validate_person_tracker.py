#!/usr/bin/env python3
"""Validate the person tracker integration slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/person_tracker.yaml",
    ROOT / "docs/contracts/person-tracker-integration.md",
    ROOT / "src/smart_home_presence_intelligence/person_tracker.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing person tracker files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/person_tracker.yaml").read_text(encoding="utf-8")
    for needle in (
        "mobile_app",
        "ble",
        "geofencing",
        "home",
        "not_home",
        "arriving",
        "leaving",
    ):
        if needle not in text:
            raise SystemExit(f"person_tracker.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.person_tracker import build_tracker_presence_event, normalize_tracker_signal  # noqa: E501, WPS433

    signal = {
        "tracker_id": "sel_phone",
        "person_id": "sel",
        "source": "mobile_app",
        "state": "home",
        "confidence": 0.95,
    }
    normalized = normalize_tracker_signal(signal)
    if normalized["source"] != "mobile_app" or normalized["state"] != "home":
        raise SystemExit("tracker normalization failed")

    event = build_tracker_presence_event(signal)
    if event["source"] != "tracker" or event["person_id"] != "sel":
        raise SystemExit("tracker event build failed")
    if event["room"] != "house":
        raise SystemExit("tracker event should default to house room")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_person_tracker.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Person tracker check passed"
        if sys.argv[1] == "check"
        else "Person tracker quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
