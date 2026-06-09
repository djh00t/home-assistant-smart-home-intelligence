# HACS package management for smart home presence intelligence

This document defines the HACS-first packaging contract for the repository.
The package must remain installable, upgradeable, downgradeable, and removable as a single Home Assistant custom integration.

## Scope

- Root HACS metadata in `hacs.json`
- Custom integration runtime in `custom_components/smart_home_presence_intelligence/`
- Brand asset in `brand/icon.png`
- Release/version alignment through `VERSION`, `CHANGELOG.md`, and `manifest.json`
- BDD coverage for install, upgrade, downgrade, and remove expectations

## Required files

- `hacs.json`
- `brand/icon.png`
- `custom_components/smart_home_presence_intelligence/__init__.py`
- `custom_components/smart_home_presence_intelligence/bridge.py`
- `custom_components/smart_home_presence_intelligence/const.py`
- `custom_components/smart_home_presence_intelligence/config_flow.py`
- `custom_components/smart_home_presence_intelligence/diagnostics.py`
- `custom_components/smart_home_presence_intelligence/manifest.json`
- `custom_components/smart_home_presence_intelligence/repair.py`
- `custom_components/smart_home_presence_intelligence/runtime.py`
- `custom_components/smart_home_presence_intelligence/services.yaml`
- `custom_components/smart_home_presence_intelligence/strings.json`
- `custom_components/smart_home_presence_intelligence/translations/en.json`

## Release rules

- The repository `VERSION` file is the canonical release number.
- The integration `manifest.json` version must match `VERSION`.
- `CHANGELOG.md` must include a matching entry for every released version.
- HACS packaging must preserve downgradeability by keeping every release self-contained.

## Runtime rules

- The integration publishes canonical presence events to `ha/presence/event`.
- Rejected or unverifiable events route to `ha/presence/event/dlq`.
- Diagnostics payloads must remain redacted and recorder-safe.
- Repair issues should surface contract drift, missing dependencies, or release mismatches.

## Acceptance criteria

- The repository installs through HACS as one integration entry.
- The integration can be upgraded and removed without breaking repository metadata.
- Version drift between manifest, changelog, and VERSION is rejected by validation.

