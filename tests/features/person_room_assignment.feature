Feature: Person room assignment

  Scenario: Face and tracker agree on the same occupied person
    Given room "room_gamma" has occupied humans "sel" and "sam"
    And face identity matches "sel" with high confidence
    And tracker identity matches "sel" with supporting confidence
    When the room assignment plan is built
    Then the assigned person should be "sel"
    And the assignment source should be "face+tracker"
    And the room context should remain "room_gamma"

  Scenario: Single occupied human falls back without identity signals
    Given room "room_epsilon" has occupied humans "sam"
    And no face or tracker identity is available
    When the room assignment plan is built
    Then the assigned person should be "sam"
    And the assignment source should be "occupancy_fallback"
    And the occupied humans list should be preserved
