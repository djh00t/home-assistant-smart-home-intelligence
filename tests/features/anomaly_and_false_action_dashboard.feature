Feature: Anomaly and false-action dashboard for review planning

  Scenario: Mixed anomaly and false-action incidents create deterministic room cards
    Given anomaly and false-action incidents for lounge_room, bedroom_spare, and driveway
    And the dashboard is focused on the bedroom_spare room
    When the anomaly and false-action dashboard is built
    Then the dashboard should be created
    And the dashboard should include the canonical rooms in order
    And the dashboard should aggregate incident counts by room
    And the dashboard should remain planning-only

  Scenario: Empty incident input does not create a dashboard
    Given no incidents are available
    When the anomaly and false-action dashboard is built
    Then no dashboard should be created
