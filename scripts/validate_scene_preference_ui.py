#!/usr/bin/env python3
"""Validate the scene preference UI slice."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/scene_preference_ui.yaml",
    ROOT / "docs/contracts/scene-preference-ui.md",
    ROOT / "src/smart_home_presence_intelligence/scene_preference_ui.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing scene preference UI files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/scene_preference_ui.yaml").read_text(encoding="utf-8")
    for needle in (
        "behavior: deterministic_scene_preference_ui",
        "planning_only: true",
        "no_actuation",
        "no_scene_writes",
        "no_dashboard_backend_mutation",
        "no_schedule_writes",
        "room_capabilities",
        "include_only_lighting_rooms: true",
        "exclude_external_zones: true",
        "ui_record_type: scene_preferences_dashboard",
        "record_name: scene_preference_ui",
        "ui_status: ready",
        "dashboard_id_digest: sha256_canonical_json",
        "dashboard_id_format: scene_preference_ui::sha256:{dashboard_digest}",
        "dashboard_id_raw_telemetry: false",
        "retention_days: 90",
        "immutable: true",
    ):
        if needle not in text:
            raise SystemExit(f"scene_preference_ui.yaml missing required text: {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.scene_preference_ui import (  # noqa: E501
        SCENE_PREFERENCE_UI_RECORD_NAME,
        SCENE_PREFERENCE_UI_RECORD_TYPE,
        SCENE_PREFERENCE_UI_RETENTION_DAYS,
        SCENE_PREFERENCE_UI_SOURCE,
        SCENE_PREFERENCE_UI_STATUS,
        build_scene_preference_ui,
    )

    ui = build_scene_preference_ui(ts="2026-06-08T12:30:00+10:00")
    if ui["source"] != SCENE_PREFERENCE_UI_SOURCE:
        raise SystemExit("scene preference UI should use canonical source")
    if ui["ui_record_type"] != SCENE_PREFERENCE_UI_RECORD_TYPE:
        raise SystemExit("scene preference UI should use canonical record type")
    if ui["record_name"] != SCENE_PREFERENCE_UI_RECORD_NAME:
        raise SystemExit("scene preference UI should use canonical record name")
    if ui["ui_status"] != SCENE_PREFERENCE_UI_STATUS:
        raise SystemExit("scene preference UI should be ready")

    cards = ui["room_cards"]
    expected_rooms = [
        "sample_room_alpha",
        "sample_room_beta",
        "sample_room_delta",
        "sample_room_epsilon",
        "sample_study_zone",
    ]
    if [card["room"] for card in cards] != expected_rooms:
        raise SystemExit("scene preference UI should include lighting rooms in order")
    if any(card["room"] == "sample_storage_zone" for card in cards):
        raise SystemExit("scene preference UI should exclude non-lighting sample entries")
    if cards[0]["available_controls"] != ["day_scene", "night_scene", "manual_override_minutes"]:
        raise SystemExit("white-only room controls should stay minimal")
    if "color_scene_toggle" not in cards[2]["available_controls"]:
        raise SystemExit("color-capable sample_room_delta should expose color controls")
    if "color_scene_toggle" not in cards[4]["available_controls"]:
        raise SystemExit("color-capable sample_study_zone should expose color controls")
    if cards[0]["manual_override_minutes"] != 120:
        raise SystemExit("sample_room_alpha override minutes should be preserved")
    if cards[1]["manual_override_minutes"] != 60:
        raise SystemExit("sample_room_beta override minutes should be preserved")
    if cards[3]["manual_override_minutes"] != 30:
        raise SystemExit("sample_room_epsilon override minutes should be preserved")
    if ui["summary"]["room_count"] != 5:
        raise SystemExit("scene preference UI should report room count")
    if ui["summary"]["color_room_count"] != 2:
        raise SystemExit("scene preference UI should report color-capable rooms")
    if ui["summary"]["white_only_room_count"] != 3:
        raise SystemExit("scene preference UI should report white-only rooms")
    expected_dashboard_id = "scene_preference_ui::sha256:" + hashlib.sha256(
        json.dumps(
            {
                "focus_room_id": None,
                "room_cards": cards,
            },
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    if ui["dashboard_id"] != expected_dashboard_id:
        raise SystemExit("scene preference UI should use a deterministic sha256 dashboard id")
    if "sample_room_delta" in ui["dashboard_id"] or "scene_day_social" in ui["dashboard_id"]:
        raise SystemExit("scene preference dashboard id should not expose raw room telemetry")

    retention = ui.get("retention")
    if not isinstance(retention, dict) or retention.get("days") != 90:
        raise SystemExit("scene preference UI should include 90-day retention")
    if retention.get("immutable") is not True:
        raise SystemExit("scene preference UI retention should be immutable")
    if SCENE_PREFERENCE_UI_RETENTION_DAYS != 90:
        raise SystemExit("scene preference UI retention constant should be 90 days")

    focused = build_scene_preference_ui(focus_room_id="sample_study_zone")
    if focused["focus_room_id"] != "sample_study_zone":
        raise SystemExit("focus room should normalize to lowercase canonical room id")
    if focused != build_scene_preference_ui(focus_room_id="sample_study_zone"):
        raise SystemExit("identical focus inputs should yield identical dashboard models")

    try:
        build_scene_preference_ui(focus_room_id="sample_storage_zone")
    except ValueError:
        pass
    else:
        raise SystemExit("invalid focus_room_id should be rejected")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_scene_preference_ui.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Scene preference UI check passed"
        if sys.argv[1] == "check"
        else "Scene preference UI quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
