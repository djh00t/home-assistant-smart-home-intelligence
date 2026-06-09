# Phase 0 Foundation Contracts

This document defines the initial data artifacts for the phase 0 foundation slice.
It is the contract between the spec, the inventory, the MQTT topic layout, the event schema, and the retention baseline.

## Scope

- Room and zone inventory for the first rollout slice
- Room capability inventory for light and policy routing
- Canonical MQTT topic contract for presence events
- MQTT presence bridge normalization and dead-letter routing
- Room presence FSM template and state vocabulary
- Dwell reset automation for motion/no-motion transitions
- Adaptive white-lighting policy and circadian scene mapping
- Color-sync routing for color-capable lights
- Bed-state override for sleep-safe wake suppression
- Empty-house pet mode switch for pet-only occupancy
- Person tracker integration for mobile app, BLE, and geofencing signals
- Person-room assignment for deterministic room identity plans
- Climate-person profiles for deterministic climate preference routing
- MmWave and Frigate room fusion for room-level occupancy
- Pet detection classifier for canonical pet occupancy events
- ANPR service and zone_alpha vehicle event normalization
- Foreign identity alert queue for review retention
- Security and retention dry-run jobs for cleanup candidates
- Face enrollment metadata and face-match canonical events
- Vehicle-person linking for deterministic zone_alpha planning events
- Non-home zone queueing for exterior-zone review artifacts
- Multi-room heatmap report for occupancy review
- Scene preference UI for room scene presets and override controls
- Anomaly and false-action dashboard for review planning
- Pram walking-vs-driving classification for transport-mode inference
- JSON schema for normalized presence events
- Minimum retention policy for phase 0 records and audit data

## Assumptions

- `room_id` values are stable snake_case identifiers and are the canonical identifiers used by all phase 0 artifacts.
- Synthetic labels are normalized to snake_case before validation, so examples like `room alpha` become `room_alpha`.
- Synthetic exterior labels normalize the same way, so examples like `zone - beta` become `zone_beta`.
- The spec typo `mwave` is normalized to `mmwave` as the canonical source token.
- `room` in the event schema is a contract identifier that also covers the exterior `zone_alpha` zone for vehicle-aware events.
- `ha/presence/event` is the canonical publish topic for validated presence events and is not retained.
- `vehicle` and `context` are optional event payload objects; publishers include them only when they have meaningful data.
- The phase 0 retention baseline is 90 days for all records and audit artefacts listed here.

## Artifact Index

- `config/inventory/rooms.yaml`
- `config/inventory/room_capabilities.yaml`
- `config/contracts/mqtt_topics.yaml`
- `config/contracts/presence_bridge.yaml`
- `config/contracts/room_fsm.yaml`
- `config/contracts/dwell_reset.yaml`
- `config/contracts/white_lighting.yaml`
- `config/contracts/color_sync.yaml`
- `config/contracts/bed_state_override.yaml`
- `config/contracts/house_mode.yaml`
- `config/contracts/person_tracker.yaml`
- `config/contracts/person_room_assignment.yaml`
- `config/contracts/climate_person_profiles.yaml`
- `config/contracts/mmwave_fusion.yaml`
- `config/contracts/face_enrollment_and_match.yaml`
- `config/contracts/presence_event.schema.json`
- `config/contracts/driveway_zone_setup.yaml`
- `config/contracts/anpr_service_and_event.yaml`
- `config/contracts/security_and_retention_jobs.yaml`
- `config/contracts/hacs_package_management.yaml`
- `config/contracts/foreign_identity_log_queue.yaml`
- `config/contracts/multi_room_heatmap.yaml`
- `config/contracts/scene_preference_ui.yaml`
- `config/contracts/anomaly_and_false_action_dashboard.yaml`
- `config/contracts/vehicle_person_linking.yaml`
- `config/contracts/non_home_zone_queue.yaml`
- `config/policies/retention.yaml`
- `docs/contracts/mqtt-presence-bridge.md`
- `docs/contracts/room-fsm-template.md`
- `docs/contracts/dwell-reset-automation.md`
- `docs/contracts/adaptive-white-lighting.md`
- `docs/contracts/color-sync-for-color-lights.md`
- `docs/contracts/bed-state-override.md`
- `docs/contracts/empty-house-with-pet-mode-switch.md`
- `docs/contracts/person-tracker-integration.md`
- `docs/contracts/person-room-assignment.md`
- `docs/contracts/climate-person-profiles.md`
- `config/contracts/desk_light_profiles.yaml`
- `docs/contracts/desk-light-profiles.md`
- `docs/contracts/mmwave-fusion-rule.md`
- `docs/contracts/anpr-service-and-event.md`
- `docs/contracts/security-and-retention-jobs.md`
- `docs/contracts/hacs-package-management.md`
- `docs/contracts/foreign-identity-log-queue.md`
- `docs/contracts/multi-room-heatmap.md`
- `docs/contracts/scene-preference-ui.md`
- `docs/contracts/anomaly-and-false-action-dashboard.md`
- `docs/contracts/non-home-zone-queue.md`
- `docs/contracts/face-enrollment-and-match.md`

## Room Inventory Notes

The published room inventory and capability examples intentionally use a synthetic public sample so the repository can exercise room-policy code paths without publishing a live deployment topology:

- `sample_room_alpha`
- `sample_room_beta`
- `sample_study_zone`
- `sample_room_delta`
- `sample_room_epsilon`
- `sample_storage_zone`

The canonical room inventory file in the repository is also a synthetic sample, including the exterior-zone entries used by vehicle-linked and outdoor event contracts, so those flows can share the same `room` field without publishing a private deployment layout.

