#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Semantic versioning and git tagging for releases.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional


def run_cmd(cmd: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def get_latest_tag(repo_path: Path) -> Optional[str]:
    """Get latest git tag."""
    result = run_cmd(["git", "describe", "--tags", "--abbrev=0"], repo_path)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def parse_version(tag: str) -> tuple:
    """Parse semantic version tag."""
    match = re.match(r"v?(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$", tag)
    if match:
        return tuple(map(int, match.groups()))
    return (0, 0, 0)


def bump_version(current: tuple, level: str) -> tuple:
    """Bump version by level."""
    major, minor, patch = current
    if level == "major":
        return (major + 1, 0, 0)
    elif level == "minor":
        return (major, minor + 1, 0)
    elif level == "patch":
        return (major, minor, patch + 1)
    return current


def generate_changelog(repo_path: Path, from_tag: str, to_tag: str) -> str:
    """Generate changelog from git log."""
    result = run_cmd(
        ["git", "log", f"{from_tag}..HEAD", "--pretty=format:- %s (%an)", "--no-merges"],
        repo_path
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return "- No changes"


def main():
    parser = argparse.ArgumentParser(description="Create semantic version tag")
    parser.add_argument("--level", choices=["major", "minor", "patch"], default="patch", help="Version bump level")
    parser.add_argument("--version", help="Explicit version (e.g., 2.3.0)")
    parser.add_argument("--message", help="Tag message")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repo path")
    parser.add_argument("--push", action="store_true", help="Push tag to remote")
    parser.add_argument("--changelog", type=Path, help="Output changelog file")
    parser.add_argument("--consensus", type=Path, help="Consensus JSON file for version decision")
    args = parser.parse_args()

    repo_path = args.repo.resolve()

    # Determine version
    if args.version:
        version = args.version.lstrip("v")
    else:
        latest = get_latest_tag(repo_path)
        if latest:
            current = parse_version(latest)
        else:
            current = (0, 0, 0)

        # Override with consensus if provided
        if args.consensus and args.consensus.exists():
            with open(args.consensus) as f:
                consensus = json.load(f)
            # Consensus can suggest version bump
            if consensus.get("version_bump"):
                level = consensus["version_bump"]
            else:
                level = args.level
        else:
            level = args.level

        new_version = bump_version(current, level)
        version = f"{new_version[0]}.{new_version[1]}.{new_version[2]}"

    tag = f"v{version}"
    message = args.message or f"Release {tag}"

    print(f"🏷️  Creating tag: {tag}")
    print(f"   Message: {message}")

    # Create annotated tag
    result = run_cmd(["git", "tag", "-a", tag, "-m", message], args.repo)
    if result.returncode != 0:
        print(f"❌ Failed to create tag: {result.stderr}")
        sys.exit(1)

    print(f"✅ Tag created: {tag}")

    # Generate changelog
    from_tag = get_latest_tag(repo_path) or ""
    changelog = generate_changelog(args.repo, from_tag, tag)

    if args.changelog:
        args.changelog.write_text(f"# {tag}\n\n{changelog}\n")
        print(f"📄 Changelog written to {args.changelog}")

    # Push tag
    if args.push:
        result = run_cmd(["git", "push", "origin", tag], args.repo)
        if result.returncode == 0:
            print(f"🚀 Tag pushed to origin")
        else:
            print(f"⚠️  Failed to push tag: {result.stderr}")

    # Output for CI/CD
    output = {
        "tag": tag,
        "version": version,
        "changelog": changelog
    }
    print(json.dumps(output))


if __name__ == "__main__":
    from typing import List
    main()