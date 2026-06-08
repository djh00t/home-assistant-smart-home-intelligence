Feature: Foreign identity queue for driveway review

  Scenario: Foreign identity snapshot is queued for review
    Given a driveway snapshot with room "driveway", camera "frigate_driveway", plate "ab c-12", and identity_status "foreign"
    And face match confidence is 0.45
    When the foreign identity queue record is built
    Then the queue should be created
    And the queue should preserve room "driveway"
    And the queue should preserve camera "frigate_driveway"
    And the queue should preserve plate "ABC12"
    And the queue should report review status "queued"

  Scenario: Recognized identity snapshot is not queued
    Given a driveway snapshot with room "driveway", camera "frigate_driveway", person "Sel", and face_match_confidence 0.86
    And identity_status is "known"
    When the foreign identity queue record is built
    Then no queue record should be created
