# Arrival Zone Zone Setup

This document defines the zone_alpha as a canonical exterior zone for phase 3 planning.

## Scope

- Keep `zone_alpha` as the canonical room identifier for all zone_alpha presence events.
- Define vehicle-aware source order for zone_alpha event normalization.
- Define deterministic entry/exit normalization rules for zone_alpha direction.
- Keep behavior minimal: configuration-only planning with no ANPR or identity/linkage processing.

## Canonical Zone

- `room_id`: `zone_alpha`
- `zone_id`: `zone_alpha`
- `scope`: `exterior`
- `canonical_room_id`: `zone_alpha`

## Source Priority

Priority is explicit and deterministic:

1. `anpr`
2. `frigate`
3. `face`

- `anpr` is the preferred source for vehicle-centric events.
- `frigate` provides continuity when ANPR is not present.
- `face` is retained as a non-primary fallback signal for phase 3.

## Direction Rules

- Raw `enter`, `entered`, or `in` normalize to `arrival`.
- Raw `exit`, `exited`, or `out` normalize to `departure`.
- Raw `stay` or `stationary` normalize to `stationary`.
- Unknown raw directions default to `stationary`.

## Guardrails

- Canonical zone_alpha reference must stay `zone_alpha`.
- Configuration is planning-only and does not add ANPR, vehicle linkage, or face-matching behavior.

## Backlog Link

- `TASK-014 zone_alpha_zone_setup`
