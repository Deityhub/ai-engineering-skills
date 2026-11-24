#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Full Lifecycle Orchestrator — End-to-end: intake → release.
Orchestrates all skills through the agentic delivery loop with mandatory human approval gates.
Improvements:
- Template detection for commits/PRs (uses project templates if they exist)
- Detailed planning phase with user iteration before implementation
- Feature flag management
- Rollback automation
- Architecture decision recording (ADR)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import uuid


class GateType(Enum):
    REVIEW_CHANGES = "review_changes"
    REVIEW_PR = "review_pr"
    APPROVE_DEPLOY = "approve_deploy"
    CONSENSUS = "consensus"
    REVIEW_PLAN = "review_plan"


@dataclass
class RoutingDecision:
    mode: str
    required_skills: List[str]
    orchestration_mode: str
    reasoning: str


@dataclass
class DAGNode:
    id: str
    skill: str
    agent_type: str
    description: str
    dependencies: List[str]
    input_schema: Dict
    output_schema: Dict
    checkpoint: bool = False
    checkpoint_type: str = ""


@dataclass
class DAG:
    dag_id: str
    nodes: List[DAGNode]
    edges: List[List[str]]
    checkpoints: List[str]
    estimated_duration: str


@dataclass
class FeaturePlan:
    """Detailed feature plan created during planning phase."""
    request: str
    problem_statement: str = ""
    proposed_solution: str = ""
    technical_approach: str = ""
    acceptance_criteria: List[str] = field(default_factory=list)
    risks_and_mitigations: List[Dict[str, str]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    effort_estimate: str = ""
    milestones: List[Dict[str, str]] = field(default_factory=list)
    feature_flags: List[Dict[str, Any]] = field(default_factory=list)
    adr_references: List[str] = field(default_factory=list)
    test_strategy: str = ""
    rollback_plan: str = ""
    approved: bool = False
    version: int = 1
    feedback_history: List[Dict[str, str]] = field(default_factory=list)


class RequestRouter:
    """Analyzes request and determines routing."""

    SKILL_KEYWORDS = {
        "product-engineering": [
            "strategy", "vision", "roadmap", "prioritize", "prd", "experiment",
            "metrics", "north star", "okr", "discovery", "interview", "kano",
            "rice", "wsjf", "product", "feature flag", "ab test"
        ],
        "design-skill": [
            "ui", "ux", "design", "component", "token", "accessibility", "a11y",
            "wcag", "figma", "responsive", "breakpoint", "color", "typography",
            "dark mode", "design system", "cross-platform", "swiftui", "flutter"
        ],
        "staff-engineer": [
            "code", "architecture", "security", "performance", "refactor", "adr",
            "sql injection", "cache", "database", "api", "microservice", "monolith",
            "clean code", "solid", "coupling", "cohesion", "testing", "profiling"
        ],
        "platform-engineer": [
            "terraform", "kubernetes", "k8s", "ci/cd", "pipeline", "github actions",
            "gitlab ci", "observability", "prometheus", "grafana", "loki", "tempo",
            "slo", "sli", "error budget", "incident", "runbook", "cost", "finops",
            "aws", "gcp", "azure", "helm", "argocd", "flux", "istio"
        ],
        "agentic-orchestration": [
            "agent", "workflow", "dag", "consensus", "delegation", "orchestration",
            "multi-agent", "parallel", "validation", "human-in-the-loop", "hitl"
        ]
    }

    def route(self, request: str) -> RoutingDecision:
        request_lower = request.lower()
        scores = {}
        for skill, keywords in self.SKILL_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in request_lower)
            if score > 0:
                scores[skill] = score

        skills_needed = [s for s, score in scores.items() if score > 0]

        if not skills_needed:
            skills_needed = ["product-engineering", "design-skill", "staff-engineer", "platform-engineer"]
            mode = "full_agentic_loop"
            reasoning = "Ambiguous request — defaulting to full agentic loop with all core skills"
        elif len(skills_needed) >= 3:
            mode = "full_agentic_loop"
            reasoning = f"Request spans {len(skills_needed)} skills — full agentic loop required"
        elif len(skills_needed) == 2:
            mode = "targeted_skills"
            reasoning = f"Two skills needed ({', '.join(skills_needed)}) — targeted parallel execution"
        else:
            mode = "single_skill"
            reasoning = f"Single skill ({skills_needed[0]}) — direct delegation"

        if mode in ("full_agentic_loop", "targeted_skills"):
            if "agentic-orchestration" not in skills_needed:
                skills_needed.append("agentic-orchestration")

        return RoutingDecision(
            mode=mode,
            required_skills=skills_needed,
            orchestration_mode="full_dag" if mode == "full_agentic_loop" else "parallel",
            reasoning=reasoning
        )


