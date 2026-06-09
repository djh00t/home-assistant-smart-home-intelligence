# Face enrollment and match phase 3 canonicalization

## Scope

- Record face enrollment metadata with deterministic opaque identifiers and retention metadata.
- Canonicalize face match signals into a normalized `face` presence-event shape.
- Preserve person/room/camera context without returning raw biometric signatures.

## Backlog boundary

- This slice is planning/canonicalization only.
- No vehicle linkage.
- No action/actuation behavior.
- No camera-only unlock/deadbolt decisions.
- Face identity is evidence, not a standalone unlock signal.

## Enrollment input

- Required:
  - `person_id`
  - `room` (canonical room identifier)
  - `camera`
  - `face_signature`
- Optional:
  - `source`
  - `enrollment_id`
  - `recorded_at`

## Match input

- Required:
  - `person_id`
  - `room` (canonical room identifier)
  - `camera`
  - `face_match_confidence` (`0.0` to `1.0`)
- Optional:
  - `track_id`
  - `event_id`
  - `ts`

## Canonicalization rules

- Enrollment builder:
  - keeps the person identity and room/camera/source context.
  - converts the returned `face_signature` into a deterministic opaque `sha256:<digest>` representation instead of retaining the raw biometric signature.
  - emits retention metadata so retention policy consumers can apply the same baseline.
  - produces a stable deterministic opaque `face-enrollment::<sha256-prefix>` `enrollment_id` when none is provided.
- Face-match builder:
  - emits event shape with:
    - `source: face`
    - `entity_class: human`
    - preserved `room` and `camera`
    - preserved `person_id`
    - preserved `face_match_confidence` as `confidence`
    - `type: confidence`
  - produces a stable deterministic opaque `face-match::<sha256-prefix>` `event_id` when none is provided.
  - rejects matches below deterministic threshold `0.75`.

## Retention

- Enrollment records use `retention_days: 90`.

## Backlog link

- `TASK-016 face_enrollment_and_match`
