# Routing Rules — Intelligent Skill Selection

## Overview
The AI Engineering Company uses intelligent routing to determine which skills to engage for any given request. This document defines the routing logic, keyword mappings, and decision criteria.

## Skill Keyword Mapping

| Skill | Primary Keywords | Secondary Keywords | Weight |
|-------|------------------|-------------------|--------|
| **product-engineering** | strategy, vision, roadmap, prd, experiment, metrics, north star, okr, discovery, prioritize | rice, wsjf, kano, ab test, feature flag, stakeholder, user interview, jobs to be done | 1.0 |
| **design-skill** | ui, ux, design, component, token, accessibility, a11y, wcag, figma, responsive | breakpoint, color, typography, dark mode, design system, cross-platform, swiftui, flutter | 1.0 |
| **staff-engineer** | code, architecture, security, performance, refactor, adr, sql injection, cache, database | api, microservice, monolith, clean code, solid, coupling, cohesion, testing, profiling | 1.0 |
| **platform-engineer** | terraform, kubernetes, k8s, ci/cd, pipeline, github actions, gitlab ci, observability | prometheus, grafana, loki, tempo, slo, sli, error budget, incident, runbook, finops | 1.0 |
| **agentic-orchestration** | agent, workflow, dag, consensus, delegation, orchestration, multi-agent, parallel | validation, human-in-the-loop, hitl, critic, red-team, coordination | 1.0 |

## Routing Algorithm

```
1. Tokenize request (lowercase, remove punctuation)
2. Score each skill: count keyword matches × weight
3. Apply thresholds:
   - Score ≥ 3 → Skill required
   - Score 1-2 → Skill optional
   - Score 0 → Skill not needed
4. Determine mode:
   - 0 skills → Default full stack (Product, Design, Staff Eng, Platform)
   - 1 skill → Single skill mode
   - 2 skills → Targeted parallel mode
   - ≥3 skills → Full agentic loop
5. Always add agentic-orchestration for multi-skill modes
```

## Mode Definitions

### Single Skill Mode
- **Trigger**: Request clearly maps to one domain
- **Execution**: Direct delegation to that skill
- **Validation**: Skill's internal validation gates
- **Example**: "Fix SQL injection in user service" → Staff Engineer only

### Targeted Parallel Mode
- **Trigger**: Two clearly distinct domains
- **Execution**: Parallel delegation to both skills
- **Validation**: Cross-skill validation + consensus
- **Example**: "Design and implement new dashboard" → Design + Staff Engineer

### Full Agentic Loop
- **Trigger**: Complex request spanning 3+ domains OR ambiguous request
- **Execution**: Full DAG with all 5 skills
- **Validation**: All gates + weighted consensus + HITL
- **Example**: "Add real-time notifications with WebSocket" → All 5 skills

## Ambiguity Resolution

| Ambiguity | Resolution |
|-----------|------------|
| No clear keywords | Default to full agentic loop (safe default) |
| Conflicting keywords | Score-based, higher score wins |
| "Build X" without context | Full agentic loop (needs strategy + design + build + deploy) |
| "Fix bug" without details | Staff Engineer + targeted routing based on bug type |

## Skill Dependency Graph

```
                    ┌─────────────────┐
                    │  PRODUCT ENG    │
                    │  (Strategy)     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │   DESIGN    │ │ STAFF ENG   │ │  PLATFORM   │
       │  (Specs)    │ │  (Arch)     │ │  (Infra)    │
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │  IMPLEMENTATION │
                    │  (Staff Eng)    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
       ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
       │  SECURITY   │ │ PERFORMANCE │ │   TESTING   │
       └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │   CONSENSUS     │
                    │ (Orchestration) │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   HITL GATE     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    DEPLOY       │
                    │  (Platform)     │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    RELEASE      │
                    │ (Orchestration) │
                    └─────────────────┘
```

## Routing Examples

| User Request | Mode | Skills | Reasoning |
|--------------|------|--------|-----------|
| "Add dark mode toggle" | Targeted | Design, Staff Eng | UI + implementation |
| "Design new onboarding flow" | Targeted | Product, Design | Strategy + specs |
| "Set up CI/CD pipeline" | Targeted | Platform, Staff Eng | Infra + arch |
| "Add real-time notifications" | Full Loop | All 5 | Spans all domains |
| "Optimize database queries" | Single | Staff Eng | Pure perf |
| "Audit WCAG compliance" | Single | Design | Pure a11y |
| "Prioritize Q3 roadmap" | Single | Product | Pure prioritization |
| "Build user authentication" | Full Loop | All 5 | Security + UI + API + Infra |

## Configuration

Routing can be customized via `routing-config.yaml`:

```yaml
skills:
  product-engineering:
    keywords: [strategy, vision, roadmap, prd, experiment, ...]
    weight: 1.0
    threshold: 2

modes:
  full_agentic_loop:
    min_skills: 3
    always_include_orchestration: true
  targeted_parallel:
    min_skills: 2
    max_skills: 2
  single_skill:
    max_skills: 1

defaults:
  ambiguous_request: full_agentic_loop
  include_orchestration_for_multi: true
```