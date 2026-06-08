Feature: Scene preference UI for room scene presets

  Scenario: Lighting rooms appear as deterministic dashboard cards
    Given the room capability catalog is available
    And the dashboard is focused on the bedroom_spare room
    When the scene preference UI is built
    Then the dashboard should be created
    And the dashboard should include only lighting rooms
    And the dashboard should expose color controls only for color-capable rooms
    And the dashboard should remain planning-only

  Scenario: Exterior zones are excluded from the scene preference UI
    Given the room capability catalog is available
    When the scene preference UI is built
    Then the driveway room should not appear in the dashboard
