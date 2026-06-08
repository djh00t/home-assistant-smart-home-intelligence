# Bed State Override

This document defines the first bed-state override slice for phase 0.

## Scope

- Suppress wake scenes while the master bedroom is in a sleep-safe state.
- Distinguish between sleeping and bed-motion-only activity.
- Clear the override when an exit event is observed.

## Policy

- `sleeping` suppresses wake scenes.
- `bed_motion_only` suppresses wake scenes.
- Exit events clear the override and return the room to `awake`.

## Backlog Link

- `TASK-006 bed_state_override`
