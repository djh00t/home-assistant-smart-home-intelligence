#!/usr/bin/env python3
"""Validate the HACS integration package scaffold."""

from __future__ import annotations

import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
import sys


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_ROOT = ROOT / "custom_components" / "smart_home_presence_intelligence"
REQUIRED_FILES = [
    ROOT / "hacs.json",
    ROOT / "brand" / "icon.png",
    INTEGRATION_ROOT / "__init__.py",
    INTEGRATION_ROOT / "binary_sensor.py",
    INTEGRATION_ROOT / "bridge.py",
    INTEGRATION_ROOT / "const.py",
    INTEGRATION_ROOT / "config_flow.py",
    INTEGRATION_ROOT / "diagnostics.py",
    INTEGRATION_ROOT / "manifest.json",
    INTEGRATION_ROOT / "policy_sensor.py",
    INTEGRATION_ROOT / "repair.py",
    INTEGRATION_ROOT / "runtime.py",
    INTEGRATION_ROOT / "sensor.py",
    INTEGRATION_ROOT / "services.yaml",
    INTEGRATION_ROOT / "strings.json",
    INTEGRATION_ROOT / "translations" / "en.json",
    ROOT / "tests" / "features" / "hacs_package_management.feature",
    ROOT / "tests" / "features" / "hacs_integration_entities.feature",
    ROOT / "tests" / "features" / "hacs_room_policy_entities.feature",
]


