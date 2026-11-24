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

## Mandatory Human Approval Gates

The AI Engineering Company enforces **three mandatory human approval gates** that no automated process can bypass:

### Gate 1: Review Changes Before Commit
- **When**: After all agent execution completes, before `git commit`
- **What Human Reviews**:
  - All agent outputs (PRD, specs, code, tests, infra plans)
  - Validation gate results (security, perf, arch, tests, a11y, infra)
  - File diffs and change summaries
- **Required**: ✅ Yes — No commit without explicit approval
- **On Reject**: Human provides feedback → agents revise → re-review

### Gate 2: Review PR Before Creation
- **When**: After commit, before `gh pr create`
- **What Human Reviews**:
  - PR title and body (generated template)
  - Validation gate statuses
  - Consensus results and confidence
  - Deployment plan summary
- **Required**: ✅ Yes — No PR created without explicit approval
- **On Reject**: Human provides feedback → PR body revised → re-review

### Gate 3: Approve Production Deployment
- **When**: After consensus approval, before production deploy
- **What Human Reviews**:
  - Version and release notes
  - PR link and consensus results
  - Deployment plan (canary steps, rollback plan)
  - SLO thresholds and rollback triggers
- **Required**: ✅ Yes — No production deploy without explicit approval
- **On Reject**: Deployment cancelled; lifecycle stops

### Gate Implementation (Python)
```python
class HumanApprovalGate:
    @staticmethod
    def request_approval(gate_type: str, context: Dict, details: Dict = None) -> Dict:
        """Interactive prompt for human approval."""
        gate_labels = {
            "review_changes": "📝 REVIEW CHANGES BEFORE COMMIT",
            "review_pr": "📋 REVIEW PR BEFORE CREATION",
            "approve_deploy": "🚀 APPROVE PRODUCTION DEPLOYMENT"
        }
        
        print(f"⏸️  HUMAN APPROVAL REQUIRED: {gate_labels[gate_type]}")
        # Show context-specific summary...
        
        while True:
            choice = input("Your decision [a/r/x]: ").strip().lower()
            if choice in ('a', 'approve', 'y', 'yes'):
                return {"approved": True, "action": "approve"}
            elif choice in ('r', 'request', 'changes'):
                feedback = input("Required changes: ").strip()
                return {"approved": False, "action": "request_changes", "feedback": feedback}
            elif choice in ('x', 'abort'):
                sys.exit(0)
```

### Gate Enforcement in DAG
```python
# DAG nodes with mandatory human checkpoints
nodes = [
    {"id": "consensus", "checkpoint": True, "checkpoint_type": "consensus"},
    {"id": "human_review_changes", "checkpoint": True, "checkpoint_type": "review_changes", "deps": ["consensus"]},
    {"id": "human_review_pr", "checkpoint": True, "checkpoint_type": "review_pr", "deps": ["human_review_changes"]},
    {"id": "human_approval_deploy", "checkpoint": True, "checkpoint_type": "approve_deploy", "deps": ["human_review_pr"]},
    {"id": "deploy", "deps": ["human_approval_deploy"]},
]
```

**No commit, PR, or deployment proceeds without explicit human approval at each gate.**

## Planning Phase Protocol (NEW)

Before any implementation begins, a **detailed feature plan** must be created, reviewed, and approved by a human. This ensures alignment, catches issues early, and provides a clear implementation roadmap.

### Planning Phase Flow

```python
class PlanningPhase:
    def create_initial_plan(self, request: str, context: Dict) -> FeaturePlan:
        """Create structured plan from request."""
        return FeaturePlan(
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
    
    def present_plan_for_approval(self, plan: FeaturePlan) -> Dict:
        """Interactive human review with iteration loop."""
        while True:
            print(f"📋 FEATURE PLAN v{plan.version}: {plan.request}")
            # Display: problem, solution, approach, criteria, risks, milestones, flags, test strategy, rollback
            
            choice = input("[a] Approve  [r] Request Changes  [x] Abort: ")
            if choice == 'a':
                plan.approved = True
                return {"approved": True, "plan": plan}
            elif choice == 'r':
                feedback = input("Required changes: ")
                plan = self.iterate_plan(plan, feedback)
            elif choice == 'x':
                sys.exit(0)
```

### Feature Plan Structure

```python
@dataclass
class FeaturePlan:
    request: str
    problem_statement: str
    proposed_solution: str
    technical_approach: str
    acceptance_criteria: List[str]
    risks_and_mitigations: List[Dict[str, str]]
    dependencies: List[str]
    effort_estimate: str
    milestones: List[Dict[str, str]]
    feature_flags: List[Dict[str, Any]]
    adr_references: List[str]
    test_strategy: str
    rollback_plan: str
    approved: bool = False
    version: int = 1
    feedback_history: List[Dict[str, str]] = field(default_factory=list)
```

### Plan Review Checklist (Human)

- [ ] **Problem Statement**: Clear, specific, measurable
- [ ] **Proposed Solution**: Addresses problem, feasible
- [ ] **Technical Approach**: Uses appropriate skills, follows patterns
- [ ] **Acceptance Criteria**: Specific, measurable, testable
- [ ] **Risks & Mitigations**: Realistic, actionable
- [ ] **Dependencies**: Identified, manageable
- [ ] **Effort Estimate**: Realistic, includes buffer
- [ ] **Milestones**: Clear, time-bound, measurable
- [ ] **Feature Flags**: Named, described, default off
- [ ] **Test Strategy**: Unit, integration, contract, a11y
- [ ] **Rollback Plan**: Feature flag → git revert → DB rollback

### Iteration Loop

