Feature: Multi-room heatmap report for occupancy review

  Scenario: Occupancy observations across multiple rooms create a heatmap report
    Given occupancy observations for hall, kitchen, and office
    And driveway observations are present but ignored
    When the multi-room heatmap report is built
    Then the report should be created
    And the report should include only occupancy-supporting rooms
    And the report should sort rooms deterministically
    And the report should remain planning-only

  Scenario: Driveway-only observations do not create a report
    Given only driveway observations are available
    When the multi-room heatmap report is built
    Then no report should be created
