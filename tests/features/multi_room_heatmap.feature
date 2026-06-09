Feature: Multi-room heatmap report for occupancy review

  Scenario: Occupancy observations across multiple rooms create a heatmap report
    Given occupancy observations for room_delta, room_epsilon, and room_gamma
    And zone_alpha observations are present but ignored
    When the multi-room heatmap report is built
    Then the report should be created
    And the report id should be opaque and deterministic
    And the report should include only occupancy-supporting rooms
    And the report should sort rooms deterministically
    And the report should omit per-room provenance and timestamp detail
    And the report should remain planning-only

  Scenario: Arrival Zone-only observations do not create a report
    Given only zone_alpha observations are available
    When the multi-room heatmap report is built
    Then no report should be created
