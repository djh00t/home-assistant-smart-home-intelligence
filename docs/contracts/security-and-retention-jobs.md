# Security and retention jobs (phase 3 planning-only)

## Scope

- Provide a deterministic retention audit report for phase 3 artifacts.
- Keep this slice planning-only:
  - no deletion commands,
  - no storage writes,
  - no cron or worker scheduling,
  - no external storage calls.
- Preserve immutable audit expectations for retention safety evidence.

## Inputs

Each artifact record must include:

- `record_type` (`event_records`, `room_state_history`, `person_vehicle_links`, `face_plate_audit`, `media_metadata`, `foreign_plate_person_alerts`)
- `age_days` (number)

Optional metadata may include:

- `record_id`
- `source`
- `room_id`
- `ts`

## Rules

- Load policy windows from `config/policies/retention.yaml`.
- For each record, compare `age_days` to the configured policy retention for `record_type`.
- A record is a cleanup candidate when `age_days > retention_days`.
- Report remains deterministic by sorting candidates and retained records by:
  - `record_type`
  - `age_days`
  - `record_id`

## Output contract

The audit report must indicate:

- retention report scope and policy version
- immutable audit expectations
- whether dry-run cleanup is required
- explicit retained records
- explicit cleanup candidates

## Planning behavior

- The report is advisory and safe-only.
- Cleanup is always dry-run for phase 3 hardening.
- Operators can consume the report to decide whether runtime cleanup execution should be enabled later.

## Backlog link

- `TASK-020 security_and_retention_jobs`
