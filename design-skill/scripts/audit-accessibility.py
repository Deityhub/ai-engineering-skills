#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Accessibility Audit Script

Scans HTML, React, Vue, and other frontend files for WCAG 2.1 AA violations.
Outputs detailed reports with line numbers and fix suggestions.

Usage:
    python audit-accessibility.py --file Component.tsx --format markdown
    python audit-accessibility.py --dir ./src --output report.md --format markdown
    python audit-accessibility.py --file page.html --check contrast --format json
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"  # WCAG AA blocking
    MAJOR = "major"        # Significant barrier
    MINOR = "minor"        # Best practice / polish


class Category(Enum):
    CONTRAST = "contrast"
    KEYBOARD = "keyboard"
    SEMANTICS = "semantics"
    FORMS = "forms"
    IMAGES = "images"
    MOTION = "motion"
    TOUCH = "touch"
    FOCUS = "focus"
    TEXT_SPACING = "text_spacing"
    RTL = "rtl"
    LANGUAGE = "language"


@dataclass
class Finding:
    severity: Severity
    category: Category
    rule: str
    message: str
    file: str
    line: int
    column: Optional[int] = None
    snippet: Optional[str] = None
    fix_suggestion: Optional[str] = None
    wcag_ref: Optional[str] = None


class AccessibilityAuditor:
    """Audit files for accessibility violations."""

    def __init__(self):
        self.findings: List[Finding] = []
        self.current_file = ""
        self.current_lines: List[str] = []

    def audit_file(self, file_path: Path, checks: List[Category] = None) -> List[Finding]:
        """Audit a single file."""
        self.current_file = str(file_path)
        self.current_lines = file_path.read_text(encoding='utf-8', errors='ignore').splitlines()
        self.findings = []

        if checks is None:
            checks = list(Category)

        content = '\n'.join(self.current_lines)

        # Run checks based on file type
        if file_path.suffix in ['.html', '.htm']:
            self._audit_html(content, checks)
        elif file_path.suffix in ['.tsx', '.jsx', '.ts', '.js']:
            self._audit_jsx_tsx(content, checks)
        elif file_path.suffix == '.vue':
            self._audit_vue(content, checks)
        elif file_path.suffix in ['.css', '.scss', '.sass']:
            self._audit_css(content, checks)

        return self.findings

    def audit_directory(self, dir_path: Path, checks: List[Category] = None,
                        patterns: List[str] = None) -> List[Finding]:
        """Audit all supported files in a directory."""
        if patterns is None:
            patterns = ['**/*.html', '**/*.htm', '**/*.tsx', '**/*.jsx',
                       '**/*.vue', '**/*.css', '**/*.scss', '**/*.sass']

        all_findings = []
        for pattern in patterns:
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    findings = self.audit_file(file_path, checks)
                    all_findings.extend(findings)

        self.findings = all_findings
        return self.findings

    def _add_finding(self, severity: Severity, category: Category, rule: str,
                     message: str, line: int, column: int = None,
                     snippet: str = None, fix: str = None, wcag: str = None):
        """Add a finding."""
        self.findings.append(Finding(
            severity=severity,
            category=category,
            rule=rule,
            message=message,
            file=self.current_file,
            line=line,
            column=column,
            snippet=snippet or (self.current_lines[line-1].strip() if 0 < line <= len(self.current_lines) else None),
            fix_suggestion=fix,
            wcag_ref=wcag
        )
        )

    def _get_line_context(self, line: int, context: int = 2) -> str:
        """Get surrounding lines for context."""
        start = max(0, line - 1 - context)
        end = min(len(self.current_lines), line + context)
        return '\n'.join(f"{i+1:4d}: {self.current_lines[i]}" for i in range(start, end))

    # ===== HTML Audits =====
    def _audit_html(self, content: str, checks: List[Category]):
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            self._check_html_line(line, i, checks)

    def _check_html_line(self, line: str, line_num: int, checks: List[Category]):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('<!--') or stripped.startswith('//'):
            return

        # Contrast checks (basic - can't compute actual contrast without rendering)
        if Category.CONTRAST in checks:
            # Check for common low-contrast patterns
            if re.search(r'color:\s*#?([0-9a-fA-F]{3,6})', line):
                # Would need computed styles to verify - flag for manual review
                pass

        # Keyboard/Focus
        if Category.KEYBOARD in checks or Category.FOCUS in checks:
            # outline: none without replacement
            if re.search(r'outline\s*:\s*none', line) and not re.search(r'box-shadow|focus-visible|:focus', line):
                self._add_finding(
                    Severity.CRITICAL, Category.FOCUS, "outline-none",
                    "outline: none without visible focus replacement",
                    line_num, fix="Add :focus-visible { box-shadow: 0 0 0 2px var(--color-focus-ring); }",
                    wcag="WCAG 2.4.7 Focus Visible"
                )

            # tabindex > 0
            if re.search(r'tabindex\s*=\s*["\']?[1-9]\d*', line):
                self._add_finding(
                    Severity.MAJOR, Category.KEYBOARD, "positive-tabindex",
                    "Positive tabindex disrupts natural focus order",
                    line_num, fix="Use tabindex='0' or tabindex='-1' only",
                    wcag="WCAG 2.4.3 Focus Order"
                )

        # Semantics
        if Category.SEMANTICS in checks:
            # Div/button used as button
            if re.search(r'<div[^>]*onclick|<span[^>]*onclick', line, re.IGNORECASE):
                self._add_finding(
                    Severity.CRITICAL, Category.SEMANTICS, "div-as-button",
                    "Interactive div/span should be <button> or <a>",
                    line_num, fix="Replace with <button> or <a href='...'>",
                    wcag="WCAG 4.1.2 Name, Role, Value"
                )

            # Missing landmarks
            if '<body' in line.lower() and not any(
                lm in content for lm in ['<header', '<nav', '<main', '<aside', '<footer']
            ):
                # Only flag once per file
                if line_num == 1 or 'body' in stripped.lower():
                    self._add_finding(
                        Severity.MAJOR, Category.SEMANTICS, "missing-landmarks",
                        "Page missing landmark elements (header, nav, main, aside, footer)",
                        line_num, fix="Add <header>, <nav>, <main>, <aside>, <footer> as appropriate",
                        wcag="WCAG 1.3.1 Info and Relationships"
                    )

            # Heading hierarchy
            heading_match = re.search(r'<h([1-6])[^>]*>', line, re.IGNORECASE)
            if heading_match:
                level = int(heading_match.group(1))
                # Track heading levels (simplified - would need full document parse)
                pass

        # Forms
        if Category.FORMS in checks:
            # Input without label
            input_match = re.search(r'<input[^>]*id\s*=\s*["\']([^"\']+)["\']', line, re.IGNORECASE)
            if input_match and 'type="hidden"' not in line:
                input_id = input_match.group(1)
                # Check if label exists for this id
                if not re.search(rf'<label[^>]*for\s*=\s*["\']?{re.escape(input_id)}["\']?', content, re.IGNORECASE):
                    self._add_finding(
                        Severity.CRITICAL, Category.FORMS, "input-without-label",
                        f"Input with id='{input_id}' has no associated label",
                        line_num, fix=f"Add <label for='{input_id}'>Label text</label>",
                        wcag="WCAG 1.3.1, 3.3.2 Labels or Instructions"
                    )

            # Missing autocomplete
            if re.search(r'<input[^>]*type\s*=\s*["\'](email|tel|url|password)["\']', line, re.IGNORECASE):
                if 'autocomplete' not in line:
                    self._add_finding(
                        Severity.MINOR, Category.FORMS, "missing-autocomplete",
                        "Input missing autocomplete attribute",
                        line_num, fix='Add autocomplete="email" (or tel, url, current-password)',
                        wcag="WCAG 1.3.5 Identify Input Purpose"
                    )

        # Images
        if Category.IMAGES in checks:
            img_match = re.search(r'<img[^>]*src\s*=\s*["\'][^"\']*["\']', line, re.IGNORECASE)
            if img_match:
                # Check for alt
                if 'alt=' not in line:
                    self._add_finding(
                        Severity.CRITICAL, Category.IMAGES, "missing-alt",
                        "Image missing alt attribute",
                        line_num, fix='Add alt="description" or alt="" for decorative',
                        wcag="WCAG 1.1.1 Non-text Content"
                    )
                elif 'alt=""' in line or 'alt=\'\'' in line:
                    # Decorative - check if it might not be
                    if not any(attr in line for attr in ['role="presentation"', 'aria-hidden="true"']):
                        pass  # OK - empty alt for decorative

        # Language
        if Category.LANGUAGE in checks:
            if '<html' in line.lower() and 'lang=' not in line:
                self._add_finding(
                    Severity.MAJOR, Category.LANGUAGE, "missing-lang",
                    "HTML element missing lang attribute",
                    line_num, fix='Add lang="en" (or appropriate language code)',
                    wcag="WCAG 3.1.1 Language of Page"
                )

    # ===== JSX/TSX Audits =====
    def _audit_jsx_tsx(self, content: str, checks: List[Category]):
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            self._check_jsx_line(line, i, checks, content)

    def _check_jsx_line(self, line: str, line_num: int, checks: List[Category], full_content: str):
        stripped = line.strip()

        # Skip comments
        if stripped.startswith('//') or stripped.startswith('/*') or stripped.startswith('*'):
            return

        # Keyboard/Focus
        if Category.KEYBOARD in checks or Category.FOCUS in checks:
            # onClick on non-interactive element
            if re.search(r'onClick\s*=', line) and not re.search(
                r'<(button|a|input|select|textarea|option|summary|details)', line, re.IGNORECASE
            ):
                # Check if it's a custom component (capitalized)
                if re.search(r'<[A-Z]\w*', line):
                    pass  # Custom component - might be accessible
                else:
                    self._add_finding(
                        Severity.CRITICAL, Category.KEYBOARD, "onclick-on-noninteractive",
                        "onClick on non-interactive element (div, span, etc.)",
                        line_num, fix="Use <button> or add role='button' + tabIndex={0} + onKeyDown",
                        wcag="WCAG 2.1.1 Keyboard, 4.1.2 Name, Role, Value"
                    )

            # Missing onKeyDown for custom buttons
            if re.search(r'onClick\s*=', line) and 'onKeyDown' not in full_content[max(0, line_num-10):line_num+10]:
                # Could be a custom button component
                if re.search(r'<[A-Z]\w*', line) and 'Button' in line:
                    self._add_finding(
                        Severity.MAJOR, Category.KEYBOARD, "missing-keydown",
                        "Interactive component with onClick but no onKeyDown for keyboard support",
                        line_num, fix="Add onKeyDown handler for Enter/Space keys",
                        wcag="WCAG 2.1.1 Keyboard"
                    )

        # Semantics
        if Category.SEMANTICS in checks:
            # Fragment without proper semantics
            if re.search(r'<>\s*$', stripped) or re.search(r'</>', stripped):
                pass  # Fragments OK

            # Missing alt on img
            if re.search(r'<img\b', line, re.IGNORECASE) and 'alt' not in line:
                self._add_finding(
                    Severity.CRITICAL, Category.IMAGES, "jsx-missing-alt",
                    "Image missing alt prop",
                    line_num, fix='Add alt="description" or alt=""',
                    wcag="WCAG 1.1.1 Non-text Content"
                )

        # Forms
        if Category.FORMS in checks:
            # Input without label (JSX)
            if re.search(r'<input\b', line, re.IGNORECASE):
                if 'id=' in line and 'htmlFor' not in full_content and 'label' not in full_content.lower():
                    # Simplified check - would need full JSX parsing
                    pass

            # aria-invalid without aria-describedby
            if 'aria-invalid' in line and 'aria-describedby' not in line:
                self._add_finding(
                    Severity.MAJOR, Category.FORMS, "aria-invalid-without-describedby",
                    "aria-invalid requires aria-describedby pointing to error message",
                    line_num, fix="Add aria-describedby='error-id' and <span id='error-id' role='alert'>Error</span>",
                    wcag="WCAG 3.3.1 Error Identification"
                )

            # Missing aria-live for error messages
            if re.search(r'error|Error', line, re.IGNORECASE) and 'aria-live' not in line and 'role="alert"' not in line:
                if any(kw in line.lower() for kw in ['message', 'text', 'span', 'div', 'p']):
                    self._add_finding(
                        Severity.MAJOR, Category.FORMS, "error-without-live",
                        "Error message should have aria-live='polite' or role='alert'",
                        line_num, fix="Add aria-live='polite' or role='alert' to error container",
                        wcag="WCAG 4.1.3 Status Messages"
                    )

        # Motion
        if Category.MOTION in checks:
            # CSS animations without prefers-reduced-motion check
            if any(prop in line for prop in ['animation:', 'transition:', '@keyframes']):
                if 'prefers-reduced-motion' not in full_content:
                    self._add_finding(
                        Severity.MINOR, Category.MOTION, "animation-without-reduced-motion",
                        "Animation/transition without prefers-reduced-motion media query",
                        line_num, fix="Wrap in @media (prefers-reduced-motion: no-preference) { ... }",
                        wcag="WCAG 2.3.3 Animation from Interactions"
                    )

        # Touch targets
        if Category.TOUCH in checks:
            # Small clickable elements
            if re.search(r'<(button|a|input)[^>]*style\s*=\s*\{[^}]*(width|height)\s*:\s*[\'"]?\d{1,2}(px)?[\'"]?', line):
                # Hard to detect inline styles - flag for review
                pass

        # RTL
        if Category.RTL in checks:
            # Left/right instead of start/end in logical properties
            if re.search(r'(margin|padding|border|left|right)\s*:\s*[^;]*;', line) and \
               not re.search(r'(margin|padding|border)-(inline-start|inline-end|block-start|block-end)', line):
                if 'style=' in line or 'className=' in line:
                    pass  # Could be logical properties in CSS

    # ===== Vue Audits =====
    def _audit_vue(self, content: str, checks: List[Category]):
        # Split into template, script, style
        template_match = re.search(r'<template>([\s\S]*?)</template>', content)
        script_match = re.search(r'<script[^>]*>([\s\S]*?)</script>', content)
        style_match = re.search(r'<style[^>]*>([\s\S]*?)</style>', content)

        if template_match:
            template_lines = template_match.group(1).splitlines()
            for i, line in enumerate(template_lines, 1):
                self._check_vue_template_line(line, i, checks)

        if style_match:
            style_lines = style_match.group(1).splitlines()
            for i, line in enumerate(style_lines, 1):
                self._check_css_line(line, i, checks)

    def _check_vue_template_line(self, line: str, line_num: int, checks: List[Category]):
        # Similar to HTML but with Vue directives
        stripped = line.strip()

        if Category.IMAGES in checks:
            if re.search(r'<img\b', line, re.IGNORECASE) and ':alt' not in line and 'alt=' not in line:
                self._add_finding(
                    Severity.CRITICAL, Category.IMAGES, "vue-missing-alt",
                    "Image missing alt attribute",
                    line_num, fix='Add :alt="description" or alt=""',
                    wcag="WCAG 1.1.1 Non-text Content"
                )

        if Category.FORMS in checks:
            if re.search(r'<input\b', line, re.IGNORECASE):
                if 'id=' in line and 'v-model' not in line:
                    pass

    # ===== CSS Audits =====
    def _audit_css(self, content: str, checks: List[Category]):
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            self._check_css_line(line, i, checks)

    def _check_css_line(self, line: str, line_num: int, checks: List[Category]):
        stripped = line.strip()

        if Category.CONTRAST in checks:
            # Can't compute actual contrast - flag color combinations for review
            pass

        if Category.FOCUS in checks:
            if re.search(r'outline\s*:\s*none', line) and \
               not re.search(r'box-shadow|focus-visible|:focus', line):
                self._add_finding(
                    Severity.CRITICAL, Category.FOCUS, "css-outline-none",
                    "outline: none without replacement focus style",
                    line_num, fix="Add :focus-visible { outline: 2px solid var(--color-focus-ring); outline-offset: 2px; }",
                    wcag="WCAG 2.4.7 Focus Visible"
                )

        if Category.MOTION in checks:
            if any(prop in line for prop in ['animation:', 'transition:']) and \
               'prefers-reduced-motion' not in content:
                self._add_finding(
                    Severity.MINOR, Category.MOTION, "css-animation-without-reduced-motion",
                    "Animation/transition without prefers-reduced-motion",
                    line_num, fix="Wrap in @media (prefers-reduced-motion: no-preference) { ... }",
                    wcag="WCAG 2.3.3 Animation from Interactions"
                )

        if Category.TOUCH in checks:
            # Check for minimum touch target sizes in CSS
            if re.search(r'(width|height)\s*:\s*(\d+)px', line):
                match = re.search(r'(width|height)\s*:\s*(\d+)px', line)
                if match and int(match.group(2)) < 44:
                    prop = match.group(1)
                    val = int(match.group(2))
                    if 'button' in content.lower() or 'link' in content.lower() or 'input' in content.lower():
                        self._add_finding(
                            Severity.MAJOR, Category.TOUCH, "css-small-touch-target",
                            f"{prop}: {val}px is below 44px minimum touch target",
                            line_num, fix=f"Increase {prop} to at least 44px or add padding",
                            wcag="WCAG 2.5.5 Target Size"
                        )

    def generate_report(self, format: str = 'markdown') -> str:
        """Generate report in specified format."""
        if format == 'json':
            return json.dumps([asdict(f) for f in self.findings], indent=2)

        # Markdown format
        lines = [
            "# Accessibility Audit Report",
            "",
            f"**Files scanned**: {len(set(f.file for f in self.findings))}",
            f"**Total findings**: {len(self.findings)}",
            f"**Critical**: {sum(1 for f in self.findings if f.severity == Severity.CRITICAL)}",
            f"**Major**: {sum(1 for f in self.findings if f.severity == Severity.MAJOR)}",
            f"**Minor**: {sum(1 for f in self.findings if f.severity == Severity.MINOR)}",
            ""
        ]

        # Group by file
        by_file: Dict[str, List[Finding]] = {}
        for f in self.findings:
            by_file.setdefault(f.file, []).append(f)

        for file, findings in sorted(by_file.items()):
            lines.append(f"## {file}")
            lines.append("")

            # Group by severity
            for severity in [Severity.CRITICAL, Severity.MAJOR, Severity.MINOR]:
                sev_findings = [f for f in findings if f.severity == severity]
                if not sev_findings:
                    continue

                lines.append(f"### {severity.value.title()} ({len(sev_findings)})")
                lines.append("")

                for f in sev_findings:
                    lines.append(f"**Line {f.line}** [{f.category.value}] {f.rule}")
                    lines.append(f"> {f.message}")
                    if f.snippet:
                        lines.append(f"```")
                        lines.append(f"{f.snippet}")
                        lines.append(f"```")
                    if f.fix_suggestion:
                        lines.append(f"**Fix**: {f.fix_suggestion}")
                    if f.wcag_ref:
                        lines.append(f"**WCAG**: {f.wcag_ref}")
                    lines.append("")

        return '\n'.join(lines)

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        return {
            "total": len(self.findings),
            "critical": sum(1 for f in self.findings if f.severity == Severity.CRITICAL),
            "major": sum(1 for f in self.findings if f.severity == Severity.MAJOR),
            "minor": sum(1 for f in self.findings if f.severity == Severity.MINOR),
            "by_category": {
                cat.value: sum(1 for f in self.findings if f.category == cat)
                for cat in Category
            },
            "by_file": {
                file: len(findings)
                for file, findings in self._group_by_file().items()
            }
        }

    def _group_by_file(self) -> Dict[str, List[Finding]]:
        by_file: Dict[str, List[Finding]] = {}
        for f in self.findings:
            by_file.setdefault(f.file, []).append(f)
        return by_file


