# AI Engineering Skills — Complete Software Development Company

> **A curated collection of production-grade skills that work together as an agentic software development company.** Each skill represents a specialized role; together they form a complete lifecycle from vision to running software.

---

## 🏢 The Company Org Chart

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI ENGINEERING COMPANY                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│   │   PRODUCT    │───▶│   DESIGN     │───▶│  STAFF ENG   │───▶│ PLATFORM │ │
│   │ ENGINEERING  │    │   (UI/UX)    │    │  (CODE)      │    │  (INFRA) │ │
│   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └────┬─────┘ │
│          │                   │                   │                 │       │
│          ▼                   ▼                   ▼                 ▼       │
│   ┌─────────────────────────────────────────────────────────────────────┐  │
│   │                    AGENTIC ORCHESTRATION                            │  │
│   │         (Task Decomposition • Consensus • Validation • HITL)        │  │
│   └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 The Agentic Development Loop

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  STRATEGY   │────▶│   DESIGN    │────▶│   BUILD     │────▶│   SHIP      │
│  (Product)  │     │  (Design)   │     │ (Staff Eng) │     │ (Platform)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                   │
       ▼                   ▼                   ▼                   ▼
  Vision & OKRs      Specs & Tokens       Code & Tests        IaC & Deploy
  Discovery          Components           Architecture        Observability
  Prioritization     Accessibility        Security            SRE
  Experiments        Responsive           Performance         Cost Control
       │                   │                   │                   │
       └─────────────────┴─────────────────┴─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  ORCHESTRATION  │
                    │  (Coordination) │
                    │  - DAG Planning │
                    │  - Validation   │
                    │  - Consensus    │
                    │  - HITL Gates   │
                    └─────────────────┘
```

---

## 📦 Skills Catalog

| Skill | Role | Trigger | Core Output |
|-------|------|---------|-------------|
| **[product-engineering](./product-engineering/)** | **Product Lead** | Strategy, PRDs, prioritization, experiments, metrics | PRDs, Experiment designs, Roadmaps, Weekly updates |
| **[design-skill](./design-skill/)** | **Senior Designer** | UI components, design systems, accessibility, tokens | Specs, Components (React/Vue/SwiftUI/Flutter), Audits |
| **[staff-engineer](./staff-engineer/)** | **Principal Engineer** | Code, architecture, security, performance, ADRs | Code reviews, ADRs, Refactors, Security scans |
| **[platform-engineer](./platform-engineer/)** | **Platform Engineer** | IaC, Kubernetes, CI/CD, observability, SRE | Terraform, K8s manifests, Pipelines, Runbooks |
| **[agentic-orchestration](./agentic-orchestration/)** | **Orchestration Lead** | Multi-agent workflows, consensus, validation | DAGs, Agent coordination, Handoffs, Checkpoints |

---

## 🔄 How They Work Together

### 1. **Product Engineering** → Defines *What & Why*
```
Input: Business vision, customer feedback, market data
Output: PRDs, Experiment designs, Prioritized roadmap, Success metrics
Handoff: → Design (specs), → Staff Eng (technical constraints), → Orchestration (DAG)
```

### 2. **Design Skill** → Defines *How It Looks & Feels*
```
Input: PRDs, User stories, Existing design tokens
Output: Component specs, Design tokens, Accessibility audits, Cross-platform components
Handoff: → Staff Eng (implementation specs), → Platform (design system as code)
```

### 3. **Staff Engineer** → Defines *How It Works*
```
Input: Specs, Architecture decisions, Security requirements
Output: Code, ADRs, Security reviews, Performance baselines, Refactoring plans
Handoff: → Platform (artifacts, containers), → Orchestration (validation tasks)
```

### 4. **Platform Engineer** → Defines *Where It Runs*
```
Input: Artifacts, Scaling requirements, SLOs
Output: Terraform modules, K8s manifests, CI/CD pipelines, Runbooks, Cost models
Handoff: → Staff Eng (deployment contracts), → Orchestration (deployment tasks)
```

### 5. **Agentic Orchestration** → Coordinates *The Whole Loop*
```
Input: Any complex task requiring multiple skills
Output: DAG execution plans, Agent coordination, Consensus decisions, Human checkpoints
Handoff: → All skills (delegated subtasks with compressed context)
```

---

## 🚀 Quick Start: Build a Feature End-to-End

### In Goose (All Skills Loaded)
```bash
# Load the full company
load_skill("product-engineering")
load_skill("design-skill")
load_skill("staff-engineer")
load_skill("platform-engineer")
load_skill("agentic-orchestration")

