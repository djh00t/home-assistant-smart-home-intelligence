Feature: Smart home presence and personalization

  Scenario: Motion resets room dwell timer
    Given room "lounge_room" is occupied by "Sel" and a dwell timer is running
    When a motion event is received for room "lounge_room"
    Then the room dwell timer should be restarted
    And lights remain on at the active occupancy level

  Scenario: Bed motion does not trigger bright wake lights
    Given room "bedroom_master" has occupant "Sel" in bed
    And lights are currently in bright mode
    When bed motion continues without exit event
    Then lights should not switch to bright wake mode
    And room state should remain in "sleeping"

  Scenario: Person-specific desk lights apply on room entry
    Given "Sel" is assigned desk profile "sel_desk"
    When "Sel" is detected entering room "bedroom_spare" with confidence above threshold
    Then bedroom_spare desk lights should turn on to "sel_desk"
    And room climate should move toward Sel preference profile

  Scenario: Person leaves with pram and no vehicle context
    Given "Sel" exits home with "pram" context
    And no matching car context in the last 90 seconds
    When no other humans are present in all rooms
    Then non-safety lights should be turned off after room dwell windows

  Scenario: Car arrival with plate and face link drives high-confidence event
    Given a driveway vehicle track is matched with plate "ABC123"
    And face recognition links plate holder to "Sel" with confidence above threshold
    When vehicle moves into arrival zone
    Then emit "vehicle_arrival" with person_id "Sel"
    And record arrival event for audit

  Scenario: Foreign plate record retained
    Given a face is unknown and plate is unknown
    When ANPR and face events fire in driveway zone
    Then create a foreign event record
    And keep the record for at least 90 days

  Scenario: Pet-only occupancy should not trigger person actions
    Given only "cat" is present in room "kitchen"
    When occupancy is evaluated
    Then house status should be "pets_only"
    And desk lights and personal climate actions should not run
    And optional pathway lighting may remain governed by pet policy
