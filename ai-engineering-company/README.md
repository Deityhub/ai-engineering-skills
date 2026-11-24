# AI Engineering Company — Root Entrypoint Skill

**The AI Engineering Company skill for Goose** — Your complete, agentic software development organization. Takes any feature request and delivers working, tested, deployed software through intelligent multi-skill orchestration.

---

## Quick Start

### In Goose
```bash
# Load the full company (loads all 5 sub-skills automatically)
load_skill("ai-engineering-company")

# Or use the full lifecycle orchestrator directly
python skills/ai-engineering-company/scripts/full-lifecycle.py "Add real-time notifications with WebSocket" --auto-merge
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

### 🎯 Intelligent Routing
- Analyzes any request and determines required skills
- Routes to: Single skill, Targeted parallel, or Full agentic loop
- Always includes Orchestration for multi-skill work

### 🔄 Agentic Delivery Loop (Enhanced)
```
1. INTAKE & ROUTING       → Analyze request → Identify skills → Create DAG
2. 📋 PLANNING PHASE       → Detailed feature plan with human iteration
3. STRATEGY & SPEC        → PRD + Experiment + Component specs + Tokens
4. ARCHITECTURE PLAN      → ADRs + Architecture + Infra plan
5. IMPLEMENTATION         → Code + Components + Tests + IaC + Pipelines
6. VALIDATION & CONSENSUS → All gates → Weighted consensus → HITL
6. DEPLOY & RELEASE       → Canary → Progressive → Full → Monitor
7. LEARN & ITERATE        → Metrics → Experiments → Next cycle
```

### 🤖 Parallel Agent Execution with Validation
- **Security**: SAST, secrets, threat model → Zero critical findings
- **Performance**: Baselines, budgets, bottlenecks → Meets SLO
- **Architecture**: Coupling, boundaries, ADRs → Zero violations
- **Code**: Implementation + tests (80% coverage) → Passes
- **Design**: Components, tokens, accessibility → WCAG 2.1 AA
- **Platform**: Terraform, K8s, CI/CD → Valid plans

### 🤝 Weighted Consensus + HITL
- **Weights**: Security 30%, Architecture 30%, Performance 20%, Test 20%
- **Quorum**: 66% (80% for production deploy)
- **Veto**: Security/Architect can veto
- **HITL Gates**: Plan approval, commit, PR, production deploy

### 🌿 Git Workflow Automation (Enhanced)
```
Feature Request → 📋 PLANNING → Branch → Parallel Commits → PR → Gates → Consensus → Auto-merge → Tag → Deploy
                      ↑
              Human approves plan
