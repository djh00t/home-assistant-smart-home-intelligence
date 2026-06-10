#!/usr/bin/env python3
"""Validate the foreign identity log queue slice."""

from __future__ import annotations

import hashlib
import json
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
        "no_room_zeta_lock_actuation",
        "room_reference_required: true",
        "queue_record_type: foreign_identity_alert",
        "record_name: foreign_identity_log",
        "review_status: queued",
        "retention_days: 90",
        "immutable: true",
        "queue_id_evidence_digest: sha256_canonical_json",
        "queue_id_format: foreign_identity_log_queue::{room}::{camera}::sha256:{evidence_digest}",
        "queue_id_raw_sensitive_evidence: false",
        "identity_raw_plate_or_person: false",
    ):
        if needle not in text:
            raise SystemExit(
                f"foreign_identity_log_queue.yaml missing required text: {needle}"
            )

    doc_text = (ROOT / "docs/contracts/foreign-identity-log-queue.md").read_text(
        encoding="utf-8"
    )
    for needle in (
        "SHA-256 digest of canonicalized identity evidence",
        "Raw plate or person values must never appear in `queue_id`",
        "foreign_identity_log_queue::{room}::{camera}::sha256:{evidence_digest}",
        "Raw plate or person values must never appear in the persisted `identity` payload.",
    ):
        if needle not in doc_text:
            raise SystemExit(
                f"foreign-identity-log-queue.md missing required privacy text: {needle}"
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
            "room_id": "zone_alpha",
            "camera": "frigate_zone_alpha",
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
    if foreign_record["room"] != "zone_alpha":
        raise SystemExit("queue record should preserve room")
    if foreign_record["camera"] != "frigate_zone_alpha":
        raise SystemExit("queue record should preserve camera")
    if foreign_record["identity"].get("plate_present") is not True:
        raise SystemExit("queue record should indicate plate presence without raw plate text")
    if "plate" in foreign_record["identity"] or "person_id" in foreign_record["identity"]:
        raise SystemExit("queue identity should not retain raw plate or person identifiers")
    expected_queue_id = (
        "foreign_identity_log_queue::zone_alpha::frigate_zone_alpha::sha256:"
        + hashlib.sha256(
            json.dumps(
                foreign_record["identity"], sort_keys=True, separators=(",", ":")
            ).encode("utf-8")
        ).hexdigest()
    )
    if foreign_record["queue_id"] != expected_queue_id:
        raise SystemExit("queue_id should use a deterministic sha256 evidence digest")
    if "ABC12" in foreign_record["queue_id"] or "ab c-12" in foreign_record["queue_id"].lower():
        raise SystemExit("queue_id should not expose raw identity evidence")
    retention = foreign_record.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 90:
        raise SystemExit("queue record should include 90-day retention")
    if retention.get("immutable") is not True:
        raise SystemExit("queue record should include immutable retention metadata")

    if FOREIGN_IDENTITY_QUEUE_RETENTION_DAYS != 90:
        raise SystemExit("foreign identity queue retention constant should be 90 days")

    recognized_record = build_foreign_identity_queue_record(
        {
            "room_id": "zone_alpha",
            "camera": "frigate_zone_alpha",
            "person_id": "Sel",
            "face_match_confidence": 0.86,
            "identity_status": "known",
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if recognized_record is not None:
        raise SystemExit("known identity should not be queued")

    person_queue_record = build_foreign_identity_queue_record(
        {
            "room_id": "zone_alpha",
            "camera": "frigate_zone_alpha",
            "person_id": "Sel",
            "identity_status": "unknown",
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if person_queue_record is None:
        raise SystemExit("unknown person identity should create a queue record")
    if person_queue_record["identity"].get("person_present") is not True:
        raise SystemExit("queue record should indicate person presence without raw person text")
    if "Sel" in person_queue_record["queue_id"] or "sel" in person_queue_record["queue_id"]:
        raise SystemExit("queue_id should not expose raw person identifiers")

    different_record = build_foreign_identity_queue_record(
        {
            "room_id": "zone_alpha",
            "camera": "frigate_zone_alpha",
            "person_id": "visitor",
            "identity_status": "unknown",
            "face_match_confidence": 0.2,
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if different_record is None:
        raise SystemExit("different foreign identity should still create a queue record")
    if different_record["queue_id"] == foreign_record["queue_id"]:
        raise SystemExit("queue_id should change when identity evidence changes")

    try:
        build_foreign_identity_queue_record(
            {
                "room_id": "zone_alpha",
                "camera": "frigate_zone_alpha",
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
