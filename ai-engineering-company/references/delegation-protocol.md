# Delegation Protocol — Agent Contracts, Handoffs, Validation

## Overview
This document defines the protocol for delegating work to specialized agents, including task contracts, context handoffs, validation gates, and consensus mechanisms.

## Agent Contract System

### Contract Structure (JSON Schema)
Every agent receives and returns structured data conforming to explicit schemas.

```json
{
  "agent_id": "security_review",
  "skill": "staff-engineer",
  "agent_type": "security",
  "input_schema": {
    "type": "object",
    "required": ["spec", "code_paths"],
    "properties": {
      "spec": {"type": "string", "description": "Feature specification/PRD"},
      "code_paths": {"type": "array", "items": {"type": "string"}, "description": "Files to review"},
      "arch_decisions": {"type": "object", "description": "Architecture decisions from arch_review"}
    }
  },
  "output_schema": {
    "type": "object",
    "required": ["findings", "risk_score", "approved"],
    "properties": {
      "findings": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["severity", "category", "description"],
          "properties": {
            "severity": {"type": "string", "enum": ["critical", "major", "minor"]},
            "category": {"type": "string"},
            "file": {"type": "string"},
            "line": {"type": "integer"},
            "description": {"type": "string"},
            "fix": {"type": "string"}
          }
        }
      },
      "risk_score": {"type": "number", "minimum": 0, "maximum": 10},
      "approved": {"type": "boolean"},
      "summary": {"type": "string"}
    }
  },
  "timeout_seconds": 300,
  "retry_policy": {"max_attempts": 2, "backoff": "exponential"}
}
```

### Standard Agent Contracts

| Agent | Input | Output | Timeout |
|-------|-------|--------|---------|
| **planner** | task, context | DAG | 60s |
| **security** | spec, code_paths, arch_decisions | findings[], risk_score, approved | 300s |
| **performance** | spec, code_paths, arch_decisions | baseline_metrics, budgets, approved | 600s |
| **architect** | spec, code_paths | decisions[], violations[], approved | 300s |
| **coder** | spec, security_findings, arch_decisions, perf_budgets | code_paths[], test_results, coverage | 1800s |
| **designer** | spec, arch_decisions | component_specs, tokens, a11y_audit | 600s |
| **tester** | spec, code_paths, perf_baseline | test_results, coverage, critical_paths_passed | 600s |
| **coordinator** | all_reports | decision, confidence, reasoning | 120s |
| **platform** | arch_decisions, spec | terraform, k8s, pipeline | 600s |

## Context Handoff Protocol

### Compression Levels (L1-L4)

| Level | Tokens | Use Case | Content |
|-------|--------|----------|---------|
| **L1** | <500 | Coordinator → Human | Task ID, decision, next steps, blockers |
| **L2** | <1500 | Security → Coder | L1 + critical findings (file:line) |
| **L3** | <3000 | Default agent→agent | L2 + major findings summary, token diff, decisions |
| **L4** | Full | Debugging only | Complete transcripts |

### Handoff Format (Markdown)
```markdown
# Agent Handoff: security_review → implementation

## Task
Implement real-time notifications (WebSocket + fallback)

## Decisions Made
- Use Redis Pub/Sub for message broker (ADR-047)
- JWT auth with 15min access / 7d refresh tokens
- Feature flag: `realtime-notifications` (default off)

## Critical Findings (Must Address)
- [ ] SEV-1: No rate limiting on WebSocket connections (security_review:finding-3)
- [ ] SEV-2: Missing input validation on message payload (security_review:finding-7)

## Major Findings (Should Address)
- Connection pooling needed for Redis (perf_baseline:finding-2)
- Consider exponential backoff for reconnection (arch_review:finding-5)

## Constraints
- Budget: <50ms p99 latency, <10MB memory per connection
- Must support 100k concurrent connections
- Backward compatible with HTTP long-polling fallback

## Artifacts
- Spec: @spec.md
- Threat Model: @threat-model.md
- Perf Baseline: @perf-baseline.json
- ADR: @adr/0047-redis-pubsub.md
```

### Compression Algorithm
```python
def compress_context(source: Context, target_tokens: int, level: str) -> HandoffBrief:
    """
    1. Score all content by relevance (semantic similarity + recency + criticality + centrality)
    2. Keep critical findings at full fidelity
    3. Summarize major findings (one-line + file:line + fix)
    4. Drop minor findings (count only)
    5. Preserve: decisions, token diffs, next steps, constraints
    6. Truncate preserving structure (headings, code blocks, tables)
    """
```

## Validation Gates

Every agent output passes through three validation gates before downstream consumption:

