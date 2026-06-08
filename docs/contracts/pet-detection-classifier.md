# Pet Detection Classifier

This document defines the first pet-normalization slice for phase 0.

## Scope

- Normalize raw pet detections into canonical pet presence events.
- Preserve room context and confidence when a pet detection is classified.
- Keep pet detections limited to pet occupancy and house-mode routing.
- Prevent pet-only signals from directly triggering person-targeted automations.
- Canonical pet events preserve the upstream Frigate source as `source: frigate`.

## Policy

- `cat`, `dog`, and `pet` are the first accepted raw labels.
- Canonical pet events use `entity_class: pet`.
- Canonical pet events use `source: frigate`.
- Room and confidence values pass through unchanged when present.
- Pet detections never imply a person identity or person action.

## Backlog Link

- `TASK-010 pet_detection_classifier`
