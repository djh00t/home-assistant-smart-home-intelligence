# Smart Home Intelligence Repo (Private Project)

This directory now contains the HACS-first Home Assistant integration scaffold for the smart home presence intelligence bundle, plus the earlier phase 0 foundation artifacts and the phase 1 through phase 4 feature bundles:

- [Smart home spec](docs/specs/2026-06-07-smart-home-intelligence-spec.md)
- [HACS package management contract](docs/contracts/hacs-package-management.md)
- [HACS package management feature scenarios](tests/features/hacs_package_management.feature)
- [Roadmap](docs/roadmap/roadmap.md)
- [Implementation plan](docs/plans/implementation-plan.md)
- [Task backlog](docs/tasks/task_backlog.md)
- [Phase 1 occupancy and lighting feature scenarios](tests/features/smart_home_presence.feature)
- [Room FSM feature scenarios](tests/features/presence_fsm_room_template.feature)
- [Dwell reset feature scenarios](tests/features/dwell_reset_automation.feature)
- [Adaptive white-lighting feature scenarios](tests/features/adaptive_white_lighting.feature)
- [Color sync feature scenarios](tests/features/color_sync_for_color_lights.feature)
- [Bed-state override feature scenarios](tests/features/bed_state_override.feature)
- [Person tracker feature scenarios](tests/features/person_tracker_integration.feature)
- [MmWave fusion feature scenarios](tests/features/mmwave_fusion_rule.feature)
- [Pet detection classifier feature scenarios](tests/features/pet_detection_classifier.feature)
- [Person-room assignment feature scenarios](tests/features/person_room_assignment.feature)
- [Desk light profile feature scenarios](tests/features/desk_light_profiles.feature)
- [Climate person profile feature scenarios](tests/features/climate_person_profiles.feature)
- [Empty house with pet mode switch feature scenarios](tests/features/empty_house_with_pet_mode_switch.feature)
- [Driveway zone setup feature scenarios](tests/features/driveway_zone_setup.feature)
- [ANPR service and event feature scenarios](tests/features/anpr_service_and_event.feature)
- [Face enrollment and match feature scenarios](tests/features/face_enrollment_and_match.feature)
- [Vehicle-person linking feature scenarios](tests/features/vehicle_person_linking.feature)
- [Pram walking-vs-driving feature scenarios](tests/features/pram_walking_vs_driving.feature)
- [Foreign identity log queue feature scenarios](tests/features/foreign_identity_log_queue.feature)
- [Security and retention jobs feature scenarios](tests/features/security_and_retention_jobs.feature)
- [Non-home zone queue feature scenarios](tests/features/non_home_zone_queue.feature)
- [Multi-room heatmap feature scenarios](tests/features/multi_room_heatmap.feature)
- [Scene preference UI feature scenarios](tests/features/scene_preference_ui.feature)
- [Anomaly and false-action dashboard feature scenarios](tests/features/anomaly_and_false_action_dashboard.feature)
- [Phase 0 foundation feature scenarios](tests/features/phase0_foundation.feature)

## How this repo is organized

- `config/` — inventory, contract, and retention artifacts for the current release slices.
- `docs/` — specification, roadmap, implementation plan, tasks, and contract notes.
- `scripts/` — validation helpers for docs, project scaffolding, contracts, and features.
- `src/` — the minimal Python package root for future implementation work.
- `tests/features/` — BDD scenarios for behavior and acceptance gates.

## Current status

- Created as an isolated private project folder under your workspace.
- HACS integration packaging and release scaffolding are now checked in locally.
- The HACS integration now exposes room activity, bridge health, override, and retention-status entity scaffolding.
- The HACS integration now also exposes room-policy sensors for house mode and per-room lighting behavior.
- Phase 1 core occupancy and lighting artifacts are now checked in locally.
- Phase 2 people and pet personalization artifacts are now checked in locally.
- Phase 3 vehicle and contextual recognition artifacts are now checked in locally.
- Phase 4 reliability and expansion artifacts are now checked in locally.
- Phase 0 foundation artifacts remain available for the broader project baseline.

## HACS install

1. Add this repository as a custom HACS integration.
2. Install `Smart Home Presence Intelligence` from the HACS integration list.
3. Reload Home Assistant and configure the MQTT topic prefix, room inventory path, and retention settings in the integration options.
4. Keep Frigate, Jetson, ANPR, and any face/plate inference services external; this repository owns the Home Assistant-facing integration and contracts.

## Publish as private GitHub repository

The project is prepared as a local repository bundle under:
- `/Users/djh/work/src/github.com_local/djh00t/smart-home-presence-intelligence`

Run these commands once `gh` auth is valid:

```bash
gh auth login
cd /Users/djh/work/src/github.com_local/djh00t/smart-home-presence-intelligence
gh repo create home-assistant-smart-home-intelligence --private --source . --remote origin --push
```

If you want a different repo name, replace `home-assistant-smart-home-intelligence`.
