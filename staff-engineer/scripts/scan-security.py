#!/usr/bin/env python3
"""
Security Scanner — SAST, Secrets, Dependencies, License, Crypto

Comprehensive security scanning for any codebase.
Language-agnostic with language-specific rules.

Usage:
    python scan-security.py --dir ./src --output report.md --fail-on critical,high
    python scan-security.py --dir . --check secrets,deps,crypto --format json
    python scan-security.py --file main.go --check sast --format sarif
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class CheckType(Enum):
    SAST = "sast"
    SECRETS = "secrets"
    DEPENDENCIES = "deps"
    LICENSE = "license"
    CRYPTO = "crypto"
    CONFIG = "config"


@dataclass
class Finding:
    severity: Severity
    check_type: CheckType
    rule_id: str
    message: str
    file: str
    line: int
    column: int = 0
    snippet: str = ""
    fix_suggestion: str = ""
    references: List[str] = None
    
    def __post_init__(self):
        if self.references is None:
            self.references = []


class SecurityScanner:
    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.findings: List[Finding] = []
        self.languages = self._detect_languages()
        
    def _detect_languages(self) -> Set[str]:
        """Detect languages in the repository."""
        languages = set()
        ext_map = {
            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
            '.tsx': 'typescript', '.jsx': 'javascript', '.go': 'go',
            '.java': 'java', '.kt': 'kotlin', '.rs': 'rust',
            '.cs': 'csharp', '.php': 'php', '.rb': 'ruby',
            '.cpp': 'cpp', '.cc': 'cpp', '.c': 'c', '.h': 'c',
            '.swift': 'swift', '.scala': 'scala', '.clj': 'clojure',
        }
        for ext, lang in ext_map.items():
            if list(self.repo_path.rglob(f'*{ext}')):
                languages.add(lang)
        return languages
    
    def scan(self, checks: List[CheckType] = None, fail_on: List[Severity] = None) -> List[Finding]:
        """Run all selected checks."""
        if checks is None:
            checks = list(CheckType)
        
        self.findings = []
        
        if CheckType.SAST in checks:
            self._run_sast()
        if CheckType.SECRETS in checks:
            self._scan_secrets()
        if CheckType.DEPENDENCIES in checks:
            self._scan_dependencies()
        if CheckType.LICENSE in checks:
            self._scan_licenses()
        if CheckType.CRYPTO in checks:
            self._scan_crypto()
        if CheckType.CONFIG in checks:
            self._scan_config()
        
        # Sort by severity
        severity_order = {Severity.CRITICAL: 0, Severity.HIGH: 1, Severity.MEDIUM: 2, Severity.LOW: 3, Severity.INFO: 4}
        self.findings.sort(key=lambda f: (severity_order[f.severity], f.file, f.line))
        
        if fail_on:
            self._check_fail_on(fail_on)
        
        return self.findings
    
    def _run_sast(self):
        """Run Semgrep for SAST (if available)."""
        try:
            result = subprocess.run(
                ['semgrep', 'scan', '--json', '--config=auto', str(self.repo_path)],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode in (0, 1):  # 0 = no findings, 1 = findings
                data = json.loads(result.stdout)
                for r in data.get('results', []):
                    self.findings.append(Finding(
                        severity=self._map_semgrep_severity(r.get('extra', {}).get('severity', 'INFO')),
                        check_type=CheckType.SAST,
                        rule_id=r.get('check_id', 'unknown'),
                        message=r.get('extra', {}).get('message', 'SAST finding'),
                        file=r.get('path', ''),
                        line=r.get('start', {}).get('line', 0),
                        column=r.get('start', {}).get('col', 0),
                        snippet=r.get('extra', {}).get('lines', ''),
                        fix_suggestion=r.get('extra', {}).get('fix', ''),
                        references=[r.get('extra', {}).get('metadata', {}).get('references', '')],
                    ))
        except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
            # Fallback to basic pattern matching
            self._basic_sast()
    
    def _basic_sast(self):
        """Basic pattern-based SAST for common vulnerabilities."""
        patterns = {
            'sql-injection': {
                'pattern': r'(execute|query|exec)\s*\(\s*["\'].*[%+].*["\']',
                'severity': Severity.HIGH,
                'message': 'Potential SQL injection: string concatenation in query',
                'fix': 'Use parameterized queries / prepared statements',
            },
            'command-injection': {
                'pattern': r'(exec|system|popen|subprocess\.(run|call|Popen))\s*\(.*[%+].*\)',
                'severity': Severity.HIGH,
                'message': 'Potential command injection: user input in command',
                'fix': 'Use subprocess with args list, validate/sanitize input',
            },
            'path-traversal': {
                'pattern': r'(open|readFile|read_file)\s*\(.*\.\./',
                'severity': Severity.MEDIUM,
                'message': 'Potential path traversal: user input in file path',
                'fix': 'Validate/sanitize paths, use safe path resolution',
            },
            'xss': {
                'pattern': r'(innerHTML|dangerouslySetInnerHTML|v-html)\s*[=:]',
                'severity': Severity.MEDIUM,
                'message': 'Potential XSS: direct HTML injection',
                'fix': 'Use safe templating, sanitize user input',
            },
            'hardcoded-secret': {
                'pattern': r'(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*["\'][a-zA-Z0-9+/=]{20,}',
                'severity': Severity.CRITICAL,
                'message': 'Hardcoded secret detected',
                'fix': 'Move to environment variables / secret manager',
            },
            'weak-crypto': {
                'pattern': r'(MD5|SHA1|DES|RC4|ECB)\s*\(',
                'severity': Severity.HIGH,
                'message': 'Weak cryptographic algorithm',
                'fix': 'Use SHA-256+, AES-GCM, ChaCha20-Poly1305',
            },
        }
        
        for file_path in self.repo_path.rglob('*'):
            if not file_path.is_file() or file_path.suffix in ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map', '.min.js', '.min.css'):
                continue
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    for rule_id, rule in patterns.items():
                        if re.search(rule['pattern'], line, re.IGNORECASE):
                            self.findings.append(Finding(
                                severity=rule['severity'],
                                check_type=CheckType.SAST,
                                rule_id=rule_id,
                                message=rule['message'],
                                file=str(file_path.relative_to(self.repo_path)),
                                line=i,
                                snippet=line.strip()[:200],
                                fix_suggestion=rule['fix'],
                                references=[],
                            ))
            except Exception:
                pass
    
    def _scan_secrets(self):
        """Scan for secrets using entropy and pattern matching."""
        secret_patterns = [
            # AWS
            (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID', Severity.CRITICAL),
            (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\'][A-Za-z0-9/+=]{40}', 'AWS Secret Access Key', Severity.CRITICAL),
            # GitHub
            (r'gh[pousr]_[A-Za-z0-9_]{36,251}', 'GitHub Token', Severity.CRITICAL),
            # Generic high entropy
            (r'(?i)(api[_-]?key|secret|password|token|private[_-]?key)\s*[:=]\s*["\']?[A-Za-z0-9+/=]{32,}["\']?', 'Generic Secret', Severity.HIGH),
            # JWT
            (r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', 'JWT Token', Severity.HIGH),
            # Private keys
            (r'-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----', 'Private Key', Severity.CRITICAL),
            # Database URLs
            (r'(postgres|mysql|mongodb|redis)://[^:\s]+:[^@\s]+@[^/\s]+', 'Database URL with Credentials', Severity.CRITICAL),
        ]
        
        for file_path in self.repo_path.rglob('*'):
            if not file_path.is_file() or file_path.name in ('.gitignore', '.env.example', '.env.template'):
                continue
            if file_path.suffix in ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map', '.pem', '.key', '.crt', '.cer'):
                continue
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    for pattern, name, severity in secret_patterns:
                        matches = re.finditer(pattern, line, re.IGNORECASE)
                        for match in matches:
                            # Skip obvious test/fake values
                            matched = match.group(0)
                            if any(fake in matched.lower() for fake in ['test', 'fake', 'dummy', 'example', 'placeholder', 'your_key', 'changeme', 'xxxx', '1234']):
                                continue
                            self.findings.append(Finding(
                                severity=severity,
                                check_type=CheckType.SECRETS,
                                rule_id=f'secret-{name.lower().replace(" ", "-")}',
                                message=f'{name} detected in source code',
                                file=str(file_path.relative_to(self.repo_path)),
                                line=i,
                                snippet=line.strip()[:200],
                                fix_suggestion='Move to environment variables / secret manager (AWS Secrets Manager, HashiCorp Vault, 1Password)',
                                references=['https://owasp.org/www-project-top-ten/2021/A02_2021-Cryptographic_Failures'],
                            ))
            except Exception:
                pass
    
    def _scan_dependencies(self):
        """Scan dependencies for vulnerabilities."""
        # Check for lockfiles and run appropriate scanner
        lockfiles = {
            'package-lock.json': ('npm', 'npm audit --json'),
            'yarn.lock': ('yarn', 'yarn audit --json'),
            'pnpm-lock.yaml': ('pnpm', 'pnpm audit --json'),
            'requirements.txt': ('pip', 'pip-audit --format=json'),
            'poetry.lock': ('poetry', 'poetry run pip-audit --format=json'),
            'Pipfile.lock': ('pipenv', 'pipenv run pip-audit --format=json'),
            'go.sum': ('go', 'govulncheck -json'),
            'Cargo.lock': ('cargo', 'cargo audit --json'),
            'composer.lock': ('composer', 'composer audit --format=json'),
        }
        
        for lockfile, (ecosystem, cmd) in lockfiles.items():
            for lock_path in self.repo_path.rglob(lockfile):
                try:
                    result = subprocess.run(cmd.split(), cwd=lock_path.parent, capture_output=True, text=True, timeout=120)
                    self._parse_dep_scan(result.stdout, ecosystem, lock_path)
                except (FileNotFoundError, subprocess.TimeoutExpired):
                    pass
    
    def _parse_dep_scan(self, output: str, ecosystem: str, lock_path: Path):
        """Parse dependency scan output."""
        try:
            if ecosystem in ('npm', 'yarn', 'pnpm'):
                data = json.loads(output)
                for advisory in data.get('advisories', {}).values():
                    self.findings.append(Finding(
                        severity=self._map_npm_severity(advisory.get('severity', 'moderate')),
                        check_type=CheckType.DEPENDENCIES,
                        rule_id=f'dep-{advisory.get("id", "unknown")}',
                        message=f'{advisory.get("title", "Vulnerability")} in {advisory.get("module_name", "unknown")}@{advisory.get("findings", [{}])[0].get("version", "unknown")}',
                        file=str(lock_path.relative_to(self.repo_path)),
                        line=0,
                        fix_suggestion=f'Update to {advisory.get("patched_versions", "latest")}',
                        references=[advisory.get('url', '')],
                    ))
            elif ecosystem == 'go':
                for line in output.strip().split('\n'):
                    if line:
                        vuln = json.loads(line)
                        self.findings.append(Finding(
                            severity=self._map_go_severity(vuln.get('Severity', 'UNKNOWN')),
                            check_type=CheckType.DEPENDENCIES,
                            rule_id=f'dep-{vuln.get("Vulnerability", "unknown")}',
                            message=f'{vuln.get("Vulnerability", "Vulnerability")} in {vuln.get("Module", "unknown")}',
                            file=str(Path(vuln.get('File', '')).relative_to(self.repo_path)) if vuln.get('File') else '',
                            line=0,
                            fix_suggestion=f'Update to fixed version',
                            references=[vuln.get('URL', '')],
                        ))
        except json.JSONDecodeError:
            pass
    
    def _scan_licenses(self):
        """Scan for license compliance."""
        # Check for problematic licenses
        problematic = {'GPL-3.0', 'AGPL-3.0', 'LGPL-3.0', 'GPL-2.0', 'AGPL-1.0', 'SSPL-1.0'}
        
        # Check package.json, Cargo.toml, go.mod, pyproject.toml, pom.xml, etc.
        license_files = {
            'package.json': lambda c: json.loads(c).get('license', ''),
            'Cargo.toml': lambda c: re.search(r'license\s*=\s*["\']([^"\']+)', c).group(1) if re.search(r'license\s*=\s*["\']([^"\']+)', c) else '',
            'go.mod': lambda c: '',  # Go modules don't have license field
            'pyproject.toml': lambda c: re.search(r'license\s*=\s*["\']([^"\']+)', c).group(1) if re.search(r'license\s*=\s*["\']([^"\']+)', c) else '',
        }
        
        for filename, extractor in license_files.items():
            for file_path in self.repo_path.rglob(filename):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    license_str = extractor(content)
                    if any(prob in license_str for prob in problematic):
                        self.findings.append(Finding(
                            severity=Severity.HIGH,
                            check_type=CheckType.LICENSE,
                            rule_id=f'license-{license_str}',
                            message=f'Potentially problematic license: {license_str}',
                            file=str(file_path.relative_to(self.repo_path)),
                            line=0,
                            fix_suggestion='Review license compatibility with project policy',
                            references=['https://choosealicense.com/'],
                        ))
                except Exception:
                    pass
    
    def _scan_crypto(self):
        """Scan for weak cryptographic practices."""
        crypto_issues = [
            (r'MD5\s*\(', 'MD5', 'Use SHA-256 or SHA-3'),
            (r'SHA1\s*\(', 'SHA-1', 'Use SHA-256 or SHA-3'),
            (r'SHA256\s*\(\s*["\']password', 'Unsalted SHA-256', 'Use Argon2id, bcrypt, or scrypt with salt'),
            (r'Random\(\)|Math\.random\(\)', 'Weak RNG', 'Use crypto/rand, secrets, os.urandom'),
            (r'ECB\s*mode|ECB\s*\)', 'ECB Mode', 'Use GCM, CBC, or CTR mode'),
            (r'DES\s*\(', 'DES', 'Use AES-256-GCM or ChaCha20-Poly1305'),
            (r'RC4\s*\(', 'RC4', 'Use ChaCha20-Poly1305 or AES-GCM'),
            (r'RSA\s*\(\s*1024|RSA\s*\(\s*2048', 'Weak RSA Key Size', 'Use RSA-3072+ or ECDSA P-256+'),
            (r'DH\s*\(\s*1024', 'Weak DH Group', 'Use DH Group 14+ (2048-bit) or ECDH'),
        ]
        
        for file_path in self.repo_path.rglob('*'):
            if not file_path.is_file() or file_path.suffix in ('.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.map'):
                continue
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    for pattern, name, fix in crypto_issues:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.findings.append(Finding(
                                severity=Severity.HIGH,
                                check_type=CheckType.CRYPTO,
                                rule_id=f'crypto-{name.lower().replace(" ", "-")}',
                                message=f'Weak cryptography: {name}',
                                file=str(file_path.relative_to(self.repo_path)),
                                line=i,
                                snippet=line.strip()[:200],
                                fix_suggestion=fix,
                                references=['https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html'],
                            ))
            except Exception:
                pass
    
    def _scan_config(self):
        """Scan configuration files for security misconfigurations."""
        config_checks = {
            'docker': [
                (r'USER\s+root', 'Container runs as root', 'Use non-root USER'),
                (r'--privileged', 'Privileged container', 'Remove --privileged, use specific capabilities'),
                (r'EXPOSE\s+22\b', 'SSH exposed', 'Remove SSH from containers'),
            ],
            'kubernetes': [
                (r'runAsUser:\s*0', 'Pod runs as root', 'Set runAsNonRoot: true'),
                (r'privileged:\s*true', 'Privileged pod', 'Remove privileged, use specific capabilities'),
                (r'hostNetwork:\s*true', 'Host network mode', 'Avoid hostNetwork unless necessary'),
                (r'hostPID:\s*true', 'Host PID namespace', 'Avoid hostPID unless necessary'),
            ],
            'terraform': [
                (r's3_bucket.*acl\s*=\s*"public-read"', 'Public S3 bucket', 'Use private ACL with CloudFront/signed URLs'),
                (r'security_group.*cidr_blocks\s*=\s*\["0\.0\.0\.0/0"\]', 'Open security group', 'Restrict to specific CIDR blocks'),
            ],
        }
        
        file_types = {
            'Dockerfile': 'docker', 'docker-compose.yml': 'docker', 'docker-compose.yaml': 'docker',
            '.k8s': 'kubernetes', 'k8s': 'kubernetes', '.yaml': 'kubernetes', '.yml': 'kubernetes',
            '.tf': 'terraform', '.tfvars': 'terraform',
        }
        
        for file_path in self.repo_path.rglob('*'):
            if not file_path.is_file():
                continue
            file_type = file_types.get(file_path.name, file_types.get(file_path.suffix, ''))
            if not file_type or file_type not in config_checks:
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()
                for i, line in enumerate(lines, 1):
                    for pattern, message, fix in config_checks[file_type]:
                        if re.search(pattern, line, re.IGNORECASE):
                            self.findings.append(Finding(
                                severity=Severity.MEDIUM,
                                check_type=CheckType.CONFIG,
                                rule_id=f'config-{file_type}-{message.lower().replace(" ", "-")}',
                                message=f'Insecure {file_type} config: {message}',
                                file=str(file_path.relative_to(self.repo_path)),
                                line=i,
                                snippet=line.strip()[:200],
                                fix_suggestion=fix,
                                references=[],
                            ))
            except Exception:
                pass
    
    def _map_semgrep_severity(self, sev: str) -> Severity:
        mapping = {'ERROR': Severity.HIGH, 'WARNING': Severity.MEDIUM, 'INFO': Severity.LOW}
        return mapping.get(sev.upper(), Severity.INFO)
    
    def _map_npm_severity(self, sev: str) -> Severity:
        mapping = {'critical': Severity.CRITICAL, 'high': Severity.HIGH, 'moderate': Severity.MEDIUM, 'low': Severity.LOW}
        return mapping.get(sev.lower(), Severity.MEDIUM)
    
    def _map_go_severity(self, sev: str) -> Severity:
        mapping = {'CRITICAL': Severity.CRITICAL, 'HIGH': Severity.HIGH, 'MEDIUM': Severity.MEDIUM, 'LOW': Severity.LOW}
        return mapping.get(sev.upper(), Severity.MEDIUM)
    
    def _check_fail_on(self, fail_on: List[Severity]):
        for finding in self.findings:
            if finding.severity in fail_on:
                sys.exit(1)
    
    def generate_report(self, format: str = 'markdown') -> str:
        if format == 'json':
            return json.dumps([asdict(f) for f in self.findings], indent=2, default=str)
        if format == 'sarif':
            return self._generate_sarif()
        
        # Markdown
        lines = [
            "# Security Scan Report",
            "",
            f"**Repository**: {self.repo_path.name}",
            f"**Languages detected**: {', '.join(sorted(self.languages)) if self.languages else 'None'}",
            f"**Total findings**: {len(self.findings)}",
            f"**Critical**: {sum(1 for f in self.findings if f.severity == Severity.CRITICAL)}",
            f"**High**: {sum(1 for f in self.findings if f.severity == Severity.HIGH)}",
            f"**Medium**: {sum(1 for f in self.findings if f.severity == Severity.MEDIUM)}",
            f"**Low**: {sum(1 for f in self.findings if f.severity == Severity.LOW)}",
            f"**Info**: {sum(1 for f in self.findings if f.severity == Severity.INFO)}",
            "",
        ]
        
        # Group by check type
        by_type = {}
        for f in self.findings:
            by_type.setdefault(f.check_type.value, []).append(f)
        
        for check_type, findings in sorted(by_type.items()):
            lines.append(f"## {check_type.upper()} ({len(findings)})")
            lines.append("")
            
            for finding in findings:
                severity_emoji = {
                    Severity.CRITICAL: '🔴', Severity.HIGH: '🟠',
                    Severity.MEDIUM: '🟡', Severity.LOW: '🟢', Severity.INFO: '🔵'
                }[finding.severity]
                
                lines.append(f"### {severity_emoji} {finding.severity.value.upper()}: {finding.rule_id}")
                lines.append(f"**File**: `{finding.file}:{finding.line}`" + (f":{finding.column}" if finding.column else ""))
                lines.append(f"**Message**: {finding.message}")
                if finding.snippet:
                    lines.append(f"**Code**:")
                    lines.append("```")
                    lines.append(finding.snippet)
                    lines.append("```")
                if finding.fix_suggestion:
                    lines.append(f"**Fix**: {finding.fix_suggestion}")
                if finding.references:
                    lines.append(f"**References**:")
                    for ref in finding.references:
                        if ref:
                            lines.append(f"- {ref}")
                lines.append("")
        
        return '\n'.join(lines)
    
    def _generate_sarif(self) -> str:
        """Generate SARIF format for IDE integration."""
        sarif = {
            "version": "2.1.0",
            "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
            "runs": [{
                "tool": {
                    "driver": {
                        "name": "staff-engineer-security-scan",
                        "version": "1.0.0",
                        "informationUri": "https://github.com/yourorg/staff-engineer",
                        "rules": []
                    }
                },
                "results": []
            }]
        }
        
        rule_map = {}
        for finding in self.findings:
            if finding.rule_id not in rule_map:
                rule_map[finding.rule_id] = {
                    "id": finding.rule_id,
                    "name": finding.rule_id,
                    "shortDescription": {"text": finding.message},
                    "defaultConfiguration": {"level": finding.severity.value},
                    "helpUri": finding.references[0] if finding.references else ""
                }
            
            sarif["runs"][0]["results"].append({
                "ruleId": finding.rule_id,
                "level": finding.severity.value,
                "message": {"text": finding.message},
                "locations": [{
                    "physicalLocation": {
                        "artifactLocation": {"uri": finding.file},
                        "region": {
                            "startLine": finding.line,
                            "startColumn": finding.column if finding.column > 0 else 1,
                        }
                    }
                }],
                "properties": {
                    "fixSuggestion": finding.fix_suggestion,
                    "references": finding.references
                }
            })
        
        sarif["runs"][0]["tool"]["driver"]["rules"] = list(rule_map.values())
        return json.dumps(sarif, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive security scanner for any codebase",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scan-security.py --dir ./src --output report.md --fail-on critical,high
  python scan-security.py --dir . --check secrets,deps,crypto --format json
  python scan-security.py --file main.go --check sast --format sarif
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dir', '-d', help='Directory to scan recursively')
    group.add_argument('--file', '-f', help='Single file to scan')
    
    parser.add_argument('--output', '-o', help='Output file (default: stdout)')
    parser.add_argument('--format', choices=['markdown', 'json', 'sarif'], default='markdown', help='Output format')
    parser.add_argument('--check', help='Comma-separated checks (sast,secrets,deps,license,crypto,config)')
    parser.add_argument('--fail-on', help='Comma-separated severities to fail on (critical,high,medium,low)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Parse checks
    checks = None
    if args.check:
        try:
            checks = [CheckType(c.strip()) for c in args.check.split(',')]
        except ValueError as e:
            print(f"Error: Invalid check: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Parse fail-on
    fail_on = None
    if args.fail_on:
        try:
            fail_on = [Severity(s.strip()) for s in args.fail_on.split(',')]
        except ValueError as e:
            print(f"Error: Invalid severity: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Determine target
    if args.dir:
        target_path = Path(args.dir)
    else:
        target_path = Path(args.file).parent
    
    if not target_path.exists():
        print(f"Error: Path not found: {target_path}", file=sys.stderr)
        sys.exit(1)
    
    scanner = SecurityScanner(target_path)
    
    if args.file:
        # Scan single file by temporarily changing repo path
        original_repo = scanner.repo_path
        scanner.repo_path = Path(args.file).parent
        # We'll filter findings to only the target file later
        findings = scanner.scan(checks, fail_on)
        # Filter to target file
        target_file = Path(args.file).name
        scanner.findings = [f for f in findings if Path(f.file).name == target_file]
    else:
        scanner.scan(checks, fail_on)
    
    if args.verbose:
        print(f"Scanned: {target_path}")
        print(f"Languages: {', '.join(sorted(scanner.languages)) if scanner.languages else 'None'}")
        print(f"Findings: {len(scanner.findings)}")
    
    report = scanner.generate_report(args.format)
    
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(report, encoding='utf-8')
        print(f"Report written to: {output_path}")
    else:
        print(report)
    
    # Exit code based on findings
    if any(f.severity in (Severity.CRITICAL, Severity.HIGH) for f in scanner.findings):
        sys.exit(1)


if __name__ == '__main__':
    main()