### Gate 1: Schema Validation (Deterministic, Fast)
```python
def validate_schema(output: Dict, schema: Dict) -> ValidationResult:
    """JSON Schema validation — fails fast on structure violations."""
    # Uses jsonschema library
    # Returns: passed, errors[]
```

### Gate 2: Policy Validation (OPA/Rego Style)
```python
def validate_policy(output: Dict, policies: List[Policy]) -> ValidationResult:
    """Business rule validation — security, cost, compliance."""
    # Examples:
    # - No hardcoded secrets
    # - Resource limits defined
    # - Cost < $X/month
    # - No deprecated APIs
```

### Gate 3: Critic Validation (LLM-Based Adversarial)
```python
def validate_critic(output: Dict, task: TaskSpec) -> ValidationResult:
    """Adversarial review — correctness, patterns, edge cases."""
    # Runs specialized critic agent with prompts like:
    # "Find security issues in this code"
    # "Find performance anti-patterns"
    # "Find correctness bugs"
    # "Check consistency with existing codebase"
```

### Validation Pipeline
```
Agent Output
    │
    ├─► Gate 1: Schema Validator (ms)
    │       └─ FAIL → Return to agent with schema errors
    │
    ├─► Gate 2: Policy Checker (ms)
    │       └─ FAIL → Return with policy violations
    │
    ├─► Gate 3: Critic Agent (seconds)
    │       └─ FAIL → Return with issues + suggested fixes
    │
    └─► PASS → Available for downstream agents
```

## Consensus Protocol

### Weighted Voting
```python
def weighted_consensus(votes: List[Vote], weights: Dict[str, float], quorum: float = 0.66) -> ConsensusResult:
    """
    votes: [{"agent": "security", "decision": "approve", "confidence": 0.9, "reasoning": "..."}, ...]
    weights: {"security": 0.3, "architect": 0.3, "performance": 0.2, "tester": 0.2}
    """
    # Check vetoes first
    for vote in votes:
        if vote.agent in veto_agents and vote.decision == "reject":
            return ConsensusResult(decision="reject", veto=True, ...)

    approve_weight = sum(w for v, w in zip(votes, weights.values()) if v.decision == "approve")
    reject_weight = sum(w for v, w in zip(votes, weights.values()) if v.decision == "reject")
    total_weight = sum(weights.values())

    if approve_weight / total_weight >= quorum:
        return approve
    elif reject_weight / total_weight >= quorum:
        return reject
    else:
        return escalate
```

### Decision-Type Specific Weights

| Decision Type | Quorum | Weights | Veto Agents |
|---------------|--------|---------|-------------|
| Security Approval | 75% | Sec: 40%, Arch: 30%, Perf: 15%, Test: 15% | Security |
| Architecture | 66% | Arch: 40%, Sec: 20%, Perf: 20%, Test: 20% | — |
| Performance Budget | 66% | Perf: 40%, Arch: 20%, Sec: 20%, Test: 20% | — |
| Production Deploy | 80% | All equal (25%) | Security, Architect |

### Conflict Resolution
1. **Automatic**: Quorum reached → proceed
2. **Mediated**: Coordinator synthesizes, proposes compromise
3. **Escalated**: Human checkpoint with full context
4. **Veto**: Security/Architect can veto (configurable)

## Retry with Feedback

```python
def execute_with_validation(node: DAGNode, context: Context) -> AgentOutput:
    for attempt in range(node.retry_policy.max_attempts):
        output = node.agent.execute(context)
        validation = validate(output, node)
        if validation.passed:
            return output
        # Inject feedback into context for retry
        context = context.add_feedback(node.agent, validation.issues)
        if attempt < node.retry_policy.max_attempts - 1:
            wait(node.retry_policy.backoff(attempt))
    raise ValidationFailed(f"Agent {node.agent} failed after {attempt+1} attempts")
```

## Observability Requirements

Every agent execution must emit:

```json
{
  "trace_id": "abc123",
  "span_id": "def456",
  "agent": "security_review",
  "task_id": "feature-2847",
  "dag_node": "security_review",
  "input_tokens": 2847,
  "output_tokens": 1203,
  "duration_ms": 45230,
  "model": "claude-3.5-sonnet",
  "temperature": 0.1,
  "validation": {"gate1": true, "gate2": true, "gate3": true, "issues": []},
  "consensus": null,
  "checkpoint": false
}
```

### Key Metrics
| Metric | Target |
|--------|--------|
| Agent success rate (first attempt) | >95% |
| Context compression ratio | >10:1 |
| Consensus time | <5min |
| Human checkpoint latency | <30min business hours |
| End-to-end task time | <30min typical |
| Token cost per task | Track & budget |