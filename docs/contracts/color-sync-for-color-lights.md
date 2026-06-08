# Color Sync for Color Lights

This document defines the first color-sync slice for phase 1.

## Scope

- Sync color scenes only to groups that support color.
- Leave white-only room groups on their white-light policy.
- Preserve the existing white-light behavior when color scenes are requested.

## Policy

- Color scene requests may target only rooms with `supports_color: true`.
- White-only rooms never receive color sync actions.
- Color scene requests should not replace the room's white-light policy.

## Backlog Link

- `TASK-005 color_sync_for_color_lights`
