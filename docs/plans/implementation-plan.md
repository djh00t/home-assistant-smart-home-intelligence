# Implementation Plan

## Program assumptions

- Home Assistant is the control brain.
- Apple Home remains a control UI, not primary automation logic.
- Cameras remain mixed-brand in ecosystem; Frigate/Jetson local event layer is the standard for automated triggers.
- 90-day retention is mandatory for events and records.

## Work streams

1. Foundation
2. Room occupancy and light orchestration
3. Person and pet presence fusion
4. Car/ANPR/face workflows
5. Rollout and hardening

## Work stream 1: Foundation

1. Create repository structure for HA packages, scripts, and secrets
2. Define room + light inventory CSV (or YAML) and add ownership comments
3. Add MQTT broker and topic contracts for presence events
4. Stand up a shared event schema validator and dead-letter capture
5. Add 90-day retention policy for raw logs and media buckets
6. Add base Makefile targets (`check`, `quality-gates`, `install`, `build`, `publish`, `clean`) as local repo baseline
7. Add baseline BDD harness for feature loading

## Work stream 2: Occupancy and lighting

1. Create room state sensors:
2. `room_<name>_occupancy_mode`
3. `room_<name>_occupants`
4. `room_<name>_dwell_timer`
5. Add restartable dwell automations for motion/no-motion transitions
6. Add white-light time-of-day policy and circadian mapping
7. Add color-sync automations scoped to color-capable groups
8. Add bed-state overrides (`in_bed`, `bed_movement`) to suppress harsh scenes
9. Add manual override locks and cooldown windows

Status: complete for the Phase 1 core occupancy + lighting slice.

Delivered artifacts:

- Room state machine helpers and contract
- Dwell reset helpers and contract
- Bed-state override helpers and contract
- White-light orchestration helpers and contract
- Color-sync routing helpers and contract

## Work stream 3: Person and pet fusion

1. Ingest person trackers, mmWave entities, and PIR/motion signals
2. Add fusion scoring and room assignment algorithm
3. Add desk-light profiles and climate profiles per person
4. Add pet occupancy channel with non-person side effects only
5. Add room-mode queue for “house empty” vs “pet present”
6. Add BDD scenarios for cross-sensor conflicts

## Work stream 4: Vehicle and recognition workflows

1. Add ANPR service on driveway cameras
2. Add face recognition service with local model and enrollment flow
3. Add person-car-event linking rules
4. Add pram walking vs driving classifier
5. Add foreign plate/face queue and action hooks
6. Add high-impact actions only with multi-signal thresholds

## Work stream 5: Rollout and hardening

1. Pilot one room until false-actions are below threshold
2. Add second room with identical pattern and calibration
3. Expand lane by room with per-room KPI sign-off
4. Build HA dashboard for overrides and recent events
5. Add periodic retention audit job and retention proof report
6. Document runbooks and incident responses

## Suggested ticket order

1. `PLAN-001` Foundation and data model
2. `PLAN-002` Dwell and base room lights
3. `PLAN-003` mmWave and motion fusion
4. `PLAN-004` Person desk-light + climate profile
5. `PLAN-005` Car/plate + pram logic
6. `PLAN-006` Pet-aware occupancy
7. `PLAN-007` Security and retention hardening
8. `PLAN-008` Full rollout

## Validation gates

1. Feature-level smoke: occupancy transitions, dwell reset, empty-house transitions
2. Cross-room race tests: two-person overlap in adjacent rooms
3. No person actions from pet-only occupancy
4. Car lock/unlock action never with single-source confidence
5. 90-day retention job dry-run and cleanup checks
