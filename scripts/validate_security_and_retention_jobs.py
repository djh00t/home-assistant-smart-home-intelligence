#!/usr/bin/env python3
"""Validate the security-and-retention jobs planning slice."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/security_and_retention_jobs.yaml",
    ROOT / "docs/contracts/security-and-retention-jobs.md",
    ROOT / "src/smart_home_presence_intelligence/security_and_retention_jobs.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing security-and-retention jobs files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/security_and_retention_jobs.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "scope:",
        "planning_only: true",
        "reference: config/policies/retention.yaml",
        "cleanup_job_required: true",
        "immutable_audit_required: true",
        "cleanup_mode: dry_run",
        "cleanup_condition: age_days > retention_days",
        "record_type: retention_audit",
        "task: TASK-020",
    ):
        if needle not in text:
            raise SystemExit(f"security_and_retention_jobs.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.security_and_retention_jobs import (
        DRY_RUN_REQUIRED,
        DEFAULT_RETENTION_DAYS,
        build_retention_audit_report,
        IMMUTABLE_AUDIT_REQUIRED,
    )

    artifacts = [
        {"record_type": "event_records", "age_days": 100, "record_id": "evt-a"},
        {"record_type": "room_state_history", "age_days": 60, "record_id": "state-b"},
        {"record_type": "face_plate_audit", "age_days": 91, "record_id": "fpa-c"},
    ]
    report = build_retention_audit_report(artifacts)
    if report["source"] != "security_and_retention_jobs":
        raise SystemExit("report source should be security_and_retention_jobs")
    if report["report_type"] != "retention_audit":
        raise SystemExit("report should be a retention_audit report")
    if not report["cleanup_dry_run_required"]:
        raise SystemExit("cleanup must be dry-run in this phase 0 slice")
    if report["cleanup_mode"] != ("dry_run" if DRY_RUN_REQUIRED else "enabled"):
        raise SystemExit("cleanup_mode should match module dry-run setting")
    if report["immutable_audit_expected"] is not IMMUTABLE_AUDIT_REQUIRED:
        raise SystemExit("immutable audit expectation should be required")
    if report["cleanup_candidate_count"] != 2:
        raise SystemExit("artifacts older than retention should be cleanup candidates")
    if report["retained_count"] != 1:
        raise SystemExit("younger artifact should be retained")

    retained = report["retained_records"]
    if not retained or retained[0]["record_type"] != "room_state_history":
        raise SystemExit("retained records should be explicitly reported")
    if report["retained_records"][0]["retention_status"] != "retained":
        raise SystemExit("retained record should retain status")

    candidate_ids = [entry["record_id"] for entry in report["cleanup_candidates"]]
    if candidate_ids != ["evt-a", "fpa-c"]:
        raise SystemExit("cleanup candidate record ids should be deterministic and sorted")

    fallback_report = build_retention_audit_report(
        [{"record_type": "unknown_kind", "age_days": DEFAULT_RETENTION_DAYS - 1}]
    )
    if fallback_report["cleanup_candidate_count"] != 0:
        raise SystemExit("unknown record types should use default retention fallback")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_security_and_retention_jobs.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Security and retention jobs check passed"
        if sys.argv[1] == "check"
        else "Security and retention jobs quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
