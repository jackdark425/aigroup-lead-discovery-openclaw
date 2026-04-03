#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FILES = [
    ".claude-plugin/plugin.json",
    ".mcp.json",
    "README.md",
    "LICENSE",
    "NOTICE",
]

FORBIDDEN_RELEASE_PATHS = [
    "upstream",
    "packs",
    "bundles",
    ".git",
    "node_modules",
]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as exc:  # pragma: no cover
        fail(f"failed to parse JSON at {path}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate an OpenClaw Claude bundle")
    parser.add_argument("root", nargs="?", default=".", help="bundle root")
    parser.add_argument("--strict-release", action="store_true")
    parser.add_argument(
        "--expected-name",
        help="expected plugin name override (useful for copied release directories)",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()

    for relative_path in REQUIRED_FILES:
        path = root / relative_path
        if not path.exists():
            fail(f"missing required file: {relative_path}")

    manifest = load_json(root / ".claude-plugin" / "plugin.json")
    expected_name = args.expected_name or root.name
    if manifest.get("name") != expected_name:
        fail(
            f"plugin manifest name mismatch: expected {expected_name}, got {manifest.get('name')}"
        )
    if not manifest.get("version"):
        fail("plugin manifest version is empty")

    package_json = root / "package.json"
    if package_json.exists():
        package = load_json(package_json)
        if package.get("version") != manifest.get("version"):
            fail(
                "package.json version does not match plugin manifest version: "
                f"{package.get('version')} != {manifest.get('version')}"
            )

    skills_dir = root / "skills"
    if not skills_dir.is_dir():
        fail("missing skills/ directory")

    skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir())
    if not skill_dirs:
        fail("skills/ directory is empty")

    for skill_dir in skill_dirs:
        if not (skill_dir / "SKILL.md").is_file():
            fail(f"missing SKILL.md for skill: {skill_dir.name}")

    load_json(root / ".mcp.json")

    if args.strict_release:
        for relative_path in FORBIDDEN_RELEASE_PATHS:
            if (root / relative_path).exists():
                fail(f"release bundle contains forbidden path: {relative_path}")

    print(f"OK: bundle validated at {root}")


if __name__ == "__main__":
    main()
