Feature: Face enrollment and match canonicalization

  Scenario: Canonical face enrollment record captures identity and context without raw biometric leakage
    Given a raw face enrollment with person "sel", room "room_gamma" and camera "cam_room_delta_front"
    And face signature "sig_abc123"
    When enrollment is normalized
    Then the enrollment record should preserve person_id "sel"
    And the enrollment room should be "room_gamma"
    And the enrollment camera should be "cam_room_delta_front"
    And the enrollment should use an opaque deterministic face signature
    And the enrollment should use an opaque fallback enrollment_id
    And the enrollment_id should not expose person "sel"
    And the enrollment_id should not expose room "room_gamma"
    And the retention days should be "90"

  Scenario: Canonical face match event is emitted with stable source, confidence, and opaque fallback event_id
    Given a face match for person "sel" in room "room_gamma" from camera "cam_room_delta_front"
    And face_match_confidence "0.84"
    When the match is normalized
    Then the match event source should be "face"
    And the entity class should be "human"
    And the event should keep person_id "sel"
    And the event should keep room "room_gamma"
    And the event should keep camera "cam_room_delta_front"
    And the face_match_confidence should be "0.84"
    And the match event should use an opaque fallback event_id
    And the match event should not expose person "sel" in the event_id
    And the match event should not expose room "room_gamma" in the event_id
