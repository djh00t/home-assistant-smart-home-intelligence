# Empty House With Pet Mode Switch

This document defines the final Priority A slice for phase 0.

## Scope

- Switch the house into `pet_mode` when pets are present and no humans are home.
- Keep human occupancy authoritative over pet-only state.
- Leave pathway lighting governed by pet policy when `pet_mode` is active.

## Policy

- No humans and at least one pet means `pet_mode`.
- Any human presence means `occupied`.
- No humans and no pets means `empty`.

## Backlog Link

- `TASK-007 empty_house_with_pet_mode_switch`
