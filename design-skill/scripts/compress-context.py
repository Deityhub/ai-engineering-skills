#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Context Compressor for Design Handoff

Summarizes design decisions, token changes, review findings, and component specs
into a compact format for efficient agent-to-agent handoff.

Usage:
    python compress-context.py --input review-report.md --output handoff.md --max-tokens 2000
    python compress-context.py --input tokens.json --diff previous-tokens.json --output token-changes.md
    python compress-context.py --session ./design-session --output summary.md
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter


@dataclass
class DesignDecision:
    """A design decision made during the session."""
    id: str
    category: str  # token, component, pattern, accessibility
    decision: str
    rationale: str
    alternatives_considered: List[str] = field(default_factory=list)
    impacted_files: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TokenChange:
    """A change to design tokens."""
    token_path: str  # e.g., "color.primary.value"
    old_value: Optional[str]
    new_value: str
    change_type: str  # added, modified, removed
    reason: str


@dataclass
class ReviewFinding:
    """A finding from design review."""
    severity: str
    category: str
    component: str
    issue: str
    fix: str
    status: str  # open, fixed, waived


class ContextCompressor:
    """Compress design context for handoff."""

    def __init__(self, max_tokens: int = 2000):
        self.max_tokens = max_tokens
        self.decisions: List[DesignDecision] = []
        self.token_changes: List[TokenChange] = []
        self.review_findings: List[ReviewFinding] = []
        self.component_specs: Dict[str, Any] = {}
        self.session_metadata: Dict[str, Any] = {}

    def load_review_report(self, report_path: Path) -> None:
        """Load findings from a review report (markdown or JSON)."""
        content = report_path.read_text(encoding='utf-8')

        if report_path.suffix == '.json':
            data = json.loads(content)
            self._parse_json_findings(data)
        else:
            self._parse_markdown_findings(content)

    def _parse_markdown_findings(self, content: str) -> None:
        """Parse findings from markdown report."""
        # Look for finding patterns
        finding_pattern = r'###\s*(Critical|Major|Minor)\s*\((\d+)\)\s*\n(.*?)(?=\n###|\n##|\Z)'
        for match in re.finditer(finding_pattern, content, re.DOTALL):
            severity, count, body = match.groups()

            # Extract individual findings
            item_pattern = r'\*\*Line (\d+):(\d+)\]\s*\[([^\]]+)\]\s*(\w+)\n>([^\n]+)\n(?:```\n([^\n]+)\n```)?\n\*\*Fix\*\*:\s*([^\n]+)'
            for item_match in re.finditer(item_pattern, body, re.MULTILINE):
                line, col, category, rule, issue, snippet, fix = item_match.groups()
                component_match = re.search(r'##\s+(.+)', content[:match.start()])
                component = component_match.group(1) if component_match else "Unknown"

                self.review_findings.append(ReviewFinding(
                    severity=severity.lower(),
                    category=category.lower(),
                    component=component,
                    issue=issue.strip(),
                    fix=fix.strip(),
                    status="open"
                ))

    def _parse_json_findings(self, data: List[Dict]) -> None:
        """Parse findings from JSON report."""
        for item in data:
            self.review_findings.append(ReviewFinding(
                severity=item.get('severity', 'minor'),
                category=item.get('category', 'unknown'),
                component=item.get('file', 'Unknown'),
                issue=item.get('message', ''),
                fix=item.get('fix_suggestion', ''),
                status="open"
            ))

    def load_token_diff(self, old_tokens_path: Path, new_tokens_path: Path) -> None:
        """Compute diff between two token files."""
        with open(old_tokens_path) as f:
            old_tokens = json.load(f)
        with open(new_tokens_path) as f:
            new_tokens = json.load(f)

        self._diff_tokens(old_tokens, new_tokens)

    def _diff_tokens(self, old: Dict, new: Dict, path: str = "") -> None:
        """Recursively diff token objects."""
        all_keys = set(old.keys()) | set(new.keys())

        for key in sorted(all_keys):
            current_path = f"{path}.{key}" if path else key

            if key not in old:
                self.token_changes.append(TokenChange(
                    token_path=current_path,
                    old_value=None,
                    new_value=json.dumps(new[key]),
                    change_type="added",
                    reason="New token added"
                ))
            elif key not in new:
                self.token_changes.append(TokenChange(
                    token_path=current_path,
                    old_value=json.dumps(old[key]),
                    new_value=None,
                    change_type="removed",
                    reason="Token removed"
                ))
            elif old[key] != new[key]:
                if isinstance(old[key], dict) and isinstance(new[key], dict):
                    self._diff_tokens(old[key], new[key], current_path)
                else:
                    self.token_changes.append(TokenChange(
                        token_path=current_path,
                        old_value=json.dumps(old[key]),
                        new_value=json.dumps(new[key]),
                        change_type="modified",
                        reason="Token value changed"
                    ))

    def load_component_specs(self, spec_dir: Path) -> None:
        """Load component specifications from directory."""
        for spec_file in spec_dir.glob("*.md"):
            content = spec_file.read_text(encoding='utf-8')
            self.component_specs[spec_file.stem] = self._parse_component_spec(content)

    def _parse_component_spec(self, content: str) -> Dict:
        """Parse component spec markdown."""
        spec = {"name": "", "props": [], "variants": [], "sizes": [], "states": []}

        # Extract name from first heading
        name_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if name_match:
            spec["name"] = name_match.group(1).strip()

        # Extract props table
        prop_pattern = r'\|\s*(\w+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
        for match in re.finditer(prop_pattern, content):
            prop_name, prop_type, prop_default, prop_desc = match.groups()
            if prop_name.lower() not in ['prop', 'name', 'property']:
                spec["props"].append({
                    "name": prop_name.strip(),
                    "type": prop_type.strip(),
                    "default": prop_default.strip(),
                    "description": prop_desc.strip(),
                })

        return spec

    def add_decision(self, category: str, decision: str, rationale: str,
                     alternatives: List[str] = None, files: List[str] = None) -> None:
        """Record a design decision."""
        self.decisions.append(DesignDecision(
            id=f"dec-{len(self.decisions) + 1:03d}",
            category=category,
            decision=decision,
            rationale=rationale,
            alternatives_considered=alternatives or [],
            impacted_files=files or []
        ))

    def set_metadata(self, **kwargs) -> None:
        """Set session metadata."""
        self.session_metadata.update(kwargs)

    def generate_handoff(self, format: str = 'markdown') -> str:
        """Generate compressed handoff document."""
        if format == 'json':
            return json.dumps({
                "metadata": self.session_metadata,
                "decisions": [d.__dict__ for d in self.decisions],
                "token_changes": [t.__dict__ for t in self.token_changes],
                "review_findings": [f.__dict__ for f in self.review_findings],
                "component_specs": self.component_specs,
            }, indent=2)

        sections = []

        # Header
        sections.append("# Design Handoff Summary")
        sections.append("")
        sections.append(f"**Generated**: {datetime.now().isoformat()}")
        sections.append(f"**Session**: {self.session_metadata.get('session_id', 'N/A')}")
        sections.append(f"**Author**: {self.session_metadata.get('author', 'N/A')}")
        sections.append("")

        # Token Changes (high priority)
        if self.token_changes:
            sections.append("## [ART] Token Changes")
            sections.append("")

            by_type = {}
            for change in self.token_changes:
                by_type.setdefault(change.change_type, []).append(change)

            for change_type, changes in by_type.items():
                emoji = {"added": "➕", "modified": "🔄", "removed": "➖"}.get(change_type, "📝")
                sections.append(f"### {emoji} {change_type.title()} ({len(changes)})")
                sections.append("")

                for change in changes[:20]:  # Limit to top 20
                    old = f" → {change.old_value}" if change.old_value else ""
                    new = f" → {change.new_value}" if change.new_value else ""
                    sections.append(f"- **{change.token_path}**: {old}{new}")
                    if change.reason:
                        sections.append(f"  *Reason*: {change.reason}")

                if len(changes) > 20:
                    sections.append(f"  *...and {len(changes) - 20} more*")

                sections.append("")

        # Design Decisions
        if self.decisions:
            sections.append("## [BRAIN] Design Decisions")
            sections.append("")

            by_category = {}
            for d in self.decisions:
                by_category.setdefault(d.category, []).append(d)

            for category, decisions in by_category.items():
                sections.append(f"### {category.title()} ({len(decisions)})")
                sections.append("")

                for d in decisions:
                    sections.append(f"**{d.id}**: {d.decision}")
                    sections.append(f"> *Rationale*: {d.rationale}")
                    if d.alternatives_considered:
                        sections.append(f"> *Alternatives*: {', '.join(d.alternatives_considered)}")
                    if d.impacted_files:
                        sections.append(f"> *Files*: {', '.join(d.impacted_files)}")
                    sections.append("")

        # Review Findings Summary
        if self.review_findings:
            sections.append("## [SEARCH] Review Findings Summary")
            sections.append("")

            # Count by severity
            severity_counts = Counter(f.severity for f in self.review_findings)
            for severity in ['critical', 'major', 'minor']:
                count = severity_counts.get(severity, 0)
                if count > 0:
                    emoji = {"critical": "[CRITICAL]", "major": "[MAJOR]", "minor": "[MINOR]"}[severity]
                    sections.append(f"- {emoji} {severity.title()}: {count}")

            sections.append("")

            # Top findings by component
            by_component = {}
            for f in self.review_findings:
                by_component.setdefault(f.component, []).append(f)

            sections.append("### Top Components by Findings")
            sections.append("")
            sorted_components = sorted(by_component.items(), key=lambda x: len(x[1]), reverse=True)
            for component, findings in sorted_components[:10]:
                sev_counts = Counter(f.severity for f in findings)
                sections.append(f"- **{component}**: {len(findings)} findings "
                              f"([CRITICAL]{sev_counts.get('critical',0)} [MAJOR]{sev_counts.get('major',0)} [MINOR]{sev_counts.get('minor',0)})")

            sections.append("")

            # Critical fixes needed
            critical = [f for f in self.review_findings if f.severity == 'critical']
            if critical:
                sections.append("### [CRITICAL] Critical Fixes Required")
                sections.append("")
                for f in critical[:10]:
                    sections.append(f"- **{f.component}** ({f.category}): {f.issue}")
                    sections.append(f"  *Fix*: {f.fix}")
                    sections.append("")

        # Component Specs
        if self.component_specs:
            sections.append("## [BOX] Component Specifications")
            sections.append("")

            for name, spec in self.component_specs.items():
                sections.append(f"### {spec.get('name', name)}")
                sections.append("")

                if spec.get('props'):
                    sections.append("**Props**:")
                    for prop in spec['props'][:10]:
                        req = " (required)" if 'required' in prop.get('default', '').lower() else ""
                        sections.append(f"- `{prop['name']}`: {prop['type']}{req} - {prop['description']}")
                    if len(spec['props']) > 10:
                        sections.append(f"  *...and {len(spec['props']) - 10} more*")
                    sections.append("")

                if spec.get('variants'):
                    sections.append(f"**Variants**: {', '.join(spec['variants'])}")
                if spec.get('sizes'):
                    sections.append(f"**Sizes**: {', '.join(spec['sizes'])}")
                if spec.get('states'):
                    sections.append(f"**States**: {', '.join(spec['states'])}")

                sections.append("")

        # Next Steps
        sections.append("## ➡️ Next Steps")
        sections.append("")

        next_steps = []

        if self.review_findings:
            critical_count = sum(1 for f in self.review_findings if f.severity == 'critical')
            if critical_count > 0:
                next_steps.append(f"Fix {critical_count} critical accessibility issues")

        if self.token_changes:
            next_steps.append("Review and approve token changes")

        if self.decisions:
            next_steps.append("Validate design decisions with stakeholders")

        if not next_steps:
            next_steps.append("No immediate actions required")

        for i, step in enumerate(next_steps, 1):
            sections.append(f"{i}. {step}")

        sections.append("")

        # Footer
        sections.append("---")
        sections.append("*Generated by design-skill context compressor*")

        return '\n'.join(sections)

    def estimate_tokens(self, text: str) -> int:
        """Rough token estimation (words * 1.3)."""
        return int(len(text.split()) * 1.3)

    def trim_to_token_limit(self, text: str) -> str:
        """Trim text to fit within token limit."""
        estimated = self.estimate_tokens(text)
        if estimated <= self.max_tokens:
            return text

        # Remove less critical sections
        lines = text.split('\n')
        # Keep header, token changes, decisions, critical findings
        # Remove detailed component specs first
        trimmed = []
        skip_section = False

        for line in lines:
            if line.startswith("## [BOX] Component Specifications"):
                skip_section = True
            elif line.startswith("## ") and not line.startswith("## [BOX]"):
                skip_section = False

            if not skip_section or line.startswith("# ") or line.startswith("## "):
                trimmed.append(line)

        result = '\n'.join(trimmed)
        if self.estimate_tokens(result) > self.max_tokens:
            # Aggressive truncation
            result = result[:self.max_tokens * 4] + "\n\n*[Truncated to fit token limit]*"

        return result


