#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Decomposer — Converts natural language task descriptions into executable DAGs.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DAGNode:
    id: str
    agent_type: str
    description: str
    dependencies: List[str]
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    timeout_seconds: int = 300
    retry_policy: Dict[str, Any] = None
    checkpoint: bool = False

    def __post_init__(self):
        if self.retry_policy is None:
            self.retry_policy = {"max_attempts": 2, "backoff": "exponential"}


@dataclass
class DAG:
    dag_id: str
    version: str
    nodes: List[DAGNode]
    edges: List[List[str]]
    checkpoints: List[str]
    consensus_rules: Dict[str, Dict[str, Any]]


class TaskDecomposer:
    """Decomposes tasks into DAGs using built-in patterns."""

    # Standard agent types with their schemas
    AGENT_SCHEMAS = {
        "security": {
            "input": {
                "type": "object",
                "properties": {
                    "spec": {"type": "string"},
                    "code_paths": {"type": "array", "items": {"type": "string"}},
                    "arch_decisions": {"type": "object"}
                },
                "required": ["spec"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "findings": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
                                "category": {"type": "string"},
                                "file": {"type": "string"},
                                "line": {"type": "integer"},
                                "description": {"type": "string"},
                                "fix": {"type": "string"}
                            },
                            "required": ["severity", "category", "description"]
                        }
                    },
                    "risk_score": {"type": "number", "minimum": 0, "maximum": 10},
                    "approved": {"type": "boolean"},
                    "summary": {"type": "string"}
                },
                "required": ["findings", "risk_score", "approved", "summary"]
            }
        },
        "performance": {
            "input": {
                "type": "object",
                "properties": {
                    "spec": {"type": "string"},
                    "code_paths": {"type": "array", "items": {"type": "string"}},
                    "arch_decisions": {"type": "object"}
                },
                "required": ["spec"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "baseline_metrics": {"type": "object"},
                    "budgets": {"type": "object"},
                    "bottlenecks": {"type": "array"},
                    "recommendations": {"type": "array"},
                    "approved": {"type": "boolean"}
                },
                "required": ["baseline_metrics", "budgets", "approved"]
            }
        },
        "architect": {
            "input": {
                "type": "object",
                "properties": {
                    "spec": {"type": "string"},
                    "code_paths": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["spec"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "decisions": {"type": "array"},
                    "boundary_violations": {"type": "array"},
                    "coupling_metrics": {"type": "object"},
                    "diagram": {"type": "string"},
                    "approved": {"type": "boolean"}
                },
                "required": ["decisions", "boundary_violations", "approved"]
            }
        },
        "coder": {
            "input": {
                "type": "object",
                "properties": {
                    "spec": {"type": "string"},
                    "security_findings": {"type": "array"},
                    "arch_decisions": {"type": "object"},
                    "perf_budgets": {"type": "object"}
                },
                "required": ["spec"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "code_paths": {"type": "array", "items": {"type": "string"}},
                    "test_results": {"type": "object"},
                    "artifacts": {"type": "array"},
                    "coverage": {"type": "number"}
                },
                "required": ["code_paths", "test_results"]
            }
        },
        "tester": {
            "input": {
                "type": "object",
                "properties": {
                    "spec": {"type": "string"},
                    "code_paths": {"type": "array", "items": {"type": "string"}},
                    "perf_baseline": {"type": "object"}
                },
                "required": ["spec", "code_paths"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "test_results": {"type": "object"},
                    "coverage": {"type": "number"},
                    "critical_paths_passed": {"type": "boolean"},
                    "artifacts": {"type": "array"}
                },
                "required": ["test_results", "critical_paths_passed"]
            }
        },
        "coordinator": {
            "input": {
                "type": "object",
                "properties": {
                    "all_reports": {"type": "object"}
                },
                "required": ["all_reports"]
            },
            "output": {
                "type": "object",
                "properties": {
                    "decision": {"type": "string", "enum": ["approve", "reject", "escalate"]},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                    "reasoning": {"type": "string"}
                },
                "required": ["decision", "confidence", "reasoning"]
            }
        }
    }

    # Standard DAG templates
    TEMPLATES = {
        "feature": {
            "nodes": [
                {"id": "security_review", "agent": "security", "deps": [], "checkpoint": False},
                {"id": "perf_baseline", "agent": "performance", "deps": [], "checkpoint": False},
                {"id": "arch_review", "agent": "architect", "deps": [], "checkpoint": False},
                {"id": "implementation", "agent": "coder", "deps": ["security_review", "arch_review"], "checkpoint": False},
                {"id": "integration_test", "agent": "tester", "deps": ["implementation", "perf_baseline"], "checkpoint": False},
                {"id": "consensus", "agent": "coordinator", "deps": ["security_review", "perf_baseline", "arch_review", "integration_test"], "checkpoint": True},
            ],
            "consensus_rules": {
                "consensus": {
                    "quorum": 0.66,
                    "weights": {"security": 0.3, "architect": 0.3, "performance": 0.2, "tester": 0.2}
                }
            }
        },
        "refactor": {
            "nodes": [
                {"id": "analyze_codebase", "agent": "architect", "deps": [], "checkpoint": False},
                {"id": "identify_candidates", "agent": "coder", "deps": ["analyze_codebase"], "checkpoint": False},
                {"id": "risk_assessment", "agent": "security", "deps": ["analyze_codebase"], "checkpoint": False},
                {"id": "refactor", "agent": "coder", "deps": ["identify_candidates", "risk_assessment"], "checkpoint": False},
                {"id": "validate", "agent": "tester", "deps": ["refactor"], "checkpoint": False},
                {"id": "consensus", "agent": "coordinator", "deps": ["risk_assessment", "validate"], "checkpoint": True},
            ],
            "consensus_rules": {
                "consensus": {
                    "quorum": 0.75,
                    "weights": {"security": 0.4, "architect": 0.3, "tester": 0.3}
                }
            }
        },
        "incident": {
            "nodes": [
                {"id": "triage", "agent": "architect", "deps": [], "checkpoint": False},
                {"id": "diagnose", "agent": "coder", "deps": ["triage"], "checkpoint": False},
                {"id": "impact_assessment", "agent": "performance", "deps": ["triage"], "checkpoint": False},
                {"id": "mitigate", "agent": "coder", "deps": ["diagnose", "impact_assessment"], "checkpoint": False},
                {"id": "verify", "agent": "tester", "deps": ["mitigate"], "checkpoint": False},
                {"id": "postmortem", "agent": "coordinator", "deps": ["verify"], "checkpoint": True},
            ],
            "consensus_rules": {
                "postmortem": {
                    "quorum": 0.66,
                    "weights": {"architect": 0.4, "performance": 0.3, "tester": 0.3}
                }
            }
        }
    }

    def __init__(self):
        self.agent_schemas = self.AGENT_SCHEMAS
        self.templates = self.TEMPLATES

    def detect_template(self, task: str) -> str:
        """Detect which template to use based on task description."""
        task_lower = task.lower()
        if any(kw in task_lower for kw in ["refactor", "rewrite", "restructure", "modernize"]):
            return "refactor"
        elif any(kw in task_lower for kw in ["incident", "outage", "bug", "fix", "debug", "hotfix"]):
            return "incident"
        else:
            return "feature"

    def decompose(self, task: str, context: str = "", template: str = None) -> DAG:
        """Decompose task into DAG."""
        if template is None:
            template = self.detect_template(task)
        
        if template not in self.templates:
            template = "feature"
        
        tmpl = self.templates[template]
        dag_id = f"{template}-{self._slugify(task)[:50]}"
        
        nodes = []
        for n in tmpl["nodes"]:
            agent_type = n["agent"]
            schemas = self.agent_schemas.get(agent_type, {})
            
            node = DAGNode(
                id=n["id"],
                agent_type=agent_type,
                description=self._generate_description(agent_type, task),
                dependencies=n["deps"],
                input_schema=schemas.get("input", {"type": "object", "properties": {}}),
                output_schema=schemas.get("output", {"type": "object", "properties": {}}),
                timeout_seconds=self._get_timeout(agent_type),
                retry_policy={"max_attempts": 2, "backoff": "exponential"},
                checkpoint=n.get("checkpoint", False)
            )
            nodes.append(node)
        
        # Build edges from dependencies
        edges = []
        for n in tmpl["nodes"]:
            for dep in n["deps"]:
                edges.append([dep, n["id"]])
        
        return DAG(
            dag_id=dag_id,
            version="1.0",
            nodes=nodes,
            edges=edges,
            checkpoints=[n["id"] for n in tmpl["nodes"] if n.get("checkpoint")],
            consensus_rules=tmpl.get("consensus_rules", {})
        )

    def _generate_description(self, agent_type: str, task: str) -> str:
        descriptions = {
            "security": f"Security review for: {task}",
            "performance": f"Performance baseline and budget for: {task}",
            "architect": f"Architecture review for: {task}",
            "coder": f"Implementation of: {task}",
            "tester": f"Integration and contract testing for: {task}",
            "coordinator": f"Consensus and final decision for: {task}",
        }
        return descriptions.get(agent_type, f"{agent_type} task for: {task}")

    def _get_timeout(self, agent_type: str) -> int:
        timeouts = {
            "security": 300,
            "performance": 600,
            "architect": 300,
            "coder": 1800,
            "tester": 600,
            "coordinator": 120,
        }
        return timeouts.get(agent_type, 300)

    def _slugify(self, text: str) -> str:
        import re
        text = text.lower()
        text = re.sub(r'[^a-z0-9\s-]', '', text)
        text = re.sub(r'[\s-]+', '-', text)
        return text.strip('-')


