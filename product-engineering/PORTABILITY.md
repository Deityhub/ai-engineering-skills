# Product Engineering Skill — Portability Guide

## Universal Prompt
Copy `/skills/product-engineering/universal-prompt.md` into **any** AI tool:
- **Claude Code**: `.claude/CLAUDE.md` or project `CLAUDE.md`
- **Codex**: `AGENTS.md`
- **Gemini**: System Instructions
- **Cursor**: Settings → Rules for AI
- **Copilot**: `.github/copilot-instructions.md`
- **Goose**: `load_skill("product-engineering")`

## References (Portable Markdown)
All files in `/references/` are plain Markdown — readable anywhere:
- `product-strategy.md` — Vision, strategy, OKRs, North Star
- `discovery.md` — Continuous discovery, JTBD, opportunity trees
- `prioritization.md` — RICE, WSJF, Kano, frameworks
- `experimentation.md` — A/B testing, feature flags, statistical rigor
- `metrics.md` — Metric hierarchy, dashboards, guardrails
- `stakeholder-communication.md` — Updates, reviews, stakeholder management
- `tech-debt.md` — Debt budget, registry, quality gates

## Scripts (Python 3.10+, Zero External Deps for Core)
```bash
# All scripts run with: python3 script.py [args]

# PRD generation
python3 scripts/generate-prd.py --context "Add real-time notifications" --template feature

# Experiment design calculator
python3 scripts/design-experiment.py --hypothesis "New onboarding increases activation" --metric activation_rate --mde 0.05

# Prioritization (RICE/WSJF/Kano)
python3 scripts/prioritize.py --framework rice --features features.csv

# Metric hierarchy builder
python3 scripts/define-metrics.py --north-star "Weekly active workspaces"

# Weekly stakeholder update generator
python3 scripts/weekly-update.py --github-org myorg --jira-project TEAM --mixpanel-project 12345

# Team/product health check
python3 scripts/health-check.py --team platform --quarter Q4
```

### Script Capabilities Without External Tools
| Script | Fallback If Tool Missing |
|--------|-------------------------|
| `generate-prd.py` | Template-based, no external deps |
| `design-experiment.py` | Built-in power analysis, sample size calculator |
| `prioritize.py` | Pure Python RICE/WSJF/Kano implementations |
| `define-metrics.py` | Template-based metric definitions |
| `weekly-update.py` | Template-based, optional GitHub/Jira/Analytics integration |
| `health-check.py` | Questionnaire-based assessment |

## Goose-Native Features (Bonus)
When loaded in Goose (`load_skill("product-engineering")`):
- **Progressive disclosure**: Only SKILL.md loads initially; references/scripts load on demand
- **Agentic delegation**: Use `delegate` tool with `source: "product-engineering"` for parallel validation
- **Context compression**: `scripts/compress-context.py` (shared) compresses handoffs to <3000 tokens

## Minimal Viable Usage (Any AI)
```markdown
# Paste this into any AI tool's system prompt:

You are a Product Engineering Lead. Bridge business strategy and technical execution.
1. Outcomes Over Output — Measure success by user/business impact
2. Evidence Over Opinion — Decisions backed by data, discovery, experiments
3. Ruthless Prioritization — If everything is priority, nothing is
4. Ship to Learn — Smallest viable experiment → measure → iterate
5. Tech Debt as Investment — Pay down strategically, allocate 20% capacity
6. Alignment Through Artifacts — PRDs, specs, dashboards, runbooks
7. Customer Voice in Every Room — Discovery is continuous

Apply frameworks: RICE/WSJF/Kano for prioritization, JTBD for discovery,
A/B testing with statistical rigor, North Star + leading/lagging/health metrics.
```

## Skill Package (`.skill` file)
```bash
cd /Users/deityhub/work/skills/product-engineering
tar -czf ../product-engineering.skill *
```
Import in Goose: `load_skill("product-engineering.skill")`

## Version Compatibility
| Component | Minimum Version |
|-----------|----------------|
| Python | 3.10 |
| Goose | 1.0 (for native features) |
| Any AI tool | System prompt support |
| Optional: GitHub CLI, Jira CLI, Analytics APIs | For enhanced scripts |