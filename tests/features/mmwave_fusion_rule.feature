Feature: MmWave fusion rule

  Scenario: MmWave and Frigate together produce high-confidence room occupancy
    Given the room_delta room has mmWave activity and a Frigate track
    When the room fusion rule is evaluated
    Then the occupancy mode should be "humans_only"
    And the fusion confidence should be high
    And the primary source should include both mmWave and Frigate

  Scenario: Frigate alone keeps room presence with lower confidence
    Given the room_delta room has a Frigate track but no mmWave activity
    When the room fusion rule is evaluated
    Then the occupancy mode should still be "humans_only"
    And the fusion confidence should be lower than the mmWave combined case
    And the primary source should be "frigate"
