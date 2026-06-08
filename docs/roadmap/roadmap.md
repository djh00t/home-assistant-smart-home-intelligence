# Roadmap: Smart Presence, Lighting, and Personalization

## Phase 0 - Foundation (2-3 weeks)

1. Data model and inventory
2. Baseline HA structure (packages + scenes + scripts)
3. Jetson + Frigate connectivity and event bridge
4. Create room and light capability catalog
5. Implement 90-day retention baseline jobs

## Phase 1 - Core Occupancy + Lighting (complete)

1. Room occupancy state machine in HA
2. Motion dwell reset automation
3. Bed presence integration and sleep-safe mode
4. White-only color-temp orchestration
5. Color matching for compatible color-capable lights
6. Initial BDD scenarios for occupancy and lighting behavior

Delivered:

- Room occupancy state machine helpers, contract, and acceptance coverage
- Motion dwell reset helpers, contract, and acceptance coverage
- Bed presence override helpers, contract, and acceptance coverage
- White-light circadian orchestration helpers, contract, and acceptance coverage
- Color-sync routing helpers, contract, and acceptance coverage

## Phase 2 - People + Pets (2-4 weeks)

1. Person tracker ingest (phone/BLE/zone)
2. mmWave and Frigate fusion for room-level occupancy
3. Pet actor model and room pet occupancy
4. Personal desk-light and climate profile actions
5. Safety rules: person actions require person signal, not pet-only signal
6. Household-hold lights with pet occupancy mode switch

## Phase 3 - Vehicle and contextual recognition (2-4 weeks)

1. ONVIF-compatible camera zones for driveway and entrances
2. ANPR service + plate-event to HA bridge
3. Face recognition service integration with confidence gating
4. Pram-aware walking-vs-driving inference
5. Car arrival/departure automations with guardrails
6. Foreign plate/person log entity and alert path

## Phase 4 - Reliability and expansion (ongoing)

1. Additional room rollout from pilot
2. Add confidence dashboards and override controls
3. Alert/incident logs with retention validation
4. Regression scenarios for mixed-brand cameras
5. Expand to 90+ day retention verification and audit jobs

## Milestones

- M1: Pilot room stable with no false brightening in bed-state
- M2: Full room lights and dwell behavior across first floor
- M3: At least one driveway flow with person-pram-car classification
- M4: Foreign plate/person event queue and retention proof

## Exit criteria

- Automation behavior documented by BDD
- No critical false-action categories in pilot
- Storage retention and cleanup proven for 90 days
- Manual override path validated per room
