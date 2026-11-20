# Product Engineering Skill

**Product Engineering Lead skill for Goose** — Bridges business strategy and technical execution. Translates vision into actionable specs, prioritizes ruthlessly, designs experiments, owns metrics, and ships value continuously.

---

## Quick Start

### In Goose
```bash
load_skill("product-engineering")
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

### 🎯 Product Strategy & Vision
- Vision statements, strategy (diagnosis + policy + actions)
- North Star Metric definition and validation
- OKR structure with leading/lagging/health metrics
- Strategy communication artifacts

### 🔍 Continuous Discovery
- Jobs-to-be-Done (JTBD) interview frameworks
- Opportunity Solution Trees
- Weekly customer interview habits
- Usability testing protocols
- Competitive scanning

### 📊 Ruthless Prioritization
- **RICE Scoring**: Reach × Impact × Confidence / Effort
- **WSJF**: Weighted Shortest Job First (SAFe)
- **Kano Model**: Must-be, Performance, Delighters
- Custom framework builder

### 🧪 Experimentation & A/B Testing
- Hypothesis-driven experiment design
- Statistical power analysis, sample size calculators
- Feature flag experimentation infrastructure
- Experiment templates with launch checklists
- Results interpretation framework (Ship/Iterate/Kill/Extend)

### 📈 Metrics & Analytics
- Metric hierarchy: North Star → Leading → Lagging → Health
- Good metric checklist (SMART+)
- Dashboard design principles
- Guardrail metrics for safe experimentation

### 📝 Stakeholder Communication
- Cadence templates: Daily, Bi-weekly, Weekly, Monthly, Quarterly
- Written update templates (OKR progress, metrics, risks, next)
- Business review structure
- Changelog/customer communication

### 🛡️ Tech Debt & Quality
- 20% capacity budget for debt reduction
- Debt registry with interest/principal/risk tracking
- Quality gates: code review, tests, performance, a11y, security, observability
- Quarterly debt sprints

---

## File Structure

```
product-engineering/
├── SKILL.md                    # Goose-native manifest
├── universal-prompt.md         # Portable system prompt (COPY THIS)
├── PORTABILITY.md              # Tool-specific setup guide
├── README.md                   # This file
├── LICENSE.txt                 # MIT
├── references/                 # Portable markdown references
│   ├── product-strategy.md
│   ├── discovery.md
│   ├── prioritization.md
│   ├── experimentation.md
│   ├── metrics.md
│   ├── stakeholder-communication.md
│   └── tech-debt.md
├── scripts/                    # Deterministic Python scripts
│   ├── generate-prd.py
│   ├── design-experiment.py
│   ├── prioritize.py
│   ├── define-metrics.py
│   ├── weekly-update.py
│   └── health-check.py
├── evals/                      # Test cases
│   ├── prd-generation.yaml
│   ├── experiment-design.yaml
│   ├── prioritization.yaml
│   └── metrics-hierarchy.yaml
├── assets/templates/
│   ├── prd.md
│   ├── experiment.md
│   ├── metric-definition.md
│   ├── weekly-update.md
│   └── roadmap.md
└── tests/                      # Unit tests for scripts
    ├── conftest.py
    ├── test_generate_prd.py
    └── test_prioritize.py
```

---

## Scripts Usage

All scripts are **standalone Python 3.10+** with zero external dependencies.

```bash
# PRD generation
python scripts/generate-prd.py --context "Add real-time notifications" --template feature

# Experiment design calculator
python scripts/design-experiment.py --hypothesis "New onboarding increases activation" --metric activation_rate --mde 0.05

# Prioritization (RICE/WSJF/Kano)
python scripts/prioritize.py --framework rice --features features.csv

# Metric hierarchy builder
python scripts/define-metrics.py --north-star "Weekly active workspaces"

# Weekly stakeholder update generator
python scripts/weekly-update.py --github-org myorg --jira-project TEAM --mixpanel-project 12345

# Team/product health check
python scripts/health-check.py --team platform --quarter Q4
```

---

## Evals (Test Cases)

Run evals to verify skill behavior:
```bash
# Each eval is a YAML file with input, expected output, and success criteria
# Example: prd-generation.yaml tests PRD template completion from context
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
| Optional: GitHub CLI | For weekly-update.py |
| Optional: Jira CLI | For weekly-update.py |
| Optional: Analytics APIs | For enhanced metrics |

---

## License

MIT — Use freely in any project, commercial or personal.

---

## Philosophy

> **Product is not a feature factory. It's a value discovery engine.**
>
> 1. **Outcomes Over Output** — Measure success by user/business impact
> 2. **Evidence Over Opinion** — Decisions backed by data, discovery, experiments
> 3. **Ruthless Prioritization** — If everything is priority, nothing is
> 4. **Ship to Learn** — Smallest viable experiment → measure → iterate
> 5. **Tech Debt as Investment** — Pay down strategically, allocate 20% capacity
> 6. **Alignment Through Artifacts** — PRDs, specs, dashboards, runbooks
> 7. **Customer Voice in Every Room** — Discovery is continuous