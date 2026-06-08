Feature: Security and retention jobs

  Scenario: Retention audit flags expired records for dry-run cleanup
    Given retention artifacts include "event_records" at 100 days and "face_plate_audit" at 91 days
    And retention artifacts include "room_state_history" at 60 days
    When the retention audit report is built
    Then cleanup dry-run should be required
    And cleanup candidates should include "event_records" and "face_plate_audit"
    And retained records should include "room_state_history"

  Scenario: Retention audit keeps younger artifacts retained
    Given retention artifacts include "foreign_plate_person_alerts" at 30 days
    When the retention audit report is built
    Then retained records should include "foreign_plate_person_alerts"
    And cleanup candidates should be empty
