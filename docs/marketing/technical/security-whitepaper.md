# Velora TPRM -- Security Whitepaper

**Enterprise Security Architecture and Compliance Posture**
**Version 2.1 | March 2026**

---

## Executive Summary

Security is not a feature of Velora TPRM. It is the foundation. As a platform that manages sensitive third-party risk data -- vendor assessments, compliance evidence, financial risk models, and audit trails -- Velora must meet the same security bar it helps its customers enforce on their vendors.

This whitepaper documents Velora's security architecture, controls, and compliance posture for CISOs, security architects, and procurement teams conducting vendor due diligence on the platform itself.

---

## Table of Contents

1. [Data Encryption](#1-data-encryption)
2. [Multi-Tenant Isolation](#2-multi-tenant-isolation)
3. [Authentication](#3-authentication)
4. [Authorization](#4-authorization)
5. [AI Security](#5-ai-security)
6. [Audit Trail](#6-audit-trail)
7. [Network Security](#7-network-security)
8. [Application Security](#8-application-security)
9. [Infrastructure Security](#9-infrastructure-security)
10. [Incident Response](#10-incident-response)
11. [Compliance Roadmap](#11-compliance-roadmap)
12. [Secure SDLC](#12-secure-sdlc)

---

## 1. Data Encryption

### 1.1 Encryption at Rest

All persistent data is encrypted using **AES-256-GCM** (Galois/Counter Mode), providing both confidentiality and authenticated encryption that detects any tampering with ciphertext.

| Data Store | Encryption Method | Key Management |
|-----------|-------------------|---------------|
| PostgreSQL 16 | Transparent Data Encryption (TDE) + application-layer field encryption | KMS with HSM backing, automated rotation |
| MinIO Object Storage | Server-side encryption (SSE-S3) with per-tenant keys | KMS-backed key hierarchy |
| Redis Cache | Application-layer encryption before caching | Ephemeral keys, TTL-bound |
| Temporal Workflow State | AES-256-GCM via custom data converter | Tenant-scoped keys |
| Backup Storage | AES-256-GCM with separate backup key hierarchy | Offline key escrow, independent from primary |

### 1.2 Encryption in Transit

All network communication uses **TLS 1.3** with no fallback to older protocol versions.

- **External traffic**: TLS 1.3 terminated at Traefik API gateway with HSTS (long max-age), OCSP stapling, and forward secrecy via ECDHE
- **Internal service-to-service**: Mutual TLS (mTLS) via service mesh in production; no plaintext communication between any services
- **Database connections**: TLS-enforced (`sslmode=verify-full`) with certificate pinning
- **Redis connections**: TLS-encrypted with client certificate authentication

Permitted cipher suites (restricted to the strongest available):
- `TLS_AES_256_GCM_SHA384`
- `TLS_CHACHA20_POLY1305_SHA256`
- `TLS_AES_128_GCM_SHA256`

### 1.3 Field-Level Encryption

Sensitive PII fields receive an additional layer of application-level encryption beyond TDE. This ensures that even database administrators with file-system access cannot read sensitive data without the application-layer keys.

| Field Category | Examples | Encryption | Access Control |
|---------------|----------|------------|---------------|
| Personal Identifiers | SSN, Tax ID, Passport numbers | AES-256-GCM, per-tenant key | Role-restricted, every access audit-logged |
| Financial Data | Bank accounts, revenue figures, contract values | AES-256-GCM, per-tenant key | GRC Manager and above only |
| Authentication Secrets | API keys, tokens, passwords | Argon2id (passwords) / AES-256-GCM (tokens) | System-only, never displayed in UI |
| Contact Information | Email, phone, address | AES-256-GCM, per-tenant key | Vendor Manager and above |
| Assessment Responses | Sensitive vendor disclosures, security findings | AES-256-GCM, per-tenant key | Assigned analysts and above |

### 1.4 Key Management Architecture

```
+-------------------+
| HSM               |  Hardware Security Module
| (Master Key)      |  - FIPS 140-2 Level 3
+--------+----------+  - Key material never exported
         |
+--------v----------+
| Tenant KEK        |  Key Encryption Key (per tenant)
| (Key Encrypting   |  - Rotated every 90 days
|  Key)             |  - Used to wrap DEKs
+--------+----------+
         |
+--------v----------+
| Field DEK         |  Data Encryption Key (per field category)
| (Data Encrypting  |  - Rotated on access pattern change
|  Key)             |  - Envelope encryption model
+-------------------+
```

- **Envelope encryption**: DEK encrypts the field data; KEK wraps the DEK. Key rotation updates KEKs without re-encrypting all stored data
- **Separation of duties**: No single administrator can access both encrypted data and decryption keys simultaneously
- **Cryptographic erasure**: Tenant offboarding destroys the tenant KEK, rendering all tenant data permanently unrecoverable without touching individual records
- **Key access logging**: Every key operation (create, rotate, access, destroy) is logged in the immutable audit trail

---

## 2. Multi-Tenant Isolation

Velora serves multiple organizations from shared infrastructure while guaranteeing complete data isolation. Tenant isolation is enforced at every layer of the stack -- not just the application layer.

### 2.1 Database-Level Isolation (PostgreSQL RLS)

Every table in every service database enforces Row-Level Security policies:

```sql
-- Applied to every tenant-scoped table
ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
ALTER TABLE assessments FORCE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_policy ON assessments
    FOR ALL
    USING (tenant_id = current_setting('app.current_tenant')::UUID)
    WITH CHECK (tenant_id = current_setting('app.current_tenant')::UUID);
```

Key properties:

- **FORCE ROW LEVEL SECURITY**: Policies apply even to table owners, preventing accidental bypass
- **Session-level context**: `app.current_tenant` is set from the authenticated JWT at connection checkout, before any query executes. It cannot be modified by application queries
- **No superuser bypass**: Application database users do not have `BYPASSRLS` privilege. Migration users have explicit bypass only for schema operations
- **Schema-per-service**: Each microservice owns its own schema, limiting blast radius of any single vulnerability
- **Both USING and WITH CHECK**: RLS policies enforce isolation on both reads and writes

### 2.2 Application-Level Isolation

- **JWT tenant claim**: Every authenticated request carries a cryptographically signed `tenant_id` claim, validated at the gateway
- **Middleware enforcement**: Tenant context is injected into every database session automatically via connection pooler middleware -- developers cannot forget or bypass it
- **API response filtering**: Response serializers validate that all returned records belong to the requesting tenant before serialization
- **Background job isolation**: Async workers process tenant-scoped jobs with tenant context propagated through the Redis Streams message envelope
- **Cache isolation**: Redis keys are prefixed with `tenant:{id}:` preventing cross-tenant cache access

### 2.3 Infrastructure-Level Isolation

- **Network policies**: Kubernetes NetworkPolicy with deny-all default restricts inter-pod communication to declared dependencies only
- **Resource quotas**: Per-tenant resource limits prevent noisy-neighbor effects on shared infrastructure
- **Separate encryption keys**: Each tenant has its own KEK hierarchy; compromising one tenant's keys does not affect others
- **Isolated object storage**: MinIO bucket-per-tenant with IAM policies; no shared bucket access

### 2.4 Cross-Tenant Attack Surface Analysis

| Attack Vector | Mitigation |
|--------------|------------|
| SQL injection bypassing RLS | Parameterized queries only (SQLAlchemy ORM); no raw SQL paths exist in the codebase |
| JWT forgery | RS256 asymmetric signing with key rotation; short-lived tokens (15 min) |
| Session hijacking | Secure, HttpOnly, SameSite=Strict cookies; token binding to IP range (optional) |
| API parameter tampering | Tenant ID extracted server-side from JWT, never from request body or query params |
| Cache poisoning | Tenant-prefixed cache keys; TTL limits; no cache key derivation from user input |
| Log injection | Structured JSON logging; no string interpolation of user-controlled values |
| Insecure direct object reference | All resource access validated against tenant context before any data operation |

---

## 3. Authentication

### 3.1 Local Authentication

- **Password hashing**: bcrypt with cost factor 12 (~250ms per hash, resistant to GPU-accelerated brute force)
- **Password policy**: Minimum 12 characters; strength validation via zxcvbn (rejects weak passwords regardless of character class); breach database check via HaveIBeenPwned k-anonymity API
- **Password history**: Last 10 passwords stored (hashed) to prevent reuse
- **Account lockout**: Progressive delays after 3 failed attempts; full lockout after 10 with 30-minute cooldown; exponential backoff prevents timing attacks
- **Session management**: JWT access tokens (15-minute expiry) + opaque refresh tokens (7-day expiry, single-use, rotated on every use)
- **Session revocation**: Immediate revocation on password change, logout, or suspicious activity detection; concurrent session limits configurable per tenant

### 3.2 Multi-Factor Authentication

| Method | Standard | Security Level |
|--------|----------|---------------|
| **TOTP** | RFC 6238 | Compatible with Google Authenticator, Authy, 1Password |
| **WebAuthn/FIDO2** | W3C WebAuthn | Hardware security key support (YubiKey, Touch ID, Windows Hello) |
| **Recovery codes** | Custom | 10 single-use codes, bcrypt-hashed at rest, generated at enrollment |

MFA enforcement is configurable per tenant:
- Optional (user choice)
- Required for administrators only
- Required for all users (recommended for regulated industries)

### 3.3 Enterprise SSO

Velora supports enterprise identity federation through industry-standard protocols:

| Protocol | Standard | Capabilities |
|----------|----------|-------------|
| **SAML 2.0** | OASIS | SP-initiated and IdP-initiated SSO, Single Logout (SLO), encrypted assertions, signed requests |
| **OIDC** | OpenID Foundation | Authorization Code + PKCE flow, discovery endpoint, dynamic client registration |

Tested and documented Identity Providers:

- Okta
- Microsoft Entra ID (Azure AD)
- Google Workspace
- OneLogin
- PingIdentity
- Auth0
- JumpCloud
- Any standards-compliant SAML 2.0 or OIDC provider

### 3.4 Service-to-Service Authentication

- **mTLS in production**: Services authenticate via X.509 certificates managed by the service mesh
- **Service tokens**: Short-lived, scope-restricted JWTs for internal API calls with per-service credential sets
- **No shared secrets**: Each service has independently generated and rotated credentials

---

## 4. Authorization

### 4.1 Role-Based Access Control (RBAC)

Velora defines 8 roles with graduated permission sets following the principle of least privilege:

| Role | Scope | Key Permissions |
|------|-------|----------------|
| **Super Admin** | Platform | Tenant provisioning, global configuration, platform health |
| **Tenant Admin** | Tenant | User management, tenant configuration, all tenant operations |
| **GRC Manager** | Tenant | Full risk/compliance operations, vendor approvals, reporting |
| **Risk Analyst** | Tenant | Assessment creation/execution, risk scoring, evidence review |
| **Compliance Officer** | Tenant | Framework management, control mapping, gap analysis |
| **Vendor Manager** | Tenant | Vendor lifecycle management, tiering, relationship tracking |
| **Auditor** | Tenant | Read-only access to all tenant data, report export |
| **Vendor Contact** | Portal | Self-service assessment response and evidence upload (own vendor only) |

### 4.2 Attribute-Based Access Control (ABAC)

Beyond static roles, Velora evaluates dynamic attributes for fine-grained access decisions:

```rego
# Example: Risk Analysts can only edit assessments assigned to them
# and only when the assessment is in an editable state
allow {
    input.action == "assessment.update"
    input.user.role == "risk_analyst"
    input.resource.assigned_to == input.user.id
    input.resource.status in ["in_progress", "pending_review"]
    input.user.mfa_verified == true
}
```

Evaluated attributes include:

| Category | Attributes |
|----------|-----------|
| **User** | Role, department, clearance level, MFA status, IP address |
| **Resource** | Owner, classification level, status, data sensitivity, creation date |
| **Context** | Time of day, source IP, device trust level, session age |
| **Tenant** | License tier, feature flags, policy overrides, MFA requirements |

### 4.3 Open Policy Agent (OPA)

All complex authorization decisions are delegated to OPA, running as a sidecar to the API gateway:

- Policies written in Rego, stored as code in version control, with automated test suites
- Policy changes require peer review and approval before deployment
- Every policy evaluation is logged for audit and forensic analysis
- Evaluation latency < 2ms (P99) via local OPA sidecar with pre-compiled bundle caching
- OPA decision logs are exported to the immutable audit trail

```
Request -> Traefik Gateway -> JWT Validation -> OPA Policy Evaluation -> Service
                                                        |
                                                        v
                                                  Allow / Deny
                                              (logged to audit trail)
```

---

## 5. AI Security

Velora's integration with Anthropic Claude introduces a unique attack surface that requires dedicated security controls. This section details the threat model and mitigations.

### 5.1 Threat Model

| Threat | Risk Level | Mitigation |
|--------|-----------|------------|
| Prompt injection | High | Multi-layer defense: input sanitization, instruction anchoring, output validation, scope limitation |
| Data exfiltration via LLM | High | Tenant-scoped prompts, PII masking, zero-data-retention API agreement |
| Model manipulation | Medium | Confidence scoring, human review loop, source citation requirement |
| Denial of service | Medium | Per-tenant rate limiting, cost tracking, circuit breakers |
| Output hallucination | Medium | Structured output validation, confidence thresholds, mandatory human review for critical decisions |
| Cross-tenant context leakage | Critical | Stateless invocations, no conversation history, tenant-isolated prompt construction |

### 5.2 Prompt Injection Protection

Velora implements defense-in-depth against prompt injection across four layers:

1. **Input sanitization**: All user-supplied and vendor-supplied data is sanitized before inclusion in LLM prompts. Known injection patterns (role-playing prompts, instruction overrides, delimiter attacks) are detected and neutralized via regex and semantic classifiers

2. **Instruction anchoring**: System prompts use XML-delimited data sections with explicit instructions to treat all content within data delimiters as untrusted input. The model is instructed to never follow instructions found in data sections

3. **Output validation**: LLM outputs are validated against expected Pydantic schemas. Responses that deviate from the expected structure (containing unexpected instructions, format anomalies, or out-of-scope content) are rejected and flagged for security review

4. **Scope limitation**: The AI Service has read-only access to vendor data and can only generate assessment responses. It has no ability to modify data, execute actions, access external systems, or call other services. Every AI output passes through the assessment workflow before affecting any system state

### 5.3 Data Isolation in AI Processing

- **Tenant-scoped prompts**: Each LLM call contains data from exactly one tenant. Cross-tenant data never appears in the same prompt context. This is enforced at the AI Engine service level
- **Stateless invocations**: No conversation history is maintained between LLM calls. Each invocation is independent, preventing information leakage across sessions
- **PII minimization**: Sensitive fields (SSN, financial data, personal identifiers) are masked before LLM processing where full content is not required for the task
- **Zero-data-retention**: Anthropic API configured with zero-data-retention agreement. Customer data is never stored by Anthropic and is never used for model training
- **Token-level cost tracking**: Per-tenant token consumption is tracked and enforced to prevent abuse

### 5.4 Confidence Scoring as a Security Control

Every AI output includes a confidence score that serves as both a quality and security mechanism:

| Confidence Level | Threshold | Action | Security Rationale |
|-----------------|-----------|--------|-------------------|
| High | >= 0.90 | Auto-accepted with audit log entry | Multiple corroborating sources reduce manipulation risk |
| Medium | 0.70 - 0.89 | Queued for human review with AI recommendation | Partial support requires human verification |
| Low | < 0.70 | Flagged for manual completion; AI suggestion hidden | Low corroboration may indicate manipulated input data |

An attacker who manipulates vendor data to influence AI outputs will likely produce low-confidence responses -- because the manipulated data will not corroborate with legitimate historical sources -- triggering human review rather than auto-acceptance.

### 5.5 AI Audit Trail

Every AI interaction is recorded in the immutable audit trail:

- Input prompt hash (with PII masking notation)
- Model version and inference parameters
- Raw output and parsed structured result
- Confidence score with per-factor breakdown
- Token consumption (input + output)
- Latency measurement
- Human review decision and justification (if applicable)
- Override record (if human changed AI output)

---

## 6. Audit Trail

### 6.1 Architecture

The audit trail is a standalone service (:8100) that receives events from all services via Redis Streams. It is architecturally separated from operational databases to prevent tampering by any single service.

### 6.2 Immutability Guarantees

```
+--------+    +--------+    +--------+    +--------+
| Event  |--->| Event  |--->| Event  |--->| Event  |
| N      |    | N+1    |    | N+2    |    | N+3    |
| hash:  |    | hash:  |    | hash:  |    | hash:  |
| abc123 |    | def456 |    | ghi789 |    | jkl012 |
|prev:   |    |prev:   |    |prev:   |    |prev:   |
| 000000 |    | abc123 |    | def456 |    | ghi789 |
+--------+    +--------+    +--------+    +--------+
```

- **Append-only storage**: The audit database user has INSERT privileges only. No UPDATE, DELETE, or TRUNCATE permissions
- **SHA-256 hash chain**: Each event includes a hash of the previous event, creating a tamper-evident, blockchain-like chain
- **Hourly verification**: Background job validates hash chain integrity every hour; any chain break triggers immediate security alert
- **Separate credentials**: Audit service database credentials are distinct from all other services and cannot be used to modify audit data

### 6.3 Retention and Partitioning

| Policy | Configuration |
|--------|--------------|
| Retention period | 7 years (configurable per tenant, minimum 7 years for regulated) |
| Partitioning | Monthly table partitions for query performance |
| Hot storage | Last 12 months (NVMe SSD, sub-100ms queries) |
| Warm storage | 12-36 months (standard SSD) |
| Cold storage | 36-84 months (object storage, compressed, Parquet format) |
| Archival | Parquet with embedded SHA-256 checksums |

### 6.4 Audit Event Schema

Every audit event captures the full context of who did what, when, where, and why:

```json
{
  "event_id": "uuid-v7",
  "tenant_id": "uuid",
  "actor_id": "uuid",
  "actor_type": "user | system | ai | service",
  "action": "vendor.created | assessment.submitted | evidence.uploaded | ...",
  "resource_type": "vendor | assessment | evidence | user | config",
  "resource_id": "uuid",
  "changes": {
    "field_name": { "old": "previous_value", "new": "new_value" }
  },
  "metadata": {
    "ip_address": "x.x.x.x",
    "user_agent": "...",
    "session_id": "uuid",
    "mfa_verified": true,
    "request_id": "uuid",
    "service_name": "assessment-engine"
  },
  "timestamp": "2026-03-29T14:30:00.000000Z",
  "hash": "sha256:...",
  "prev_hash": "sha256:..."
}
```

---

## 7. Network Security

### 7.1 Perimeter Defense

- **Traefik API Gateway**: Single ingress point with TLS 1.3 termination, request validation, and centralized access logging
- **Web Application Firewall**: OWASP Core Rule Set (CRS) blocking SQL injection, XSS, SSRF, path traversal, and protocol attacks
- **Rate limiting**: Configurable per-tenant, per-endpoint, per-user; prevents brute force, credential stuffing, and API abuse
- **DDoS protection**: Connection throttling, SYN flood protection, request rate caps
- **IP allowlisting**: Optional per-tenant IP restriction for API and portal access
- **Geographic restrictions**: Optional geo-fencing for data residency compliance

### 7.2 Internal Network

- **Zero-trust networking**: All internal communication is authenticated (mTLS) and encrypted; no implicit trust based on network location
- **Network policies**: Kubernetes NetworkPolicy with deny-all default; explicit allow rules per service dependency graph
- **Service mesh**: Automatic mTLS between all pods, traffic encryption, observability, and policy enforcement
- **DNS security**: Internal-only DNS resolution; application pods cannot resolve external hostnames except through explicit egress rules
- **Egress control**: Strict allowlist for external API calls (Anthropic API, identity provider endpoints, notification providers, threat intelligence feeds)

### 7.3 Port Exposure

Only ports 443 (HTTPS) and 80 (redirect to 443) are exposed externally. All service ports (3000, 8001-8130) are internal only, unreachable from outside the cluster.

---

## 8. Application Security

### 8.1 Input Validation

- All API inputs validated through Pydantic v2 models with strict type enforcement and custom validators
- Request size limits: 10 MB default, configurable up to 100 MB for evidence uploads
- File upload validation: magic byte verification, extension allowlisting, antivirus scanning before storage
- No XML parsing anywhere in the stack (XXE prevention by elimination)
- SQL injection prevention: All database access through SQLAlchemy ORM with parameterized queries; no raw SQL execution paths

### 8.2 Output Security

- JSON-only API responses with `Content-Type: application/json` enforcement
- Security headers on all responses:
  - `Content-Security-Policy` (strict, no inline scripts)
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Referrer-Policy: strict-origin-when-cross-origin`
  - `Permissions-Policy` (restrictive defaults)
- No sensitive data in error messages; generic error codes for clients, detailed errors in server-side structured logs only
- Stack traces never exposed to clients in any environment

### 8.3 Dependency Security

- Automated dependency scanning in CI/CD pipeline (Trivy for container images, safety for Python packages)
- Zero tolerance for critical CVEs in production dependencies
- Lock files pinned to exact versions: Poetry (`poetry.lock`) for Python, pnpm (`pnpm-lock.yaml`) for Node.js
- SBOM (Software Bill of Materials) generated for every release
- Private registry with vetted dependencies for production builds

### 8.4 Secrets Management

- No secrets in code, environment variables, configuration files, or container images
- All secrets sourced from Kubernetes Secrets (encrypted at rest via etcd encryption) or external vault (HashiCorp Vault compatible)
- API keys and service tokens rotated on 90-day schedule
- Secret access is logged and auditable
- Pre-commit hooks (Gitleaks) prevent accidental secret commits

### 8.5 OWASP Top 10 Coverage

| OWASP Risk | Velora Mitigation |
|------------|-------------------|
| A01: Broken Access Control | RLS + RBAC + ABAC + OPA; per-request authorization at gateway |
| A02: Cryptographic Failures | AES-256-GCM at rest, TLS 1.3 in transit, HSM-backed KMS, field-level encryption |
| A03: Injection | Parameterized queries via ORM, input validation via Pydantic, no raw SQL |
| A04: Insecure Design | Threat modeling during design phase, security architecture review |
| A05: Security Misconfiguration | Infrastructure-as-code, hardened base images, CIS benchmarks, automated scanning |
| A06: Vulnerable Components | SCA scanning, automated dependency updates, SBOM generation |
| A07: Auth Failures | bcrypt, MFA (TOTP + FIDO2), session management, rate limiting, account lockout |
| A08: Data Integrity Failures | Signed container images, immutable audit log, cryptographic hash chains |
| A09: Logging Failures | Structured JSON logging, immutable audit trail, SIEM integration |
| A10: SSRF | Outbound request allowlisting, URL validation, no user-controlled URLs in server requests |

---

## 9. Infrastructure Security

### 9.1 Container Security

- **Minimal base images**: `python:3.12-slim` and `node:20-alpine` for minimal attack surface
- **Non-root execution**: All containers run as non-root users with read-only root filesystem
- **Security contexts**: No privilege escalation (`allowPrivilegeEscalation: false`), dropped capabilities, seccomp profiles enforced
- **Image scanning**: Every build scanned with Trivy; images with critical or high vulnerabilities are blocked from deployment
- **Image signing**: Container images signed with cosign and verified at deployment via admission controller
- **Runtime monitoring**: Falco-compatible for runtime anomaly detection

### 9.2 Kubernetes Hardening

- RBAC for cluster API access with least-privilege service accounts per service
- Pod Security Standards: Restricted profile enforced via admission controller
- Resource limits and quotas prevent resource exhaustion attacks
- Automated node patching and rotation on configurable schedule
- etcd encryption at rest for all Kubernetes secrets
- Admission controllers enforce image source, resource limits, and security context requirements

### 9.3 Backup and Disaster Recovery

| Component | RPO | RTO | Method |
|-----------|-----|-----|--------|
| PostgreSQL | 1 hour | 4 hours | Continuous WAL archiving + daily base backups |
| MinIO | 4 hours | 8 hours | Cross-region replication + versioning |
| Temporal | 1 hour | 2 hours | Database backup (PostgreSQL backend) |
| Configuration | Real-time | 1 hour | Git-based, infrastructure-as-code |
| Audit Trail | 0 (synchronous) | 4 hours | Replicated + archived to object storage |

All backups are encrypted with separate backup encryption keys and stored in a different region from primary. Backup restoration is tested quarterly.

---

## 10. Incident Response

### 10.1 Detection

- Real-time alerting on anomalous authentication patterns (credential stuffing, impossible travel, MFA bypass attempts)
- Automated detection of privilege escalation attempts and unauthorized data access patterns
- AI-powered anomaly detection on API usage patterns (unusual query volumes, off-hours access, bulk export attempts)
- Integration with customer SIEM for correlated alerting across the customer's security ecosystem

### 10.2 Response Process

| Phase | SLA | Actions |
|-------|-----|---------|
| **Identification** | < 15 min | Automated triage classifies severity (P1-P4), pages on-call team |
| **Containment** | < 1 hour | Tenant isolation, credential rotation, access revocation, evidence preservation |
| **Eradication** | < 4 hours | Root cause identification, vulnerability remediation, patch deployment |
| **Recovery** | < 8 hours | Service restoration, data integrity verification, monitoring enhancement |
| **Post-mortem** | < 48 hours | Documented RCA, preventive actions, customer communication, control improvements |

### 10.3 Customer Communication

- Affected customers notified within **24 hours** of confirmed data breach (per GDPR Article 33 and contractual obligations)
- Notification includes: nature of incident, data affected, actions taken, recommended customer actions, timeline
- Status page updates for service availability incidents
- Detailed post-incident reports available upon request within 30 days
- Dedicated incident communication channel for enterprise customers

---

## 11. Compliance Roadmap

### 11.1 Current Status and Targets

| Standard | Status | Target Date | Notes |
|----------|--------|-------------|-------|
| SOC 2 Type I | In progress | Q3 2026 | Auditor engaged, evidence collection underway |
| SOC 2 Type II | Planned | Q1 2027 | 6-month observation period begins after Type I |
| ISO 27001 | Gap analysis complete (94% coverage) | Q4 2026 | Remaining items: physical security controls, formal ISMS documentation |
| GDPR | Compliant by design | Current | DPA available, DPIA completed for AI processing |
| HIPAA | Technical safeguards implemented | Q3 2026 | BAA available upon request |

### 11.2 SOC 2 Trust Services Criteria Coverage

| Criteria | Key Controls |
|----------|-------------|
| **Security (CC1-CC9)** | MFA, RLS, OPA, AES-256-GCM, WAF, immutable audit trail, vulnerability management, access reviews |
| **Availability** | HA database (3 replicas), auto-scaling, health checks, disaster recovery tested quarterly |
| **Processing Integrity** | Hash-chain audit trail, Pydantic input validation, automated testing (80%+ coverage), data reconciliation |
| **Confidentiality** | AES-256-GCM with field-level encryption, RBAC + ABAC access controls, data classification enforcement |
| **Privacy** | Consent management, data minimization, configurable retention policies, right to erasure, DPIA |

### 11.3 ISO 27001:2022 Annex A Alignment

Velora's security controls map to ISO 27001:2022 Annex A with 94% coverage confirmed via gap analysis. The remaining controls (primarily physical security and formal ISMS process documentation) are in progress for certification readiness by Q4 2026.

### 11.4 Framework Alignment Summary

Velora manages 8 compliance frameworks for its customers. The platform itself is built to meet the same standards:

| Framework | Relevance to Velora |
|-----------|-------------------|
| **SOC 2** | Primary certification target; all Trust Services Criteria addressed |
| **ISO 27001** | ISMS-ready controls; certification planned |
| **NIST CSF** | Five-function coverage: Identify, Protect, Detect, Respond, Recover |
| **HIPAA** | Technical safeguards for any ePHI processed on behalf of healthcare customers |
| **PCI DSS** | Applicable data protection controls for payment-adjacent data |
| **GDPR** | Privacy by design; data subject rights; DPA and DPIA available |
| **DORA** | ICT risk management controls applicable to financial sector customers |
| **NIS2** | Essential entity security requirements for EU-based deployments |

---

## 12. Secure SDLC

### 12.1 Development Phase

- **Threat modeling**: STRIDE analysis for every new feature and service before development begins; threat models maintained and updated
- **Secure coding standards**: OWASP guidelines enforced through automated linting, code review checklists, and CI/CD gates
- **Peer review**: Every code change requires at least one reviewer; security-sensitive changes (auth, crypto, data access) require two reviewers including a security-aware engineer
- **Pre-commit hooks**: Gitleaks (secret scanning), Ruff (Python linting), ESLint (TypeScript linting), type checking (mypy, tsc)

### 12.2 Build Phase

- **SAST**: Semgrep and Bandit run on every pull request with blocking rules for high-severity findings
- **SCA**: Trivy dependency scanning with CVE blocking policy; license compliance checking
- **Container scanning**: Image vulnerability scanning before registry push; critical/high CVEs block deployment
- **Unit testing**: Minimum 80% code coverage enforced in CI; security-specific test cases for auth, authorization, data isolation, and encryption

### 12.3 Test Phase

- **DAST**: OWASP ZAP automated scanning against staging environment on every release candidate
- **API security testing**: Fuzzing, authentication bypass testing, IDOR validation, rate limit verification
- **Penetration testing**: Annual third-party penetration test by certified firm (report available under NDA)
- **Load testing**: Performance and resilience testing under adversarial conditions (spike load, resource exhaustion)
- **Chaos engineering**: Periodic fault injection testing (network partitions, service crashes, database failover)

### 12.4 Deploy Phase

- **Infrastructure as Code**: All deployments reproducible from version-controlled manifests (Kubernetes YAML, Helm charts)
- **Immutable deployments**: No in-place modifications to running containers; every change is a new deployment
- **Blue-green deployment**: Zero-downtime releases with instant rollback capability
- **Post-deploy verification**: Automated smoke tests, health checks, and security scan after every deployment
- **Signed artifacts**: Container images and Helm charts are signed and verified at deployment via admission controller

### 12.5 Operate Phase

- **Continuous monitoring**: 24/7 automated alerting on security-relevant events with PagerDuty integration
- **Vulnerability management**: CVEs triaged within 24 hours; critical patches deployed within 72 hours
- **Access reviews**: Quarterly review of all user and service account permissions with documented sign-off
- **Security training**: Development team undergoes annual secure coding training with certification

---

## Appendix A: Shared Responsibility Model

| Control Area | Velora Responsibility | Customer Responsibility |
|-------------|----------------------|------------------------|
| Application security | Full ownership | N/A |
| Data encryption (at rest and in transit) | Full ownership | N/A |
| Platform availability | Full ownership (SLA-backed) | N/A |
| User provisioning | Platform capability provided | Execution, review, and offboarding |
| MFA enforcement | Platform capability provided | Policy decision and rollout |
| SSO configuration | SAML 2.0/OIDC endpoints provided | IdP configuration and testing |
| Password policy | Secure defaults provided | Custom policy settings if overriding |
| IP allowlisting | Platform capability provided | Configuration per tenant needs |
| Data classification | Framework and tooling provided | Classification decisions for their data |
| Compliance framework selection | 8 frameworks built-in | Selection and gap remediation ownership |
| Incident response | Platform/infra incidents | Customer-side response and remediation |
| Data retention configuration | Configurable policies provided | Policy decisions per regulatory needs |

---

## Appendix B: Data Flow Diagram

```
                    +------------------+
                    | External Users   |
                    | (Browser/API)    |
                    +--------+---------+
                             |
                        TLS 1.3
                             |
                    +--------v---------+
                    | Traefik Gateway   |
                    | (WAF, rate limit, |
                    |  JWT validation)  |
                    +--------+---------+
                             |
                        mTLS |
                             |
              +--------------+--------------+
              |              |              |
        +-----v----+  +-----v----+  +------v-----+
        | FastAPI   |  | FastAPI  |  | FastAPI    |
        | Services  |  | AI/ML   |  | Audit      |
        | (:8001-   |  | Engine  |  | Trail      |
        |  :8130)   |  | (:8060) |  | (:8100)    |
        +-----+----+  +-----+---+  +------+-----+
              |              |              |
              |         TLS  |              |
              |              v              |
              |     +--------+-------+      |
              |     | Anthropic API  |      |
              |     | (zero-data-    |      |
              |     |  retention)    |      |
              |     +----------------+      |
              |                             |
        +-----v-----------------------------v----+
        |         PostgreSQL 16 + RLS            |
        |    (TDE + field-level encryption)       |
        +----+----------------------------+------+
             |                            |
       +-----v------+            +-------v------+
       | MinIO       |            | Redis        |
       | (SSE, per-  |            | (encrypted,  |
       |  tenant     |            |  tenant-     |
       |  buckets)   |            |  prefixed)   |
       +-------------+            +--------------+
```

---

## Appendix C: Security Contact

For security concerns, vulnerability reports, or to request compliance documentation:

- **Security Team**: security@velora.io
- **Responsible Disclosure**: https://velora.io/.well-known/security.txt
- **Compliance Documentation**: compliance@velora.io
- **PGP Key**: Available at https://velora.io/pgp
- **Penetration Test Report**: Available under NDA upon request

---

*This whitepaper is updated quarterly. Last review: Q1 2026.*

*Velora TPRM -- Security is the architecture, not a layer on top.*
