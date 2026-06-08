Feature: Non-home zone queue for review planning

  Scenario: External-zone snapshot is queued for review
    Given a non-home snapshot with room "driveway", camera "frigate_driveway", plate "ab c-12", and source "frigate"
    And direction is "enter" and identity_status "foreign"
    When the non-home zone queue record is built
    Then the queue should be created
    And the queue should preserve room "driveway"
    And the queue should preserve camera "frigate_driveway"
    And the queue should preserve source evidence "frigate"
    And the queue should report review status "queued"

  Scenario: Interior room snapshot is not queued
    Given a home snapshot with room "hall", camera "hall_cam", and person "Sel"
    When the non-home zone queue record is built
    Then no queue record should be created
