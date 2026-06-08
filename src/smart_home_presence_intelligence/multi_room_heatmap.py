"""Planning-only multi-room heatmap report helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable, Mapping
import json

import yaml


MULTI_ROOM_HEATMAP_SOURCE = "multi_room_heatmap"
MULTI_ROOM_HEATMAP_RECORD_TYPE = "room_heatmap"
MULTI_ROOM_HEATMAP_RECORD_NAME = "multi_room_heatmap"
MULTI_ROOM_HEATMAP_REPORT_STATUS = "ready"
MULTI_ROOM_HEATMAP_RETENTION_DAYS = 90
DEFAULT_TS = "1970-01-01T00:00:00Z"

ROOM_INVENTORY_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "inventory" / "rooms.yaml"
)


def _read_room_inventory(path: Path | None = None) -> dict[str, Any]:
    """Read and normalize the room inventory payload."""

    inventory_path = path or ROOM_INVENTORY_PATH
    with inventory_path.open(encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)
    if not isinstance(payload, dict):
        raise ValueError("room inventory contract must be a mapping")
    return payload


def _load_occupancy_rooms(path: Path | None = None) -> set[str]:
    payload = _read_room_inventory(path)
    rooms: set[str] = set()

    for section in ("rooms", "external_zones"):
        entries = payload.get(section, [])
        if not isinstance(entries, list):
            raise ValueError(f"room inventory must define {section} as a list")
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            if entry.get("supports_occupancy") is not True:
                continue
            room_id = entry.get("room_id")
            if not isinstance(room_id, str):
                continue
            normalized_room = room_id.strip().lower()
            if normalized_room:
                rooms.add(normalized_room)

    if not rooms:
        raise ValueError("room inventory has no occupancy-supporting rooms configured")
    return rooms


def _normalize_room(observation: Mapping[str, Any]) -> str:
    room = observation.get("room_id") or observation.get("room") or observation.get("zone_id")
    if room is None:
        raise ValueError("observation missing room_id/room/zone_id")
    room_text = str(room).strip().lower()
    if not room_text:
        raise ValueError("observation room_id/room/zone_id cannot be empty")
    return room_text


def _normalize_confidence(observation: Mapping[str, Any]) -> float:
    confidence = observation.get("confidence")
    if not isinstance(confidence, (int, float)):
        raise ValueError("observation missing or invalid confidence")
    confidence_value = float(confidence)
    if not 0.0 <= confidence_value <= 1.0:
        raise ValueError(f"confidence must be between 0.0 and 1.0: {confidence_value!r}")
    return confidence_value


def _normalize_source(observation: Mapping[str, Any]) -> str | None:
    source = observation.get("source")
    if source is None:
        return None
    if not isinstance(source, str):
        raise ValueError("source must be a string when provided")
    source_text = source.strip()
    if not source_text:
        return None
    return source_text


def _normalize_ts(observation: Mapping[str, Any]) -> str:
    ts = observation.get("ts", DEFAULT_TS)
    return str(ts)


def _bucket_heat(count: int) -> int:
    if count <= 0:
        return 0
    return min(count, 4)


def _report_id(cells: list[dict[str, Any]]) -> str:
    fragment = json.dumps(cells, sort_keys=True, separators=(",", ":"))
    return f"{MULTI_ROOM_HEATMAP_SOURCE}::{fragment}"


def _build_cells(observations: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    eligible_rooms = _load_occupancy_rooms()
    aggregates: dict[str, dict[str, Any]] = {}

    for observation in observations:
        room = _normalize_room(observation)
        if room not in eligible_rooms:
            continue

        confidence = _normalize_confidence(observation)
        source = _normalize_source(observation)
        ts = _normalize_ts(observation)

        aggregate = aggregates.setdefault(
            room,
            {
                "room": room,
                "observation_count": 0,
                "_confidence_total": 0.0,
                "sources": set(),
                "latest_ts": ts,
            },
        )
        aggregate["observation_count"] += 1
        aggregate["_confidence_total"] += confidence
        aggregate["latest_ts"] = max(aggregate["latest_ts"], ts)
        if source is not None:
            aggregate["sources"].add(source)

    cells: list[dict[str, Any]] = []
    for room in sorted(aggregates):
        aggregate = aggregates[room]
        count = aggregate["observation_count"]
        average_confidence = round(aggregate["_confidence_total"] / count, 3)
        cell = {
            "room": room,
            "observation_count": count,
            "average_confidence": average_confidence,
            "heat_level": _bucket_heat(count),
            "sources": sorted(aggregate["sources"]),
            "latest_ts": aggregate["latest_ts"],
        }
        cells.append(cell)

    return cells


def build_multi_room_heatmap_report(
    observations: Iterable[Mapping[str, Any]],
) -> dict[str, Any] | None:
    """Build an immutable multi-room heatmap report for review planning."""

    cells = _build_cells(observations)
    if not cells:
        return None

    total_observations = sum(cell["observation_count"] for cell in cells)
    summary = {
        "room_count": len(cells),
        "observation_count": total_observations,
        "supported_rooms_seen": [cell["room"] for cell in cells],
    }

    ts = min(cell["latest_ts"] for cell in cells)

    return {
        "report_id": _report_id(cells),
        "source": MULTI_ROOM_HEATMAP_SOURCE,
        "report_record_type": MULTI_ROOM_HEATMAP_RECORD_TYPE,
        "record_name": MULTI_ROOM_HEATMAP_RECORD_NAME,
        "report_status": MULTI_ROOM_HEATMAP_REPORT_STATUS,
        "heatmap_cells": cells,
        "summary": summary,
        "immutable": True,
        "retention": {
            "days": MULTI_ROOM_HEATMAP_RETENTION_DAYS,
            "immutable": True,
        },
        "ts": ts,
    }
