# Staff Engineer Skill — Portability Guide

## Universal Prompt
Copy `/skills/staff-engineer/universal-prompt.md` into **any** AI tool:
- **Claude Code**: Paste at conversation start or add to `CLAUDE.md`
- **Codex**: Paste in system prompt or `AGENTS.md`
- **Gemini**: Paste in system instructions
- **Cursor**: Add to `.cursorrules` or project rules
- **Copilot**: Add to `.github/copilot-instructions.md`
- **Goose**: Load via `load_skill("staff-engineer")` — uses SKILL.md natively

## References (Portable Markdown)
All files in `/references/` are plain Markdown — readable anywhere:
- `security-playbook.md` — OWASP, threat modeling, crypto standards
- `performance-patterns.md` — profiling hierarchy, caching, budgets
- `architecture-principles.md` — hexagonal, coupling metrics, ADRs
- `context-optimizer.md` — progressive disclosure, relevance scoring
- `refactoring-catalog.md` — risk-assessed transformations
- `language-adaptation.md` — universal principles + template for ANY language

## Scripts (Python 3.10+, Zero External Deps for Core)
```bash
# All scripts run with: python3 script.py [args]
# Optional deps (install if needed): pip3 install pyyaml

# Security scanning
python3 scripts/scan-security.py --path . --checks sast,secrets,deps,license,crypto,config

# Architecture analysis
python3 scripts/analyze-architecture.py --path . --format mermaid

# Performance profiling
python3 scripts/profile-performance.py --command "go test -bench=." --budget "latency:p99<200ms,throughput:>1000rps"
```

### Script Capabilities Without External Tools
| Script | Fallback If Tool Missing |
|--------|-------------------------|
| `scan-security.py` | Pattern-based SAST (SQLi, XSS, path traversal, cmd injection), entropy-based secret detection, lockfile parsing for deps |
| `analyze-architecture.py` | Pure Python import parsing (TS/JS, Python, Go, Rust, Java), Tarjan's SCC for cycles |
| `profile-performance.py` | Parses `go test -bench`, `cargo bench`, `pytest-benchmark` output natively |

## Goose-Native Features (Bonus)
When loaded in Goose (`load_skill("staff-engineer")`):
- **Progressive disclosure**: Only SKILL.md loads initially; references/scripts load on demand
- **Agentic delegation**: Use `delegate` tool with `source: "staff-engineer"` for parallel validation
- **Context compression**: `scripts/optimize-context.py` (to be added) compresses handoffs to <3000 tokens

## Minimal Viable Usage (Any AI)
```markdown
# Paste this into any AI tool's system prompt:

You are a Principal/Staff Software Engineer. Apply these 10 universal principles to ALL code:
1. Secure by Default — validate at boundaries, parameterized queries, encrypt, rotate secrets
2. Explicit over Implicit — no magic, declared deps, explicit types, config over convention
3. Single Responsibility — one reason to change per module
4. Dependency Inversion — policies depend on abstractions, not details
5. Fail Fast, Fail Loud — validate early, crash on programmer errors, structured errors
6. Observability Built-In — structured logs, RED/USE metrics, W3C traces
7. Test as Specification — tests document behavior; unit/integration/contract
8. Performance by Measurement — no optimization without profiling; budgets in CI
9. Immutable by Default — values over refs, pure functions, no shared mutable state
10. Document Decisions, Not Code — ADRs capture why; comments explain intent

For the current project's language(s), apply the Language Adaptation Template from language-adaptation.md.
```

## Skill Package (`.skill` file)
To distribute as a single file:
```bash
cd /Users/deityhub/work/skills/staff-engineer
tar -czf ../staff-engineer.skill *
```
Import in Goose: `load_skill("staff-engineer.skill")`

## Version Compatibility
| Component | Minimum Version |
|-----------|----------------|
| Python | 3.10 |
| Goose | 1.0 (for native features) |
| Any AI tool | System prompt support |