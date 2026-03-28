# Security Policy

## Reporting Vulnerabilities

If you discover a security vulnerability in Velora TPRM, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, email: **security@archeon.dev** (or contact the maintainer directly)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge receipt within 48 hours and provide a timeline for resolution.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 2.x.x | Yes |
| < 2.0 | No |

## Security Features

Velora TPRM implements the following security controls:

- **Authentication**: JWT with bcrypt (cost factor 12), refresh token rotation
- **Authorization**: OPA (Open Policy Agent) for RBAC + ABAC + tenant isolation
- **Encryption at rest**: AES-256-GCM for PII fields, PostgreSQL TDE
- **Encryption in transit**: TLS 1.2+ required
- **Multi-tenancy**: PostgreSQL Row-Level Security (RLS) on every tenant-scoped table
- **Audit trail**: Immutable audit logging of all security-relevant actions
- **Input validation**: Pydantic v2 schemas on all API inputs
- **Rate limiting**: slowapi on all endpoints
- **Secret management**: No secrets in code; environment variable configuration only
- **Dependency scanning**: Automated vulnerability scanning in CI pipeline
