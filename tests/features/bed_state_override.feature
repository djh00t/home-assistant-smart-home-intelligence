Feature: Bed state override

  Scenario: Bed motion only suppresses wake scenes
    Given the master bedroom is in bed with motion active
    When the override is evaluated
    Then the room state should be "bed_motion_only"
    And wake scenes should be suppressed

  Scenario: Exit events clear the bed override
    Given the master bedroom is in bed with motion active
    And an exit event is received
    When the override is evaluated
    Then the room state should be "awake"
    And wake scenes should no longer be suppressed
