#!/usr/bin/env python3
"""
Performance Profiler — Benchmarks, Flame Graphs, Budgets

Language-agnostic performance profiling with CI/CD integration.

Usage:
    python profile-performance.py --dir ./src --budget latency:p99<200ms,throughput:>1000rps
    python profile-performance.py --command "go test -bench=." --output bench.json
    python profile-performance.py --baseline benchmarks/base.json --current benchmarks/current.json --threshold 5%
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class BenchmarkResult:
    name: str
    language: str
    metrics: Dict[str, float]  # metric -> value
    unit: Dict[str, str]  # metric -> unit
    iterations: int
    timestamp: str


@dataclass
class PerformanceBudget:
    metric: str
    operator: str  # <, >, <=, >=, ==
    threshold: float
    unit: str


class PerformanceProfiler:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.budgets: List[PerformanceBudget] = []
        self.results: List[BenchmarkResult] = []
        self.baseline: Dict[str, BenchmarkResult] = {}
    
    def parse_budget(self, budget_str: str) -> List[PerformanceBudget]:
        """Parse budget string like 'latency:p99<200ms,throughput:>1000rps'."""
        budgets = []
        for part in budget_str.split(','):
            part = part.strip()
            if not part:
                continue
            # Parse: metric:operator<valueunit
            match = re.match(r'(\w+):([<>]=?)(\d+(?:\.\d+)?)(\w*)', part)
            if match:
                metric, op, value, unit = match.groups()
                budgets.append(PerformanceBudget(
                    metric=metric,
                    operator=op,
                    threshold=float(value),
                    unit=unit or 'ms'
                ))
        self.budgets = budgets
        return budgets
    
    def run_benchmarks(self, command: str, language: str = None, 
                       iterations: int = 1) -> List[BenchmarkResult]:
        """Run benchmark command and parse results."""
        results = []
        
        for i in range(iterations):
            start = time.time()
            try:
                result = subprocess.run(
                    command, shell=True, cwd=self.repo_path,
                    capture_output=True, text=True, timeout=300
                )
                duration = time.time() - start
                
                # Parse output based on language
                metrics = self._parse_benchmark_output(result.stdout, language)
                metrics['duration_seconds'] = duration
                metrics['exit_code'] = float(result.returncode)
                
                results.append(BenchmarkResult(
                    name=f"benchmark_{i+1}",
                    language=language or self._detect_language(),
                    metrics=metrics,
                    unit=self._get_units(language),
                    iterations=1,
                    timestamp=time.strftime('%Y-%m-%dT%H:%M:%S')
                ))
            except subprocess.TimeoutExpired:
                print(f"Benchmark timeout (iteration {i+1})", file=sys.stderr)
            except Exception as e:
                print(f"Benchmark error: {e}", file=sys.stderr)
        
        self.results = results
        return results
    
    def _detect_language(self) -> str:
        """Detect primary language in repo."""
        lang_files = {
            'go': ['go.mod', '*.go'],
            'rust': ['Cargo.toml', '*.rs'],
            'python': ['pyproject.toml', 'requirements.txt', '*.py'],
            'typescript': ['tsconfig.json', 'package.json', '*.ts'],
            'javascript': ['package.json', '*.js'],
            'java': ['pom.xml', 'build.gradle', '*.java'],
            'kotlin': ['build.gradle.kts', '*.kt'],
            'python': ['pyproject.toml', '*.py'],
        }
        
        for lang, patterns in lang_files.items():
            for pattern in patterns:
                if list(self.repo_path.rglob(pattern)):
                    return lang
        return 'unknown'
    
    def _parse_benchmark_output(self, output: str, language: str) -> Dict[str, float]:
        """Parse benchmark output based on language."""
        metrics = {}
        
        # Go: go test -bench=. -benchmem
        if language == 'go':
            # BenchmarkXxx-8   	 1000000	      1234 ns/op	   567 B/op	     12 allocs/op
            for line in output.splitlines():
                match = re.match(r'Benchmark\w+\s+\d+\s+(\d+)\s+(\d+\.?\d*)\s+ns/op\s+(\d+\.?\d*)\s+B/op\s+(\d+\.?\d*)\s+allocs/op', line)
                if match:
                    name = line.split()[0]
                    metrics[f'{name}_ns_per_op'] = float(match.group(2))
                    metrics[f'{name}_bytes_per_op'] = float(match.group(3))
                    metrics[f'{name}_allocs_per_op'] = float(match.group(4))
        
        # Rust: cargo bench
        elif language == 'rust':
            # benchmark_name    time:   [1.2345 us 1.2345 us 1.2345 us]
            for line in output.splitlines():
                match = re.match(r'(\w+)\s+time:\s+\[([\d.]+)\s+(\w+)\s+([\d.]+)\s+(\w+)\s+([\d.]+)\s+(\w+)\]', line)
                if match:
                    name = match.group(1)
                    # Convert to ns
                    metrics[f'{name}_time_ns'] = self._convert_time(float(match.group(2)), match.group(3))
        
        # Python: pytest-benchmark
        elif language == 'python':
            # Name (time in ms)  Min    Max   Mean  StdDev  Median   IQR  Outliers  OPS  Rounds  Iterations
            in_table = False
            for line in output.splitlines():
                if 'Name' in line and 'Mean' in line:
                    in_table = True
                    continue
                if in_table and line.strip() and not line.startswith('-'):
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            name = parts[0]
                            mean_ms = float(parts[3])
                            metrics[f'{name}_mean_ms'] = mean_ms
                        except (ValueError, IndexError):
                            pass
        
        # Generic patterns (fallback)
        if not metrics:
            # Look for common patterns
            patterns = [
                (r'(\w+)[:\s]+(\d+\.?\d*)\s*(ms|us|ns|s)', lambda m: (m.group(1), self._convert_time(float(m.group(2)), m.group(3)))),
                (r'(\w+)[:\s]+(\d+\.?\d*)\s*(MB|KB|GB|B)', lambda m: (m.group(1), self._convert_bytes(float(m.group(2)), m.group(3)))),
                (r'(\w+)[:\s]+(\d+\.?\d*)\s*(rps|req/s|ops/s)', lambda m: (m.group(1), float(m.group(2)))),
            ]
            for line in output.splitlines():
                for pattern, extractor in patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        name, value = extractor(match)
                        metrics[name] = value
        
        return metrics
    
    def _convert_time(self, value: float, unit: str) -> float:
        """Convert time to nanoseconds."""
        unit = unit.lower()
        if unit in ('ns', 'nanosecond', 'nanoseconds'):
            return value
        elif unit in ('us', 'µs', 'microsecond', 'microseconds'):
            return value * 1_000
        elif unit in ('ms', 'millisecond', 'milliseconds'):
            return value * 1_000_000
        elif unit in ('s', 'sec', 'second', 'seconds'):
            return value * 1_000_000_000
        return value
    
    def _convert_bytes(self, value: float, unit: str) -> float:
        """Convert bytes to bytes."""
        unit = unit.upper()
        if unit in ('B', 'BYTES'):
            return value
        elif unit in ('KB', 'KIB'):
            return value * 1_024
        elif unit in ('MB', 'MIB'):
            return value * 1_024 * 1_024
        elif unit in ('GB', 'GIB'):
            return value * 1_024 * 1_024 * 1_024
        return value
    
    def _get_units(self, language: str) -> Dict[str, str]:
        """Get default units for metrics."""
        return {
            'ns_per_op': 'ns',
            'bytes_per_op': 'B',
            'allocs_per_op': 'count',
            'time_ns': 'ns',
            'mean_ms': 'ms',
            'duration_seconds': 's',
        }
    
    def load_baseline(self, baseline_path: Path) -> Dict[str, BenchmarkResult]:
        """Load baseline benchmark results."""
        with open(baseline_path) as f:
            data = json.load(f)
        
        self.baseline = {}
        for name, result_data in data.items():
            self.baseline[name] = BenchmarkResult(**result_data)
        
        return self.baseline
    
    def compare_with_baseline(self, threshold_pct: float = 5.0) -> Dict[str, Any]:
        """Compare current results with baseline."""
        comparison = {
            'regressions': [],
            'improvements': [],
            'unchanged': [],
            'new_benchmarks': [],
            'missing_benchmarks': [],
        }
        
        baseline_names = set(self.baseline.keys())
        current_names = {r.name for r in self.results}
        
        # Check for missing/new
        for name in baseline_names - current_names:
            comparison['missing_benchmarks'].append(name)
        for name in current_names - baseline_names:
            comparison['new_benchmarks'].append(name)
        
        # Compare common benchmarks
        for name in baseline_names & current_names:
            baseline = self.baseline[name]
            current = next(r for r in self.results if r.name == name)
            
            for metric in baseline.metrics:
                if metric in current.metrics:
                    b_val = baseline.metrics[metric]
                    c_val = current.metrics[metric]
                    
                    if b_val != 0:
                        change_pct = ((c_val - b_val) / abs(b_val)) * 100
                    else:
                        change_pct = 100 if c_val > 0 else 0
                    
                    # Determine if regression or improvement
                    # For latency/memory: lower is better
                    # For throughput: higher is better
                    is_latency = any(k in metric for k in ['ns', 'ms', 'us', 'latency', 'duration', 'time'])
                    is_memory = any(k in metric for k in ['bytes', 'memory', 'alloc'])
                    is_throughput = any(k in metric for k in ['rps', 'ops', 'throughput', 'qps'])
                    
                    if is_latency or is_memory:
                        # Lower is better
                        if change_pct > threshold_pct:
                            comparison['regressions'].append({
                                'benchmark': name,
                                'metric': metric,
                                'baseline': b_val,
                                'current': c_val,
                                'change_pct': round(change_pct, 2),
                                'type': 'latency' if is_latency else 'memory',
                            })
                        elif change_pct < -threshold_pct:
                            comparison['improvements'].append({
                                'benchmark': name,
                                'metric': metric,
                                'baseline': b_val,
                                'current': c_val,
                                'change_pct': round(change_pct, 2),
                            })
                    elif is_throughput:
                        # Higher is better
                        if change_pct < -threshold_pct:
                            comparison['regressions'].append({
                                'benchmark': name,
                                'metric': metric,
                                'baseline': b_val,
                                'current': c_val,
                                'change_pct': round(change_pct, 2),
                                'type': 'throughput',
                            })
                        elif change_pct > threshold_pct:
                            comparison['improvements'].append({
                                'benchmark': name,
                                'metric': metric,
                                'baseline': b_val,
                                'current': c_val,
                                'change_pct': round(change_pct, 2),
                            })
                    else:
                        if abs(change_pct) > threshold_pct:
                            comparison['regressions' if change_pct > 0 else 'improvements'].append({
                                'benchmark': name,
                                'metric': metric,
                                'baseline': b_val,
                                'current': c_val,
                                'change_pct': round(change_pct, 2),
                            })
                        else:
                            comparison['unchanged'].append({
                                'benchmark': name,
                                'metric': metric,
                                'baseline': b_val,
                                'current': c_val,
                                'change_pct': round(change_pct, 2),
                            })
        
        return comparison
    
    def check_budgets(self) -> Dict[str, Any]:
        """Check results against budgets."""
        results = {
            'passed': [],
            'failed': [],
            'skipped': [],
        }
        
        for budget in self.budgets:
            # Find matching metric in results
            matched = False
            for result in self.results:
                if budget.metric in result.metrics:
                    matched = True
                    value = result.metrics[budget.metric]
                    passed = self._check_budget(value, budget)
                    
                    if passed:
                        results['passed'].append({
                            'metric': budget.metric,
                            'value': value,
                            'budget': f"{budget.operator}{budget.threshold}{budget.unit}",
                        })
                    else:
                        results['failed'].append({
                            'metric': budget.metric,
                            'value': value,
                            'budget': f"{budget.operator}{budget.threshold}{budget.unit}",
                        })
                    break
            
            if not matched:
                results['skipped'].append({
                    'metric': budget.metric,
                    'reason': 'Metric not found in benchmark results',
                })
        
        return results
    
    def _check_budget(self, value: float, budget: PerformanceBudget) -> bool:
        """Check if value satisfies budget."""
        op = budget.operator
        threshold = budget.threshold
        
        if op == '<':
            return value < threshold
        elif op == '<=':
            return value <= threshold
        elif op == '>':
            return value > threshold
        elif op == '>=':
            return value >= threshold
        elif op == '==':
            return abs(value - threshold) < 0.001
        return False
    
    def generate_report(self, format: str = 'markdown') -> str:
        if format == 'json':
            return json.dumps({
                'results': [asdict(r) for r in self.results],
                'budgets': [asdict(b) for b in self.budgets],
                'baseline_comparison': getattr(self, 'comparison', {}),
                'budget_check': getattr(self, 'budget_results', {}),
            }, indent=2, default=str)
        
        lines = [
            "# Performance Report",
            "",
            f"**Language**: {self.results[0].language if self.results else 'unknown'}",
            f"**Benchmarks run**: {len(self.results)}",
            f"**Budgets defined**: {len(self.budgets)}",
            "",
        ]
        
        # Benchmark Results
        if self.results:
            lines.append("## Benchmark Results")
            lines.append("")
            for result in self.results:
                lines.append(f"### {result.name}")
                lines.append(f"**Language**: {result.language}")
                lines.append(f"**Iterations**: {result.iterations}")
                lines.append(f"**Timestamp**: {result.timestamp}")
                lines.append("")
                lines.append("**Metrics**:")
                for metric, value in result.metrics.items():
                    unit = result.unit.get(metric, '')
                    lines.append(f"- {metric}: {value} {unit}")
                lines.append("")
        
        # Budget Check
        if hasattr(self, 'budget_results'):
            br = self.budget_results
            lines.append("## Budget Check")
            lines.append("")
            lines.append(f"**Passed**: {len(br['passed'])}")
            lines.append(f"**Failed**: {len(br['failed'])}")
            lines.append(f"**Skipped**: {len(br['skipped'])}")
            lines.append("")
            
            if br['failed']:
                lines.append("### ❌ Failed Budgets")
                for f in br['failed']:
                    lines.append(f"- **{f['metric']}**: {f['value']} (budget: {f['budget']})")
                lines.append("")
            
            if br['passed']:
                lines.append("### ✅ Passed Budgets")
                for p in br['passed']:
                    lines.append(f"- **{p['metric']}**: {p['value']} (budget: {p['budget']})")
                lines.append("")
        
        # Baseline Comparison
        if hasattr(self, 'comparison'):
            comp = self.comparison
            lines.append("## Baseline Comparison")
            lines.append("")
            lines.append(f"**Regressions**: {len(comp['regressions'])}")
            lines.append(f"**Improvements**: {len(comp['improvements'])}")
            lines.append(f"**Unchanged**: {len(comp['unchanged'])}")
            lines.append(f"**New**: {len(comp['new_benchmarks'])}")
            lines.append(f"**Missing**: {len(comp['missing_benchmarks'])}")
            lines.append("")
            
            if comp['regressions']:
                lines.append("### 🔴 Regressions")
                for r in comp['regressions']:
                    lines.append(f"- **{r['benchmark']}.{r['metric']}**: {r['baseline']} → {r['current']} ({r['change_pct']:+.1f}%) [{r['type']}]")
                lines.append("")
            
            if comp['improvements']:
                lines.append("### 🟢 Improvements")
                for i in comp['improvements']:
                    lines.append(f"- **{i['benchmark']}.{i['metric']}**: {i['baseline']} → {i['current']} ({i['change_pct']:+.1f}%)")
                lines.append("")
        
        return '\n'.join(lines)
    
    def save_results(self, path: Path):
        """Save results to JSON file."""
        data = {r.name: asdict(r) for r in self.results}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(
        description="Performance profiling with budgets and baseline comparison",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python profile-performance.py --dir ./src --budget "latency:p99<200ms,throughput:>1000rps"
  python profile-performance.py --command "go test -bench=. -benchmem" --output bench.json
  python profile-performance.py --baseline benchmarks/base.json --current benchmarks/current.json --threshold 5%
        """
    )
    
    parser.add_argument('--dir', '-d', required=True, help='Project directory')
    parser.add_argument('--command', '-c', help='Benchmark command to run')
    parser.add_argument('--language', '-l', help='Language (auto-detected if not specified)')
    parser.add_argument('--iterations', '-i', type=int, default=1, help='Number of iterations')
    parser.add_argument('--budget', '-b', help='Performance budget (e.g., "latency:p99<200ms,throughput:>1000rps")')
    parser.add_argument('--baseline', help='Baseline benchmark JSON file')
    parser.add_argument('--current', help='Current benchmark JSON file (for comparison)')
    parser.add_argument('--threshold', type=float, default=5.0, help='Regression threshold %')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--save-results', help='Save benchmark results to JSON file')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    parser.add_argument('--verbose', '-v', action='store_true')
    
    args = parser.parse_args()
    
    repo_path = Path(args.dir)
    if not repo_path.exists():
        print(f"Error: Directory not found: {repo_path}", file=sys.stderr)
        sys.exit(1)
    
    profiler = PerformanceProfiler(repo_path)
    
    # Parse budget
    if args.budget:
        profiler.parse_budget(args.budget)
    
    # Load baseline if provided
    if args.baseline:
        profiler.load_baseline(Path(args.baseline))
    
    # Run benchmarks or load current
    if args.command:
        language = args.language or profiler._detect_language()
        if args.verbose:
            print(f"Running benchmarks: {args.command}")
            print(f"Language: {language}")
        profiler.run_benchmarks(args.command, language, args.iterations)
    elif args.current:
        # Load current from file
        with open(args.current) as f:
            data = json.load(f)
        profiler.results = [BenchmarkResult(**r) for r in data.values()]
    
    # Compare with baseline
    if args.baseline and (args.command or args.current):
        if args.verbose:
            print(f"Comparing with baseline (threshold: {args.threshold}%)")
        profiler.comparison = profiler.compare_with_baseline(args.threshold)
    
    # Check budgets
    if profiler.budgets:
        if args.verbose:
            print("Checking budgets...")
        profiler.budget_results = profiler.check_budgets()
    
    # Save results if requested
    if args.save_results:
        profiler.save_results(Path(args.save_results))
        if args.verbose:
            print(f"Results saved to: {args.save_results}")
    
    # Generate report
    report = profiler.generate_report(args.format)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    # Exit code based on budgets
    if hasattr(profiler, 'budget_results') and profiler.budget_results['failed']:
        sys.exit(1)
    
    # Exit code based on regressions
    if hasattr(profiler, 'comparison') and profiler.comparison['regressions']:
        sys.exit(1)


if __name__ == '__main__':
    main()