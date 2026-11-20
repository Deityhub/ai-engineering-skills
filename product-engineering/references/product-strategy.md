# Product Strategy Reference

## Vision Framework

### Vision Statement Template
```
"A world where [TARGET USERS] can [CORE BENEFIT] without [CURRENT PAIN]."
```

**Examples:**
- **Slack**: "A world where teams can communicate effortlessly without email overload."
- **Airbnb**: "A world where anyone can belong anywhere without hotel constraints."
- **Stripe**: "A world where developers can accept payments without banking complexity."
- **Notion**: "A world where teams can organize knowledge without rigid tools."

### Strategy = Diagnosis + Guiding Policy + Coherent Actions (Rumelt)

| Component | Questions | Output |
|-----------|-----------|--------|
| **Diagnosis** | What's the fundamental challenge? What's the root cause? | Clear problem statement |
| **Guiding Policy** | Our overall approach to overcome the challenge | Strategic direction |
| **Coherent Actions** | Specific, coordinated bets we're making | Roadmap initiatives |

**Example:**
- **Diagnosis**: "Developers spend 40% of time on undifferentiated infrastructure instead of product code."
- **Guiding Policy**: "Provide managed infrastructure abstractions that reduce ops burden to <10%."
- **Coherent Actions**: 1) Launch managed Kubernetes, 2) Serverless functions, 3) Managed databases, 4) Observability suite.

---

## North Star Metric (NSM)

### NSM Criteria
| Criterion | Test |
|-----------|------|
| **Leading Indicator** | Predicts long-term success, not just current revenue |
| **Measurable** | Instrumented, queryable, unambiguous |
| **Actionable** | Team can directly influence |
| **Customer Value** | Represents value delivered to user |
| **Aligned** | Unifies team priorities |

### NSM by Company Type
| Type | NSM Examples |
|------|--------------|
| **SaaS (B2B)** | Weekly active teams, MRR per customer, Net revenue retention |
| **Consumer** | Daily active users, Sessions per user, Content created |
| **Marketplace** | Transactions (GMV), Take rate, Repeat purchase rate |
| **Platform/API** | API calls, Active developers, Revenue per developer |
| **Content** | Time spent, Content created, Shares per piece |

### NSM Validation Checklist
- [ ] Single metric (not a dashboard)
- [ ] Leading indicator of business health
- [ ] Measurable daily/weekly
- [ ] Team can move it in a sprint
- [ ] Connects to revenue long-term
- [ ] Understood by every team member

---

## OKR Framework

### Structure
```
Objective: Qualitative, ambitious, inspiring, time-bound (quarterly)
  KR1: Quantitative, leading indicator, measurable weekly
  KR2: Quantitative, lagging indicator, measurable monthly
  KR3: Health metric (guardrail — don't optimize at expense of)
```

### OKR Quality Checklist
| Criterion | Good | Bad |
|-----------|------|-----|
| **Objective** | "Deliver magical onboarding experience" | "Improve onboarding" |
| **KR** | "Activation rate 25% → 40% by Q2 end" | "Increase activation" |
| **Health KR** | "Latency p99 < 500ms" | (missing) |

### OKR Anti-Patterns
| Anti-Pattern | Fix |
|--------------|-----|
| Too many OKRs | Max 3 Objectives, 3-5 KRs each |
| Output-based KRs | "Launch 5 features" → "Activation +15%" |
| Sandbagging | Stretch goals, 70% achievement = success |
| Set and forget | Weekly check-ins, quarterly grading |

---

## Strategy Communication Artifacts

### One-Pager Strategy Doc
```markdown
# [Product] Strategy — [Quarter/Year]

## Vision
[Vision statement]

## Diagnosis
[Root problem, evidence]

## Guiding Policy
[Our approach]

## Strategic Bets (3-5)
1. **Bet**: [Initiative] — **Why**: [Reasoning] — **Success**: [Metric]
2. **Bet**: [Initiative] — **Why**: [Reasoning] — **Success**: [Metric]

## OKRs
### O1: [Objective]
- KR1: [Metric] from [X] to [Y] by [Date]
- KR2: [Metric] from [X] to [Y] by [Date]
- Health: [Guardrail metric] stays above [Threshold]

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
```

### Roadmap Visualization
```
Quarter: Q1     Q2     Q3     Q4
├─ Bet 1: ████████░░░░  (Discovery → Beta → Launch)
├─ Bet 2: ░░████████░░  (Design → Build → Beta)
├─ Bet 3: ░░░░████████  (Research → Prototype)
└─ Health: ████████████ (Continuous)
```

---

## Strategy Review Cadence

| Cadence | Participants | Duration | Focus |
|---------|--------------|----------|-------|
| **Weekly** | Product triad (PM, Eng, Design) | 30min | Progress, blockers, decisions |
| **Bi-weekly** | Extended team | 60min | Demo, metrics, learnings |
| **Monthly** | Leadership | 60min | OKR progress, risks, resource asks |
| **Quarterly** | Company | 90min | Strategy review, next quarter bets |

---

## Decision Log (Lightweight ADR for Product)
```markdown
# Decision: [Title]

## Context
[What situation demands a decision?]

## Options Considered
1. [Option A] — Pros/Cons
2. [Option B] — Pros/Cons
3. [Option C] — Pros/Cons

## Decision
[Chosen option]

## Reasoning
[Why this over others?]

## Consequences
- Positive: [...]
- Negative: [...]
- Mitigations: [...]

## Review Date
[When to revisit]
```