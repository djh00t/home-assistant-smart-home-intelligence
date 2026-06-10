Feature: Arrival Zone zone setup canonicalization

  Scenario: Arrival Zone zone is configured as the canonical exterior zone
    Given the zone_alpha zone setup contract is present
    When canonical zone setup is loaded
    Then the canonical room id should be "zone_alpha"
    And source priority should start with "anpr"

  Scenario: Arrival Zone direction normalization is deterministic
    Given a zone_alpha event has raw direction "enter"
    When the direction is normalized
    Then the canonical direction should be "arrival"
    Given a zone_alpha event has raw direction "exit"
    When the direction is normalized
    Then the canonical direction should be "departure"