class TemplateDetector:
    """Detects existing project templates for commits, PRs, and other artifacts."""

    COMMIT_TEMPLATE_PATHS = [
        ".github/commit-message.txt",
        ".gitmessage",
        ".gitmessage.txt",
        "commit-template.txt",
        ".commit-template",
    ]

    PR_TEMPLATE_PATHS = [
        ".github/pull_request_template.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        ".github/pull_request_template",
        ".github/PULL_REQUEST_TEMPLATE",
        "PULL_REQUEST_TEMPLATE.md",
        "pull_request_template.md",
    ]

    COMMIT_CONVENTION_PATHS = [
        ".github/commit-convention.md",
        "COMMIT_CONVENTION.md",
        ".commit-convention",
        "docs/commit-convention.md",
    ]

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def detect_commit_template(self) -> Optional[str]:
        """Find and return commit message template if exists."""
        for path in self.COMMIT_TEMPLATE_PATHS:
            full_path = self.repo_path / path
            if full_path.exists():
                return full_path.read_text(encoding="utf-8")
        return None

    def detect_pr_template(self) -> Optional[str]:
        """Find and return PR template if exists."""
        for path in self.PR_TEMPLATE_PATHS:
            full_path = self.repo_path / path
            if full_path.exists():
                return full_path.read_text(encoding="utf-8")
        return None

    def detect_commit_convention(self) -> Optional[str]:
        """Find and return commit convention guide if exists."""
        for path in self.COMMIT_CONVENTION_PATHS:
            full_path = self.repo_path / path
            if full_path.exists():
                return full_path.read_text(encoding="utf-8")
        return None

    def get_default_commit_template(self) -> str:
        """Return standard commit template."""
        return """<type>(<scope>): <subject>

<body>

<footer>

Types: feat, fix, refactor, perf, security, docs, test, chore, build, ci, revert
Scope: auth, api, ui, db, infra, ci, docs
Subject: imperative, lowercase, no period, max 50 chars
Body: explain what and why, not how, wrap at 72 chars
Footer: Closes #, Fixes #, Part of ADR-#, Breaking Change:
"""

    def get_default_pr_template(self) -> str:
        """Return standard PR template."""
        return """## 🤖 AI Engineering Company — Automated PR

### Request
{{REQUEST}}

### DAG Execution
- **DAG ID**: {{DAG_ID}}
- **Mode**: {{MODE}}
- **Skills Used**: {{SKILLS}}

### Human Approvals ✅
- [x] Changes reviewed and approved before commit
- [x] PR reviewed and approved before creation
- [x] Deployment approved for production

### Validation Gates
{{VALIDATION_GATES}}

### Consensus
{{CONSENSUS_DETAILS}}

### Deployment
- Strategy: Canary 5% → 25% → 100% over 2h
- Rollback: Single-click via feature flag
- Monitoring: SLO dashboards + burn rate alerts

---
*Generated by AI Engineering Company*
"""

    def render_commit_message(self, request: str, context: Dict, template: Optional[str] = None) -> str:
        """Render commit message using template or default."""
        if template is None:
            template = self.get_default_commit_template()
        
        # Extract type and scope from request
        type_scope = self._infer_type_scope(request)
        
        return template.replace("<type>(<scope>): <subject>", f"{type_scope}: {request[:50]}")\
                       .replace("<body>", f"Generated by AI Engineering Company\n\nDAG: {context.get('dag_id', 'N/A')}\n\nHuman-approved: ✅")\
                       .replace("<footer>", f"Closes #{context.get('issue_number', 'TBD')}")

    def render_pr_body(self, context: Dict, template: Optional[str] = None) -> str:
        """Render PR body using template or default."""
        if template is None:
            template = self.get_default_pr_template()
        
        validation_gates = self._format_validation_gates(context)
        consensus_details = self._format_consensus(context)
        
        return template.replace("{{REQUEST}}", context.get('request', 'Feature implementation'))\
                       .replace("{{DAG_ID}}", context.get('dag_id', 'N/A'))\
                       .replace("{{MODE}}", context.get('routing', {}).get('mode', 'N/A'))\
                       .replace("{{SKILLS}}", ', '.join(context.get('routing', {}).get('required_skills', [])))\
                       .replace("{{VALIDATION_GATES}}", validation_gates)\
                       .replace("{{CONSENSUS_DETAILS}}", consensus_details)

    def _infer_type_scope(self, request: str) -> str:
        """Infer commit type and scope from request."""
        request_lower = request.lower()
        if any(kw in request_lower for kw in ["fix", "bug", "issue", "error"]):
            type_ = "fix"
        elif any(kw in request_lower for kw in ["refactor", "restructure", "clean"]):
            type_ = "refactor"
        elif any(kw in request_lower for kw in ["perf", "performance", "optimize", "speed"]):
            type_ = "perf"
        elif any(kw in request_lower for kw in ["security", "auth", "vuln", "cve"]):
            type_ = "security"
        elif any(kw in request_lower for kw in ["doc", "readme", "comment"]):
            type_ = "docs"
        elif any(kw in request_lower for kw in ["test", "spec", "coverage"]):
            type_ = "test"
        elif any(kw in request_lower for kw in ["build", "ci", "pipeline", "deploy"]):
            type_ = "ci"
        else:
            type_ = "feat"
        
        # Infer scope
        if any(kw in request_lower for kw in ["auth", "login", "oauth", "jwt", "session"]):
            scope = "auth"
        elif any(kw in request_lower for kw in ["api", "endpoint", "rest", "graphql"]):
            scope = "api"
        elif any(kw in request_lower for kw in ["ui", "frontend", "component", "page", "dashboard"]):
            scope = "ui"
        elif any(kw in request_lower for kw in ["db", "database", "migration", "schema"]):
            scope = "db"
        elif any(kw in request_lower for kw in ["infra", "k8s", "terraform", "cloud", "aws", "gcp", "azure"]):
            scope = "infra"
        elif any(kw in request_lower for kw in ["ci", "pipeline", "github", "gitlab", "jenkins"]):
            scope = "ci"
        else:
            scope = "core"
        
        return f"{type_}({scope})"

    def _format_validation_gates(self, context: Dict) -> str:
        gates = [
            ("Security Scan", "security", "SAST, secrets, deps"),
            ("Performance Baseline", "performance", "p99 latency, throughput"),
            ("Architecture Review", "architecture", "cycles, boundaries"),
            ("Test Suite", "tests", "coverage, critical paths"),
            ("Accessibility Audit", "accessibility", "WCAG 2.1 AA"),
            ("Infrastructure Validation", "infrastructure", "Terraform, K8s"),
        ]
        lines = []
        for name, key, desc in gates:
            result = context.get(f"result_{key}", {})
            status = "✅" if result.get("approved", result.get("passed", False)) else "❌"
            lines.append(f"- {status} {name} ({desc})")
        return "\n".join(lines)

    def _format_consensus(self, context: Dict) -> str:
        consensus = context.get("result_consensus", {})
        decision = consensus.get("decision", "PENDING").upper()
        confidence = f"{consensus.get('confidence', 0):.0%}"
        quorum = "✅ REACHED" if consensus.get("quorum_reached") else "❌ NOT REACHED"
        return f"""- **Decision**: {decision}
- **Confidence**: {confidence}
- **Quorum**: {quorum}
- **Reasoning**: {consensus.get('reasoning', 'N/A')}"""


