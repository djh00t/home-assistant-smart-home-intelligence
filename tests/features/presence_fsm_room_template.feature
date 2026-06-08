Feature: Room presence FSM template

  Scenario: Humans only room resolves to the humans state
    Given a room snapshot for "hall" with 1 human and 0 pets
    When the room state template is evaluated
    Then the occupancy mode should be "humans_only"
    And the canonical room state should be "humans_only"

  Scenario: Master bedroom sleeping state suppresses wake scenes
    Given a room snapshot for "master_bedroom" with sleep mode enabled
    And bed motion is still active
    When the room state template is evaluated
    Then the canonical room state should be "bed_motion_only"
    And the wake scene should remain suppressed
