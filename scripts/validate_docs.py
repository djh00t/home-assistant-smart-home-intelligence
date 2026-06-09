#!/usr/bin/env python3
"""Validate the documentation bundle for this repository."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    ROOT / "README.md",
    ROOT / "docs/specs/2026-06-07-smart-home-intelligence-spec.md",
    ROOT / "docs/roadmap/roadmap.md",
    ROOT / "docs/plans/implementation-plan.md",
    ROOT / "docs/tasks/task_backlog.md",
    ROOT / "tests/features/smart_home_presence.feature",
    ROOT / "tests/features/hacs_package_management.feature",
    ROOT / "tests/features/hacs_integration_entities.feature",
    ROOT / "tests/features/hacs_room_policy_entities.feature",
    ROOT / "tests/features/hacs_release_and_validation.feature",
]


def validate_required_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        print("Missing required files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_feature_file() -> None:
    feature = ROOT / "tests/features/smart_home_presence.feature"
    lines = feature.read_text(encoding="utf-8").splitlines()

    if not any(line.startswith("Feature:") for line in lines):
        print(f"{feature.relative_to(ROOT)}: missing Feature header")
        raise SystemExit(1)

    for index, line in enumerate(lines[:-1]):
        if line.startswith("  Scenario:") and lines[index + 1].startswith("  Scenario:"):
            print(
                f"{feature.relative_to(ROOT)}: malformed scenario header near line {index + 2}"
            )
            raise SystemExit(1)


def validate_docs_are_non_empty() -> None:
    empty = [
        str(path.relative_to(ROOT))
        for path in ROOT.glob("docs/**/*.md")
        if path.is_file() and not path.read_text(encoding="utf-8").strip()
    ]

    if empty:
        raise SystemExit("Empty markdown files:\n" + "\n".join(empty))


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_docs.py [check|quality-gates]")
        return 2

    validate_required_files()
    validate_feature_file()

    if sys.argv[1] == "quality-gates":
        validate_docs_are_non_empty()

    print(
        "Documentation bundle check passed"
        if sys.argv[1] == "check"
        else "Documentation quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
