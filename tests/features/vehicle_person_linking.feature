Feature: Vehicle-person linking for driveway planning

  Scenario: High-confidence driveway plate and face evidence emits linked arrival event
    Given a raw driveway linking payload with person "Sel", plate "ab c-12", plate_confidence 0.86, face_match_confidence 0.84, direction "enter", and camera "frigate_driveway"
    When the linked event is normalized
    Then the linked event type should be "vehicle_arrival"
    And the linked event should keep person_id "Sel"
    And the linked event should keep room "driveway"
    And the linked event should keep camera "frigate_driveway"
    And the linked event should keep plate "ABC12"

  Scenario: Low-confidence payload is rejected before linking
    Given a raw driveway linking payload with person "Sel", plate "ab c-12", plate_confidence 0.5, face_match_confidence 0.84, direction "enter", and camera "frigate_driveway"
    When the linked event is normalized
    Then linking should be rejected

  Scenario: Non-driveway linking payload is rejected
    Given a raw linking payload with room "hall" and plate "ABC123"
    When the linked event is normalized
    Then linking should be rejected
