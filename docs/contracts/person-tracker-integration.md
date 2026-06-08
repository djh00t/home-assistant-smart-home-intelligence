# Person Tracker Integration

This document defines the first Priority B slice for phase 2.

## Scope

- Ingest tracker signals from mobile apps, BLE, and geofencing.
- Normalize them into a canonical tracker state payload.
- Preserve tracker-to-person ownership for later room assignment and occupancy fusion.

## Policy

- `mobile_app`, `ble`, and `geofencing` are the first accepted tracker sources.
- Tracker states are `home`, `not_home`, `arriving`, and `leaving`.
- Tracker signals can publish presence context but do not on their own establish room identity.

## Backlog Link

- `TASK-008 person_tracker_integration`
