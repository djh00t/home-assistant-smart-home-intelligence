Feature: Pet detection classifier

  Scenario: Cat detections normalize to canonical pet events
    Given a raw "cat" detection in room "room_epsilon" with confidence 0.87
    When the pet detection is classified
    Then the canonical entity class should be "pet"
    And the canonical source should be "frigate"
    And the canonical room should be "room_epsilon"
    And the confidence should be preserved
    And no person id should be set

  Scenario: Pet detections stay in pet occupancy scope
    Given a raw "dog" detection in room "room_delta" with confidence 0.92
    When the pet detection is classified
    Then the canonical event should be eligible for pet occupancy only
    And person-targeted automations should not be enabled
