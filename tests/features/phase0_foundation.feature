Feature: Phase 0 foundation

  Scenario: Repository scaffold exists for phase 0
    Given the repository is in phase 0
    When the top-level tree is inspected
    Then the repository should include README.md and Makefile
    And the tests and scripts directories should be present

  Scenario: Config artifacts are discoverable for phase 0
    Given phase 0 config artifacts are needed
    When the configuration surface is inspected
    Then a config directory should exist for environment and runtime settings
    And the config artifacts should be easy to discover from the repository root

  Scenario: Room capability inventory is defined for phase 0
    Given phase 0 room capability rules are needed
    When the capability catalog is inspected
    Then a room capability inventory should exist for every phase 0 room and zone
    And each capability entry should state lighting support and occupancy source order

  Scenario: Retention policy is defined for phase 0
    Given phase 0 retention rules are needed
    When the retention baseline is inspected
    Then the repository should define a 90-day retention policy for presence evidence
    And short-lived operational data should have an explicit cleanup boundary

  Scenario: Presence-topic contract exists for phase 0
    Given the presence topic integration is needed
    When contract files are inspected
    Then a presence-topic contract should exist for downstream consumers
    And the contract should describe the observable presence event surface
