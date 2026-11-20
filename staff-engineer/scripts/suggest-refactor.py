#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactoring Suggestion Engine — Analyzes code and suggests risk-assessed refactorings.
Based on the refactoring catalog with validation requirements.
"""

import argparse
import ast
import json
import os
import re
import sys
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RefactoringType(Enum):
    # Low risk — safe to auto-apply with tests
    EXTRACT_FUNCTION = "extract_function"
    EXTRACT_VARIABLE = "extract_variable"
    RENAME_SYMBOL = "rename_symbol"
    REMOVE_DEAD_CODE = "remove_dead_code"
    SIMPLIFY_CONDITIONAL = "simplify_conditional"
    REPLACE_MAGIC_NUMBER = "replace_magic_number"
    CONVERT_TO_FSTRING = "convert_to_fstring"  # Python
    USE_COLLECTION_METHOD = "use_collection_method"  # .map/.filter/.reduce

    # Medium risk — needs review, tests must pass
    EXTRACT_CLASS = "extract_class"
    MOVE_METHOD = "move_method"
    REPLACE_CONDITIONAL_WITH_POLYMORPHISM = "replace_conditional_with_polymorphism"
    INTRODUCE_PARAMETER_OBJECT = "introduce_parameter_object"
    REPLACE_PRIMITIVE_WITH_OBJECT = "replace_primitive_with_object"
    SPLIT_LOOP = "split_loop"
    REPLACE_LOOP_WITH_PIPELINE = "replace_loop_with_pipeline"
    EXTRACT_INTERFACE = "extract_interface"

    # High risk — architectural, needs ADR, extensive testing
    DECOMPOSE_SERVICE = "decompose_service"
    CHANGE_MODULE_BOUNDARY = "change_module_boundary"
    INTRODUCE_EVENT_DRIVEN = "introduce_event_driven"
    MIGRATE_DATABASE_SCHEMA = "migrate_database_schema"
    REPLACE_SYNC_WITH_ASYNC = "replace_sync_with_async"
    STRANGLER_FIG_MIGRATION = "strangler_fig_migration"


@dataclass
class RefactoringSuggestion:
    type: RefactoringType
    risk: RiskLevel
    file: str
    line_start: int
    line_end: int
    description: str
    rationale: str
    effort: str  # "minutes" | "hours" | "days"
    validation_required: List[str]
    code_before: str
    code_after: str
    confidence: float  # 0.0 - 1.0


class CodeAnalyzer:
    """Language-agnostic pattern detector for refactoring opportunities."""

    def __init__(self):
        self.suggestions: List[RefactoringSuggestion] = []

    def analyze_file(self, path: Path) -> List[RefactoringSuggestion]:
        self.suggestions = []
        content = path.read_text(encoding="utf-8")
        lines = content.split("\n")

        if path.suffix == ".py":
            self._analyze_python(path, content, lines)
        elif path.suffix in (".ts", ".tsx", ".js", ".jsx"):
            self._analyze_typescript(path, content, lines)
        elif path.suffix == ".go":
            self._analyze_go(path, content, lines)
        elif path.suffix == ".rs":
            self._analyze_rust(path, content, lines)
        elif path.suffix == ".java":
            self._analyze_java(path, content, lines)

        # Universal patterns
        self._analyze_universal(path, content, lines)

        return self.suggestions

    def _add_suggestion(self, suggestion: RefactoringSuggestion):
        self.suggestions.append(suggestion)

    def _get_snippet(self, lines: List[str], start: int, end: int, context: int = 2) -> str:
        s = max(0, start - context)
        e = min(len(lines), end + context)
        return "\n".join(lines[s:e])

    # --- Python ---
    def _analyze_python(self, path: Path, content: str, lines: List[str]):
        try:
            tree = ast.parse(content)
        except SyntaxError:
            return

        for node in ast.walk(tree):
            # Long function (>50 lines)
            if isinstance(node, ast.FunctionDef):
                if node.end_lineno and node.end_lineno - node.lineno > 50:
                    self._add_suggestion(RefactoringSuggestion(
                        type=RefactoringType.EXTRACT_FUNCTION,
                        risk=RiskLevel.LOW,
                        file=str(path),
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        description=f"Function '{node.name}' is {node.end_lineno - node.lineno} lines (max 50)",
                        rationale="Long functions hurt readability, testability, and reuse",
                        effort="minutes",
                        validation_required=["unit tests pass", "cyclomatic complexity reduced"],
                        code_before=self._get_snippet(lines, node.lineno - 1, node.end_lineno or node.lineno),
                        code_after=f"# Extract logical blocks into helper functions\n# def {node.name}_part1():\n#     ...\n# def {node.name}_part2():\n#     ...",
                        confidence=0.85,
                    ))

            # Magic numbers
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in (0, 1, -1, 2, 10, 100, 1000):
                    # Check if it's in a context that suggests a constant
                    parent = getattr(node, 'parent', None)
                    if not isinstance(parent, (ast.Call, ast.Subscript, ast.Attribute)):
                        self._add_suggestion(RefactoringSuggestion(
                            type=RefactoringType.REPLACE_MAGIC_NUMBER,
                            risk=RiskLevel.LOW,
                            file=str(path),
                            line_start=node.lineno,
                            line_end=node.lineno,
                            description=f"Magic number {node.value} should be a named constant",
                            rationale="Named constants improve readability and maintainability",
                            effort="minutes",
                            validation_required=["tests pass", "constant named appropriately"],
                            code_before=self._get_snippet(lines, node.lineno - 1, node.lineno),
                            code_after=f"# CONSTANT_NAME = {node.value}\n# ... = CONSTANT_NAME",
                            confidence=0.7,
                        ))

            # Long parameter list (>4 params)
            if isinstance(node, ast.FunctionDef):
                args = node.args
                param_count = len(args.args) + len(args.kwonlyargs)
                if param_count > 4:
                    self._add_suggestion(RefactoringSuggestion(
                        type=RefactoringType.INTRODUCE_PARAMETER_OBJECT,
                        risk=RiskLevel.MEDIUM,
                        file=str(path),
                        line_start=node.lineno,
                        line_end=node.lineno,
                        description=f"Function '{node.name}' has {param_count} parameters (max 4)",
                        rationale="Parameter objects reduce coupling and improve clarity",
                        effort="hours",
                        validation_required=["tests pass", "callers updated", "new type documented"],
                        code_before=self._get_snippet(lines, node.lineno - 1, node.lineno),
                        code_after=f"# class {node.name}Params:\n#     def __init__(self, ...):\n#         ...\n# def {node.name}(params: {node.name}Params):",
                        confidence=0.75,
                    ))

    # --- TypeScript/JavaScript ---
    def _analyze_typescript(self, path: Path, content: str, lines: List[str]):
        # Long function
        func_pattern = re.compile(r"(export\s+)?(async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{", re.MULTILINE)
        for match in func_pattern.finditer(content):
            start_line = content[:match.start()].count("\n")
            # Find matching brace (simplified)
            brace_count = 0
            end_line = start_line
            for i, line in enumerate(lines[start_line:], start_line):
                brace_count += line.count("{") - line.count("}")
                if brace_count == 0 and i > start_line:
                    end_line = i
                    break
            if end_line - start_line > 50:
                self._add_suggestion(RefactoringSuggestion(
                    type=RefactoringType.EXTRACT_FUNCTION,
                    risk=RiskLevel.LOW,
                    file=str(path),
                    line_start=start_line + 1,
                    line_end=end_line + 1,
                    description=f"Function is {end_line - start_line} lines (max 50)",
                    rationale="Long functions hurt readability and testability",
                    effort="minutes",
                    validation_required=["tests pass", "complexity reduced"],
                    code_before=self._get_snippet(lines, start_line, end_line),
                    code_after="// Extract into smaller functions\n// function helper1() { ... }\n// function helper2() { ... }",
                    confidence=0.8,
                ))

        # Magic numbers/strings
        magic_pattern = re.compile(r"(?<![\w\.])(\d{2,}|\"[^\"]{3,}\"|'[^']{3,}')(?!.*=)")
        for match in magic_pattern.finditer(content):
            line_num = content[:match.start()].count("\n")
            val = match.group(1)
            if val.isdigit() and int(val) not in (0, 1, -1, 2, 10, 100, 1000):
                self._add_suggestion(RefactoringSuggestion(
                    type=RefactoringType.REPLACE_MAGIC_NUMBER,
                    risk=RiskLevel.LOW,
                    file=str(path),
                    line_start=line_num + 1,
                    line_end=line_num + 1,
                    description=f"Magic value {val} should be a named constant",
                    rationale="Named constants improve maintainability",
                    effort="minutes",
                    validation_required=["tests pass"],
                    code_before=self._get_snippet(lines, line_num, line_num),
                    code_after=f"// const CONSTANT_NAME = {val};\n// ... = CONSTANT_NAME;",
                    confidence=0.65,
                ))

    # --- Go ---
    def _analyze_go(self, path: Path, content: str, lines: List[str]):
        # Long function
        func_pattern = re.compile(r"func\s+(?:\(\w+\s+\*?\w+\)\s+)?(\w+)\s*\([^)]*\)\s*(?:\(\w+\s+\w+\)\s*)?\{", re.MULTILINE)
        for match in func_pattern.finditer(content):
            start_line = content[:match.start()].count("\n")
            brace_count = 0
            end_line = start_line
            for i, line in enumerate(lines[start_line:], start_line):
                brace_count += line.count("{") - line.count("}")
                if brace_count == 0 and i > start_line:
                    end_line = i
                    break
            if end_line - start_line > 50:
                self._add_suggestion(RefactoringSuggestion(
                    type=RefactoringType.EXTRACT_FUNCTION,
                    risk=RiskLevel.LOW,
                    file=str(path),
                    line_start=start_line + 1,
                    line_end=end_line + 1,
                    description=f"Function '{match.group(1)}' is {end_line - start_line} lines (max 50)",
                    rationale="Long functions hurt readability and testability",
                    effort="minutes",
                    validation_required=["tests pass", "go vet passes"],
                    code_before=self._get_snippet(lines, start_line, end_line),
                    code_after="// func helper1() { ... }\n// func helper2() { ... }",
                    confidence=0.8,
                ))

    # --- Rust ---
    def _analyze_rust(self, path: Path, content: str, lines: List[str]):
        # Long function
        func_pattern = re.compile(r"fn\s+(\w+)\s*\([^)]*\)\s*(?:->\s*\w+)?\s*\{", re.MULTILINE)
        for match in func_pattern.finditer(content):
            start_line = content[:match.start()].count("\n")
            brace_count = 0
            end_line = start_line
            for i, line in enumerate(lines[start_line:], start_line):
                brace_count += line.count("{") - line.count("}")
                if brace_count == 0 and i > start_line:
                    end_line = i
                    break
            if end_line - start_line > 50:
                self._add_suggestion(RefactoringSuggestion(
                    type=RefactoringType.EXTRACT_FUNCTION,
                    risk=RiskLevel.LOW,
                    file=str(path),
                    line_start=start_line + 1,
                    line_end=end_line + 1,
                    description=f"Function '{match.group(1)}' is {end_line - start_line} lines (max 50)",
                    rationale="Long functions hurt readability",
                    effort="minutes",
                    validation_required=["cargo test passes", "clippy clean"],
                    code_before=self._get_snippet(lines, start_line, end_line),
                    code_after="// fn helper1() { ... }\n// fn helper2() { ... }",
                    confidence=0.8,
                ))

    # --- Java ---
    def _analyze_java(self, path: Path, content: str, lines: List[str]):
        # Long method
        method_pattern = re.compile(r"(public|private|protected)?\s+(static\s+)?\w+\s+(\w+)\s*\([^)]*\)\s*(?:throws\s+\w+)?\s*\{", re.MULTILINE)
        for match in method_pattern.finditer(content):
            start_line = content[:match.start()].count("\n")
            brace_count = 0
            end_line = start_line
            for i, line in enumerate(lines[start_line:], start_line):
                brace_count += line.count("{") - line.count("}")
                if brace_count == 0 and i > start_line:
                    end_line = i
                    break
            if end_line - start_line > 50:
                self._add_suggestion(RefactoringSuggestion(
                    type=RefactoringType.EXTRACT_FUNCTION,
                    risk=RiskLevel.LOW,
                    file=str(path),
                    line_start=start_line + 1,
                    line_end=end_line + 1,
                    description=f"Method '{match.group(3)}' is {end_line - start_line} lines (max 50)",
                    rationale="Long methods hurt readability and testability",
                    effort="minutes",
                    validation_required=["tests pass", "checkstyle clean"],
                    code_before=self._get_snippet(lines, start_line, end_line),
                    code_after="// private void helper1() { ... }\n// private void helper2() { ... }",
                    confidence=0.8,
                ))

    # --- Universal ---
    def _analyze_universal(self, path: Path, content: str, lines: List[str]):
        # TODO/FIXME comments
        for i, line in enumerate(lines):
            if re.search(r"(TODO|FIXME|HACK|XXX)", line, re.IGNORECASE):
                self._add_suggestion(RefactoringSuggestion(
                    type=RefactoringType.REMOVE_DEAD_CODE,
                    risk=RiskLevel.LOW,
                    file=str(path),
                    line_start=i + 1,
                    line_end=i + 1,
                    description=f"Technical debt marker: {line.strip()}",
                    rationale="Track technical debt in issue tracker, not code comments",
                    effort="minutes",
                    validation_required=["issue created", "comment removed or linked"],
                    code_before=line.strip(),
                    code_after="// See issue #XXX",
                    confidence=0.9,
                ))

        # Duplicated code blocks (simple detection)
        # This is a placeholder - real implementation would use AST diffing
        pass


class RefactoringEngine:
    def __init__(self, root: Path):
        self.root = root
        self.analyzer = CodeAnalyzer()

    def scan(self, paths: List[Path] = None, min_risk: RiskLevel = RiskLevel.LOW) -> List[RefactoringSuggestion]:
        all_suggestions = []
        targets = paths or list(self.root.rglob("*"))

        for path in targets:
            if not path.is_file():
                continue
            if path.suffix not in (".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java"):
                continue
            if any(part.startswith(".") for part in path.parts):
                continue
            if "node_modules" in path.parts or "target" in path.parts or "__pycache__" in path.parts:
                continue
            if "vendor" in path.parts or "dist" in path.parts or "build" in path.parts:
                continue

            suggestions = self.analyzer.analyze_file(path)
            filtered = [s for s in suggestions if self._risk_priority(s.risk) >= self._risk_priority(min_risk)]
            all_suggestions.extend(filtered)

        # Sort by risk (high first), then confidence
        all_suggestions.sort(key=lambda s: (-self._risk_priority(s.risk), -s.confidence))
        return all_suggestions

    def _risk_priority(self, risk: RiskLevel) -> int:
        return {"low": 1, "medium": 2, "high": 3}[risk.value]

    def generate_report(self, suggestions: List[RefactoringSuggestion], format: str = "markdown") -> str:
        if format == "json":
            return json.dumps([asdict(s) for s in suggestions], indent=2, default=str)

        # Group by risk
        by_risk = {"high": [], "medium": [], "low": []}
        for s in suggestions:
            by_risk[s.risk.value].append(s)

        lines = ["# Refactoring Suggestions\n"]
        for risk in ["high", "medium", "low"]:
            items = by_risk[risk]
            if not items:
                continue
            lines.append(f"## {risk.title()} Risk ({len(items)})")
            for s in items:
                lines.append(f"\n### {s.type.value.replace('_', ' ').title()} — {s.file}:{s.line_start}")
                lines.append(f"**Confidence**: {s.confidence:.0%} | **Effort**: {s.effort}")
                lines.append(f"**Description**: {s.description}")
                lines.append(f"**Rationale**: {s.rationale}")
                lines.append(f"**Validation Required**: {', '.join(s.validation_required)}")
                lines.append(f"**Before**:\n```\n{s.code_before}\n```")
                lines.append(f"**After**:\n```\n{s.code_after}\n```")
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Suggest refactorings with risk assessment")
    parser.add_argument("paths", nargs="*", default=["."], help="Files or directories to analyze")
    parser.add_argument("--min-risk", choices=["low", "medium", "high"], default="low", help="Minimum risk level to report")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    args = parser.parse_args()

    root = Path(args.paths[0]).resolve() if args.paths else Path.cwd()
    engine = RefactoringEngine(root)

    target_paths = [Path(p).resolve() for p in args.paths]
    min_risk = RiskLevel(args.min_risk)

    suggestions = engine.scan(target_paths, min_risk)
    report = engine.generate_report(suggestions, args.format)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)


if __name__ == "__main__":
    main()