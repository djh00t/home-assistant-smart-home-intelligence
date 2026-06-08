# MmWave Fusion Rule

This document defines the first mmWave fusion slice for phase 2.

## Scope

- Fuse mmWave and Frigate room occupancy signals into a canonical room state.
- Prefer mmWave as the leading source for room presence.
- Keep Frigate as a continuity source when mmWave is briefly absent.
- Provide a stable fused room state for later automation slices.

## Policy

- `mmwave` is the preferred room-presence source.
- `frigate` may keep room presence alive when a track is still present.
- Fused room state is the input to occupancy and lighting automation.
- This slice does not attempt identity resolution.

## Backlog Link

- `TASK-009 mmwave_fusion_rule`
