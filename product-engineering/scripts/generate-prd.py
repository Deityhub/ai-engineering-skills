#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRD Generator — Creates Product Requirements Documents from templates.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from string import Template


PRD_TEMPLATE = Template("""# PRD: ${feature_name}

## Context
- **Problem**: ${problem}
- **Evidence**: ${evidence}
- **Assumptions**: ${assumptions}

## Success Metrics
- **Primary (NSM impact)**: ${primary_metric} from ${baseline} to ${target} by ${target_date}
- **Secondary**: ${secondary_metrics}
- **Guardrail**: ${guardrail_metric} must not degrade below ${guardrail_threshold}

## Scope
### In Scope
${in_scope}

### Out of Scope
${out_of_scope}

## User Stories
${user_stories}

## Technical Approach
- Architecture decision links: ${adr_links}
- API contracts: ${api_contracts}
- Data model changes: ${data_model}
- Migration strategy: ${migration}

## Risks & Mitigations
| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
${risks}

## Rollout Plan
1. Internal dogfood → 2. Beta (${beta_percent}%) → 3. Gradual rollout (${rollout_steps}) → 4. Full launch
- Feature flag: \`${feature_flag}\`
- Rollback: Single-click via flag

## Post-Launch
- Success review: ${review_date} (2 weeks post-launch)
- Metrics dashboard: ${dashboard_link}
- Retrospective: ${retro_date}
""")


def main():
    parser = argparse.ArgumentParser(description="Generate PRD from template")
    parser.add_argument("--context", required=True, help="Feature context/description")
    parser.add_argument("--template", choices=["feature", "experiment", "tech-debt", "migration"], default="feature")
    parser.add_argument("--output", "-o", help="Output file")
    parser.add_argument("--interactive", action="store_true", help="Interactive mode")
    args = parser.parse_args()

    context = args.context

    if args.interactive:
        print("📝 Interactive PRD Generation")
        print("=" * 40)
        feature_name = input("Feature name: ").strip()
        problem = input("Problem statement: ").strip()
        evidence = input("Evidence (data, quotes, links): ").strip()
        assumptions = input("Assumptions (comma-separated): ").strip()
        primary_metric = input("Primary metric: ").strip()
        baseline = input("Baseline value: ").strip()
        target = input("Target value: ").strip()
        target_date = input("Target date (YYYY-MM-DD): ").strip()
        secondary_metrics = input("Secondary metrics (comma-separated): ").strip()
        guardrail_metric = input("Guardrail metric: ").strip()
        guardrail_threshold = input("Guardrail threshold: ").strip()
        in_scope = input("In scope (one per line, empty to finish):\n")
        out_of_scope = input("Out of scope (one per line, empty to finish):\n")
        user_stories = input("User stories (As a... I want... So that...):\n")
        adr_links = input("ADR links: ").strip()
        api_contracts = input("API contracts: ").strip()
        data_model = input("Data model changes: ").strip()
        migration = input("Migration strategy: ").strip()
        risks = input("Risks (Risk|Likelihood|Impact|Mitigation per line):\n")
        feature_flag = input("Feature flag name: ").strip()
        beta_percent = input("Beta %: ").strip() or "5"
        rollout_steps = input("Rollout steps (e.g., 25/50/100): ").strip() or "25/50/100"
        review_date = input("Success review date (YYYY-MM-DD): ").strip()
        dashboard_link = input("Metrics dashboard link: ").strip()
        retro_date = input("Retrospective date (YYYY-MM-DD): ").strip()
    else:
        # Parse from context (simplified)
        feature_name = context.split("\n")[0][:80]
        problem = context
        evidence = "TBD — add discovery insights"
        assumptions = "TBD"
        primary_metric = "Activation rate"
        baseline = "25%"
        target = "40%"
        target_date = (datetime.now().replace(month=datetime.now().month+3)).strftime("%Y-%m-%d")
        secondary_metrics = "Time to value, Feature adoption"
        guardrail_metric = "Latency p99"
        guardrail_threshold = "500ms"
        in_scope = "- Core functionality\n- Basic UI\n- API endpoints"
        out_of_scope = "- Advanced analytics\n- Mobile app (phase 2)"
        user_stories = "As a user I want to [action] so that [benefit]"
        adr_links = "TBD"
        api_contracts = "TBD"
        data_model = "TBD"
        migration = "TBD"
        risks = "Technical complexity|Medium|High|Spike first\nScope creep|High|Medium|Strict scope"
        feature_flag = "feature-" + feature_name.lower().replace(" ", "-")
        beta_percent = "5"
        rollout_steps = "25/50/100"
        review_date = (datetime.now().replace(month=datetime.now().month+1)).strftime("%Y-%m-%d")
        dashboard_link = "https://dashboard.example.com"
        retro_date = (datetime.now().replace(month=datetime.now().month+1, day=15)).strftime("%Y-%m-%d")

    # Format risks table
    risk_lines = []
    for risk in risks.strip().split("\n"):
        parts = [p.strip() for p in risk.split("|")]
        if len(parts) == 4:
            risk_lines.append(f"| {parts[0]} | {parts[1]} | {parts[2]} | {parts[3]} |")
    risks_table = "\n".join(risk_lines) if risk_lines else "| TBD | | | |"

    # Format in_scope/out_of_scope
    in_scope_fmt = "\n".join(f"- {line.strip()}" for line in in_scope.strip().split("\n") if line.strip())
    out_of_scope_fmt = "\n".join(f"- {line.strip()}" for line in out_of_scope.strip().split("\n") if line.strip())

    prd = PRD_TEMPLATE.substitute(
        feature_name=feature_name,
        problem=problem,
        evidence=evidence,
        assumptions=assumptions,
        primary_metric=primary_metric,
        baseline=baseline,
        target=target,
        target_date=target_date,
        secondary_metrics=secondary_metrics,
        guardrail_metric=guardrail_metric,
        guardrail_threshold=guardrail_threshold,
        in_scope=in_scope_fmt,
        out_of_scope=out_of_scope_fmt,
        user_stories=user_stories,
        adr_links=adr_links,
        api_contracts=api_contracts,
        data_model=data_model,
        migration=migration,
        risks=risks_table,
        feature_flag=feature_flag,
        beta_percent=beta_percent,
        rollout_steps=rollout_steps,
        review_date=review_date,
        dashboard_link=dashboard_link,
        retro_date=retro_date,
    )

    if args.output:
        Path(args.output).write_text(prd, encoding="utf-8")
        print(f"PRD written to {args.output}")
    else:
        print(prd)


if __name__ == "__main__":
    main()