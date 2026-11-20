#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-merge PR based on consensus results.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def run_cmd(cmd: List[str], cwd: Path = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def check_consensus(consensus_file: Path) -> Dict:
    """Load and validate consensus results."""
    with open(consensus_file) as f:
        consensus = json.load(f)

    # Check criteria for auto-merge
    checks = {
        "quorum_reached": consensus.get("quorum_reached", False),
        "decision_approve": consensus.get("decision") == "approve",
        "confidence_threshold": consensus.get("confidence", 0) >= 0.8,
        "no_vetoes": not any(
            v.get("decision") == "reject" and v.get("weight", 0) > 0.3
            for v in consensus.get("votes", [])
        )
    }

    all_passed = all(checks.values())
    return {"checks": checks, "all_passed": all_passed, "consensus": consensus}


def main():
    parser = argparse.ArgumentParser(description="Auto-merge PR based on consensus")
    parser.add_argument("--pr", required=True, help="PR number")
    parser.add_argument("--consensus", required=True, type=Path, help="Consensus JSON file")
    parser.add_argument("--base", default="main", help="Base branch")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="Repo path")
    parser.add_argument("--method", choices=["squash", "merge", "rebase"], default="squash")
    args = parser.parse_args()

    repo_path = args.repo.resolve()

    # Check consensus
    result = check_consensus(args.consensus)

    print("🔍 Consensus Checks:")
    for check, passed in result["checks"].items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")

    if not result["all_passed"]:
        print("\n❌ Auto-merge criteria not met")
        sys.exit(1)

    print("\n✅ All checks passed — proceeding with auto-merge")

    # Merge PR
    cmd = ["gh", "pr", "merge", args.pr, f"--{args.method}", "--delete-branch"]
    result = subprocess.run(cmd, cwd=args.repo, capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ PR merged successfully")
        print(result.stdout)
    else:
        print("❌ Merge failed")
        print(result.stderr)
        sys.exit(1)


if __name__ == "__main__":
    from typing import List, Dict
    main()