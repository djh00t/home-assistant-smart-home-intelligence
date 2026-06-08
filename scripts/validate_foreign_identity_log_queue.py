#!/usr/bin/env python3
"""Validate the foreign identity log queue slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/foreign_identity_log_queue.yaml",
    ROOT / "docs/contracts/foreign-identity-log-queue.md",
    ROOT / "src/smart_home_presence_intelligence/foreign_identity_log_queue.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing foreign identity log queue files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/foreign_identity_log_queue.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "behavior: immutable_foreign_identity_queue",
        "no_action_hooks",
        "no_vehicle_person_linking",
        "no_garage_lock_actuation",
        "room_reference_required: true",
        "queue_record_type: foreign_identity_alert",
        "record_name: foreign_identity_log",
        "review_status: queued",
        "retention_days: 90",
        "immutable: true",
    ):
        if needle not in text:
            raise SystemExit(
                f"foreign_identity_log_queue.yaml missing required text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.foreign_identity_log_queue import (  # noqa: E501
        build_foreign_identity_queue_record,
        FOREIGN_IDENTITY_QUEUE_RECORD_NAME,
        FOREIGN_IDENTITY_QUEUE_RECORD_TYPE,
        FOREIGN_IDENTITY_QUEUE_RETENTION_DAYS,
        FOREIGN_IDENTITY_LOG_QUEUE_SOURCE,
        FOREIGN_IDENTITY_QUEUE_REVIEW_STATUS,
    )

    foreign_record = build_foreign_identity_queue_record(
        {
            "room_id": "driveway",
            "camera": "frigate_driveway",
            "plate": "ab c-12",
            "identity_status": "foreign",
            "face_match_confidence": 0.45,
            "event_id": "foreign-1",
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if foreign_record is None:
        raise SystemExit("foreign identity should create a queue record")
    if foreign_record["source"] != FOREIGN_IDENTITY_LOG_QUEUE_SOURCE:
        raise SystemExit("queue record should use foreign_identity_log_queue source")
    if foreign_record["queue_record_type"] != FOREIGN_IDENTITY_QUEUE_RECORD_TYPE:
        raise SystemExit("queue record type should be foreign_identity_alert")
    if foreign_record["record_name"] != FOREIGN_IDENTITY_QUEUE_RECORD_NAME:
        raise SystemExit("queue record should use canonical record name")
    if foreign_record["review_status"] != FOREIGN_IDENTITY_QUEUE_REVIEW_STATUS:
        raise SystemExit("queue record should be review queued")
    if foreign_record["room"] != "driveway":
        raise SystemExit("queue record should preserve room")
    if foreign_record["camera"] != "frigate_driveway":
        raise SystemExit("queue record should preserve camera")
    if foreign_record["identity"]["plate"] != "ABC12":
        raise SystemExit("plate should be canonicalized in queue identity evidence")
    retention = foreign_record.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 90:
        raise SystemExit("queue record should include 90-day retention")
    if retention.get("immutable") is not True:
        raise SystemExit("queue record should include immutable retention metadata")

    if FOREIGN_IDENTITY_QUEUE_RETENTION_DAYS != 90:
        raise SystemExit("foreign identity queue retention constant should be 90 days")

    recognized_record = build_foreign_identity_queue_record(
        {
            "room_id": "driveway",
            "camera": "frigate_driveway",
            "person_id": "Sel",
            "face_match_confidence": 0.86,
            "identity_status": "known",
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if recognized_record is not None:
        raise SystemExit("known identity should not be queued")

    try:
        build_foreign_identity_queue_record(
            {
                "room_id": "driveway",
                "camera": "frigate_driveway",
            }
        )
    except ValueError:
        pass
    else:
        raise SystemExit("missing identity evidence should be rejected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_foreign_identity_log_queue.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Foreign identity log queue check passed"
        if sys.argv[1] == "check"
        else "Foreign identity log queue quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

