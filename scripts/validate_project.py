#!/usr/bin/env python3
"""Validate the project scaffold for this repository."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ROOT = ROOT / "src" / "smart_home_presence_intelligence"
REQUIRED_FILES = [
    PACKAGE_ROOT / "__init__.py",
    ROOT / "VERSION",
    ROOT / "CHANGELOG.md",
    ROOT / "LICENSE",
    ROOT / "SECURITY.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "CODE_OF_CONDUCT.md",
    ROOT / "SUPPORT.md",
    ROOT / ".editorconfig",
    ROOT / ".gitattributes",
    ROOT / "hacs.json",
    ROOT / "brand" / "icon.png",
    ROOT / ".github" / "CODEOWNERS",
    ROOT / ".github" / "pull_request_template.md",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "bug_report.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "feature_request.yml",
    ROOT / ".github" / "ISSUE_TEMPLATE" / "config.yml",
    ROOT / "custom_components" / "smart_home_presence_intelligence" / "manifest.json",
]
REQUIRED_GITIGNORE_ENTRIES = [
    ".venv/",
    "dist/",
    "__pycache__/",
]


def validate_required_files() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]
    if missing:
        print("Missing required files:")
        for path in missing:
            print(path)
        raise SystemExit(1)


def validate_gitignore() -> None:
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        print(".gitignore is missing")
        raise SystemExit(1)

    lines = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    missing = [entry for entry in REQUIRED_GITIGNORE_ENTRIES if entry not in lines]
    if missing:
        print("Missing .gitignore entries:")
        for entry in missing:
            print(entry)
        raise SystemExit(1)


def validate_version_file() -> None:
    version_file = ROOT / "VERSION"
    if version_file.is_symlink():
        print("VERSION must not be a symlink")
        raise SystemExit(1)
    version = version_file.read_text(encoding="utf-8").strip()
    if not version:
        print("VERSION is empty")
        raise SystemExit(1)
    if version.count(".") != 2 or not all(part.isdigit() for part in version.split(".")):
        print("VERSION is not semver")
        raise SystemExit(1)


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in {"check", "quality-gates"}:
        print("Usage: validate_project.py [check|quality-gates]")
        return 2

    validate_required_files()
    validate_gitignore()
    validate_version_file()

    print(
        "Project scaffold check passed"
        if sys.argv[1] == "check"
        else "Project scaffold quality gates passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
