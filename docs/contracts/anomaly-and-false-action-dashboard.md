# Phase 4 anomaly and false-action dashboard

## Scope

- Build a deterministic planning-only dashboard model for review of anomalies and false actions.
- Keep the slice advisory only:
  - no actuation,
  - no scene writes,
  - no schedule writes,
  - no dashboard backend mutations,
  - no alert escalation.
- Surface review priority and per-room incident counts without introducing a live frontend implementation.

## Input

- Required:
  - `incidents`
- Each incident should include:
  - `room_id`
  - `kind` (`anomaly` or `false_action`)
  - `severity`
- Optional incident metadata:
  - `category`
  - `source`
  - `confidence`
  - `event_id`
  - `ts`
  - `notes`

## Rules

- Load canonical room inventory from `config/inventory/rooms.yaml`.
- Sort room cards by canonical room order from the inventory.
- Accept only canonical rooms; reject unknown room ids.
- Group incidents by room and preserve separate anomaly and false-action counts.
- Compute review priority from the highest severity present in each room card.
- Reports are deterministic for identical input incidents.

## Output

- `source: anomaly_and_false_action_dashboard`
- deterministic opaque `dashboard_id` using `anomaly_and_false_action_dashboard::sha256:{dashboard_digest}`
- `dashboard_record_type: anomaly_false_action_dashboard`
- `record_name: anomaly_and_false_action_dashboard`
- `dashboard_status: ready`
- `tabs` for summary, rooms, anomalies, and false actions
- `room_cards` grouped by room
- immutable 90-day retention metadata
- raw room telemetry fragments and timestamps must never appear inside `dashboard_id`

## Backlog link

- `TASK-024 anomaly_and_false_action_dashboard`