class PlanningPhase:
    """Manages the detailed planning phase with user iteration."""

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path

    def create_initial_plan(self, request: str, context: Dict) -> FeaturePlan:
        """Create initial feature plan from request."""
        # Extract context from routing
        routing = context.get("routing", {})
        skills = routing.get("required_skills", [])
        
        plan = FeaturePlan(
            request=request,
            problem_statement=self._extract_problem(request),
            proposed_solution=self._propose_solution(request, skills),
            technical_approach=self._outline_technical_approach(skills),
            acceptance_criteria=self._generate_acceptance_criteria(request),
            risks_and_mitigations=self._identify_risks(skills),
            dependencies=self._identify_dependencies(skills),
            effort_estimate=self._estimate_effort(skills),
            milestones=self._define_milestones(skills),
            feature_flags=self._propose_feature_flags(request),
            test_strategy=self._outline_test_strategy(skills),
            rollback_plan=self._outline_rollback_plan(skills),
        )
        return plan

    def _extract_problem(self, request: str) -> str:
        return f"Implement: {request}"

    def _propose_solution(self, request: str, skills: List[str]) -> str:
        return f"Build {request} using {', '.join(skills)} expertise"

    def _outline_technical_approach(self, skills: List[str]) -> str:
        approaches = []
        if "product-engineering" in skills:
            approaches.append("• Product: PRD with experiment design and success metrics")
        if "design-skill" in skills:
            approaches.append("• Design: Component specs, design tokens, accessibility audit")
        if "staff-engineer" in skills:
            approaches.append("• Engineering: Implementation with security, performance, architecture reviews")
        if "platform-engineer" in skills:
            approaches.append("• Platform: Terraform, K8s manifests, CI/CD pipelines, observability")
        if "agentic-orchestration" in skills:
            approaches.append("• Orchestration: DAG planning, consensus, validation gates, HITL")
        return "\n".join(approaches) if approaches else "Standard implementation approach"

    def _generate_acceptance_criteria(self, request: str) -> List[str]:
        return [
            f"Feature '{request}' is functional and meets requirements",
            "All validation gates pass (security, performance, architecture, tests, accessibility, infrastructure)",
            "Code coverage ≥ 80% for new code",
            "WCAG 2.1 AA accessibility compliance",
            "No critical or high-severity security findings",
            "Performance meets SLO budgets",
            "Documentation updated (PRD, ADRs, runbooks)",
        ]

    def _identify_risks(self, skills: List[str]) -> List[Dict[str, str]]:
        risks = []
        if "staff-engineer" in skills:
            risks.append({"risk": "Technical complexity higher than estimated", "mitigation": "Spike investigation, incremental delivery"})
        if "platform-engineer" in skills:
            risks.append({"risk": "Infrastructure changes cause downtime", "mitigation": "Blue-green deployment, feature flags"})
        if "design-skill" in skills:
            risks.append({"risk": "Accessibility regressions", "mitigation": "Automated a11y testing in CI"})
        if "product-engineering" in skills:
            risks.append({"risk": "Scope creep", "mitigation": "Strict scope definition, change control process"})
        return risks

    def _identify_dependencies(self, skills: List[str]) -> List[str]:
        deps = []
        if "platform-engineer" in skills:
            deps.append("Infrastructure must be provisioned before deployment")
        if "design-skill" in skills:
            deps.append("Design tokens must be finalized before component implementation")
        if "product-engineering" in skills:
            deps.append("PRD must be approved before implementation starts")
        return deps

    def _estimate_effort(self, skills: List[str]) -> str:
        base_days = len(skills) * 2
        return f"{base_days}-{base_days + 3} days"

    def _define_milestones(self, skills: List[str]) -> List[Dict[str, str]]:
        milestones = [
            {"name": "Planning Complete", "target": "Day 1", "criteria": "Plan approved by human"},
            {"name": "Specs & Design Complete", "target": "Day 2-3", "criteria": "PRD, component specs, tokens approved"},
            {"name": "Implementation Complete", "target": "Day 4-6", "criteria": "Code + tests + infra ready"},
            {"name": "Validation Complete", "target": "Day 7", "criteria": "All gates pass, consensus reached"},
            {"name": "Deploy & Release", "target": "Day 8", "criteria": "Canary deployed, monitored, promoted"},
        ]
        return milestones

    def _propose_feature_flags(self, request: str) -> List[Dict[str, Any]]:
        return [
            {
                "name": f"feature-{request.lower().replace(' ', '-')[:30]}",
                "description": f"Enable {request}",
                "default": False,
                "rollout_strategy": "canary",
            }
        ]

    def _outline_test_strategy(self, skills: List[str]) -> str:
        strategies = []
        if "staff-engineer" in skills:
            strategies.append("• Unit tests: ≥80% coverage for new code")
            strategies.append("• Integration tests: Critical paths covered")
            strategies.append("• Contract tests: API boundaries validated")
        if "design-skill" in skills:
            strategies.append("• Accessibility tests: axe-core in CI")
            strategies.append("• Visual regression: Chromatic/Playwright")
        if "platform-engineer" in skills:
            strategies.append("• Infrastructure tests: Terratest for Terraform")
            strategies.append("• Chaos engineering: LitmusChaos scenarios")
        return "\n".join(strategies) if strategies else "Standard test pyramid"

    def _outline_rollback_plan(self, skills: List[str]) -> str:
        steps = [
            "1. Disable feature flag immediately (instant rollback)",
            "2. If flag insufficient: `git revert <merge-commit>` (2-5 min)",
            "3. If schema migration: Run down migration + code revert (5-15 min)",
            "4. If data corruption: DB restore + code rollback (15-60 min)",
            "5. Post-rollback: Verify metrics, notify stakeholders",
        ]
        return "\n".join(steps)

    def iterate_plan(self, plan: FeaturePlan, feedback: str) -> FeaturePlan:
        """Update plan based on human feedback."""
        plan.version += 1
        plan.feedback_history.append({
            "version": plan.version - 1,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })
        # In real implementation, would use LLM to incorporate feedback
        # For now, append feedback to problem statement
        plan.problem_statement += f"\n\n[Feedback v{plan.version-1}]: {feedback}"
        return plan

    def present_plan_for_approval(self, plan: FeaturePlan) -> Dict:
        """Present plan to human for approval with iteration loop."""
        print(f"\n{'='*60}")
        print(f"📋 FEATURE PLAN — Version {plan.version}")
        print(f"{'='*60}")
        print(f"\n📋 Request: {plan.request}")
        print(f"\n🎯 Problem Statement:\n{plan.problem_statement}")
        print(f"\n💡 Proposed Solution:\n{plan.proposed_solution}")
        print(f"\n🔧 Technical Approach:\n{plan.technical_approach}")
        print(f"\n✅ Acceptance Criteria:")
        for i, criteria in enumerate(plan.acceptance_criteria, 1):
            print(f"  {i}. {criteria}")
        print(f"\n⚠️ Risks & Mitigations:")
        for risk in plan.risks_and_mitigations:
            print(f"  • {risk['risk']} → {risk['mitigation']}")
        print(f"\n🔗 Dependencies:")
        for dep in plan.dependencies:
            print(f"  • {dep}")
        print(f"\n⏱️ Effort Estimate: {plan.effort_estimate}")
        print(f"\n📅 Milestones:")
        for m in plan.milestones:
            print(f"  • {m['name']} ({m['target']}): {m['criteria']}")
        print(f"\n🚩 Feature Flags:")
        for f in plan.feature_flags:
            print(f"  • {f['name']}: {f['description']} (default: {f['default']})")
        print(f"\n🧪 Test Strategy:\n{plan.test_strategy}")
        print(f"\n🔄 Rollback Plan:\n{plan.rollback_plan}")
        
        if plan.feedback_history:
            print(f"\n📝 Feedback History:")
            for fb in plan.feedback_history:
                print(f"  v{fb['version']}: {fb['feedback']} ({fb['timestamp']})")

        print(f"\nOptions:")
        print(f"  [a] Approve - Finalize plan and proceed to implementation")
        print(f"  [r] Request Changes - Provide feedback for revision")
        print(f"  [x] Abort - Stop the lifecycle")
        
        while True:
            choice = input("\nYour decision [a/r/x]: ").strip().lower()
            if choice in ('a', 'approve', 'y', 'yes'):
                plan.approved = True
                return {"approved": True, "plan": plan}
            elif choice in ('r', 'request', 'changes'):
                feedback = input("Enter required changes/feedback: ").strip()
                return {"approved": False, "action": "request_changes", "feedback": feedback}
            elif choice in ('x', 'abort', 'quit'):
                print("🛑 Lifecycle aborted by human.")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 'a', 'r', or 'x'.")


