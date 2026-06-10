Feature: Desk light profiles

  Scenario: Spare bedroom desk-light profile resolves for an assigned person
    Given room "room_gamma" has assigned person "Sel"
    And assignment source is "face+tracker"
    And assignment confidence is 0.93
    And desk profiles map "Sel" to "sel_desk"
    When the desk-light profile plan is resolved
    Then the room id should remain "room_gamma"
    And the assigned person should be "Sel"
    And the desk-light profile should be "sel_desk"
    And should apply should be true

  Scenario: Non-room_gamma rooms do not resolve desk-light profiles
    Given room "room_epsilon" has assigned person "Sel"
    And assignment source is "occupancy_fallback"
    And assignment confidence is 0.7
    And desk profiles map "Sel" to "sel_desk"
    When the desk-light profile plan is resolved
    Then the room id should remain "room_epsilon"
    And the assigned person should be "Sel"
    And the desk-light profile should be empty
    And should apply should be false
