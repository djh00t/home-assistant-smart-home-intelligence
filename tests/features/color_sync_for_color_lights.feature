Feature: Color sync for color lights

  Scenario: Bedroom spare color scene targets only color-capable lights
    Given the bedroom_spare room supports color lighting
    When a color scene is requested for the bedroom_spare
    Then the bedroom_spare color groups should be selected
    And white groups should remain on the white-light policy

  Scenario: Lounge room color scene skips white-only lights
    Given the lounge_room room is white-only
    When a color scene is requested for the lounge_room
    Then no color groups should be selected
    And the white-light policy should remain unchanged
