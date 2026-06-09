#!/usr/bin/env python3
"""Validate the HACS release metadata and downgrade path."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
INTEGRATION_ROOT = ROOT / "custom_components" / "smart_home_presence_intelligence"


def read_version() -> str:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not version:
        raise SystemExit("VERSION is empty")
    return version


def validate_manifest(version: str) -> None:
    data = json.loads((INTEGRATION_ROOT / "manifest.json").read_text(encoding="utf-8"))
    if data.get("version") != version:
        raise SystemExit("manifest version does not match VERSION")


def validate_changelog(version: str) -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    heading = f"## [{version}]"
    if heading not in changelog:
        raise SystemExit(f"CHANGELOG.md missing release entry for {version}")


def validate_git_tag(version: str) -> None:
    tag = f"v{version}"
    result = subprocess.run(
        ["git", "rev-parse", "--verify", f"refs/tags/{tag}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if not result.stdout.strip():
        raise SystemExit(f"release tag {tag} is missing")


def validate_downgrade_path(version: str) -> None:
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    current_heading = f"## [{version}]"
    previous_entries = [
        line.strip()
        for line in changelog.splitlines()
        if line.startswith("## [") and current_heading not in line
    ]
    if not previous_entries:
        raise SystemExit("CHANGELOG.md does not include a previous release entry")


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_hacs_release.py [check|quality-gates]")
        return 2

    version = read_version()
    validate_manifest(version)
    validate_changelog(version)
    validate_git_tag(version)
    validate_downgrade_path(version)

    print(
        "HACS release check passed"
        if sys.argv[1] == "check"
        else "HACS release quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
