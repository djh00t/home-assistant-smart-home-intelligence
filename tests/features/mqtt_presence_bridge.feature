Feature: MQTT presence bridge

  Scenario: Bridge normalizes source and room aliases
    Given a raw presence event from "mwave" for room "bedroom_master"
    When the bridge normalizes the event
    Then the canonical source should be "mmwave"
    And the canonical room should be "bedroom_master"
    And the canonical topic should be "ha/presence/event"

  Scenario: Bridge slugifies backyard labels to canonical room ids
    Given a raw presence event from "motion" for room "backyard - shed"
    When the bridge normalizes the event
    Then the canonical source should be "motion"
    And the canonical room should be "backyard_shed"
    And the canonical topic should be "ha/presence/event"

  Scenario: Bridge sends invalid payloads to dead letter topic
    Given a raw presence event missing "event_id"
    When the bridge validates the event
    Then the bridge should route the event to "ha/presence/event/dlq"
    And the dead letter record should include validation errors
