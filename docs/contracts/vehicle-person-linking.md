# Vehicle-person linking (phase 3 driveway planning)

## Scope

- Canonicalize driveway ANPR+face evidence into a linked vehicle-person planning event.
- Planning-only behavior: no garage-door actuation, no lock/unlock behavior, and no ANPR-only actions.
- Require deterministic thresholds and driveway context before producing linked arrival or departure planning events.

## Input contract

- Required:
  - `room_id` (canonical room must resolve to `driveway`)
  - `person_id`
  - `plate`
  - `plate_confidence` (`0.0` to `1.0`)
  - `face_match_confidence` (`0.0` to `1.0`)
  - `direction`
  - `camera`
- Optional:
  - `event_id`
  - `ts`

## Canonicalization rules

- Only `driveway` scope is allowed.
- `plate` is canonicalized by stripping separators and uppercasing.
- `direction` is normalized with the driveway setup rules:
  - `arrival` -> `vehicle_arrival`
  - `departure` -> `vehicle_departure`
  - other normalized directions are rejected for linked-event emission.
- `plate_confidence` must be at least `0.8` and `face_match_confidence` at least `0.75`.
- Output `confidence` is deterministic and uses the minimum of the two evidence confidences.

## Output contract

- Output fields:
  - `event_id`
  - `source`
  - `type` (`vehicle_arrival` or `vehicle_departure`)
  - `room`
  - `person_id`
  - `camera`
  - `confidence`
  - `vehicle`
- `vehicle` contains:
  - `plate` (canonicalized)
  - `plate_confidence`
  - `face_match_confidence`

## Rejection behavior

- Reject non-driveway references.
- Reject packets below either confidence threshold.
- Reject non-arrival/departure canonical directions.

## Backlog link

- `TASK-017 vehicle_person_linking`
