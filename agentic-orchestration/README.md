# Agentic Orchestration Skill

**Agentic Orchestration Engineer skill for Goose** — Designs multi-agent systems that decompose tasks, coordinate execution, validate outputs, and achieve consensus — with human-in-the-loop checkpoints.

---

## Quick Start

### In Goose
```bash
load_skill("agentic-orchestration")
```

### In Any AI Tool
Copy the **SYSTEM PROMPT** from `universal-prompt.md` into:
- **Claude Code**: `.claude/CLAUDE.md`
- **Codex**: `AGENTS.md`
- **Gemini**: System Instructions
- **Cursor**: Settings → Rules for AI
- **Copilot**: `.github/copilot-instructions.md`

---

## What This Skill Provides

### 🔀 Task Decomposition & Planning
- DAG-based task breakdown with explicit input/output contracts
- Planner agent generates execution graphs from natural language
- Parallelizable node identification, checkpoint insertion
- Schema validation (JSON Schema / Pydantic) per node

### 🤖 Agent Registry & Specialization
- Standard agent types: Planner, Security, Performance, Architect, Coder, Tester, Critic, Coordinator
- Agent definitions with model, tools, schemas, timeouts, retry policies
- Extensible registry for domain-specific agents

### 🗳️ Consensus Protocols
- Weighted voting with configurable quorum (default 66%)
- Decision-type specific weights (security veto, architect tiebreaker)
- Conflict resolution: automatic → mediated → escalated → veto
- Audit trail of all votes, reasoning, and outcomes

### 📦 Context Compression for Handoffs
- Progressive disclosure levels (L1-L4) with token budgets
- Relevance scoring: semantic similarity + recency + criticality + centrality
- Structure-preserving truncation (headings, code blocks, tables)
- Handoff format: decisions, critical/major findings, constraints, artifacts

### ✅ Validation Loops
- Schema validation (fast, deterministic)
- Policy checking (OPA/Rego-style for security, cost, compliance)
- Critic agent (LLM-based adversarial review: security, perf, correctness)
- Retry with feedback injection until pass or max attempts

### 👤 Human-in-the-Loop Checkpoints
- Checkpoint types: Approval, Review, Information
- Timeout-based auto-reject/escalate
- Rich context: summary, artifacts, decisions, actions
- Slack/email/GitHub/webhook integrations

### 📈 Observability for Agent Systems
- Distributed tracing per agent (input/output tokens, duration, model, validation)
- Key metrics: success rate, compression ratio, consensus time, checkpoint latency
- Debugging: replay from any checkpoint, full transcript access

---

## File Structure

```
agentic-orchestration/
├── SKILL.md                    # Goose-native manifest
├── universal-prompt.md         # Portable system prompt (COPY THIS)
├── PORTABILITY.md              # Tool-specific setup guide
├── README.md                   # This file
├── LICENSE.txt                 # MIT
├── references/                 # Portable markdown references
│   ├── orchestration-patterns.md
│   ├── delegation-protocols.md
│   ├── validation-frameworks.md
│   ├── consensus-protocols.md
│   ├── context-management.md
│   ├── observability.md
│   └── frameworks.md
├── scripts/                    # Deterministic Python scripts
│   ├── decompose-task.py
│   ├── coordinate-agents.py
│   ├── consensus.py
│   ├── compress-context.py
│   ├── validate-output.py
│   └── checkpoint.py
├── evals/                      # Test cases
│   ├── task-decomposition.yaml
│   ├── agent-coordination.yaml
│   ├── consensus-voting.yaml
│   ├── context-compression.yaml
│   └── validation-pipeline.yaml
├── assets/templates/
│   ├── dag-template.json
│   ├── agent-spec.yaml
│   ├── checkpoint-template.md
│   └── handoff-template.md
└── tests/                      # Unit tests for scripts
    ├── conftest.py
    ├── test_decompose_task.py
    ├── test_consensus.py
    └── test_compress_context.py
```

---

## Scripts Usage

All scripts are **standalone Python 3.10+** with zero external dependencies.

```bash
# Task decomposition → DAG
python scripts/decompose-task.py --task "Add real-time notifications" --context ./spec.md

# DAG execution with parallel agents
python scripts/coordinate-agents.py --dag dag.json --agents-dir ./agents --checkpoints checkpoints.yaml

# Consensus voting
python scripts/consensus.py --votes votes.json --weights weights.yaml --quorum 0.66

# Context compression for handoffs
python scripts/compress-context.py --input full_context.md --level L3 --max-tokens 3000

# Output validation pipeline
python scripts/validate-output.py --output agent_output.json --schema output_schema.json --policies ./policies

# Human-in-the-loop checkpoints
python scripts/checkpoint.py --type approval --context checkpoint_context.md --timeout 4h
```

---

## Evals (Test Cases)

Run evals to verify skill behavior:
```bash
# Each eval is a YAML file with input, expected output, and success criteria
# Example: task-decomposition.yaml tests DAG generation from task description
```

---

## Frameworks Supported

| Framework | Use Case |
|-----------|----------|
| **LangGraph** | Complex DAGs with state, cycles, human-in-the-loop |
| **AutoGen** | Conversational agents, group chat, code execution |
| **CrewAI** | Role-based crews, process-driven workflows |
| **Custom** | Lightweight orchestrator (included in scripts) |

---

## Portability

See `PORTABILITY.md` for detailed setup in:
- Goose (native)
- Claude Code
- Codex
- Gemini
- Cursor
- Copilot
- CLI / Local Scripts

---

## Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.10+ |
| LangGraph | 0.1+ (optional) |
| AutoGen | 0.2+ (optional) |
| CrewAI | 0.1+ (optional) |

---

## License

MIT — Use freely in any project, commercial or personal.

---

## Philosophy

> **Agents are workers. Orchestration is the system.** Design for: observability, determinism, graceful degradation, human oversight.
>
> 1. **Decompose Before Delegate** — Break task into DAG of subtasks with clear contracts
> 2. **Validate, Don't Trust** — Every agent output passes through critic/validator
> 3. **Compress Context** — Handoffs ≤3000 tokens. Summarize decisions, not transcripts
> 4. **Consensus Over Authority** — Multiple agents vote/verify. Weighted by expertise
> 5. **Human-in-the-Loop** — Checkpoints for irreversible decisions
> 6. **Observability Built-In** — Trace every agent: input, output, tokens, duration, rationale
> 7. **Graceful Degradation** — Agent fails → retry, fallback, escalate. Never silent failure
> 8. **Idempotency & Replay** — Same input → same output. Replay from any checkpoint