#!/usr/bin/env python3
"""Validate feature file discoverability and basic Gherkin structure."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
FEATURE_DIR = ROOT / "tests" / "features"
REQUIRED_FEATURE_FILES = [
    FEATURE_DIR / "adaptive_white_lighting.feature",
    FEATURE_DIR / "bed_state_override.feature",
    FEATURE_DIR / "color_sync_for_color_lights.feature",
    FEATURE_DIR / "dwell_reset_automation.feature",
    FEATURE_DIR / "empty_house_with_pet_mode_switch.feature",
    FEATURE_DIR / "mqtt_presence_bridge.feature",
    FEATURE_DIR / "mmwave_fusion_rule.feature",
    FEATURE_DIR / "pet_detection_classifier.feature",
    FEATURE_DIR / "person_tracker_integration.feature",
    FEATURE_DIR / "person_room_assignment.feature",
    FEATURE_DIR / "phase0_foundation.feature",
    FEATURE_DIR / "presence_fsm_room_template.feature",
    FEATURE_DIR / "smart_home_presence.feature",
]
STEP_PREFIXES = ("Given ", "When ", "Then ", "And ", "But ")
SCENARIO_PREFIXES = ("Scenario:", "Scenario Outline:")


def discover_feature_files() -> list[Path]:
    return sorted(FEATURE_DIR.glob("*.feature"))


def validate_discoverability(feature_files: list[Path]) -> None:
    if not FEATURE_DIR.exists():
        raise SystemExit(f"Missing feature directory: {FEATURE_DIR.relative_to(ROOT)}")

    if not feature_files:
        raise SystemExit(f"No feature files found in {FEATURE_DIR.relative_to(ROOT)}")

    discovered = set(feature_files)
    missing = [path for path in REQUIRED_FEATURE_FILES if path not in discovered]
    if missing:
        print("Missing required feature files:")
        for path in missing:
            print(path.relative_to(ROOT))
        raise SystemExit(1)


def validate_feature_structure(feature_path: Path) -> None:
    lines = feature_path.read_text(encoding="utf-8").splitlines()
    if not any(line.startswith("Feature:") for line in lines):
        raise SystemExit(f"{feature_path.relative_to(ROOT)}: missing Feature header")

    scenario_indexes = [
        index for index, line in enumerate(lines) if line.lstrip().startswith(SCENARIO_PREFIXES)
    ]
    if not scenario_indexes:
        raise SystemExit(f"{feature_path.relative_to(ROOT)}: missing Scenario content")

    for scenario_index, start in enumerate(scenario_indexes):
        end = scenario_indexes[scenario_index + 1] if scenario_index + 1 < len(scenario_indexes) else len(lines)
        scenario_lines = lines[start + 1 : end]
        has_step = any(
            line.startswith("    ") and line.lstrip().startswith(STEP_PREFIXES)
            for line in scenario_lines
        )
        if not has_step:
            line_number = start + 1
            raise SystemExit(
                f"{feature_path.relative_to(ROOT)}: scenario at line {line_number} has no steps"
            )


def main() -> int:
    feature_files = discover_feature_files()
    validate_discoverability(feature_files)

    for feature_file in feature_files:
        validate_feature_structure(feature_file)

    print(f"Validated {len(feature_files)} feature files under tests/features")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
