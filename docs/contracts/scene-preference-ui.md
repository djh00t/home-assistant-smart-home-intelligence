# Scene preference UI

## Scope

- Build a deterministic planning-only dashboard model for room scene preferences.
- Keep the slice advisory only:
  - no actuation,
  - no scene writes,
  - no dashboard backend mutations,
  - no schedule writes.
- Surface room scene presets and manual override boundaries without introducing a live frontend implementation.

## Input

- Required:
  - `room_capabilities`
- Optional:
  - `focus_room_id`
  - `ts`

## Rules

- Load canonical room capabilities from `config/inventory/room_capabilities.yaml`.
- Include only rooms with `supports_lighting: true`.
- Exclude exterior zones such as `driveway`.
- Sort room cards by canonical `room_id`.
- Surface per-room day/night scene presets, color support, and manual override minutes.
- Preserve planning-only safety flags for each room card.

## Output

- `source: scene_preference_ui`
- deterministic `dashboard_id`
- `ui_record_type: scene_preferences_dashboard`
- `record_name: scene_preference_ui`
- `ui_status: ready`
- `tabs` for rooms, overrides, and safety
- `room_cards` grouped by room
- immutable 90-day retention metadata

## Backlog link

- `TASK-023 scene_preference_ui`