def main():
    parser = argparse.ArgumentParser(
        description="Audit accessibility violations in frontend files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python audit-accessibility.py --file Component.tsx --format markdown
  python audit-accessibility.py --dir ./src --output report.md --format markdown
  python audit-accessibility.py --file page.html --check contrast,forms --format json
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', help='Single file to audit')
    group.add_argument('--dir', '-d', help='Directory to audit recursively')

    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='Output format')
    parser.add_argument('--check', help='Comma-separated checks (contrast,keyboard,semantics,forms,images,motion,touch,focus,text_spacing,rtl,language)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    # Parse checks
    checks = None
    if args.check:
        try:
            checks = [Category(c.strip()) for c in args.check.split(',')]
        except ValueError as e:
            print(f"Error: Invalid check category: {e}", file=sys.stderr)
            sys.exit(1)

    auditor = AccessibilityAuditor()

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"Auditing: {file_path}")
        findings = auditor.audit_file(file_path, checks)
    else:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"Error: Directory not found: {dir_path}", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"Auditing directory: {dir_path}")
        findings = auditor.audit_directory(dir_path, checks)

    # Generate report
    report = auditor.generate_report(args.format)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report written to: {output_path}")
    else:
        print(report)

    # Print summary
    summary = auditor.get_summary()
    print(f"\n[STATS] Summary:", file=sys.stderr)
    print(f"   Total findings: {summary['total']}", file=sys.stderr)
    print(f"   [CRITICAL] Critical: {summary['critical']}", file=sys.stderr)
    print(f"   [MAJOR] Major: {summary['major']}", file=sys.stderr)
    print(f"   [MINOR] Minor: {summary['minor']}", file=sys.stderr)

    if summary['by_category']:
        print(f"   By category:", file=sys.stderr)
        for cat, count in summary['by_category'].items():
            if count > 0:
                print(f"     {cat}: {count}", file=sys.stderr)

    # Exit code based on critical findings
    if summary['critical'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()