def main():
    parser = argparse.ArgumentParser(
        description="Compress design context for efficient agent handoff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python compress-context.py --input review-report.md --output handoff.md --max-tokens 2000
  python compress-context.py --input tokens.json --diff previous-tokens.json --output token-changes.md
  python compress-context.py --session ./design-session --output summary.md
        """
    )

    parser.add_argument('--input', '-i', help='Input review report or session directory')
    parser.add_argument('--diff', help='Previous tokens file for diff')
    parser.add_argument('--output', '-o', required=True, help='Output handoff file')
    parser.add_argument('--max-tokens', '-t', type=int, default=2000, help='Maximum tokens in output')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='Output format')
    parser.add_argument('--session-id', help='Session identifier')
    parser.add_argument('--author', help='Author name')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    compressor = ContextCompressor(max_tokens=args.max_tokens)
    compressor.set_metadata(
        session_id=args.session_id or "design-session",
        author=args.author or "design-skill",
        generated_at=datetime.now().isoformat()
    )

    if args.input:
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input not found: {input_path}", file=sys.stderr)
            sys.exit(1)

        if input_path.is_file():
            if args.diff:
                # Token diff mode
                diff_path = Path(args.diff)
                if not diff_path.exists():
                    print(f"Error: Diff file not found: {diff_path}", file=sys.stderr)
                    sys.exit(1)

                if args.verbose:
                    print(f"Computing token diff: {diff_path} → {input_path}")
                compressor.load_token_diff(diff_path, input_path)
            elif input_path.suffix in ['.md', '.json']:
                # Review report mode
                if args.verbose:
                    print(f"Loading review report: {input_path}")
                compressor.load_review_report(input_path)
            elif input_path.suffix == '.json':
                # Token file only
                if args.verbose:
                    print(f"Loading tokens: {input_path}")
                # Could add token analysis here
        elif input_path.is_dir():
            # Session directory mode
            if args.verbose:
                print(f"Loading session: {input_path}")

            # Load review reports
            for report in input_path.glob("**/*review*.md"):
                compressor.load_review_report(report)
            for report in input_path.glob("**/*review*.json"):
                compressor.load_review_report(report)

            # Load token diffs
            token_files = list(input_path.glob("**/tokens*.json"))
            if len(token_files) >= 2:
                token_files.sort(key=lambda f: f.stat().st_mtime)
                compressor.load_token_diff(token_files[-2], token_files[-1])

            # Load component specs
            spec_dirs = [input_path / "specs", input_path / "components", input_path / "component-specs"]
            for spec_dir in spec_dirs:
                if spec_dir.exists():
                    compressor.load_component_specs(spec_dir)

    # Generate handoff
    handoff = compressor.generate_handoff(args.format)
    handoff = compressor.trim_to_token_limit(handoff)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(handoff, encoding='utf-8')

    estimated_tokens = compressor.estimate_tokens(handoff)
    print(f"[OK] Handoff generated: {output_path}")
    print(f"   Estimated tokens: {estimated_tokens} / {args.max_tokens}")

    if args.verbose:
        print(f"\n[STATS] Summary:")
        print(f"   Decisions: {len(compressor.decisions)}")
        print(f"   Token changes: {len(compressor.token_changes)}")
        print(f"   Review findings: {len(compressor.review_findings)}")
        print(f"   Component specs: {len(compressor.component_specs)}")


if __name__ == '__main__':
    main()