# Orchestration Patterns

## DAG-Based Task Decomposition

### Core Concepts
A **Directed Acyclic Graph (DAG)** represents the task workflow where:
- **Nodes** = Atomic units of work assigned to specialized agents
- **Edges** = Dependencies (data flow, ordering constraints)
- **No cycles** — Enables topological sort for execution order

### DAG Schema (JSON)
```json
{
  "dag_id": "feature-realtime-notifications",
  "version": "1.0",
  "nodes": [
    {
      "id": "security_review",
      "agent_type": "security",
      "description": "Threat model, OWASP scan, secrets detection",
      "dependencies": [],
      "input_schema": { "type": "object", "properties": { "spec": { "type": "string" } }, "required": ["spec"] },
      "output_schema": { "type": "object", "properties": { "findings": { "type": "array" }, "risk_score": { "type": "number" }, "approved": { "type": "boolean" } }, "required": ["findings", "risk_score", "approved"] },
      "timeout_seconds": 300,
      "retry_policy": { "max_attempts": 2, "backoff": "exponential" },
      "checkpoint": false
    },
    {
      "id": "implementation",
      "agent_type": "coder",
      "description": "Implement WebSocket server + Redis Pub/Sub + FE integration",
      "dependencies": ["security_review", "arch_review"],
      "input_schema": { "type": "object", "properties": { "spec": { "type": "string" }, "security_findings": { "type": "array" }, "arch_decisions": { "type": "object" } }, "required": ["spec"] },
      "output_schema": { "type": "object", "properties": { "code_paths": { "type": "array", "items": { "type": "string" } }, "test_results": { "type": "object" }, "artifacts": { "type": "array" } }, "required": ["code_paths", "test_results"] },
      "timeout_seconds": 1800,
      "retry_policy": { "max_attempts": 3, "backoff": "exponential" },
      "checkpoint": false
    },
    {
      "id": "consensus",
      "agent_type": "coordinator",
      "description": "Aggregate all reviews, weighted voting, final decision",
      "dependencies": ["security_review", "perf_baseline", "arch_review", "integration_test"],
      "input_schema": { "type": "object", "properties": { "all_reports": { "type": "object" } }, "required": ["all_reports"] },
      "output_schema": { "type": "object", "properties": { "decision": { "type": "string", "enum": ["approve", "reject", "escalate"] }, "confidence": { "type": "number" }, "reasoning": { "type": "string" } }, "required": ["decision", "confidence", "reasoning"] },
      "timeout_seconds": 120,
      "retry_policy": { "max_attempts": 1 },
      "checkpoint": true
    }
  ],
  "edges": [
    ["security_review", "implementation"],
    ["arch_review", "implementation"],
    ["implementation", "integration_test"],
    ["perf_baseline", "integration_test"],
    ["security_review", "consensus"],
    ["perf_baseline", "consensus"],
    ["arch_review", "consensus"],
    ["integration_test", "consensus"]
  ],
  "checkpoints": ["consensus"],
  "consensus_rules": {
    "consensus": { "quorum": 0.66, "weights": { "security": 0.3, "arch": 0.3, "perf": 0.2, "test": 0.2 } }
  }
}
```

### Decomposition Principles

#### 1. Single Responsibility per Node
Each node handles exactly one concern:
- `security_review` → Only security
- `perf_baseline` → Only performance
- `arch_review` → Only architecture
- `implementation` → Only coding
- `integration_test` → Only testing
- `consensus` → Only decision synthesis

#### 2. Explicit Contracts
Every node declares:
- **Input Schema**: What it needs (validated before execution)
- **Output Schema**: What it produces (validated after execution)
- **Dependencies**: Explicit DAG edges, not implicit

#### 3. Parallelizability
Nodes with no shared dependencies run simultaneously:
```
security_review    perf_baseline    arch_review
       │                │                │
       └───────┬────────┴────────┬──────┘
               ▼
        implementation
               │
               ▼
        integration_test
               │
               ▼
           consensus
```

#### 4. Checkpointability
State saved after each node enables:
- **Resume** from failure point
- **Replay** with modified inputs
- **Audit** trail for compliance

## Agent Registry

