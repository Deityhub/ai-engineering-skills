# Agent Handoff: {{ .FromAgent }} → {{ .ToAgent }}

## Task
{{ .Task }}

## Decisions Made
{{ .Decisions }}

## Critical Findings (Must Address)
{{ .CriticalFindings }}

## Major Findings (Should Address)
{{ .MajorFindings }}

## Constraints
{{ .Constraints }}

## Artifacts
{{ .Artifacts }}

## Context Compression Level
{{ .Level }} ({{ .TokenBudget }} token budget)

---

## Handoff Levels

### L1 (<500 tokens) - Executive Summary
- Task ID, decision, next steps, critical blockers only
- Use for: Coordinator → Human, high-level status

### L2 (<1500 tokens) - L1 + Critical Findings
- L1 + critical findings with file:line
- Use for: Security → Coder, Arch → Coder

### L3 (<3000 tokens) - L2 + Major Findings + Token Diff
- L2 + major findings summary, token diff, decisions
- **Default for most agent-to-agent handoffs**

### L4 (Full) - Complete Transcripts
- Complete transcripts (debugging only)
- Use for: Postmortem, debugging failures

---

## Template Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `FromAgent` | Source agent | `security_review` |
| `ToAgent` | Target agent | `implementation` |
| `Task` | Task description | `Implement real-time notifications (WebSocket + fallback)` |
| `Decisions` | Bullet list | `- Use Redis Pub/Sub (ADR-047)\n- JWT auth 15min/7d\n- Feature flag: realtime-notifications` |
| `CriticalFindings` | Numbered list with file:line | `1. SEV-1: No rate limiting on WebSocket (security_review:finding-3)` |
| `MajorFindings` | Numbered list | `1. Connection pooling needed for Redis (perf_baseline:finding-2)` |
| `Constraints` | Bullet list | `- Budget: <50ms p99, <10MB/conn\n- 100k concurrent connections\n- Backward compatible with HTTP long-polling` |
| `Artifacts` | Links | `- Spec: @spec.md\n- Threat Model: @threat-model.md\n- ADR: @adr/0047-redis-pubsub.md` |
| `Level` | Compression level | `L3` |
| `TokenBudget` | Token limit | `3000` |

---

## Usage
```bash
# Generate handoff from review report
python scripts/compress-context.py --review review-report.md --level L3 --output handoff.md

# With token diff
python scripts/compress-context.py --review review-report.md --old-tokens old-tokens.json --new-tokens new-tokens.json --level L3
```