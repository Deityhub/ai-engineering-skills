# Agentic Orchestration Skill — Portability Guide

## Universal Prompt
Copy `/skills/agentic-orchestration/universal-prompt.md` into **any** AI tool:
- **Claude Code**: `.claude/CLAUDE.md` or project `CLAUDE.md`
- **Codex**: `AGENTS.md`
- **Gemini**: System Instructions
- **Cursor**: Settings → Rules for AI
- **Copilot**: `.github/copilot-instructions.md`
- **Goose**: `load_skill("agentic-orchestration")`

## References (Portable Markdown)
All files in `/references/` are plain Markdown — readable anywhere:
- `orchestration-patterns.md` — DAG design, agent registry, coordination
- `delegation-protocols.md` — Task contracts, handoff formats, checkpoints
- `validation-frameworks.md` — Schema, policy, critic, mutation testing
- `consensus-protocols.md` — Weighted voting, quorum, conflict resolution
- `context-management.md` — Compression algorithms, relevance scoring
- `observability.md` — Tracing, metrics, debugging agent systems
- `frameworks.md` — LangGraph, AutoGen, CrewAI, custom patterns

## Scripts (Python 3.10+, Zero External Deps for Core)
```bash
# All scripts run with: python3 script.py [args]

# Task decomposition → DAG
python3 scripts/decompose-task.py --task "Add real-time notifications" --context ./spec.md

# DAG execution with parallel agents
python3 scripts/coordinate-agents.py --dag dag.json --agents-dir ./agents --checkpoints checkpoints.yaml

# Consensus voting
python3 scripts/consensus.py --votes votes.json --weights weights.yaml --quorum 0.66

# Context compression for handoffs
python3 scripts/compress-context.py --input full_context.md --level L3 --max-tokens 3000

# Output validation pipeline
python3 scripts/validate-output.py --output agent_output.json --schema output_schema.json --policies ./policies

# Human-in-the-loop checkpoints
python3 scripts/checkpoint.py --type approval --context checkpoint_context.md --timeout 4h
```

### Script Capabilities Without External Tools
| Script | Fallback If Tool Missing |
|--------|-------------------------|
| `decompose-task.py` | Built-in planning prompts, outputs DAG JSON |
| `coordinate-agents.py` | Async execution with subprocess/threading, no framework needed |
| `consensus.py` | Pure Python weighted voting, quorum, conflict resolution |
| `compress-context.py` | Relevance scoring + truncation (shared with other skills) |
| `validate-output.py` | JSON Schema validation + OPA-style policy + LLM critic prompts |
| `checkpoint.py` | Template-based approval workflows (Slack/email/GitHub via webhooks) |

## Goose-Native Features (Bonus)
When loaded in Goose (`load_skill("agentic-orchestration")`):
- **Progressive disclosure**: Only SKILL.md loads initially; references/scripts load on demand
- **Agentic delegation**: Use `delegate` tool with `source: "agentic-orchestration"` for orchestrating subagents
- **Context compression**: `scripts/compress-context.py` compresses handoffs to <3000 tokens

## Minimal Viable Usage (Any AI)
```markdown
# Paste this into any AI tool's system prompt:

You are an Agentic Orchestration Engineer. Design multi-agent systems that:
1. Decompose tasks into DAGs with clear contracts
2. Execute agents in parallel with validation
3. Achieve consensus through weighted voting
4. Compress context for handoffs (≤3000 tokens)
5. Include human-in-the-loop checkpoints
6. Trace everything for observability

Apply patterns from references/ for orchestration, delegation, validation, consensus, context management.
```

## Skill Package (`.skill` file)
```bash
cd /Users/deityhub/work/skills/agentic-orchestration
tar -czf ../agentic-orchestration.skill *
```
Import in Goose: `load_skill("agentic-orchestration.skill")`

## Version Compatibility
| Component | Minimum Version |
|-----------|----------------|
| Python | 3.10 |
| LangGraph | 0.1+ (optional) |
| AutoGen | 0.2+ (optional) |
| CrewAI | 0.1+ (optional) |
| Goose | 1.0 (for native features) |
| Any AI tool | System prompt support |