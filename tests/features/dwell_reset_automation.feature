Feature: Dwell reset automation

  Scenario: Motion restarts the active dwell timer
    Given a room_delta dwell timer has 120 seconds remaining
    When a motion event is received for room "room_delta"
    Then the dwell timer should restart to its configured duration
    And the room should remain in the active occupancy state

  Scenario: Foreign events do not restart the dwell timer
    Given a room_epsilon dwell timer has 60 seconds remaining
    When a zone_alpha ANPR event is received
    Then the dwell timer should remain unchanged
    And the room should keep its current occupancy state
