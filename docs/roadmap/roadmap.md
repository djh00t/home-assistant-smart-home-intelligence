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

## Phase 2 - People + Pets (complete)

Delivered:

- Person tracker ingest helpers, contract, and acceptance coverage
- mmWave and Frigate fusion helpers, contract, and acceptance coverage
- Pet detection classifier helpers, contract, and acceptance coverage
- Person room assignment helpers, contract, and acceptance coverage
- Desk-light profile helpers, contract, and acceptance coverage
- Climate-person profile helpers, contract, and acceptance coverage
- Empty-house pet-mode switch helpers, contract, and acceptance coverage

## Phase 3 - Vehicle and contextual recognition (complete)

Delivered:

- Driveway zone setup helpers, contract, and acceptance coverage
- ANPR service and event helpers, contract, and acceptance coverage
- Face enrollment and match helpers, contract, and acceptance coverage
- Vehicle-person linking helpers, contract, and acceptance coverage
- Pram walking-vs-driving helpers, contract, and acceptance coverage
- Foreign identity log queue helpers, contract, and acceptance coverage
- Security and retention job helpers, contract, and acceptance coverage

## Phase 4 - Reliability and expansion (complete)

Delivered:

- Additional room rollout helpers, contract, and acceptance coverage
- Confidence dashboards and override control helpers, contracts, and acceptance coverage
- Alert and incident log helpers, contracts, and retention validation coverage
- Regression scenarios for mixed-brand camera behavior
- 90+ day retention verification and audit helpers, contracts, and acceptance coverage
- Non-home zone queue helpers, contract, and acceptance coverage
- Multi-room heatmap helpers, contract, and acceptance coverage
- Scene preference UI helpers, contract, and acceptance coverage
- Anomaly and false-action dashboard helpers, contract, and acceptance coverage

## Phase 5 - HACS integration foundation

Delivered:

- HACS repository metadata and brand assets
- Custom integration scaffold and config flow
- Room activity, bridge health, override, and retention status entity scaffolding
- Room-policy sensor scaffolding for house mode and per-room lighting policy
- Restoreable config-entry runtime payloads
- Canonical MQTT bridge and runtime helpers
- Service, diagnostics, and repair scaffolding
- Release/version packaging alignment
- HACS release verification and downgrade path

Planned next:

- Later phase-5 entity coverage for dashboards and richer automation surfaces

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
