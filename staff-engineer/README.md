# Staff Engineer Skill

**Principal/Staff Software Engineer skill for Goose** — Build secure, efficient, clean, reusable, and maintainable software across any language or architecture.

---

## Quick Start

### In Goose
```bash
load_skill("staff-engineer")
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

### 🔒 Security by Default
- OWASP Top 10 scanning (SAST + pattern fallback)
- Secrets detection (entropy + patterns)
- Dependency vulnerability scanning (npm, cargo, pip, go, maven)
- License compliance
- Crypto weakness detection
- Config misconfiguration scanning (Docker, K8s, Terraform)

### ⚡ Performance by Measurement
- Multi-language benchmark parsing (Go, Rust, Python, JS)
- Baseline comparison with regression detection
- Performance budgets in CI (latency, throughput, memory)
- Profiling hierarchy: macro → meso → micro

### 🏗️ Architecture Principles
- Hexagonal/clean architecture enforcement
- Module boundary validation
- Circular dependency detection (Tarjan's SCC)
- Coupling metrics (afferent/efferent, instability, distance from main sequence)
- Mermaid diagram generation

### 🧠 Context Optimization
- Progressive disclosure (L1-L4)
- Relevance scoring algorithm
- Token budget management
- Agent handoff protocol

### ♻️ Safe Refactoring
- Risk-assessed transformations (low/medium/high)
- Validation requirements per refactoring
- Pattern detection across languages

### 📝 ADR Generation
- MADR format with YAML frontmatter
- Supersession tracking
- Decision log from git history

### 🌍 Language-Agnostic
- **Universal 10 principles** applied to ANY language
- **Adaptation template** — fill in for your detected language
- **Canonical examples** for Go, TypeScript, Python, Rust, Java/Kotlin
- No language-specific guides to maintain

---

## File Structure

```
staff-engineer/
├── SKILL.md                    # Goose-native manifest
├── universal-prompt.md         # Portable system prompt (COPY THIS)
├── PORTABILITY.md              # Tool-specific setup guide
├── LICENSE.txt                 # MIT
├── README.md                   # This file
├── references/                 # Portable markdown references
│   ├── security-playbook.md
│   ├── performance-patterns.md
│   ├── architecture-principles.md
│   ├── context-optimizer.md
│   ├── refactoring-catalog.md
│   └── language-adaptation.md  # Universal framework
├── scripts/                    # Deterministic Python scripts
│   ├── scan-security.py
│   ├── analyze-architecture.py
│   ├── profile-performance.py
│   ├── optimize-context.py
│   ├── suggest-refactor.py
│   └── generate-adr.py
├── evals/                      # Test cases
│   ├── sql-injection-prevention.yaml
│   ├── cache-invalidation.yaml
│   ├── module-boundary-enforcement.yaml
│   └── context-compression-ratio.yaml
└── assets/templates/
    ├── adr-template.md
    └── threat-model.md
```

---

## Scripts Usage

All scripts are **standalone Python 3.10+** with zero external dependencies.

```bash
# Security scan (SAST, secrets, deps, license, crypto, config)
python scripts/scan-security.py --path . --checks sast,secrets,deps,license,crypto,config

# Architecture analysis (coupling, cycles, boundaries, Mermaid diagram)
python scripts/analyze-architecture.py --path . --format mermaid

# Performance profiling (with budget enforcement)
python scripts/profile-performance.py --command "go test -bench=." --budget "latency:p99<200ms,throughput:>1000rps"

# Context optimization (relevance scoring, compression)
python scripts/optimize-context.py --task "add user auth" --max-tokens 3000

# Refactoring suggestions (risk-assessed)
python scripts/suggest-refactor.py --path ./src --min-risk medium --format markdown

# Generate ADR
python scripts/generate-adr.py generate --title "Migrate to PostgreSQL" --context "..." --decision "..." --positive "..." --negative "..." --tags "data,migration" --deciders "Team"
```

---

## Evals (Test Cases)

Run evals to verify skill behavior:

```bash
# Each eval is a YAML file with input, expected output, and success criteria
# Example: sql-injection-prevention.yaml tests SAST detects SQLi in Go/Python/TS
```

---

## Universal Language Adaptation

**No language guides to maintain.** Instead:

1. Detect project language from files (`go.mod`, `package.json`, `Cargo.toml`, etc.)
2. Apply the **10 Universal Principles** from `references/language-adaptation.md`
3. Fill in the **Adaptation Template** with language-specific tooling:
   - Strict mode command
   - Null safety approach
   - Generics syntax
   - Discriminated unions
   - Branded types
4. Use **canonical examples** as reference

This works for **any language** — not just the 5 examples provided.

---

## Agentic Delegation

The skill includes a protocol for parallel subagent validation:

```
Feature: "Add real-time notifications"
├── Agent A: Security review (threat model, auth, data flow)
├── Agent B: Performance baseline (load test, profiling)
├── Agent C: Implementation (WebSocket + fallback, tests)
├── Agent D: Architecture review (coupling, boundaries, ADR)
└── Coordinator: Consensus, integration, deploy
```

Context handoff via `scripts/optimize-context.py` compresses to <3000 tokens.

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
| git | Any (for history analysis) |
| Language tools | Detected per project (optional) |

---

## License

MIT — Use freely in any project, commercial or personal.

---

## Philosophy

> **Code is a liability, not an asset.** Every line must justify its existence.
>
> 1. **Secure by Default** — Threat model first, code second
> 2. **Efficient by Design** — Measure before optimizing
> 3. **Clean by Discipline** — Coupling kills velocity
> 4. **Reusable by Architecture** — DRY applies to knowledge, not syntax
> 5. **Maintainable by Empathy** — The next reader is you at 3 AM