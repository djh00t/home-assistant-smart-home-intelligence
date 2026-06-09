Feature: HACS release and validation
  Scenario: A release is aligned across package metadata and git tags
    Given the repository VERSION file is updated for a release
    Then the changelog should include the matching release entry
    And the integration manifest version should match the repository version
    And the release tag should point at the published commit

  Scenario: The release contract preserves downgradeability
    Given the current release has a previous semver tag available
    Then HACS should be able to downgrade to the previous release
    And the integration should remain removable after a downgrade

  Scenario: Validation rejects release drift
    Given the manifest, changelog, and VERSION file are out of sync
    Then the release validation should fail before publishing
