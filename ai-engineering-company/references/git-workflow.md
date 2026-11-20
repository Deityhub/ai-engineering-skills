# Git Workflow — Branch, Commit, PR, Merge, Release

## Branch Strategy

### Branch Types
| Prefix | Purpose | Lifetime | Merge Target |
|--------|---------|----------|--------------|
| `feat/` | New features | Days-weeks | main (via PR) |
| `fix/` | Bug fixes | Hours-days | main (via PR) |
| `refactor/` | Code improvements | Days | main (via PR) |
| `docs/` | Documentation | Hours | main (via PR) |
| `chore/` | Maintenance | Hours | main (via PR) |
| `release/` | Release preparation | Hours | main (tag) |
| `hotfix/` | Production fixes | Hours | main + release/* |

### Branch Naming Convention
```
<type>/<slug>-<YYYYMMDD>-<HHMMSS>-<short-sha>

Examples:
  feat/realtime-notifications-20261120-143000-a1b2c3d
  fix/sql-injection-user-service-20261120-101500-e4f5g6h
  refactor/extract-user-repository-20261120-090000-i7j8k9l
```

### Branch Protection Rules (main)
- Require PR review (2 approvals)
- Require status checks (all validation gates)
- Require linear history (squash merge)
- Require signed commits
- Restrict pushes to admins only

## Commit Convention

### Commit Message Format (Conventional Commits)
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
| Type | Description |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `refactor` | Code restructuring |
| `perf` | Performance improvement |
| `security` | Security fix |
| `docs` | Documentation |
| `test` | Test changes |
| `chore` | Maintenance |
| `build` | Build system |
| `ci` | CI/CD changes |
| `revert` | Revert commit |

### Scope
Module, component, or area affected: `auth`, `api`, `ui`, `db`, `infra`, `ci`, `docs`

### Examples
```
feat(auth): add WebSocket authentication with JWT

- Implement JWT validation for WebSocket connections
- Add refresh token rotation (15min access / 7d refresh)
- Include rate limiting per connection

Closes #2847
```

```
fix(security): prevent SQL injection in user repository

- Use parameterized queries instead of string interpolation
- Add input validation for user_id parameter
- Add integration test for injection attempt

Fixes CVE-2026-XXXX
```

```
refactor(user): extract UserRepository interface

- Create UserRepository interface in domain layer
- Implement PostgresUserRepository in adapters
- Update UserService to depend on interface
- Add contract tests

Part of ADR-047
```

## PR Workflow

### PR Lifecycle (with Mandatory Human Approval Gates)
```
1. Create feature branch
2. Agent execution (parallel, validated)
3. ⏸️ HUMAN GATE 1: Review all changes before commit
4. Commit changes (only after human approval)
5. ⏸️ HUMAN GATE 2: Review PR before creation
6. Create PR with template (only after human approval)
7. Push branch → CI runs validation gates
8. Automated validation gates run
9. Code review (2 approvals required)
10. Consensus check (if multi-skill)
11. ⏸️ HUMAN GATE 3: Approve production deployment
12. Auto-merge on consensus + approvals
13. Tag release
14. Deploy
```

### Mandatory Human Approval Gates

| Gate | When | What Human Reviews | Required |
|------|------|-------------------|----------|
| **Gate 1: Review Changes** | Before `git commit` | All agent outputs, validation results, file diffs | ✅ Required |
| **Gate 2: Review PR** | Before `gh pr create` | PR title, body, validation gates, consensus | ✅ Required |
| **Gate 3: Approve Deploy** | Before production deploy | Version, PR, consensus, deployment plan | ✅ Required |

**No commit, PR, or deployment proceeds without explicit human approval.**

### PR Template (Auto-generated)
```markdown
## 🤖 AI Engineering Company — Automated PR

### Request
Add real-time notifications with WebSocket and fallback

### DAG Execution
- **DAG ID**: feature-realtime-notifications-abc123
- **Mode**: Full Agentic Loop
- **Skills Used**: Product, Design, Staff Eng, Platform, Orchestration

### Validation Gates
- ✅ Security scan (SAST, secrets, deps)
- ✅ Performance baseline (p99 < 50ms)
- ✅ Architecture review (0 cycles, 0 boundary violations)
- ✅ Tests (coverage ≥80%, critical paths green)
- ✅ Accessibility audit (WCAG 2.1 AA)
- ✅ Terraform/K8s validation

### Consensus
- Security: ✅ Approve
- Architecture: ✅ Approve
- Performance: ✅ Approve
- Testing: ✅ Approve
- **Quorum: 92% — APPROVED**

### Deployment
- Strategy: Canary 5% → 25% → 100% over 2h
- Rollback: Single-click via feature flag
- Monitoring: SLO dashboards + burn rate alerts

### Checklist
- [ ] All validation gates passed
- [ ] Consensus reached (quorum ≥66%)
- [ ] Human approval for production deploy
- [ ] Feature flag created for rollout
- [ ] Runbook updated
- [ ] Changelog entry added
```

### Required Status Checks (Branch Protection)
| Check | Required | Description |
|-------|----------|-------------|
| `security-scan` | ✅ | SAST, secrets, dependency scan |
| `performance-baseline` | ✅ | p99 latency, throughput budgets |
| `architecture-review` | ✅ | No cycles, boundary violations |
| `test-suite` | ✅ | Unit, integration, contract tests |
| `accessibility-audit` | ✅ | WCAG 2.1 AA compliance |
| `infrastructure-validation` | ✅ | Terraform plan, K8s manifests |
| `consensus-check` | ✅ | Weighted voting quorum |

## Merge Strategy

### Squash Merge (Default)
- Combines all commits into single commit
- Clean history, easy revert
- PR title becomes commit message
- Branch deleted after merge

### When to Use Other Strategies
| Strategy | When |
|----------|------|
| `merge` | Preserve detailed commit history (rare) |
| `rebase` | Linear history without merge commit |
| `squash` | **Default** — clean, atomic features |

## Release Workflow

### Versioning (Semantic Versioning)
```
MAJOR.MINOR.PATCH

MAJOR: Breaking changes (API, schema, behavior)
MINOR: New features (backward compatible)
PATCH: Bug fixes (backward compatible)
```

### Release Process
```
1. Consensus approves release
2. Create release branch: release/v<version>
3. Generate changelog from merged PRs
4. Create annotated tag: v<major>.<minor>.<patch>
5. Push tag → triggers CI/CD release pipeline
6. Deploy to production (canary → progressive)
7. Post-deployment verification
8. Close release branch
```

### Tag Format
```
v<major>.<minor>.<patch>[-<prerelease>][+<build>]

Examples:
  v2.3.0
  v1.0.0-rc.1
  v2.3.0+build.123
```

### Changelog Format
```markdown
# v2.3.0 (2026-11-20)

## Features
- Add real-time notifications with WebSocket and fallback (#2847)
- Add dark mode support for dashboard (#2832)

## Fixes
- Prevent SQL injection in user service (#2851)
- Fix memory leak in notification service (#2849)

## Performance
- Reduce p99 latency from 85ms to 47ms (#2845)

## Security
- Rotate JWT signing keys (#2850)

## Breaking Changes
- None

## Contributors
- @ai-engineering-company (automated)
```

## Hotfix Workflow

For critical production fixes:

```
1. Create hotfix branch from main: hotfix/<slug>-<date>
2. Apply minimal fix
3. Run full validation gates
4. Create PR → expedited review (1 approval)
5. Merge to main with squash
6. Tag patch release: v<major>.<minor>.<patch+1>
7. Deploy immediately (expedited canary)
8. Backport to supported release branches if needed
```

## Rollback Procedure

### Feature Flag Rollback (Preferred)
```
1. Disable feature flag in LaunchDarkly/Unleash
2. Verify metrics recover
3. No code deploy needed
```

### Code Rollback (If flag insufficient)
```
1. git revert <merge-commit-sha>
2. Push revert → triggers CI/CD
3. Deploy revert
4. Verify recovery
```

### Full Rollback (Emergency)
```
1. git checkout <last-known-good-tag>
2. git push --force-with-lease origin main
3. Trigger emergency deploy
4. Post-incident review
```

## Git Configuration

### Required Git Config
```bash
# Commit signing
git config --global commit.gpgsign true
git config --global user.signingkey <key-id>

# Commit template
git config --global commit.template ~/.gitmessage.txt

# Autocorrect
git config --global help.autocorrect 10

# Push default
git config --global push.default simple
```

### Commit Template (~/.gitmessage.txt)
```
<type>(<scope>): <subject>

<body>

<footer>
# Type: feat, fix, refactor, perf, security, docs, test, chore, build, ci, revert
# Scope: auth, api, ui, db, infra, ci, docs
# Subject: imperative, lowercase, no period, max 50 chars
# Body: explain what and why, not how, wrap at 72 chars
# Footer: Closes #, Fixes #, Part of ADR-#, Breaking Change:
```

## CI/CD Integration

### GitHub Actions Workflow (Example)
```yaml
# .github/workflows/validate.yml
name: Validation Gates

on:
  pull_request:
    branches: [main]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: python -m pip install -r requirements.txt
      - run: python skills/staff-engineer/scripts/scan-security.py --path . --fail-on critical

  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python skills/staff-engineer/scripts/profile-performance.py --budget "latency:p99<50ms"

  architecture:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python skills/staff-engineer/scripts/analyze-architecture.py --path . --fail-on cycles,boundaries

  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make test  # or pytest, go test, etc.

  accessibility:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python skills/design-skill/scripts/audit-accessibility.py --path . --fail-on critical

  infrastructure:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: python skills/platform-engineer/scripts/validate-terraform.py --path ./infra --fail-on any

  consensus:
    runs-on: ubuntu-latest
    needs: [security, performance, architecture, tests, accessibility, infrastructure]
    steps:
      - run: python skills/agentic-orchestration/scripts/consensus.py --votes votes.json --rule production_deploy
```