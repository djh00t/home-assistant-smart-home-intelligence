# Jetson Xavier, Frigate, and MQTT

This repository keeps the Home Assistant integration on one side and the Jetson Xavier inference stack on the other side. The Jetson should run Frigate and publish to the same MQTT broker that Home Assistant uses, while the integration consumes canonical presence events from MQTT.

## What to run on the Jetson

- Frigate for camera and detection workloads.
- An MQTT client or bridge that republishes canonical presence events.
- No Home Assistant secrets or long-lived API tokens on the Jetson unless you explicitly need them for a separate automation.

## Broker and topic settings

The integration expects the canonical topic pair below:

- `ha/presence/event`
- `ha/presence/event/dlq`

Keep the `mqtt_topic_prefix` in the integration aligned with the broker-side namespace you use for the presence bridge. The default is `ha/presence`.

## Example Frigate MQTT block

```yaml
mqtt:
  host: 192.168.1.10
  port: 1883
  user: frigate
  password: your_password_here
  client_id: jetson-xavier-frigate
  topic_prefix: frigate
```

## Minimal wiring steps

1. Install Frigate on the Jetson Xavier.
2. Point Frigate at your MQTT broker.
3. Publish or translate detections into the canonical presence contract used by this repo.
4. Confirm the integration's `mqtt_topic_prefix` stays aligned with the bridge namespace.
5. Open the status dashboard and verify bridge health, topic routing, and room state.

## Network and security

- Allow the Jetson to reach the MQTT broker on the broker's MQTT port, usually `1883` or `8883`.
- Do not expose the broker or Home Assistant to the internet just for this integration.
- Use separate credentials for the Jetson bridge and rotate them if the device is re-imaged.
- Prefer TLS on the broker if the Jetson and Home Assistant are not on the same trusted LAN.

## Verification checklist

- Use the dashboard's `publish_test_event` button to confirm the integration can route synthetic events through MQTT.
- `sensor.bridge_health` reports `healthy`.
- `sensor.bridge_last_topic` shows `ha/presence/event`.
- `sensor.mqtt_topic_prefix` matches the bridge namespace.
- `sensor.retention_audit_status` returns `pass` after a retention audit.
- The dashboard's Publish test event button routes through the canonical MQTT bridge.

## Troubleshooting

- If `sensor.bridge_health` shows `degraded`, inspect the dead-letter topic `ha/presence/event/dlq`.
- If events are missing, confirm the Jetson can publish to the MQTT broker and that Frigate is still running.
- If the dashboard shows the wrong prefix, update the integration options flow and restart Home Assistant if needed.
