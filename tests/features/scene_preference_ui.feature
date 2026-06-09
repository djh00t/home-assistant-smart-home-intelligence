Feature: Scene preference UI for room scene presets

  Scenario: Lighting rooms appear as deterministic dashboard cards
    Given the room capability catalog is available
    And the dashboard is focused on the sample_study_zone room
    When the scene preference UI is built
    Then the dashboard should be created
    And the dashboard id should be opaque and deterministic
    And the dashboard should include only lighting rooms
    And the dashboard should expose color controls only for color-capable rooms
    And the dashboard should remain planning-only

  Scenario: Non-lighting sample entries are excluded from the scene preference UI
    Given the room capability catalog is available
    When the scene preference UI is built
    Then the sample_storage_zone room should not appear in the dashboard
