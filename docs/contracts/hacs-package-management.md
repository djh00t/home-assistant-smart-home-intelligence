# HACS package management for smart home presence intelligence

This document defines the HACS-first packaging contract for the repository.
The package must remain installable, upgradeable, downgradeable, and removable as a single Home Assistant custom integration.

## Scope

- Root HACS metadata in `hacs.json`
- Custom integration runtime in `custom_components/smart_home_presence_intelligence/`
- Brand asset in `brand/icon.png`
- Release/version alignment through `VERSION`, `CHANGELOG.md`, and `manifest.json`
- Runtime entity scaffolding for room activity, bridge health, override state, and retention status
- Room-policy sensor scaffolding for house mode and per-room lighting policy
- BDD coverage for install, upgrade, downgrade, and remove expectations

## Required files

- `hacs.json`
- `brand/icon.png`
- `custom_components/smart_home_presence_intelligence/__init__.py`
- `custom_components/smart_home_presence_intelligence/binary_sensor.py`
- `custom_components/smart_home_presence_intelligence/bridge.py`
- `custom_components/smart_home_presence_intelligence/const.py`
- `custom_components/smart_home_presence_intelligence/config_flow.py`
- `custom_components/smart_home_presence_intelligence/diagnostics.py`
- `custom_components/smart_home_presence_intelligence/manifest.json`
- `custom_components/smart_home_presence_intelligence/repair.py`
- `custom_components/smart_home_presence_intelligence/runtime.py`
- `custom_components/smart_home_presence_intelligence/sensor.py`
- `custom_components/smart_home_presence_intelligence/policy_sensor.py`
- `custom_components/smart_home_presence_intelligence/services.yaml`
- `custom_components/smart_home_presence_intelligence/strings.json`
- `custom_components/smart_home_presence_intelligence/translations/en.json`

## Release rules

- The repository `VERSION` file is the canonical release number.
- The integration `manifest.json` version must match `VERSION`.
- `CHANGELOG.md` must include a matching entry for every released version.
- The published commit must carry the matching `v<VERSION>` git tag.
- HACS packaging must preserve downgradeability by keeping every release self-contained.
- Release validation must reject drift between `VERSION`, `manifest.json`, `CHANGELOG.md`, and the release tag.

## Runtime rules

- The integration publishes canonical presence events to `ha/presence/event`.
- Rejected or unverifiable events route to `ha/presence/event/dlq`.
- Runtime state persists through config-entry restore payloads so reloads and upgrades can keep bridge health, override state, and room activity snapshots.
- Room-policy sensors derive house mode, white scene, and color-sync state from the room inventory and capability catalog.
- Diagnostics payloads must remain redacted and recorder-safe.
- Repair issues should surface contract drift, missing dependencies, or release mismatches.

## Acceptance criteria

- The repository installs through HACS as one integration entry.
- The integration can be upgraded and removed without breaking repository metadata.
- Version drift between manifest, changelog, and VERSION is rejected by validation.
- The published release is tagged and can be downgraded to the prior semver release.
