# Velora TPRM — Multi-Tenant Architecture

**Version**: 1.0.0
**Author**: Tantron (CTO, Pantheon)
**Date**: 2026-03-29
**Status**: Active

---

## Overview

Velora TPRM implements a flexible multi-tenant architecture that supports three deployment models based on customer requirements. The default model (Shared Schema) serves most customers; Premium and Enterprise tiers offer stronger isolation guarantees.

## Tenant Isolation Tiers

| Tier | Model | Isolation Level | Use Case |
|------|-------|----------------|----------|
| **Standard** | Shared database, schema-per-service, RLS | Logical | Most customers (Professional/Business) |
| **Premium** | Schema-per-tenant within shared database | Schema | Regulated industries (Business tier) |
| **Enterprise** | Database-per-tenant (dedicated instance) | Physical | Large enterprises, data residency requirements |

## Architecture Components

### 1. Tenant Identification

Every request carries a `tenant_id` derived from the authentication context:

```
Client Login Flow:
1. User enters Client ID (e.g., "acme-corp") on login page
2. System resolves Client ID → tenant_id (UUID)
3. JWT token includes tenant_id in claims
4. Every API request carries tenant context
5. PostgreSQL RLS enforces row-level isolation
6. OPA policies validate tenant access
```

**JWT Token Structure:**
```json
{
  "sub": "user-uuid",
  "tenant_id": "tenant-uuid",
  "roles": ["risk_analyst"],
  "permissions": ["vendor:read", "assessment:write"],
  "exp": 1711728000,
  "iat": 1711726200
}
```

### 2. Database Isolation (Standard Tier)

**Row-Level Security (RLS):**

Every table that holds tenant data inherits from `TenantBase`:

```sql
-- All tenant tables include:
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id),
    name VARCHAR(255) NOT NULL,
    -- ... other columns
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS Policy (applied to every tenant table):
ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON vendors
    USING (tenant_id = current_setting('app.tenant_id')::UUID);

-- Before each request, the service sets:
SET app.tenant_id = '<tenant-uuid>';
```

**Schema-Per-Service:**

Each microservice owns its own PostgreSQL schema:

```
auth_svc       → users, roles, permissions, refresh_tokens, tenants
vendor_svc     → vendors, vendor_contacts, vendor_enrichment
assessment_svc → assessments, questionnaires, questions, responses
framework_svc  → frameworks, controls, clauses
scoring_svc    → risk_scores, scoring_models
evidence_svc   → evidence, evidence_control_mappings
monitoring_svc → signals, alerts, alert_rules
finding_svc    → findings, remediation_tracking
comms_svc      → notifications, notification_templates
reporting_svc  → dashboard_materialized_views
admin_svc      → audit_logs, api_keys, tenant_settings
ai_svc         → ai_usage_stats, autofill_cache
```

No cross-schema joins. Services communicate via REST API or Redis Streams.

### 3. Premium Tier (Schema-Per-Tenant)

For customers requiring stronger isolation:

```
Database: velora_production
├── shared        → framework data, templates (read-only for tenants)
├── tenant_abc123 → all tables for Acme Corp
├── tenant_def456 → all tables for Widget Inc
└── tenant_ghi789 → all tables for Mega Corp

Each tenant schema is a complete copy of all service schemas.
Service determines schema from JWT tenant_id at connection time.
```

**Connection Routing:**
```python
# Service middleware sets schema search path per request
async def set_tenant_schema(request, db_session):
    tenant_id = request.state.tenant_id
    tenant = await get_tenant_config(tenant_id)
    if tenant.isolation_tier == "premium":
        await db_session.execute(f"SET search_path TO tenant_{tenant_id}")
    else:
        await db_session.execute(f"SET app.tenant_id = '{tenant_id}'")
```

### 4. Enterprise Tier (Database-Per-Tenant)

For the largest customers with data residency requirements:

```
Separate PostgreSQL instances per tenant:
├── velora-acme.us-east-1.rds.amazonaws.com     → Acme Corp (US)
├── velora-widget.eu-west-1.rds.amazonaws.com   → Widget Inc (EU)
└── velora-mega.ap-southeast-1.rds.amazonaws.com → Mega Corp (APAC)

Connection string resolved at runtime from tenant registry.
```

**Tenant Registry (central):**
```json
{
  "tenant_id": "ghi789",
  "name": "Mega Corp",
  "isolation_tier": "enterprise",
  "region": "ap-southeast-1",
  "database_url": "postgresql://...",
  "data_residency": "APAC",
  "encryption_key_arn": "arn:aws:kms:ap-southeast-1:..."
}
```

