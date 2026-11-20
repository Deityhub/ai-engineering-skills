# Runbook: {{ .AlertName }}

## Overview
- **Service**: {{ .Service }}
- **Team**: {{ .Team }}
- **Severity**: SEV-{{ .Severity }}
- **SLO Impact**: {{ .SLIImpact }}

## Symptoms
- **Alert**: {{ .AlertName }}
- **Dashboard**: {{ .DashboardLink }}
- **Logs**: {{ .LogsQuery }}

## Diagnosis Steps
1. Check {{ .PrimaryMetric }} on {{ .DashboardLink }}
2. Run: `kubectl logs -l app={{ .App }} --since=10m | grep ERROR`
3. Check dependency: {{ .UpstreamService }} status on {{ .UpstreamDashboard }}

## Mitigation (Quick Fixes)
- [ ] **Rollback**: `argocd app rollback {{ .App }} <revision>`
- [ ] **Scale**: `kubectl scale deployment {{ .App }} --replicas={{ .ScaleReplicas }}`
- [ ] **Feature Flag**: Disable `{{ .FeatureFlag }}` in LaunchDarkly
- [ ] **Circuit Break**: `kubectl annotate svc {{ .App }} "traffic.split=0"`

## Escalation
- **SEV-1**: Page {{ .OnCall }}, Slack #incidents, bridge call in 5min
- **SEV-2**: Slack #incidents, acknowledge in 15min
- **SEV-3**: Ticket, next business day

## Postmortem
- **Template**: {{ .PostmortemTemplate }}
- **Due**: 5 business days
- **Reviewers**: {{ .Reviewers }}

---

## Runbook Template Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `AlertName` | Exact alert name from Alertmanager | `HighErrorRate` |
| `Service` | Service name | `api` |
| `Team` | Owning team | `platform` |
| `Severity` | 1, 2, or 3 | `1` |
| `SLIImpact` | Which SLI, budget burn rate | `Availability, 5x burn rate` |
| `DashboardLink` | Grafana dashboard URL | `https://grafana.example.com/d/api` |
| `LogsQuery` | Loki query | `{app="api"} |= "ERROR"` |
| `PrimaryMetric` | Key metric to check | `http_requests_total{code=~"5.."}` |
| `App` | Kubernetes app label | `api` |
| `UpstreamService` | Dependency service | `auth` |
| `UpstreamDashboard` | Dependency dashboard | `https://grafana.example.com/d/auth` |
| `ScaleReplicas` | Replicas to scale to | `10` |
| `FeatureFlag` | LaunchDarkly flag | `new-checkout-flow` |
| `PostmortemTemplate` | Postmortem template link | `https://wiki.example.com/postmortem` |
| `Reviewers` | Postmortem reviewers | `@team-leads` |