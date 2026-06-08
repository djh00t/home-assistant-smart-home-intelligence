---
title: Smart Home Presence, Lighting, and Personalization Spec
owner: Home Assistant Program
created: 2026-06-07
version: 0.1.0
---

# Smart Home Presence, Lighting, and Personalization

## 1) Goal

Build a local-first home automation stack where Home Assistant is the orchestration brain and Apple Home is a control surface, with:

- multi-room color-capable and white-only light matching
- room occupancy detection with resettable dwell timers
- mmWave in-bed detection and bed-protective light behavior
- person, pet, and vehicle-aware room presence
- car arrival/departure and foreign plate/face logging
- local face/object recognition, with optional external API integrations later

Retention requirement: keep records, metadata, and media (images where needed) for at least 90 days.

## 2) Scope

In scope:

- Home Assistant automations/packages and supporting scripts
- Jetson Xavier ML stack (Frigate + optional face/plate service + MQTT bridge)
- Event and scene policy in HA
- Dashboard for mode/room state and overrides
- BDD scenarios for every behavior change

Out of scope (for this stage):

- rewriting vendor camera apps
- full custom integration development for every brand
- automatic cloud backups of face/plate records

## 3) Source-of-truth model

Home Assistant remains source of home control state. Vendor apps remain for manual control/monitoring only.

Priority input sources:

1. Device/person trackers (mobile app, BLE, geofencing)
2. mmWave radar state
3. Motion/PIR
4. Frigate track + local zones
5. Face/object inferences from Jetson
6. Number plate events from local ANPR service

People, pets, and vehicle events are fanned in through a canonical event schema so automations are source-agnostic.

## 4) Canonical event contract

Publish all detection events on MQTT topic prefix `ha/presence/event`.

Payload schema:

```json
{
  "event_id": "uuid",
  "source": "frigate|mwave|motion|face|anpr|tracker",
  "type": "enter|leave|stay|state_change|confidence",
  "room": "kitchen|bedroom_master|... ",
  "camera": "cam_front_drive|...",
  "entity_class": "human|pet|vehicle",
  "person_id": "sel|sam|unknown",
  "confidence": 0.93,
  "track_id": "camera-track-id-or-empty",
  "vehicle": {
    "plate": "ABC123",
    "plate_confidence": 0.88,
    "vehicle_type": "car|unknown"
  },
  "context": {
    "with_pram": true,
    "with_face_match": true,
    "is_owner_plate": true,
    "lighting_blocked": false
  },
  "ts": "2026-06-07T12:00:00+10:00"
}
```

## 5) Room occupancy model

Per room, compute:

- `humans_present`: count
- `pets_present`: count
- `occupancy_mode`: `empty|humans_only|pets_only|mixed`
- `occupied_humans`: set/list of best-estimate occupants
- `room_mode`: `awake|sleeping|bed_motion_only`

Rules:

- mmWave has highest weight for `bed_motion_only` and `sleeping`
- Frigate tracks provide motion and zone continuity but are never sole identity proof
- Face match upgrades identity confidence when aligned with mmWave/motion in same room within 30 seconds
- Pet detections change `pets_present` only and never trigger person-targeted automations directly

## 6) Lighting model

Per room define:

- `light_groups.white_lights` and `light_groups.color_lights`
- `dwell_on_seconds` and `dwell_dim_seconds`

Behavior:

- On occupancy entry:
  - Turn on room defaults.
  - Apply white lights via circadian scene and preserve hue/temperature policy.
  - If user request is color scene, sync matching-color lights only among color-capable groups.
- On repeated occupancy activity:
  - reset dwell timers.
  - keep dim level for active states.
- On dwell expiry:
  - first step: dim to off/low based on `room_mode`.
  - second step: full off after longer inactivity.

Global rules:

- Never full-brighten while `bed_motion_only`.
- Never auto-on in explicit manual override window for that room.

## 7) Personalization model

Each person can map to:

- preferred desk lights
- climate preference profile
- wake/no-wake policies
- safe zones for no-lighting at night

Trigger example:

- if `occupied_humans` includes `sel` and room is `bedroom_spare`, turn on desk light profile for Sel on occupancy entry.

## 8) Vehicle and outside-context logic

- A person is considered to be driving only when face/track/person evidence and ANPR context align.
- Pram logic:
  - if `with_pram=true` and no matching vehicle context in last 90 seconds, classify as walk mode.
- Car logic:
  - plate + direction + vehicle zone + person linkage => arrival/departure event
  - no single-source action on ANPR alone

Actions:

- `vehicle_arrival` and `vehicle_departure` events are used for:
  - garage door / lock workflows
  - occupancy mode adjustments
  - event logging

## 9) Logging and retention

Retention target: minimum 90 days for all records and media required by automations.

Retention tiers:

- high: person/room/vehicle state events
- medium: image crops, face descriptors (subject to storage policy)
- low: raw recordings (can be shorter depending on camera retention rules)

Policy:

- At least 90 days: event records, face/plate linkage logs, person-vehicle logs.
- Add cleanup jobs keyed by source and age.
- Maintain immutable foreign plate/person alerts for review, with retention extension if storage allows.
- Store only consented/encrypted media outside volatile cache.

## 10) Safety / constraints

- No action that unlocks/opens anything uses camera-only identity.
- Every high-impact action requires:
  - confidence threshold
  - two-signal validation
  - per-room manual override and cooldown guard.
- Provide kill switches for:
  - ML disabled
  - face recognition disabled
  - logging disabled for privacy windows

## 11) KPIs and acceptance criteria

- Room occupancy state updates within 2 seconds of source event in normal local network.
- Dwell resets successfully on each motion event.
- 95% of repeated room entry scenarios recover expected light state in < 5 seconds.
- 90-day retention verified for logs and media metadata.
- Zero person-specific actions fired from pet-only occupancy.

## 12) Dependencies and blockers

- Entity inventories for all rooms and lights must be complete before room policy rules.
- mmWave devices with per-room stable entity names required.
- Camera feed compatibility for Frigate zones.
- Jetson services deployed and reachable over MQTT.
