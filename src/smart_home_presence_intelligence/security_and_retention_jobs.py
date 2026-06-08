"""Deterministic planning-only retention audit helper for phase 0."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping

import yaml


SECURITY_AND_RETENTION_JOB_SOURCE = "security_and_retention_jobs"
RETENTION_AUDIT_REPORT_TYPE = "retention_audit"
DEFAULT_RETENTION_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "policies" / "retention.yaml"
)
DEFAULT_RETENTION_DAYS = 90
IMMUTABLE_AUDIT_REQUIRED = True
DRY_RUN_REQUIRED = True


def _load_retention_payload(path: Path | None = None) -> dict[str, int]:
    policy_path = path or DEFAULT_RETENTION_PATH
    payload = yaml.safe_load(policy_path.read_text(encoding="utf-8")) or {}
    if not isinstance(payload, dict):
        raise ValueError("retention policy must be a mapping")

    retention_days = payload.get("retention_days")
    if not isinstance(retention_days, dict):
        raise ValueError("retention policy must include retention_days map")

    parsed = {}
    for key, value in retention_days.items():
        if not isinstance(key, str):
            raise ValueError(f"invalid retention key {key!r}, expected string")
        if not isinstance(value, int):
            raise ValueError(
                f"retention_days[{key!r}] must be an integer, got {type(value).__name__}"
            )
        parsed[key] = value
    if not parsed:
        raise ValueError("retention_days map must not be empty")
    return parsed


def _normalise_record_type(record: Mapping[str, Any]) -> str:
    raw_record_type = record.get("record_type")
    if raw_record_type is None:
        raise ValueError("artifact record missing record_type")
    if not isinstance(raw_record_type, str):
        raise ValueError("record_type must be a string")
    record_type = raw_record_type.strip().lower()
    if not record_type:
        raise ValueError("record_type must not be empty")
    return record_type


def _normalise_age_days(record: Mapping[str, Any]) -> int:
    if "age_days" not in record:
        raise ValueError("artifact record missing age_days")
    age = record["age_days"]
    if isinstance(age, bool) or not isinstance(age, (int, float)):
        raise ValueError("age_days must be a numeric value")
    age_days = int(age)
    if age_days < 0:
        raise ValueError("age_days must be >= 0")
    return age_days


def _normalise_record_id(record: Mapping[str, Any]) -> str:
    raw_record_id = record.get("record_id")
    if raw_record_id is None:
        return ""
    return str(raw_record_id)


def _iter_records(artifact_records: Iterable[Mapping[str, Any]]) -> Iterable[dict[str, Any]]:
    for item in artifact_records:
        if not isinstance(item, Mapping):
            raise ValueError("each artifact record must be a mapping")
        yield {
            "record_type": _normalise_record_type(item),
            "age_days": _normalise_age_days(item),
            "record_id": _normalise_record_id(item),
        }


def _enrich_records(
    artifact_records: Iterable[Mapping[str, Any]],
    retention_days: Mapping[str, int],
) -> list[dict[str, Any]]:
    normalized = []
    for item in _iter_records(artifact_records):
        threshold = retention_days.get(item["record_type"], DEFAULT_RETENTION_DAYS)
        entry = dict(item)
        entry["retention_days"] = threshold
        entry["cleanup_candidate"] = item["age_days"] > threshold
        entry["retention_status"] = (
            "cleanup_candidate" if entry["cleanup_candidate"] else "retained"
        )
        normalized.append(entry)
    normalized.sort(key=lambda entry: (entry["record_type"], entry["age_days"], entry["record_id"]))
    return normalized


def build_retention_audit_report(
    artifact_records: Iterable[Mapping[str, Any]],
    *,
    retention_policy_path: Path | None = None,
    dry_run: bool = DRY_RUN_REQUIRED,
) -> dict[str, Any]:
    """
    Build a planning-only retention audit report.
    """

    retention_days = _load_retention_payload(retention_policy_path)
    normalized_records = _enrich_records(artifact_records, retention_days)
    cleanup_candidates = [
        record for record in normalized_records if record["cleanup_candidate"]
    ]
    retained_records = [
        record for record in normalized_records if not record["cleanup_candidate"]
    ]
    immutable_audit_required = IMMUTABLE_AUDIT_REQUIRED

    return {
        "source": SECURITY_AND_RETENTION_JOB_SOURCE,
        "report_type": RETENTION_AUDIT_REPORT_TYPE,
        "cleanup_job_required": True,
        "cleanup_mode": "dry_run" if dry_run else "enabled",
        "immutable_audit_required": immutable_audit_required,
        "record_count": len(normalized_records),
        "cleanup_candidate_count": len(cleanup_candidates),
        "retained_count": len(retained_records),
        "cleanup_candidates": cleanup_candidates,
        "retained_records": retained_records,
        "immutable_audit_expected": immutable_audit_required,
        "cleanup_dry_run_required": bool(dry_run),
    }
