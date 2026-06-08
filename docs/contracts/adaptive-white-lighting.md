# Adaptive White Lighting

This document defines the first adaptive white-lighting slice for phase 0.

## Scope

- Apply circadian white-light scenes for occupied rooms.
- Preserve hue and temperature policy for white lights.
- Prevent automatic full-brightening during bed-motion-only states.
- Respect manual override windows.

## Policy

- Morning and day use the room's day scene.
- Evening uses the room's evening scene when available, otherwise the night scene.
- Night uses the room's night scene.
- `sleeping` and `bed_motion_only` should not auto-trigger a full-bright scene.
- Manual override windows suppress automatic white-light changes.

## Backlog Link

- `TASK-004 adaptive_white_lighting`
