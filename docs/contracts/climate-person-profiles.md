# Climate Person Profiles

This document defines the first deterministic climate preference profile slice for phase 0.

## Scope

- Resolve a person's climate preference profile from a room assignment plan.
- Preserve room context, assignment metadata, and the input climate profile mapping in the output.
- Keep the slice planning-only; it must not perform any climate-control action.

## Policy

- A climate profile is applied only when the assignment includes a person and that person has a mapped profile.
- When no person is assigned or no profile can be resolved, the plan returns `should_apply: false`.
- The output is a planning artifact only and does not execute climate control.
- The slice must not directly trigger person-targeted automations.

## Backlog Link

- `TASK-013 climate_person_profiles`
