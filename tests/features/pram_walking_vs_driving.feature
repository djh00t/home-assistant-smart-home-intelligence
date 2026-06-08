Feature: Pram walking-vs-driving classification

  Scenario: Pram snapshot is walk when matching vehicle context is absent
    Given a snapshot for person "Sel" in room "lounge_room" with with_pram true
    And the matching vehicle context age is 120 seconds
    When transport mode is classified
    Then the transport mode should be "walk"
    And room and person context should be preserved

  Scenario: Pram snapshot is drive when matching vehicle context is fresh
    Given a snapshot for person "Sel" in room "lounge_room" with with_pram true
    And the matching vehicle context age is 30 seconds
    When transport mode is classified
    Then the transport mode should be "drive"

  Scenario: Non-pram snapshot is not classified as pram transport
    Given a snapshot for room "bedroom_spare" with with_pram false
    When transport mode is classified
    Then the transport mode should be "not_pram"
