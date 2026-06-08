# Pram walking-vs-driving transport classification

## Scope

- Deterministically classify a pram snapshot as `walk` or `drive` using local vehicle-context recency.
- Preserve available room/person context from the input snapshot.
- Planning-only behavior; do not trigger lock/garage actions, unlocks, or actuation.
- Do not implement ANPR-only decisioning or vehicle-person linking logic here.

## Input contract

- Required:
  - `with_pram` (`boolean`)
- Optional:
  - `person_id`
  - `room_id` or `room`
  - `vehicle_context_age_seconds`
  - `ts`

## Classification rules

- If `with_pram` is `false`, output `not_pram`.
- If `with_pram` is `true` and a matching vehicle context is within `90` seconds, output `drive`.
- If `with_pram` is `true` and no matching vehicle context is present within `90` seconds, output `walk`.

## Output contract

- Output includes:
  - `source: pram_walking_vs_driving`
  - `transport_mode: walk|drive|not_pram`
  - `room` when present in snapshot
  - `person_id` when present in snapshot
  - `context` object with:
    - `with_pram`
    - `vehicle_context_age_seconds`
    - `vehicle_context_window_seconds`

## Determinism notes

- Matching is timestamp-window based only, with no score thresholds and no learned behavior.
- The decision is always one of `walk`, `drive`, or `not_pram` for any valid snapshot.

## Backlog link

- `TASK-018 pram_walking_vs_driving`
