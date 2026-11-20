# AI Engineering Company — Portability Guide

## Universal Prompt
Copy `/skills/ai-engineering-company/universal-prompt.md` into **any** AI tool:
- **Claude Code**: `.claude/CLAUDE.md` or project `CLAUDE.md`
- **Codex**: `AGENTS.md`
- **Gemini**: System Instructions
- **Cursor**: Settings → Rules for AI
- **Copilot**: `.github/copilot-instructions.md`
- **Goose**: `load_skill("ai-engineering-company")`

## References (Portable Markdown)
All files in `/references/` are plain Markdown — readable anywhere:
- `routing-rules.md` — Intelligent skill selection logic
- `delegation-protocol.md` — Agent contracts, handoffs, validation, consensus
- `git-workflow.md` — Branch, commit, PR, merge, release conventions
- `release-management.md` — Versioning, changelogs, rollback, post-release

## Scripts (Python 3.10+, Zero External Deps for Core)
```bash
# All scripts run with: python3 script.py [args]

# Full lifecycle: intake → release
python3 scripts/full-lifecycle.py "Add real-time notifications with WebSocket" --auto-merge

# Individual components
python3 scripts/create-pr.py --title "feat: Add notifications" --context context.json --validation validation.json
python3 scripts/auto-merge.py --pr 247 --consensus consensus.json
python3 scripts/tag-release.py --level minor --push --changelog CHANGELOG.md
python3 scripts/deploy.py --version v2.3.0 --environment production --strategy canary
```

### Script Capabilities Without External Tools
| Script | Fallback If Tool Missing |
|--------|-------------------------|
| `full-lifecycle.py` | Simulates agent execution, outputs plan |
| `create-pr.py` | Template generation only |
| `auto-merge.py` | Consensus validation only |
| `tag-release.py` | Local git tag only |
| `deploy.py` | Dry-run mode |

## Goose-Native Features (Bonus)
When loaded in Goose (`load_skill("ai-engineering-company")`):
- **Progressive disclosure**: Only SKILL.md loads initially; references/scripts load on demand
- **Agentic delegation**: Uses `agentic-orchestration` skill for multi-agent coordination
- **Sub-skill integration**: Auto-loads Product, Design, Staff Eng, Platform skills
- **Context compression**: Shared `compress-context.py` for ≤3000 token handoffs

## Minimal Viable Usage (Any AI)
```markdown
# Paste this into any AI tool's system prompt:

You are the AI Engineering Company — a complete agentic software development organization.
You take ANY feature request and deliver working, tested, deployed software through:
1. Intelligent routing to specialized skills (Product, Design, Staff Eng, Platform, Orchestration)
2. DAG-based task decomposition with parallel agent execution
3. Validation gates (schema + policy + critic) on every output
4. Weighted consensus with human-in-the-loop checkpoints
5. Git workflow automation (branch → PR → consensus → merge → tag → deploy)
6. Progressive deployment with automatic rollback on SLO breach

Route every request through the full agentic delivery loop unless it's a single-skill task.
```

## Skill Package (`.skill` file)
```bash
cd /Users/deityhub/work/skills/ai-engineering-company
tar -czf ../ai-engineering-company.skill *
```
Import in Goose: `load_skill("ai-engineering-company.skill")`

## Sub-skill Dependencies
This skill orchestrates these sub-skills (must be installed):
- `product-engineering` — Strategy, PRDs, experiments, metrics
- `design-skill` — UI/UX, tokens, accessibility, components
- `staff-engineer` — Code, architecture, security, performance
- `platform-engineer` — IaC, K8s, CI/CD, observability, SRE
- `agentic-orchestration` — DAGs, consensus, validation, HITL

Install all: `load_skill("product-engineering")` etc.

## Version Compatibility
| Component | Minimum Version |
|-----------|----------------|
| Python | 3.10 |
| Git | 2.30+ |
| GitHub CLI (gh) | 2.0+ (for PR/merge automation) |
| Goose | 1.0 (for native features) |
| Any AI tool | System prompt support |
| Optional: Terraform, kubectl, helm, cloud CLIs | For Platform scripts |

## Environment Variables
```bash
# Optional: for enhanced functionality
export GITHUB_TOKEN="ghp_xxx"           # For gh CLI
export PROMETHEUS_URL="http://prom:9090" # For SLO checks
export LAUNCHDARKLY_SDK_KEY="sdk-xxx"   # For feature flags
export SLACK_WEBHOOK_URL="https://..."  # For notifications
```