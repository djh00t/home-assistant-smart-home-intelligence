# Desk Light Profiles

This document defines the first deterministic desk-light profile slice for phase 2.

## Scope

- Resolve a person's desk-light profile from a room assignment plan.
- Restrict resolution to the `room_gamma` room.
- Preserve the assigned person, room context, and assignment metadata in the output.
- Keep the slice planning-only; it must not perform any light-control action.

## Policy

- Only `room_gamma` room plans may resolve a desk-light profile.
- A desk-light profile is applied only when the assignment includes a person and that person has a mapped profile.
- When no profile can be resolved, the plan returns `should_apply: false`.
- The output is a planning artifact only and does not execute light control.
- The slice must not directly trigger person-targeted automations.

## Backlog Link

- `TASK-012 desk_light_profiles`
