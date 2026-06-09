Feature: Color sync for color lights

  Scenario: Bedroom spare color scene targets only color-capable lights
    Given the room_gamma room supports color lighting
    When a color scene is requested for the room_gamma
    Then the room_gamma color groups should be selected
    And white groups should remain on the white-light policy

  Scenario: Lounge room color scene skips white-only lights
    Given the room_delta room is white-only
    When a color scene is requested for the room_delta
    Then no color groups should be selected
    And the white-light policy should remain unchanged
