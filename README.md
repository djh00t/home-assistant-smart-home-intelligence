# Smart Home Presence Intelligence

HACS-first Home Assistant integration for presence routing, room state, lighting policy, and operator-facing runtime controls.

[![Open your Home Assistant instance and show the repository in HACS](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=djh00t&repository=home-assistant-smart-home-intelligence&category=integration)

This repository packages the Home Assistant side of a smart-home presence system. It consumes canonical MQTT presence events, normalizes room and policy state, exposes Home Assistant entities and services, and keeps external inference systems out of the HA runtime.

## What It Does

- Consumes canonical presence events from MQTT.
- Tracks room state for `bedroom_master`, `bedroom_max`, `bedroom_spare`, `lounge_room`, `garage`, `driveway`, `backyard_shed`, `backyard_deck`, and `kitchen`.
- Publishes operator-facing sensors for room activity, bridge health, retention, house mode, and room lighting policy.
- Exposes Home Assistant services for test events, contract reloads, manual overrides, and retention audits.
- Restores runtime state across Home Assistant reloads so current state is not lost on restart.
- Keeps Frigate, Jetson, ANPR, face recognition, and other inference services external to the integration.

## What It Looks Like

### Example entities

The integration creates runtime-backed entities such as:

```text
sensor.lounge_room_state                 occupied
sensor.bridge_health                     healthy
sensor.retention_audit_status            pass
sensor.house_mode                        occupied
sensor.lounge_room_white_scene           lounge_room_day
sensor.lounge_room_color_sync            true
binary_sensor.manual_override_active     off
binary_sensor.diagnostics_enabled        on
```

### Example room policy state

Per-room policy sensors reflect both room capabilities and live occupancy:

```yaml
room_id: lounge_room
house_mode: occupied
supports_lighting: true
supports_color: true
white_scene: lounge_room_day
color_sync_enabled: true
manual_override_minutes: 45
occupancy_state: occupied
human_count: 1
pet_count: 0
vehicle_count: 0
```

### Example MQTT event

The canonical event contract is intentionally small and recorder-safe:

```json
{
  "event_id": "evt-001",
  "source": "tracker",
  "type": "enter",
  "room": "lounge_room",
  "entity_class": "human",
  "confidence": 0.98,
  "ts": "2026-06-09T12:00:00Z"
}
```

### Example Home Assistant service calls

Publish a synthetic event through the integration:

```yaml
service: smart_home_presence_intelligence.publish_test_event
data:
  source: tracker
  room: lounge_room
  type: enter
```

Enable a manual override:

```yaml
service: smart_home_presence_intelligence.set_override
data:
  enabled: true
  reason: family activity
```

## Install

### HACS

1. Click the HACS button above.
2. If HACS does not open the repository directly, add this repo as a custom repository in HACS with category `integration`.
3. Install `Smart Home Presence Intelligence`.
4. Restart Home Assistant.
5. Add the integration in `Settings > Devices & services`.

### Manual fallback

1. Copy `custom_components/smart_home_presence_intelligence` into your Home Assistant `custom_components/` directory.
2. Restart Home Assistant.
3. Add the integration in `Settings > Devices & services`.

## Configure

The config flow expects these inputs:

| Setting | Purpose | Default |
| --- | --- | --- |
| `mqtt_topic_prefix` | Base MQTT namespace used by the integration | `ha/presence` |
| `room_inventory_path` | YAML inventory of canonical rooms and zones | `config/inventory/rooms.yaml` |
| `room_capabilities_path` | YAML capability catalog for lighting and policy behavior | `config/inventory/room_capabilities.yaml` |
| `retention_days` | Retention target for audit and event history | `90` |
| `enable_diagnostics` | Expose redacted diagnostics entities and payloads | `true` |

## Drive It

The integration exposes these Home Assistant services:

| Service | Purpose |
| --- | --- |
| `publish_test_event` | Send a synthetic event through the MQTT bridge and runtime model |
| `reload_contracts` | Reload inventory, capability, and contract-backed runtime data |
| `set_override` | Toggle a manual override with an operator-readable reason |
| `run_retention_audit` | Produce a retention audit summary with redacted metadata |

The main runtime entity groups are:

| Entity group | Examples |
| --- | --- |
| Room activity sensors | `sensor.lounge_room_state`, `sensor.kitchen_state` |
| Bridge and runtime sensors | `sensor.bridge_health`, `sensor.bridge_last_topic` |
| Retention sensors | `sensor.retention_days`, `sensor.retention_audit_status` |
| Override and diagnostics binary sensors | `binary_sensor.manual_override_active`, `binary_sensor.diagnostics_enabled` |
| House and room policy sensors | `sensor.house_mode`, `sensor.lounge_room_white_scene`, `sensor.bedroom_spare_color_sync` |

## Architecture

- Home Assistant integration: config flow, services, diagnostics, repairs, runtime state, entities.
- MQTT contract: canonical ingress topic plus dead-letter routing.
- Room inventory: explicit room and external-zone model.
- Room capabilities: lighting support, color support, default scenes, and policy flags.
- External inference layer: Frigate, Jetson, ANPR, face match, and other upstream systems publish into the canonical event contract.

## MQTT Contract

- Canonical topic: `ha/presence/event`
- Dead-letter topic: `ha/presence/event/dlq`
- Allowed sources: `frigate`, `mmwave`, `motion`, `face`, `anpr`, `tracker`
- Allowed entity classes: `human`, `pet`, `vehicle`

See the full contract in [config/contracts/presence_event.schema.json](config/contracts/presence_event.schema.json) and [docs/contracts/hacs-package-management.md](docs/contracts/hacs-package-management.md).

## Repository Layout

- `custom_components/smart_home_presence_intelligence/` — Home Assistant integration code
- `config/inventory/` — room inventory and room capability catalogs
- `config/contracts/` — MQTT, runtime, and behavior contracts
- `tests/features/` — BDD coverage for install, runtime, and policy behavior
- `scripts/` — local validation gates used by `make check` and `make quality-gates`

## Development

```bash
make check
make quality-gates
```

These commands validate the README, contracts, package shape, release alignment, and BDD feature coverage used by the repo.

## More Detail

- [Specification](docs/specs/2026-06-07-smart-home-intelligence-spec.md)
- [Roadmap](docs/roadmap/roadmap.md)
- [Implementation plan](docs/plans/implementation-plan.md)
- [Task backlog](docs/tasks/task_backlog.md)
