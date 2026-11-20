#!/usr/bin/env python3
"""
Architecture Analyzer — Coupling, Cycles, Boundaries, Hotspots

Language-agnostic architecture analysis for any codebase.
Detects module boundaries, dependency violations, complexity hotspots.

Usage:
    python analyze-architecture.py --dir ./src --fail-on cycles,boundaries
    python analyze-architecture.py --dir . --layers domain,application,adapters --diagram arch.mmd
    python analyze-architecture.py --dir ./src --max-cyclomatic 10 --max-cognitive 15
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib


@dataclass
class Module:
    name: str
    path: str
    language: str
    files: List[str]
    loc: int
    complexity: Dict[str, float]  # cyclomatic, cognitive, etc.
    dependencies: List[str]  # modules this depends on
    dependents: List[str]  # modules that depend on this
    layer: str = ""


@dataclass
class Violation:
    type: str  # cycle, boundary, forbidden, complexity
    severity: str  # critical, high, medium, low
    message: str
    module: str
    details: Dict[str, Any] = None


class ArchitectureAnalyzer:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.modules: Dict[str, Module] = {}
        self.violations: List[Violation] = []
        self.layer_rules: Dict[str, List[str]] = {}
        self.forbidden_patterns: List[re.Pattern] = []
        self.max_cyclomatic = 10
        self.max_cognitive = 15
        self.max_nesting = 3

    def analyze(self, 
                layer_rules: Dict[str, List[str]] = None,
                forbidden_imports: List[str] = None,
                max_cyclomatic: int = 10,
                max_cognitive: int = 15,
                max_nesting: int = 3) -> List[Violation]:
        """Run full architecture analysis."""
        self.layer_rules = layer_rules or {}
        self.forbidden_patterns = [re.compile(p) for p in (forbidden_imports or [])]
        self.max_cyclomatic = max_cyclomatic
        self.max_cognitive = max_cognitive
        self.max_nesting = max_nesting

        self.violations = []
        
        # 1. Discover modules
        self._discover_modules()
        
        # 2. Analyze dependencies
        self._analyze_dependencies()
        
        # 3. Check for cycles
        self._check_cycles()
        
        # 4. Check layer boundaries
        if self.layer_rules:
            self._check_layer_boundaries()
        
        # 5. Check forbidden imports
        if self.forbidden_patterns:
            self._check_forbidden_imports()
        
        # 6. Check complexity
        self._check_complexity()
        
        # 7. Calculate coupling metrics
        self._calculate_coupling_metrics()
        
        return self.violations

    def _discover_modules(self):
        """Discover modules from directory structure."""
        # Language detection by file extensions
        lang_exts = {
            '.go': 'go', '.rs': 'rust', '.py': 'python',
            '.ts': 'typescript', '.tsx': 'typescript', '.js': 'javascript', '.jsx': 'javascript',
            '.java': 'java', '.kt': 'kotlin', '.cs': 'csharp',
            '.php': 'php', '.rb': 'ruby', '.swift': 'swift',
            '.cpp': 'cpp', '.cc': 'cpp', '.c': 'c', '.h': 'c',
        }
        
        # Find module roots (directories with source files)
        module_dirs = set()
        for ext, lang in lang_exts.items():
            for file_path in self.repo_path.rglob(f'*{ext}'):
                # Skip vendor, node_modules, target, build, dist, .git
                parts = file_path.relative_to(self.repo_path).parts
                if any(skip in parts for skip in ['vendor', 'node_modules', 'target', 'build', 'dist', '.git', '__pycache__', '.venv', 'venv']):
                    continue
                # Module is the first directory level (or first two for monorepos)
                if len(parts) >= 2:
                    module_dirs.add(parts[0])
                elif len(parts) == 1:
                    module_dirs.add('.')
        
        # Build modules
        for module_dir in sorted(module_dirs):
            module_path = self.repo_path / module_dir
            if not module_path.is_dir():
                continue
            
            files = []
            loc = 0
            lang = None
            for ext, l in lang_exts.items():
                for f in module_path.rglob(f'*{ext}'):
                    if f.is_file():
                        files.append(str(f.relative_to(self.repo_path)))
                        try:
                            content = f.read_text(encoding='utf-8', errors='ignore')
                            loc += len(content.splitlines())
                            if lang is None:
                                lang = l
                        except Exception:
                            pass
            
            if files:
                # Determine layer from path
                layer = self._infer_layer(module_dir)
                self.modules[module_dir] = Module(
                    name=module_dir,
                    path=str(module_path.relative_to(self.repo_path)),
                    language=lang or 'unknown',
                    files=files,
                    loc=loc,
                    complexity={},
                    dependencies=[],
                    dependents=[],
                    layer=layer,
                )

    def _infer_layer(self, module_name: str) -> str:
        """Infer architectural layer from module name/path."""
        name = module_name.lower()
        if any(x in name for x in ['domain', 'core', 'entities', 'models', 'kernel']):
            return 'domain'
        elif any(x in name for x in ['application', 'usecase', 'service', 'handler', 'command', 'query']):
            return 'application'
        elif any(x in name for x in ['adapter', 'infrastructure', 'persistence', 'repository', 'gateway', 'external', 'api', 'controller', 'cli']):
            return 'adapters'
        elif any(x in name for x in ['app', 'main', 'cmd', 'server', 'worker', 'consumer']):
            return 'apps'
        elif any(x in name for x in ['shared', 'common', 'lib', 'util', 'pkg']):
            return 'shared'
        return 'unknown'

    def _analyze_dependencies(self):
        """Analyze import dependencies between modules."""
        # Language-specific import patterns
        import_patterns = {
            'go': [r'import\s+\(([^)]+)\)', r'import\s+"([^"]+)"'],
            'rust': [r'use\s+([^;]+);', r'extern\s+crate\s+(\w+)'],
            'python': [r'^import\s+([\w.]+)', r'^from\s+([\w.]+)\s+import'],
            'typescript': [r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]', r'import\s*\([\'"]'],
            'javascript': [r'import\s+.*\s+from\s+[\'"]([^\'"]+)[\'"]', r'require\s*\(\s*[\'"]([^\'"]+)[\'"]'],
            'java': [r'import\s+([\w.]+);'],
            'kotlin': [r'import\s+([\w.]+)'],
            'csharp': [r'using\s+([\w.]+);'],
            'rust': [r'use\s+([^;]+);'],
        }
        
        # Map external package to internal module
        module_prefixes = {name: name.split('/')[0] for name in self.modules.keys()}
        
        for module_name, module in self.modules.items():
            deps = set()
            lang = module.language
            patterns = import_patterns.get(lang, [])
            
            for file_rel in module.files:
                file_path = self.repo_path / file_rel
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    for pattern in patterns:
                        for match in re.finditer(pattern, content, re.MULTILINE):
                            imp = match.group(1) if match.groups() else match.group(0)
                            # Check if import maps to internal module
                            for prefix, mod_name in module_prefixes.items():
                                if imp.startswith(prefix) and mod_name != module_name:
                                    deps.add(mod_name)
                                    break
                except Exception:
                    pass
            
            module.dependencies = sorted(deps)
            for dep in deps:
                if dep in self.modules:
                    self.modules[dep].dependents.append(module_name)

    def _check_cycles(self):
        """Detect circular dependencies using Tarjan's algorithm."""
        # Build adjacency list
        graph = {name: set(m.dependencies) for name, m in self.modules.items()}
        
        # Tarjan's SCC algorithm
        index = 0
        stack = []
        on_stack = set()
        indices = {}
        lowlinks = {}
        sccs = []
        
        def strongconnect(v: str):
            nonlocal index
            indices[v] = index
            lowlinks[v] = index
            index += 1
            stack.append(v)
            on_stack.add(v)
            
            for w in graph.get(v, []):
                if w not in indices:
                    strongconnect(w)
                    lowlinks[v] = min(lowlinks[v], lowlinks[w])
                elif w in on_stack:
                    lowlinks[v] = min(lowlinks[v], indices[w])
            
            if lowlinks[v] == indices[v]:
                scc = []
                while True:
                    w = stack.pop()
                    on_stack.remove(w)
                    scc.append(w)
                    if w == v:
                        break
                if len(scc) > 1:
                    sccs.append(scc)
        
        for v in graph:
            if v not in indices:
                strongconnect(v)
        
        for scc in sccs:
            self.violations.append(Violation(
                type='cycle',
                severity='high',
                message=f'Circular dependency detected: {" -> ".join(scc)} -> {scc[0]}',
                module=', '.join(scc),
                details={'cycle': scc, 'modules': scc},
            ))

    def _check_layer_boundaries(self):
        """Check that layer dependencies follow rules."""
        # Build allowed dependencies from layer rules
        allowed = defaultdict(set)
        for layer, allowed_layers in self.layer_rules.items():
            allowed[layer] = set(allowed_layers)
        
        # Check each module's dependencies
        for module_name, module in self.modules.items():
            if not module.layer or module.layer not in allowed:
                continue
            
            for dep_name in module.dependencies:
                if dep_name not in self.modules:
                    continue
                dep = self.modules[dep_name]
                if not dep.layer:
                    continue
                
                if dep.layer not in allowed[module.layer]:
                    self.violations.append(Violation(
                        type='boundary',
                        severity='high',
                        message=f'Layer violation: {module.layer} module "{module_name}" depends on {dep.layer} module "{dep_name}"',
                        module=module_name,
                        details={
                            'source_layer': module.layer,
                            'target_layer': dep.layer,
                            'source_module': module_name,
                            'target_module': dep_name,
                            'allowed': list(allowed[module.layer]),
                        },
                    ))

    def _check_forbidden_imports(self):
        """Check for forbidden import patterns."""
        for module_name, module in self.modules.items():
            for file_rel in module.files:
                file_path = self.repo_path / file_rel
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    lines = content.splitlines()
                    for i, line in enumerate(lines, 1):
                        for pattern in self.forbidden_patterns:
                            if pattern.search(line):
                                self.violations.append(Violation(
                                    type='forbidden',
                                    severity='medium',
                                    message=f'Forbidden import pattern: {pattern.pattern}',
                                    module=module_name,
                                    details={
                                        'file': file_rel,
                                        'line': i,
                                        'pattern': pattern.pattern,
                                        'snippet': line.strip()[:200],
                                    },
                                ))
                except Exception:
                    pass

    def _check_complexity(self):
        """Check cyclomatic and cognitive complexity."""
        # Language-specific complexity analysis
        for module_name, module in self.modules.items():
            for file_rel in module.files:
                file_path = self.repo_path / file_rel
                try:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    # Use external tools if available
                    complexity = self._calculate_complexity(content, module.language, file_rel)
                    module.complexity[file_rel] = complexity
                    
                    if complexity.get('cyclomatic', 0) > self.max_cyclomatic:
                        self.violations.append(Violation(
                            type='complexity',
                            severity='medium',
                            message=f'Cyclomatic complexity {complexity["cyclomatic"]} exceeds limit {self.max_cyclomatic}',
                            module=module_name,
                            details={
                                'file': file_rel,
                                'cyclomatic': complexity['cyclomatic'],
                                'limit': self.max_cyclomatic,
                            },
                        ))
                    
                    if complexity.get('cognitive', 0) > self.max_cognitive:
                        self.violations.append(Violation(
                            type='complexity',
                            severity='medium',
                            message=f'Cognitive complexity {complexity["cognitive"]} exceeds limit {self.max_cognitive}',
                            module=module_name,
                            details={
                                'file': file_rel,
                                'cognitive': complexity['cognitive'],
                                'limit': self.max_cognitive,
                            },
                        ))
                    
                    if complexity.get('nesting', 0) > self.max_nesting:
                        self.violations.append(Violation(
                            type='complexity',
                            severity='low',
                            message=f'Max nesting depth {complexity["nesting"]} exceeds limit {self.max_nesting}',
                            module=module_name,
                            details={
                                'file': file_rel,
                                'nesting': complexity['nesting'],
                                'limit': self.max_nesting,
                            },
                        ))
                except Exception:
                    pass

    def _calculate_complexity(self, content: str, language: str, file_path: str) -> Dict[str, float]:
        """Calculate complexity metrics for a file."""
        # Simplified complexity calculation
        # In production, use proper tools: gocyclo, radon, eslint, etc.
        
        lines = content.splitlines()
        cyclomatic = 1  # Base complexity
        cognitive = 0
        nesting = 0
        max_nesting = 0
        current_nesting = 0
        
        # Language-specific keywords that increase complexity
        complexity_keywords = {
            'go': ['if', 'for', 'switch', 'case', 'select', '&&', '||', '?'],
            'rust': ['if', 'for', 'while', 'loop', 'match', '&&', '||', '?'],
            'python': ['if', 'for', 'while', 'try', 'except', 'elif', 'and', 'or'],
            'typescript': ['if', 'for', 'while', 'switch', 'case', 'catch', '&&', '||', '?'],
            'javascript': ['if', 'for', 'while', 'switch', 'case', 'catch', '&&', '||', '?'],
            'java': ['if', 'for', 'while', 'switch', 'case', 'catch', '&&', '||', '?'],
            'kotlin': ['if', 'for', 'while', 'when', 'catch', '&&', '||', '?'],
            'csharp': ['if', 'for', 'while', 'switch', 'case', 'catch', '&&', '||', '?'],
        }
        
        keywords = complexity_keywords.get(self._normalize_lang(language), complexity_keywords['python'])
        
        for line in content.splitlines():
            stripped = line.strip()
            # Skip comments
            if stripped.startswith('//') or stripped.startswith('#') or stripped.startswith('/*'):
                continue
            
            # Count complexity keywords
            for kw in keywords:
                # Simple word boundary check
                count = len(re.findall(rf'\b{re.escape(kw)}\b', stripped))
                cyclomatic += count
                cognitive += count * 1.5  # Cognitive weight
            
            # Track nesting (indentation-based)
            indent = len(line) - len(line.lstrip())
            if indent > 0:
                current_nesting = indent // 2  # Assume 2-space indent
                max_nesting = max(max_nesting, current_nesting)
            else:
                current_nesting = 0
        
        return {
            'cyclomatic': cyclomatic,
            'cognitive': round(cognitive, 1),
            'nesting': max_nesting,
            'loc': len(lines),
        }

    def _normalize_lang(self, lang: str) -> str:
        lang = lang.lower()
        if lang in ('ts', 'tsx', 'javascript', 'js', 'jsx'):
            return 'typescript'
        return lang

    def _calculate_coupling_metrics(self):
        """Calculate coupling metrics for each module."""
        for module_name, module in self.modules.items():
            ca = len(module.dependents)  # Afferent coupling
            ce = len(module.dependencies)  # Efferent coupling
            total = ca + ce
            instability = ce / total if total > 0 else 0
            
            # Abstractness would need interface detection - simplified
            abstractness = 0.0
            
            # Distance from main sequence
            distance = abs(instability + abstractness - 1) / (2 ** 0.5)
            
            module.complexity['_coupling'] = {
                'afferent': ca,
                'efferent': ce,
                'instability': round(instability, 2),
                'abstractness': round(abstractness, 2),
                'distance_from_main_sequence': round(distance, 2),
            }
            
            # Flag high instability for stable layers
            if module.layer in ('domain', 'application') and instability > 0.3:
                self.violations.append(Violation(
                    type='coupling',
                    severity='medium',
                    message=f'{module.layer} module "{module_name}" has high instability ({instability:.2f})',
                    module=module_name,
                    details={
                        'instability': round(instability, 2),
                        'afferent': ca,
                        'efferent': ce,
                        'recommendation': 'Stable layers should have low instability (<0.3)',
                    },
                ))

    def generate_diagram(self, format: str = 'mermaid') -> str:
        """Generate architecture diagram."""
        if format == 'mermaid':
            lines = ['```mermaid', 'graph TD']
            
            # Group by layer
            layers = defaultdict(list)
            for name, module in self.modules.items():
                layers[module.layer or 'unknown'].append(name)
            
            # Define subgraphs for layers
            layer_order = ['domain', 'application', 'adapters', 'apps', 'shared', 'unknown']
            for i, layer in enumerate(layer_order):
                if layer in layers and layers[layer]:
                    lines.append(f'    subgraph {layer.upper()}["{layer.title()} Layer"]')
                    for module in layers[layer]:
                        lines.append(f'        {self._sanitize(module)}["{module}"]')
                    lines.append('    end')
            
            # Add dependencies
            for name, module in self.modules.items():
                for dep in module.dependencies:
                    if dep in self.modules:
                        lines.append(f'    {self._sanitize(name)} --> {self._sanitize(dep)}')
            
            lines.append('```')
            return '\n'.join(lines)
        
        return 'Unsupported format'

    def _sanitize(self, name: str) -> str:
        return re.sub(r'[^a-zA-Z0-9_]', '_', name)

    def generate_report(self, format: str = 'markdown') -> str:
        if format == 'json':
            return json.dumps({
                'modules': {name: asdict(m) for name, m in self.modules.items()},
                'violations': [asdict(v) for v in self.violations],
            }, indent=2, default=str)
        
        lines = [
            "# Architecture Analysis Report",
            "",
            f"**Modules analyzed**: {len(self.modules)}",
            f"**Violations found**: {len(self.violations)}",
            "",
        ]
        
        # Summary by layer
        layer_counts = defaultdict(int)
        for m in self.modules.values():
            layer_counts[m.layer or 'unknown'] += 1
        
        lines.append("## Module Layers")
        for layer, count in sorted(layer_counts.items()):
            lines.append(f"- **{layer}**: {count} modules")
        lines.append("")
        
        # Violations by type
        by_type = defaultdict(list)
        for v in self.violations:
            by_type[v.type].append(v)
        
        for vtype, violations in sorted(by_type.items()):
            lines.append(f"## {vtype.title()} Violations ({len(violations)})")
            lines.append("")
            
            for v in violations:
                severity_emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(v.severity, '⚪')
                lines.append(f"### {severity_emoji} {v.severity.upper()}: {v.message}")
                lines.append(f"**Module**: `{v.module}`")
                if v.details:
                    for k, val in v.details.items():
                        if isinstance(val, (list, dict)):
                            lines.append(f"**{k}**: ```json\n{json.dumps(val, indent=2)}\n```")
                        else:
                            lines.append(f"**{k}**: {val}")
                lines.append("")
        
        # Architecture diagram
        lines.append("## Architecture Diagram")
        lines.append(self.generate_diagram('mermaid'))
        
        return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze architecture: coupling, cycles, boundaries, complexity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze-architecture.py --dir ./src --fail-on cycles,boundaries
  python analyze-architecture.py --dir . --layers domain,application,adapters --diagram arch.mmd
  python analyze-architecture.py --dir ./src --max-cyclomatic 10 --max-cognitive 15
        """
    )
    
    parser.add_argument('--dir', '-d', required=True, help='Directory to analyze')
    parser.add_argument('--layers', help='Layer rules as JSON: {"domain": ["shared"], "application": ["domain", "shared"]}')
    parser.add_argument('--forbidden', help='Comma-separated forbidden import patterns (regex)')
    parser.add_argument('--max-cyclomatic', type=int, default=10, help='Max cyclomatic complexity')
    parser.add_argument('--max-cognitive', type=int, default=15, help='Max cognitive complexity')
    parser.add_argument('--max-nesting', type=int, default=3, help='Max nesting depth')
    parser.add_argument('--diagram', help='Output diagram file (Mermaid)')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    parser.add_argument('--fail-on', help='Comma-separated violation types to fail on (cycles,boundaries,forbidden,complexity,coupling)')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    repo_path = Path(args.dir)
    if not repo_path.exists():
        print(f"Error: Directory not found: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    # Parse layer rules
    layer_rules = {}
    if args.layers:
        try:
            layer_rules = json.loads(args.layers)
        except json.JSONDecodeError as e:
            print(f"Error parsing layer rules: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Parse forbidden patterns
    forbidden = []
    if args.forbidden:
        forbidden = [p.strip() for p in args.forbidden.split(',')]
    
    # Parse fail-on
    fail_on = set()
    if args.fail_on:
        fail_on = set(f.strip() for f in args.fail_on.split(','))
    
    analyzer = ArchitectureAnalyzer(repo_path)
    violations = analyzer.analyze(
        layer_rules=layer_rules,
        forbidden_imports=forbidden,
        max_cyclomatic=args.max_cyclomatic,
        max_cognitive=args.max_cognitive,
        max_nesting=args.max_nesting,
    )
    
    if args.verbose:
        print(f"Analyzed {len(analyzer.modules)} modules")
        print(f"Found {len(violations)} violations")
    
    # Generate diagram if requested
    if args.diagram:
        diagram_path = Path(args.diagram)
        diagram_path.parent.mkdir(parents=True, exist_ok=True)
        diagram_path.write_text(analyzer.generate_diagram('mermaid'), encoding='utf-8')
        print(f"Diagram written to: {diagram_path}")
    
    # Generate report
    report = analyzer.generate_report(args.format)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    # Check fail-on
    violation_types = set(v.type for v in violations)
    if fail_on & violation_types:
        print(f"FAIL: Found violations of type: {fail_on & violation_types}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()