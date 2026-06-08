Feature: Color sync for color lights

  Scenario: Office color scene targets only color-capable lights
    Given the office room supports color lighting
    When a color scene is requested for the office
    Then the office color groups should be selected
    And white groups should remain on the white-light policy

  Scenario: Hall color scene skips white-only lights
    Given the hall room is white-only
    When a color scene is requested for the hall
    Then no color groups should be selected
    And the white-light policy should remain unchanged
