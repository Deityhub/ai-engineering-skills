# Security Playbook — Staff Engineer Reference

**Language-agnostic security practices.** Adapt tooling to detected language (see `language-guides/`).

---

## Threat Modeling (Do First)

### STRIDE Model
| Threat | Description | Mitigation |
|--------|-------------|------------|
| **S**poofing | Impersonating users/services | Strong auth, mutual TLS, signed requests |
| **T**ampering | Modifying data | Integrity checks, signatures, immutable logs |
| **R**epudiation | Denying actions | Audit logs, non-repudiation, digital signatures |
| **I**nformation Disclosure | Leaking secrets/data | Encryption, least privilege, data classification |
| **D**enial of Service | Overwhelming resources | Rate limiting, circuit breakers, autoscaling |
| **E**levation of Privilege | Gaining unauthorized access | RBAC/ABAC, principle of least privilege |

### Data Flow Diagrams
```
[Client] → [WAF] → [API Gateway] → [Auth Service] → [Business Logic] → [Database]
                ↓                    ↓                    ↓
            [Rate Limit]         [Token Validate]    [Encrypt/Decrypt]
```

**For each boundary**: Identify trust zones, data classification, encryption requirements.

---

## OWASP Top 10 (2023) — Mitigation Checklist

| # | Vulnerability | Primary Mitigation | Language-Agnostic Tools |
|---|---------------|-------------------|-------------------------|
| A01 | Broken Access Control | Deny-by-default, RBAC/ABAC, integration tests | OWASP ZAP, custom auth tests |
| A02 | Cryptographic Failures | TLS 1.3+, AEAD, Argon2id, key rotation | `scripts/scan-security.py --crypto` |
| A03 | Injection | Parameterized queries, allowlist validation, ORM | SAST (Semgrep, CodeQL), schema validation |
| A04 | Insecure Design | Threat modeling, secure patterns, design reviews | ADR for security decisions |
| A05 | Security Misconfiguration | Hardened defaults, config-as-code, drift detection | IaC scanners (Checkov, tfsec), kube-score |
| A06 | Vulnerable Components | Dependency scanning, SBOM, automated updates | `scripts/scan-security.py --deps`, Dependabot |
| A07 | Auth Failures | MFA, short-lived tokens, rate limiting, breach detection | Auth0/Keycloak/Cognito + custom rules |
| A08 | Software Integrity Failures | Signed builds, provenance, reproducible builds | SLSA, Sigstore, SBOM verification |
| A09 | Logging Failures | Structured logs, correlation IDs, alerting on anomalies | OpenTelemetry, SIEM integration |
| A10 | SSRF | Allowlist URLs, no user-controlled fetch, network policies | Egress controls, URL validation |

---

## Input Validation (Universal)

### Validation Layers
```
┌─────────────────────────────────────────────────────────────┐
│ 1. TRANSPORT: TLS 1.3, certificate validation, HSTS        │
├─────────────────────────────────────────────────────────────┤
│ 2. SCHEMA: JSON Schema / Protobuf / OpenAPI validation     │
├─────────────────────────────────────────────────────────────┤
│ 3. BUSINESS: Domain rules, allowlists, range checks        │
├─────────────────────────────────────────────────────────────┤
│ 4. OUTPUT: Encoding (HTML, SQL, JS, URL, CSS)              │
└─────────────────────────────────────────────────────────────┘
```

### Allowlist Patterns
| Input Type | Allowlist Strategy |
|------------|-------------------|
| Email | RFC 5322 regex + domain allowlist (if applicable) |
| UUID | `^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` |
| File upload | MIME type + extension + magic bytes + size limit |
| SQL | Parameterized queries ONLY (never string concat) |
| HTML | DOMPurify / sanitize-html / allowlist tags/attrs |
| Path | `path.resolve()` + allowlist base directory |
| Regex | User-supplied regex → RE2 (no backtracking) or timeout |

---

## Cryptography Standards

