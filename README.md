# Smart Home Intelligence Repo (Private Project)

This directory contains the phase 1 core occupancy and lighting bundle, the phase 2 people and pets bundle, and the phase 3 vehicle and contextual recognition bundle for your Home Assistant automation design, plus the earlier phase 0 foundation artifacts:

- [Smart home spec](docs/specs/2026-06-07-smart-home-intelligence-spec.md)
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
- [Phase 0 foundation feature scenarios](tests/features/phase0_foundation.feature)

## How this repo is organized

- `config/` — inventory, contract, and retention artifacts for the current release slices.
- `docs/` — specification, roadmap, implementation plan, tasks, and contract notes.
- `scripts/` — validation helpers for docs, project scaffolding, contracts, and features.
- `src/` — the minimal Python package root for future implementation work.
- `tests/features/` — BDD scenarios for behavior and acceptance gates.

## Current status

- Created as an isolated private project folder under your workspace.
- Phase 1 core occupancy and lighting artifacts are now checked in locally.
- Phase 2 people and pet personalization artifacts are now checked in locally.
- Phase 3 vehicle and contextual recognition artifacts are now checked in locally.
- Phase 0 foundation artifacts remain available for the broader project baseline.
- Phase 4 and beyond are documented and queued for subsequent work.

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