```
Human reviews plan
    │
    ├─▶ Approve → Proceed to implementation
    │
    └─▶ Request Changes
            │
            ▼
        Agent incorporates feedback
            │
            ▼
        Plan version incremented
            │
            ▼
        Re-present to human
            │
            ▼
        (Repeat until approved)
```

## Template Detection Protocol (NEW)

The system automatically detects and uses project-specific templates:

### Commit Message Templates

Search order (first match wins):
1. `.github/commit-message.txt`
2. `.gitmessage`
3. `.gitmessage.txt`
4. `commit-template.txt`
5. `.commit-template`

**Fallback**: Standard Conventional Commits format

```python
class TemplateDetector:
    COMMIT_TEMPLATE_PATHS = [
        ".github/commit-message.txt",
        ".gitmessage",
        ".gitmessage.txt",
        "commit-template.txt",
        ".commit-template",
    ]
    
    def detect_commit_template(self) -> Optional[str]:
        for path in self.COMMIT_TEMPLATE_PATHS:
            full_path = self.repo_path / path
            if full_path.exists():
                return full_path.read_text()
        return None
    
    def render_commit_message(self, request: str, context: Dict, template: str = None) -> str:
        if template is None:
            template = self.get_default_commit_template()
        type_scope = self._infer_type_scope(request)
        return template.replace("<type>(<scope>): <subject>", f"{type_scope}: {request[:50]}")
```

### PR Description Templates

Search order:
1. `.github/pull_request_template.md`
2. `.github/PULL_REQUEST_TEMPLATE.md`
3. `PULL_REQUEST_TEMPLATE.md`
4. `pull_request_template.md`

**Fallback**: Standard PR template with gates, consensus, deployment plan

### Commit Convention Detection

Search order:
1. `.github/commit-convention.md`
2. `COMMIT_CONVENTION.md`
3. `.commit-convention`

Used to validate commit messages and guide template rendering.

## Feature Flags & Rollback Protocol (NEW)

Every feature implementation includes feature flag management:

### Feature Flag Specification

```python
feature_flags = [
    {
        "name": "feature-realtime-notifications",
        "description": "Enable real-time WebSocket notifications",
        "default": False,           # Always off by default
        "rollout_strategy": "canary",  # canary, progressive, instant
        "targeting": {},            # Optional: user segments, environments
        "owner": "platform-team",
        "expiry": "2026-12-31",     # Optional: auto-cleanup date
    }
]
```

### Rollback Hierarchy (Fastest to Slowest)

| Method | Time | Data Risk | When |
|--------|------|-----------|------|
| **Feature Flag Off** | <1 min | None | Feature bug, flag exists |
| **Git Revert** | 2-5 min | Low | Code bug, no flag |
| **DB Migration Down + Code Revert** | 5-15 min | Medium | Schema migration issue |
| **Full DB Restore + Code Revert** | 15-60 min | High | Data corruption |

### Rollback Plan Template (in Feature Plan)

```markdown
## Rollback Plan
1. **Feature Flag**: Disable `feature-xyz` in LaunchDarkly/Unleash (instant)
2. **Code Revert**: `git revert <merge-sha> -m 1` → auto-redeploy
3. **DB Rollback**: Run down migration `migrate down 1` + code revert
4. **Full Restore**: Restore DB from backup + code revert (last resort)

### Verification Steps
- [ ] Error rates return to baseline
- [ ] Latency returns to baseline  
- [ ] Business metrics normalize
- [ ] No error budget burn
```

## Architecture Decision Records (NEW)

Every significant technical decision is recorded as an ADR.

### ADR Format

```markdown
# ADR-001: Use Redis Pub/Sub for Real-time Notifications

## Status
Accepted

## Context
Need real-time message delivery for notification feature. 
Options: Redis Pub/Sub, RabbitMQ, Kafka, Server-Sent Events.

## Decision
Use Redis Pub/Sub with fallback to HTTP long-polling.

## Consequences
### Positive
- Low latency (<5ms)
- Simple operations (Redis already in stack)
- Built-in pub/sub semantics

### Negative
- No message persistence (acceptable for notifications)
- Single point of failure (mitigated by Redis Sentinel)

## Alternatives Considered
- RabbitMQ: More complex ops, overkill for pub/sub
- Kafka: Overkill, higher latency
- SSE: No bidirectional, browser limits

## Related
- PR #247
- Feature plan v3
```

### ADR Template

```markdown
# ADR-XXX: [Title]

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
[What situation demands a decision?]

## Decision
[What we decided to do]

## Consequences
### Positive
- [Benefit 1]
- [Benefit 2]

### Negative
- [Drawback 1]
- [Mitigation]

## Alternatives Considered
- [Option 1]: [Why rejected]
- [Option 2]: [Why rejected]

## Related
- [PR #, Issue #, Feature plan version]
```

### ADR Integration in Workflow

1. **During Planning**: Identify decisions needing ADRs
2. **During Architecture Review**: Create ADRs for key decisions
3. **In PR Description**: Link relevant ADRs
4. **In Feature Plan**: Reference ADRs for context
5. **In Handoffs**: Include ADR references for downstream agents

### ADR Storage

```
adr/
├── 001-use-redis-pubsub.md
├── 002-adopt-event-sourcing.md
├── 003-migrate-to-postgresql.md
└── 004-deprecate-legacy-auth.md
```

Naming: `NNN-kebab-case-title.md` (zero-padded, sequential)

## Updated DAG with New Phases

```python
# Full agentic loop DAG with all phases
nodes = [
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
]
```

**Total Gates: 5 (Plan, Consensus, Changes, PR, Deploy)**

---

*End of Delegation Protocol — All agents must follow these protocols for consistent, safe, and auditable execution.*