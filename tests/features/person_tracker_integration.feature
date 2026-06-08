Feature: Person tracker integration

  Scenario: Mobile app tracker normalizes to canonical tracker events
    Given a mobile app tracker signal for "sel"
    When the tracker signal is normalized
    Then the canonical source should be "tracker"
    And the person id should be "sel"
    And the canonical event type should reflect tracker confidence

  Scenario: Geofencing tracker defaults to house-level room context
    Given a geofencing tracker signal for "sam"
    When the tracker event is built
    Then the canonical room should default to "house"
    And the tracker state should be preserved in context
