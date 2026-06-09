# MQTT Presence Bridge

This document defines the first backlog slice for the MQTT presence bridge.

## Scope

- Normalize raw upstream presence payloads into the canonical phase 0 event shape.
- Apply stable aliases before publishing to the canonical topic.
- Route invalid payloads to the dead-letter topic with validation context.

## Canonical Topics

- `ha/presence/event`
- `ha/presence/event/dlq`

## Normalization Rules

- `mwave` is normalized to `mmwave`.
- Room labels are slugified to snake_case before validation, so labels like `room alpha` normalize to `room_alpha`.
- Hyphenated synthetic labels such as `zone - beta` normalize to `zone_beta`.
- Canonical payloads must satisfy the phase 0 presence event schema before publish.
- Canonical publishes forward only schema-backed contract fields: `event_id`, `source`, `type`, `room`, `camera`, `entity_class`, `person_ref`, `confidence`, `tracker_ref`, `vehicle`, `context`, and `ts`.
- Non-opaque supplied `event_id` values are deterministically re-keyed before canonical publish or dead-letter storage.
- Raw resident ids, tracker ids, and license plates are converted into deterministic opaque SHA-256 refs before publish or dead-letter storage.

## Failure Handling

- Missing required fields produce a dead-letter record.
- Dead-letter records include validation errors plus only the contract-backed subset of the original payload.
- Dead-letter records preserve opaque refs only and never echo raw resident, tracker, or plate identifiers.
- Dead-letter records do not echo unexpected raw upstream fields back onto MQTT.

## Backlog Link

- `TASK-001 mqtt_presence_bridge`
