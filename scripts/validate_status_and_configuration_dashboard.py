#!/usr/bin/env python3
"""Validate the status and configuration dashboard slice."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/status_and_configuration_dashboard.yaml",
    ROOT / "docs/contracts/status-and-configuration-dashboard.md",
    ROOT / "docs/dashboards/status-and-configuration-dashboard.yaml",
    ROOT / "docs/guides/jetson-xavier-frigate-mqtt.md",
    ROOT / "src/smart_home_presence_intelligence/status_and_configuration_dashboard.py",
    ROOT / "tests/features/status_and_configuration_dashboard.feature",
    ROOT / "README.md",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing status and configuration dashboard files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/status_and_configuration_dashboard.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "behavior: deterministic_status_and_configuration_dashboard",
        "dashboard_artifact: lovelace_yaml",
        "read_only_configuration: true",
        "no_persistent_config_mutation",
        "no_dashboard_backend_mutation",
        "canonical_room_inventory: config/inventory/rooms.yaml",
        "canonical_room_capabilities: config/inventory/room_capabilities.yaml",
        "canonical_topic: ha/presence/event",
        "dead_letter_topic: ha/presence/event/dlq",
        "dashboard_record_type: status_configuration_dashboard",
        "record_name: status_and_configuration_dashboard",
        "dashboard_status: ready",
        "retention_days: 90",
        "immutable: true",
    ):
        if needle not in text:
            raise SystemExit(
                f"status_and_configuration_dashboard.yaml missing required text: {needle}"
            )


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.status_and_configuration_dashboard import (  # noqa: E501
        STATUS_CONFIGURATION_DASHBOARD_RECORD_NAME,
        STATUS_CONFIGURATION_DASHBOARD_RECORD_TYPE,
        STATUS_CONFIGURATION_DASHBOARD_RETENTION_DAYS,
        STATUS_CONFIGURATION_DASHBOARD_SOURCE,
        STATUS_CONFIGURATION_DASHBOARD_STATUS,
        build_status_and_configuration_dashboard,
    )

    class DummyRuntime:
        def __init__(self) -> None:
            self._snapshot = {
                "settings": {
                    "mqtt_topic_prefix": "ha/presence",
                    "room_inventory_path": "config/inventory/rooms.yaml",
                    "room_capabilities_path": "config/inventory/room_capabilities.yaml",
                    "retention_days": 90,
                    "enable_diagnostics": True,
                },
                "override_enabled": True,
                "override_reason": "family activity",
                "bridge_health": "healthy",
                "bridge_last_topic": "ha/presence/event",
                "retention_audit_status": "pass",
                "retention_audit_message": "audit_ok",
                "house_mode": "occupied",
                "total_humans_present": 1,
                "total_pets_present": 0,
                "room_activity": {
                    "lounge_room": {
                        "state": "occupied",
                        "human_count": 1,
                        "pet_count": 0,
                        "vehicle_count": 0,
                        "last_event_type": "enter",
                        "last_source": "frigate",
                        "last_confidence": 0.98,
                        "last_seen": "2026-06-09T12:00:00+10:00",
                    }
                },
                "refreshed_at": "2026-06-09T12:15:00+10:00",
            }

        def snapshot(self) -> dict[str, object]:
            return dict(self._snapshot)

        def room_policy_snapshot(self, room_id: str) -> dict[str, object]:
            room = self._snapshot["room_activity"].get(room_id, {})
            if room_id == "lounge_room":
                return {
                    "room_id": room_id,
                    "house_mode": "occupied",
                    "supports_lighting": True,
                    "supports_color": True,
                    "white_scene": "lounge_room_day",
                    "color_sync_enabled": False,
                    "manual_override_minutes": 45,
                    "person_only_actions": True,
                    "pet_only_actions": True,
                    "occupancy_state": room.get("state", "idle"),
                    "human_count": int(room.get("human_count", 0) or 0),
                    "pet_count": int(room.get("pet_count", 0) or 0),
                    "vehicle_count": int(room.get("vehicle_count", 0) or 0),
                    "last_seen": str(room.get("last_seen", "")),
                }
            return {
                "room_id": room_id,
                "house_mode": "occupied",
                "supports_lighting": room_id not in {"garage", "driveway", "backyard_shed", "backyard_deck"},
                "supports_color": False,
                "white_scene": "none",
                "color_sync_enabled": False,
                "manual_override_minutes": 0,
                "person_only_actions": False,
                "pet_only_actions": False,
                "occupancy_state": room.get("state", "idle"),
                "human_count": int(room.get("human_count", 0) or 0),
                "pet_count": int(room.get("pet_count", 0) or 0),
                "vehicle_count": int(room.get("vehicle_count", 0) or 0),
                "last_seen": str(room.get("last_seen", "")),
            }

    runtime = DummyRuntime()

    dashboard = build_status_and_configuration_dashboard(runtime, ts="2026-06-09T12:30:00+10:00")
    if dashboard["source"] != STATUS_CONFIGURATION_DASHBOARD_SOURCE:
        raise SystemExit("dashboard should use canonical source")
    if dashboard["dashboard_record_type"] != STATUS_CONFIGURATION_DASHBOARD_RECORD_TYPE:
        raise SystemExit("dashboard should use canonical record type")
    if dashboard["record_name"] != STATUS_CONFIGURATION_DASHBOARD_RECORD_NAME:
        raise SystemExit("dashboard should use canonical record name")
    if dashboard["dashboard_status"] != STATUS_CONFIGURATION_DASHBOARD_STATUS:
        raise SystemExit("dashboard should be ready")
    if dashboard["summary"]["room_count"] != 9:
        raise SystemExit("dashboard should include all canonical rooms")
    if dashboard["summary"]["occupied_room_count"] != 1:
        raise SystemExit("dashboard should count occupied rooms")
    if dashboard["summary"]["bridge_health"] != "healthy":
        raise SystemExit("dashboard should surface bridge health")
    if dashboard["summary"]["mqtt_topic_prefix"] != "ha/presence":
        raise SystemExit("dashboard should surface MQTT topic prefix")
    if dashboard["config_snapshot"]["canonical_topic"] != "ha/presence/event":
        raise SystemExit("dashboard should surface canonical topic")
    if dashboard["config_snapshot"]["dead_letter_topic"] != "ha/presence/event/dlq":
        raise SystemExit("dashboard should surface dead-letter topic")

    sections = dashboard["sections"]
    if [section["key"] for section in sections] != [
        "overview",
        "configuration",
        "actions",
        "jetson",
        "rooms",
    ]:
        raise SystemExit("dashboard sections should stay in canonical order")

    room_cards = dashboard["room_cards"]
    if [card["room_id"] for card in room_cards] != [
        "bedroom_master",
        "bedroom_max",
        "bedroom_spare",
        "lounge_room",
        "kitchen",
        "garage",
        "driveway",
        "backyard_shed",
        "backyard_deck",
    ]:
        raise SystemExit("dashboard should include rooms in canonical order")
    lounge_room = room_cards[3]
    if lounge_room["state"] != "occupied":
        raise SystemExit("dashboard should preserve room state")
    if not lounge_room["white_scene"].startswith("lounge_room_"):
        raise SystemExit("dashboard should surface room policy details")

    actions = dashboard["action_cards"]
    if [card["key"] for card in actions] != [
        "publish_test_event",
        "reload_contracts",
        "set_override",
        "run_retention_audit",
    ]:
        raise SystemExit("dashboard should expose the canonical actions")

    repeated = build_status_and_configuration_dashboard(runtime, ts="2026-06-09T12:30:00+10:00")
    if repeated != dashboard:
        raise SystemExit("identical inputs should yield identical dashboards")
    if dashboard["retention"]["days"] != STATUS_CONFIGURATION_DASHBOARD_RETENTION_DAYS:
        raise SystemExit("dashboard retention should be 90 days")

    minimal = build_status_and_configuration_dashboard(
        {
            "settings": {
                "mqtt_topic_prefix": "ha/presence",
                "room_inventory_path": "config/inventory/rooms.yaml",
                "room_capabilities_path": "config/inventory/room_capabilities.yaml",
                "retention_days": 90,
                "enable_diagnostics": False,
            },
            "bridge_health": "unknown",
            "house_mode": "empty",
            "room_activity": {},
        }
    )
    if minimal["room_cards"][0]["state"] != "idle":
        raise SystemExit("missing room state should default to idle")
    if minimal["summary"]["occupied_room_count"] != 0:
        raise SystemExit("empty dashboards should report zero occupied rooms")


def validate_dashboard_yaml() -> None:
    dashboard_path = ROOT / "docs/dashboards/status-and-configuration-dashboard.yaml"
    data = yaml.safe_load(dashboard_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit("dashboard YAML must be a mapping")
    if data.get("title") != "Smart Home Presence Intelligence":
        raise SystemExit("dashboard YAML should use the integration title")
    views = data.get("views", [])
    if not isinstance(views, list) or not views:
        raise SystemExit("dashboard YAML should define at least one view")
    first_view = views[0]
    if not isinstance(first_view, dict):
        raise SystemExit("dashboard view must be a mapping")
    cards = first_view.get("cards", [])
    if not isinstance(cards, list) or not cards:
        raise SystemExit("dashboard YAML should define cards")
    raw_yaml = dashboard_path.read_text(encoding="utf-8")
    for needle in (
        "sensor.bridge_health",
        "sensor.bridge_last_topic",
        "sensor.mqtt_topic_prefix",
        "sensor.room_inventory_path",
        "sensor.room_capabilities_path",
        "sensor.retention_days",
        "binary_sensor.manual_override_active",
        "binary_sensor.diagnostics_enabled",
        "smart_home_presence_intelligence.publish_test_event",
        "smart_home_presence_intelligence.reload_contracts",
        "smart_home_presence_intelligence.set_override",
        "smart_home_presence_intelligence.run_retention_audit",
        "ha/presence/event",
        "ha/presence/event/dlq",
    ):
        if needle not in raw_yaml:
            raise SystemExit(f"dashboard YAML missing required text: {needle}")


def validate_docs_and_readme() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for needle in (
        "Status And Configuration Dashboard",
        "docs/dashboards/status-and-configuration-dashboard.yaml",
        "docs/guides/jetson-xavier-frigate-mqtt.md",
    ):
        if needle not in readme:
            raise SystemExit(f"README missing required text: {needle}")

    guide = (ROOT / "docs/guides/jetson-xavier-frigate-mqtt.md").read_text(
        encoding="utf-8"
    )
    for needle in (
        "Jetson Xavier",
        "Frigate",
        "MQTT",
        "ha/presence/event",
        "ha/presence/event/dlq",
        "publish_test_event",
    ):
        if needle not in guide:
            raise SystemExit(f"Jetson guide missing required text: {needle}")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_status_and_configuration_dashboard.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()
    validate_dashboard_yaml()
    validate_docs_and_readme()

    print(
        "Status and configuration dashboard check passed"
        if sys.argv[1] == "check"
        else "Status and configuration dashboard quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
