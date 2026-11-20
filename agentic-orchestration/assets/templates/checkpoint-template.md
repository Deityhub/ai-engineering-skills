# Human Checkpoint: {{ .CheckpointType | title }}

## Context
- **Feature**: {{ .Feature }}
- **PR**: {{ .PR }}
- **DAG Node**: {{ .NodeId }}
- **All Validations**: {{ .ValidationsStatus }}

## Summary
{{ .Summary }}

## Decisions Requiring {{ .Action }}
{{ .Decisions }}

## Artifacts
{{ .Artifacts }}

## Actions
- [ ] **{{ .ApproveAction }}** — {{ .ApproveDescription }}
- [ ] **{{ .RejectAction }}** — {{ .RejectDescription }}
- [ ] **{{ .RequestChangesAction }}** — Specify in comments

## Timeout
{{ .Timeout }} — {{ .TimeoutAction }} if no action.

---

## Checkpoint Types

### Approval (Production Deploy, Schema Change, Security Exception)
- **Timeout**: 4 business hours
- **Timeout Action**: Auto-reject
- **Escalation**: Page on-call, Slack #incidents, bridge call in 5min
- **Approvers**: Tech lead + Security (for security exceptions)

### Review (Architecture Decision, Cost >$10k/mo, New Vendor)
- **Timeout**: 24 hours
- **Timeout Action**: Escalate to director
- **Escalation**: Slack #architecture-review
- **Reviewers**: Architect + affected team leads

### Information (Incident Declared, Budget Exhausted, SLO Breach)
- **Timeout**: Immediate (page)
- **Timeout Action**: N/A
- **Escalation**: Page on-call immediately
- **Recipients**: On-call + team + stakeholders

---

## Template Variables
| Variable | Description | Example |
|----------|-------------|---------|
| `CheckpointType` | approval, review, information | `approval` |
| `Feature` | Feature name | `Real-time Notifications` |
| `PR` | Pull request link/number | `#2847` |
| `NodeId` | DAG node ID | `consensus` |
| `ValidationsStatus` | All validations passed? | `✅ Passed (security, perf, arch, test)` |
| `Summary` | One-paragraph summary | `WebSocket server + Redis Pub/Sub + FE integration. Canary 5% → 100% over 2h.` |
| `Decisions` | Bullet list of decisions | `1. Enable feature flag for 5% canary\n2. Provision 3 Redis replicas ($120/mo)` |
| `Artifacts` | Links to runbooks, reviews, ADRs | `[Runbook](link) | [Load Test](link) | [Security Review](link)` |
| `ApproveAction` | Button label | `Approve Canary` |
| `ApproveDescription` | What approve means | `Proceed with 5% canary rollout` |
| `RejectAction` | Button label | `Reject` |
| `RejectDescription` | What reject means | `Stop rollout, keep feature flag off` |
| `RequestChangesAction` | Button label | `Request Changes` |
| `Timeout` | Human-readable timeout | `4 business hours` |
| `TimeoutAction` | What happens on timeout | `Auto-rejects if no action` |