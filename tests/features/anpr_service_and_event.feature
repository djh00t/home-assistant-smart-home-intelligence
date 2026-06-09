Feature: ANPR zone_alpha vehicle normalization and event planning

  Scenario: Canonical ANPR zone_alpha plate enters as vehicle presence event
    Given a raw zone_alpha ANPR payload with plate "ab c-12-34", plate_confidence 0.9 and camera "frigate_zone_alpha"
    And direction "enter" and room_id "zone_alpha"
    When the ANPR snapshot is normalized
    Then the canonical event source should be "anpr"
    And the event should use an opaque fallback event id
    And the room should be "zone_alpha"
    And the entity class should be "vehicle"
    And the event type should be "enter"
    And the vehicle should be canonicalized plate "ABC1234" with confidence 0.9

  Scenario: Non-zone_alpha ANPR payload is rejected
    Given a raw ANPR payload with room_id "room_delta" and plate "XYZ-9"
    When the ANPR snapshot is normalized
    Then normalization should be rejected
