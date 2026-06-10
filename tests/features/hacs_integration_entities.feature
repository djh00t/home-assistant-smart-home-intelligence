Feature: HACS integration entities
  Scenario: Room activity sensors reflect routed events
    Given the integration runtime has a routed presence event for room "lounge_room"
    Then the lounge room state sensor should be available
    And the lounge room state sensor should show "occupied"

  Scenario: Manual override is surfaced as a binary sensor
    Given manual override is enabled in the runtime
    Then the manual override binary sensor should be on

  Scenario: Policy entities register through the sensor platform
    Given the integration is loaded by Home Assistant
    Then runtime sensors and room policy sensors should be registered on the sensor platform

  Scenario: Packaged defaults support reload contracts after HACS install
    Given the integration is installed by HACS without repository root config files
    When reload contracts is called
    Then packaged room capability defaults should be used

  Scenario: Runtime state is serializable for restore
    Given the runtime has a retention audit result and a room activity snapshot
    When the runtime state is serialized
    Then the serialized payload should include bridge health, room activity, and retention status
