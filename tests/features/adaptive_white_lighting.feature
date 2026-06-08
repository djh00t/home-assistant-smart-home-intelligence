Feature: Adaptive white lighting

  Scenario: Circadian scenes follow the time of day
    Given the lounge_room room has white lighting available
    When the local hour is 13
    Then the white lighting scene should be "lounge_room_day"
    And the room should be eligible for full brightening

  Scenario: Bed motion only suppresses full brightening
    Given the master bedroom is in "bed_motion_only" state
    When the local hour is 13
    Then the white lighting scene should not auto-apply
    And the room should not be full brightened

  Scenario: Manual override suppresses automatic white lighting
    Given the lounge_room room has an active manual override window
    When the local hour is 18
    Then the white lighting scene should not auto-apply
    And the room should remain under manual control
