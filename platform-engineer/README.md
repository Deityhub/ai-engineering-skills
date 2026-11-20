# Platform Engineer Skill

**Senior Platform/DevOps Engineer skill for Goose** — Builds scalable, reliable, observable infrastructure. Expert in IaC, Kubernetes, CI/CD, cloud, SRE, and cost optimization.

---

## Quick Start

### In Goose
```bash
load_skill("platform-engineer")
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

### 🏗️ Infrastructure as Code
- Terraform modules, workspaces, state management, drift detection, policy as code (OPA)
- Pulumi component resources, stack references, CrossGuard policies
- CloudFormation nested stacks, CDK patterns

### ☸️ Kubernetes Patterns
- Managed clusters (EKS/GKE/AKS), node pools, Cluster API
- GitOps (ArgoCD/Flux), Helm library charts, values schemas
- Operators (controller-runtime/Kubebuilder), CRDs, webhooks
- Service mesh (Istio/Linkerd/Cilium): mTLS, traffic management, auth

### 🚀 CI/CD Pipeline Design
- Pipeline as code (GitHub Actions, GitLab CI, Buildkite, Tekton)
- Artifact promotion, progressive delivery (canary, blue/green)
- Feature flags (LaunchDarkly, Unleash), decouple deploy from release
- Gates: lint → test → build → SAST/SCA → integration → deploy

### 📊 Observability (OpenTelemetry Native)
- Unified collector: metrics (Prometheus), logs (Loki), traces (Tempo)
- RED/USE/SLI metrics, cardinality management
- Structured JSON logging, W3C TraceContext
- SLO-based alerting with burn rates, runbook links

### ☁️ Cloud Patterns (AWS/GCP/Azure)
- Networking: VPC, Transit Gateway, PrivateLink, DNS, load balancing
- Security/IAM: Least privilege, ABAC, secrets rotation, compliance
- Serverless: Lambda/Cloud Functions/Functions, EventBridge/Eventarc/Event Grid
- Containers: ECS/Fargate/EKS, Cloud Run/GKE, Container Apps/AKS

### 🎯 SRE Practices
- SLO/SLI/SLA framework (availability, latency, throughput, durability)
- Error budgets with burn rate alerts (1×, 2×, 10×)
- Incident response: detect → triage → mitigate → resolve → postmortem
- Chaos engineering: LitmusChaos, Chaos Mesh, AWS FIS

### 💰 Cost Optimization (FinOps)
- Rightsizing: VPA, Compute Optimizer, Karpenter
- Savings Plans / Committed Use Discounts
- Tagging strategy, showback/chargeback, anomaly detection
- Waste elimination: orphans, zombies, data transfer optimization

---

## File Structure

```
platform-engineer/
├── SKILL.md                    # Goose-native manifest
├── universal-prompt.md         # Portable system prompt (COPY THIS)
├── PORTABILITY.md              # Tool-specific setup guide
├── README.md                   # This file
├── LICENSE.txt                 # MIT
├── references/                 # Portable markdown references
│   ├── iac-patterns.md
│   ├── kubernetes-patterns.md
│   ├── cicd-patterns.md
│   ├── observability-patterns.md
│   ├── cloud-patterns.md
│   ├── sre-practices.md
│   └── cost-optimization.md
├── scripts/                    # Deterministic Python scripts
│   ├── validate-terraform.py
│   ├── analyze-k8s.py
│   ├── lint-pipeline.py
│   ├── check-slos.py
│   ├── estimate-costs.py
│   └── generate-runbook.py
├── evals/                      # Test cases
│   ├── terraform-validation.yaml
│   ├── k8s-security.yaml
│   ├── pipeline-linting.yaml
│   ├── slo-burn-rate.yaml
│   └── cost-estimation.yaml
├── assets/templates/
│   ├── terraform-module.tf
│   ├── helm-chart.yaml
│   ├── pipeline.yaml
│   ├── dashboard.json
│   ├── runbook.md
│   └── slo.yaml
└── tests/                      # Unit tests for scripts
    ├── conftest.py
    ├── test_validate_terraform.py
    ├── test_analyze_k8s.py
    └── test_lint_pipeline.py
```

---

## Scripts Usage

All scripts are **standalone Python 3.10+** with zero external dependencies (optional tools enhance functionality).

```bash
# Terraform validation with OPA policy
python scripts/validate-terraform.py --path ./infra --policy ./policies

# Kubernetes manifest analysis
python scripts/analyze-k8s.py --manifests ./k8s --fail-on critical

# CI/CD pipeline linting
python scripts/lint-pipeline.py --file .github/workflows/deploy.yml

# SLO burn rate checking
python scripts/check-slos.py --prometheus http://prom:9090 --window 30d

# Infrastructure cost estimation
python scripts/estimate-costs.py --terraform ./infra --kubernetes ./k8s

# Runbook generation from alerts
python scripts/generate-runbook.py --alert HighErrorRate --service api
```

---

## Evals (Test Cases)

Run evals to verify skill behavior:
```bash
# Each eval is a YAML file with input, expected output, and success criteria
# Example: terraform-validation.yaml tests TF module validation with policy checks
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
| Terraform | 1.5+ (optional, for scripts) |
| kubectl | 1.28+ (optional, for scripts) |
| helm | 3.12+ (optional, for scripts) |
| Cloud CLIs | Optional (aws, gcloud, az) |

---

## License

MIT — Use freely in any project, commercial or personal.

---

## Philosophy

> **Infrastructure is code. Treat it like code.** Version it, test it, review it, deploy it.
>
> 1. **Infrastructure as Code Everything** — No manual console clicks
> 2. **Immutable Infrastructure** — Replace, don't mutate
> 3. **Observability First** — You can't fix what you can't see
> 4. **Security by Default** — Least privilege, encryption, secrets management
> 5. **Developer Experience Matters** — Self-service, fast feedback, golden paths
> 6. **Cost Consciousness** — Right-size, auto-scale, spot, FinOps
> 7. **Resilience by Design** — Multi-AZ, circuit breakers, chaos engineering, DR tested