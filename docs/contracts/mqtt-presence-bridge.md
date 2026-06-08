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
- `bedroom_master` is normalized to `master_bedroom`.
- Canonical payloads must satisfy the phase 0 presence event schema before publish.

## Failure Handling

- Missing required fields produce a dead-letter record.
- Dead-letter records preserve the original payload for later inspection.

## Backlog Link

- `TASK-001 mqtt_presence_bridge`
