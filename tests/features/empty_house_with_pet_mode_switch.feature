Feature: Empty house with pet mode switch

  Scenario: Pet-only occupancy switches the house to pet mode
    Given no humans are present and at least one pet is present
    When the house mode is evaluated
    Then the house mode should be "pet_mode"
    And pathway lighting may remain governed by pet policy

  Scenario: Human presence overrides pet mode
    Given a pet-only house mode is active
    And a human enters the home
    When the house mode is evaluated
    Then the house mode should be "occupied"
    And pet mode should be cleared
