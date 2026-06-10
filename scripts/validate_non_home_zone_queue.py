#!/usr/bin/env python3
"""Validate the non-home zone queue slice."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/non_home_zone_queue.yaml",
    ROOT / "docs/contracts/non-home-zone-queue.md",
    ROOT / "src/smart_home_presence_intelligence/non_home_zone_queue.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing non-home zone queue files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/non_home_zone_queue.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "behavior: deterministic_non_home_zone_queue",
        "no_actuation",
        "no_indoor_room_automation",
        "no_vehicle_person_linking",
        "room_reference_required: true",
        "queue_id_evidence_digest: sha256_canonical_json",
        "queue_record_type: non_home_zone_alert",
        "record_name: non_home_zone_queue",
        "review_status: queued",
        "retention_days: 90",
        "immutable: true",
        "queue_id_raw_sensitive_evidence: false",
        "evidence_identity_fields_mode: presence_flags_only",
        "evidence_linkable_refs_retained: false",
    ):
        if needle not in text:
            raise SystemExit(f"non_home_zone_queue.yaml missing required text: {needle}")

    doc_text = (ROOT / "docs/contracts/non-home-zone-queue.md").read_text(
        encoding="utf-8"
    )
    for needle in (
        "SHA-256 digest of canonicalized evidence",
        "presence-only flags instead of retaining person or plate references",
        "linkable `event_id`, raw plate values, raw person identifiers, and hashed identity refs are excluded",
        "non_home_zone_queue::{room}::{camera}::sha256:{evidence_digest}",
    ):
        if needle not in doc_text:
            raise SystemExit(
                f"non-home-zone-queue.md missing required privacy text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.non_home_zone_queue import (  # noqa: E501
        NON_HOME_ZONE_QUEUE_RECORD_NAME,
        NON_HOME_ZONE_QUEUE_RECORD_TYPE,
        NON_HOME_ZONE_QUEUE_REVIEW_STATUS,
        NON_HOME_ZONE_QUEUE_RETENTION_DAYS,
        NON_HOME_ZONE_QUEUE_SOURCE,
        build_non_home_zone_queue_record,
    )

    snapshot = {
        "room_id": "zone_alpha",
        "camera": "frigate_zone_alpha",
        "source": "frigate",
        "plate": "ab c-12",
        "person_id": "sel",
        "identity_status": "foreign",
        "direction": "enter",
        "ts": "2026-06-08T10:00:00+10:00",
    }
    non_home_record = build_non_home_zone_queue_record(snapshot)
    if non_home_record is None:
        raise SystemExit("zone_alpha sighting should create queue record")
    if non_home_record["source"] != NON_HOME_ZONE_QUEUE_SOURCE:
        raise SystemExit("queue record should use non-home zone queue source")
    if non_home_record["queue_record_type"] != NON_HOME_ZONE_QUEUE_RECORD_TYPE:
        raise SystemExit("queue record type should be non_home_zone_alert")
    if non_home_record["record_name"] != NON_HOME_ZONE_QUEUE_RECORD_NAME:
        raise SystemExit("queue record should use canonical record name")
    if non_home_record["review_status"] != NON_HOME_ZONE_QUEUE_REVIEW_STATUS:
        raise SystemExit("queue record should be queued for review")
    if non_home_record["room"] != "zone_alpha":
        raise SystemExit("queue record should preserve room")
    if non_home_record["camera"] != "frigate_zone_alpha":
        raise SystemExit("queue record should preserve camera")
    if non_home_record["evidence"].get("plate_seen") is not True:
        raise SystemExit("queue record should retain a plate presence flag")
    if non_home_record["evidence"].get("person_seen") is not True:
        raise SystemExit("queue record should retain a person presence flag")
    if non_home_record["evidence"].get("source") != "frigate":
        raise SystemExit("queue record should keep source evidence when provided")
    if "plate" in non_home_record["evidence"] or "person_id" in non_home_record["evidence"]:
        raise SystemExit("queue record should not retain raw plate or person identifiers")
    if "plate_ref" in non_home_record["evidence"] or "person_ref" in non_home_record["evidence"]:
        raise SystemExit("queue record should not retain hashed identity references")
    if "event_id" in non_home_record["evidence"]:
        raise SystemExit("queue record should not retain linkable event ids")
    if "ts" in non_home_record["evidence"]:
        raise SystemExit("queue record should not retain evidence timestamps")
    if non_home_record["queue_id"].count("::") != 3:
        raise SystemExit("queue_id should be deterministic and structured")
    evidence_digest = hashlib.sha256(
        json.dumps(
            non_home_record["evidence"], sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    expected_queue_id = (
        f"{NON_HOME_ZONE_QUEUE_SOURCE}::zone_alpha::frigate_zone_alpha::sha256:{evidence_digest}"
    )
    if non_home_record["queue_id"] != expected_queue_id:
        raise SystemExit("queue_id should use a deterministic sha256 evidence digest")
    if "ab c-12" in non_home_record["queue_id"] or "sel" in non_home_record["queue_id"]:
        raise SystemExit("queue_id should not expose raw sensitive evidence")
    retention = non_home_record.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 90:
        raise SystemExit("queue record should include 90-day retention")
    if retention.get("immutable") is not True:
        raise SystemExit("retention metadata should be immutable")
    if NON_HOME_ZONE_QUEUE_RETENTION_DAYS != 90:
        raise SystemExit("non-home queue retention constant should be 90 days")

    repeated = build_non_home_zone_queue_record(snapshot)
    if repeated != non_home_record:
        raise SystemExit("identical snapshots should yield identical queue records")

    redacted_identity_record = build_non_home_zone_queue_record(
        {
            **snapshot,
            "person_id": "alex",
            "plate": "zz9 999",
        }
    )
    if redacted_identity_record is None:
        raise SystemExit("identity-redacted zone_alpha sighting should still create queue record")
    if redacted_identity_record["queue_id"] != non_home_record["queue_id"]:
        raise SystemExit("queue_id should stay stable when only redacted identity details change")

    different_evidence_record = build_non_home_zone_queue_record(
        {
            **snapshot,
            "direction": "leave",
        }
    )
    if different_evidence_record is None:
        raise SystemExit("changed zone_alpha sighting should still create queue record")
    if different_evidence_record["queue_id"] == non_home_record["queue_id"]:
        raise SystemExit("queue_id should change when retained evidence changes")

    home_record = build_non_home_zone_queue_record(
        {
            "room_id": "room_delta",
            "camera": "room_delta_cam",
            "person_id": "sel",
            "ts": "2026-06-08T10:00:00+10:00",
        }
    )
    if home_record is not None:
        raise SystemExit("interior/home room sighting should not be queued")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_non_home_zone_queue.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Non-home zone queue check passed"
        if sys.argv[1] == "check"
        else "Non-home zone queue quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
