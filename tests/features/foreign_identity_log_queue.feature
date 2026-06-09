Feature: Foreign identity queue for zone_alpha review

  Scenario: Foreign identity snapshot is queued for review
    Given a zone_alpha snapshot with room "zone_alpha", camera "frigate_zone_alpha", plate "ab c-12", and identity_status "foreign"
    And face match confidence is 0.45
    When the foreign identity queue record is built
    Then the queue should be created
    And the queue id should be opaque and deterministic
    And the queue should preserve room "zone_alpha"
    And the queue should preserve camera "frigate_zone_alpha"
    And the queue identity should avoid raw plate or person values
    And the queue should report review status "queued"

  Scenario: Recognized identity snapshot is not queued
    Given a zone_alpha snapshot with room "zone_alpha", camera "frigate_zone_alpha", person "Sel", and face_match_confidence 0.86
    And identity_status is "known"
    When the foreign identity queue record is built
    Then no queue record should be created
