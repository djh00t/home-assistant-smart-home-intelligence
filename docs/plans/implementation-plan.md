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

Status: complete for the Phase 2 people + pet fusion slice.

Delivered artifacts:

- Person tracker ingest helpers and contract
- MmWave fusion helpers and contract
- Pet classifier helpers and contract
- Person room assignment helpers and contract
- Desk-light profile helpers and contract
- Climate person profile helpers and contract
- Pet-mode household switch helpers and contract

## Work stream 4: Vehicle and recognition workflows

Status: complete for the Phase 3 vehicle and contextual recognition slice.

Delivered artifacts:

- Arrival Zone zone setup helpers and contract
- ANPR service and event helpers and contract
- Face enrollment and match helpers and contract
- Vehicle-person linking helpers and contract
- Pram walking-vs-driving helpers and contract
- Foreign identity log queue helpers and contract
- Security and retention job helpers and contract

## Work stream 5: Rollout and hardening

Status: complete for the Phase 4 reliability and expansion slice.

Delivered artifacts:

- Pilot-room stabilization and false-action reduction helpers
- Additional room rollout helpers and per-room KPI sign-off artifacts
- HA dashboard helpers for overrides and recent events
- Periodic retention audit job and retention proof helpers
- Runbook and incident-response documentation
- Non-home zone queue helpers and contract
- Multi-room heatmap helpers and contract
- Scene preference UI helpers and contract
- Anomaly and false-action dashboard helpers and contract

## Work stream 6: HACS packaging and integration foundation

Status: complete for the HACS-first packaging and release-guard slice.

Planned artifacts:

- `hacs.json` repository metadata
- `custom_components/smart_home_presence_intelligence/manifest.json`
- room activity, override, and retention status entities
- room-policy sensors for house mode, white scene, and color sync
- config flow and options flow
- service, diagnostics, and repair scaffolding
- restoreable config-entry runtime payloads
- policy snapshots derived from room capabilities and runtime occupancy
- release metadata and downgrade notes
- HACS package management BDD scenarios
- HACS release verification and downgrade path

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
