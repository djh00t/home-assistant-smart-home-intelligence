Feature: Climate person profiles

  Scenario: Assigned person resolves a climate preference profile
    Given room "room_delta" has assigned person "Sel"
    And assignment source is "face+tracker"
    And assignment confidence is 0.93
    And climate profiles map "Sel" to "cool_evening"
    When the climate-person profile plan is resolved
    Then the room id should remain "room_delta"
    And the assigned person should be "Sel"
    And the climate profile should be "cool_evening"
    And should apply should be true

  Scenario: Unassigned room does not resolve a climate profile
    Given room "room_epsilon" has no assigned person
    And assignment source is "occupancy_fallback"
    And assignment confidence is 0.7
    And climate profiles map "Sel" to "cool_evening"
    When the climate-person profile plan is resolved
    Then the room id should remain "room_epsilon"
    And the assigned person should be empty
    And the climate profile should be empty
    And should apply should be false
