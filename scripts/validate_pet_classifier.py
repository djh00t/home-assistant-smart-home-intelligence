#!/usr/bin/env python3
"""Validate the pet detection classifier slice."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FILES = [
    ROOT / "config/contracts/pet_detection_classifier.yaml",
    ROOT / "docs/contracts/pet-detection-classifier.md",
    ROOT / "src/smart_home_presence_intelligence/pet_classifier.py",
]


def validate_files_exist() -> None:
    missing = [str(path.relative_to(ROOT)) for path in FILES if not path.exists()]
    if missing:
        print("Missing pet classifier files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_contract_text() -> None:
    text = (ROOT / "config/contracts/pet_detection_classifier.yaml").read_text(encoding="utf-8")
    for needle in (
        "cat",
        "dog",
        "pet",
        "canonical_source: frigate",
        "canonical_entity_class: pet",
        "preserve_room_context: true",
        "preserve_confidence: true",
        "pet_only_affects_pet_occupancy: true",
        "person_targeted_automations: false",
    ):
        if needle not in text:
            raise SystemExit(f"pet_detection_classifier.yaml missing {needle}")


def validate_module_behavior() -> None:
    sys.path.insert(0, str(ROOT / "src"))
    from smart_home_presence_intelligence.pet_classifier import build_pet_presence_event, normalize_pet_detection  # noqa: E501, WPS433

    detection = {
        "label": "cat",
        "room": "kitchen",
        "confidence": 0.87,
        "source": "frigate",
    }
    normalized = normalize_pet_detection(detection)
    if normalized["label"] != "cat" or normalized["room"] != "kitchen":
        raise SystemExit("pet detection normalization failed")

    event = build_pet_presence_event(detection)
    if event["entity_class"] != "pet" or event["room"] != "kitchen":
        raise SystemExit("pet presence event build failed")
    if event["source"] != "frigate":
        raise SystemExit("pet presence event should preserve the frigate source")
    if event["confidence"] != 0.87:
        raise SystemExit("pet confidence should be preserved")
    if "person_id" in event:
        raise SystemExit("pet events must not set person_id")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_pet_classifier.py [check|quality-gates]")
        return 2

    validate_files_exist()
    validate_contract_text()
    validate_module_behavior()

    print(
        "Pet classifier check passed"
        if sys.argv[1] == "check"
        else "Pet classifier quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
