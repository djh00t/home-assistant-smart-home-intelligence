# Changelog

All notable changes to this project are documented in this file.

## [0.6.0] - 2026-06-09

### Added

- Room-policy sensor surfaces for house mode, white scenes, and color-sync decisions derived from the room capability catalog.

### Changed

- Rebased the HACS package metadata, validators, README, roadmap, and implementation plan to reflect the new runtime policy surfaces.

## [0.5.0] - 2026-06-09

### Added

- HACS-first Home Assistant integration scaffold with canonical MQTT bridge helpers, config flow, services, diagnostics, repair support, and release packaging metadata.

### Changed

- Reframed the project around an installable `smart_home_presence_intelligence` custom integration so upgrades, downgrades, and removal can follow the HACS lifecycle.

## [0.4.0] - 2026-06-09

### Added

- Delivered the Phase 4 reliability and expansion bundle: non-home zone queueing, multi-room heatmaps, scene preference UI planning, anomaly and false-action dashboard planning, and retention/reporting helpers.

### Changed

- Rebased the backlog, roadmap, README, implementation plan, and phase-specific contract docs to mark Phase 4 complete.

## [0.3.0] - 2026-06-09

### Added

- Delivered the Phase 3 vehicle and contextual recognition bundle: driveway zoning, ANPR canonicalization, face enrollment and match, vehicle-person linking, pram transport classification, foreign identity queueing, and retention job helpers.

### Changed

- Rebased the backlog, roadmap, README, implementation plan, and phase-specific contract docs to mark Phase 3 complete and queue Phase 4 work.

## [0.2.0] - 2026-06-08

### Added

- Delivered the Phase 2 people and pets bundle: person tracker ingest, mmWave and Frigate fusion, pet normalization, room assignment, desk-light profiles, climate profiles, and the empty-house pet-mode switch.

### Changed

- Rebased the backlog, roadmap, README, implementation plan, and phase-specific contract docs to mark Phase 2 complete and queue Phase 3 work.

## [0.1.0] - 2026-06-08

### Added

- Canonical phase 0 room inventory with `bedroom_master`, `bedroom_max`, `bedroom_spare`, `lounge_room`, `garage`, `driveway`, `backyard_shed`, `backyard_deck`, and `kitchen`.
- Semver release bookkeeping via a canonical `VERSION` file and normalized `0.1.0` artifact headers.
- Legacy room alias normalization for `hall`, `living_room`, `office`, and `master_bedroom` inputs.
- Updated phase 0 contract docs, validators, and BDD coverage to reflect the new room model.
