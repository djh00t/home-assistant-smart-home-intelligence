#!/usr/bin/env python3
"""Validate the HACS integration package scaffold."""

from __future__ import annotations

import json
from pathlib import Path
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
    INTEGRATION_ROOT / "data" / "room_capabilities.yaml",
    INTEGRATION_ROOT / "data" / "rooms.yaml",
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
        "Manual override is surfaced as a binary sensor",
        "Policy entities register through the sensor platform",
        "Packaged defaults support reload contracts after HACS install",
        "Runtime state is serializable for restore",
    ):
        if needle not in text:
            raise SystemExit(f"{feature.relative_to(ROOT)} missing scenario text: {needle}")


def validate_home_assistant_platforms() -> None:
    const_text = (INTEGRATION_ROOT / "const.py").read_text(encoding="utf-8")
    sensor_text = (INTEGRATION_ROOT / "sensor.py").read_text(encoding="utf-8")
    if '"policy_sensor"' in const_text:
        raise SystemExit("room policy entities must register through the sensor platform")
    if "build_policy_sensor_entities" not in sensor_text:
        raise SystemExit("sensor.py must register room policy entities")


def validate_policy_feature_file() -> None:
    feature = ROOT / "tests" / "features" / "hacs_room_policy_entities.feature"
    text = feature.read_text(encoding="utf-8")
    for needle in (
        "House mode reflects tracked occupancy",
        "Room policy sensors expose white scenes and color sync state",
        "Room policy sensors restore from runtime state",
    ):
        if needle not in text:
            raise SystemExit(f"{feature.relative_to(ROOT)} missing scenario text: {needle}")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_hacs_package.py [check|quality-gates]")
        return 2

    validate_required_files()
    validate_repository_structure()
    validate_hacs_json()
    validate_manifest()
    validate_home_assistant_platforms()
    validate_feature_file()
    validate_entity_feature_file()
    validate_policy_feature_file()

    print(
        "HACS package check passed"
        if sys.argv[1] == "check"
        else "HACS package quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