## Room Capability Notes

The capability catalog provides the first pass at per-room routing rules for phase 0:

- `room_id` stays stable within the published synthetic sample.
- `occupancy_sources` expresses the preferred sensor order for each room.
- `lighting` captures whether a room supports white or color lighting and which groups should receive automations.
- `policies` carries room-specific override and safety expectations for later automation slices.

The catalog is intentionally simple, declarative, and synthetic so that later backlog items can reference one consistent public sample for room behavior.

## Topic Contract Notes

- `ha/presence/event` carries normalized presence events from all upstream sources.
- `ha/presence/event/dlq` is the dead-letter topic for rejected or unroutable events.
- `config/contracts/presence_bridge.yaml` defines source and room alias normalization before publish.
- `docs/contracts/mqtt-presence-bridge.md` documents the first backlog slice for bridge behavior.
- `config/contracts/room_fsm.yaml` defines the initial room-state vocabulary and transitions.
- `docs/contracts/room-fsm-template.md` documents the first room FSM backlog slice.
- `config/contracts/dwell_reset.yaml` defines the initial dwell reset trigger and timer stages.
- `docs/contracts/dwell-reset-automation.md` documents the first dwell reset backlog slice.
- `config/contracts/white_lighting.yaml` defines the circadian white-light policy and guardrails.
- `docs/contracts/adaptive-white-lighting.md` documents the first adaptive white-lighting backlog slice.
- `config/contracts/color_sync.yaml` defines the first color-sync routing guardrails.
- `docs/contracts/color-sync-for-color-lights.md` documents the first color-sync backlog slice.
- `config/contracts/bed_state_override.yaml` defines the master bedroom sleep-safe override contract.
- `docs/contracts/bed-state-override.md` documents the first bed-state override backlog slice.
- `config/contracts/house_mode.yaml` defines the pet-only house mode switch contract.
- `docs/contracts/empty-house-with-pet-mode-switch.md` documents the final Priority A backlog slice.
- `config/contracts/person_tracker.yaml` defines the first tracker integration contract.
- `docs/contracts/person-tracker-integration.md` documents the first person tracker backlog slice.
- `config/contracts/person_room_assignment.yaml` defines deterministic room assignment from occupancy and identity signals.
- `docs/contracts/person-room-assignment.md` documents the room assignment plan slice that feeds later personalization.
- `config/contracts/climate_person_profiles.yaml` defines deterministic climate preference routing from assigned people.
- `docs/contracts/climate-person-profiles.md` documents the first climate-person profile backlog slice.
- `config/contracts/mmwave_fusion.yaml` defines the initial mmWave/frigate fusion contract.
- `docs/contracts/mmwave-fusion-rule.md` documents the first mmWave fusion backlog slice.
- `config/contracts/pet_detection_classifier.yaml` defines the pet classifier normalization contract.
- `docs/contracts/pet-detection-classifier.md` documents the first pet classifier backlog slice.
- `docs/contracts/driveway-zone-setup.md` defines the canonical arrival-zone setup and normalization contract.
- `config/contracts/anpr_service_and_event.yaml` defines ANPR zone_alpha vehicle canonicalization and validation.
- `config/contracts/non_home_zone_queue.yaml` defines planning-only queue records for non-home zone sightings.
- `config/contracts/multi_room_heatmap.yaml` defines planning-only heatmap reports for multi-room occupancy review.
- `config/contracts/scene_preference_ui.yaml` defines planning-only dashboard models for room scene preferences and override controls.
- `config/contracts/anomaly_and_false_action_dashboard.yaml` defines planning-only dashboard models for anomaly and false-action review.
- `docs/contracts/anpr-service-and-event.md` documents ANPR-only vehicle planning and event creation behavior.
- `docs/contracts/non-home-zone-queue.md` documents the non-home zone review queue behavior.
- `docs/contracts/multi-room-heatmap.md` documents the multi-room heatmap report behavior.
- `docs/contracts/scene-preference-ui.md` documents the scene preference dashboard model behavior.
- `docs/contracts/anomaly-and-false-action-dashboard.md` documents the anomaly and false-action dashboard model behavior.
- `docs/contracts/vehicle-person-linking.md` documents deterministic vehicle-person linking for zone_alpha planning events.
- `config/contracts/pram_walking_vs_driving.yaml`
- `docs/contracts/pram-walking-vs-driving.md` documents pram walking-vs-driving transport classification.

## Arrival Zone Zone Notes

- `zone_alpha` is the canonical exterior zone identifier for vehicle-aware events in phase 0.
- The zone_alpha setup defines explicit source priority as `anpr`, `frigate`, then `face`.
- Direction normalization is deterministic and canonicalized to `arrival`, `departure`, and `stationary`.
- Canonical publishers are bridge-style producers only; consumers should not republish raw upstream payloads back onto the canonical topic.

## Schema Notes

- The schema is intentionally strict with `additionalProperties: false` at the root level and for nested objects.
- `confidence` is normalized to the inclusive range `0.0` to `1.0`.
- `source`, `type`, `entity_class`, and `room` are enumerated to keep the phase 0 event vocabulary stable.

## Retention Notes

- Phase 0 retention is a minimum baseline, not a maximum.
- Event records, room-state history, linkage logs, audit records, and media metadata all retain for 90 days in this phase.
- Cleanup jobs and auditability are required for the phase 0 retention policy to be considered implemented.
- TASK-020 requires planning-only dry-run retention candidate reports to prove cleanup boundaries.
