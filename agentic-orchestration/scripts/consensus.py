#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Consensus Engine — Weighted voting, quorum checking, conflict resolution for multi-agent decisions.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class Decision(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    ESCALATE = "escalate"


@dataclass
class Vote:
    agent: str
    decision: Decision
    confidence: float
    reasoning: str
    weight: float = 1.0


@dataclass
class ConsensusResult:
    decision: Decision
    confidence: float
    quorum_reached: bool
    total_weight: float
    approve_weight: float
    reject_weight: float
    votes: List[Vote]
    reasoning: str


class ConsensusEngine:
    def __init__(self, weights: Dict[str, float], quorum: float = 0.66, veto_agents: List[str] = None):
        self.weights = weights
        self.quorum = quorum
        self.veto_agents = veto_agents or []

    def compute(self, votes: List[Vote]) -> ConsensusResult:
        """Compute consensus from votes."""
        # Apply weights
        for vote in votes:
            vote.weight = self.weights.get(vote.agent, 1.0)
        
        total_weight = sum(v.weight for v in votes)
        approve_weight = sum(v.weight for v in votes if v.decision == Decision.APPROVE)
        reject_weight = sum(v.weight for v in votes if v.decision == Decision.REJECT)
        
        # Check veto
        for vote in votes:
            if vote.agent in self.veto_agents and vote.decision == Decision.REJECT:
                return ConsensusResult(
                    decision=Decision.REJECT,
                    confidence=1.0,
                    quorum_reached=True,
                    total_weight=total_weight,
                    approve_weight=approve_weight,
                    reject_weight=reject_weight,
                    votes=votes,
                    reasoning=f"Veto by {vote.agent}: {vote.reasoning}"
                )
        
        # Check quorum
        approve_ratio = approve_weight / total_weight if total_weight > 0 else 0
        reject_ratio = reject_weight / total_weight if total_weight > 0 else 0
        
        if approve_ratio >= self.quorum:
            decision = Decision.APPROVE
            confidence = approve_ratio
            quorum_reached = True
            reasoning = f"Quorum reached: {approve_ratio:.1%} approve weight ({approve_weight}/{total_weight})"
        elif reject_ratio >= self.quorum:
            decision = Decision.REJECT
            confidence = reject_ratio
            quorum_reached = True
            reasoning = f"Quorum reached: {reject_ratio:.1%} reject weight ({reject_weight}/{total_weight})"
        else:
            decision = Decision.ESCALATE
            confidence = 0.0
            quorum_reached = False
            reasoning = f"Quorum not reached: approve={approve_ratio:.1%}, reject={reject_ratio:.1%} (need {self.quorum:.1%})"
        
        return ConsensusResult(
            decision=decision,
            confidence=confidence,
            quorum_reached=quorum_reached,
            total_weight=total_weight,
            approve_weight=approve_weight,
            reject_weight=reject_weight,
            votes=votes,
            reasoning=reasoning
        )


# Predefined consensus rules for different decision types
CONSENSUS_RULES = {
    "security_approval": {
        "quorum": 0.75,
        "weights": {"security": 0.4, "architect": 0.3, "performance": 0.15, "tester": 0.15},
        "veto_agents": ["security"]
    },
    "architecture": {
        "quorum": 0.66,
        "weights": {"architect": 0.4, "security": 0.2, "performance": 0.2, "tester": 0.2},
        "veto_agents": []
    },
    "performance_budget": {
        "quorum": 0.66,
        "weights": {"performance": 0.4, "architect": 0.2, "security": 0.2, "tester": 0.2},
        "veto_agents": []
    },
    "production_deploy": {
        "quorum": 0.80,
        "weights": {"security": 0.25, "architect": 0.25, "performance": 0.25, "tester": 0.25},
        "veto_agents": ["security", "architect"]
    },
    "refactor_approval": {
        "quorum": 0.75,
        "weights": {"security": 0.4, "architect": 0.3, "tester": 0.3},
        "veto_agents": ["security"]
    }
}


def load_votes(votes_file: Path) -> List[Dict]:
    """Load votes from JSON file."""
    with open(votes_file) as f:
        data = json.load(f)
    
    votes = []
    for v in data:
        votes.append({
            "agent": v["agent"],
            "decision": v["decision"],
            "confidence": v.get("confidence", 1.0),
            "reasoning": v.get("reasoning", ""),
        })
    return votes


def load_weights(weights_file: Path) -> Dict[str, float]:
    """Load weights from YAML or JSON file."""
    import yaml
    with open(weights_file) as f:
        if weights_file.suffix in (".yaml", ".yml"):
            return yaml.safe_load(f)
        else:
            return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Compute consensus from agent votes")
    parser.add_argument("--votes", required=True, type=Path, help="Votes JSON file")
    parser.add_argument("--weights", type=Path, help="Weights YAML/JSON file")
    parser.add_argument("--quorum", type=float, default=0.66, help="Quorum threshold (default: 0.66)")
    parser.add_argument("--veto", nargs="*", help="Agent IDs with veto power")
    parser.add_argument("--rule", choices=list(CONSENSUS_RULES.keys()), help="Use predefined consensus rule")
    parser.add_argument("--output", "-o", type=Path, help="Output file")
    parser.add_argument("--format", choices=["json", "text"], default="text", help="Output format")
    args = parser.parse_args()

    # Load votes
    votes_data = load_votes(args.votes)
    votes = []
    for v in votes_data:
        votes.append({
            "agent": v["agent"],
            "decision": v["decision"],
            "confidence": v.get("confidence", 1.0),
            "reasoning": v.get("reasoning", ""),
        })

    # Determine weights and rules
    if args.rule:
        rule = CONSENSUS_RULES[args.rule]
        weights = rule["weights"]
        quorum = rule["quorum"]
        veto_agents = rule["veto_agents"]
    else:
        weights = load_weights(args.weights) if args.weights else {}
        quorum = args.quorum
        veto_agents = args.veto or []

    # Ensure all voting agents have weights
    for v in votes:
        if v["agent"] not in weights:
            weights[v["agent"]] = 1.0

    # Create vote objects
    vote_objects = []
    for v in votes:
        vote_objects.append({
            "agent": v["agent"],
            "decision": Decision(v["decision"]),
            "confidence": v["confidence"],
            "reasoning": v["reasoning"],
            "weight": weights.get(v["agent"], 1.0)
        })

    # Compute consensus
    engine = ConsensusEngine(weights, quorum, veto_agents)
    result = engine.compute(vote_objects)

    # Output
    if args.format == "json":
        output = asdict(result)
        output["decision"] = result.decision.value
        output["votes"] = [asdict(v) for v in result.votes]
    else:
        output = f"""Consensus Result
================
Decision: {result.decision.value.upper()}
Confidence: {result.confidence:.1%}
Quorum Reached: {'YES' if result.quorum_reached else 'NO'}
Quorum Threshold: {quorum:.1%}

Weight Summary:
  Total Weight: {result.total_weight:.2f}
  Approve Weight: {result.approve_weight:.2f} ({result.approve_weight/result.total_weight:.1%})
  Reject Weight: {result.reject_weight:.2f} ({result.reject_weight/result.total_weight:.1%})

Reasoning: {result.reasoning}

Votes:
"""
        for v in result.votes:
            output += f"  {v.agent} ({v.weight:.2f}): {v.decision.value} (confidence: {v.confidence:.1%}) - {v.reasoning}\n"

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Result written to {args.output}")
    else:
        print(output)

    # Exit code based on decision
    if result.decision == Decision.REJECT:
        sys.exit(2)
    elif result.decision == Decision.ESCALATE:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()