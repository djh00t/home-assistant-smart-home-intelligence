Feature: Vehicle-person linking for zone_alpha planning

  Scenario: High-confidence zone_alpha plate and face evidence emits linked arrival event
    Given a raw zone_alpha linking payload with person "Sel", plate "ab c-12", plate_confidence 0.86, face_match_confidence 0.84, direction "enter", and camera "frigate_zone_alpha"
    When the linked event is normalized
    Then the linked event type should be "vehicle_arrival"
    And the linked event should keep person_id "Sel"
    And the linked event should keep room "zone_alpha"
    And the linked event should keep camera "frigate_zone_alpha"
    And the linked event should keep plate "ABC12"

  Scenario: Fallback event_id stays opaque for linked departure events
    Given a raw zone_alpha linking payload with person "Sel", plate "xy z-9", plate_confidence 1.0, face_match_confidence 0.9, direction "exit", and camera "frigate_zone_alpha"
    When the linked event is normalized
    Then the linked event type should be "vehicle_departure"
    And the linked event should use an opaque fallback event_id
    And the linked event should not expose person "Sel" in the event_id
    And the linked event should not expose plate "XYZ9" in the event_id

  Scenario: Low-confidence payload is rejected before linking
    Given a raw zone_alpha linking payload with person "Sel", plate "ab c-12", plate_confidence 0.5, face_match_confidence 0.84, direction "enter", and camera "frigate_zone_alpha"
    When the linked event is normalized
    Then linking should be rejected

  Scenario: Non-zone_alpha linking payload is rejected
    Given a raw linking payload with room "room_delta" and plate "ABC123"
    When the linked event is normalized
    Then linking should be rejected
