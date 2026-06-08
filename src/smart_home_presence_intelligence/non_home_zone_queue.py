"""Planning-only non-home zone queue helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping
import json

import yaml


NON_HOME_ZONE_QUEUE_SOURCE = "non_home_zone_queue"
NON_HOME_ZONE_QUEUE_RECORD_TYPE = "non_home_zone_alert"
NON_HOME_ZONE_QUEUE_RECORD_NAME = "non_home_zone_queue"
NON_HOME_ZONE_QUEUE_REVIEW_STATUS = "queued"
NON_HOME_ZONE_QUEUE_RETENTION_DAYS = 90
DEFAULT_TS = "1970-01-01T00:00:00Z"

ROOM_INVENTORY_PATH = (
    Path(__file__).resolve().parents[2]
    / "config"
    / "inventory"
    / "rooms.yaml"
)
CURRENT_NON_HOME_ZONE = "driveway"


def _read_room_inventory(path: Path | None = None) -> dict[str, Any]:
    """Read and normalize the room inventory payload."""

    inventory_path = path or ROOM_INVENTORY_PATH
    with inventory_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("room inventory contract must be a mapping")
    return payload


def _load_non_home_zones(path: Path | None = None) -> set[str]:
    payload = _read_room_inventory(path)
    external_zones = payload.get("external_zones", [])
    if not isinstance(external_zones, list):
        raise ValueError("room inventory must define external_zones as a list")

    zones = set()
    for zone in external_zones:
        if not isinstance(zone, dict):
            continue
        zone_id = zone.get("room_id")
        if not isinstance(zone_id, str):
            continue
        normalized_zone = zone_id.strip().lower()
        if normalized_zone:
            zones.add(normalized_zone)

    if not zones:
        raise ValueError("room inventory has no non-home zones configured")
    return zones


def _normalize_room(snapshot: Mapping[str, Any]) -> str:
    room = snapshot.get("room_id") or snapshot.get("room") or snapshot.get("zone_id")
    if room is None:
        raise ValueError("snapshot missing room_id/room/zone_id")
    room_text = str(room).strip().lower()
    if not room_text:
        raise ValueError("snapshot room_id/room/zone_id cannot be empty")
    return room_text


def _normalize_camera(snapshot: Mapping[str, Any]) -> str:
    camera = snapshot.get("camera")
    if not isinstance(camera, str):
        raise ValueError("snapshot missing or invalid camera")
    camera_text = camera.strip()
    if not camera_text:
        raise ValueError("camera cannot be empty")
    return camera_text


def _build_queue_id(room: str, camera: str, evidence: dict[str, Any]) -> str:
    evidence_text = json.dumps(evidence, sort_keys=True, separators=(",", ":"))
    return f"{NON_HOME_ZONE_QUEUE_SOURCE}::{room}::{camera}::{evidence_text}"


def _extract_evidence(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    for key, value in snapshot.items():
        if key in {"room_id", "room", "zone_id", "camera"}:
            continue
        if value is not None:
            evidence[key] = value
    return evidence


def build_non_home_zone_queue_record(
    snapshot: Mapping[str, Any],
) -> dict[str, Any] | None:
    """Build an immutable non-home queue record for deterministic review planning."""

    room = _normalize_room(snapshot)
    non_home_zones = _load_non_home_zones()
    if CURRENT_NON_HOME_ZONE not in non_home_zones:
        raise ValueError("inventory is missing expected non-home zone: driveway")
    if room not in non_home_zones:
        return None

    camera = _normalize_camera(snapshot)
    evidence = _extract_evidence(snapshot)
    queue_id = _build_queue_id(room, camera, evidence)

    return {
        "queue_id": queue_id,
        "source": NON_HOME_ZONE_QUEUE_SOURCE,
        "queue_record_type": NON_HOME_ZONE_QUEUE_RECORD_TYPE,
        "record_name": NON_HOME_ZONE_QUEUE_RECORD_NAME,
        "review_status": NON_HOME_ZONE_QUEUE_REVIEW_STATUS,
        "room": room,
        "camera": camera,
        "evidence": evidence,
        "immutable": True,
        "retention": {
            "days": NON_HOME_ZONE_QUEUE_RETENTION_DAYS,
            "immutable": True,
        },
        "ts": str(snapshot.get("ts", DEFAULT_TS)),
    }
