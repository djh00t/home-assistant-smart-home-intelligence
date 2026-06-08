# Smart Home Intelligence Repo (Private Project)

This directory contains the phase 1 core occupancy and lighting bundle for your Home Assistant automation design, plus the earlier phase 0 foundation artifacts:

- [Smart home spec](docs/specs/2026-06-07-smart-home-intelligence-spec.md)
- [Roadmap](docs/roadmap/roadmap.md)
- [Implementation plan](docs/plans/implementation-plan.md)
- [Task backlog](docs/tasks/task_backlog.md)
- [Phase 1 occupancy and lighting feature scenarios](tests/features/smart_home_presence.feature)
- [Room FSM feature scenarios](tests/features/presence_fsm_room_template.feature)
- [Dwell reset feature scenarios](tests/features/dwell_reset_automation.feature)
- [Adaptive white-lighting feature scenarios](tests/features/adaptive_white_lighting.feature)
- [Color sync feature scenarios](tests/features/color_sync_for_color_lights.feature)
- [Bed-state override feature scenarios](tests/features/bed_state_override.feature)
- [Phase 0 foundation feature scenarios](tests/features/phase0_foundation.feature)

## How this repo is organized

- `config/` — phase 0 inventory, contract, and retention artifacts.
- `docs/` — specification, roadmap, implementation plan, tasks, and contract notes.
- `scripts/` — validation helpers for docs, project scaffolding, contracts, and features.
- `src/` — the minimal Python package root for future implementation work.
- `tests/features/` — BDD scenarios for behavior and acceptance gates.

## Current status

- Created as an isolated private project folder under your workspace.
- Phase 1 core occupancy and lighting artifacts are now checked in locally.
- Phase 0 foundation artifacts remain available for the broader project baseline.
- Later-phase slices are documented and queued for subsequent work.

## Publish as private GitHub repository

The project is prepared as a local repository bundle under:
- `/Users/djh/work/src/github.com_local/djh00t/smart-home-presence-intelligence`

Run these commands once `gh` auth is valid:

```bash
gh auth login
cd /Users/djh/work/src/github.com_local/djh00t/smart-home-presence-intelligence
gh repo create home-assistant-smart-home-intelligence --private --source . --remote origin --push
```

If you want a different repo name, replace `home-assistant-smart-home-intelligence`.