### 5. OPA Authorization Layer

Every request passes through OPA for authorization:

```rego
# policies/gateway/tenant_isolation.rego
package velora.gateway

default allow = false

# Allow if token is valid and tenant context is set
allow {
    input.token_valid == true
    input.tenant_id != ""
}

# Public endpoints (no auth required)
allow { startswith(input.path, "/health") }
allow { startswith(input.path, "/auth/login") }
allow { startswith(input.path, "/auth/sso") }

# Vendor portal (magic link auth)
allow {
    startswith(input.path, "/portal/")
    input.portal_token_valid == true
}
```

### 6. Redis Streams (Event Bus)

Inter-service communication uses Redis Streams with tenant context:

```json
{
  "event_type": "assessment.completed",
  "tenant_id": "abc123",
  "payload": {
    "assessment_id": "assess-uuid",
    "vendor_id": "vendor-uuid",
    "score": 72
  },
  "timestamp": "2026-03-29T10:00:00Z"
}
```

Consumer groups ensure at-least-once delivery. Events are tenant-scoped — a consumer only processes events for accessible tenants.

## Client ID Configuration

### For Customers

1. **During Onboarding**: Velora assigns a unique Client ID (e.g., `acme-corp`)
2. **Login Page**: Users enter Client ID first, then authenticate
3. **Custom Domains**: Enterprise customers can use `tprm.acme.com` (CNAME to Velora)
4. **SSO Auto-Resolution**: If SSO is configured, the Client ID can be auto-detected from the IdP domain

### For Self-Hosted Deployments

Single-tenant mode is available for customers who want to self-host:

```yaml
# docker-compose.override.yml
services:
  auth-service:
    environment:
      SINGLE_TENANT_MODE: "true"
      DEFAULT_TENANT_ID: "self-hosted"
```

In single-tenant mode, the Client ID step is skipped on login.

## Data Residency

| Region | Location | Supported Tiers |
|--------|----------|----------------|
| US | us-east-1 (Virginia) | All |
| EU | eu-west-1 (Ireland) | Premium, Enterprise |
| APAC | ap-southeast-1 (Singapore) | Enterprise only |

Data residency is configured per-tenant in the tenant registry. Enterprise tier customers can choose their deployment region during onboarding.

## Security Controls

| Control | Implementation |
|---------|---------------|
| Tenant isolation | PostgreSQL RLS + OPA policies |
| Data encryption (at-rest) | AES-256-GCM per-tenant key |
| Data encryption (in-transit) | TLS 1.3 |
| PII encryption | Field-level AES-256-GCM (emails, phones) |
| Access control | RBAC (8 roles) + ABAC (OPA) |
| Audit logging | Immutable, tenant-scoped, 7-year retention |
| Key management | AWS KMS (per-tenant keys for Enterprise) |
| Network isolation | VPC per region, private subnets |

## API Endpoints

### Tenant Management (Admin only)

```
POST   /admin/tenants              Create tenant
GET    /admin/tenants              List tenants
GET    /admin/tenants/:id          Get tenant
PATCH  /admin/tenants/:id          Update tenant
DELETE /admin/tenants/:id          Deactivate tenant

POST   /admin/tenants/:id/rotate-key   Rotate encryption key
GET    /admin/tenants/:id/usage         Usage metrics
```

### Tenant Resolution

```
GET    /auth/resolve-tenant?client_id=acme-corp
Response: { "tenant_id": "uuid", "name": "Acme Corp", "sso_enabled": true, "sso_providers": ["okta"] }
```

## Deployment Architecture

```
                    ┌─────────────────┐
                    │   Traefik LB    │
                    │  (API Gateway)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──┐  ┌───────▼───┐  ┌──────▼──────┐
     │ BFF       │  │ Auth      │  │ Services    │
     │ Service   │  │ Service   │  │ (12 more)   │
     └────────┬──┘  └───────┬───┘  └──────┬──────┘
              │              │              │
              └──────────────┼──────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
     ┌────────▼──┐  ┌───────▼───┐  ┌──────▼──────┐
     │ PostgreSQL │  │ Redis     │  │ OPA         │
     │ (RLS)     │  │ (Streams) │  │ (Policies)  │
     └───────────┘  └───────────┘  └─────────────┘
```

## Migration Path

| From | To | Process |
|------|----|---------|
| Standard → Premium | Online | Create tenant schema, migrate data, update routing |
| Premium → Enterprise | Scheduled | Provision dedicated DB, pg_dump/restore, DNS cutover |
| Self-hosted → Cloud | Manual | Export/import with tenant ID mapping |