### Encryption
| Use Case | Algorithm | Key Management |
|----------|-----------|----------------|
| Data at rest | AES-256-GCM / ChaCha20-Poly1305 | Cloud KMS / Vault / Hardware HSM |
| Data in transit | TLS 1.3 (X25519, AES-GCM) | Automated cert rotation (Let's Encrypt / ACME) |
| Passwords | Argon2id (t=3, m=64MB, p=4) | Per-user salt, pepper in vault |
| Tokens | Ed25519 / RS256 (JWT) | Short expiry (≤15min), rotation |
| File encryption | Age / libsodium sealed boxes | Per-file keys, master key in KMS |

### Key Rotation Schedule
| Key Type | Rotation | Grace Period |
|----------|----------|--------------|
| TLS certificates | 90 days (auto) | 30 days |
| JWT signing keys | 90 days | 24 hours |
| Database encryption | 1 year | 30 days (re-encrypt) |
| API keys | 1 year | 7 days |
| Master keys | 2 years | 90 days (HSM ceremony) |

---

## Supply Chain Security

### Dependency Management
```bash
# Pin with hashes (example: npm)
npm install --package-lock-only --ignore-scripts
npm audit signatures

# SBOM generation
cyclonedx-bom -o sbom.xml
syft packages dir:. -o spdx-json=sbom.spdx.json

# License compliance
license-checker --onlyAllow "MIT;Apache-2.0;BSD-3-Clause" --failOn violation
```

### Update Policy
| Severity | SLA | Action |
|----------|-----|--------|
| Critical (CVSS ≥9) | 24 hours | Emergency patch, deploy immediately |
| High (CVSS 7-8.9) | 7 days | Patch in next sprint |
| Medium (CVSS 4-6.9) | 30 days | Schedule in backlog |
| Low (CVSS <4) | 90 days | Batch with other updates |

### Provenance Verification
- **SLSA Level 3+** for build pipeline
- **Sigstore** signatures on artifacts
- **Reproducible builds** verified in CI

---

## Secrets Management

### Detection Patterns (scan-security.py)
```regex
# Generic high-entropy strings
(?i)(api[_-]?key|secret|password|token|private[_-]?key)[\s]*[:=][\s]*['\"]?[a-zA-Z0-9+/=]{20,}

# Cloud provider keys
AWS: AKIA[0-9A-Z]{16}
GCP: ya29\.[0-9A-Za-z_-]+
Azure: [a-zA-Z0-9/+=]{88}
GitHub: gh[pousr]_[A-Za-z0-9_]{36,251}
```

### Remediation Workflow
1. **Revoke** immediately (automated via API)
2. **Rotate** in vault
3. **Audit** access logs for misuse
4. **Update** CI/CD with new secret
5. **Document** in incident log

---

## Secure Coding Patterns by Language

### TypeScript/JavaScript
```typescript
// ✅ Parameterized queries
const user = await db.query('SELECT * FROM users WHERE id = $1', [userId]);

// ✅ Schema validation at boundary
const schema = z.object({ email: z.string().email(), age: z.number().min(18) });
const input = schema.parse(req.body);

// ✅ Constant-time comparison
import { timingSafeEqual } from 'crypto';
timingSafeEqual(Buffer.from(token), Buffer.from(expected));

// ❌ Never: eval, Function constructor, innerHTML with user data
// ❌ Never: string concatenation in SQL
```

### Python
```python
# ✅ Parameterized queries
cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

# ✅ Pydantic validation
class UserInput(BaseModel):
    email: EmailStr
    age: conint(ge=18)

# ✅ Secrets from environment
SECRET_KEY = os.environ["SECRET_KEY"]  # Never hardcode

# ❌ Never: pickle.loads(user_data), eval(), exec()
# ❌ Never: f"SELECT * FROM users WHERE id = {user_id}"
```

### Go
```go
// ✅ Parameterized queries
row := db.QueryRow("SELECT * FROM users WHERE id = $1", userID)

// ✅ Constant-time compare
subtle.ConstantTimeCompare([]byte(token), []byte(expected)) == 1

// ✅ Context for timeouts/cancellation
ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)

// ❌ Never: fmt.Sprintf for SQL
// ❌ Never: template.Execute with untrusted data (use html/template)
```

### Rust
```rust
// ✅ Parameterized queries (sqlx)
let user = sqlx::query!("SELECT * FROM users WHERE id = $1", user_id)
    .fetch_one(&pool).await?;

// ✅ Constant-time compare (subtle crate)
use subtle::ConstantTimeEq;
token.ct_eq(&expected).unwrap_u8() == 1

// ✅ No unsafe unless absolutely necessary (audit if used)

// ❌ Never: string concatenation for SQL
```

---

## Security Testing Integration

### CI/CD Pipeline
```yaml
# .github/workflows/security.yml
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SAST
        uses: github/codeql-action/init@v2
      - name: Secrets scan
        run: python scripts/scan-security.py --secrets --fail-on critical
      - name: Dependency scan
        run: python scripts/scan-security.py --deps --fail-on high
      - name: License check
        run: python scripts/scan-security.py --license --fail-on violation
      - name: Crypto check
        run: python scripts/scan-security.py --crypto --fail-on major
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: detect-private-key
      - id: detect-aws-credentials
  - repo: local
    hooks:
      - id: security-scan
        entry: python scripts/scan-security.py --staged
        language: system
        types: [file]
```

---

## Incident Response (Security)

### Runbook Template
```markdown
# Security Incident: [Type]

## Detection
- Alert: [Source, time, severity]
- Indicators: [IOCs, logs, anomalies]

## Triage
- Severity: [Critical/High/Medium/Low]
- Affected systems: [List]
- Data exposed: [Classification, volume]

## Containment
- [ ] Revoke compromised credentials
- [ ] Block malicious IPs/domains
- [ ] Isolate affected systems
- [ ] Preserve evidence (logs, memory dumps)

## Eradication
- Root cause: [CWE, vector]
- Fix: [Patch, config change, architecture]
- Verification: [Tests, scans]

## Recovery
- Restore from clean backups
- Monitor for recurrence
- Post-incident review (blameless)
```

---

## Compliance Mapping

| Standard | Key Requirements | Automation |
|----------|------------------|------------|
| SOC 2 Type II | Access control, encryption, monitoring, incident response | Continuous compliance dashboards |
| GDPR | Data minimization, consent, right to deletion, DPIA | Data mapping, automated deletion |
| HIPAA | PHI encryption, audit logs, access controls, BAA | Encrypted DB, structured logging |
| PCI DSS | Network segmentation, tokenization, vulnerability scans | Network policies, tokenization service |
| ISO 27001 | Risk assessment, asset management, continual improvement | Risk register, automated evidence |