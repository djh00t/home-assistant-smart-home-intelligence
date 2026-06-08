# Changelog

All notable changes to this project are documented in this file.

## [0.1.0] - 2026-06-08

### Added

- Canonical phase 0 room inventory with `bedroom_master`, `bedroom_max`, `bedroom_spare`, `lounge_room`, `garage`, `driveway`, `backyard_shed`, `backyard_deck`, and `kitchen`.
- Semver release bookkeeping via a canonical `VERSION` file and normalized `0.1.0` artifact headers.
- Legacy room alias normalization for `hall`, `living_room`, `office`, and `master_bedroom` inputs.
- Updated phase 0 contract docs, validators, and BDD coverage to reflect the new room model.
