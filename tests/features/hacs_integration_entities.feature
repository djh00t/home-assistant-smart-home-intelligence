Feature: HACS integration entities
  Scenario: Room activity sensors reflect routed events
    Given the integration runtime has a routed presence event for room "room_delta"
    Then the lounge room state sensor should be available
    And the lounge room state sensor should show "occupied"
    And the lounge room state sensor should not expose room telemetry attributes

  Scenario: Manual override is surfaced as a binary sensor
    Given manual override is enabled in the runtime
    Then the manual override binary sensor should be on

  Scenario: Runtime state only persists restore-safe fields
    Given the runtime has a retention audit result and a room activity snapshot
    When the runtime state is serialized
    Then the serialized payload should exclude room activity and last routed event
    And the serialized payload should include override state, bridge health, and retention status

  Scenario: Diagnostics export respects the diagnostics toggle
    Given diagnostics are disabled in the runtime settings
    Then the diagnostics payload should only report that diagnostics are disabled