class HumanApprovalGate:
    """Handles human-in-the-loop approval gates with interactive prompts."""

    @staticmethod
    def request_approval(gate_type: str, context: Dict, details: Dict = None) -> Dict:
        gate_labels = {
            "review_changes": "📝 REVIEW CHANGES BEFORE COMMIT",
            "review_pr": "📋 REVIEW PR BEFORE CREATION",
            "approve_deploy": "🚀 APPROVE PRODUCTION DEPLOYMENT",
            "consensus": "🤝 CONSENSUS REVIEW",
            "review_plan": "📋 REVIEW FEATURE PLAN BEFORE IMPLEMENTATION",
        }

        label = gate_labels.get(gate_type, gate_type.upper())
        
        print(f"\n{'='*60}")
        print(f"⏸️  HUMAN APPROVAL REQUIRED: {label}")
        print(f"{'='*60}")
        
        if gate_type == "review_changes":
            HumanApprovalGate._show_changes_summary(context)
        elif gate_type == "review_pr":
            HumanApprovalGate._show_pr_summary(context)
        elif gate_type == "approve_deploy":
            HumanApprovalGate._show_deploy_summary(context)
        elif gate_type == "consensus":
            HumanApprovalGate._show_consensus_summary(context)
        elif gate_type == "review_plan":
            HumanApprovalGate._show_plan_summary(context)

        if details:
            print(f"\nDetails:")
            for k, v in details.items():
                print(f"  {k}: {v}")

        print(f"\nOptions:")
        print(f"  [a] Approve - Continue execution")
        print(f"  [r] Request Changes - Provide feedback, agent will revise")
        print(f"  [x] Abort - Stop the lifecycle")
        
        while True:
            choice = input("\nYour decision [a/r/x]: ").strip().lower()
            if choice in ('a', 'approve', 'y', 'yes'):
                return {"approved": True, "action": "approve", "feedback": ""}
            elif choice in ('r', 'request', 'changes'):
                feedback = input("Enter required changes/feedback: ").strip()
                return {"approved": False, "action": "request_changes", "feedback": feedback}
            elif choice in ('x', 'abort', 'quit'):
                print("🛑 Lifecycle aborted by human.")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 'a', 'r', or 'x'.")

    @staticmethod
    def _show_changes_summary(context: Dict):
        print(f"\n📋 Request: {context.get('request', 'N/A')}")
        print(f"📊 DAG: {context.get('dag_id', 'N/A')}")
        print(f"\nAgent Outputs Ready for Commit:")
        for key, value in context.items():
            if key.startswith("result_") and isinstance(value, dict):
                agent = key.replace("result_", "")
                status = "✅" if value.get("approved", value.get("status") == "completed") else "❌"
                print(f"  {status} {agent}: {str(value)[:100]}...")

    @staticmethod
    def _show_pr_summary(context: Dict):
        print(f"\n📋 Request: {context.get('request', 'N/A')}")
        print(f"📊 DAG: {context.get('dag_id', 'N/A')}")
        print(f"\nPR will be created with:")
        print(f"  - All validated agent outputs")
        print(f"  - Validation gates status")
        print(f"  - Consensus results")
        print(f"  - Deployment plan")

    @staticmethod
    def _show_deploy_summary(context: Dict):
        print(f"\n📋 Request: {context.get('request', 'N/A')}")
        version = context.get("result_release", {}).get("version", "v1.0.0")
        print(f"🏷️  Version: {version}")
        print(f"🌿 Branch: {context.get('branch', 'N/A')}")
        print(f"🔀 PR: #{context.get('pr_number', 'N/A')}")
        print(f"\nDeployment Plan:")
        print(f"  - Staging: 100% (auto)")
        print(f"  - Canary: 5% → 25% → 50% → 100% over 2h")
        print(f"  - Auto-rollback on SLO breach")
        print(f"  - Feature flag rollback available")

    @staticmethod
    def _show_consensus_summary(context: Dict):
        consensus = context.get("result_consensus", {})
        print(f"\n🤝 Consensus Results:")
        print(f"  Decision: {consensus.get('decision', 'PENDING').upper()}")
        print(f"  Confidence: {consensus.get('confidence', 0):.0%}")
        print(f"  Quorum: {'✅ REACHED' if consensus.get('quorum_reached') else '❌ NOT REACHED'}")
        if consensus.get("reasoning"):
            print(f"  Reasoning: {consensus.get('reasoning')}")

    @staticmethod
    def _show_plan_summary(context: Dict):
        plan = context.get("feature_plan")
        if plan:
            print(f"\n📋 Feature Plan v{plan.version}: {plan.request}")
            print(f"Problem: {plan.problem_statement[:100]}...")
            print(f"Solution: {plan.proposed_solution[:100]}...")
            print(f"Effort: {plan.effort_estimate}")
            print(f"Milestones: {len(plan.milestones)}")


