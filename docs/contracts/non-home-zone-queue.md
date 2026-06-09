# Non-home zone queue for phase 4 planning review

## Scope

- Build a deterministic review queue record whenever a snapshot references a
  non-home (exterior) zone.
- Keep the slice planning-only with no actuation, no indoor room automation, and no vehicle-person linking.
- Preserve room and camera context, original event evidence, queue metadata, and review status.

## Queue input

- Required:
  - `room_id` or `room` or `zone_id` (canonical room identifier)
  - `camera`
- Optional:
  - `source`
  - `plate`
  - `person_id`
  - `identity_status`
  - `face_match_confidence`
  - `event_id`
  - `confidence`
  - `direction`
  - `ts`

## Rules

- Load room inventory from `config/inventory/rooms.yaml`.
- Treat entries under `external_zones` as queue-eligible non-home zones.
- The queue is currently driven by the `zone_alpha` exterior zone in phase 4.
- Return `None` for home-zone/supported-occupancy rooms.
- Preserve only review-relevant non-room/camera evidence in the queue payload.
- Queue records are deterministic.
- Convert raw `plate` and `person_id` values into presence-only flags instead of retaining person or plate references.
- linkable `event_id`, raw plate values, raw person identifiers, and hashed identity refs are excluded from retained evidence.
- Derive `queue_id` from a SHA-256 digest of canonicalized evidence so raw plate, person, or other sensitive evidence never appears in the identifier.

## Output

- `source: non_home_zone_queue`
- deterministic `queue_id` using `non_home_zone_queue::{room}::{camera}::sha256:{evidence_digest}`
- deterministic `queue_record_type` and `record_name`
- room and camera context fields
- `evidence` object with event payload details
- `evidence` keeps review signals such as `source`, `direction`, `identity_status`, confidence fields, and `plate_seen` / `person_seen`
- immutable retention metadata:
  - `retention.days = 90`
  - `retention.immutable = true`
- `review_status: queued`
- `ts` from source or default epoch timestamp

## Backlog link

- `TASK-021 non_home_zone_queue`
