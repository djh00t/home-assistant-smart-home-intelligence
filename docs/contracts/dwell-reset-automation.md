# Dwell Reset Automation

This document defines the first dwell-reset automation slice for phase 1.

## Scope

- Restart active room dwell timers when the configured motion-like sources report activity.
- Keep the active occupancy level stable while the timer is being restarted.
- Provide a stable template for later dim/off behavior.

## Contract

- `motion`, `mmwave`, and `frigate` are the first dwell-reset trigger sources.
- `enter`, `stay`, and `state_change` are the first dwell-reset trigger events.
- The canonical action is to restart the dwell timer.
- Later automation slices can use the timer stages `restart`, `dim`, and `off`.

## Backlog Link

- `TASK-003 dwell_reset_automation`