def main():
    parser = argparse.ArgumentParser(description="Decompose task into DAG")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--context", help="Additional context (file path or string)")
    parser.add_argument("--template", choices=["feature", "refactor", "incident"], help="Force template")
    parser.add_argument("--output", "-o", help="Output file (JSON)")
    parser.add_argument("--format", choices=["json", "yaml"], default="json", help="Output format")
    args = parser.parse_args()

    context = ""
    if args.context:
        path = Path(args.context)
        if path.exists():
            context = path.read_text(encoding="utf-8")
        else:
            context = args.context

    decomposer = TaskDecomposer()
    dag = decomposer.decompose(args.task, context, args.template)

    # Convert to dict for output
    output = {
        "dag_id": dag.dag_id,
        "version": dag.version,
        "nodes": [asdict(n) for n in dag.nodes],
        "edges": dag.edges,
        "checkpoints": dag.checkpoints,
        "consensus_rules": dag.consensus_rules,
        "created_at": datetime.now().isoformat(),
    }

    if args.format == "yaml":
        import yaml
        result = yaml.dump(output, sort_keys=False, default_flow_style=False)
    else:
        result = json.dumps(output, indent=2, default=str)

    if args.output:
        Path(args.output).write_text(result, encoding="utf-8")
        print(f"DAG written to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()