```

### 🚀 Progressive Deployment (Enhanced)
- **Canary**: 5% → 25% → 50% → 100% over 2 hours
- **SLO Gates**: Auto-rollback on burn rate >1x
- **Feature Flags**: Instant rollback without deploy (default: off)
- **Rollback Hierarchy**: Flag → Git revert → DB rollback → Full restore
- **Observability**: SLO dashboards, burn rate alerts, runbook links

---

## 🆕 New Capabilities

### 📋 Planning Phase (NEW)
Before any implementation, a detailed feature plan is created and approved:
- Problem statement, proposed solution, technical approach
- Acceptance criteria, risks/mitigations, dependencies
- Effort estimate, milestones, feature flags
- Test strategy, rollback plan, ADR references
- **Human iterates and approves before implementation**

### 🔍 Template Detection (NEW)
- **Commits**: Detects `.github/commit-message.txt`, `.gitmessage`, `.commit-template` → falls back to Conventional Commits
- **PRs**: Detects `.github/pull_request_template.md`, `PULL_REQUEST_TEMPLATE.md` → falls back to standard
- **Conventions**: Detects `.github/commit-convention.md` → guides template rendering

### 🚩 Feature Flags (NEW)
- Every feature gets a flag (default: **off**) for instant rollback
- Rollout strategies: canary, progressive, instant
- Targeting support for segments/environments

### 📝 Architecture Decision Records (NEW)
- Every significant decision recorded as ADR in `adr/` directory
- Standard format: Context → Decision → Consequences → Alternatives
- Linked from feature plans, PRs, and handoffs

### 🔄 Rollback Automation (NEW)
- **Hierarchy**: Feature flag off → Git revert → DB migration down → Full DB restore
- Documented in feature plan, implemented in deployment
- Verification steps for each rollback method

### 🤝 Weighted Consensus + 4 HITL Gates
- **Weights**: Security 30%, Architecture 30%, Performance 20%, Test 20%
- **Quorum**: 66% (80% for production deploy)
- **Veto**: Security/Architect can veto
- **4 HITL Gates**: Plan → Commit → PR → Deploy

### 🚀 Progressive Deployment (Enhanced)
- **Canary**: 5% → 25% → 50% → 100% over 2 hours
- **SLO Gates**: Auto-rollback on burn rate >1x
- **Feature Flags**: Instant rollback without deploy (default: off)
- **Rollback Hierarchy**: Flag → Git revert → DB rollback → Full restore
- **Observability**: SLO dashboards, burn rate alerts, runbook links

---

## File Structure

```
ai-engineering-company/
├── SKILL.md                    # Goose-native manifest
├── universal-prompt.md         # Portable system prompt (COPY THIS)
├── PORTABILITY.md              # Tool-specific setup guide
├── README.md                   # This file
├── LICENSE.txt                 # MIT
├── references/                 # Portable markdown references
│   ├── routing-rules.md        # Intelligent skill selection
│   ├── delegation-protocol.md  # Agent contracts, handoffs, validation
│   ├── git-workflow.md         # Branch, commit, PR, merge, release
│   └── release-management.md   # Versioning, changelogs, rollback
├── scripts/                    # Deterministic Python scripts
│   ├── full-lifecycle.py       # End-to-end: intake → planning → release
│   ├── create-pr.py            # PR with template detection
│   ├── auto-merge.py           # Consensus-gated auto-merge
│   ├── tag-release.py          # Semantic versioning + tagging
│   └── deploy.py               # Progressive deployment
├── assets/templates/
│   ├── pr-template.md          # Rich PR template with gates
│   └── release-notes.md        # Release notes template
└── evals/                      # Test cases (to be added)
```

---

## Sub-Skills (Auto-Loaded)

| Skill | Role | Loaded |
|-------|------|--------|
| `product-engineering` | Strategy, PRDs, experiments, metrics | ✅ Auto |
| `design-skill` | UI/UX, tokens, accessibility, components | ✅ Auto |
| `staff-engineer` | Code, architecture, security, performance | ✅ Auto |
| `platform-engineer` | IaC, K8s, CI/CD, observability, SRE | ✅ Auto |
| `agentic-orchestration` | DAGs, consensus, validation, HITL | ✅ Auto |

---

## Scripts Usage

### Full Lifecycle (One Command)
```bash
# Complete: request → plan → execute → validate → consensus → merge → tag → deploy
python skills/ai-engineering-company/scripts/full-lifecycle.py "Add real-time notifications with WebSocket and fallback" --auto-merge

# Dry run (show plan only)
python skills/ai-engineering-company/scripts/full-lifecycle.py "Add user dashboard" --dry-run
```

### Individual Components
```bash
# Create PR with validation gates
python scripts/create-pr.py --title "feat: Add notifications" --context context.json --validation validation.json

# Auto-merge on consensus
python scripts/auto-merge.py --pr 247 --consensus consensus.json

# Semantic version tag + changelog
python scripts/tag-release.py --level minor --push --changelog CHANGELOG.md

# Progressive deployment
python scripts/deploy.py --version v2.3.0 --environment production --strategy canary
```

---

## Evals (Test Cases)

Run evals to verify skill behavior:
```bash
# Each eval is a YAML file with input, expected output, and success criteria
# Example: evals/routing-test.yaml tests intelligent routing
# Example: evals/consensus-test.yaml tests weighted voting
```

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
| Git | 2.30+ |
| GitHub CLI (gh) | 2.0+ (for PR/merge automation) |
| Goose | 1.0 (for native features) |
| Any AI tool | System prompt support |
| Optional: Terraform, kubectl, helm, cloud CLIs | For Platform scripts |

---

## License

MIT — Use freely in any project, commercial or personal.

---

## Philosophy

> **We don't build features. We build a company that builds features.**

The AI Engineering Company is a **complete agentic software development organization** where:
- Every request goes through intelligent routing
- **Every feature starts with a detailed, human-approved plan**
- Specialized agents execute in parallel with validation
- **Every commit, PR, and deployment requires human approval**
- **Templates detected from project, falling back to standards**
- **Feature flags for instant, safe rollback**
- **Architecture decisions recorded as formal ADRs**
- Every deployment is observable and reversible
- The loop closes with metrics → experiments → next cycle

**This is how modern software gets built at scale.** 🚀