# Or they auto-trigger based on your request
```

### Example: "Add Real-Time Notifications"

```
┌────────────────────────────────────────────────────────────────────┐
│ USER: "Add real-time notifications with WebSocket and fallback"   │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│ AGENTIC ORCHESTRATION: Decomposes into DAG                        │
│                                                                     │
│  security_review ──┐                                               │
│  perf_baseline   ──┼──▶ implementation ──▶ integration_test ──▶ consensus
│  arch_review     ──┘         │                    │                 │
│                             ▼                    ▼                 │
│                      ┌─────────────┐         ┌─────────────┐      │
│                      │   DESIGN    │         │  PLATFORM   │      │
│                      │  (components│         │ (infra,     │      │
│                      │   tokens)   │         │  pipelines) │      │
│                      └─────────────┘         └─────────────┘      │
└────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌────────────────────────────────────────────────────────────────────┐
│ PARALLEL EXECUTION WITH VALIDATION                                 │
│                                                                     │
│  🔴 Security:  SAST, secrets, threat model → PASS                 │
│  🟡 Perf:     Baseline <50ms p99, budget met → PASS               │
│  🟢 Arch:     Zero cycles, boundaries clean → PASS                │
│  🔵 Code:     Implementation + tests (80% coverage) → PASS        │
│  🟣 Test:     Integration + contract tests → PASS                 │
│  🟠 Design:   Components + tokens + a11y audit → PASS             │
│  🟤 Infra:    TF plan + K8s manifests + pipeline → PASS           │
│                                                                     │
│  🤝 CONSENSUS: Weighted vote (Sec 30%, Arch 30%, Perf 20%, Test 20%)│
│  ✅ APPROVED → Human checkpoint for production deploy             │
└────────────────────────────────────────────────────────────────────┘
```

---

## 📁 Repository Structure

```
skills/
├── README.md                    # ← YOU ARE HERE
├── product-engineering/         # Product strategy, discovery, experiments
│   ├── SKILL.md
│   ├── universal-prompt.md
│   ├── references/ (7 files)
│   ├── scripts/ (6 files)
│   ├── evals/ (4 files)
│   └── assets/templates/ (5 files)
│
├── design-skill/                # UI/UX, tokens, accessibility, components
│   ├── SKILL.md
│   ├── universal-prompt.md
│   ├── references/ (7 files)
│   ├── scripts/ (6 files)
│   ├── evals/ (5 files)
│   └── assets/templates/ (3 files)
│
├── staff-engineer/              # Code, architecture, security, performance
│   ├── SKILL.md
│   ├── universal-prompt.md
│   ├── references/ (7 files)
│   ├── scripts/ (7 files)
│   ├── evals/ (5 files)
│   └── assets/templates/ (2 files)
│
├── platform-engineer/           # IaC, K8s, CI/CD, observability, SRE
│   ├── SKILL.md
│   ├── universal-prompt.md
│   ├── references/ (2 files + more coming)
│   ├── scripts/ (3 files + more coming)
│   ├── evals/ (2 files)
│   └── assets/templates/ (5 files)
│
└── agentic-orchestration/       # Multi-agent workflows, consensus, HITL
    ├── SKILL.md
    ├── universal-prompt.md
    ├── references/ (1 file + more coming)
    ├── scripts/ (3 files + more coming)
    ├── evals/ (2 files)
    └── assets/templates/ (4 files)
```

---

## 🌐 Universal Portability

**Every skill works in ANY AI tool** — not just Goose.

### Copy the Universal Prompt
```bash
# Each skill has a universal-prompt.md with a "SYSTEM PROMPT — PASTE THIS" section
cat skills/product-engineering/universal-prompt.md
cat skills/design-skill/universal-prompt.md
cat skills/staff-engineer/universal-prompt.md
cat skills/platform-engineer/universal-prompt.md
cat skills/agentic-orchestration/universal-prompt.md
```

### Paste Into Your Tool
| Tool | Location |
|------|----------|
| **Claude Code** | `.claude/CLAUDE.md` |
| **Codex** | `AGENTS.md` |
| **Gemini** | System Instructions |
| **Cursor** | Settings → Rules for AI |
| **Copilot** | `.github/copilot-instructions.md` |
| **Any CLI** | Prepend to prompt |

### Deterministic Scripts (Run Anywhere)
```bash
# All scripts: Python 3.10+, zero external deps
python skills/product-engineering/scripts/generate-prd.py --context "Add notifications"
python skills/design-skill/scripts/audit-accessibility.py --file Component.tsx
python skills/staff-engineer/scripts/scan-security.py --path ./src
python skills/platform-engineer/scripts/validate-terraform.py --path ./infra
python skills/agentic-orchestration/scripts/decompose-task.py --task "Add notifications"
```

---

## 🧪 Evaluation & Quality

Each skill includes **evals** (YAML test cases) for validation:

```bash
# Run evals to verify skill behavior
# Each eval defines: input, expected output, success criteria
# Example: design-skill/evals/login-page-design.yaml
# Example: staff-engineer/evals/sql-injection-prevention.yaml
```

---

## 📄 License

All skills: **MIT License** — Use freely in any project, commercial or personal.

---

## 🤝 Contributing

1. Skills follow the same structure: `SKILL.md`, `universal-prompt.md`, `references/`, `scripts/`, `evals/`, `assets/`
2. Universal prompts must work in ANY AI tool
3. Scripts must be deterministic Python 3.10+ with zero required dependencies
4. Evals must have clear success criteria
5. Templates must be production-ready

---

## 🎓 Philosophy

> **We don't build features. We build a company that builds features.**

Each skill is a **specialized role** with deep expertise. The **orchestration layer** coordinates them into an **agentic loop** that:
- Decomposes complex work
- Executes in parallel with validation
- Achieves consensus through weighted voting
- Compresses context for clean handoffs
- Includes human checkpoints for irreversible decisions
- Traces everything for observability

**This is how modern software gets built.** 🚀