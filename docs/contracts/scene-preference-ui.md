# Phase 4 scene preference UI

## Scope

- Build a deterministic planning-only dashboard model for room scene preferences.
- Use the synthetic `sample_*` room ids from `config/inventory/room_capabilities.yaml` for public examples and validator coverage.
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
- Treat the published room capability file as a synthetic sample that preserves the supported lighting and override combinations.
- Include only rooms with `supports_lighting: true`.
- Exclude non-lighting or exterior-only entries from dashboard cards.
- Sort room cards by canonical `room_id`.
- Surface per-room day/night scene presets, color support, and manual override minutes.
- Preserve planning-only safety flags for each room card.
- Use an opaque `scene_preference_ui::sha256:{dashboard_digest}` dashboard identifier so raw room and scene metadata does not leak through the record key.

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
