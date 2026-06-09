"""Constants for the smart home presence intelligence integration."""

from __future__ import annotations


DOMAIN = "smart_home_presence_intelligence"
NAME = "Smart Home Presence Intelligence"
MANUFACTURER = "DJH"

CONF_ENABLE_DIAGNOSTICS = "enable_diagnostics"
CONF_MQTT_TOPIC_PREFIX = "mqtt_topic_prefix"
CONF_RETENTION_DAYS = "retention_days"
CONF_ROOM_INVENTORY_PATH = "room_inventory_path"

DEFAULT_ENABLE_DIAGNOSTICS = True
DEFAULT_MQTT_TOPIC_PREFIX = "ha/presence"
DEFAULT_RETENTION_DAYS = 90
DEFAULT_ROOM_INVENTORY_PATH = "config/inventory/rooms.yaml"

SERVICE_PUBLISH_TEST_EVENT = "publish_test_event"
SERVICE_RELOAD_CONTRACTS = "reload_contracts"
SERVICE_SET_OVERRIDE = "set_override"
SERVICE_RUN_RETENTION_AUDIT = "run_retention_audit"

PLATFORMS: tuple[str, ...] = ("sensor", "binary_sensor")
