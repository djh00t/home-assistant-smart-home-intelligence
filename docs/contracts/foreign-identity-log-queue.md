# Foreign identity log queue for phase 3 review

## Scope

- Capture a deterministic, immutable queue artifact for foreign or unknown zone_alpha identity snapshots.
- Keep this slice planning-only. Do not generate action hooks, automation actions, vehicle-person linking, or room_zeta/lock commands.
- Preserve review metadata for human review and retention workflows without retaining raw plate or person identifiers.

## Queue input

- Required:
  - `room_id` (`zone_alpha` canonical room)
  - `camera`
- Optional:
  - `plate`
  - `face_match_confidence` (`0.0` to `1.0`)
  - `person_id`
  - `identity_status` (`foreign`, `unknown`, or `known`)
  - `event_id`
  - `ts`

## Rules

- Canonical room is fixed to `zone_alpha`.
- `plate` is canonicalized to uppercase with separators removed.
- The queue is built only when one of these explicit rules is true:
  - `identity_status` is `foreign` or `unknown`.
  - `person_id` is missing or one of unknown values.
  - `face_match_confidence` is present and below `0.75`.
- `person_id` present and not unknown preserves identity confidence of known person.
- If none of the optional identity evidence fields is present and identity status is omitted, input is invalid.
- `queue_id` is derived from a SHA-256 digest of canonicalized identity evidence.
- Raw plate or person values must never appear in `queue_id`.
- Raw plate or person values must never appear in the persisted `identity` payload.

## Output

The queue record includes:

- `source: foreign_identity_log_queue`
- deterministic `queue_id` using `foreign_identity_log_queue::{room}::{camera}::sha256:{evidence_digest}`
- deterministic `queue_record_type` and `record_name`
- room and camera context
- identity evidence fields (`plate_present`, `person_present`, `face_match_confidence`, `identity_status` when available)
- immutable retention metadata:
  - `retention_days: 90`
  - `immutable: true`
- `review_status: queued` until manually drained

## Backlog link

- `TASK-019 foreign_identity_log_queue`
