#!/usr/bin/env python3
"""Validate the anomaly and false-action dashboard slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/anomaly_and_false_action_dashboard.yaml",
    ROOT / "docs/contracts/anomaly-and-false-action-dashboard.md",
    ROOT / "src/smart_home_presence_intelligence/anomaly_and_false_action_dashboard.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing anomaly and false-action dashboard files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/anomaly_and_false_action_dashboard.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "behavior: deterministic_anomaly_and_false_action_dashboard",
        "planning_only: true",
        "no_actuation",
        "no_scene_writes",
        "no_schedule_writes",
        "no_dashboard_backend_mutation",
        "no_alert_escalation",
        "incidents",
        "room_reference_required: true",
        "dashboard_record_type: anomaly_false_action_dashboard",
        "record_name: anomaly_and_false_action_dashboard",
        "dashboard_status: ready",
        "retention_days: 90",
        "immutable: true",
    ):
        if needle not in text:
            raise SystemExit(
                f"anomaly_and_false_action_dashboard.yaml missing required text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.anomaly_and_false_action_dashboard import (  # noqa: E501
        ANOMALY_DASHBOARD_RECORD_NAME,
        ANOMALY_DASHBOARD_RECORD_TYPE,
        ANOMALY_DASHBOARD_RETENTION_DAYS,
        ANOMALY_DASHBOARD_SOURCE,
        ANOMALY_DASHBOARD_STATUS,
        build_anomaly_and_false_action_dashboard,
    )

    incidents = [
        {
            "room_id": "hall",
            "kind": "anomaly",
            "severity": "medium",
            "category": "motion_gap",
            "ts": "2026-06-08T12:45:00+10:00",
        },
        {
            "room_id": "hall",
            "kind": "false_action",
            "severity": "high",
            "category": "false_light",
            "ts": "2026-06-08T12:46:00+10:00",
        },
        {
            "room_id": "office",
            "kind": "false_action",
            "severity": "critical",
            "category": "false_override",
            "ts": "2026-06-08T12:47:00+10:00",
        },
        {
            "room_id": "driveway",
            "kind": "anomaly",
            "severity": "low",
            "category": "foreign_review",
            "ts": "2026-06-08T12:48:00+10:00",
        },
    ]

    dashboard = build_anomaly_and_false_action_dashboard(
        incidents, focus_room_id="office"
    )
    if dashboard is None:
        raise SystemExit("incidents should create a dashboard")
    if dashboard["source"] != ANOMALY_DASHBOARD_SOURCE:
        raise SystemExit("dashboard should use canonical source")
    if dashboard["dashboard_record_type"] != ANOMALY_DASHBOARD_RECORD_TYPE:
        raise SystemExit("dashboard should use canonical record type")
    if dashboard["record_name"] != ANOMALY_DASHBOARD_RECORD_NAME:
        raise SystemExit("dashboard should use canonical record name")
    if dashboard["dashboard_status"] != ANOMALY_DASHBOARD_STATUS:
        raise SystemExit("dashboard should be ready")

    cards = dashboard["room_cards"]
    if [card["room"] for card in cards] != ["hall", "office", "driveway"]:
        raise SystemExit("dashboard cards should follow canonical room order")
    hall = cards[0]
    office = cards[1]
    driveway = cards[2]
    if hall["incident_count"] != 2 or hall["false_action_count"] != 1:
        raise SystemExit("hall incidents should be aggregated")
    if office["peak_severity"] != "critical":
        raise SystemExit("office should preserve highest severity")
    if driveway["review_priority"] != "low":
        raise SystemExit("driveway review priority should match severity")
    if dashboard["summary"]["incident_count"] != 4:
        raise SystemExit("summary should count all incidents")
    if dashboard["summary"]["anomaly_count"] != 2:
        raise SystemExit("summary should count anomalies")
    if dashboard["summary"]["false_action_count"] != 2:
        raise SystemExit("summary should count false actions")
    if dashboard["summary"]["critical_room_count"] != 1:
        raise SystemExit("summary should count critical rooms")
    if dashboard["focus_room_id"] != "office":
        raise SystemExit("focus_room_id should normalize to lowercase")

    retention = dashboard.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 90:
        raise SystemExit("dashboard should include 90-day retention")
    if retention.get("immutable") is not True:
        raise SystemExit("dashboard retention should be immutable")
    if ANOMALY_DASHBOARD_RETENTION_DAYS != 90:
        raise SystemExit("dashboard retention constant should be 90 days")

    repeated = build_anomaly_and_false_action_dashboard(
        incidents, focus_room_id="office"
    )
    if repeated != dashboard:
        raise SystemExit("identical incidents should yield identical dashboard models")

    if build_anomaly_and_false_action_dashboard([]) is not None:
        raise SystemExit("empty incident lists should not create a dashboard")

    try:
        build_anomaly_and_false_action_dashboard(
            [
                {
                    "room_id": "attic",
                    "kind": "anomaly",
                    "severity": "low",
                }
            ]
        )
    except ValueError:
        pass
    else:
        raise SystemExit("unknown rooms should be rejected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_anomaly_and_false_action_dashboard.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Anomaly and false-action dashboard check passed"
        if sys.argv[1] == "check"
        else "Anomaly and false-action dashboard quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
