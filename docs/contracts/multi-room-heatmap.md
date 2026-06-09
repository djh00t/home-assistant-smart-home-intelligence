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
- Reports are deterministic for identical input observations.

## Output

- `source: multi_room_heatmap`
- deterministic `report_id`
- `report_record_type: room_heatmap`
- `record_name: multi_room_heatmap`
- `report_status: ready`
- `heatmap_cells` grouped by room
- `summary` with total and per-room counts
- immutable 90-day retention metadata

## Backlog link

- `TASK-022 multi_room_heatmap`