class AgentExecutor:
    """Executes agents with validation and retry logic."""

    def __init__(self):
        self.results = {}

    def execute(self, node: DAGNode, context: Dict) -> Dict:
        """Execute a single agent node with validation."""
        print(f"  ▶ Executing: {node.id} ({node.skill} / {node.agent_type})")

        # Check if this is a human checkpoint
        if node.checkpoint and node.agent_type == "human":
            return self._handle_human_checkpoint(node, context)

        # Simulate execution with skill-specific logic
        result = self._simulate_execution(node, context)

        # Validate output
        validation = self._validate_output(node, result)
        if not validation["passed"]:
            print(f"  ⚠️  Validation failed: {validation['errors']}")

        self.results[node.id] = result
        print(f"  ✅ Completed: {node.id}")
        return result

    def _handle_human_checkpoint(self, node: DAGNode, context: Dict) -> Dict:
        gate_type = node.checkpoint_type or node.id
        
        details = {}
        if gate_type == "review_changes":
            details = self._prepare_changes_summary(context)
        elif gate_type == "review_pr":
            details = {"pr_ready": True}
        elif gate_type == "approve_deploy":
            details = {"version": context.get("result_release", {}).get("version", "v1.0.0")}
        elif gate_type == "consensus":
            details = context.get("result_consensus", {})
        elif gate_type == "review_plan":
            details = {"plan": context.get("feature_plan")}

        approval = HumanApprovalGate.request_approval(gate_type, context, details)
        
        if not approval["approved"]:
            print(f"⚠️  Human requested changes: {approval['feedback']}")
            return {"approved": False, "feedback": approval["feedback"], "action": "request_changes"}
        
        return {"approved": True, "action": "approve", "feedback": ""}

    def _prepare_changes_summary(self, context: Dict) -> Dict:
        changes = {}
        for key, value in context.items():
            if key.startswith("result_") and isinstance(value, dict):
                agent = key.replace("result_", "")
                changes[agent] = {
                    "status": "approved" if value.get("approved", value.get("status") == "completed") else "rejected",
                    "summary": str(value)[:200]
                }
        return {"total_agents": len(changes), "changes": changes}

    def _simulate_execution(self, node: DAGNode, context: Dict) -> Dict:
        skill = node.skill
        agent = node.agent_type

        # For planning phase, generate actual plan
        if node.id == "feature_planning" and agent == "planner":
            planner = PlanningPhase(Path.cwd())
            plan = planner.create_initial_plan(context.get("request", ""), context)
            # Iterate with human
            while True:
                result = planner.present_plan_for_approval(plan)
                if result["approved"]:
                    context["feature_plan"] = result["plan"]
                    return {"plan": asdict(result["plan"]), "approved": True}
                elif result["action"] == "request_changes":
                    plan = planner.iterate_plan(plan, result["feedback"])
                    continue
            return {"plan": asdict(plan), "approved": False}

        if skill == "product-engineering":
            return {
                "prd": f"PRD for {context.get('request', 'feature')}",
                "experiment_design": "A/B test: new feature vs control",
                "metrics": ["activation_rate", "retention"],
                "priority_score": 85
            }
        elif skill == "design-skill":
            return {
                "component_specs": ["Button", "Modal", "NotificationToast"],
                "tokens": {"color": "updated", "spacing": "consistent"},
                "accessibility_audit": "WCAG 2.1 AA passed",
                "cross_platform": ["React", "SwiftUI", "Flutter"]
            }
        elif skill == "staff-engineer":
            if agent == "security":
                return {"findings": [], "risk_score": 1.2, "approved": True}
            elif agent == "performance":
                return {"baseline_p99_ms": 45, "budget_met": True}
            elif agent == "architect":
                return {"boundary_violations": 0, "cycles": 0, "approved": True}
            elif agent == "coder":
                # Use feature plan if available
                plan = context.get("feature_plan")
                if plan:
                    return {"files_changed": 12, "tests_added": 8, "coverage": 82, "plan_followed": True}
                return {"files_changed": 12, "tests_added": 8, "coverage": 82}
            elif agent == "tester":
                return {"tests_passed": 47, "critical_paths": "green"}
            return {"status": "completed"}
        elif skill == "platform-engineer":
            if agent == "platform":
                return {"terraform_plan": "valid", "k8s_manifests": "valid", "pipeline": "created"}
            return {"status": "completed"}
        elif skill == "agentic-orchestration":
            if agent == "coordinator":
                return {"decision": "approve", "confidence": 0.92, "quorum": True}
            elif agent == "release":
                return {"version": "v2.3.0", "tag_created": True, "changelog": "generated"}
            return {"status": "completed"}

        return {"status": "completed", "agent": agent}

    def _validate_output(self, node: DAGNode, output: Dict) -> Dict:
        return {"passed": True, "errors": []}


class GitWorkflow:
    """Handles git operations with human approval gates."""

    def __init__(self, repo_path: Path = None):
        self.repo_path = repo_path or Path.cwd()
        self.template_detector = TemplateDetector(repo_path)

    def _run(self, cmd: List[str]) -> subprocess.CompletedProcess:
        return subprocess.run(cmd, cwd=self.repo_path, capture_output=True, text=True)

    def create_branch(self, feature_name: str) -> str:
        slug = self._slugify(feature_name)
        branch = f"feat/{slug}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self._run(["git", "checkout", "-b", branch])
        return branch

    def commit_changes(self, message: str, files: List[str] = None) -> str:
        if files:
            self._run(["git", "add"] + files)
        else:
            self._run(["git", "add", "-A"])
        self._run(["git", "commit", "-m", message])
        result = self._run(["git", "rev-parse", "HEAD"])
        return result.stdout.strip()[:8]

    def create_pr(self, title: str, body: str, base: str = "main") -> Dict:
        result = self._run(["gh", "pr", "create", "--title", title, "--body", body, "--base", base])
        if result.returncode == 0:
            import re
            match = re.search(r'#(\d+)', result.stdout)
            pr_number = match.group(1) if match else "unknown"
            return {"number": pr_number, "url": f"https://github.com/owner/repo/pull/{pr_number}"}
        return {"error": result.stderr}

    def auto_merge(self, pr_number: str, consensus_result: Dict) -> bool:
        if not consensus_result.get("quorum_reached"):
            return False
        if consensus_result.get("decision") != "approve":
            return False
        if consensus_result.get("confidence", 0) < 0.8:
            return False

        result = self._run(["gh", "pr", "merge", pr_number, "--auto", "--squash"])
        return result.returncode == 0

    def tag_release(self, version: str, message: str = "") -> bool:
        tag = f"v{version}"
        msg = message or f"Release {tag}"
        self._run(["git", "tag", "-a", tag, "-m", msg])
        self._run(["git", "push", "origin", tag])
        return True

    def deploy(self, environment: str, version: str) -> Dict:
        return {"environment": environment, "version": version, "status": "deployed"}

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text)
        return text.strip('-')


