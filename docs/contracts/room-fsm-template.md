# Room Presence FSM Template

This document defines the first room-state-machine slice for phase 1.

## Scope

- Encode a template for room occupancy and sleep-state transitions.
- Keep the template consistent with the room capability inventory and bridge contract.
- Give later dwell and lighting tasks a stable state vocabulary.

## States

- `empty`
- `humans_only`
- `pets_only`
- `mixed`
- `sleeping`
- `bed_motion_only`

## Transition Notes

- Empty rooms become `humans_only` or `pets_only` when the corresponding occupancy count becomes non-zero.
- Mixed occupancy is used when both humans and pets are present.
- The master bedroom can enter `sleeping` and `bed_motion_only` states.
- `bed_motion_only` is a transient sleep-safe state that keeps wake scenes suppressed.

## Backlog Link

- `TASK-002 presence_fsm_room_template`
