# Foreign identity log queue for phase 3 review

## Scope

- Capture a deterministic, immutable queue artifact for foreign or unknown driveway identity snapshots.
- Keep this slice planning-only. Do not generate action hooks, automation actions, vehicle-person linking, or garage/lock commands.
- Preserve identity evidence and review metadata for human review and retention workflows.

## Queue input

- Required:
  - `room_id` (`driveway` canonical room)
  - `camera`
- Optional:
  - `plate`
  - `face_match_confidence` (`0.0` to `1.0`)
  - `person_id`
  - `identity_status` (`foreign`, `unknown`, or `known`)
  - `event_id`
  - `ts`

## Rules

- Canonical room is fixed to `driveway`.
- `plate` is canonicalized to uppercase with separators removed.
- The queue is built only when one of these explicit rules is true:
  - `identity_status` is `foreign` or `unknown`.
  - `person_id` is missing or one of unknown values.
  - `face_match_confidence` is present and below `0.75`.
- `person_id` present and not unknown preserves identity confidence of known person.
- If none of the optional identity evidence fields is present and identity status is omitted, input is invalid.

## Output

The queue record includes:

- `source: foreign_identity_log_queue`
- deterministic `queue_record_type` and `record_name`
- room and camera context
- identity evidence fields (`plate`, `person_id`, `face_match_confidence`, `identity_status` when available)
- immutable retention metadata:
  - `retention_days: 90`
  - `immutable: true`
- `review_status: queued` until manually drained

## Backlog link

- `TASK-019 foreign_identity_log_queue`
