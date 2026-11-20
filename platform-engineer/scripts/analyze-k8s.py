#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kubernetes Manifest Analyzer — Validates K8s manifests for security, best practices, and resource management.
"""

import argparse
import json
import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


@dataclass
class Finding:
    severity: Severity
    category: str
    message: str
    file: str
    line: int
    resource_kind: str
    resource_name: str
    namespace: str = ""
    fix: str = ""


class K8sAnalyzer:
    def __init__(self):
        self.findings: List[Finding] = []
        self.required_labels = {"app", "version", "team", "environment"}

    def analyze_file(self, file_path: Path) -> List[Finding]:
        """Analyze a single YAML file."""
        self.findings = []
        try:
            with open(file_path) as f:
                docs = list(yaml.safe_load_all(f))
        except yaml.YAMLError as e:
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                category="syntax",
                message=f"YAML parse error: {e}",
                file=str(file_path),
                line=getattr(e, 'line', 0) + 1,
                resource_kind="Unknown",
                resource_name="Unknown",
            ))
            return self.findings

        for doc in docs:
            if doc is None:
                continue
            self._analyze_resource(doc, file_path)

        return self.findings

    def _analyze_resource(self, resource: Dict, file_path: Path):
        """Analyze a single K8s resource."""
        kind = resource.get("kind", "Unknown")
        metadata = resource.get("metadata", {})
        name = metadata.get("name", "unnamed")
        namespace = metadata.get("namespace", "")
        line = metadata.get("__line__", 0)

        # Common checks
        self._check_labels(resource, file_path, kind, name, namespace, line)
        self._check_annotations(resource, file_path, kind, name, namespace, line)

        # Kind-specific checks
        if kind in ("Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"):
            self._check_workload(resource, file_path, kind, name, namespace, line)
        elif kind == "Service":
            self._check_service(resource, file_path, kind, name, namespace, line)
        elif kind == "Ingress":
            self._check_ingress(resource, file_path, kind, name, namespace, line)
        elif kind == "NetworkPolicy":
            self._check_network_policy(resource, file_path, kind, name, namespace, line)
        elif kind == "Pod":
            self._check_pod_spec(resource.get("spec", {}), file_path, kind, name, namespace, line)
        elif kind == "ConfigMap":
            self._check_configmap(resource, file_path, kind, name, namespace, line)
        elif kind == "Secret":
            self._check_secret(resource, file_path, kind, name, namespace, line)

    def _check_labels(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check for required labels."""
        metadata = resource.get("metadata", {})
        labels = metadata.get("labels", {})
        missing = self.required_labels - set(labels.keys())
        for label in missing:
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="labeling",
                message=f"Missing required label: {label}",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix=f"Add label '{label}' to metadata.labels",
            ))

    def _check_annotations(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check for useful annotations."""
        metadata = resource.get("metadata", {})
        annotations = metadata.get("annotations", {})
        
        # Prometheus scraping
        if kind in ("Deployment", "StatefulSet", "DaemonSet", "Pod"):
            if "prometheus.io/scrape" not in annotations:
                self.findings.append(Finding(
                    severity=Severity.INFO,
                    category="observability",
                    message="Missing prometheus.io/scrape annotation",
                    file=str(file_path),
                    line=line,
                    resource_kind=kind,
                    resource_name=name,
                    namespace=namespace,
                    fix="Add annotation: prometheus.io/scrape: 'true'",
                ))

    def _check_workload(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check Deployment/StatefulSet/DaemonSet/Job/CronJob."""
        spec = resource.get("spec", {})
        template = spec.get("template", {})
        pod_spec = template.get("spec", {})
        
        self._check_pod_spec(pod_spec, file_path, kind, name, namespace, line)
        
        # Replicas check
        if kind in ("Deployment", "StatefulSet", "DaemonSet"):
            replicas = spec.get("replicas", 1)
            if replicas < 2 and kind != "DaemonSet":
                self.findings.append(Finding(
                    severity=Severity.MAJOR,
                    category="availability",
                    message=f"Replicas should be >=2 for HA (current: {replicas})",
                    file=str(file_path),
                    line=line,
                    resource_kind=kind,
                    resource_name=name,
                    namespace=namespace,
                    fix="Set replicas >= 2",
                ))
        
        # Strategy
        if kind == "Deployment":
            strategy = spec.get("strategy", {})
            if strategy.get("type") != "RollingUpdate":
                self.findings.append(Finding(
                    severity=Severity.MINOR,
                    category="deployment",
                    message="Deployment should use RollingUpdate strategy",
                    file=str(file_path),
                    line=line,
                    resource_kind=kind,
                    resource_name=name,
                    namespace=namespace,
                    fix="Set strategy.type: RollingUpdate",
                ))

    def _check_pod_spec(self, pod_spec: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check pod spec for security and resource management."""
        containers = pod_spec.get("containers", [])
        init_containers = pod_spec.get("initContainers", [])
        all_containers = containers + init_containers

        if not all_containers:
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                category="configuration",
                message="No containers defined",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
            ))
            return

        for container in all_containers:
            self._check_container(container, file_path, kind, name, namespace, line)

        # Pod-level security context
        sec_ctx = pod_spec.get("securityContext", {})
        if not sec_ctx.get("runAsNonRoot"):
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="security",
                message="Pod should run as non-root (securityContext.runAsNonRoot: true)",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add securityContext.runAsNonRoot: true at pod level",
            ))
        if not sec_ctx.get("fsGroup"):
            self.findings.append(Finding(
                severity=Severity.MINOR,
                category="security",
                message="Pod should set fsGroup in securityContext",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add securityContext.fsGroup: 1000",
            ))

    def _check_container(self, container: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check individual container."""
        c_name = container.get("name", "unnamed")

        # Resources
        resources = container.get("resources", {})
        requests = resources.get("requests", {})
        limits = resources.get("limits", {})

        if not requests:
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                category="resources",
                message=f"Container '{c_name}' missing resource requests",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add resources.requests with cpu and memory",
            ))
        else:
            if "cpu" not in requests:
                self.findings.append(Finding(
                    severity=Severity.MAJOR,
                    category="resources",
                    message=f"Container '{c_name}' missing CPU request",
                    file=str(file_path),
                    line=line,
                    resource_kind=kind,
                    resource_name=name,
                    namespace=namespace,
                    fix="Add resources.requests.cpu",
                ))
            if "memory" not in requests:
                self.findings.append(Finding(
                    severity=Severity.MAJOR,
                    category="resources",
                    message=f"Container '{c_name}' missing memory request",
                    file=str(file_path),
                    line=line,
                    resource_kind=kind,
                    resource_name=name,
                    namespace=namespace,
                    fix="Add resources.requests.memory",
                ))

        if not limits:
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="resources",
                message=f"Container '{c_name}' missing resource limits",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add resources.limits with cpu and memory",
            ))
        else:
            # Check limits >= requests
            for res_type in ("cpu", "memory"):
                if res_type in requests and res_type in limits:
                    req = self._parse_quantity(requests[res_type])
                    lim = self._parse_quantity(limits[res_type])
                    if req and lim and lim < req:
                        self.findings.append(Finding(
                            severity=Severity.MAJOR,
                            category="resources",
                            message=f"Container '{c_name}' limit < request for {res_type}",
                            file=str(file_path),
                            line=line,
                            resource_kind=kind,
                            resource_name=name,
                            namespace=namespace,
                            fix=f"Set {res_type} limit >= request",
                        ))

        # Probes
        has_liveness = "livenessProbe" in container
        has_readiness = "readinessProbe" in container
        has_startup = "startupProbe" in container

        if not has_liveness:
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="reliability",
                message=f"Container '{c_name}' missing livenessProbe",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add livenessProbe (HTTP/TCP/Exec)",
            ))
        if not has_readiness:
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="reliability",
                message=f"Container '{c_name}' missing readinessProbe",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add readinessProbe (HTTP/TCP/Exec)",
            ))
        if not has_startup:
            self.findings.append(Finding(
                severity=Severity.MINOR,
                category="reliability",
                message=f"Container '{c_name}' missing startupProbe (recommended for slow-starting apps)",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add startupProbe",
            ))

        # Security context
        sec_ctx = container.get("securityContext", {})
        if sec_ctx.get("privileged"):
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                category="security",
                message=f"Container '{c_name}' runs privileged (securityContext.privileged: true)",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Remove privileged: true, use specific capabilities if needed",
            ))
        if sec_ctx.get("runAsUser") == 0:
            self.findings.append(Finding(
                severity=Severity.CRITICAL,
                category="security",
                message=f"Container '{c_name}' runs as root (runAsUser: 0)",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Set runAsUser to non-zero (e.g., 1000)",
            ))
        if not sec_ctx.get("readOnlyRootFilesystem"):
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="security",
                message=f"Container '{c_name}' root filesystem not read-only",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Set securityContext.readOnlyRootFilesystem: true",
            ))
        if not sec_ctx.get("allowPrivilegeEscalation") is False:
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="security",
                message=f"Container '{c_name}' allows privilege escalation",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Set securityContext.allowPrivilegeEscalation: false",
            ))
        if not sec_ctx.get("capabilities", {}).get("drop", []):
            self.findings.append(Finding(
                severity=Severity.MINOR,
                category="security",
                message=f"Container '{c_name}' doesn't drop capabilities",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add securityContext.capabilities.drop: [ALL]",
            ))

        # Image
        image = container.get("image", "")
        if ":latest" in image or ":" not in image:
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="configuration",
                message=f"Container '{c_name}' uses 'latest' or untagged image: {image}",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Use specific image tag (e.g., v1.2.3 or sha256:...)",
            ))
        if image and not image.startswith(("ghcr.io/", "docker.io/", "registry.", "localhost")):
            # Could be private registry - just warn
            pass

    def _parse_quantity(self, qty: str) -> Optional[int]:
        """Parse Kubernetes quantity string to integer (base unit)."""
        qty = str(qty).strip()
        if qty.endswith("m"):  # millicpu
            try:
                return int(qty[:-1])
            except ValueError:
                return None
        elif qty.endswith("Ki"):
            try:
                return int(qty[:-2]) * 1024
            except ValueError:
                return None
        elif qty.endswith("Mi"):
            try:
                return int(qty[:-2]) * 1024 * 1024
            except ValueError:
                return None
        elif qty.endswith("Gi"):
            try:
                return int(qty[:-2]) * 1024 * 1024 * 1024
            except ValueError:
                return None
        elif qty.isdigit():
            return int(qty)
        return None

    def _check_service(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check Service resource."""
        spec = resource.get("spec", {})
        if spec.get("type") == "LoadBalancer":
            self.findings.append(Finding(
                severity=Severity.INFO,
                category="networking",
                message="LoadBalancer service — ensure proper annotations for cloud provider",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add service.beta.kubernetes.io/aws-load-balancer-type: nlb (or equivalent)",
            ))

    def _check_ingress(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check Ingress resource."""
        spec = resource.get("spec", {})
        if "tls" not in spec:
            self.findings.append(Finding(
                severity=Severity.MAJOR,
                category="security",
                message="Ingress missing TLS configuration",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add spec.tls with secretName for TLS certificate",
            ))

    def _check_network_policy(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check NetworkPolicy."""
        spec = resource.get("spec", {})
        if "policyTypes" not in spec:
            self.findings.append(Finding(
                severity=Severity.MINOR,
                category="networking",
                message="NetworkPolicy should specify policyTypes",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
                fix="Add policyTypes: [Ingress, Egress]",
            ))

    def _check_configmap(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check ConfigMap."""
        data = resource.get("data", {})
        if not data and "binaryData" not in resource:
            self.findings.append(Finding(
                severity=Severity.INFO,
                category="configuration",
                message="ConfigMap is empty",
                file=str(file_path),
                line=line,
                resource_kind=kind,
                resource_name=name,
                namespace=namespace,
            ))

    def _check_secret(self, resource: Dict, file_path: Path, kind: str, name: str, namespace: str, line: int):
        """Check Secret."""
        secret_type = resource.get("type", "Opaque")
        if secret_type == "Opaque":
            # Check for base64 encoded values (should be stringData)
            data = resource.get("data", {})
            string_data = resource.get("stringData", {})
            if data and not string_data:
                self.findings.append(Finding(
                    severity=Severity.INFO,
                    category="configuration",
                    message="Consider using stringData instead of base64-encoded data",
                    file=str(file_path),
                    line=line,
                    resource_kind=kind,
                    resource_name=name,
                    namespace=namespace,
                    fix="Use stringData for plain-text values, they'll be encoded automatically",
                ))

    def generate_report(self, format: str = "text") -> str:
        """Generate report from findings."""
        if format == "json":
            return json.dumps([asdict(f) for f in self.findings], indent=2, default=str)

        # Group by severity
        by_severity = {s: [] for s in Severity}
        for f in self.findings:
            by_severity[f.severity].append(f)

        lines = ["# Kubernetes Manifest Analysis Report\n"]
        total = len(self.findings)
        critical = len(by_severity[Severity.CRITICAL])
        major = len(by_severity[Severity.MAJOR])
        minor = len(by_severity[Severity.MINOR])
        info = len(by_severity[Severity.INFO])
        lines.append(f"**Total Findings**: {total} (🔴 {critical} Critical, 🟡 {major} Major, 🟢 {minor} Minor, ℹ️ {info} Info)\n")

        for severity in [Severity.CRITICAL, Severity.MAJOR, Severity.MINOR, Severity.INFO]:
            findings = by_severity[severity]
            if not findings:
                continue
            icon = {"critical": "🔴", "major": "🟡", "minor": "🟢", "info": "ℹ️"}[severity.value]
            lines.append(f"## {icon} {severity.value.title()} ({len(findings)})\n")
            for f in findings:
                lines.append(f"### {f.category}: {f.message}")
                lines.append(f"- **File**: `{f.file}`:{f.line}")
                lines.append(f"- **Resource**: {f.resource_kind}/{f.resource_name}" + (f" (ns: {f.namespace})" if f.namespace else ""))
                if f.fix:
                    lines.append(f"- **Fix**: {f.fix}")
                lines.append("")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Analyze Kubernetes manifests")
    parser.add_argument("--manifests", required=True, help="Path to manifests directory or file")
    parser.add_argument("--fail-on", choices=["critical", "major", "minor", "info"], default="critical", help="Fail on severity level")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--output", "-o", help="Output file")
    args = parser.parse_args()

    path = Path(args.manifests).resolve()
    if not path.exists():
        print(f"❌ Path not found: {path}", file=sys.stderr)
        sys.exit(1)

    analyzer = K8sAnalyzer()
    all_findings = []

    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.yaml")) + list(path.rglob("*.yml"))

    for file_path in files:
        # Skip certain files
        if any(skip in file_path.parts for skip in (".git", "node_modules", "vendor", ".terraform")):
            continue
        findings = analyzer.analyze_file(file_path)
        all_findings.extend(findings)

    # Temporarily replace analyzer findings for report
    analyzer.findings = all_findings
    report = analyzer.generate_report(args.format)

    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report)

    # Exit code based on fail-on
    severity_order = {"critical": 0, "major": 1, "minor": 2, "info": 3}
    fail_level = severity_order[args.fail_on]
    has_failure = any(severity_order.get(f.severity.value, 4) <= fail_level for f in all_findings)

    if has_failure:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()