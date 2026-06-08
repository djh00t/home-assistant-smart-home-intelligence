#!/usr/bin/env python3
"""Validate the phase 0 contract bundle."""

from __future__ import annotations

from json import loads
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    ROOT / "config/inventory/rooms.yaml",
    ROOT / "config/inventory/room_capabilities.yaml",
    ROOT / "config/contracts/mqtt_topics.yaml",
    ROOT / "config/contracts/presence_bridge.yaml",
    ROOT / "config/contracts/room_fsm.yaml",
    ROOT / "config/contracts/dwell_reset.yaml",
    ROOT / "config/contracts/white_lighting.yaml",
    ROOT / "config/contracts/color_sync.yaml",
    ROOT / "config/contracts/bed_state_override.yaml",
    ROOT / "config/contracts/house_mode.yaml",
    ROOT / "config/contracts/person_tracker.yaml",
    ROOT / "config/contracts/person_room_assignment.yaml",
    ROOT / "config/contracts/desk_light_profiles.yaml",
    ROOT / "config/contracts/climate_person_profiles.yaml",
    ROOT / "config/contracts/mmwave_fusion.yaml",
    ROOT / "config/contracts/pet_detection_classifier.yaml",
    ROOT / "config/contracts/driveway_zone_setup.yaml",
    ROOT / "config/contracts/anpr_service_and_event.yaml",
    ROOT / "config/contracts/face_enrollment_and_match.yaml",
    ROOT / "config/contracts/vehicle_person_linking.yaml",
    ROOT / "config/contracts/pram_walking_vs_driving.yaml",
    ROOT / "config/contracts/presence_event.schema.json",
    ROOT / "config/policies/retention.yaml",
    ROOT / "docs/contracts/phase0-foundation.md",
    ROOT / "docs/contracts/mqtt-presence-bridge.md",
    ROOT / "docs/contracts/room-fsm-template.md",
    ROOT / "docs/contracts/dwell-reset-automation.md",
    ROOT / "docs/contracts/adaptive-white-lighting.md",
    ROOT / "docs/contracts/color-sync-for-color-lights.md",
    ROOT / "docs/contracts/bed-state-override.md",
    ROOT / "docs/contracts/empty-house-with-pet-mode-switch.md",
    ROOT / "docs/contracts/person-tracker-integration.md",
    ROOT / "docs/contracts/person-room-assignment.md",
    ROOT / "docs/contracts/climate-person-profiles.md",
    ROOT / "docs/contracts/mmwave-fusion-rule.md",
    ROOT / "docs/contracts/pet-detection-classifier.md",
    ROOT / "docs/contracts/driveway-zone-setup.md",
    ROOT / "docs/contracts/anpr-service-and-event.md",
    ROOT / "docs/contracts/face-enrollment-and-match.md",
    ROOT / "docs/contracts/vehicle-person-linking.md",
    ROOT / "docs/contracts/pram-walking-vs-driving.md",
]
REQUIRED_ROOMS = [
    "hall",
    "kitchen",
    "living_room",
    "office",
    "master_bedroom",
    "driveway",
]
REQUIRED_CAPABILITY_LINES = [
    "room_id: hall",
    "room_id: kitchen",
    "room_id: living_room",
    "room_id: office",
    "room_id: master_bedroom",
    "room_id: driveway",
    "supports_lighting: true",
    "supports_lighting: false",
    "supports_color: true",
    "supports_color: false",
]
REQUIRED_TOPICS = [
    "ha/presence/event",
    "ha/presence/event/dlq",
]
REQUIRED_BRIDGE_LINES = [
    "canonical_topic: ha/presence/event",
    "dead_letter_topic: ha/presence/event/dlq",
    "mwave: mmwave",
    "bedroom_master: master_bedroom",
]
REQUIRED_FSM_LINES = [
    "empty",
    "humans_only",
    "pets_only",
    "mixed",
    "sleeping",
    "bed_motion_only",
]
REQUIRED_DWELL_LINES = [
    "motion",
    "mmwave",
    "frigate",
    "restart_timer",
    "dim",
    "off",
]
REQUIRED_WHITE_LINES = [
    "manual_override_suppresses_auto_on: true",
    "bed_motion_only_never_full_brightens: true",
    "preserve_hue_temperature_policy: true",
    "morning",
    "day",
    "evening",
    "night",
]
REQUIRED_COLOR_LINES = [
    "color_scenes_only_target_color_capable_groups: true",
    "white_only_rooms_skip_color_sync: true",
    "preserve_white_lighting_for_color_scene_requests: true",
]
REQUIRED_BED_LINES = [
    "awake",
    "sleeping",
    "bed_motion_only",
    "suppress_wake_scene_while_bed_motion_only: true",
    "suppress_wake_scene_while_sleeping: true",
    "clear_override_on_exit_event: true",
]
REQUIRED_HOUSE_LINES = [
    "empty",
    "pet_mode",
    "occupied",
    "pets_only_selects_pet_mode: true",
    "humans_present_forces_occupied: true",
    "pet_mode_may_keep_pathway_lighting: true",
]
REQUIRED_TRACKER_LINES = [
    "mobile_app",
    "ble",
    "geofencing",
    "home",
    "not_home",
    "arriving",
    "leaving",
]
REQUIRED_PERSON_ROOM_LINES = [
    "occupied_humans",
    "face+tracker",
    "occupancy_fallback",
    "face_tracker_agreement_requires_occupant_match: true",
    "face_match_prefers_face_source: true",
    "tracker_match_prefers_tracker_source: true",
    "single_occupant_fallback_allowed: true",
    "preserve_room_context: true",
    "preserve_occupied_humans: true",
    "person_targeted_automations: false",
]
REQUIRED_DESK_LIGHT_LINES = [
    "room_id",
    "assigned_person",
    "assignment_source",
    "confidence",
    "desk_profiles",
    "office_only_resolution: true",
    "assignment_required_for_resolution: true",
    "should_apply_marks_planning_only: true",
    "preserve_room_context: true",
    "preserve_assigned_person: true",
    "preserve_assignment_source: true",
    "preserve_confidence: true",
]
REQUIRED_CLIMATE_LINES = [
    "room_id",
    "assigned_person",
    "assignment_source",
    "confidence",
    "climate_profiles",
    "assignment_required_for_resolution: true",
    "mapping_required_for_apply: true",
    "should_apply_marks_planning_only: true",
    "preserve_room_context: true",
    "preserve_assigned_person: true",
    "preserve_assignment_source: true",
    "preserve_confidence: true",
    "preserve_climate_profiles: true",
]
REQUIRED_PET_LINES = [
    "cat",
    "dog",
    "pet",
    "canonical_entity_class: pet",
    "preserve_room_context: true",
    "preserve_confidence: true",
    "pet_only_affects_pet_occupancy: true",
    "person_targeted_automations: false",
]
REQUIRED_MMWAVE_LINES = [
    "mmwave",
    "frigate",
    "mmwave_takes_priority_for_room_presence: true",
    "frigate_provides_continuity_only: true",
    "fused_room_state_drives_room_automation: true",
]
REQUIRED_ANPR_LINES = [
    "behavior: canonicalization_only",
    "no_face_linkage",
    "no_foreign_plate_queue",
    "no_vehicle_person_linking",
    "canonical_room_id: driveway",
    "source: anpr",
    "entity_class: vehicle",
    "room_reference_required: true",
    "plate_transform: uppercase_strip_separators",
    "plate_confidence_range: [0.0, 1.0]",
    "vehicle_type_fallback: unknown",
    "mapping_source: driveway_zone_setup",
]
REQUIRED_VEHICLE_PERSON_LINKING_LINES = [
    "behavior: deterministic_linking",
    "canonical_room_id: driveway",
    "room_reference_required: true",
    "plate_confidence_threshold: 0.8",
    "face_match_confidence_threshold: 0.75",
    "arrival: vehicle_arrival",
    "departure: vehicle_departure",
]
REQUIRED_PRAM_LINES = [
    "behavior: deterministic_classification",
    "planning_only: true",
    "vehicle_context_window_seconds: 90",
    "with_pram_false: not_pram",
    "with_pram_true_match_within_window: drive",
    "with_pram_true_no_match_or_stale: walk",
]
REQUIRED_FACE_LINES = [
    "canonicalization_only",
    "backlog_boundary:",
    "no_vehicle_person_linking",
    "no_camera_only_unlock_actions",
    "no_door_or_lock_actuation",
    "no_face_match_as_only_unlock_signal",
    "deterministic_threshold: 0.75",
    "retention_days: 90",
    "source: face",
    "entity_class: human",
    "room_reference_required: true",
    "output_event_type: confidence",
]
REQUIRED_RETENTION_LINES = [
    "event_records: 90",
    "room_state_history: 90",
    "person_vehicle_links: 90",
    "face_plate_audit: 90",
    "media_metadata: 90",
    "foreign_plate_person_alerts: 90",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        print("Missing required contract files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_rooms() -> None:
    text = (ROOT / "config/inventory/rooms.yaml").read_text(encoding="utf-8")
    missing = [room for room in REQUIRED_ROOMS if f"room_id: {room}" not in text]
    if missing:
        print("Missing required room ids:")
        for room in missing:
            print(room)
        raise SystemExit(1)


def validate_capabilities() -> None:
    text = (ROOT / "config/inventory/room_capabilities.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_CAPABILITY_LINES if line not in text]
    if missing:
        print("Missing required room capability entries:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_topics() -> None:
    text = (ROOT / "config/contracts/mqtt_topics.yaml").read_text(encoding="utf-8")
    missing = [topic for topic in REQUIRED_TOPICS if topic not in text]
    if missing:
        print("Missing required MQTT topics:")
        for topic in missing:
            print(topic)
        raise SystemExit(1)


def validate_bridge_contract() -> None:
    text = (ROOT / "config/contracts/presence_bridge.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_BRIDGE_LINES if line not in text]
    if missing:
        print("Missing bridge contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_room_fsm_contract() -> None:
    text = (ROOT / "config/contracts/room_fsm.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_FSM_LINES if line not in text]
    if missing:
        print("Missing room FSM lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_dwell_contract() -> None:
    text = (ROOT / "config/contracts/dwell_reset.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_DWELL_LINES if line not in text]
    if missing:
        print("Missing dwell reset contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_white_contract() -> None:
    text = (ROOT / "config/contracts/white_lighting.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_WHITE_LINES if line not in text]
    if missing:
        print("Missing white lighting contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_color_contract() -> None:
    text = (ROOT / "config/contracts/color_sync.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_COLOR_LINES if line not in text]
    if missing:
        print("Missing color sync contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_bed_contract() -> None:
    text = (ROOT / "config/contracts/bed_state_override.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_BED_LINES if line not in text]
    if missing:
        print("Missing bed state override contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_house_contract() -> None:
    text = (ROOT / "config/contracts/house_mode.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_HOUSE_LINES if line not in text]
    if missing:
        print("Missing house mode contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_tracker_contract() -> None:
    text = (ROOT / "config/contracts/person_tracker.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_TRACKER_LINES if line not in text]
    if missing:
        print("Missing person tracker contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_person_room_contract() -> None:
    text = (ROOT / "config/contracts/person_room_assignment.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_PERSON_ROOM_LINES if line not in text]
    if missing:
        print("Missing person room assignment contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_desk_light_contract() -> None:
    text = (ROOT / "config/contracts/desk_light_profiles.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_DESK_LIGHT_LINES if line not in text]
    if missing:
        print("Missing desk light profile contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_climate_contract() -> None:
    text = (ROOT / "config/contracts/climate_person_profiles.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_CLIMATE_LINES if line not in text]
    if missing:
        print("Missing climate person profile contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_pet_contract() -> None:
    text = (ROOT / "config/contracts/pet_detection_classifier.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_PET_LINES if line not in text]
    if missing:
        print("Missing pet classifier contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_mmwave_contract() -> None:
    text = (ROOT / "config/contracts/mmwave_fusion.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_MMWAVE_LINES if line not in text]
    if missing:
        print("Missing mmWave fusion contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_anpr_contract() -> None:
    text = (ROOT / "config/contracts/anpr_service_and_event.yaml").read_text(
        encoding="utf-8"
    )
    missing = [line for line in REQUIRED_ANPR_LINES if line not in text]
    if missing:
        print("Missing ANPR service contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_vehicle_person_linking_contract() -> None:
    text = (ROOT / "config/contracts/vehicle_person_linking.yaml").read_text(
        encoding="utf-8"
    )
    missing = [
        line for line in REQUIRED_VEHICLE_PERSON_LINKING_LINES if line not in text
    ]
    if missing:
        print("Missing vehicle-person linking contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_pram_contract() -> None:
    text = (ROOT / "config/contracts/pram_walking_vs_driving.yaml").read_text(
        encoding="utf-8"
    )
    missing = [line for line in REQUIRED_PRAM_LINES if line not in text]
    if missing:
        print("Missing pram walking-vs-driving contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_face_contract() -> None:
    text = (ROOT / "config/contracts/face_enrollment_and_match.yaml").read_text(
        encoding="utf-8"
    )
    missing = [line for line in REQUIRED_FACE_LINES if line not in text]
    if missing:
        print("Missing face enrollment and match contract lines:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def validate_schema() -> None:
    schema_path = ROOT / "config/contracts/presence_event.schema.json"
    schema = loads(schema_path.read_text(encoding="utf-8"))

    required_keys = {
        "event_id",
        "source",
        "type",
        "room",
        "entity_class",
        "confidence",
        "ts",
    }
    if set(schema.get("required", [])) != required_keys:
        raise SystemExit("presence_event.schema.json has unexpected required keys")

    properties = schema.get("properties", {})
    source_enum = properties.get("source", {}).get("enum", [])
    type_enum = properties.get("type", {}).get("enum", [])
    room_enum = properties.get("room", {}).get("enum", [])
    entity_class_enum = properties.get("entity_class", {}).get("enum", [])

    if source_enum != ["frigate", "mmwave", "motion", "face", "anpr", "tracker"]:
        raise SystemExit("presence_event.schema.json has unexpected source enum")
    if type_enum != ["enter", "leave", "stay", "state_change", "confidence"]:
        raise SystemExit("presence_event.schema.json has unexpected type enum")
    if entity_class_enum != ["human", "pet", "vehicle"]:
        raise SystemExit("presence_event.schema.json has unexpected entity_class enum")
    if room_enum != REQUIRED_ROOMS:
        raise SystemExit("presence_event.schema.json has unexpected room enum")

    if schema.get("additionalProperties") is not False:
        raise SystemExit("presence_event.schema.json must forbid additionalProperties")


def validate_retention() -> None:
    text = (ROOT / "config/policies/retention.yaml").read_text(encoding="utf-8")
    missing = [line for line in REQUIRED_RETENTION_LINES if line not in text]
    if missing:
        print("Missing retention requirements:")
        for line in missing:
            print(line)
        raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_contracts.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_rooms()
    validate_capabilities()
    validate_topics()
    validate_bridge_contract()
    validate_room_fsm_contract()
    validate_dwell_contract()
    validate_white_contract()
    validate_color_contract()
    validate_bed_contract()
    validate_house_contract()
    validate_tracker_contract()
    validate_person_room_contract()
    validate_desk_light_contract()
    validate_climate_contract()
    validate_pet_contract()
    validate_mmwave_contract()
    validate_anpr_contract()
    validate_face_contract()
    validate_vehicle_person_linking_contract()
    validate_pram_contract()
    validate_schema()
    validate_retention()

    print(
        "Phase 0 contract bundle check passed"
        if sys.argv[1] == "check"
        else "Phase 0 contract bundle quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
