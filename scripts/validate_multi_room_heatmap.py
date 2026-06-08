#!/usr/bin/env python3
"""Validate the multi-room heatmap slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/multi_room_heatmap.yaml",
    ROOT / "docs/contracts/multi-room-heatmap.md",
    ROOT / "src/smart_home_presence_intelligence/multi_room_heatmap.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing multi-room heatmap files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/multi_room_heatmap.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "behavior: deterministic_multi_room_heatmap",
        "planning_only: true",
        "no_actuation",
        "no_room_control",
        "no_light_control",
        "no_schedule_writes",
        "observations",
        "room_reference_required: true",
        "supports_occupancy_required: true",
        "ignore_non_occupancy_rooms: true",
        "report_record_type: room_heatmap",
        "record_name: multi_room_heatmap",
        "report_status: ready",
        "retention_days: 90",
        "immutable: true",
    ):
        if needle not in text:
            raise SystemExit(f"multi_room_heatmap.yaml missing required text: {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.multi_room_heatmap import (  # noqa: E501
        MULTI_ROOM_HEATMAP_RECORD_NAME,
        MULTI_ROOM_HEATMAP_RECORD_TYPE,
        MULTI_ROOM_HEATMAP_REPORT_STATUS,
        MULTI_ROOM_HEATMAP_RETENTION_DAYS,
        MULTI_ROOM_HEATMAP_SOURCE,
        build_multi_room_heatmap_report,
    )

    observations = [
        {
            "room_id": "hall",
            "source": "mmwave",
            "confidence": 0.9,
            "ts": "2026-06-08T09:00:00+10:00",
        },
        {
            "room_id": "hall",
            "source": "motion",
            "confidence": 0.8,
            "ts": "2026-06-08T09:01:00+10:00",
        },
        {
            "room_id": "kitchen",
            "source": "frigate",
            "confidence": 0.7,
            "ts": "2026-06-08T09:02:00+10:00",
        },
        {
            "room_id": "driveway",
            "source": "anpr",
            "confidence": 1.0,
            "ts": "2026-06-08T09:03:00+10:00",
        },
    ]

    report = build_multi_room_heatmap_report(observations)
    if report is None:
        raise SystemExit("occupancy observations should create a heatmap report")
    if report["source"] != MULTI_ROOM_HEATMAP_SOURCE:
        raise SystemExit("heatmap report should use canonical source")
    if report["report_record_type"] != MULTI_ROOM_HEATMAP_RECORD_TYPE:
        raise SystemExit("heatmap report should use canonical record type")
    if report["record_name"] != MULTI_ROOM_HEATMAP_RECORD_NAME:
        raise SystemExit("heatmap report should use canonical record name")
    if report["report_status"] != MULTI_ROOM_HEATMAP_REPORT_STATUS:
        raise SystemExit("heatmap report should be ready for review")

    cells = report["heatmap_cells"]
    if [cell["room"] for cell in cells] != ["hall", "kitchen"]:
        raise SystemExit("heatmap should only include occupancy-supporting rooms")
    if cells[0]["observation_count"] != 2:
        raise SystemExit("hall should aggregate two observations")
    if cells[1]["observation_count"] != 1:
        raise SystemExit("kitchen should aggregate one observation")
    if cells[0]["heat_level"] != 2:
        raise SystemExit("hall heat level should match observation count")
    if cells[1]["sources"] != ["frigate"]:
        raise SystemExit("kitchen sources should preserve provenance")
    if report["summary"]["room_count"] != 2:
        raise SystemExit("summary should report the number of rooms included")
    if report["summary"]["observation_count"] != 3:
        raise SystemExit("summary should count included observations only")

    retention = report.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 90:
        raise SystemExit("heatmap report should include 90-day retention")
    if retention.get("immutable") is not True:
        raise SystemExit("heatmap retention should be immutable")
    if MULTI_ROOM_HEATMAP_RETENTION_DAYS != 90:
        raise SystemExit("heatmap retention constant should be 90 days")

    repeated = build_multi_room_heatmap_report(observations)
    if repeated != report:
        raise SystemExit("identical observations should yield identical reports")

    ignored_only = build_multi_room_heatmap_report(
        [
            {
                "room_id": "driveway",
                "source": "anpr",
                "confidence": 1.0,
                "ts": "2026-06-08T09:03:00+10:00",
            }
        ]
    )
    if ignored_only is not None:
        raise SystemExit("non-occupancy-only observations should not create a report")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_multi_room_heatmap.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Multi-room heatmap check passed"
        if sys.argv[1] == "check"
        else "Multi-room heatmap quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
