Feature: Non-home zone queue for review planning

  Scenario: External-zone snapshot is queued for review
    Given a non-home snapshot with room "zone_alpha", camera "frigate_zone_alpha", plate "ab c-12", person "sel", and source "frigate"
    And direction is "enter" and identity_status "foreign"
    When the non-home zone queue record is built
    Then the queue should be created
    And the queue should preserve room "zone_alpha"
    And the queue should preserve camera "frigate_zone_alpha"
    And the queue should preserve source evidence "frigate"
    And the queue evidence should store only non-linkable plate and person presence flags
    And the queue id should not expose raw plate or person evidence
    And the queue should report review status "queued"

  Scenario: Interior room snapshot is not queued
    Given a home snapshot with room "room_delta", camera "room_delta_cam", and person "Sel"
    When the non-home zone queue record is built
    Then no queue record should be created
