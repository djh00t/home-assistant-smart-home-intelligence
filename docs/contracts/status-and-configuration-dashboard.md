# Status and configuration dashboard

- Build a deterministic operational dashboard model for Home Assistant status, configuration visibility, and service actions.
- Keep persistent configuration in the existing config flow and options flow.
- Surface runtime health, room state, retention state, MQTT topic alignment, and Jetson Xavier wiring guidance.

## Scope

- No persistent configuration writes from the dashboard.
- No dashboard backend mutation.
- No scheduling writes.
- No actuation beyond the existing integration services.

## Input

- `runtime_snapshot`
- optional `ts`

## Normalization

- Load canonical room inventory from `config/inventory/rooms.yaml`.
- Load canonical room capabilities from `config/inventory/room_capabilities.yaml`.
- Include all canonical rooms in inventory order.
- Keep the MQTT bridge topics aligned with `ha/presence/event` and `ha/presence/event/dlq`.

## Output

- `source: status_and_configuration_dashboard`
- deterministic `dashboard_id`
- `dashboard_record_type: status_configuration_dashboard`
- `record_name: status_and_configuration_dashboard`
- `dashboard_status: ready`
- `tabs` for overview, configuration, actions, Jetson Xavier, and rooms
- `sections` for overview, configuration, actions, Jetson Xavier, and rooms
- `config_snapshot`
- `action_cards`
- `jetson_cards`
- `room_cards`
- immutable 90-day retention metadata

## Actions

- `smart_home_presence_intelligence.publish_test_event`
- `smart_home_presence_intelligence.reload_contracts`
- `smart_home_presence_intelligence.set_override`
- `smart_home_presence_intelligence.run_retention_audit`

