#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Optimizer — Compresses design reviews, token diffs, architecture decisions
into compact handoff briefs for agent-to-agent delegation.
Implements progressive disclosure levels (L1-L4) with relevance scoring.
"""

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple


@dataclass
class HandoffBrief:
    """Compact context handoff for agent delegation."""
    summary: str
    critical_findings: List[Dict]
    major_findings: List[Dict]
    token_changes: Dict[str, List[Dict]]
    decisions: List[Dict]
    next_steps: List[str]
    metadata: Dict
    token_estimate: int


class RelevanceScorer:
    """Scores content relevance for progressive disclosure."""

    CRITICAL_KEYWORDS = {
        "security": ["sql injection", "xss", "csrf", "authentication", "authorization", "secret", "token", "credential", "vulnerability", "exploit", "owasp"],
        "architecture": ["circular dependency", "layer violation", "coupling", "cohesion", "boundary", "module", "service", "hexagonal", "clean architecture"],
        "performance": ["n+1", "memory leak", "cache stampede", "latency", "throughput", "budget", "regression", "bottleneck", "profiling"],
        "data": ["migration", "schema", "data loss", "consistency", "transaction", "integrity", "backup"],
        "accessibility": ["wcag", "contrast", "keyboard", "screen reader", "aria", "focus", "alt text"],
    }

    def __init__(self):
        self.keyword_weights = {cat: 1.0 for cat in self.CRITICAL_KEYWORDS}

    def score(self, text: str, category: str = None) -> float:
        """Score 0-1 for relevance."""
        text_lower = text.lower()
        if category and category in self.CRITICAL_KEYWORDS:
            keywords = self.CRITICAL_KEYWORDS[category]
        else:
            keywords = [kw for kws in self.CRITICAL_KEYWORDS.values() for kw in kws]

        matches = sum(1 for kw in keywords if kw in text_lower)
        return min(1.0, matches * 0.15)


class ContextCompressor:
    def __init__(self, token_budget: int = 3000):
        self.token_budget = token_budget
        self.scorer = RelevanceScorer()
        self.avg_chars_per_token = 4  # rough estimate

    def load_review_report(self, path: Path) -> Dict:
        """Parse markdown review report into structured data."""
        content = path.read_text(encoding="utf-8")
        return self._parse_review(content)

    def _parse_review(self, content: str) -> Dict:
        """Extract sections from review markdown."""
        sections = {
            "summary": "",
            "critical": [],
            "major": [],
            "minor": [],
            "token_diff": {"added": [], "modified": [], "removed": []},
            "decisions": [],
            "next_steps": [],
        }

        current_section = None
        current_finding = {}

        for line in content.split("\n"):
            # Section headers
            if line.startswith("## Summary"):
                current_section = "summary"
                continue
            elif line.startswith("## Critical Findings"):
                current_section = "critical"
                continue
            elif line.startswith("## Major Findings"):
                current_section = "major"
                continue
            elif line.startswith("## Minor Findings"):
                current_section = "minor"
                continue
            elif line.startswith("## Token Diff"):
                current_section = "token_diff"
                continue
            elif line.startswith("## Decisions"):
                current_section = "decisions"
                continue
            elif line.startswith("## Next Steps"):
                current_section = "next_steps"
                continue

            # Finding headers (### 1. Title)
            if line.startswith("### ") and current_section in ("critical", "major", "minor"):
                if current_finding:
                    sections[current_section].append(current_finding)
                current_finding = {"title": line[4:].strip(), "details": [], "file": "", "line": 0}
                # Extract file:line from title
                file_match = re.search(r"`([^`]+):(\d+)`", current_finding["title"])
                if file_match:
                    current_finding["file"] = file_match.group(1)
                    current_finding["line"] = int(file_match.group(2))
                continue

            # File:line in body
            if line.strip().startswith("**File**:"):
                file_match = re.search(r"\*\*File\*\*:\s*`([^`]+):(\d+)`", line)
                if file_match:
                    current_finding["file"] = file_match.group(1)
                    current_finding["line"] = int(file_match.group(2))
                continue

            # Fix suggestion
            if line.strip().startswith("**Fix**:"):
                current_finding["fix"] = line.replace("**Fix**:", "").strip()
                continue

            # Token diff
            if current_section == "token_diff":
                if line.startswith("### Added"):
                    current_finding = {"type": "added", "tokens": []}
                elif line.startswith("### Modified"):
                    current_finding = {"type": "modified", "tokens": []}
                elif line.startswith("### Removed"):
                    current_finding = {"type": "removed", "tokens": []}
                elif line.startswith("- ") and current_finding:
                    current_finding["tokens"].append(line[2:].strip())
                elif line == "" and current_finding and "tokens" in current_finding:
                    sections["token_diff"][current_finding["type"]].extend(current_finding["tokens"])
                    current_finding = {}
                continue

            # Decisions
            if current_section == "decisions" and line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "- ")):
                sections["decisions"].append(line.strip().lstrip("1234567890.- "))
                continue

            # Next steps
            if current_section == "next_steps" and line.strip().startswith(("1.", "2.", "3.", "4.", "5.", "- ")):
                sections["next_steps"].append(line.strip().lstrip("1234567890.- "))
                continue

            # Accumulate
            if current_section == "summary" and line.strip():
                sections["summary"] += line + " "
            elif current_finding and line.strip():
                current_finding["details"].append(line.strip())

        if current_finding:
            sections[current_section].append(current_finding)

        # Cleanup
        sections["summary"] = sections["summary"].strip()
        return sections

    def load_token_diff(self, old_path: Path, new_path: Path) -> Dict:
        """Compute diff between two token files (JSON or CSS)."""
        old_tokens = self._load_tokens(old_path)
        new_tokens = self._load_tokens(new_path)

        diff = {"added": [], "modified": [], "removed": []}
        all_keys = set(old_tokens.keys()) | set(new_tokens.keys())

        for key in sorted(all_keys):
            if key not in old_tokens:
                diff["added"].append({"token": key, "value": new_tokens[key]})
            elif key not in new_tokens:
                diff["removed"].append({"token": key, "value": old_tokens[key]})
            elif old_tokens[key] != new_tokens[key]:
                diff["modified"].append({"token": key, "old": old_tokens[key], "new": new_tokens[key]})

        return diff

    def _load_tokens(self, path: Path) -> Dict:
        """Load tokens from JSON or CSS file."""
        content = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            return json.loads(content)
        elif path.suffix == ".css":
            tokens = {}
            for match in re.finditer(r"--([\w-]+):\s*([^;]+);", content):
                tokens[match.group(1)] = match.group(2).strip()
            return tokens
        return {}

    def generate_handoff(
        self,
        review_data: Dict,
        token_diff: Dict = None,
        level: str = "L3",
        format: str = "markdown",
    ) -> HandoffBrief:
        """Generate compressed handoff brief at specified level."""

        # Score and filter findings
        critical = self._filter_findings(review_data.get("critical", []), threshold=0.5)
        major = self._filter_findings(review_data.get("major", []), threshold=0.3)
        minor = review_data.get("minor", [])

        # Build brief based on level
        if level == "L1":
            brief = self._build_l1(review_data, critical, token_diff)
        elif level == "L2":
            brief = self._build_l2(review_data, critical, major, token_diff)
        elif level == "L3":
            brief = self._build_l3(review_data, critical, major, token_diff)
        else:  # L4
            brief = self._build_l4(review_data, critical, major, minor, token_diff)

        brief.token_estimate = self._estimate_tokens(brief)
        return brief

    def _filter_findings(self, findings: List[Dict], threshold: float) -> List[Dict]:
        """Filter findings by relevance score."""
        scored = []
        for f in findings:
            text = f.get("title", "") + " " + " ".join(f.get("details", []))
            score = self.scorer.score(text)
            if score >= threshold:
                f["relevance_score"] = score
                scored.append(f)
        return sorted(scored, key=lambda x: x.get("relevance_score", 0), reverse=True)

    def _build_l1(self, review: Dict, critical: List, token_diff: Dict) -> HandoffBrief:
        """Executive summary only."""
        return HandoffBrief(
            summary=review.get("summary", "")[:500],
            critical_findings=[{"title": f["title"], "file": f.get("file", ""), "fix": f.get("fix", "")} for f in critical],
            major_findings=[],
            token_changes=token_diff or {},
            decisions=review.get("decisions", [])[:3],
            next_steps=review.get("next_steps", [])[:3],
            metadata={"level": "L1", "generated": datetime.now().isoformat()},
            token_estimate=0,
        )

    def _build_l2(self, review: Dict, critical: List, major: List, token_diff: Dict) -> HandoffBrief:
        """L1 + critical findings with file:line."""
        return HandoffBrief(
            summary=review.get("summary", "")[:800],
            critical_findings=[{"title": f["title"], "file": f.get("file", ""), "line": f.get("line", 0), "fix": f.get("fix", ""), "score": f.get("relevance_score", 0)} for f in critical],
            major_findings=[{"title": f["title"], "file": f.get("file", "")} for f in major[:5]],
            token_changes=token_diff or {},
            decisions=review.get("decisions", [])[:5],
            next_steps=review.get("next_steps", [])[:5],
            metadata={"level": "L2", "generated": datetime.now().isoformat()},
            token_estimate=0,
        )

    def _build_l3(self, review: Dict, critical: List, major: List, token_diff: Dict) -> HandoffBrief:
        """L2 + major findings summary + token diff."""
        return HandoffBrief(
            summary=review.get("summary", ""),
            critical_findings=[{"title": f["title"], "file": f.get("file", ""), "line": f.get("line", 0), "fix": f.get("fix", ""), "details": f.get("details", [])[:3], "score": f.get("relevance_score", 0)} for f in critical],
            major_findings=[{"title": f["title"], "file": f.get("file", ""), "fix": f.get("fix", ""), "score": f.get("relevance_score", 0)} for f in major],
            token_changes=token_diff or {},
            decisions=review.get("decisions", []),
            next_steps=review.get("next_steps", []),
            metadata={"level": "L3", "generated": datetime.now().isoformat()},
            token_estimate=0,
        )

    def _build_l4(self, review: Dict, critical: List, major: List, minor: List, token_diff: Dict) -> HandoffBrief:
        """Full report."""
        return HandoffBrief(
            summary=review.get("summary", ""),
            critical_findings=critical,
            major_findings=major,
            token_changes=token_diff or {},
            decisions=review.get("decisions", []),
            next_steps=review.get("next_steps", []),
            metadata={"level": "L4", "generated": datetime.now().isoformat(), "minor_count": len(minor)},
            token_estimate=0,
        )

    def _estimate_tokens(self, brief: HandoffBrief) -> int:
        """Estimate token count of brief."""
        text = json.dumps(asdict(brief))
        return len(text) // self.avg_chars_per_token

    def trim_to_budget(self, brief: HandoffBrief) -> HandoffBrief:
        """Trim brief to fit token budget by reducing detail."""
        if brief.token_estimate <= self.token_budget:
            return brief

        # Progressive trimming
        trimmed = brief
        while trimmed.token_estimate > self.token_budget:
            # Reduce critical finding details
            for f in trimmed.critical_findings:
                if "details" in f and len(f["details"]) > 1:
                    f["details"] = f["details"][:1]
            # Reduce major findings
            if len(trimmed.major_findings) > 5:
                trimmed.major_findings = trimmed.major_findings[:5]
            # Reduce decisions
            if len(trimmed.decisions) > 3:
                trimmed.decisions = trimmed.decisions[:3]
            # Reduce next steps
            if len(trimmed.next_steps) > 3:
                trimmed.next_steps = trimmed.next_steps[:3]

            trimmed.token_estimate = self._estimate_tokens(trimmed)

            if trimmed.token_estimate <= self.token_budget:
                break

        trimmed.metadata["trimmed"] = True
        return trimmed

    def export(self, brief: HandoffBrief, format: str = "markdown") -> str:
        """Export brief to specified format."""
        if format == "json":
            return json.dumps(asdict(brief), indent=2, default=str)

        lines = [
            "# Agent Handoff Brief",
            f"**Level**: {brief.metadata.get('level', 'L3')} | **Tokens**: ~{brief.token_estimate} | **Budget**: {self.token_budget}",
            f"**Generated**: {brief.metadata.get('generated', '')}",
            "",
            "## Summary",
            brief.summary or "(no summary)",
            "",
            "## Critical Findings",
        ]
        for f in brief.critical_findings:
            lines.append(f"- **{f['title']}**")
            if f.get("file"):
                lines.append(f"  - File: `{f['file']}`" + (f":{f['line']}" if f.get('line') else ""))
            if f.get("fix"):
                lines.append(f"  - Fix: {f['fix']}")
            if f.get("details"):
                for d in f["details"]:
                    lines.append(f"  - {d}")
            lines.append("")

        lines.append("## Major Findings")
        for f in brief.major_findings:
            lines.append(f"- **{f['title']}**")
            if f.get("file"):
                lines.append(f"  - File: `{f['file']}`")
            if f.get("fix"):
                lines.append(f"  - Fix: {f['fix']}")
            lines.append("")

        if brief.token_changes and any(brief.token_changes.values()):
            lines.append("## Token Changes")
            for change_type in ["added", "modified", "removed"]:
                items = brief.token_changes.get(change_type, [])
                if items:
                    lines.append(f"### {change_type.title()}")
                    for item in items:
                        if change_type == "modified":
                            lines.append(f"- `{item['token']}`: `{item['old']}` → `{item['new']}`")
                        else:
                            lines.append(f"- `{item['token']}`: `{item['value']}`")
                    lines.append("")

        if brief.decisions:
            lines.append("## Decisions")
            for d in brief.decisions:
                lines.append(f"- {d}")
            lines.append("")

        if brief.next_steps:
            lines.append("## Next Steps")
            for step in brief.next_steps:
                lines.append(f"- {step}")
            lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Compress context for agent handoff")
    parser.add_argument("--review", help="Path to review report (markdown)")
    parser.add_argument("--old-tokens", help="Path to old token file (JSON/CSS)")
    parser.add_argument("--new-tokens", help="Path to new token file (JSON/CSS)")
    parser.add_argument("--level", choices=["L1", "L2", "L3", "L4"], default="L3", help="Disclosure level")
    parser.add_argument("--budget", type=int, default=3000, help="Token budget")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--output", "-o", help="Output file")
    args = parser.parse_args()

    compressor = ContextCompressor(token_budget=args.budget)

    review_data = {}
    if args.review:
        review_data = compressor.load_review_report(Path(args.review))

    token_diff = {}
    if args.old_tokens and args.new_tokens:
        token_diff = compressor.load_token_diff(Path(args.old_tokens), Path(args.new_tokens))

    brief = compressor.generate_handoff(review_data, token_diff, args.level, args.format)
    brief = compressor.trim_to_budget(brief)
    output = compressor.export(brief, args.format)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Handoff brief written to {args.output} ({brief.token_estimate} tokens)")
    else:
        print(output)


if __name__ == "__main__":
    main()