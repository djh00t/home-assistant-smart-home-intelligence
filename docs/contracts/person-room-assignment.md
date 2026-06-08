# Person Room Assignment

This document defines the first deterministic room-to-person assignment slice for phase 2.

## Scope

- Consume room context, `occupied_humans`, and optional face or tracker identity hints.
- Produce a canonical assignment plan for one room at a time.
- Prefer stronger identity evidence before occupancy-only fallback.
- Preserve room context for later desk-light and climate personalization slices.

## Policy

- Face and tracker agreement wins only when the agreed person is present in `occupied_humans`.
- Face-only or tracker-only matches may assign a person when that person is present in `occupied_humans`.
- If there is exactly one occupied human and no stronger identity signal, occupancy fallback may assign that person at low confidence.
- The output is a planning artifact only and must not directly trigger person-targeted automations.

## Backlog Link

- `TASK-011 person_room_assignment`