def validate_required_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        print("Missing HACS package files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_repository_structure() -> None:
    custom_components = ROOT / "custom_components"
    if not custom_components.exists():
        raise SystemExit("custom_components directory is missing")

    integration_dirs = [
        path
        for path in custom_components.iterdir()
        if path.is_dir() and not path.name.startswith(".")
    ]
    if integration_dirs != [INTEGRATION_ROOT]:
        print("HACS integration repositories must contain exactly one integration directory:")
        for path in integration_dirs:
            print(path.relative_to(ROOT))
        raise SystemExit(1)


def validate_hacs_json() -> None:
    data = json.loads((ROOT / "hacs.json").read_text(encoding="utf-8"))
    if data.get("name") != "Smart Home Presence Intelligence":
        raise SystemExit("hacs.json name does not match the integration display name")
    if data.get("category") != "integration":
        raise SystemExit("hacs.json category must be integration")


def validate_manifest() -> None:
    data = json.loads((INTEGRATION_ROOT / "manifest.json").read_text(encoding="utf-8"))
    for key in ("domain", "documentation", "issue_tracker", "codeowners", "name", "version"):
        if key not in data:
            raise SystemExit(f"manifest.json missing required key: {key}")
    if data["domain"] != "smart_home_presence_intelligence":
        raise SystemExit("manifest domain is not smart_home_presence_intelligence")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if data["version"] != version:
        raise SystemExit("manifest version does not match VERSION")
    if "mqtt" not in data.get("dependencies", []):
        raise SystemExit("manifest should depend on mqtt")


def validate_feature_file() -> None:
    feature = ROOT / "tests" / "features" / "hacs_package_management.feature"
    text = feature.read_text(encoding="utf-8")
    for needle in (
        "HACS custom integration",
        "integration version is aligned",
        "upgrade and removal via HACS",
    ):
        if needle not in text:
            raise SystemExit(f"{feature.relative_to(ROOT)} missing scenario text: {needle}")


def validate_entity_feature_file() -> None:
    feature = ROOT / "tests" / "features" / "hacs_integration_entities.feature"
    text = feature.read_text(encoding="utf-8")
    for needle in (
        "Room activity sensors reflect routed events",
        "lounge room state sensor should not expose room telemetry attributes",
        "Manual override is surfaced as a binary sensor",
        "Runtime state only persists restore-safe fields",
        "Diagnostics export respects the diagnostics toggle",
    ):
        if needle not in text:
            raise SystemExit(f"{feature.relative_to(ROOT)} missing scenario text: {needle}")


def validate_policy_feature_file() -> None:
    feature = ROOT / "tests" / "features" / "hacs_room_policy_entities.feature"
    text = feature.read_text(encoding="utf-8")
    for needle in (
        "House mode reflects tracked occupancy",
        "Room policy sensors expose white scenes and color sync state",
        "bedroom spare white scene sensor should not expose room policy telemetry",
        "House mode policy sensors minimize extra attributes",
        "house mode policy sensor should not expose supported rooms or refresh timestamps",
        "Room policy sensors restore from runtime state",
    ):
        if needle not in text:
            raise SystemExit(f"{feature.relative_to(ROOT)} missing scenario text: {needle}")


def validate_entity_attribute_minimization() -> None:
    sys.path.insert(0, str(ROOT))
    from custom_components.smart_home_presence_intelligence.policy_sensor import (  # noqa: WPS433
        RUNTIME_POLICY_SPECS,
        RoomPolicySensor,
        _room_policy_specs,
    )
    from custom_components.smart_home_presence_intelligence.runtime import (  # noqa: WPS433
        IntegrationRuntime,
        IntegrationSettings,
    )
    from custom_components.smart_home_presence_intelligence.sensor import (  # noqa: WPS433
        ROOM_SENSOR_SPECS,
        RuntimeSensor,
    )

    settings = IntegrationSettings(
        mqtt_topic_prefix="ha/presence",
        room_inventory_path="config/inventory/rooms.yaml",
        room_capabilities_path="config/inventory/room_capabilities.yaml",
        retention_days=90,
        enable_diagnostics=True,
    )
    runtime = IntegrationRuntime(settings=settings)
    runtime.room_activity["room_delta"].update({"state": "occupied", "human_count": 1})
    runtime.room_activity["room_gamma"].update({"state": "occupied", "human_count": 1})

    room_delta_spec = next(spec for spec in ROOM_SENSOR_SPECS if spec.key == "room_room_delta_state")
    room_delta_sensor = RuntimeSensor(runtime=runtime, entry_id="entry-1", spec=room_delta_spec)
    if room_delta_sensor.native_value != "occupied":
        raise SystemExit("room state sensor should preserve its primary occupied state")
    if room_delta_sensor.extra_state_attributes:
        raise SystemExit("room state sensor should not expose room telemetry attributes")

    bedroom_white_scene_spec = next(
        spec for spec in _room_policy_specs("room_gamma") if spec.key == "room_room_gamma_white_scene"
    )
    bedroom_white_scene_sensor = RoomPolicySensor(
        runtime=runtime,
        entry_id="entry-1",
        spec=bedroom_white_scene_spec,
    )
    if bedroom_white_scene_sensor.native_value == "none":
        raise SystemExit("room policy sensor should preserve its primary white-scene state")
    if bedroom_white_scene_sensor.extra_state_attributes:
        raise SystemExit("room policy sensor should not expose room policy telemetry")

    house_mode_spec = next(spec for spec in RUNTIME_POLICY_SPECS if spec.key == "house_mode")
    house_mode_sensor = RoomPolicySensor(runtime=runtime, entry_id="entry-1", spec=house_mode_spec)
    if house_mode_sensor.native_value != "occupied":
        raise SystemExit("house mode sensor should preserve its primary occupied state")
    if house_mode_sensor.extra_state_attributes:
        raise SystemExit("house mode policy sensor should not expose supported rooms or refresh timestamps")


def validate_runtime_privacy_contract() -> None:
    text = (ROOT / "config" / "contracts" / "hacs_package_management.yaml").read_text(
        encoding="utf-8"
    )
    for needle in (
        "diagnostics_redacted: true",
        "diagnostics_respects_enable_toggle: true",
        "restore_state_minimal_fields:",
        "- override_enabled",
        "- bridge_health",
        "- retention_audit_status",
        "- retention_audit_message",
    ):
        if needle not in text:
            raise SystemExit(f"hacs_package_management.yaml missing {needle}")


def validate_runtime_privacy_behavior() -> None:
    sys.path.insert(0, str(ROOT))
    from custom_components.smart_home_presence_intelligence.const import DOMAIN  # noqa: WPS433
    from custom_components.smart_home_presence_intelligence.diagnostics import (  # noqa: WPS433
        async_get_config_entry_diagnostics,
    )
    from custom_components.smart_home_presence_intelligence.runtime import (  # noqa: WPS433
        IntegrationRuntime,
        IntegrationSettings,
    )

    settings = IntegrationSettings(
        mqtt_topic_prefix="ha/presence",
        room_inventory_path="config/inventory/rooms.yaml",
        room_capabilities_path="config/inventory/room_capabilities.yaml",
        retention_days=90,
        enable_diagnostics=True,
    )
    runtime = IntegrationRuntime(settings=settings)
    runtime.set_override(enabled=True, reason="quiet hours")
    runtime.retention_audit_status = "pass"
    runtime.retention_audit_message = "audit_ok"
    runtime.room_activity["room_delta"].update(
        {
            "state": "occupied",
            "human_count": 1,
            "last_event_type": "enter",
            "last_source": "frigate",
            "last_entity_class": "human",
            "last_confidence": 0.91,
            "last_seen": "2026-06-10T08:00:00+10:00",
        }
    )
    runtime.last_routed_event = {
        "event": {"event_id": "evt-1", "room": "room_delta"},
        "topic": "ha/presence/event",
    }
    runtime.last_retention_audit = {"retention_days": 90, "audit_ok": True}
    runtime.bridge_last_topic = "ha/presence/event"
    runtime.bridge_last_error = "none"
    payload = runtime.serialize()

    expected_keys = {
        "override_enabled",
        "bridge_health",
        "retention_audit_status",
        "retention_audit_message",
    }
    if set(payload) != expected_keys:
        raise SystemExit(
            "runtime restore payload should only contain minimal restore-safe fields"
        )
    for sensitive_key in (
        "room_activity",
        "last_routed_event",
        "last_retention_audit",
        "bridge_last_topic",
        "bridge_last_error",
        "refreshed_at",
    ):
        if sensitive_key in payload:
            raise SystemExit(f"runtime restore payload leaked {sensitive_key}")

    restored = IntegrationRuntime.from_restore_payload(settings=settings, payload=payload)
    if restored.override_enabled is not True:
        raise SystemExit("restore payload did not preserve manual override state")
    if restored.override_reason != "":
        raise SystemExit("restore payload should not preserve free-text override reasons")
    if restored.bridge_health != runtime.bridge_health:
        raise SystemExit("restore payload did not preserve bridge health")
    if restored.room_activity["room_delta"]["human_count"] != 0:
        raise SystemExit("restore payload should not repopulate room activity telemetry")
    lounge_policy = runtime.room_policy_snapshot("room_delta")
    if lounge_policy["supports_lighting"] is not True:
        raise SystemExit("canonical runtime rooms should still resolve lighting support")
    if lounge_policy["white_scene"] == "none":
        raise SystemExit("canonical runtime rooms should still resolve a sample-backed scene")

    hass = SimpleNamespace(data={DOMAIN: {"entry-1": runtime}})
    enabled_entry = SimpleNamespace(entry_id="entry-1")
    diagnostics = asyncio.run(async_get_config_entry_diagnostics(hass, enabled_entry))[DOMAIN]
    if diagnostics.get("settings") != {
        "mqtt_topic_prefix": "ha/presence",
        "retention_days": 90,
        "enable_diagnostics": True,
    }:
        raise SystemExit("diagnostics settings should be redacted to safe fields")
    for sensitive_key in (
        "room_activity",
        "last_routed_event",
        "last_retention_audit",
        "bridge_last_topic",
        "bridge_last_error",
        "house_mode",
        "total_humans_present",
        "total_pets_present",
        "refreshed_at",
    ):
        if sensitive_key in diagnostics:
            raise SystemExit(f"diagnostics payload leaked {sensitive_key}")

    disabled_settings = IntegrationSettings(
        mqtt_topic_prefix="ha/presence",
        room_inventory_path="config/inventory/rooms.yaml",
        room_capabilities_path="config/inventory/room_capabilities.yaml",
        retention_days=90,
        enable_diagnostics=False,
    )
    disabled_runtime = IntegrationRuntime(settings=disabled_settings)
    hass.data[DOMAIN]["entry-disabled"] = disabled_runtime
    disabled_entry = SimpleNamespace(entry_id="entry-disabled")
    disabled_diagnostics = asyncio.run(
        async_get_config_entry_diagnostics(hass, disabled_entry)
    )[DOMAIN]
    if disabled_diagnostics != {"diagnostics_enabled": False}:
        raise SystemExit("disabled diagnostics should only report the disabled flag")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_hacs_package.py [check|quality-gates]")
        return 2

    validate_required_files()
    validate_repository_structure()
    validate_hacs_json()
    validate_manifest()
    validate_feature_file()
    validate_entity_feature_file()
    validate_policy_feature_file()
    validate_entity_attribute_minimization()
    validate_runtime_privacy_contract()
    validate_runtime_privacy_behavior()

    print(
        "HACS package check passed"
        if sys.argv[1] == "check"
        else "HACS package quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
