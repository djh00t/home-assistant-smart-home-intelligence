SHELL := /bin/bash

.PHONY: check quality-gates install clean build publish

check:
	@python3 scripts/validate_docs.py check
	@python3 scripts/validate_project.py check
	@python3 scripts/validate_hacs_package.py check
	@python3 scripts/validate_contracts.py check
	@python3 scripts/validate_anpr_service_and_event.py check
	@python3 scripts/validate_features.py check
	@python3 scripts/validate_bridge.py check
	@python3 scripts/validate_room_fsm.py check
	@python3 scripts/validate_dwell_reset.py check
	@python3 scripts/validate_white_lighting.py check
	@python3 scripts/validate_color_sync.py check
	@python3 scripts/validate_bed_state_override.py check
	@python3 scripts/validate_house_mode.py check
	@python3 scripts/validate_person_tracker.py check
	@python3 scripts/validate_person_room_assignment.py check
	@python3 scripts/validate_desk_light_profiles.py check
	@python3 scripts/validate_climate_person_profiles.py check
	@python3 scripts/validate_mmwave_fusion.py check
	@python3 scripts/validate_face_enrollment_and_match.py check
	@python3 scripts/validate_pet_classifier.py check
	@python3 scripts/validate_driveway_zone_setup.py check
	@python3 scripts/validate_vehicle_person_linking.py check
	@python3 scripts/validate_foreign_identity_log_queue.py check
	@python3 scripts/validate_multi_room_heatmap.py check
	@python3 scripts/validate_scene_preference_ui.py check
	@python3 scripts/validate_anomaly_and_false_action_dashboard.py check
	@python3 scripts/validate_non_home_zone_queue.py check
	@python3 scripts/validate_pram_walking_vs_driving.py check
	@python3 scripts/validate_security_and_retention_jobs.py check

quality-gates: check
	@python3 scripts/validate_docs.py quality-gates
	@python3 scripts/validate_project.py quality-gates
	@python3 scripts/validate_hacs_package.py quality-gates
	@python3 scripts/validate_contracts.py quality-gates
	@python3 scripts/validate_anpr_service_and_event.py quality-gates
	@python3 scripts/validate_features.py quality-gates
	@python3 scripts/validate_bridge.py quality-gates
	@python3 scripts/validate_room_fsm.py quality-gates
	@python3 scripts/validate_dwell_reset.py quality-gates
	@python3 scripts/validate_white_lighting.py quality-gates
	@python3 scripts/validate_color_sync.py quality-gates
	@python3 scripts/validate_bed_state_override.py quality-gates
	@python3 scripts/validate_house_mode.py quality-gates
	@python3 scripts/validate_person_tracker.py quality-gates
	@python3 scripts/validate_person_room_assignment.py quality-gates
	@python3 scripts/validate_desk_light_profiles.py quality-gates
	@python3 scripts/validate_climate_person_profiles.py quality-gates
	@python3 scripts/validate_mmwave_fusion.py quality-gates
	@python3 scripts/validate_face_enrollment_and_match.py quality-gates
	@python3 scripts/validate_pet_classifier.py quality-gates
	@python3 scripts/validate_driveway_zone_setup.py quality-gates
	@python3 scripts/validate_vehicle_person_linking.py quality-gates
	@python3 scripts/validate_foreign_identity_log_queue.py quality-gates
	@python3 scripts/validate_multi_room_heatmap.py quality-gates
	@python3 scripts/validate_scene_preference_ui.py quality-gates
	@python3 scripts/validate_anomaly_and_false_action_dashboard.py quality-gates
	@python3 scripts/validate_non_home_zone_queue.py quality-gates
	@python3 scripts/validate_pram_walking_vs_driving.py quality-gates
	@python3 scripts/validate_security_and_retention_jobs.py quality-gates

install:
	@python3 -m venv .venv

clean:
	@rm -rf .venv dist __pycache__ .pytest_cache .mypy_cache .ruff_cache htmlcov

build:
	@mkdir -p dist
	@printf '%s\n' 'Phase 0 foundation bundle; no compiled artifact.' > dist/build.txt

publish: build
	@printf '%s\n' 'No publish target configured for this phase 0 foundation bundle.'
