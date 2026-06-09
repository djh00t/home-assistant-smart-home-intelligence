Feature: HACS package management
  Scenario: The repository can be installed as a HACS custom integration
    Given the repository root contains a HACS manifest
    And the integration lives under custom_components/smart_home_presence_intelligence
    Then the package should be installable as a single HACS integration

  Scenario: The integration version is aligned across packaging files
    Given the repository VERSION file is updated
    Then the integration manifest version should match the repository version

  Scenario: The integration supports upgrade and removal via HACS
    Given the integration is installed through HACS
    When a newer release is published
    Then HACS should offer an upgrade path
    And the integration should remain removable from the HACS UI

