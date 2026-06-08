Feature: Desk light profiles

  Scenario: Office desk-light profile resolves for an assigned person
    Given room "office" has assigned person "Sel"
    And assignment source is "face+tracker"
    And assignment confidence is 0.93
    And desk profiles map "Sel" to "sel_desk"
    When the desk-light profile plan is resolved
    Then the room id should remain "office"
    And the assigned person should be "Sel"
    And the desk-light profile should be "sel_desk"
    And should apply should be true

  Scenario: Non-office rooms do not resolve desk-light profiles
    Given room "kitchen" has assigned person "Sel"
    And assignment source is "occupancy_fallback"
    And assignment confidence is 0.7
    And desk profiles map "Sel" to "sel_desk"
    When the desk-light profile plan is resolved
    Then the room id should remain "kitchen"
    And the assigned person should be "Sel"
    And the desk-light profile should be empty
    And should apply should be false

