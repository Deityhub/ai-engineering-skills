#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token Compliance Validator

Checks files for magic numbers (hardcoded values) that should use design tokens.
Ensures design system consistency across the codebase.

Usage:
    python validate-tokens.py --file Component.tsx --tokens tokens.json
    python validate-tokens.py --dir ./src --tokens tokens.json --output report.md
    python validate-tokens.py --file styles.css --tokens tokens.json --fix
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


class TokenType(Enum):
    SPACING = "spacing"
    COLOR = "color"
    TYPOGRAPHY = "typography"
    BORDER_RADIUS = "border_radius"
    SHADOW = "shadow"
    BREAKPOINT = "breakpoint"
    Z_INDEX = "z_index"
    TRANSITION = "transition"


@dataclass
class Violation:
    token_type: TokenType
    found_value: str
    expected_token: str
    file: str
    line: int
    column: int
    context: str
    severity: str  # "error" | "warning"
    auto_fixable: bool = False


class TokenValidator:
    """Validate token compliance in source files."""

    def __init__(self, tokens_file: Path):
        self.tokens = self._load_tokens(tokens_file)
        self.token_patterns = self._build_patterns()
        self.violations: List[Violation] = []
        self.current_file = ""
        self.current_lines: List[str] = []

    def _load_tokens(self, tokens_file: Path) -> Dict:
        """Load token definitions from JSON file."""
        try:
            content = tokens_file.read_text(encoding='utf-8')
            return json.loads(content)
        except Exception as e:
            print(f"Error loading tokens: {e}", file=sys.stderr)
            sys.exit(1)

    def _build_patterns(self) -> Dict[TokenType, List[Tuple[re.Pattern, str]]]:
        """Build regex patterns for detecting magic numbers."""
        patterns = {}

        # Spacing patterns (px, rem, em values that should use spacing tokens)
        spacing_patterns = []
        # CSS: padding: 16px, margin: 1rem, gap: 24px
        spacing_patterns.append((
            re.compile(r'\b(padding|margin|gap|inset|top|right|bottom|left)\s*:\s*(\d+(?:\.\d+)?)(px|rem|em)\b', re.IGNORECASE),
            "spacing"
        ))
        # JS/TS: style={{ padding: '16px' }}, margin: 16
        spacing_patterns.append((
            re.compile(r'(padding|margin|gap|top|right|bottom|left)\s*:\s*[\'"`](\d+(?:\.\d+)?)(px|rem|em)[\'"`]', re.IGNORECASE),
            "spacing"
        ))
        spacing_patterns.append((
            re.compile(r'(padding|margin|gap|top|right|bottom|left)\s*:\s*(\d+)(?!\s*(px|rem|em|%))', re.IGNORECASE),
            "spacing"
        ))
        patterns[TokenType.SPACING] = spacing_patterns

        # Color patterns (hex, rgb, hsl values)
        color_patterns = []
        # CSS: color: #2563eb, background: rgb(37, 99, 235)
        color_patterns.append((
            re.compile(r'\b(color|background|border|fill|stroke)\s*:\s*(#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|hsla\([^)]+\))\b', re.IGNORECASE),
            "color"
        ))
        # JS/TS: style={{ color: '#2563eb' }}
        color_patterns.append((
            re.compile(r'(color|background|border|fill|stroke)\s*:\s*[\'"`](#[0-9a-fA-F]{3,8}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|hsla\([^)]+\))[\'"`]', re.IGNORECASE),
            "color"
        ))
        # Tailwind arbitrary values: bg-[#2563eb]
        color_patterns.append((
            re.compile(r'(bg|text|border|fill|stroke)-\[#[0-9a-fA-F]{3,8}\]', re.IGNORECASE),
            "color"
        ))
        patterns[TokenType.COLOR] = color_patterns

        # Typography patterns (font-size, font-weight, line-height)
        typography_patterns = []
        # CSS: font-size: 16px, font-weight: 600, line-height: 1.5
        typography_patterns.append((
            re.compile(r'\b(font-size|font-weight|line-height|letter-spacing)\s*:\s*(\d+(?:\.\d+)?)(px|rem|em|%)\b', re.IGNORECASE),
            "typography"
        ))
        # JS/TS: fontSize: '16px'
        typography_patterns.append((
            re.compile(r'(fontSize|fontWeight|lineHeight|letterSpacing)\s*:\s*[\'"`](\d+(?:\.\d+)?)(px|rem|em|%)[\'"`]', re.IGNORECASE),
            "typography"
        ))
        patterns[TokenType.TYPOGRAPHY] = typography_patterns

        # Border radius patterns
        radius_patterns = []
        radius_patterns.append((
            re.compile(r'\b(border-radius)\s*:\s*(\d+(?:\.\d+)?)(px|rem|em)\b', re.IGNORECASE),
            "border_radius"
        ))
        radius_patterns.append((
            re.compile(r'(borderRadius)\s*:\s*[\'"`](\d+(?:\.\d+)?)(px|rem|em)[\'"`]', re.IGNORECASE),
            "border_radius"
        ))
        radius_patterns.append((
            re.compile(r'rounded-\[(\d+(?:\.\d+)?)(px|rem|em)\]', re.IGNORECASE),
            "border_radius"
        ))
        patterns[TokenType.BORDER_RADIUS] = radius_patterns

        # Shadow patterns
        shadow_patterns = []
        shadow_patterns.append((
            re.compile(r'\b(box-shadow)\s*:\s*([^;]{10,})', re.IGNORECASE),
            "shadow"
        ))
        shadow_patterns.append((
            re.compile(r'(boxShadow)\s*:\s*[\'"`]([^\'"`]{10,})[\'"`]', re.IGNORECASE),
            "shadow"
        ))
        shadow_patterns.append((
            re.compile(r'shadow-\[([^\]]+)\]', re.IGNORECASE),
            "shadow"
        ))
        patterns[TokenType.SHADOW] = shadow_patterns

        # Breakpoint patterns
        breakpoint_patterns = []
        breakpoint_patterns.append((
            re.compile(r'@media\s*\(\s*(min|max)-width\s*:\s*(\d+)px\s*\)', re.IGNORECASE),
            "breakpoint"
        ))
        breakpoint_patterns.append((
            re.compile(r'(sm|md|lg|xl|2xl):', re.IGNORECASE),
            "breakpoint"  # Tailwind - usually OK but flag for review
        ))
        patterns[TokenType.BREAKPOINT] = breakpoint_patterns

        return patterns

    def _get_expected_token(self, token_type: TokenType, value: str) -> Optional[str]:
        """Map a magic value to its expected token."""
        value_lower = value.lower().strip()

        if token_type == TokenType.SPACING:
            # Map px/rem values to spacing tokens
            px_match = re.match(r'(\d+(?:\.\d+)?)px', value_lower)
            rem_match = re.match(r'(\d+(?:\.\d+)?)rem', value_lower)
            em_match = re.match(r'(\d+(?:\.\d+)?)em', value_lower)

            if px_match:
                px_val = float(px_match.group(1))
                # Map to 4px base grid
                step = round(px_val / 4)
                if step <= 16 and step > 0:
                    return f"var(--space-{step})"
            elif rem_match:
                rem_val = float(rem_match.group(1))
                # 1rem = 16px typically
                px_val = rem_val * 16
                step = round(px_val / 4)
                if step <= 16 and step > 0:
                    return f"var(--space-{step})"

        elif token_type == TokenType.COLOR:
            # Map common hex colors to semantic tokens
            color_map = {
                '#2563eb': 'var(--color-primary)',
                '#1d4ed8': 'var(--color-primary-hover)',
                '#1e40af': 'var(--color-primary-active)',
                '#93c5fd': 'var(--color-primary-disabled)',
                '#64748b': 'var(--color-secondary)',
                '#475569': 'var(--color-secondary-hover)',
                '#ffffff': 'var(--color-surface)',
                '#f8fafc': 'var(--color-surface-hover)',
                '#e2e8f0': 'var(--color-border)',
                '#cbd5e1': 'var(--color-border-strong)',
                '#0f172a': 'var(--color-text-primary)',
                '#475569': 'var(--color-text-secondary)',
                '#94a3b8': 'var(--color-text-muted)',
                '#dc2626': 'var(--color-error)',
                '#16a34a': 'var(--color-success)',
                '#ca8a04': 'var(--color-warning)',
            }
            return color_map.get(value_lower)

        elif token_type == TokenType.TYPOGRAPHY:
            # Map font sizes to typography tokens
            size_map = {
                '0.75rem': 'var(--font-size-xs)', '12px': 'var(--font-size-xs)',
                '0.875rem': 'var(--font-size-sm)', '14px': 'var(--font-size-sm)',
                '1rem': 'var(--font-size-md)', '16px': 'var(--font-size-md)',
                '1.125rem': 'var(--font-size-lg)', '18px': 'var(--font-size-lg)',
                '1.25rem': 'var(--font-size-xl)', '20px': 'var(--font-size-xl)',
                '1.5rem': 'var(--font-size-2xl)', '24px': 'var(--font-size-2xl)',
                '1.875rem': 'var(--font-size-3xl)', '30px': 'var(--font-size-3xl)',
                '2.25rem': 'var(--font-size-4xl)', '36px': 'var(--font-size-4xl)',
                '3rem': 'var(--font-size-5xl)', '48px': 'var(--font-size-5xl)',
            }
            return size_map.get(value_lower)

        elif token_type == TokenType.BORDER_RADIUS:
            radius_map = {
                '4px': 'var(--radius-sm)', '0.25rem': 'var(--radius-sm)',
                '6px': 'var(--radius-md)', '0.375rem': 'var(--radius-md)',
                '8px': 'var(--radius-lg)', '0.5rem': 'var(--radius-lg)',
                '12px': 'var(--radius-xl)', '0.75rem': 'var(--radius-xl)',
                '9999px': 'var(--radius-full)', '50%': 'var(--radius-full)',
            }
            return radius_map.get(value_lower)

        return None

    def validate_file(self, file_path: Path, fix: bool = False) -> List[Violation]:
        """Validate a single file for token compliance."""
        self.current_file = str(file_path)
        self.current_lines = file_path.read_text(encoding='utf-8', errors='ignore').splitlines()
        self.violations = []

        content = '\n'.join(self.current_lines)

        # Determine file type for context-aware checking
        file_type = file_path.suffix.lower()

        for token_type, patterns in self.token_patterns.items():
            for pattern, prop_name in patterns:
                for match in pattern.finditer(content):
                    line_num = content[:match.start()].count('\n') + 1
                    column = match.start() - content.rfind('\n', 0, match.start())

                    # Extract the value
                    value = match.group(2) if match.lastindex >= 2 else match.group(1)

                    # Skip if already using a token
                    if 'var(--' in value or 'var(--' in match.group(0):
                        continue

                    # Skip CSS variables definitions
                    if line_num <= len(self.current_lines) and self.current_lines[line_num - 1].strip().startswith('--'):
                        continue

                    # Skip in comments
                    line_content = self.current_lines[line_num - 1] if line_num <= len(self.current_lines) else ""
                    if self._is_in_comment(line_content, column):
                        continue

                    expected = self._get_expected_token(token_type, value)
                    if expected:
                        severity = "error" if token_type in [TokenType.COLOR, TokenType.SPACING] else "warning"
                        self.violations.append(Violation(
                            token_type=token_type,
                            found_value=value,
                            expected_token=expected,
                            file=self.current_file,
                            line=line_num,
                            column=column,
                            context=line_content.strip(),
                            severity=severity,
                            auto_fixable=True
                        ))

        return self.violations

    def validate_directory(self, dir_path: Path, patterns: List[str] = None) -> List[Violation]:
        """Validate all supported files in a directory."""
        if patterns is None:
            patterns = ['**/*.css', '**/*.scss', '**/*.sass', '**/*.tsx', '**/*.jsx', '**/*.ts', '**/*.js', '**/*.vue']

        all_violations = []
        for pattern in patterns:
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    violations = self.validate_file(file_path)
                    all_violations.extend(violations)

        self.violations = all_violations
        return self.violations

    def _is_in_comment(self, line: str, column: int) -> bool:
        """Check if position is within a comment."""
        # Simple check for // and /* */
        if '//' in line:
            comment_pos = line.find('//')
            if column > comment_pos:
                return True
        return False

    def generate_report(self, format: str = 'markdown') -> str:
        """Generate violation report."""
        if format == 'json':
            return json.dumps([{
                'token_type': v.token_type.value,
                'found_value': v.found_value,
                'expected_token': v.expected_token,
                'file': v.file,
                'line': v.line,
                'column': v.column,
                'context': v.context,
                'severity': v.severity,
                'auto_fixable': v.auto_fixable
            } for v in self.violations], indent=2)

        lines = [
            "# Token Compliance Report",
            "",
            f"**Files scanned**: {len(set(v.file for v in self.violations))}",
            f"**Total violations**: {len(self.violations)}",
            f"**Errors**: {sum(1 for v in self.violations if v.severity == 'error')}",
            f"**Warnings**: {sum(1 for v in self.violations if v.severity == 'warning')}",
            f"**Auto-fixable**: {sum(1 for v in self.violations if v.auto_fixable)}",
            ""
        ]

        # Group by file
        by_file: Dict[str, List[Violation]] = {}
        for v in self.violations:
            by_file.setdefault(v.file, []).append(v)

        for file, violations in sorted(by_file.items()):
            lines.append(f"## {file}")
            lines.append("")

            # Group by token type
            by_type: Dict[str, List[Violation]] = {}
            for v in violations:
                by_type.setdefault(v.token_type.value, []).append(v)

            for token_type, type_violations in sorted(by_type.items()):
                lines.append(f"### {token_type.replace('_', ' ').title()} ({len(type_violations)})")
                lines.append("")

                for v in type_violations:
                    lines.append(f"**Line {v.line}:{v.column}** [{v.severity.upper()}]")
                    lines.append(f"- **Found**: `{v.found_value}`")
                    lines.append(f"- **Expected**: `{v.expected_token}`")
                    lines.append(f"- **Context**: `{v.context}`")
                    lines.append(f"- **Auto-fixable**: {'Yes' if v.auto_fixable else 'No'}")
                    lines.append("")

        return '\n'.join(lines)

    def auto_fix(self, dry_run: bool = True) -> Dict[str, int]:
        """Auto-fix violations where possible."""
        fixes_by_file: Dict[str, List[Violation]] = {}
        for v in self.violations:
            if v.auto_fixable:
                fixes_by_file.setdefault(v.file, []).append(v)

        results = {"fixed": 0, "skipped": 0, "errors": 0}

        for file_path_str, violations in fixes_by_file.items():
            file_path = Path(file_path_str)
            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content

                # Sort by position (reverse to maintain indices)
                violations.sort(key=lambda v: (v.line, v.column), reverse=True)

                for v in violations:
                    # Simple string replacement
                    if v.found_value in content:
                        content = content.replace(v.found_value, v.expected_token, 1)
                        results["fixed"] += 1
                    else:
                        results["skipped"] += 1

                if not dry_run and content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                elif dry_run:
                    results["skipped"] += results["fixed"]
                    results["fixed"] = 0

            except Exception as e:
                print(f"Error fixing {file_path}: {e}", file=sys.stderr)
                results["errors"] += 1

        return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate design token compliance in source files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate-tokens.py --file Component.tsx --tokens tokens.json
  python validate-tokens.py --dir ./src --tokens tokens.json --output report.md
  python validate-tokens.py --file styles.css --tokens tokens.json --fix --dry-run
        """
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file', '-f', help='Single file to validate')
    group.add_argument('--dir', '-d', help='Directory to validate recursively')

    parser.add_argument('--tokens', '-t', required=True, help='Token definitions JSON file')
    parser.add_argument('--output', '-o', help='Output report file (default: stdout)')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown', help='Output format')
    parser.add_argument('--fix', action='store_true', help='Auto-fix violations')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed without applying')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')

    args = parser.parse_args()

    tokens_path = Path(args.tokens)
    if not tokens_path.exists():
        print(f"Error: Tokens file not found: {tokens_path}", file=sys.stderr)
        sys.exit(1)

    validator = TokenValidator(tokens_path)

    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found: {file_path}", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"Validating: {file_path}")
        violations = validator.validate_file(file_path, fix=args.fix)
    else:
        dir_path = Path(args.dir)
        if not dir_path.exists():
            print(f"Error: Directory not found: {dir_path}", file=sys.stderr)
            sys.exit(1)

        if args.verbose:
            print(f"Validating directory: {dir_path}")
        violations = validator.validate_directory(dir_path)

    # Auto-fix if requested
    if args.fix:
        if args.verbose:
            print("Applying auto-fixes...")
        results = validator.auto_fix(dry_run=args.dry_run)
        print(f"\n🔧 Fix results: {results['fixed']} fixed, {results['skipped']} skipped, {results['errors']} errors")

    # Generate report
    report = validator.generate_report(args.format)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report written to: {output_path}")
    else:
        print(report)

    # Summary
    error_count = sum(1 for v in violations if v.severity == 'error')
    warning_count = sum(1 for v in violations if v.severity == 'warning')

    print(f"\n[STATS] Summary:", file=sys.stderr)
    print(f"   Total violations: {len(violations)}", file=sys.stderr)
    print(f"   [CRITICAL] Errors: {error_count}", file=sys.stderr)
    print(f"   [MAJOR] Warnings: {warning_count}", file=sys.stderr)

    # Exit with error code if errors found
    if error_count > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()