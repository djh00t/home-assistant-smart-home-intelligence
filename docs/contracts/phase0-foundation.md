# Phase 0 Foundation Contracts

This document defines the initial data artifacts for the phase 0 foundation slice.
It is the contract between the spec, the inventory, the MQTT topic layout, the event schema, and the retention baseline.

## Scope

- Room and zone inventory for the first rollout slice
- Room capability inventory for light and policy routing
- Canonical MQTT topic contract for presence events
- MQTT presence bridge normalization and dead-letter routing
- Room presence FSM template and state vocabulary
- JSON schema for normalized presence events
- Minimum retention policy for phase 0 records and audit data

## Assumptions

- `room_id` values are stable snake_case identifiers and are the canonical identifiers used by all phase 0 artifacts.
- The spec example `bedroom_master` is normalized to `master_bedroom` in the inventory and schema.
- The spec typo `mwave` is normalized to `mmwave` as the canonical source token.
- `room` in the event schema is a contract identifier that also covers the exterior `driveway` zone for vehicle-aware events.
- `ha/presence/event` is the canonical publish topic for validated presence events and is not retained.
- `vehicle` and `context` are optional event payload objects; publishers include them only when they have meaningful data.
- The phase 0 retention baseline is 90 days for all records and audit artefacts listed here.

## Artifact Index

- `config/inventory/rooms.yaml`
- `config/inventory/room_capabilities.yaml`
- `config/contracts/mqtt_topics.yaml`
- `config/contracts/presence_bridge.yaml`
- `config/contracts/room_fsm.yaml`
- `config/contracts/presence_event.schema.json`
- `config/policies/retention.yaml`
- `docs/contracts/mqtt-presence-bridge.md`
- `docs/contracts/room-fsm-template.md`

## Room Inventory Notes

The initial inventory covers the spaces referenced by the current spec and feature scenarios:

- `hall`
- `kitchen`
- `living_room`
- `office`
- `master_bedroom`
- `driveway` as an exterior zone

The `driveway` entry is retained in the room inventory file so that vehicle-linked presence events can share the same canonical `room` field without introducing a second location identifier model in phase 0.

## Room Capability Notes

The capability catalog provides the first pass at per-room routing rules for phase 0:

- `room_id` stays aligned with the canonical room inventory.
- `occupancy_sources` expresses the preferred sensor order for each room.
- `lighting` captures whether a room supports white or color lighting and which groups should receive automations.
- `policies` carries room-specific override and safety expectations for later automation slices.

The catalog is intentionally simple and declarative so that later backlog items can reference one consistent source for room behavior.

## Topic Contract Notes

- `ha/presence/event` carries normalized presence events from all upstream sources.
- `ha/presence/event/dlq` is the dead-letter topic for rejected or unroutable events.
- `config/contracts/presence_bridge.yaml` defines source and room alias normalization before publish.
- `docs/contracts/mqtt-presence-bridge.md` documents the first backlog slice for bridge behavior.
- `config/contracts/room_fsm.yaml` defines the initial room-state vocabulary and transitions.
- `docs/contracts/room-fsm-template.md` documents the first room FSM backlog slice.
- Canonical publishers are bridge-style producers only; consumers should not republish raw upstream payloads back onto the canonical topic.

## Schema Notes

- The schema is intentionally strict with `additionalProperties: false` at the root level and for nested objects.
- `confidence` is normalized to the inclusive range `0.0` to `1.0`.
- `source`, `type`, `entity_class`, and `room` are enumerated to keep the phase 0 event vocabulary stable.

## Retention Notes

- Phase 0 retention is a minimum baseline, not a maximum.
- Event records, room-state history, linkage logs, audit records, and media metadata all retain for 90 days in this phase.
- Cleanup jobs and auditability are required for the phase 0 retention policy to be considered implemented.