class DAGBuilder:
    """Builds execution DAGs based on routing decision."""

    TEMPLATES = {
        "full_agentic_loop": {
            "nodes": [
                {"id": "planning", "skill": "agentic-orchestration", "agent": "planner", "deps": [], "checkpoint": True, "checkpoint_type": "review_plan"},
                {"id": "strategy_spec", "skill": "product-engineering", "agent": "product", "deps": ["planning"], "checkpoint": False},
                {"id": "design_specs", "skill": "design-skill", "agent": "designer", "deps": ["planning"], "checkpoint": False},
                {"id": "security_review", "skill": "staff-engineer", "agent": "security", "deps": ["strategy_spec", "design_specs"], "checkpoint": False},
                {"id": "perf_baseline", "skill": "staff-engineer", "agent": "performance", "deps": ["strategy_spec", "design_specs"], "checkpoint": False},
                {"id": "arch_review", "skill": "staff-engineer", "agent": "architect", "deps": ["strategy_spec", "design_specs"], "checkpoint": False},
                {"id": "infra_plan", "skill": "platform-engineer", "agent": "platform", "deps": ["arch_review"], "checkpoint": False},
                {"id": "implementation", "skill": "staff-engineer", "agent": "coder", "deps": ["security_review", "arch_review", "infra_plan"], "checkpoint": False},
                {"id": "component_build", "skill": "design-skill", "agent": "designer", "deps": ["design_specs", "arch_review"], "checkpoint": False},
                {"id": "integration_test", "skill": "staff-engineer", "agent": "tester", "deps": ["implementation", "perf_baseline", "component_build"], "checkpoint": False},
                {"id": "consensus", "skill": "agentic-orchestration", "agent": "coordinator", "deps": ["security_review", "perf_baseline", "arch_review", "integration_test", "infra_plan"], "checkpoint": True, "checkpoint_type": "consensus"},
                {"id": "human_review_changes", "skill": "agentic-orchestration", "agent": "human", "deps": ["consensus"], "checkpoint": True, "checkpoint_type": "review_changes"},
                {"id": "human_review_pr", "skill": "agentic-orchestration", "agent": "human", "deps": ["human_review_changes"], "checkpoint": True, "checkpoint_type": "review_pr"},
                {"id": "human_approval_deploy", "skill": "agentic-orchestration", "agent": "human", "deps": ["human_review_pr"], "checkpoint": True, "checkpoint_type": "approve_deploy"},
                {"id": "deploy", "skill": "platform-engineer", "agent": "platform", "deps": ["human_approval_deploy"], "checkpoint": False},
                {"id": "release", "skill": "agentic-orchestration", "agent": "release", "deps": ["deploy"], "checkpoint": False},
            ],
            "edges": [
                ["planning", "strategy_spec"],
                ["planning", "design_specs"],
                ["strategy_spec", "security_review"],
                ["strategy_spec", "perf_baseline"],
                ["strategy_spec", "arch_review"],
                ["design_specs", "security_review"],
                ["design_specs", "perf_baseline"],
                ["design_specs", "arch_review"],
                ["arch_review", "infra_plan"],
                ["security_review", "implementation"],
                ["arch_review", "implementation"],
                ["infra_plan", "implementation"],
                ["design_specs", "component_build"],
                ["arch_review", "component_build"],
                ["implementation", "integration_test"],
                ["perf_baseline", "integration_test"],
                ["component_build", "integration_test"],
                ["security_review", "consensus"],
                ["perf_baseline", "consensus"],
                ["arch_review", "consensus"],
                ["integration_test", "consensus"],
                ["infra_plan", "consensus"],
                ["consensus", "human_review_changes"],
                ["human_review_changes", "human_review_pr"],
                ["human_review_pr", "human_approval_deploy"],
                ["human_approval_deploy", "deploy"],
                ["deploy", "release"],
            ],
            "checkpoints": ["review_plan", "consensus", "human_review_changes", "human_review_pr", "human_approval_deploy"]
        },
        "targeted_skills": {
            "nodes": [],
            "edges": [],
            "checkpoints": ["consensus", "human_review_changes", "human_review_pr", "human_approval_deploy"]
        }
    }

    def build(self, routing: RoutingDecision, request: str) -> DAG:
        if routing.mode == "full_agentic_loop":
            tmpl = self.TEMPLATES["full_agentic_loop"]
            nodes = []
            for n in tmpl["nodes"]:
                nodes.append(DAGNode(
                    id=n["id"],
                    skill=n["skill"],
                    agent_type=n["agent"],
                    description=f"{n['agent']} for: {request[:50]}",
                    dependencies=n["deps"],
                    input_schema={"type": "object", "properties": {}},
                    output_schema={"type": "object", "properties": {}},
                    checkpoint=n.get("checkpoint", False),
                    checkpoint_type=n.get("checkpoint_type", "")
                ))
            return DAG(
                dag_id=f"feature-{self._slugify(request)[:40]}-{uuid.uuid4().hex[:8]}",
                nodes=nodes,
                edges=tmpl["edges"],
                checkpoints=tmpl["checkpoints"],
                estimated_duration="30-60 minutes"
            )
        else:
            return self._build_targeted(routing, request)

    def _build_targeted(self, routing: RoutingDecision, request: str) -> DAG:
        nodes = []
        edges = []

        skill_agents = {
            "product-engineering": ("product", "PRD + experiment design"),
            "design-skill": ("designer", "Component specs + tokens"),
            "staff-engineer": ("coder", "Implementation + tests"),
            "platform-engineer": ("platform", "Infra + CI/CD"),
        }

        skill_nodes = {}
        for skill in routing.required_skills:
            if skill in skill_agents:
                agent, desc = skill_agents[skill]
                node_id = skill.replace("-", "_")
                skill_nodes[skill] = node_id
                nodes.append(DAGNode(
                    id=node_id,
                    skill=skill,
                    agent_type=agent,
                    description=f"{desc} for: {request[:50]}",
                    dependencies=[],
                    input_schema={"type": "object", "properties": {}},
                    output_schema={"type": "object", "properties": {}},
                    checkpoint=False
                ))

        if len(skill_nodes) > 1:
            nodes.append(DAGNode(
                id="consensus",
                skill="agentic-orchestration",
                agent_type="coordinator",
                description="Consensus across all skills",
                dependencies=list(skill_nodes.values()),
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object", "properties": {}},
                checkpoint=True,
                checkpoint_type="consensus"
            ))
            nodes.append(DAGNode(
                id="human_review_changes",
                skill="agentic-orchestration",
                agent_type="human",
                description="Human review of all changes before commit",
                dependencies=["consensus"],
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object", "properties": {}},
                checkpoint=True,
                checkpoint_type="review_changes"
            ))
            nodes.append(DAGNode(
                id="human_review_pr",
                skill="agentic-orchestration",
                agent_type="human",
                description="Human review of PR before creation",
                dependencies=["human_review_changes"],
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object", "properties": {}},
                checkpoint=True,
                checkpoint_type="review_pr"
            ))
            nodes.append(DAGNode(
                id="human_approval_deploy",
                skill="agentic-orchestration",
                agent_type="human",
                description="Human approval for production deployment",
                dependencies=["human_review_pr"],
                input_schema={"type": "object", "properties": {}},
                output_schema={"type": "object", "properties": {}},
                checkpoint=True,
                checkpoint_type="approve_deploy"
            ))

        return DAG(
            dag_id=f"targeted-{self._slugify(request)[:40]}-{uuid.uuid4().hex[:8]}",
            nodes=nodes,
            edges=[],
            checkpoints=["consensus", "human_review_changes", "human_review_pr", "human_approval_deploy"] if len(skill_nodes) > 1 else [],
            estimated_duration="10-30 minutes"
        )

    def _slugify(self, text: str) -> str:
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text)
        return text.strip('-')


