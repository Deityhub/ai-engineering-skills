# Platform Engineer Skill — Portability Guide

## Universal Prompt
Copy `/skills/platform-engineer/universal-prompt.md` into **any** AI tool:
- **Claude Code**: `.claude/CLAUDE.md` or project `CLAUDE.md`
- **Codex**: `AGENTS.md`
- **Gemini**: System Instructions
- **Cursor**: Settings → Rules for AI
- **Copilot**: `.github/copilot-instructions.md`
- **Goose**: `load_skill("platform-engineer")`

## References (Portable Markdown)
All files in `/references/` are plain Markdown — readable anywhere:
- `iac-patterns.md` — Terraform/Pulumi/CloudFormation
- `kubernetes-patterns.md` — K8s, GitOps, Operators, Service Mesh
- `cicd-patterns.md` — Pipeline design, progressive delivery, feature flags
- `observability-patterns.md` — OpenTelemetry, Prometheus, Loki, Tempo
- `cloud-patterns.md` — AWS/GCP/Azure networking, IAM, serverless
- `sre-practices.md` — SLOs, error budgets, incident response, chaos
- `cost-optimization.md` — FinOps, rightsizing, savings plans

## Scripts (Python 3.10+, Zero External Deps for Core)
```bash
# All scripts run with: python3 script.py [args]

# Terraform validation with OPA policy
python3 scripts/validate-terraform.py --path ./infra --policy ./policies

# Kubernetes manifest analysis
python3 scripts/analyze-k8s.py --manifests ./k8s --fail-on critical

# CI/CD pipeline linting
python3 scripts/lint-pipeline.py --file .github/workflows/deploy.yml

# SLO burn rate checking
python3 scripts/check-slos.py --prometheus http://prom:9090 --window 30d

# Infrastructure cost estimation
python3 scripts/estimate-costs.py --terraform ./infra --kubernetes ./k8s

# Runbook generation from alerts
python3 scripts/generate-runbook.py --alert HighErrorRate --service api
```

### Script Capabilities Without External Tools
| Script | Fallback If Tool Missing |
|--------|-------------------------|
| `validate-terraform.py` | Parses HCL for basic validation, runs `terraform fmt/validate` if available |
| `analyze-k8s.py` | YAML parsing for resource quotas, network policies, security contexts |
| `lint-pipeline.py` | YAML schema validation for GitHub Actions/GitLab CI/Buildkite |
| `check-slos.py` | PromQL parser + burn rate calculation (no Prometheus needed for logic) |
| `estimate-costs.py` | Infracost/Kubecost integration if available, else cloud pricing API |
| `generate-runbook.py` | Template-based, no external deps |

## Goose-Native Features (Bonus)
When loaded in Goose (`load_skill("platform-engineer")`):
- **Progressive disclosure**: Only SKILL.md loads initially; references/scripts load on demand
- **Agentic delegation**: Use `delegate` tool with `source: "platform-engineer"` for parallel validation
- **Context compression**: `scripts/compress-context.py` (shared with other skills) compresses handoffs to <3000 tokens

## Minimal Viable Usage (Any AI)
```markdown
# Paste this into any AI tool's system prompt:

You are a Senior Platform/DevOps Engineer. Apply these principles:
1. Infrastructure as Code Everything — No manual console clicks
2. Immutable Infrastructure — Replace, don't mutate
3. Observability First — Logs, metrics, traces, alerts built-in
4. Security by Default — Least privilege, encryption, secrets management
5. Developer Experience Matters — Self-service, fast feedback, golden paths
6. Cost Consciousness — Right-size, auto-scale, spot, FinOps
7. Resilience by Design — Multi-AZ, circuit breakers, chaos engineering, DR tested

For the current project's cloud/platform, apply the relevant patterns from references/.
```

## Skill Package (`.skill` file)
```bash
cd /Users/deityhub/work/skills/platform-engineer
tar -czf ../platform-engineer.skill *
```
Import in Goose: `load_skill("platform-engineer.skill")`

## Version Compatibility
| Component | Minimum Version |
|-----------|----------------|
| Python | 3.10 |
| Terraform | 1.5+ (if used) |
| kubectl | 1.28+ (if used) |
| helm | 3.12+ (if used) |
| Goose | 1.0 (for native features) |
| Any AI tool | System prompt support |