#!/usr/bin/env python3
"""Validate the multi-room heatmap slice."""

from __future__ import annotations

import hashlib
import json
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
        "retention_days: 14",
        "immutable: true",
        "report_id_digest: sha256_canonical_json",
        "report_id_format: multi_room_heatmap::sha256:{report_digest}",
        "report_id_raw_telemetry: false",
        "per_room_provenance_retained: false",
        "per_room_timestamp_detail: omitted",
        "report_level_input_timestamp_retained: false",
    ):
        if needle not in text:
            raise SystemExit(f"multi_room_heatmap.yaml missing required text: {needle}")

    doc_text = (ROOT / "docs/contracts/multi-room-heatmap.md").read_text(
        encoding="utf-8"
    )
    for needle in (
        "SHA-256 digest of canonicalized heatmap cells",
        "Per-room source provenance and per-room timestamps are excluded from retained heatmap cells",
        "Input-derived timestamps are not retained anywhere in the persisted report body",
        "Raw room telemetry fragments and timestamps must never appear in `report_id`",
        "multi_room_heatmap::sha256:{report_digest}",
        "Retention is capped at 14 days",
    ):
        if needle not in doc_text:
            raise SystemExit(
                f"multi-room-heatmap.md missing required privacy text: {needle}"
            )


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
            "room_id": "room_delta",
            "source": "mmwave",
            "confidence": 0.9,
            "ts": "2026-06-08T09:00:00+10:00",
        },
        {
            "room_id": "room_delta",
            "source": "motion",
            "confidence": 0.8,
            "ts": "2026-06-08T09:01:00+10:00",
        },
        {
            "room_id": "room_epsilon",
            "source": "frigate",
            "confidence": 0.7,
            "ts": "2026-06-08T09:02:00+10:00",
        },
        {
            "room_id": "zone_alpha",
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
    if [cell["room"] for cell in cells] != ["room_delta", "room_epsilon"]:
        raise SystemExit("heatmap should only include occupancy-supporting rooms")
    if cells[0]["observation_count"] != 2:
        raise SystemExit("room_delta should aggregate two observations")
    if cells[1]["observation_count"] != 1:
        raise SystemExit("room_epsilon should aggregate one observation")
    if cells[1]["heat_level"] != 1:
        raise SystemExit("room_epsilon heat level should match observation count")
    if "sources" in cells[0] or "sources" in cells[1]:
        raise SystemExit("heatmap cells should not retain per-room source provenance")
    if "latest_ts" in cells[0] or "latest_ts" in cells[1]:
        raise SystemExit("heatmap cells should not retain per-room timestamp detail")
    if report["summary"]["room_count"] != 2:
        raise SystemExit("summary should report the number of rooms included")
    if report["summary"]["observation_count"] != 3:
        raise SystemExit("summary should count included observations only")
    if "ts" in report:
        raise SystemExit("heatmap report should not retain an input-derived report timestamp")
    expected_report_id = "multi_room_heatmap::sha256:" + hashlib.sha256(
        json.dumps(cells, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if report["report_id"] != expected_report_id:
        raise SystemExit("report_id should use a deterministic sha256 digest")
    if "room_epsilon" in report["report_id"] or "2026-06-08" in report["report_id"]:
        raise SystemExit("report_id should not expose raw telemetry fragments")

    retention = report.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 14:
        raise SystemExit("heatmap report should include 14-day retention")
    if retention.get("immutable") is not True:
        raise SystemExit("heatmap retention should be immutable")
    if MULTI_ROOM_HEATMAP_RETENTION_DAYS != 14:
        raise SystemExit("heatmap retention constant should be 14 days")

    repeated = build_multi_room_heatmap_report(observations)
    if repeated != report:
        raise SystemExit("identical observations should yield identical reports")

    changed_report = build_multi_room_heatmap_report(
        observations
        + [
            {
                "room_id": "room_epsilon",
                "source": "motion",
                "confidence": 0.9,
                "ts": "2026-06-08T09:04:00+10:00",
            }
        ]
    )
    if changed_report is None:
        raise SystemExit("changed observations should still create a report")
    if changed_report["report_id"] == report["report_id"]:
        raise SystemExit("report_id should change when heatmap cells change")

    provenance_only_changed = build_multi_room_heatmap_report(
        [
            {
                "room_id": "room_delta",
                "source": "camera",
                "confidence": 0.9,
                "ts": "2026-06-08T11:00:00+10:00",
            },
            {
                "room_id": "room_delta",
                "source": "manual_override",
                "confidence": 0.8,
                "ts": "2026-06-08T11:05:00+10:00",
            },
            {
                "room_id": "room_epsilon",
                "source": "ble",
                "confidence": 0.7,
                "ts": "2026-06-08T11:07:00+10:00",
            },
        ]
    )
    if provenance_only_changed is None:
        raise SystemExit("provenance-only changes should still create a report")
    if provenance_only_changed["report_id"] != report["report_id"]:
        raise SystemExit("report_id should ignore per-room provenance and timestamp detail")

    ignored_only = build_multi_room_heatmap_report(
        [
            {
                "room_id": "zone_alpha",
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
