Feature: MQTT presence bridge

  Scenario: Bridge normalizes source and room aliases
    Given a raw presence event from "mwave" for room "room alpha"
    When the bridge normalizes the event
    Then the canonical source should be "mmwave"
    And the canonical room should be "room_alpha"
    And the canonical topic should be "ha/presence/event"

  Scenario: Bridge slugifies backyard labels to canonical room ids
    Given a raw presence event from "motion" for room "zone - beta"
    When the bridge normalizes the event
    Then the canonical source should be "motion"
    And the canonical room should be "zone_beta"
    And the canonical topic should be "ha/presence/event"

  Scenario: Bridge publishes only allowlisted canonical fields with opaque identity refs
    Given a raw presence event with schema fields, raw identifiers, and unexpected debug metadata
    When the bridge normalizes the event
    Then the canonical topic should be "ha/presence/event"
    And the canonical event should keep only documented contract fields
    And the canonical event should replace raw resident, tracker, and plate identifiers with opaque refs

  Scenario: Bridge sends invalid payloads to dead letter topic
    Given a raw presence event missing "event_id"
    When the bridge validates the event
    Then the bridge should route the event to "ha/presence/event/dlq"
    And the dead letter record should include validation errors
    And the dead letter payload should omit unexpected raw upstream fields
    And the dead letter payload should replace raw resident, tracker, and plate identifiers with opaque refs

  Scenario: Bridge re-keys caller-supplied event ids that embed raw identifiers
    Given a raw presence event with event_id "resident.sam|trk-999|XYZ123"
    When the bridge normalizes the event
    Then the canonical topic should be "ha/presence/event"
    And the canonical event should replace the supplied event_id with an opaque identifier
