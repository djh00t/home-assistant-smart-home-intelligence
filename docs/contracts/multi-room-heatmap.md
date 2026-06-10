# Phase 4 multi-room heatmap report

## Scope

- Build a deterministic planning-only heatmap report from multiple room occupancy observations.
- Keep the slice advisory only:
  - no actuation,
  - no room control,
  - no light control,
  - no scheduling writes.
- Preserve reviewability without creating a second state machine or dashboard dependency.

## Input

- Required:
  - `observations`
- Each observation should include:
  - `room_id` or `room` or `zone_id`
  - `confidence`
- Optional observation metadata:
  - `source`
  - `type`
  - `event_id`
  - `ts`

## Rules

- Load canonical room inventory from `config/inventory/rooms.yaml`.
- Only rooms with `supports_occupancy: true` participate in the report.
- Exterior or non-occupancy zones are ignored.
- Cells are grouped by canonical `room_id` and sorted by `room_id`.
- Cell intensity is based on observation count, with confidence preserved as an average for review context.
- Per-room source provenance and per-room timestamps are excluded from retained heatmap cells.
- Input-derived timestamps are not retained anywhere in the persisted report body.
- Reports are deterministic for identical input observations.
- `report_id` is derived from a SHA-256 digest of canonicalized heatmap cells.
- Raw room telemetry fragments and timestamps must never appear in `report_id`.

## Output

- `source: multi_room_heatmap`
- deterministic `report_id` using `multi_room_heatmap::sha256:{report_digest}`
- `report_record_type: room_heatmap`
- `record_name: multi_room_heatmap`
- `report_status: ready`
- `heatmap_cells` grouped by room with only `room`, `observation_count`, `average_confidence`, and `heat_level`
- `summary` with total and per-room counts
- immutable retention metadata
  - `retention.days = 14`
  - `retention.immutable = true`

Retention is capped at 14 days so the report stays useful for planning without keeping long-lived telemetry detail.

## Backlog link

- `TASK-022 multi_room_heatmap`
