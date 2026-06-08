Feature: Face enrollment and match canonicalization

  Scenario: Canonical face enrollment record captures identity and context
    Given a raw face enrollment with person "sel", room "office" and camera "cam_hall_front"
    And face signature "sig_abc123"
    When enrollment is normalized
    Then the enrollment record should preserve person_id "sel"
    And the enrollment room should be "office"
    And the enrollment camera should be "cam_hall_front"
    And the retention days should be "90"

  Scenario: Canonical face match event is emitted with stable source and confidence
    Given a face match for person "sel" in room "office" from camera "cam_hall_front"
    And face_match_confidence "0.84"
    When the match is normalized
    Then the match event source should be "face"
    And the entity class should be "human"
    And the event should keep person_id "sel"
    And the event should keep room "office"
    And the event should keep camera "cam_hall_front"
    And the face_match_confidence should be "0.84"
