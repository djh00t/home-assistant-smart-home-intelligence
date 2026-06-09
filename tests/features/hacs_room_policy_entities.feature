Feature: HACS room policy entities
  Scenario: House mode reflects tracked occupancy
    Given the runtime has one tracked human in the lounge room
    Then the house mode sensor should be "occupied"

  Scenario: Room policy sensors expose white scenes and color sync state
    Given the runtime has routed occupancy events for bedroom spare
    Then the bedroom spare white scene sensor should be available
    And the bedroom spare color sync sensor should reflect the room capability

  Scenario: Room policy sensors restore from runtime state
    Given the runtime has a restored policy snapshot
    Then the bedroom spare house mode sensor should be "occupied"

