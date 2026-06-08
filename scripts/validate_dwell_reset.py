#!/usr/bin/env python3
"""Validate the dwell reset automation slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/dwell_reset.yaml",
    ROOT / "docs/contracts/dwell-reset-automation.md",
    ROOT / "src/smart_home_presence_intelligence/dwell_reset.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing dwell reset files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/dwell_reset.yaml").read_text(encoding="utf-8")
    for needle in ("motion", "mmwave", "frigate", "restart_timer", "dim", "off"):
        if needle not in text:
            raise SystemExit(f"dwell_reset.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.dwell_reset import DwellTimer, restart_dwell_timer, should_restart_dwell  # noqa: E501, WPS433

    motion_event = {"source": "motion", "type": "enter"}
    if not should_restart_dwell(motion_event):
        raise SystemExit("motion event should restart dwell")

    timer = DwellTimer("hall", 300, 120)
    restarted = restart_dwell_timer(timer, motion_event)
    if restarted.remaining_seconds != 300:
        raise SystemExit("dwell timer did not restart to duration")
    if restarted.restart_count != 1:
        raise SystemExit("dwell timer restart count did not increment")

    foreign_event = {"source": "anpr", "type": "enter"}
    if should_restart_dwell(foreign_event):
        raise SystemExit("foreign event should not restart dwell")
    if restart_dwell_timer(timer, foreign_event) != timer:
        raise SystemExit("non-trigger event should not change timer")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_dwell_reset.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Dwell reset check passed"
        if sys.argv[1] == "check"
        else "Dwell reset quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