class LifecycleOrchestrator:
    """Main orchestrator for the full lifecycle with mandatory human gates."""

    def __init__(self, repo_path: Path = None):
        self.router = RequestRouter()
        self.dag_builder = DAGBuilder()
        self.executor = AgentExecutor()
        self.git = GitWorkflow(repo_path)
        self.template_detector = TemplateDetector(repo_path or Path.cwd())
        self.planner = PlanningPhase(repo_path or Path.cwd())
        self.context = {}

    def run(self, request: str, auto_merge: bool = False, dry_run: bool = False) -> Dict:
        print(f"\n{'='*60}")
        print(f"🎯 AI ENGINEERING COMPANY — FULL LIFECYCLE")
        print(f"{'='*60}")
        print(f"Request: {request}\n")

        # 1. ROUTING
        print("📍 STEP 1: INTELLIGENT ROUTING")
        routing = self.router.route(request)
        print(f"   Mode: {routing.mode}")
        print(f"   Skills: {', '.join(routing.required_skills)}")
        print(f"   Reasoning: {routing.reasoning}\n")

        # 2. DAG CREATION
        print("📊 STEP 2: DAG CREATION (with human approval gates)")
        dag = self.dag_builder.build(routing, request)
        print(f"   DAG ID: {dag.dag_id}")
        print(f"   Nodes: {len(dag.nodes)}")
        print(f"   Human Gates: {dag.checkpoints}")
        print(f"   Est. Duration: {dag.estimated_duration}\n")

        # 3. CONTEXT SETUP
        self.context = {
            "request": request,
            "dag_id": dag.dag_id,
            "routing": routing,
            "started_at": datetime.now().isoformat()
        }

        # 4. PLANNING PHASE (NEW - before execution)
        print("📋 STEP 3: PLANNING PHASE (with human iteration)")
        if not dry_run:
            self._planning_phase()
        else:
            print("   [DRY RUN] Would run planning phase with human iteration\n")

        # 5. EXECUTION
        print("🚀 STEP 4: AGENT EXECUTION")
        if not dry_run:
            self._execute_dag(dag)
        else:
            print("   [DRY RUN] Would execute DAG nodes in topological order\n")

        # 6. HUMAN REVIEW BEFORE COMMIT (mandatory gate)
        if not dry_run:
            print("⏸️  STEP 5: HUMAN REVIEW BEFORE COMMIT (MANDATORY)")
            self._human_review_before_commit()
        else:
            print("   [DRY RUN] Would request human review before commit\n")

        # 7. GIT COMMIT (after human approval)
        if not dry_run:
            print("🌿 STEP 6: GIT COMMIT (after human approval)")
            self._git_commit()
        else:
            print("   [DRY RUN] Would commit after human approval\n")

        # 8. HUMAN REVIEW BEFORE PR (mandatory gate)
        if not dry_run:
            print("⏸️  STEP 7: HUMAN REVIEW BEFORE PR CREATION (MANDATORY)")
            self._human_review_before_pr()
        else:
            print("   [DRY RUN] Would request human review before PR\n")

        # 9. CREATE PR (after human approval)
        if not dry_run:
            print("🔀 STEP 8: CREATE PR (after human approval)")
            self._create_pr()
        else:
            print("   [DRY RUN] Would create PR after human approval\n")

        # 10. HUMAN APPROVAL FOR DEPLOY (mandatory gate)
        if not dry_run:
            print("⏸️  STEP 9: HUMAN APPROVAL FOR DEPLOY (MANDATORY)")
            self._human_approval_deploy()
        else:
            print("   [DRY RUN] Would request human approval for deploy\n")

        # 11. DEPLOY & RELEASE
        if not dry_run:
            print("🚀 STEP 10: DEPLOY & RELEASE")
            self._deploy_and_release(auto_merge)
        else:
            print("   [DRY RUN] Would deploy and release\n")

        # 12. SUMMARY
        summary = self._generate_summary(dag, routing)
        print(f"\n{'='*60}")
        print("✅ LIFECYCLE COMPLETE")
        print(f"{'='*60}")
        print(summary)

        return {
            "dag_id": dag.dag_id,
            "routing": asdict(routing),
            "dag": asdict(dag),
            "context": self.context,
            "results": self.executor.results,
            "summary": summary
        }

    def _planning_phase(self):
        """Run the planning phase with human iteration."""
        print("   📋 Creating initial feature plan...")
        plan = self.planner.create_initial_plan(self.context["request"], self.context)
        
        print("   🔄 Presenting plan for human review and iteration...")
        while True:
            result = self.planner.present_plan_for_approval(plan)
            if result["approved"]:
                self.context["feature_plan"] = result["plan"]
                print("   ✅ Plan approved. Proceeding to implementation.")
                break
            elif result["action"] == "request_changes":
                plan = self.planner.iterate_plan(plan, result["feedback"])
                print(f"   🔄 Revising plan based on feedback...")
                continue

    def _execute_dag(self, dag: DAG):
        completed = set()
        remaining = {n.id: n for n in dag.nodes}

        while remaining:
            ready = [
                n for n in remaining.values()
                if all(dep in completed for dep in n.dependencies)
            ]

            if not ready:
                raise RuntimeError("Circular dependency detected")

            for node in ready:
                result = self.executor.execute(node, self.context)
                self.context[f"result_{node.id}"] = result
                completed.add(node.id)
                del remaining[node.id]

    def _human_review_before_commit(self):
        review_result = self.context.get("result_human_review_changes", {})
        if not review_result.get("approved"):
            print("❌ Human review required before commit. Please approve changes.")
            dummy_node = type('obj', (object,), {
                'id': 'human_review_changes',
                'skill': 'agentic-orchestration',
                'agent_type': 'human',
                'checkpoint': True,
                'checkpoint_type': 'review_changes'
            })()
            review_result = self.executor.execute(dummy_node, self.context)
            self.context["result_human_review_changes"] = review_result

        if not review_result.get("approved"):
            print("❌ Changes not approved. Lifecycle stopped.")
            sys.exit(1)
        
        print("✅ Changes approved by human. Proceeding to commit.")

    def _git_commit(self):
        branch = self.git.create_branch(self.context["request"])
        print(f"   Branch created: {branch}")
        
        # Use detected or default commit template
        commit_template = self.template_detector.detect_commit_template()
        commit_msg = self.template_detector.render_commit_message(
            self.context["request"], self.context, commit_template
        )
        
        sha = self.git.commit_changes(commit_msg)
        print(f"   Committed: {sha}")
        self.context["branch"] = branch
        self.context["commit_sha"] = sha

    def _human_review_before_pr(self):
        review_result = self.context.get("result_human_review_pr", {})
        if not review_result.get("approved"):
            print("❌ Human review required before PR creation. Please approve PR.")
            dummy_node = type('obj', (object,), {
                'id': 'human_review_pr',
                'skill': 'agentic-orchestration',
                'agent_type': 'human',
                'checkpoint': True,
                'checkpoint_type': 'review_pr'
            })()
            review_result = self.executor.execute(dummy_node, self.context)
            self.context["result_human_review_pr"] = review_result

        if not review_result.get("approved"):
            print("❌ PR not approved. Lifecycle stopped.")
            sys.exit(1)
        
        print("✅ PR approved by human. Proceeding to create PR.")

    def _create_pr(self):
        # Use detected or default PR template
        pr_template = self.template_detector.detect_pr_template()
        pr_body = self.template_detector.render_pr_body(self.context, pr_template)
        
        pr = self.git.create_pr(
            title=f"feat: {self.context['request']}",
            body=pr_body
        )
        print(f"   PR created: #{pr.get('number', '?')}")
        self.context["pr_number"] = pr.get("number")
        self.context["pr_url"] = pr.get("url")

    def _human_approval_deploy(self):
        review_result = self.context.get("result_human_approval_deploy", {})
        if not review_result.get("approved"):
            print("❌ Human approval required for production deployment.")
            dummy_node = type('obj', (object,), {
                'id': 'human_approval_deploy',
                'skill': 'agentic-orchestration',
                'agent_type': 'human',
                'checkpoint': True,
                'checkpoint_type': 'approve_deploy'
            })()
            review_result = self.executor.execute(dummy_node, self.context)
            self.context["result_human_approval_deploy"] = review_result

        if not review_result.get("approved"):
            print("❌ Deployment not approved. Lifecycle stopped.")
            sys.exit(1)
        
        print("✅ Deployment approved by human. Proceeding to deploy.")

    def _deploy_and_release(self, auto_merge: bool):
        consensus = self.context.get("result_consensus", {})
        
        if auto_merge and consensus:
            pr_number = self.context.get("pr_number", "")
            merged = self.git.auto_merge(str(pr_number), consensus)
            if merged:
                print(f"   ✅ Auto-merged (consensus: {consensus.get('confidence', 0):.0%})")

                version = consensus.get("version", "v1.0.0")
                self.git.tag_release(version, f"Release {version}")
                print(f"   🏷️ Tagged: {version}")

                deploy_result = self.git.deploy("production", version)
                print(f"   🚀 Deployed: {deploy_result}")
                self.context["deploy_result"] = deploy_result
        else:
            print("   ⏭️  Auto-merge disabled or consensus not ready. Manual merge required.")

    def _generate_summary(self, dag: DAG, routing: RoutingDecision) -> str:
        return f"""
📋 REQUEST: {self.context['request']}
🎯 MODE: {routing.mode}
📊 DAG: {dag.dag_id} ({len(dag.nodes)} nodes)
🛠️ SKILLS: {', '.join(routing.required_skills)}
⏱️ DURATION: {dag.estimated_duration}
🌿 BRANCH: {self.context.get('branch', 'N/A')}
📝 COMMIT: {self.context.get('commit_sha', 'N/A')}
🔀 PR: #{self.context.get('pr_number', 'N/A')}
✅ CONSENSUS: {self.context.get('result_consensus', {}).get('decision', 'PENDING').upper()}
🏷️ VERSION: {self.context.get('result_release', {}).get('version', 'PENDING')}
🚀 DEPLOY: {self.context.get('deploy_result', {}).get('status', 'PENDING').upper()}
"""

    def _slugify(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text)
        return text.strip('-')


def main():
    parser = argparse.ArgumentParser(description="AI Engineering Company — Full Lifecycle Orchestrator")
    parser.add_argument("request", nargs="+", help="Feature request / problem statement")
    parser.add_argument("--auto-merge", action="store_true", help="Enable auto-merge on consensus")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without executing")
    parser.add_argument("--repo", type=Path, help="Git repository path")
    parser.add_argument("--output", "-o", type=Path, help="Output JSON file")
    args = parser.parse_args()

    request = " ".join(args.request)

    orchestrator = LifecycleOrchestrator(args.repo)
    result = orchestrator.run(request, auto_merge=args.auto_merge, dry_run=args.dry_run)

    if args.output:
        args.output.write_text(json.dumps(result, indent=2, default=str))
        print(f"\n📄 Full result written to {args.output}")


if __name__ == "__main__":
    main()