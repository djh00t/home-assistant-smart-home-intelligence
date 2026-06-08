Feature: ANPR driveway vehicle normalization and event planning

  Scenario: Canonical ANPR driveway plate enters as vehicle presence event
    Given a raw driveway ANPR payload with plate "ab c-12-34", plate_confidence 0.9 and camera "frigate_driveway"
    And direction "enter" and room_id "driveway"
    When the ANPR snapshot is normalized
    Then the canonical event source should be "anpr"
    And the room should be "driveway"
    And the entity class should be "vehicle"
    And the event type should be "enter"
    And the vehicle should be canonicalized plate "ABC1234" with confidence 0.9

  Scenario: Non-driveway ANPR payload is rejected
    Given a raw ANPR payload with room_id "lounge_room" and plate "XYZ-9"
    When the ANPR snapshot is normalized
    Then normalization should be rejected
