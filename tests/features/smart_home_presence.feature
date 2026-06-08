Feature: Phase 1 core occupancy and lighting

  Scenario: Room occupancy state resolves to humans only
    Given a room snapshot for "lounge_room" with 1 human and 0 pets
    When the room state template is evaluated
    Then the occupancy mode should be "humans_only"
    And the canonical room state should be "humans_only"

  Scenario: Motion restarts the active dwell timer
    Given a lounge_room dwell timer has 120 seconds remaining
    When a motion event is received for room "lounge_room"
    Then the dwell timer should restart to its configured duration
    And the room should remain in the active occupancy state

  Scenario: Bed motion only suppresses wake scenes
    Given the master bedroom is in bed with motion active
    When the override is evaluated
    Then the room state should be "bed_motion_only"
    And wake scenes should be suppressed

  Scenario: Circadian white scenes follow the time of day
    Given the lounge_room room has white lighting available
    When the local hour is 13
    Then the white lighting scene should be "lounge_room_day"
    And the room should be eligible for full brightening

  Scenario: Color scene requests target only color-capable rooms
    Given the bedroom_spare room supports color lighting
    When a color scene is requested for the bedroom_spare
    Then the bedroom_spare color groups should be selected
    And white groups should remain on the white-light policy
