Feature: Status and configuration dashboard for Home Assistant operations

  Scenario: Runtime snapshot creates ordered status and configuration sections
    Given the runtime snapshot is available
    When the status and configuration dashboard is built
    Then the dashboard should be created
    And the dashboard should include overview, configuration, actions, Jetson Xavier, and rooms sections
    And the dashboard should include the canonical rooms in order
    And the dashboard should surface the MQTT topic prefix, room inventory path, room capability path, and retention settings
    And the dashboard should remain read-only for persistent configuration

  Scenario: Action cards target the existing integration services
    Given the runtime snapshot is available
    When the status and configuration dashboard is built
    Then the dashboard should expose service actions for publish_test_event, reload_contracts, set_override, and run_retention_audit

  Scenario: Missing room activity still yields a safe dashboard
    Given the runtime snapshot is missing room activity
    When the status and configuration dashboard is built
    Then the dashboard should still be created
    And the dashboard should default missing rooms to idle
