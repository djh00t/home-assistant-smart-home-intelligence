Feature: Driveway zone setup canonicalization

  Scenario: Driveway zone is configured as the canonical exterior zone
    Given the driveway zone setup contract is present
    When canonical zone setup is loaded
    Then the canonical room id should be "driveway"
    And source priority should start with "anpr"

  Scenario: Driveway direction normalization is deterministic
    Given a driveway event has raw direction "enter"
    When the direction is normalized
    Then the canonical direction should be "arrival"
    Given a driveway event has raw direction "exit"
    When the direction is normalized
    Then the canonical direction should be "departure"
