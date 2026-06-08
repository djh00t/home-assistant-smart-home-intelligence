# ANPR service and event planning slice

## Scope

- Canonicalize driveway ANPR detections into vehicle presence events.
- Keep this slice planning-only with no face linkage, no vehicle-person linking, and no foreign plate queue behavior.
- Normalize plate, room reference, camera context, and direction into a deterministic vehicle event shape.

## Input contract

- Required:
  - `room_id` (required canonical value must be `driveway`)
  - `plate`
  - `plate_confidence` (`0.0` to `1.0`)
  - `camera`
- Optional:
  - `direction`
  - `vehicle_type`

## Canonicalization rules

- Canonical room is fixed to `driveway`.
- `plate` is canonicalized to uppercase and separator characters are removed.
- ANPR raw payloads that do not validate as driveway context are rejected.
- Direction is normalized through the driveway zone mapping:
  - known inbound values become `arrival`
  - known outbound values become `departure`
  - unknown or missing direction becomes deterministic `stationary`
- Canonical event type is derived from normalized direction:
  - `arrival` -> `enter`
  - `departure` -> `leave`
  - `stationary` -> `stay`
- The canonical event keeps source and room context:
  - `source: anpr`
  - `entity_class: vehicle`
  - `room: driveway`

## Vehicle payload

- A `vehicle` object is always emitted:
  - `plate` (canonicalized)
  - `plate_confidence`
  - `vehicle_type` (`car`, `truck`, `motorcycle`, or `unknown`)

## Backlog boundary

- No face-person linking, no foreign-plate queue, and no vehicle-to-person association are part of this task.
  Those follow-up behaviors remain in later backlog items.

## Backlog link

- `TASK-015 anpr_service_and_event`