### Standard Agent Types
| Agent ID | Type | Focus | Tools | Validation |
|----------|------|-------|-------|------------|
| `planner` | Planning | Task → DAG | LLM + schema | DAG validity, no cycles |
| `security` | Specialist | Threat model, OWASP, secrets | SAST, dep scan, threat model | Zero critical, ≤2 major |
| `performance` | Specialist | Profiling, load test, budgets | Benchmarks, flame graphs | Meets SLO, no regression |
| `architect` | Specialist | Coupling, boundaries, ADRs | Arch analysis, Mermaid | Zero cycles, ≤5 boundary violations |
| `coder` | Specialist | Implementation, tests | Language tools, test runner | Tests pass, coverage ≥80% |
| `tester` | Specialist | Integration, contract, E2E | Testcontainers, Pact, Playwright | Critical paths green |
| `critic` | Adversarial | Red-team, fuzzing, mutation | Property tests, fuzzers | Finds ≥1 issue or explicit pass |
| `coordinator` | Synthesis | Consensus, weighted voting | Voting algorithms, conflict resolution | Quorum achieved |

### Agent Definition (YAML)
```yaml
# agents/security.yaml
name: security
description: "Security review specialist — threat modeling, OWASP, secrets"
model: claude-3.5-sonnet  # or gpt-4o, gemini-1.5-pro
temperature: 0.1
tools:
  - scan-security.py
  - threat-model.md
  - owasp-top10.md
  - cwe-top25.md
input_schema:
  type: object
  properties:
    spec: { type: string }
    code_paths: { type: array, items: { type: string } }
    arch_decisions: { type: object }
  required: [spec]
output_schema:
  type: object
  properties:
    findings:
      type: array
      items:
        type: object
        properties:
          severity: { type: string, enum: [critical, major, minor] }
          category: { type: string }
          file: { type: string }
          line: { type: integer }
          description: { type: string }
          fix: { type: string }
        required: [severity, category, description]
    risk_score: { type: number, minimum: 0, maximum: 10 }
    approved: { type: boolean }
    summary: { type: string }
  required: [findings, risk_score, approved, summary]
timeout_seconds: 300
retry_policy:
  max_attempts: 2
  backoff: exponential
  base_delay_seconds: 10
```

### Agent Discovery & Loading
```python
class AgentRegistry:
    def __init__(self, agents_dir: Path):
        self.agents = {}
        self.load_agents(agents_dir)
    
    def load_agents(self, agents_dir: Path):
        for agent_file in agents_dir.glob("*.yaml"):
            with open(agent_file) as f:
                spec = yaml.safe_load(f)
            self.agents[spec["name"]] = AgentSpec(**spec)
    
    def get(self, name: str) -> AgentSpec:
        if name not in self.agents:
            raise ValueError(f"Unknown agent: {name}")
        return self.agents[name]
    
    def list_by_type(self, agent_type: str) -> List[AgentSpec]:
        return [a for a in self.agents.values() if a.type == agent_type]
```

## Coordination Patterns

### 1. Parallel Fan-Out / Fan-In
```
         ┌─► security_review
         │
    ┌───► perf_baseline ──► integration_test ──► consensus
    │     │
    │     └─► arch_review
    │
    ▼
implementation
```
- **Fan-out**: Multiple independent nodes from single parent
- **Fan-in**: Multiple nodes converge to single consumer
- **Synchronization**: `integration_test` waits for ALL predecessors

### 2. Pipeline (Sequential)
```
planner → decomposer → validator → executor → reviewer → consensus
```
- Each node depends on exactly one predecessor
- Simple but slower — no parallelism

### 3. Scatter-Gather (Map-Reduce)
```
          ┌─► process_shard_1
scatter ──┼─► process_shard_2
          └─► process_shard_N
                    │
                    ▼
               gather (merge results)
```
- Dynamic fan-out based on input size
- Useful for: file processing, batch analysis, test sharding

### 4. Human-in-the-Loop Checkpoint
```
consensus ──► [HUMAN CHECKPOINT] ──► deploy
```
- Execution pauses at checkpoint node
- Human reviews context, votes Approve/Reject/Request Changes
- Timeout → auto-reject or escalate

## State Management

### Checkpoint State (Persisted)
```json
{
  "dag_id": "feature-realtime-notifications",
  "execution_id": "exec-abc123",
  "status": "running",
  "current_node": "implementation",
  "completed_nodes": ["security_review", "perf_baseline", "arch_review"],
  "node_results": {
    "security_review": {
      "status": "completed",
      "output": { "findings": [...], "risk_score": 2.3, "approved": true },
      "duration_ms": 45230,
      "tokens": { "input": 2847, "output": 1203 }
    }
  },
  "checkpoints": {
    "consensus": { "status": "pending", "requested_at": "2026-11-20T10:00:00Z" }
  },
  "created_at": "2026-11-20T09:55:00Z",
  "updated_at": "2026-11-20T10:00:15Z"
}
```

### Replay from Checkpoint
```python
def replay_from(execution_id: str, from_node: str, modified_inputs: Dict = None):
    """
    1. Load checkpoint state
    2. Truncate completed_nodes at from_node
    3. Apply modified_inputs if provided
    4. Resume execution from from_node
    5. Preserve all prior node results
    """
```

---

## Validation & Quality Gates

### Pre-Execution Validation
```python
def validate_dag(dag: DAG) -> ValidationResult:
    errors = []
    
    # 1. No cycles
    if has_cycle(dag.edges):
        errors.append("DAG contains cycles")
    
    # 2. All dependencies exist
    node_ids = {n.id for n in dag.nodes}
    for from_id, to_id in dag.edges:
        if from_id not in node_ids or to_id not in node_ids:
            errors.append(f"Edge references unknown node: {from_id} -> {to_id}")
    
    # 3. All agents registered
    for node in dag.nodes:
        if node.agent_type not in registry.agents:
            errors.append(f"Unknown agent type: {node.agent_type}")
    
    # 4. Input/output schemas valid JSON Schema
    for node in dag.nodes:
        try:
            jsonschema.Draft7Validator.check_schema(node.input_schema)
            jsonschema.Draft7Validator.check_schema(node.output_schema)
        except jsonschema.SchemaError as e:
            errors.append(f"Node {node.id} schema invalid: {e}")
    
    # 5. Checkpoints reference valid nodes
    for cp in dag.checkpoints:
        if cp not in node_ids:
            errors.append(f"Checkpoint references unknown node: {cp}")
    
    return ValidationResult(valid=len(errors) == 0, errors=errors)
```

### Post-Execution Validation
```python
def validate_node_output(node: DAGNode, output: Dict) -> ValidationResult:
    # 1. Schema validation
    try:
        jsonschema.validate(output, node.output_schema)
    except jsonschema.ValidationError as e:
        return ValidationResult(valid=False, errors=[f"Schema violation: {e.message}"])
    
    # 2. Business rule validation (custom per agent)
    if node.agent_type == "security":
        if output.get("risk_score", 0) > 7 and output.get("approved"):
            return ValidationResult(valid=False, errors=["High risk score but approved — review required"])
    
    return ValidationResult(valid=True, errors=[])
```

---

## Patterns for Common Scenarios

### Feature Development
```
planner → [security, perf, arch] → coder → tester → consensus → deploy_checkpoint
```

### Incident Response
```
alert_triage → [diagnose, impact_assessment] → mitigate → verify → postmortem_checkpoint
```

### Refactoring
```
analyze_codebase → [identify_candidates, risk_assessment] → refactor → test → validate → consensus
```

### Release Management
```
version_bump → changelog → [security_scan, perf_test, integration_test] → stage_deploy → promote_checkpoint → prod_deploy
```

---

## Anti-Patterns to Avoid

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **God Agent** | One agent does everything | Decompose into specialists |
| **Implicit Dependencies** | Nodes share state without edges | Make all deps explicit in DAG |
| **No Checkpoints** | Irreversible actions auto-execute | Add human approval for prod deploy, schema changes |
| **No Schema Validation** | Garbage in, garbage out | Enforce JSON Schema on all inputs/outputs |
| **Silent Failures** | Agent fails, downstream uses stale data | Fail fast, propagate errors, alert |
| **Unbounded Retries** | Infinite loops on persistent failures | Max attempts + exponential backoff + escalation |
| **No Observability** | Can't debug what happened | Trace every agent: input, output, tokens, duration |