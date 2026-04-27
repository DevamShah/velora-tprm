---
tags:
  - archeon
  - forgeon
  - product
  - product-velora
---

# Velora TPRM -- Low-Level Design

> **Product**: Velora TPRM (Third-Party Risk Management)
> **Author**: Vinyason (System Designer, Pantheon)
> **Version**: 1.0.0
> **Date**: 2026-03-27
> **Status**: Draft -- Pending MCA Review
> **Classification**: Internal -- Engineering
> **Inputs**: PRD v1.0.0 (Darshika), HLD v1.0.0 (Rachnika), Technical Architecture Research v1.0.0, Scoring & Framework Research v1.0.0

---

## Table of Contents

1. [Database Schema](#1-database-schema)
2. [API Specification](#2-api-specification)
3. [State Machine Definitions](#3-state-machine-definitions)
4. [Background Job Definitions](#4-background-job-definitions)
5. [Event System](#5-event-system)
6. [Configuration Schema](#6-configuration-schema)
7. [AI Pipeline Specifications](#7-ai-pipeline-specifications)

---

## 1. Database Schema

### 1.1 Enum Types

```sql
-- Vendor lifecycle states
CREATE TYPE vendor_status AS ENUM (
    'discovered', 'classified', 'assessing', 'active',
    'monitoring', 'reassessing', 'offboarding', 'offboarded', 'archived'
);

-- Vendor tiers
CREATE TYPE vendor_tier AS ENUM ('tier_1', 'tier_2', 'tier_3', 'tier_4');

-- Assessment states
CREATE TYPE assessment_status AS ENUM (
    'draft', 'distributed', 'in_progress', 'submitted',
    'under_review', 'completed', 'cancelled'
);

-- Finding states
CREATE TYPE finding_status AS ENUM (
    'open', 'remediation_in_progress', 'submitted_for_verification',
    'verified_closed', 'risk_accepted', 'wont_fix'
);

-- Alert states
CREATE TYPE alert_status AS ENUM (
    'new', 'acknowledged', 'investigating', 'resolved', 'suppressed'
);

-- Evidence states
CREATE TYPE evidence_status AS ENUM (
    'uploaded', 'processing', 'parsed', 'mapped', 'verified', 'failed'
);

-- Alert priority
CREATE TYPE alert_priority AS ENUM ('p0', 'p1', 'p2', 'p3', 'p4');

-- Evidence document types
CREATE TYPE document_type AS ENUM (
    'soc2_type1', 'soc2_type2', 'iso27001_cert', 'pentest_report',
    'vuln_scan', 'policy_document', 'insurance_cert', 'bcp_plan',
    'privacy_policy', 'dpa', 'custom', 'other'
);

-- Evidence coverage types
CREATE TYPE coverage_type AS ENUM ('full', 'partial', 'supportive');

-- Confidence tier
CREATE TYPE confidence_tier AS ENUM ('high', 'medium', 'low');

-- Scoring method
CREATE TYPE scoring_method AS ENUM ('weighted_average', 'multiplicative');

-- Residual risk method
CREATE TYPE residual_risk_method AS ENUM ('subtraction', 'multiplication');

-- Mapping relationship type
CREATE TYPE mapping_type AS ENUM ('equivalent', 'partial', 'related', 'subset', 'superset');

-- Framework status
CREATE TYPE framework_status AS ENUM ('active', 'superseded', 'draft');

-- Notification channel
CREATE TYPE notification_channel AS ENUM ('email', 'slack', 'teams', 'in_app', 'sms');

-- Actor type for audit logs
CREATE TYPE actor_type AS ENUM ('user', 'system', 'api_key', 'ai_pipeline', 'vendor_portal');

-- Question type
CREATE TYPE question_type AS ENUM (
    'yes_no', 'yes_no_na', 'single_select', 'multi_select',
    'open_text', 'numeric', 'date', 'file_upload'
);

-- Report format
CREATE TYPE report_format AS ENUM ('pdf', 'pptx', 'csv', 'json', 'xlsx');

-- Data sensitivity classification
CREATE TYPE data_sensitivity AS ENUM ('public', 'internal', 'confidential', 'restricted');

-- Remediation action status
CREATE TYPE remediation_status AS ENUM (
    'pending', 'in_progress', 'evidence_submitted',
    'verification_in_progress', 'verified', 'rejected', 'overdue'
);
```

### 1.2 Core Tables

#### tenants

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    domain TEXT,
    industry TEXT,
    employee_count_range TEXT,
    regulatory_exposure TEXT[],
    isolation_tier TEXT NOT NULL DEFAULT 'standard'
        CHECK (isolation_tier IN ('standard', 'premium', 'enterprise')),
    onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
    subscription_tier TEXT NOT NULL DEFAULT 'professional'
        CHECK (subscription_tier IN ('professional', 'business', 'enterprise')),
    subscription_status TEXT NOT NULL DEFAULT 'active'
        CHECK (subscription_status IN ('active', 'trial', 'suspended', 'cancelled')),
    trial_ends_at TIMESTAMPTZ,
    settings JSONB NOT NULL DEFAULT '{}',
    -- settings schema:
    -- {
    --   "timezone": "America/New_York",
    --   "date_format": "YYYY-MM-DD",
    --   "default_assessment_deadline_days": 30,
    --   "session_timeout_minutes": 30,
    --   "mfa_required": false,
    --   "allowed_ip_ranges": [],
    --   "data_residency_region": "us-east-1"
    -- }
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tenants_slug ON tenants (slug);
CREATE INDEX idx_tenants_domain ON tenants (domain);
```

#### users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT NOT NULL,
    display_name TEXT,
    avatar_url TEXT,
    idp_subject_id TEXT,
    idp_provider TEXT,
    mfa_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    mfa_secret_encrypted BYTEA,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'suspended', 'pending_activation')),
    last_login_at TIMESTAMPTZ,
    last_login_ip INET,
    failed_login_count INT NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    notification_preferences JSONB NOT NULL DEFAULT '{}',
    -- notification_preferences schema:
    -- {
    --   "email": true,
    --   "in_app": true,
    --   "slack": false,
    --   "sms_for_p0": false,
    --   "digest_frequency": "daily",
    --   "quiet_hours": { "start": "22:00", "end": "07:00", "timezone": "America/New_York" }
    -- }
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, email)
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON users
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_users_tenant_email ON users (tenant_id, email);
CREATE INDEX idx_users_tenant_status ON users (tenant_id, status);
CREATE INDEX idx_users_idp ON users (idp_provider, idp_subject_id);
```

#### roles

```sql
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    -- tenant_id is NULL for system-defined roles (global)
    name TEXT NOT NULL,
    display_name TEXT NOT NULL,
    description TEXT,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    is_custom BOOLEAN NOT NULL DEFAULT FALSE,
    permissions TEXT[] NOT NULL DEFAULT '{}',
    -- permissions: array of permission strings e.g.
    -- ['vendors:read', 'vendors:write', 'assessments:read', 'assessments:write',
    --  'assessments:approve', 'evidence:read', 'evidence:upload', 'reports:read',
    --  'reports:generate', 'admin:users', 'admin:config', 'admin:audit',
    --  'scoring:read', 'scoring:configure', 'scoring:override',
    --  'monitoring:read', 'monitoring:configure', 'findings:read', 'findings:write',
    --  'portal:manage', 'ai:query', 'integrations:manage']
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, name)
);

-- System roles are not tenant-scoped; custom roles are
ALTER TABLE roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY role_isolation ON roles
    USING (tenant_id IS NULL OR tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_roles_tenant ON roles (tenant_id);
```

#### permissions

```sql
CREATE TABLE permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    resource TEXT NOT NULL,
    action TEXT NOT NULL,
    description TEXT,
    UNIQUE (resource, action)
);

-- Seed data: vendors:read, vendors:write, vendors:delete, vendors:approve,
-- assessments:read, assessments:write, assessments:approve, assessments:distribute,
-- evidence:read, evidence:upload, evidence:delete, findings:read, findings:write,
-- findings:close, scoring:read, scoring:configure, scoring:override,
-- monitoring:read, monitoring:configure, monitoring:acknowledge,
-- reports:read, reports:generate, reports:schedule,
-- admin:users, admin:config, admin:audit, admin:integrations,
-- portal:manage, ai:query, frameworks:read, frameworks:manage
```

#### user_roles

```sql
CREATE TABLE user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE (tenant_id, user_id, role_id)
);

ALTER TABLE user_roles ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON user_roles
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_user_roles_tenant_user ON user_roles (tenant_id, user_id);
CREATE INDEX idx_user_roles_tenant_role ON user_roles (tenant_id, role_id);
```

#### sessions

```sql
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash TEXT NOT NULL UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON sessions
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_sessions_tenant_user ON sessions (tenant_id, user_id);
CREATE INDEX idx_sessions_refresh ON sessions (refresh_token_hash) WHERE NOT revoked;
CREATE INDEX idx_sessions_expiry ON sessions (expires_at) WHERE NOT revoked;
```

### 1.3 Vendor Tables

#### vendors

```sql
CREATE TABLE vendors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    legal_name TEXT,
    domain TEXT,
    website TEXT,
    industry TEXT,
    employee_count_range TEXT,
    headquarters_country TEXT,
    headquarters_city TEXT,
    description TEXT,
    status vendor_status NOT NULL DEFAULT 'discovered',
    tier vendor_tier,
    data_sensitivity data_sensitivity,
    access_level TEXT CHECK (access_level IN ('none', 'network', 'application', 'data', 'physical')),
    business_criticality INT CHECK (business_criticality BETWEEN 1 AND 5),
    regulatory_exposure TEXT[],
    inherent_risk_score NUMERIC(5,2),
    residual_risk_score NUMERIC(5,2),
    composite_risk_score NUMERIC(5,2),
    external_rating_score NUMERIC(5,2),
    external_rating_provider TEXT,
    external_rating_grade TEXT,
    external_rating_updated_at TIMESTAMPTZ,
    risk_tier TEXT CHECK (risk_tier IN ('critical', 'high', 'medium', 'low')),
    contract_start_date DATE,
    contract_end_date DATE,
    contract_value NUMERIC(15,2),
    contract_currency TEXT DEFAULT 'USD',
    onboarding_completed_at TIMESTAMPTZ,
    last_assessment_at TIMESTAMPTZ,
    next_assessment_due DATE,
    last_enrichment_at TIMESTAMPTZ,
    tags TEXT[],
    parent_vendor_id UUID REFERENCES vendors(id),
    metadata JSONB NOT NULL DEFAULT '{}',
    -- metadata schema:
    -- {
    --   "procurement_system_id": "...",
    --   "internal_reference": "...",
    --   "business_unit": "...",
    --   "relationship_owner": "user_uuid",
    --   "dpa_signed": true,
    --   "dpa_signed_date": "2025-06-01"
    -- }
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, domain)
);

ALTER TABLE vendors ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendors
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_vendors_tenant_id ON vendors (tenant_id, id);
CREATE INDEX idx_vendors_tenant_status ON vendors (tenant_id, status);
CREATE INDEX idx_vendors_tenant_tier ON vendors (tenant_id, tier);
CREATE INDEX idx_vendors_tenant_risk ON vendors (tenant_id, composite_risk_score);
CREATE INDEX idx_vendors_tenant_name ON vendors (tenant_id, name);
CREATE INDEX idx_vendors_domain ON vendors (tenant_id, domain);
CREATE INDEX idx_vendors_next_assessment ON vendors (tenant_id, next_assessment_due)
    WHERE next_assessment_due IS NOT NULL;
CREATE INDEX idx_vendors_parent ON vendors (parent_vendor_id)
    WHERE parent_vendor_id IS NOT NULL;
CREATE INDEX idx_vendors_tags ON vendors USING GIN (tags);
```

#### vendor_contacts

```sql
CREATE TABLE vendor_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    full_name TEXT NOT NULL,
    email_encrypted BYTEA NOT NULL,
    email_hash TEXT NOT NULL,
    phone_encrypted BYTEA,
    title TEXT,
    role TEXT CHECK (role IN (
        'primary_security', 'secondary_security', 'privacy', 'compliance',
        'it_admin', 'executive', 'procurement', 'legal', 'other'
    )),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    portal_access_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    last_contacted_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE vendor_contacts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendor_contacts
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_vendor_contacts_tenant_vendor ON vendor_contacts (tenant_id, vendor_id);
CREATE INDEX idx_vendor_contacts_email ON vendor_contacts (tenant_id, email_hash);
```

#### vendor_enrichment

```sql
CREATE TABLE vendor_enrichment (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    -- source: 'clearbit', 'zoominfo', 'securityscorecard', 'bitsight',
    -- 'hibp', 'iacertsearch', 'csa_star', 'trust_center', 'dns_ssl', 'ai_inference'
    raw_data JSONB NOT NULL,
    parsed_data JSONB NOT NULL,
    -- parsed_data varies by source; examples:
    -- clearbit: { "industry": "...", "employee_count": 500, "revenue_range": "...", "tech_stack": [...] }
    -- securityscorecard: { "score": 82, "grade": "B", "factors": {...} }
    -- hibp: { "breaches": [{"name": "...", "date": "...", "data_classes": [...]}] }
    -- ai_inference: { "risk_signals": [...], "inferred_tech_stack": [...], "confidence": 0.85 }
    confidence NUMERIC(3,2),
    enriched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    workflow_run_id TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE vendor_enrichment ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendor_enrichment
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_vendor_enrichment_vendor ON vendor_enrichment (tenant_id, vendor_id, source);
CREATE INDEX idx_vendor_enrichment_current ON vendor_enrichment (tenant_id, vendor_id)
    WHERE is_current = TRUE;
```

#### vendor_tags

```sql
CREATE TABLE vendor_tags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    color TEXT,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, name)
);

ALTER TABLE vendor_tags ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendor_tags
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_vendor_tags_tenant ON vendor_tags (tenant_id);
```

#### vendor_relationships (Nth-party mapping)

```sql
CREATE TABLE vendor_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    related_vendor_id UUID REFERENCES vendors(id) ON DELETE SET NULL,
    related_vendor_name TEXT NOT NULL,
    related_vendor_domain TEXT,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN (
        'sub_processor', 'sub_contractor', 'technology_provider',
        'hosting_provider', 'data_processor', 'reseller', 'parent', 'subsidiary'
    )),
    data_shared TEXT[],
    criticality TEXT CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    source TEXT CHECK (source IN ('manual', 'dpa_extraction', 'ai_inferred', 'vendor_declared')),
    confidence NUMERIC(3,2),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE vendor_relationships ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendor_relationships
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_vendor_relationships_vendor ON vendor_relationships (tenant_id, vendor_id);
CREATE INDEX idx_vendor_relationships_related ON vendor_relationships (tenant_id, related_vendor_id)
    WHERE related_vendor_id IS NOT NULL;
```

### 1.4 Assessment Tables

#### assessment_templates

```sql
CREATE TABLE assessment_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    -- tenant_id is NULL for system-provided templates
    name TEXT NOT NULL,
    description TEXT,
    questionnaire_type TEXT NOT NULL CHECK (questionnaire_type IN (
        'sig_core', 'sig_lite', 'caiq_v4', 'caiq_lite',
        'cis_controls', 'nist_800_171', 'custom'
    )),
    applicable_tiers vendor_tier[],
    applicable_frameworks UUID[],
    default_deadline_days INT NOT NULL DEFAULT 30,
    question_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    version INT NOT NULL DEFAULT 1,
    config JSONB NOT NULL DEFAULT '{}',
    -- config schema:
    -- {
    --   "sections": [
    --     {
    --       "id": "uuid",
    --       "title": "Access Control",
    --       "order": 1,
    --       "framework_domain": "access_control",
    --       "question_ids": ["uuid1", "uuid2"]
    --     }
    --   ],
    --   "scoring_weights": { "access_control": 0.15, "encryption": 0.10, ... },
    --   "conditional_sections": [
    --     { "condition": { "field": "vendor.tier", "op": "eq", "value": "tier_1" }, "include_sections": ["uuid"] }
    --   ]
    -- }
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE assessment_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY template_isolation ON assessment_templates
    USING (tenant_id IS NULL OR tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_assessment_templates_tenant ON assessment_templates (tenant_id);
CREATE INDEX idx_assessment_templates_type ON assessment_templates (questionnaire_type);
```

#### assessments

```sql
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES assessment_templates(id),
    title TEXT NOT NULL,
    status assessment_status NOT NULL DEFAULT 'draft',
    assessment_type TEXT NOT NULL DEFAULT 'periodic'
        CHECK (assessment_type IN ('initial', 'periodic', 'event_triggered', 'fast_track', 'contract_renewal')),
    triggered_by TEXT,
    -- triggered_by: 'schedule', 'breach_alert', 'rating_drop', 'cert_expiry',
    --   'contract_renewal', 'manual', 'm_and_a'
    assigned_to UUID REFERENCES users(id),
    reviewer_id UUID REFERENCES users(id),
    vendor_contact_id UUID REFERENCES vendor_contacts(id),
    distributed_at TIMESTAMPTZ,
    deadline TIMESTAMPTZ,
    submitted_at TIMESTAMPTZ,
    review_started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancelled_reason TEXT,
    questionnaire_score NUMERIC(5,2),
    evidence_score NUMERIC(5,2),
    composite_score NUMERIC(5,2),
    total_questions INT NOT NULL DEFAULT 0,
    answered_questions INT NOT NULL DEFAULT 0,
    ai_prefilled_questions INT NOT NULL DEFAULT 0,
    human_reviewed_questions INT NOT NULL DEFAULT 0,
    flagged_items_count INT NOT NULL DEFAULT 0,
    findings_count INT NOT NULL DEFAULT 0,
    applicable_frameworks UUID[],
    reminder_schedule JSONB NOT NULL DEFAULT '[]',
    -- reminder_schedule: [
    --   { "day": 7, "sent": false, "sent_at": null },
    --   { "day": 14, "sent": false, "sent_at": null },
    --   { "day": 21, "sent": false, "sent_at": null }
    -- ]
    scoring_details JSONB NOT NULL DEFAULT '{}',
    -- scoring_details: {
    --   "method": "weighted_average",
    --   "dimension_scores": { "security": 72, "privacy": 65, "operational": 80, ... },
    --   "section_scores": { "access_control": 85, "encryption": 70, ... },
    --   "confidence": 0.82
    -- }
    metadata JSONB NOT NULL DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE assessments ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON assessments
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_assessments_tenant_id ON assessments (tenant_id, id);
CREATE INDEX idx_assessments_tenant_vendor ON assessments (tenant_id, vendor_id);
CREATE INDEX idx_assessments_tenant_status ON assessments (tenant_id, status);
CREATE INDEX idx_assessments_assigned ON assessments (tenant_id, assigned_to)
    WHERE status NOT IN ('completed', 'cancelled');
CREATE INDEX idx_assessments_reviewer ON assessments (tenant_id, reviewer_id)
    WHERE status = 'under_review';
CREATE INDEX idx_assessments_deadline ON assessments (tenant_id, deadline)
    WHERE status IN ('distributed', 'in_progress');
```

#### question_banks

```sql
CREATE TABLE question_banks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    -- NULL for system question banks
    name TEXT NOT NULL,
    description TEXT,
    source TEXT CHECK (source IN ('sig_2025', 'caiq_v4', 'cis_v8', 'nist_800_171', 'system_generated', 'custom')),
    version TEXT,
    question_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE question_banks ENABLE ROW LEVEL SECURITY;
CREATE POLICY bank_isolation ON question_banks
    USING (tenant_id IS NULL OR tenant_id = current_setting('app.current_tenant_id')::UUID);
```

#### questions

```sql
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bank_id UUID NOT NULL REFERENCES question_banks(id) ON DELETE CASCADE,
    section_path TEXT,
    question_number TEXT,
    question_text TEXT NOT NULL,
    question_type question_type NOT NULL DEFAULT 'open_text',
    options JSONB,
    -- options (for single_select/multi_select):
    -- [
    --   { "value": "yes", "label": "Yes", "score": 1.0 },
    --   { "value": "no", "label": "No", "score": 0.0 },
    --   { "value": "partial", "label": "Partially Implemented", "score": 0.5 },
    --   { "value": "na", "label": "Not Applicable", "score": null }
    -- ]
    guidance TEXT,
    evidence_expected TEXT[],
    scoring_guidance TEXT,
    weight NUMERIC(3,2) NOT NULL DEFAULT 1.0,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    framework_clause_ids UUID[],
    risk_domain TEXT,
    -- risk_domain: 'access_control', 'application_security', 'ai',
    -- 'asset_management', 'business_continuity', 'cloud_hosting', 'compliance',
    -- 'data_privacy', 'endpoint_protection', 'encryption', 'governance',
    -- 'human_resources', 'incident_management', 'information_security',
    -- 'network_security', 'nth_party', 'operations', 'physical_security',
    -- 'risk_management', 'server_security', 'esg'
    conditional_on JSONB,
    -- conditional_on: { "question_id": "uuid", "answer_value": "yes" }
    sort_order INT NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_questions_bank ON questions (bank_id, sort_order);
CREATE INDEX idx_questions_framework ON questions USING GIN (framework_clause_ids);
CREATE INDEX idx_questions_domain ON questions (risk_domain);
```

#### questionnaire_responses

```sql
CREATE TABLE questionnaire_responses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    assessment_id UUID NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES questions(id),
    response_value TEXT,
    response_text TEXT,
    response_data JSONB,
    -- response_data for complex answers:
    -- {
    --   "selected_options": ["yes"],
    --   "attachments": [{"evidence_id": "uuid", "file_name": "..."}],
    --   "additional_context": "..."
    -- }
    score NUMERIC(3,2),
    is_ai_prefilled BOOLEAN NOT NULL DEFAULT FALSE,
    ai_confidence NUMERIC(3,2),
    ai_citations JSONB,
    -- ai_citations: [
    --   { "source": "prior_response", "assessment_id": "uuid", "text": "..." },
    --   { "source": "evidence", "evidence_id": "uuid", "page": 12, "text": "..." },
    --   { "source": "trust_center", "url": "...", "text": "..." }
    -- ]
    ai_prefill_source TEXT,
    -- ai_prefill_source: 'prior_response', 'evidence', 'trust_center', 'public_info'
    review_status TEXT DEFAULT 'pending'
        CHECK (review_status IN ('pending', 'accepted', 'modified', 'rejected', 'flagged')),
    reviewer_id UUID REFERENCES users(id),
    reviewer_comment TEXT,
    reviewed_at TIMESTAMPTZ,
    vendor_modified BOOLEAN NOT NULL DEFAULT FALSE,
    vendor_comment TEXT,
    responded_by TEXT,
    responded_at TIMESTAMPTZ,
    flag_reason TEXT,
    -- flag_reason: 'low_confidence', 'inconsistency_detected', 'evidence_contradiction',
    --   'incomplete_response', 'manual_flag'
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, assessment_id, question_id)
);

ALTER TABLE questionnaire_responses ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON questionnaire_responses
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_qr_tenant_assessment ON questionnaire_responses (tenant_id, assessment_id);
CREATE INDEX idx_qr_review_status ON questionnaire_responses (tenant_id, assessment_id, review_status)
    WHERE review_status IN ('pending', 'flagged');
CREATE INDEX idx_qr_ai_prefilled ON questionnaire_responses (tenant_id, assessment_id)
    WHERE is_ai_prefilled = TRUE;
```

### 1.5 Framework Tables

These are global (not tenant-scoped) -- frameworks are shared across all tenants.

#### frameworks

```sql
CREATE TABLE frameworks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    short_name TEXT NOT NULL,
    version TEXT NOT NULL,
    publisher TEXT,
    effective_date DATE,
    status framework_status NOT NULL DEFAULT 'active',
    supersedes_id UUID REFERENCES frameworks(id),
    source_url TEXT,
    source_format TEXT CHECK (source_format IN ('oscal_json', 'oscal_xml', 'pdf', 'html', 'manual')),
    clause_count INT NOT NULL DEFAULT 0,
    structure JSONB NOT NULL DEFAULT '{}',
    -- structure:
    -- {
    --   "hierarchy": ["function", "category", "subcategory"],
    --   "domains": ["access_control", "asset_management", ...],
    --   "total_controls": 93
    -- }
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (short_name, version)
);

CREATE INDEX idx_frameworks_status ON frameworks (status);
CREATE INDEX idx_frameworks_name ON frameworks (short_name);
```

#### framework_versions

```sql
CREATE TABLE framework_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID NOT NULL REFERENCES frameworks(id) ON DELETE CASCADE,
    version TEXT NOT NULL,
    release_date DATE,
    effective_date DATE,
    changelog TEXT,
    diff_from_previous JSONB,
    -- diff_from_previous:
    -- {
    --   "added": [{"clause_id": "...", "section_path": "A.5.1", "title": "..."}],
    --   "modified": [{"clause_id": "...", "section_path": "A.8.9", "changes": "..."}],
    --   "removed": [{"section_path": "A.11.3", "title": "..."}],
    --   "summary": "93 controls (down from 114), reorganized into 4 themes"
    -- }
    imported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    imported_by TEXT
);

CREATE INDEX idx_framework_versions_framework ON framework_versions (framework_id);
```

#### framework_clauses

```sql
CREATE TABLE framework_clauses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    framework_id UUID NOT NULL REFERENCES frameworks(id) ON DELETE CASCADE,
    section_path TEXT NOT NULL,
    title TEXT,
    clause_text TEXT NOT NULL,
    parent_clause_id UUID REFERENCES framework_clauses(id),
    depth INT NOT NULL DEFAULT 0,
    sort_order INT NOT NULL DEFAULT 0,
    domain TEXT,
    keywords TEXT[],
    applicability_tags JSONB,
    -- applicability_tags:
    -- {
    --   "industries": ["financial_services", "healthcare"],
    --   "data_types": ["pii", "phi"],
    --   "mandatory": true
    -- }
    embedding vector(1536),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (framework_id, section_path)
);

CREATE INDEX idx_clauses_framework ON framework_clauses (framework_id, sort_order);
CREATE INDEX idx_clauses_parent ON framework_clauses (parent_clause_id);
CREATE INDEX idx_clauses_domain ON framework_clauses (domain);
CREATE INDEX idx_clauses_embedding ON framework_clauses
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_clauses_keywords ON framework_clauses USING GIN (keywords);
```

#### control_mappings

```sql
CREATE TABLE control_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_clause_id UUID NOT NULL REFERENCES framework_clauses(id) ON DELETE CASCADE,
    target_clause_id UUID NOT NULL REFERENCES framework_clauses(id) ON DELETE CASCADE,
    mapping_type mapping_type NOT NULL,
    confidence NUMERIC(3,2) NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('nist_olir', 'ai_generated', 'manual', 'ucf_import')),
    rationale TEXT,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (source_clause_id, target_clause_id)
);

CREATE INDEX idx_control_mappings_source ON control_mappings (source_clause_id);
CREATE INDEX idx_control_mappings_target ON control_mappings (target_clause_id);
CREATE INDEX idx_control_mappings_unverified ON control_mappings (verified)
    WHERE verified = FALSE;
```

#### question_framework_mappings

```sql
CREATE TABLE question_framework_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    clause_id UUID NOT NULL REFERENCES framework_clauses(id) ON DELETE CASCADE,
    coverage coverage_type NOT NULL DEFAULT 'full',
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (question_id, clause_id)
);

CREATE INDEX idx_qfm_question ON question_framework_mappings (question_id);
CREATE INDEX idx_qfm_clause ON question_framework_mappings (clause_id);
```

### 1.6 Scoring Tables

#### scoring_models

```sql
CREATE TABLE scoring_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    method scoring_method NOT NULL DEFAULT 'weighted_average',
    residual_method residual_risk_method NOT NULL DEFAULT 'multiplication',
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    version INT NOT NULL DEFAULT 1,
    config JSONB NOT NULL,
    -- config schema (documented in Section 6):
    -- {
    --   "inherent_risk": {
    --     "factors": [
    --       { "name": "data_sensitivity", "weight": 0.20, "source": "vendor.data_sensitivity", "scale": { "public": 1, "internal": 3, "confidential": 7, "restricted": 10 } },
    --       { "name": "access_level", "weight": 0.20, "source": "vendor.access_level", "scale": { "none": 1, "network": 3, "application": 5, "data": 8, "physical": 10 } },
    --       { "name": "business_criticality", "weight": 0.20, "source": "vendor.business_criticality", "scale_min": 1, "scale_max": 5 },
    --       { "name": "regulatory_exposure", "weight": 0.15, "source": "vendor.regulatory_exposure", "scale_per_framework": 2.0, "max": 10 }
    --     ],
    --     "tier_thresholds": { "tier_1": 85, "tier_2": 70, "tier_3": 40, "tier_4": 0 }
    --   },
    --   "composite_risk": {
    --     "dimensions": [
    --       { "name": "security_posture", "weight": 0.25, "source": "external_rating" },
    --       { "name": "data_sensitivity", "weight": 0.18, "source": "inherent_risk.data_sensitivity" },
    --       { "name": "business_criticality", "weight": 0.18, "source": "inherent_risk.business_criticality" },
    --       { "name": "compliance_status", "weight": 0.12, "source": "assessment.compliance_score" },
    --       { "name": "control_maturity", "weight": 0.12, "source": "assessment.questionnaire_score" },
    --       { "name": "incident_history", "weight": 0.08, "source": "monitoring.incident_count" },
    --       { "name": "financial_stability", "weight": 0.07, "source": "enrichment.financial_signals" }
    --     ]
    --   },
    --   "risk_thresholds": { "critical": 85, "high": 70, "medium": 40, "low": 0 }
    -- }
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE scoring_models ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON scoring_models
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_scoring_models_tenant ON scoring_models (tenant_id);
CREATE INDEX idx_scoring_models_default ON scoring_models (tenant_id)
    WHERE is_default = TRUE;
```

#### scoring_configs

```sql
CREATE TABLE scoring_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    scoring_model_id UUID NOT NULL REFERENCES scoring_models(id) ON DELETE CASCADE,
    scope_type TEXT NOT NULL CHECK (scope_type IN ('global', 'tier', 'industry', 'regulation', 'vendor')),
    scope_value TEXT,
    -- scope_value examples: 'tier_1', 'financial_services', 'hipaa', 'vendor_uuid'
    overrides JSONB NOT NULL DEFAULT '{}',
    -- overrides: partial overrides to the parent scoring_model config
    -- { "composite_risk.dimensions[0].weight": 0.30 }
    priority INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE scoring_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON scoring_configs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_scoring_configs_tenant ON scoring_configs (tenant_id, scoring_model_id);
CREATE INDEX idx_scoring_configs_scope ON scoring_configs (tenant_id, scope_type, scope_value);
```

#### vendor_scores

```sql
CREATE TABLE vendor_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    scoring_model_id UUID NOT NULL REFERENCES scoring_models(id),
    inherent_risk_score NUMERIC(5,2) NOT NULL,
    residual_risk_score NUMERIC(5,2),
    composite_risk_score NUMERIC(5,2),
    external_rating_normalized NUMERIC(5,2),
    risk_tier TEXT CHECK (risk_tier IN ('critical', 'high', 'medium', 'low')),
    dimension_scores JSONB NOT NULL DEFAULT '{}',
    -- dimension_scores:
    -- {
    --   "security_posture": 72.5,
    --   "data_sensitivity": 85.0,
    --   "business_criticality": 60.0,
    --   "compliance_status": 70.0,
    --   "control_maturity": 65.0,
    --   "incident_history": 90.0,
    --   "financial_stability": 80.0
    -- }
    fair_estimate JSONB,
    -- fair_estimate (FAIR quantification):
    -- {
    --   "annual_loss_expectancy": 125000.00,
    --   "loss_event_frequency": 0.15,
    --   "loss_magnitude": 833333.33,
    --   "primary_loss": 500000.00,
    --   "secondary_loss": 333333.33,
    --   "confidence_interval": { "low": 50000, "high": 300000, "percentile": 90 },
    --   "scenario": "Data breach via vendor access",
    --   "calculated_at": "2026-03-27T10:00:00Z"
    -- }
    input_snapshot JSONB NOT NULL DEFAULT '{}',
    -- input_snapshot: frozen copy of all inputs used for this calculation
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_current BOOLEAN NOT NULL DEFAULT TRUE,
    triggered_by TEXT,
    -- triggered_by: 'assessment_completed', 'evidence_uploaded', 'rating_changed',
    --   'monitoring_alert', 'manual_recalc', 'config_change'
    UNIQUE (tenant_id, vendor_id) -- only current score enforced unique
);

ALTER TABLE vendor_scores ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendor_scores
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_vendor_scores_tenant_vendor ON vendor_scores (tenant_id, vendor_id)
    WHERE is_current = TRUE;
CREATE INDEX idx_vendor_scores_risk ON vendor_scores (tenant_id, composite_risk_score DESC)
    WHERE is_current = TRUE;
```

#### score_history

```sql
CREATE TABLE score_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    scoring_model_id UUID NOT NULL REFERENCES scoring_models(id),
    inherent_risk_score NUMERIC(5,2),
    residual_risk_score NUMERIC(5,2),
    composite_risk_score NUMERIC(5,2),
    external_rating_normalized NUMERIC(5,2),
    risk_tier TEXT,
    dimension_scores JSONB,
    fair_estimate JSONB,
    input_snapshot JSONB NOT NULL DEFAULT '{}',
    triggered_by TEXT,
    calculated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE score_history ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON score_history
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_score_history_vendor ON score_history (tenant_id, vendor_id, calculated_at DESC);
CREATE INDEX idx_score_history_time ON score_history (tenant_id, calculated_at DESC);
```

#### score_overrides

```sql
CREATE TABLE score_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    override_type TEXT NOT NULL CHECK (override_type IN (
        'composite_score', 'risk_tier', 'dimension_score', 'inherent_risk', 'residual_risk'
    )),
    dimension_name TEXT,
    original_value NUMERIC(5,2) NOT NULL,
    override_value NUMERIC(5,2) NOT NULL,
    original_tier TEXT,
    override_tier TEXT,
    justification TEXT NOT NULL,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    renewal_required BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE score_overrides ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON score_overrides
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_score_overrides_vendor ON score_overrides (tenant_id, vendor_id)
    WHERE is_active = TRUE;
CREATE INDEX idx_score_overrides_expiry ON score_overrides (expires_at)
    WHERE is_active = TRUE AND expires_at IS NOT NULL;
```

### 1.7 Evidence Tables

#### evidence

```sql
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES assessments(id),
    file_name TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    mime_type TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    document_type document_type,
    document_type_confidence NUMERIC(3,2),
    status evidence_status NOT NULL DEFAULT 'uploaded',
    version INT NOT NULL DEFAULT 1,
    previous_version_id UUID REFERENCES evidence(id),
    valid_from DATE,
    valid_until DATE,
    issuer TEXT,
    subject TEXT,
    scope TEXT,
    opinion_type TEXT,
    -- opinion_type (for SOC 2): 'unqualified', 'qualified', 'adverse', 'disclaimer'
    exceptions_count INT,
    overall_confidence NUMERIC(3,2),
    freshness_status TEXT GENERATED ALWAYS AS (
        CASE
            WHEN valid_until IS NULL THEN 'unknown'
            WHEN valid_until < CURRENT_DATE THEN 'expired'
            WHEN valid_until < CURRENT_DATE + INTERVAL '90 days' THEN 'stale'
            ELSE 'valid'
        END
    ) STORED,
    parsed_content JSONB,
    -- parsed_content varies by document_type; examples:
    -- soc2_type2: {
    --   "audit_period_start": "2025-04-01", "audit_period_end": "2026-03-31",
    --   "opinion_type": "unqualified",
    --   "auditor": "Deloitte",
    --   "exceptions": [{"control": "CC6.1", "description": "..."}],
    --   "control_statuses": [{"control": "CC1.1", "status": "effective", "description": "..."}],
    --   "cuecs": ["CUEC 1: ...", "CUEC 2: ..."],
    --   "subservice_orgs": [{"name": "AWS", "method": "carve_out"}]
    -- }
    -- iso27001_cert: {
    --   "certifying_body": "BSI", "accredited": true,
    --   "certificate_number": "IS 12345",
    --   "scope": "Cloud hosting and SaaS platform operations",
    --   "issue_date": "2025-01-15", "expiry_date": "2028-01-14",
    --   "surveillance_audits": ["2025-12-01", "2026-12-01"],
    --   "soa_controls_in_scope": ["A.5.1", "A.5.2", ...]
    -- }
    -- pentest_report: {
    --   "testing_firm": "NCC Group", "methodology": "OWASP",
    --   "test_date": "2026-02-15", "scope": "External web application",
    --   "findings_summary": { "critical": 0, "high": 2, "medium": 5, "low": 8, "info": 12 },
    --   "findings": [{ "title": "...", "severity": "high", "cvss": 8.1, "status": "remediated" }]
    -- }
    embedding vector(1536),
    expiry_notified BOOLEAN NOT NULL DEFAULT FALSE,
    uploaded_by UUID REFERENCES users(id),
    uploaded_via TEXT DEFAULT 'ui' CHECK (uploaded_via IN ('ui', 'portal', 'api', 'email')),
    processing_started_at TIMESTAMPTZ,
    processing_completed_at TIMESTAMPTZ,
    processing_error TEXT,
    workflow_run_id TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE evidence ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON evidence
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_evidence_tenant_vendor ON evidence (tenant_id, vendor_id);
CREATE INDEX idx_evidence_tenant_assessment ON evidence (tenant_id, assessment_id)
    WHERE assessment_id IS NOT NULL;
CREATE INDEX idx_evidence_tenant_status ON evidence (tenant_id, status);
CREATE INDEX idx_evidence_tenant_type ON evidence (tenant_id, document_type);
CREATE INDEX idx_evidence_hash ON evidence (tenant_id, file_hash);
CREATE INDEX idx_evidence_expiry ON evidence (tenant_id, valid_until)
    WHERE valid_until IS NOT NULL;
CREATE INDEX idx_evidence_embedding ON evidence
    USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);
CREATE INDEX idx_evidence_freshness ON evidence (tenant_id, freshness_status)
    WHERE freshness_status IN ('expired', 'stale');
```

#### evidence_versions

```sql
CREATE TABLE evidence_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    evidence_id UUID NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    version INT NOT NULL,
    file_hash TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL,
    uploaded_by UUID REFERENCES users(id),
    change_summary TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE evidence_versions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON evidence_versions
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_evidence_versions_evidence ON evidence_versions (tenant_id, evidence_id, version DESC);
```

#### evidence_control_mappings

```sql
CREATE TABLE evidence_control_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    evidence_id UUID NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    clause_id UUID NOT NULL REFERENCES framework_clauses(id),
    coverage coverage_type NOT NULL,
    confidence NUMERIC(3,2) NOT NULL,
    confidence_tier confidence_tier NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('ai_extracted', 'manual', 'rule_based')),
    extracted_text TEXT,
    page_number INT,
    control_status TEXT CHECK (control_status IN (
        'effective', 'ineffective', 'not_tested', 'exception', 'not_applicable'
    )),
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, evidence_id, clause_id)
);

ALTER TABLE evidence_control_mappings ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON evidence_control_mappings
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_ecm_evidence ON evidence_control_mappings (tenant_id, evidence_id);
CREATE INDEX idx_ecm_clause ON evidence_control_mappings (clause_id);
CREATE INDEX idx_ecm_unverified ON evidence_control_mappings (tenant_id)
    WHERE verified = FALSE AND source = 'ai_extracted';
```

#### evidence_extractions

```sql
CREATE TABLE evidence_extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    evidence_id UUID NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    extraction_type TEXT NOT NULL CHECK (extraction_type IN (
        'classification', 'metadata', 'control_status', 'finding',
        'exception', 'scope', 'date', 'entity', 'custom'
    )),
    field_name TEXT NOT NULL,
    extracted_value TEXT,
    structured_value JSONB,
    confidence NUMERIC(3,2) NOT NULL,
    page_number INT,
    bounding_box JSONB,
    -- bounding_box: { "x": 100, "y": 200, "width": 300, "height": 50, "page": 3 }
    llm_prompt_hash TEXT,
    verified BOOLEAN NOT NULL DEFAULT FALSE,
    verified_by UUID REFERENCES users(id),
    verified_value TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE evidence_extractions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON evidence_extractions
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_evidence_extractions_evidence ON evidence_extractions (tenant_id, evidence_id);
CREATE INDEX idx_evidence_extractions_type ON evidence_extractions (tenant_id, extraction_type);
```

### 1.8 Monitoring Tables

#### monitoring_configs

```sql
CREATE TABLE monitoring_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID REFERENCES vendors(id) ON DELETE CASCADE,
    -- NULL vendor_id means tenant-wide default
    signal_source TEXT NOT NULL CHECK (signal_source IN (
        'securityscorecard', 'bitsight', 'riskrecon', 'hibp', 'breachsense',
        'spycloud', 'ct_logs', 'dns', 'ssl', 'news', 'cve_nvd', 'dark_web', 'financial'
    )),
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    frequency_minutes INT NOT NULL,
    -- frequency_minutes: 240 (4hr), 1440 (daily), 10080 (weekly), 43200 (monthly), 129600 (quarterly)
    tier_overrides JSONB NOT NULL DEFAULT '{}',
    -- tier_overrides: { "tier_1": 240, "tier_2": 1440, "tier_3": 10080, "tier_4": 43200 }
    last_poll_at TIMESTAMPTZ,
    next_poll_at TIMESTAMPTZ,
    config JSONB NOT NULL DEFAULT '{}',
    -- config varies by source:
    -- securityscorecard: { "api_key_vault_ref": "vault:ssc_key", "include_factors": true }
    -- hibp: { "monitor_domains": true, "monitor_emails": false }
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE monitoring_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON monitoring_configs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_monitoring_configs_tenant ON monitoring_configs (tenant_id);
CREATE INDEX idx_monitoring_configs_vendor ON monitoring_configs (tenant_id, vendor_id)
    WHERE vendor_id IS NOT NULL;
CREATE INDEX idx_monitoring_configs_next_poll ON monitoring_configs (next_poll_at)
    WHERE is_enabled = TRUE;
```

#### monitoring_signals

```sql
CREATE TABLE monitoring_signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    -- signal_type: 'rating_change', 'breach_detected', 'credential_leak',
    --   'cert_expiry', 'dns_change', 'cve_exposure', 'news_mention',
    --   'dark_web_mention', 'regulatory_action', 'financial_change', 'personnel_change'
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'info')),
    title TEXT NOT NULL,
    description TEXT,
    raw_data JSONB NOT NULL,
    -- raw_data: original API response data
    enriched_data JSONB,
    -- enriched_data: {
    --   "affected_data_types": ["pii", "credentials"],
    --   "estimated_impact": "high",
    --   "regulatory_implications": ["gdpr_art_33", "hipaa_breach_notification"],
    --   "related_signals": ["signal_uuid_1", "signal_uuid_2"]
    -- }
    dedup_key TEXT NOT NULL,
    -- dedup_key: hash of (vendor_id + signal_type + key_attributes) for dedup window
    is_duplicate BOOLEAN NOT NULL DEFAULT FALSE,
    duplicate_of UUID REFERENCES monitoring_signals(id),
    detected_at TIMESTAMPTZ NOT NULL,
    processed_at TIMESTAMPTZ DEFAULT NOW(),
    alert_id UUID,
    -- populated if this signal generated or contributed to an alert
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE monitoring_signals ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON monitoring_signals
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_monitoring_signals_vendor ON monitoring_signals (tenant_id, vendor_id, detected_at DESC);
CREATE INDEX idx_monitoring_signals_dedup ON monitoring_signals (dedup_key, detected_at DESC);
CREATE INDEX idx_monitoring_signals_source ON monitoring_signals (tenant_id, source, detected_at DESC);
CREATE INDEX idx_monitoring_signals_severity ON monitoring_signals (tenant_id, severity)
    WHERE NOT is_duplicate;
```

#### alerts

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    priority alert_priority NOT NULL,
    status alert_status NOT NULL DEFAULT 'new',
    title TEXT NOT NULL,
    description TEXT,
    signal_ids UUID[] NOT NULL,
    correlation_key TEXT,
    -- correlation_key: vendor_id + signal_category for multi-signal correlation
    escalated_from UUID REFERENCES alerts(id),
    -- if this alert was auto-escalated from lower priority
    assigned_to UUID REFERENCES users(id),
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMPTZ,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,
    suppressed_by UUID REFERENCES users(id),
    suppressed_at TIMESTAMPTZ,
    suppression_reason TEXT,
    suppression_expires_at TIMESTAMPTZ,
    impact_assessment JSONB,
    -- impact_assessment: {
    --   "data_at_risk": ["pii", "financial_records"],
    --   "regulatory_exposure": ["hipaa", "gdpr"],
    --   "estimated_financial_impact": 150000,
    --   "affected_systems": ["crm", "billing"],
    --   "recommended_actions": ["initiate_fast_track_assessment", "contact_vendor_security"]
    -- }
    notification_sent BOOLEAN NOT NULL DEFAULT FALSE,
    notification_channels notification_channel[],
    triggered_assessment_id UUID REFERENCES assessments(id),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON alerts
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_alerts_tenant_status ON alerts (tenant_id, status)
    WHERE status IN ('new', 'acknowledged', 'investigating');
CREATE INDEX idx_alerts_tenant_vendor ON alerts (tenant_id, vendor_id, created_at DESC);
CREATE INDEX idx_alerts_tenant_priority ON alerts (tenant_id, priority)
    WHERE status IN ('new', 'acknowledged', 'investigating');
CREATE INDEX idx_alerts_assigned ON alerts (tenant_id, assigned_to)
    WHERE status NOT IN ('resolved', 'suppressed');
CREATE INDEX idx_alerts_correlation ON alerts (correlation_key, created_at DESC);
```

#### alert_rules

```sql
CREATE TABLE alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    signal_type TEXT NOT NULL,
    conditions JSONB NOT NULL,
    -- conditions:
    -- {
    --   "operator": "and",
    --   "rules": [
    --     { "field": "severity", "op": "gte", "value": "high" },
    --     { "field": "vendor.tier", "op": "in", "value": ["tier_1", "tier_2"] }
    --   ]
    -- }
    resulting_priority alert_priority NOT NULL,
    actions JSONB NOT NULL DEFAULT '[]',
    -- actions:
    -- [
    --   { "type": "notify", "channels": ["email", "slack"], "recipients": ["role:ciso", "role:tprm_manager"] },
    --   { "type": "create_ticket", "template": "security_incident" },
    --   { "type": "trigger_assessment", "template_id": "uuid", "type": "fast_track" },
    --   { "type": "escalate", "from_priority": "p2", "to_priority": "p1", "condition": "multiple_signals_48h" }
    -- ]
    cooldown_minutes INT NOT NULL DEFAULT 1440,
    sort_order INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE alert_rules ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON alert_rules
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_alert_rules_tenant ON alert_rules (tenant_id, is_active, sort_order);
CREATE INDEX idx_alert_rules_signal ON alert_rules (signal_type) WHERE is_active = TRUE;
```

#### vendor_timelines

```sql
CREATE TABLE vendor_timelines (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    -- event_type: 'vendor_created', 'enrichment_completed', 'tier_changed',
    --   'assessment_created', 'assessment_completed', 'evidence_uploaded',
    --   'evidence_expired', 'alert_created', 'alert_resolved', 'score_changed',
    --   'finding_created', 'finding_closed', 'remediation_completed',
    --   'rating_change', 'contact_changed', 'status_changed', 'communication_sent'
    title TEXT NOT NULL,
    description TEXT,
    reference_type TEXT,
    reference_id UUID,
    -- reference_type + reference_id point to related entity (assessment, alert, evidence, etc.)
    actor_id UUID REFERENCES users(id),
    actor_type actor_type,
    data JSONB NOT NULL DEFAULT '{}',
    -- data: event-specific payload (e.g., { "old_score": 72, "new_score": 65, "delta": -7 })
    occurred_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE vendor_timelines ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendor_timelines
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_vendor_timelines_vendor ON vendor_timelines (tenant_id, vendor_id, occurred_at DESC);
CREATE INDEX idx_vendor_timelines_type ON vendor_timelines (tenant_id, event_type, occurred_at DESC);
```

### 1.9 Findings Tables

#### findings

```sql
CREATE TABLE findings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    assessment_id UUID REFERENCES assessments(id),
    alert_id UUID REFERENCES alerts(id),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('critical', 'high', 'medium', 'low', 'informational')),
    status finding_status NOT NULL DEFAULT 'open',
    source TEXT NOT NULL CHECK (source IN (
        'assessment_gap', 'evidence_review', 'monitoring_alert',
        'manual', 'ai_detected', 'external_audit'
    )),
    affected_controls UUID[],
    -- affected_controls: array of framework_clause IDs
    affected_frameworks TEXT[],
    remediation_guidance TEXT,
    ai_generated_guidance TEXT,
    ai_guidance_confidence NUMERIC(3,2),
    deadline TIMESTAMPTZ,
    -- deadline computed from severity SLAs: critical=30d, high=60d, medium=90d, low=120d
    sla_status TEXT GENERATED ALWAYS AS (
        CASE
            WHEN status IN ('verified_closed', 'risk_accepted', 'wont_fix') THEN 'completed'
            WHEN deadline IS NULL THEN 'no_sla'
            WHEN deadline < NOW() THEN 'overdue'
            WHEN deadline < NOW() + INTERVAL '7 days' THEN 'at_risk'
            ELSE 'on_track'
        END
    ) STORED,
    assigned_to_vendor_contact UUID REFERENCES vendor_contacts(id),
    internal_owner UUID REFERENCES users(id),
    risk_accepted_by UUID REFERENCES users(id),
    risk_accepted_at TIMESTAMPTZ,
    risk_acceptance_justification TEXT,
    risk_acceptance_expires_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    closed_by UUID REFERENCES users(id),
    closure_notes TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE findings ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON findings
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_findings_tenant_vendor ON findings (tenant_id, vendor_id);
CREATE INDEX idx_findings_tenant_status ON findings (tenant_id, status)
    WHERE status NOT IN ('verified_closed', 'risk_accepted', 'wont_fix');
CREATE INDEX idx_findings_tenant_severity ON findings (tenant_id, severity)
    WHERE status NOT IN ('verified_closed', 'risk_accepted', 'wont_fix');
CREATE INDEX idx_findings_deadline ON findings (tenant_id, deadline)
    WHERE status NOT IN ('verified_closed', 'risk_accepted', 'wont_fix');
CREATE INDEX idx_findings_assessment ON findings (tenant_id, assessment_id)
    WHERE assessment_id IS NOT NULL;
CREATE INDEX idx_findings_owner ON findings (tenant_id, internal_owner)
    WHERE status NOT IN ('verified_closed', 'risk_accepted', 'wont_fix');
CREATE INDEX idx_findings_controls ON findings USING GIN (affected_controls);
```

#### remediation_actions

```sql
CREATE TABLE remediation_actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    finding_id UUID NOT NULL REFERENCES findings(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    action_type TEXT NOT NULL CHECK (action_type IN (
        'implement_control', 'update_policy', 'patch_system', 'configure_setting',
        'conduct_training', 'engage_vendor', 'accept_risk', 'transfer_risk', 'other'
    )),
    status remediation_status NOT NULL DEFAULT 'pending',
    priority INT NOT NULL DEFAULT 0,
    assigned_to TEXT,
    due_date TIMESTAMPTZ,
    effort_estimate TEXT,
    -- effort_estimate: 'hours', 'days', 'weeks', 'months'
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMPTZ,
    verification_notes TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE remediation_actions ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON remediation_actions
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_remediation_actions_finding ON remediation_actions (tenant_id, finding_id);
CREATE INDEX idx_remediation_actions_status ON remediation_actions (tenant_id, status)
    WHERE status NOT IN ('verified', 'rejected');
```

#### remediation_evidence

```sql
CREATE TABLE remediation_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    remediation_action_id UUID NOT NULL REFERENCES remediation_actions(id) ON DELETE CASCADE,
    evidence_id UUID REFERENCES evidence(id),
    description TEXT,
    file_name TEXT,
    s3_key TEXT,
    ai_verification_result JSONB,
    -- ai_verification_result: {
    --   "addresses_finding": true,
    --   "confidence": 0.88,
    --   "reasoning": "...",
    --   "gaps_remaining": []
    -- }
    uploaded_by TEXT,
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE remediation_evidence ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON remediation_evidence
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_remediation_evidence_action ON remediation_evidence (tenant_id, remediation_action_id);
```

### 1.10 Communication Tables

#### notifications

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    channel notification_channel NOT NULL,
    category TEXT NOT NULL CHECK (category IN (
        'assessment', 'alert', 'finding', 'evidence', 'vendor',
        'scoring', 'system', 'reminder', 'escalation', 'report'
    )),
    priority TEXT NOT NULL DEFAULT 'normal'
        CHECK (priority IN ('critical', 'high', 'normal', 'low')),
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    html_body TEXT,
    reference_type TEXT,
    reference_id UUID,
    action_url TEXT,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    read_at TIMESTAMPTZ,
    delivered BOOLEAN NOT NULL DEFAULT FALSE,
    delivered_at TIMESTAMPTZ,
    delivery_error TEXT,
    external_message_id TEXT,
    -- external_message_id: SendGrid message ID, Slack ts, etc.
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON notifications
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_notifications_tenant_user ON notifications (tenant_id, user_id, created_at DESC);
CREATE INDEX idx_notifications_unread ON notifications (tenant_id, user_id)
    WHERE is_read = FALSE;
CREATE INDEX idx_notifications_delivery ON notifications (delivered, channel)
    WHERE delivered = FALSE;
```

#### notification_preferences

```sql
CREATE TABLE notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    channel notification_channel NOT NULL,
    is_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    min_priority TEXT DEFAULT 'normal'
        CHECK (min_priority IN ('critical', 'high', 'normal', 'low')),
    digest_frequency TEXT CHECK (digest_frequency IN ('immediate', 'hourly', 'daily', 'weekly')),
    quiet_hours_start TIME,
    quiet_hours_end TIME,
    quiet_hours_timezone TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, user_id, category, channel)
);

ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON notification_preferences
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_notification_prefs_user ON notification_preferences (tenant_id, user_id);
```

#### email_templates

```sql
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    -- NULL for system templates
    slug TEXT NOT NULL,
    name TEXT NOT NULL,
    subject_template TEXT NOT NULL,
    body_html_template TEXT NOT NULL,
    body_text_template TEXT NOT NULL,
    category TEXT NOT NULL,
    variables JSONB NOT NULL DEFAULT '[]',
    -- variables: [
    --   { "name": "vendor_name", "required": true, "description": "Vendor display name" },
    --   { "name": "deadline", "required": true, "description": "Assessment deadline date" },
    --   { "name": "portal_url", "required": true, "description": "Vendor portal assessment link" }
    -- ]
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    version INT NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, slug)
);

ALTER TABLE email_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY template_isolation ON email_templates
    USING (tenant_id IS NULL OR tenant_id = current_setting('app.current_tenant_id')::UUID);
```

#### communication_logs

```sql
CREATE TABLE communication_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID REFERENCES vendors(id),
    assessment_id UUID REFERENCES assessments(id),
    finding_id UUID REFERENCES findings(id),
    communication_type TEXT NOT NULL CHECK (communication_type IN (
        'assessment_distribution', 'reminder', 'escalation', 'finding_notification',
        'remediation_request', 'evidence_request', 'general', 'alert_notification'
    )),
    channel notification_channel NOT NULL,
    direction TEXT NOT NULL CHECK (direction IN ('outbound', 'inbound')),
    sender TEXT NOT NULL,
    recipients TEXT[] NOT NULL,
    subject TEXT,
    body_preview TEXT,
    template_id UUID REFERENCES email_templates(id),
    external_message_id TEXT,
    status TEXT NOT NULL DEFAULT 'sent'
        CHECK (status IN ('queued', 'sent', 'delivered', 'opened', 'bounced', 'failed')),
    opened_at TIMESTAMPTZ,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE communication_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON communication_logs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_communication_logs_vendor ON communication_logs (tenant_id, vendor_id, created_at DESC);
CREATE INDEX idx_communication_logs_assessment ON communication_logs (tenant_id, assessment_id)
    WHERE assessment_id IS NOT NULL;
```

### 1.11 Portal Tables

#### vendor_portal_access

```sql
CREATE TABLE vendor_portal_access (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    vendor_contact_id UUID REFERENCES vendor_contacts(id),
    access_token_hash TEXT NOT NULL UNIQUE,
    access_type TEXT NOT NULL CHECK (access_type IN ('token_link', 'authenticated')),
    email TEXT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    scoped_assessment_ids UUID[],
    -- NULL means access to all vendor's assessments for this tenant
    last_accessed_at TIMESTAMPTZ,
    last_accessed_ip INET,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE vendor_portal_access ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON vendor_portal_access
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_portal_access_token ON vendor_portal_access (access_token_hash)
    WHERE is_active = TRUE;
CREATE INDEX idx_portal_access_vendor ON vendor_portal_access (tenant_id, vendor_id);
```

#### trust_profiles

```sql
CREATE TABLE trust_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vendor_domain TEXT NOT NULL UNIQUE,
    vendor_name TEXT NOT NULL,
    description TEXT,
    industry TEXT,
    certifications JSONB NOT NULL DEFAULT '[]',
    -- certifications: [
    --   { "framework": "ISO 27001", "status": "certified", "valid_until": "2028-01-14", "scope": "..." },
    --   { "framework": "SOC 2 Type II", "status": "completed", "audit_period_end": "2026-03-31" }
    -- ]
    security_documentation JSONB NOT NULL DEFAULT '[]',
    -- security_documentation: [
    --   { "type": "soc2_report", "available": true, "nda_required": false, "s3_key": "..." },
    --   { "type": "pentest_summary", "available": true, "nda_required": true }
    -- ]
    sub_processors JSONB NOT NULL DEFAULT '[]',
    -- sub_processors: [
    --   { "name": "AWS", "service": "Cloud hosting", "data_types": ["all"], "location": "US" }
    -- ]
    data_processing_locations TEXT[],
    encryption_standards JSONB,
    trust_center_url TEXT,
    bug_bounty_url TEXT,
    privacy_policy_url TEXT,
    dpa_template_url TEXT,
    last_updated_by TEXT,
    published BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Trust profiles are NOT tenant-scoped -- they are global vendor profiles
CREATE INDEX idx_trust_profiles_domain ON trust_profiles (vendor_domain);
CREATE INDEX idx_trust_profiles_published ON trust_profiles (published) WHERE published = TRUE;
```

#### trust_profile_shares

```sql
CREATE TABLE trust_profile_shares (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    trust_profile_id UUID NOT NULL REFERENCES trust_profiles(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    vendor_id UUID NOT NULL REFERENCES vendors(id) ON DELETE CASCADE,
    shared_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    accepted_at TIMESTAMPTZ,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'accepted', 'rejected', 'revoked')),
    UNIQUE (trust_profile_id, tenant_id, vendor_id)
);

ALTER TABLE trust_profile_shares ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON trust_profile_shares
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_trust_shares_tenant ON trust_profile_shares (tenant_id, vendor_id);
CREATE INDEX idx_trust_shares_profile ON trust_profile_shares (trust_profile_id);
```

### 1.12 Report Tables

#### report_templates

```sql
CREATE TABLE report_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    report_type TEXT NOT NULL CHECK (report_type IN (
        'executive_summary', 'board_report', 'vendor_assessment',
        'regulatory_compliance', 'portfolio_risk', 'operational_analytics',
        'dora_register', 'hipaa_matrix', 'gdpr_art28', 'pci_dss_status',
        'custom'
    )),
    output_format report_format NOT NULL DEFAULT 'pdf',
    template_content JSONB NOT NULL,
    -- template_content:
    -- {
    --   "sections": [
    --     {
    --       "id": "executive_summary",
    --       "title": "Executive Summary",
    --       "type": "ai_narrative",
    --       "data_sources": ["portfolio_risk_summary"],
    --       "prompt_template": "Summarize the portfolio risk posture..."
    --     },
    --     {
    --       "id": "risk_heatmap",
    --       "title": "Risk Heatmap",
    --       "type": "chart",
    --       "chart_type": "heatmap",
    --       "data_sources": ["vendor_scores"]
    --     },
    --     {
    --       "id": "top_10_vendors",
    --       "title": "Top 10 Riskiest Vendors",
    --       "type": "table",
    --       "data_sources": ["vendor_scores_top_10"],
    --       "columns": ["name", "tier", "composite_score", "risk_tier", "open_findings"]
    --     }
    --   ],
    --   "branding": { "use_tenant_branding": true },
    --   "cover_page": true,
    --   "table_of_contents": true
    -- }
    is_system BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE report_templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY template_isolation ON report_templates
    USING (tenant_id IS NULL OR tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_report_templates_tenant ON report_templates (tenant_id);
CREATE INDEX idx_report_templates_type ON report_templates (report_type);
```

#### generated_reports

```sql
CREATE TABLE generated_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES report_templates(id),
    title TEXT NOT NULL,
    output_format report_format NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued', 'generating', 'completed', 'failed')),
    s3_key TEXT,
    file_size_bytes BIGINT,
    parameters JSONB NOT NULL DEFAULT '{}',
    -- parameters: { "vendor_ids": [...], "date_range": {...}, "frameworks": [...] }
    generation_started_at TIMESTAMPTZ,
    generation_completed_at TIMESTAMPTZ,
    generation_error TEXT,
    ai_sections_generated INT NOT NULL DEFAULT 0,
    reviewed BOOLEAN NOT NULL DEFAULT FALSE,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    generated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE generated_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON generated_reports
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_generated_reports_tenant ON generated_reports (tenant_id, created_at DESC);
CREATE INDEX idx_generated_reports_status ON generated_reports (status)
    WHERE status IN ('queued', 'generating');
```

#### dashboard_configs

```sql
CREATE TABLE dashboard_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id),
    -- NULL user_id means tenant-level default dashboard
    dashboard_type TEXT NOT NULL CHECK (dashboard_type IN (
        'executive', 'operational', 'compliance', 'vendor_detail', 'custom'
    )),
    name TEXT NOT NULL,
    layout JSONB NOT NULL,
    -- layout:
    -- {
    --   "widgets": [
    --     {
    --       "id": "portfolio_risk",
    --       "type": "metric_card",
    --       "position": { "x": 0, "y": 0, "w": 4, "h": 2 },
    --       "config": { "metric": "avg_composite_score", "trend_period": "90d" }
    --     },
    --     {
    --       "id": "risk_heatmap",
    --       "type": "heatmap",
    --       "position": { "x": 4, "y": 0, "w": 8, "h": 4 },
    --       "config": { "x_axis": "likelihood", "y_axis": "impact", "data": "vendor_inherent_risk" }
    --     }
    --   ],
    --   "filters": { "tier": null, "status": null, "framework": null },
    --   "refresh_interval_seconds": 300
    -- }
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

ALTER TABLE dashboard_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON dashboard_configs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_dashboard_configs_tenant ON dashboard_configs (tenant_id, dashboard_type);
CREATE INDEX idx_dashboard_configs_user ON dashboard_configs (tenant_id, user_id);
```

### 1.13 Audit Tables

#### audit_logs (partitioned by month)

```sql
CREATE TABLE audit_logs (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    actor_id UUID NOT NULL,
    actor_type actor_type NOT NULL,
    action TEXT NOT NULL,
    -- action format: '{resource}.{verb}' e.g. 'vendor.created', 'assessment.submitted',
    -- 'evidence.uploaded', 'score.overridden', 'user.login', 'config.updated',
    -- 'ai_pipeline.executed', 'report.generated', 'portal.accessed'
    resource_type TEXT NOT NULL,
    resource_id UUID,
    changes JSONB,
    -- changes: { "field_name": { "old": "value", "new": "value" } }
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    request_id TEXT,
    -- request_id: correlation ID for tracing across services
    ai_confidence NUMERIC(3,2),
    ai_pipeline_id TEXT,
    duration_ms INT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create monthly partitions (example for 2026)
CREATE TABLE audit_logs_2026_01 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE audit_logs_2026_02 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');
CREATE TABLE audit_logs_2026_03 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');
CREATE TABLE audit_logs_2026_04 PARTITION OF audit_logs
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
-- ... continue for each month; automate partition creation via cron job

-- RLS on partitioned table
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON audit_logs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

-- NO UPDATE or DELETE permissions on audit_logs for any application role
-- GRANT INSERT, SELECT ON audit_logs TO velora_app;

CREATE INDEX idx_audit_logs_tenant_time ON audit_logs (tenant_id, created_at DESC);
CREATE INDEX idx_audit_logs_actor ON audit_logs (tenant_id, actor_id, created_at DESC);
CREATE INDEX idx_audit_logs_resource ON audit_logs (tenant_id, resource_type, resource_id, created_at DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs (tenant_id, action, created_at DESC);
CREATE INDEX idx_audit_logs_request ON audit_logs (request_id) WHERE request_id IS NOT NULL;
```

### 1.14 Config Tables

#### tenant_configs

```sql
CREATE TABLE tenant_configs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    config_type TEXT NOT NULL CHECK (config_type IN (
        'scoring', 'workflows', 'escalation', 'notifications',
        'roles', 'branding', 'integrations', 'monitoring', 'sso'
    )),
    config_data JSONB NOT NULL,
    -- config_data schema varies by config_type; full schemas in Section 6
    json_schema_version TEXT NOT NULL DEFAULT '1.0',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    version INT NOT NULL DEFAULT 1,
    previous_version_id UUID REFERENCES tenant_configs(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (tenant_id, config_type) -- one active config per type per tenant
);

ALTER TABLE tenant_configs ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON tenant_configs
    USING (tenant_id = current_setting('app.current_tenant_id')::UUID);

CREATE INDEX idx_tenant_configs_tenant ON tenant_configs (tenant_id, config_type);
```

---

## 2. API Specification

All endpoints are prefixed with `/api/v1`. Authentication is via JWT Bearer token unless otherwise noted. Responses follow RFC 7807 Problem Details for errors. Pagination uses cursor-based pagination via `cursor` and `limit` query parameters.

### Standard Response Envelope

```python
class PaginatedResponse(BaseModel):
    data: list[Any]
    cursor: str | None = None
    has_more: bool = False
    total_count: int | None = None

class ErrorResponse(BaseModel):
    type: str              # error URI
    title: str             # human-readable summary
    status: int            # HTTP status code
    detail: str            # human-readable explanation
    instance: str | None   # URI of the specific occurrence
    errors: list[dict] | None  # field-level validation errors
```

### 2.1 Auth Module -- `/api/v1/auth`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `POST` | `/auth/login` | Email/password login (non-SSO tenants) | `{ "email": str, "password": str, "tenant_slug": str }` | `{ "access_token": str, "refresh_token": str, "expires_in": int, "user": UserResponse }` | None | 10/min per IP |
| `GET` | `/auth/sso/init` | Initiate SSO flow | Query: `tenant_slug`, `redirect_uri` | Redirect to IdP | None | 20/min per IP |
| `POST` | `/auth/sso/callback` | SSO callback (SAML assertion or OIDC code) | `{ "saml_response": str }` or `{ "code": str, "state": str }` | `{ "access_token": str, "refresh_token": str, "user": UserResponse }` | None | 20/min per IP |
| `POST` | `/auth/refresh` | Refresh access token | `{ "refresh_token": str }` | `{ "access_token": str, "expires_in": int }` | Refresh token | 30/min per user |
| `POST` | `/auth/logout` | Revoke session | `{}` | `204 No Content` | Bearer | 10/min per user |
| `POST` | `/auth/mfa/setup` | Initialize MFA setup | `{}` | `{ "secret": str, "qr_code_uri": str, "recovery_codes": list[str] }` | Bearer | 5/min per user |
| `POST` | `/auth/mfa/verify` | Verify MFA code | `{ "code": str }` | `{ "verified": bool }` | Bearer | 10/min per user |
| `GET` | `/auth/me` | Get current user profile | -- | `UserResponse` | Bearer | 60/min |

**UserResponse**:
```python
class UserResponse(BaseModel):
    id: UUID
    email: str
    full_name: str
    display_name: str | None
    avatar_url: str | None
    roles: list[RoleResponse]
    permissions: list[str]
    tenant_id: UUID
    tenant_name: str
    mfa_enabled: bool
    last_login_at: datetime | None
```

### 2.2 Tenants Module -- `/api/v1/tenants`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/tenants/current` | Get current tenant | -- | `TenantResponse` | Bearer (any) | 60/min |
| `PUT` | `/tenants/current` | Update tenant profile | `TenantUpdate` | `TenantResponse` | `admin:config` | 20/min |
| `GET` | `/tenants/current/config/{config_type}` | Get tenant config by type | -- | `TenantConfigResponse` | `admin:config` | 60/min |
| `PUT` | `/tenants/current/config/{config_type}` | Update tenant config | `TenantConfigUpdate` | `TenantConfigResponse` | `admin:config` | 20/min |
| `GET` | `/tenants/current/branding` | Get branding config | -- | `BrandingResponse` | Bearer (any) | 60/min |
| `PUT` | `/tenants/current/branding` | Update branding | `BrandingUpdate` | `BrandingResponse` | `admin:config` | 10/min |
| `POST` | `/tenants/setup` | Complete onboarding wizard | `OnboardingWizard` | `TenantResponse` | `admin:config` | 5/min |

**Key models**:
```python
class TenantUpdate(BaseModel):
    name: str | None
    industry: str | None
    employee_count_range: str | None
    regulatory_exposure: list[str] | None
    settings: dict | None

class OnboardingWizard(BaseModel):
    company_profile: dict    # name, domain, industry, size
    frameworks: list[UUID]   # selected framework IDs
    scoring_model: dict      # default scoring configuration
    team_roles: list[dict]   # initial user invites with roles

class BrandingUpdate(BaseModel):
    logo_url: str | None
    primary_color: str | None
    secondary_color: str | None
    portal_domain: str | None
    portal_title: str | None
```

### 2.3 Vendors Module -- `/api/v1/vendors`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/vendors` | List vendors | Query: `status`, `tier`, `risk_tier`, `search`, `tags`, `sort_by`, `cursor`, `limit` | `PaginatedResponse[VendorSummary]` | `vendors:read` | 60/min |
| `POST` | `/vendors` | Create vendor | `VendorCreate` | `VendorResponse` | `vendors:write` | 30/min |
| `GET` | `/vendors/{id}` | Get vendor detail (360-degree view) | -- | `VendorDetailResponse` | `vendors:read` | 60/min |
| `PUT` | `/vendors/{id}` | Update vendor | `VendorUpdate` | `VendorResponse` | `vendors:write` | 30/min |
| `DELETE` | `/vendors/{id}` | Soft-delete vendor | -- | `204 No Content` | `vendors:delete` | 10/min |
| `POST` | `/vendors/bulk-import` | Bulk import from CSV | Multipart: CSV file | `{ "job_id": str, "total_rows": int, "valid_rows": int, "errors": list }` | `vendors:write` | 5/min |
| `POST` | `/vendors/{id}/enrich` | Trigger enrichment | `{ "sources": list[str] }` (optional) | `{ "workflow_run_id": str }` | `vendors:write` | 10/min per vendor |
| `POST` | `/vendors/{id}/calculate-tier` | Recalculate inherent risk tier | `{}` | `{ "previous_tier": str, "new_tier": str, "score": float }` | `vendors:write` | 20/min |
| `GET` | `/vendors/{id}/enrichment` | Get enrichment data | -- | `list[EnrichmentResponse]` | `vendors:read` | 60/min |
| `GET` | `/vendors/{id}/timeline` | Get vendor risk timeline | Query: `event_type`, `from_date`, `to_date`, `cursor`, `limit` | `PaginatedResponse[TimelineEvent]` | `vendors:read` | 60/min |
| `GET` | `/vendors/{id}/relationships` | Get Nth-party map | -- | `list[VendorRelationship]` | `vendors:read` | 60/min |
| `POST` | `/vendors/{id}/relationships` | Add relationship | `VendorRelationshipCreate` | `VendorRelationship` | `vendors:write` | 20/min |
| `GET` | `/vendors/{id}/contacts` | List vendor contacts | -- | `list[VendorContact]` | `vendors:read` | 60/min |
| `POST` | `/vendors/{id}/contacts` | Add contact | `VendorContactCreate` | `VendorContact` | `vendors:write` | 20/min |
| `PUT` | `/vendors/{id}/contacts/{contact_id}` | Update contact | `VendorContactUpdate` | `VendorContact` | `vendors:write` | 20/min |

**Key models**:
```python
class VendorCreate(BaseModel):
    name: str
    domain: str | None
    website: str | None
    industry: str | None
    description: str | None
    data_sensitivity: DataSensitivity | None
    access_level: str | None
    business_criticality: int | None  # 1-5
    regulatory_exposure: list[str] | None
    contract_start_date: date | None
    contract_end_date: date | None
    contract_value: Decimal | None
    tags: list[str] | None
    contacts: list[VendorContactCreate] | None
    auto_enrich: bool = True

class VendorDetailResponse(BaseModel):
    vendor: VendorResponse
    scores: VendorScoreResponse | None
    recent_assessments: list[AssessmentSummary]
    recent_alerts: list[AlertSummary]
    open_findings: list[FindingSummary]
    evidence_summary: EvidenceSummaryResponse
    enrichment: list[EnrichmentResponse]
    contacts: list[VendorContact]
    relationships: list[VendorRelationship]
    timeline: list[TimelineEvent]
```

### 2.4 Assessments Module -- `/api/v1/assessments`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/assessments` | List assessments | Query: `vendor_id`, `status`, `assigned_to`, `sort_by`, `cursor`, `limit` | `PaginatedResponse[AssessmentSummary]` | `assessments:read` | 60/min |
| `POST` | `/assessments` | Create assessment | `AssessmentCreate` | `AssessmentResponse` | `assessments:write` | 20/min |
| `GET` | `/assessments/{id}` | Get assessment detail | -- | `AssessmentDetailResponse` | `assessments:read` | 60/min |
| `PUT` | `/assessments/{id}` | Update assessment | `AssessmentUpdate` | `AssessmentResponse` | `assessments:write` | 20/min |
| `POST` | `/assessments/{id}/distribute` | Distribute to vendor | `{ "vendor_contact_id": UUID, "deadline": datetime, "message": str }` | `{ "distribution_id": str, "portal_url": str }` | `assessments:distribute` | 10/min |
| `POST` | `/assessments/{id}/submit` | Vendor submits responses | `{ "responses": list[ResponseSubmission] }` | `AssessmentResponse` | `assessments:write` or portal | 5/min |
| `POST` | `/assessments/{id}/start-review` | Begin review process | `{ "reviewer_id": UUID }` | `AssessmentResponse` | `assessments:write` | 10/min |
| `POST` | `/assessments/{id}/complete` | Complete assessment | `{ "notes": str }` | `AssessmentResponse` | `assessments:approve` | 10/min |
| `POST` | `/assessments/{id}/cancel` | Cancel assessment | `{ "reason": str }` | `AssessmentResponse` | `assessments:write` | 10/min |
| `GET` | `/assessments/{id}/responses` | Get all responses | Query: `review_status`, `is_flagged` | `list[ResponseDetail]` | `assessments:read` | 60/min |
| `PUT` | `/assessments/{id}/responses/{response_id}` | Review a response | `ResponseReview` | `ResponseDetail` | `assessments:write` | 60/min |
| `GET` | `/assessments/{id}/findings` | Get assessment findings | -- | `list[FindingResponse]` | `assessments:read` | 60/min |
| `GET` | `/assessments/review-queue` | Get items needing review | Query: `priority`, `assigned_to`, `cursor`, `limit` | `PaginatedResponse[ReviewQueueItem]` | `assessments:write` | 60/min |
| `GET` | `/assessments/templates` | List available templates | Query: `questionnaire_type`, `tier` | `list[TemplateResponse]` | `assessments:read` | 60/min |
| `POST` | `/assessments/templates` | Create custom template | `TemplateCreate` | `TemplateResponse` | `admin:config` | 10/min |

**Key models**:
```python
class AssessmentCreate(BaseModel):
    vendor_id: UUID
    template_id: UUID | None  # auto-select if None
    title: str | None
    assessment_type: str = "periodic"
    applicable_frameworks: list[UUID] | None
    auto_prefill: bool = True
    deadline_days: int | None

class ResponseReview(BaseModel):
    review_status: str  # 'accepted', 'modified', 'rejected', 'flagged'
    modified_value: str | None
    modified_score: float | None
    comment: str | None

class ResponseSubmission(BaseModel):
    question_id: UUID
    response_value: str | None
    response_text: str | None
    response_data: dict | None
    comment: str | None
```

### 2.5 Frameworks Module -- `/api/v1/frameworks`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/frameworks` | List frameworks | Query: `status`, `search` | `list[FrameworkSummary]` | `frameworks:read` | 60/min |
| `GET` | `/frameworks/{id}` | Get framework detail | -- | `FrameworkDetailResponse` | `frameworks:read` | 60/min |
| `GET` | `/frameworks/{id}/clauses` | Get clause tree | Query: `depth`, `domain`, `search` | `list[ClauseResponse]` | `frameworks:read` | 60/min |
| `GET` | `/frameworks/{id}/clauses/{clause_id}` | Get single clause | -- | `ClauseDetailResponse` | `frameworks:read` | 60/min |
| `GET` | `/frameworks/{id}/clauses/{clause_id}/mappings` | Get cross-framework mappings | -- | `list[MappingResponse]` | `frameworks:read` | 60/min |
| `GET` | `/frameworks/{id}/question-bank` | Get associated questions | Query: `domain`, `cursor`, `limit` | `PaginatedResponse[QuestionResponse]` | `frameworks:read` | 60/min |
| `GET` | `/frameworks/unified-controls` | Get deduplicated controls across frameworks | Query: `framework_ids` | `list[UnifiedControl]` | `frameworks:read` | 30/min |
| `POST` | `/frameworks/{id}/mappings` | Create custom mapping | `MappingCreate` | `MappingResponse` | `frameworks:manage` | 20/min |
| `GET` | `/frameworks/{id}/versions` | Get version history | -- | `list[FrameworkVersion]` | `frameworks:read` | 60/min |
| `GET` | `/frameworks/{id}/diff/{version_id}` | Get diff between versions | -- | `FrameworkDiff` | `frameworks:read` | 30/min |

### 2.6 Scoring Module -- `/api/v1/scoring`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/scoring/models` | List scoring models | -- | `list[ScoringModelResponse]` | `scoring:read` | 60/min |
| `POST` | `/scoring/models` | Create scoring model | `ScoringModelCreate` | `ScoringModelResponse` | `scoring:configure` | 10/min |
| `PUT` | `/scoring/models/{id}` | Update scoring model | `ScoringModelUpdate` | `ScoringModelResponse` | `scoring:configure` | 10/min |
| `POST` | `/scoring/calculate/{vendor_id}` | Trigger score recalculation | `{ "reason": str }` | `VendorScoreResponse` | `scoring:configure` | 20/min |
| `POST` | `/scoring/calculate/bulk` | Bulk recalculate | `{ "vendor_ids": list[UUID], "reason": str }` | `{ "job_id": str }` | `scoring:configure` | 5/min |
| `GET` | `/scoring/vendors/{vendor_id}` | Get current vendor score | -- | `VendorScoreResponse` | `scoring:read` | 60/min |
| `GET` | `/scoring/vendors/{vendor_id}/history` | Get score history | Query: `from_date`, `to_date`, `cursor`, `limit` | `PaginatedResponse[ScoreHistoryEntry]` | `scoring:read` | 60/min |
| `POST` | `/scoring/vendors/{vendor_id}/override` | Create score override | `ScoreOverrideCreate` | `ScoreOverrideResponse` | `scoring:override` | 10/min |
| `DELETE` | `/scoring/vendors/{vendor_id}/override/{id}` | Remove override | -- | `204 No Content` | `scoring:override` | 10/min |
| `GET` | `/scoring/portfolio` | Get portfolio risk aggregation | Query: `group_by` (tier, industry, framework) | `PortfolioRiskResponse` | `scoring:read` | 30/min |
| `POST` | `/scoring/fair/{vendor_id}` | Calculate FAIR estimate | `FAIRInput` | `FAIRResponse` | `scoring:read` | 10/min |
| `GET` | `/scoring/normalization` | Get normalization configs | -- | `list[NormalizationConfig]` | `scoring:configure` | 60/min |

**Key models**:
```python
class ScoreOverrideCreate(BaseModel):
    override_type: str
    dimension_name: str | None
    override_value: Decimal
    override_tier: str | None
    justification: str  # required
    expires_at: datetime | None

class FAIRInput(BaseModel):
    scenario: str
    threat_event_frequency: float | None  # auto-estimated if None
    vulnerability: float | None
    primary_loss: float | None
    secondary_loss: float | None
    confidence_level: float = 0.9

class FAIRResponse(BaseModel):
    annual_loss_expectancy: Decimal
    loss_event_frequency: float
    loss_magnitude: Decimal
    primary_loss: Decimal
    secondary_loss: Decimal
    confidence_interval: dict  # { "low": Decimal, "high": Decimal, "percentile": int }
    scenario: str
    inputs_used: dict
    calculated_at: datetime
```

### 2.7 Monitoring Module -- `/api/v1/monitoring`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/monitoring/config` | Get monitoring configs | Query: `vendor_id`, `source` | `list[MonitoringConfigResponse]` | `monitoring:configure` | 60/min |
| `PUT` | `/monitoring/config/{id}` | Update monitoring config | `MonitoringConfigUpdate` | `MonitoringConfigResponse` | `monitoring:configure` | 20/min |
| `GET` | `/monitoring/alerts` | List alerts | Query: `status`, `priority`, `vendor_id`, `assigned_to`, `cursor`, `limit` | `PaginatedResponse[AlertResponse]` | `monitoring:read` | 60/min |
| `GET` | `/monitoring/alerts/{id}` | Get alert detail | -- | `AlertDetailResponse` | `monitoring:read` | 60/min |
| `PUT` | `/monitoring/alerts/{id}/acknowledge` | Acknowledge alert | `{ "notes": str }` | `AlertResponse` | `monitoring:acknowledge` | 30/min |
| `PUT` | `/monitoring/alerts/{id}/resolve` | Resolve alert | `{ "resolution_notes": str }` | `AlertResponse` | `monitoring:acknowledge` | 30/min |
| `PUT` | `/monitoring/alerts/{id}/suppress` | Suppress alert | `{ "reason": str, "expires_at": datetime }` | `AlertResponse` | `monitoring:acknowledge` | 20/min |
| `PUT` | `/monitoring/alerts/{id}/assign` | Assign alert | `{ "user_id": UUID }` | `AlertResponse` | `monitoring:acknowledge` | 30/min |
| `POST` | `/monitoring/alerts/{id}/trigger-assessment` | Trigger fast-track assessment from alert | `{ "template_id": UUID }` | `AssessmentResponse` | `assessments:write` | 5/min |
| `GET` | `/monitoring/signals` | List raw signals | Query: `vendor_id`, `source`, `severity`, `cursor`, `limit` | `PaginatedResponse[SignalResponse]` | `monitoring:read` | 60/min |
| `GET` | `/monitoring/vendors/{vendor_id}/timeline` | Get vendor monitoring timeline | Query: `from_date`, `to_date` | `list[TimelineEvent]` | `monitoring:read` | 60/min |
| `GET` | `/monitoring/alert-rules` | List alert rules | -- | `list[AlertRuleResponse]` | `monitoring:configure` | 60/min |
| `POST` | `/monitoring/alert-rules` | Create alert rule | `AlertRuleCreate` | `AlertRuleResponse` | `monitoring:configure` | 10/min |
| `PUT` | `/monitoring/alert-rules/{id}` | Update alert rule | `AlertRuleUpdate` | `AlertRuleResponse` | `monitoring:configure` | 10/min |

### 2.8 Evidence Module -- `/api/v1/evidence`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `POST` | `/evidence/upload-url` | Get presigned upload URL | `{ "vendor_id": UUID, "assessment_id": UUID, "file_name": str, "mime_type": str, "file_size": int }` | `{ "upload_url": str, "evidence_id": UUID, "expires_in": int }` | `evidence:upload` | 30/min |
| `POST` | `/evidence/{id}/process` | Trigger parsing pipeline | `{}` | `{ "workflow_run_id": str }` | `evidence:upload` | 20/min |
| `GET` | `/evidence` | List evidence | Query: `vendor_id`, `assessment_id`, `document_type`, `status`, `freshness`, `cursor`, `limit` | `PaginatedResponse[EvidenceSummary]` | `evidence:read` | 60/min |
| `GET` | `/evidence/{id}` | Get evidence detail | -- | `EvidenceDetailResponse` | `evidence:read` | 60/min |
| `GET` | `/evidence/{id}/download-url` | Get presigned download URL | -- | `{ "download_url": str, "expires_in": int }` | `evidence:read` | 60/min |
| `GET` | `/evidence/{id}/mappings` | Get control mappings | -- | `list[EvidenceControlMapping]` | `evidence:read` | 60/min |
| `PUT` | `/evidence/{id}/mappings/{mapping_id}` | Verify/modify mapping | `MappingVerification` | `EvidenceControlMapping` | `evidence:upload` | 30/min |
| `GET` | `/evidence/{id}/extractions` | Get parsed extractions | -- | `list[ExtractionResponse]` | `evidence:read` | 60/min |
| `GET` | `/evidence/{id}/versions` | Get version history | -- | `list[EvidenceVersion]` | `evidence:read` | 60/min |
| `GET` | `/evidence/expiring` | Get expiring evidence | Query: `days_ahead` (default 90) | `list[EvidenceSummary]` | `evidence:read` | 30/min |
| `DELETE` | `/evidence/{id}` | Soft-delete evidence | -- | `204 No Content` | `evidence:delete` | 10/min |

### 2.9 Reports Module -- `/api/v1/reports`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `POST` | `/reports/generate` | Generate report | `ReportGenerateRequest` | `{ "report_id": UUID, "status": str }` | `reports:generate` | 10/min |
| `GET` | `/reports` | List generated reports | Query: `report_type`, `status`, `cursor`, `limit` | `PaginatedResponse[ReportSummary]` | `reports:read` | 60/min |
| `GET` | `/reports/{id}` | Get report detail | -- | `ReportDetailResponse` | `reports:read` | 60/min |
| `GET` | `/reports/{id}/download` | Download report file | -- | `{ "download_url": str }` | `reports:read` | 30/min |
| `GET` | `/reports/templates` | List report templates | Query: `report_type` | `list[ReportTemplateResponse]` | `reports:read` | 60/min |
| `POST` | `/reports/templates` | Create custom template | `ReportTemplateCreate` | `ReportTemplateResponse` | `admin:config` | 10/min |
| `GET` | `/reports/dashboards` | Get dashboard config | Query: `dashboard_type` | `DashboardConfigResponse` | `reports:read` | 60/min |
| `PUT` | `/reports/dashboards/{id}` | Update dashboard layout | `DashboardConfigUpdate` | `DashboardConfigResponse` | `reports:read` | 20/min |
| `GET` | `/reports/dashboards/data/{dashboard_type}` | Get dashboard data | Query: `filters` | `DashboardDataResponse` | `reports:read` | 60/min |
| `POST` | `/reports/export/{format}` | Export data | `ExportRequest` | `{ "job_id": str }` | `reports:generate` | 10/min |

**Key models**:
```python
class ReportGenerateRequest(BaseModel):
    template_id: UUID
    title: str | None
    output_format: ReportFormat = ReportFormat.pdf
    parameters: dict = {}
    # parameters: { "vendor_ids": [...], "date_range": {...}, "frameworks": [...] }
```

### 2.10 Communications Module -- `/api/v1/communications`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/communications/templates` | List email templates | Query: `category` | `list[EmailTemplateResponse]` | `admin:config` | 60/min |
| `POST` | `/communications/templates` | Create template | `EmailTemplateCreate` | `EmailTemplateResponse` | `admin:config` | 10/min |
| `PUT` | `/communications/templates/{id}` | Update template | `EmailTemplateUpdate` | `EmailTemplateResponse` | `admin:config` | 10/min |
| `POST` | `/communications/send` | Send communication | `SendRequest` | `{ "message_id": str, "status": str }` | `vendors:write` | 30/min |
| `GET` | `/communications/logs` | Get communication logs | Query: `vendor_id`, `assessment_id`, `channel`, `cursor`, `limit` | `PaginatedResponse[CommLogResponse]` | `vendors:read` | 60/min |
| `GET` | `/communications/notifications` | Get user notifications | Query: `is_read`, `category`, `cursor`, `limit` | `PaginatedResponse[NotificationResponse]` | Bearer (any) | 60/min |
| `PUT` | `/communications/notifications/{id}/read` | Mark notification read | -- | `204 No Content` | Bearer (any) | 120/min |
| `PUT` | `/communications/notifications/read-all` | Mark all read | -- | `{ "count": int }` | Bearer (any) | 10/min |
| `GET` | `/communications/preferences` | Get notification preferences | -- | `list[NotificationPreference]` | Bearer (any) | 60/min |
| `PUT` | `/communications/preferences` | Update preferences | `list[NotificationPreferenceUpdate]` | `list[NotificationPreference]` | Bearer (any) | 10/min |
| `GET` | `/communications/escalation-rules` | Get escalation rules | -- | `list[EscalationRule]` | `admin:config` | 60/min |
| `PUT` | `/communications/escalation-rules` | Update escalation rules | `list[EscalationRuleUpdate]` | `list[EscalationRule]` | `admin:config` | 10/min |

### 2.11 Portal Module -- `/api/v1/portal`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/portal/assessments` | List vendor's assessments | -- | `list[PortalAssessmentSummary]` | Portal token | 60/min |
| `GET` | `/portal/assessments/{id}` | Get assessment with questions | -- | `PortalAssessmentDetail` | Portal token | 60/min |
| `POST` | `/portal/assessments/{id}/responses` | Submit responses | `list[PortalResponseSubmission]` | `PortalSubmissionResult` | Portal token | 10/min |
| `POST` | `/portal/assessments/{id}/evidence` | Upload evidence | Multipart or `{ "upload_url_request": ... }` | `PortalEvidenceResponse` | Portal token | 20/min |
| `GET` | `/portal/findings` | List findings for vendor | -- | `list[PortalFindingResponse]` | Portal token | 60/min |
| `POST` | `/portal/findings/{id}/remediation` | Submit remediation evidence | Multipart | `RemediationSubmissionResult` | Portal token | 20/min |
| `GET` | `/portal/trust-profile` | Get own trust profile | -- | `TrustProfileResponse` | Portal auth | 60/min |
| `PUT` | `/portal/trust-profile` | Update trust profile | `TrustProfileUpdate` | `TrustProfileResponse` | Portal auth | 10/min |
| `POST` | `/portal/trust-profile/publish` | Publish trust profile | -- | `TrustProfileResponse` | Portal auth | 5/min |
| `GET` | `/portal/trust-profile/shares` | List organizations with access | -- | `list[ShareResponse]` | Portal auth | 60/min |

### 2.12 Admin Module -- `/api/v1/admin`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `GET` | `/admin/users` | List users | Query: `status`, `role`, `search`, `cursor`, `limit` | `PaginatedResponse[UserResponse]` | `admin:users` | 60/min |
| `POST` | `/admin/users` | Create/invite user | `UserCreate` | `UserResponse` | `admin:users` | 20/min |
| `PUT` | `/admin/users/{id}` | Update user | `UserUpdate` | `UserResponse` | `admin:users` | 20/min |
| `DELETE` | `/admin/users/{id}` | Deactivate user | -- | `204 No Content` | `admin:users` | 10/min |
| `POST` | `/admin/users/{id}/roles` | Assign role | `{ "role_id": UUID }` | `UserResponse` | `admin:users` | 20/min |
| `DELETE` | `/admin/users/{id}/roles/{role_id}` | Remove role | -- | `204 No Content` | `admin:users` | 20/min |
| `GET` | `/admin/roles` | List roles | -- | `list[RoleResponse]` | `admin:users` | 60/min |
| `POST` | `/admin/roles` | Create custom role | `RoleCreate` | `RoleResponse` | `admin:users` | 10/min |
| `PUT` | `/admin/roles/{id}` | Update role | `RoleUpdate` | `RoleResponse` | `admin:users` | 10/min |
| `GET` | `/admin/audit-logs` | Query audit logs | Query: `actor_id`, `action`, `resource_type`, `resource_id`, `from_date`, `to_date`, `cursor`, `limit` | `PaginatedResponse[AuditLogEntry]` | `admin:audit` | 30/min |
| `POST` | `/admin/audit-logs/export` | Export audit logs | `{ "from_date": datetime, "to_date": datetime, "format": str }` | `{ "job_id": str }` | `admin:audit` | 5/min |
| `GET` | `/admin/integrations` | List integrations | -- | `list[IntegrationResponse]` | `admin:integrations` | 60/min |
| `PUT` | `/admin/integrations/{id}` | Configure integration | `IntegrationConfig` | `IntegrationResponse` | `admin:integrations` | 10/min |
| `POST` | `/admin/integrations/{id}/test` | Test integration connectivity | -- | `{ "status": str, "details": str }` | `admin:integrations` | 10/min |

### 2.13 AI Module -- `/api/v1/ai`

| Method | Path | Description | Request Body | Response | Auth | Rate Limit |
|--------|------|-------------|--------------|----------|------|------------|
| `POST` | `/ai/enrich` | AI vendor enrichment | `{ "vendor_id": UUID, "sources": list[str] }` | `{ "workflow_run_id": str }` | `vendors:write` | 10/min |
| `POST` | `/ai/parse-evidence` | Trigger evidence parsing | `{ "evidence_id": UUID }` | `{ "workflow_run_id": str }` | `evidence:upload` | 20/min |
| `POST` | `/ai/auto-fill` | Pre-fill assessment responses | `{ "assessment_id": UUID }` | `{ "prefilled_count": int, "high_confidence": int, "low_confidence": int }` | `assessments:write` | 5/min |
| `POST` | `/ai/risk-query` | Natural language risk Q&A | `{ "query": str, "context": dict }` | `{ "answer": str, "citations": list, "confidence": float, "sql_generated": str }` | `ai:query` | 20/min |
| `GET` | `/ai/review-queue` | Get AI items needing review | Query: `pipeline`, `confidence_below`, `cursor`, `limit` | `PaginatedResponse[ReviewQueueItem]` | `assessments:write` | 60/min |
| `PUT` | `/ai/review-queue/{id}` | Submit review decision | `{ "decision": str, "modified_value": Any, "comment": str }` | `ReviewQueueItem` | `assessments:write` | 60/min |
| `POST` | `/ai/framework-map` | AI-assisted mapping | `{ "source_clause_id": UUID, "target_framework_id": UUID }` | `list[SuggestedMapping]` | `frameworks:manage` | 10/min |
| `GET` | `/ai/usage` | Get AI usage stats | Query: `from_date`, `to_date` | `AIUsageResponse` | `admin:config` | 30/min |

---

## 3. State Machine Definitions

### 3.1 Vendor Lifecycle

```
States: discovered -> classified -> assessing -> active -> monitoring -> reassessing -> offboarding -> offboarded -> archived

Transitions:
  discovered -> classified
    Guard: inherent risk tier calculated
    Action: set tier, update risk_score
    Trigger: auto after enrichment completes

  classified -> assessing
    Guard: assessment created and distributed
    Action: create initial assessment
    Trigger: manual or auto based on tier

  assessing -> active
    Guard: initial assessment completed with acceptable risk
    Action: onboarding_completed_at = now(), start monitoring schedule
    Trigger: assessment completion + risk within threshold

  assessing -> classified
    Guard: assessment shows unacceptable risk, vendor fails onboarding
    Action: log rejection, notify stakeholders
    Trigger: manual decision

  active -> monitoring
    Guard: active vendor with monitoring configured
    Action: enroll in tier-based monitoring schedule
    Trigger: automatic after activation

  monitoring -> reassessing
    Guard: reassessment triggered (schedule, event, alert)
    Action: create reassessment, pause certain monitoring alerts
    Trigger: scheduled date, alert event, contract renewal, manual

  reassessing -> monitoring
    Guard: reassessment completed
    Action: update scores, update next_assessment_due, resume monitoring
    Trigger: assessment completion

  reassessing -> offboarding
    Guard: reassessment reveals unacceptable risk, decision to offboard
    Action: initiate offboarding workflow
    Trigger: manual decision

  monitoring -> offboarding
    Guard: vendor contract ending or business decision
    Action: initiate offboarding checklist
    Trigger: manual or contract_end_date approaching

  active -> offboarding
    Guard: immediate offboarding required (critical incident)
    Action: initiate emergency offboarding
    Trigger: manual (P0 alert response)

  offboarding -> offboarded
    Guard: all offboarding checklist items completed
    Action: revoke all access, final risk snapshot, archive communications
    Trigger: checklist completion

  offboarded -> archived
    Guard: retention period actions complete
    Action: archive vendor data per retention policy
    Trigger: manual or scheduled

  discovered -> archived
    Guard: vendor determined to be irrelevant
    Action: archive
    Trigger: manual
```

### 3.2 Assessment Lifecycle

```
States: draft -> distributed -> in_progress -> submitted -> under_review -> completed
                                                                          -> cancelled (from any state except completed)

Transitions:
  draft -> distributed
    Guard: vendor contact assigned, deadline set, at least one framework selected
    Action: send portal link to vendor, start SLA timer, schedule reminders
    Trigger: POST /assessments/{id}/distribute

  draft -> cancelled
    Guard: none
    Action: log cancellation reason
    Trigger: manual

  distributed -> in_progress
    Guard: vendor opens assessment in portal or first response received
    Action: update status, log portal access
    Trigger: automatic on first vendor interaction

  distributed -> cancelled
    Guard: none
    Action: log cancellation, notify vendor
    Trigger: manual

  in_progress -> submitted
    Guard: all required questions answered (or explicitly skipped with justification)
    Action: trigger AI validation, calculate preliminary scores, notify reviewer
    Trigger: vendor clicks submit in portal

  in_progress -> cancelled
    Guard: none
    Action: log, notify vendor
    Trigger: manual

  submitted -> under_review
    Guard: reviewer assigned
    Action: AI cross-validates responses vs evidence, flags inconsistencies, routes low-confidence items to review queue
    Trigger: automatic after submission or manual assignment

  submitted -> cancelled
    Guard: none
    Action: log
    Trigger: manual

  under_review -> completed
    Guard: all flagged items reviewed, no unresolved critical items
    Action: calculate final scores, generate findings, update vendor risk score, log to timeline, notify stakeholders
    Trigger: reviewer completes review

  under_review -> in_progress
    Guard: reviewer sends back to vendor for corrections
    Action: reopen for vendor, notify with specific items needing attention
    Trigger: manual (reviewer action)
```

### 3.3 Finding Lifecycle

```
States: open -> remediation_in_progress -> submitted_for_verification -> verified_closed
                                                                      -> risk_accepted (from open or remediation_in_progress)
                                                                      -> wont_fix (from open)

Transitions:
  open -> remediation_in_progress
    Guard: vendor acknowledges finding, remediation plan submitted
    Action: start remediation SLA timer
    Trigger: vendor action in portal or manual update

  open -> risk_accepted
    Guard: risk acceptance justification provided, approved by authorized role (CISO for critical/high)
    Action: log acceptance, set expiry for re-review, update risk score with acceptance factor
    Trigger: manual with approval workflow

  open -> wont_fix
    Guard: finding determined to be false positive or not applicable, justification provided
    Action: log justification, no score impact
    Trigger: manual with justification

  remediation_in_progress -> submitted_for_verification
    Guard: vendor submits remediation evidence
    Action: trigger AI verification, route to reviewer if confidence < 85%
    Trigger: vendor uploads evidence via portal

  remediation_in_progress -> risk_accepted
    Guard: remediation impractical, risk acceptance approved
    Action: log, set expiry
    Trigger: manual with approval

  submitted_for_verification -> verified_closed
    Guard: remediation evidence verified (AI or human), finding resolved
    Action: close finding, recalculate vendor risk score, log to timeline, notify stakeholders
    Trigger: reviewer verification or AI auto-verify (confidence > 90%)

  submitted_for_verification -> remediation_in_progress
    Guard: verification fails, remediation insufficient
    Action: notify vendor with specific gaps, extend SLA
    Trigger: reviewer rejection

  risk_accepted -> open
    Guard: risk acceptance expired or revoked
    Action: reopen finding, notify owner
    Trigger: scheduled expiry check or manual revocation
```

### 3.4 Alert Lifecycle

```
States: new -> acknowledged -> investigating -> resolved
                                             -> suppressed (from new or acknowledged)

Transitions:
  new -> acknowledged
    Guard: user explicitly acknowledges
    Action: set acknowledged_by, acknowledged_at, stop initial notification escalation
    Trigger: PUT /monitoring/alerts/{id}/acknowledge

  new -> investigating
    Guard: user begins investigation (bypasses acknowledged state)
    Action: set assigned_to, log
    Trigger: PUT /monitoring/alerts/{id}/assign

  new -> suppressed
    Guard: known false positive, suppression reason provided, suppression expiry set
    Action: log suppression, stop notifications, schedule re-evaluation at expiry
    Trigger: PUT /monitoring/alerts/{id}/suppress

  acknowledged -> investigating
    Guard: investigation started
    Action: assign investigator
    Trigger: manual assignment

  acknowledged -> suppressed
    Guard: false positive determined after initial review
    Action: log
    Trigger: manual

  investigating -> resolved
    Guard: investigation complete, root cause determined, actions taken
    Action: set resolution_notes, update vendor timeline, trigger score recalculation if needed
    Trigger: PUT /monitoring/alerts/{id}/resolve

  investigating -> new (escalation)
    Guard: multiple correlated signals elevate priority
    Action: create new higher-priority alert, link to original
    Trigger: automatic correlation engine

  suppressed -> new
    Guard: suppression expires or is manually revoked
    Action: reopen alert
    Trigger: scheduled check or manual
```

### 3.5 Evidence Lifecycle

```
States: uploaded -> processing -> parsed -> mapped -> verified
                              -> failed (from processing)

Transitions:
  uploaded -> processing
    Guard: virus scan passed, file validated
    Action: start Temporal parsing workflow, set processing_started_at
    Trigger: automatic after upload or manual via POST /evidence/{id}/process

  processing -> parsed
    Guard: document classification and extraction completed
    Action: store parsed_content JSONB, generate embedding
    Trigger: Temporal workflow activity completion

  processing -> failed
    Guard: parsing error (unsupported format, corrupted file, extraction failure)
    Action: set processing_error, notify uploader
    Trigger: Temporal workflow failure

  parsed -> mapped
    Guard: control-to-framework mappings generated
    Action: create evidence_control_mappings records, index in Typesense
    Trigger: Temporal workflow mapping activity completion

  mapped -> verified
    Guard: human verifies key mappings (or all high-confidence mappings auto-verified)
    Action: set verified flag on mappings, update evidence overall_confidence
    Trigger: manual review or auto-verify for confidence > 90%

  failed -> processing
    Guard: issue resolved, retry requested
    Action: restart workflow
    Trigger: manual retry
```

---

## 4. Background Job Definitions

### 4.1 Temporal Workflows

#### Vendor Enrichment Workflow

```
Workflow: vendor_enrichment
Trigger: vendor.created event OR manual trigger OR scheduled re-enrichment
Task Queue: enrichment-workers
Timeout: 15 minutes
Retry Policy: max 3 attempts, initial interval 30s, backoff coefficient 2.0

Activities (parallel where possible):
  1. [Parallel Group A]
     a. fetch_firmographics(vendor_domain)
        - Call Clearbit/ZoomInfo API
        - Timeout: 30s, Retry: 3x
        - Output: { industry, employee_count, revenue, hq, tech_stack }

     b. fetch_security_rating(vendor_domain)
        - Call SecurityScorecard or BitSight API
        - Timeout: 30s, Retry: 3x
        - Output: { score, grade, risk_factors, last_updated }

     c. check_certifications(vendor_name, vendor_domain)
        - Scrape IAF CertSearch, CSA STAR
        - Timeout: 60s, Retry: 2x
        - Output: { iso27001: {...}, soc2: {...}, star: {...} }

     d. check_breach_history(vendor_domain)
        - Call HIBP API
        - Timeout: 15s, Retry: 3x
        - Output: { breaches: [...] }

     e. scan_dns_ssl(vendor_domain)
        - DNS queries + SSL check
        - Timeout: 15s, Retry: 2x
        - Output: { ssl_grade, cert_expiry, spf, dkim, dmarc }

  2. [Sequential after Group A]
     f. detect_trust_center(vendor_domain, vendor_name)
        - Web scrape /security, /trust, /compliance pages
        - Timeout: 60s, Retry: 1x
        - Output: { trust_center_url, docs_found: [...] }

     g. ai_inference(all_enrichment_data)
        - LLM synthesis of all collected data
        - Timeout: 60s, Retry: 2x
        - Input: aggregated results from steps a-f
        - Output: { risk_signals: [...], inferred_tech_stack, confidence }

  3. [Final]
     h. assemble_and_store(vendor_id, all_results)
        - Store enrichment records, update vendor fields
        - Trigger tier recalculation
        - Emit vendor.enriched event
        - Index in Typesense
```

#### Evidence Parsing Pipeline

```
Workflow: evidence_parsing
Trigger: evidence.uploaded event OR manual trigger
Task Queue: evidence-workers
Timeout: 10 minutes
Retry Policy: max 2 attempts, initial interval 15s

Activities (sequential):
  1. validate_and_intake(evidence_id)
     - Verify file in S3, check hash, virus scan (ClamAV)
     - Timeout: 60s
     - Output: { valid: bool, file_metadata: {...} }

  2. classify_document(evidence_id, first_pages_text)
     - LLM classification: document type + metadata extraction
     - Timeout: 30s, Retry: 2x
     - Output: { document_type, confidence, metadata }

  3. parse_layout(evidence_id, s3_key)
     - Azure Document Intelligence or AWS Textract
     - Timeout: 180s (large documents), Retry: 2x
     - Output: { pages: [...], tables: [...], sections: [...] }

  4. extract_structured_data(evidence_id, document_type, parsed_layout)
     - LLM extraction with type-specific prompts
     - Timeout: 120s, Retry: 2x
     - Output: parsed_content JSONB (varies by type)

  5. map_to_controls(evidence_id, extracted_data, applicable_frameworks)
     - Embedding similarity + LLM validation
     - Timeout: 120s, Retry: 2x
     - Output: list[EvidenceControlMapping]

  6. index_and_embed(evidence_id, parsed_content)
     - Generate embedding for semantic search
     - Index full text in Typesense
     - Timeout: 30s, Retry: 2x

  7. finalize(evidence_id)
     - Update evidence status to 'mapped'
     - Emit evidence.parsed event
     - Flag items below confidence threshold for human review
```

#### Assessment Distribution and Reminder Workflow

```
Workflow: assessment_lifecycle
Trigger: assessment.distributed event
Task Queue: assessment-workers
Timeout: indefinite (continues until completion or cancellation)

Activities:
  1. distribute(assessment_id)
     - Generate portal access token
     - Send distribution email to vendor contact
     - Log communication
     - Set deadline timer

  2. [Timer-based reminders]
     reminder_day_7(assessment_id)
       - Condition: status still 'distributed' or 'in_progress'
       - Send gentle reminder email
       - Update reminder_schedule

     reminder_day_14(assessment_id)
       - Condition: status still 'distributed' or 'in_progress'
       - Send escalation reminder (CC vendor manager)
       - Update reminder_schedule

     reminder_day_21(assessment_id)
       - Condition: status still 'distributed' or 'in_progress'
       - Send final notice (consequences stated)
       - Update reminder_schedule

  3. [Signal handlers]
     on_vendor_submission(assessment_id)
       - Trigger AI validation activity
       - Calculate preliminary scores
       - Route to review queue

     on_deadline_exceeded(assessment_id)
       - Escalate per tenant escalation rules
       - Notify internal stakeholders
       - Log escalation

     on_cancellation(assessment_id)
       - Clean up timers
       - Notify vendor
       - Log
```

### 4.2 BullMQ Jobs

#### Monitoring Signal Collection (Scheduled)

```
Job: monitoring.signal_collection
Queue: monitoring-signals
Schedule: per monitoring_configs.next_poll_at (dynamic)
Concurrency: 10 workers
Retry: 3 attempts, exponential backoff

Process:
  1. Query monitoring_configs WHERE next_poll_at <= NOW() AND is_enabled = TRUE
  2. For each config:
     a. Fetch data from source API
     b. Parse response into MonitoringSignal records
     c. Deduplicate against existing signals (dedup_key + 24h window)
     d. Process non-duplicate signals through alert rules
     e. Update monitoring_configs.last_poll_at, next_poll_at
  3. Emit monitoring.signals_processed event
```

#### Alert Processing and Routing

```
Job: monitoring.alert_processing
Queue: alert-processing
Trigger: monitoring.signal_created event
Priority: signal severity maps to job priority (P0=highest)
Concurrency: 5 workers
Retry: 2 attempts

Process:
  1. Load signal and vendor context
  2. Match against tenant's alert_rules (ordered by sort_order)
  3. Apply correlation: check for related alerts within 48h window
  4. Determine final priority (may escalate based on correlation)
  5. Create alert record
  6. Execute rule actions:
     - Send notifications per configured channels
     - Create investigation ticket (if configured)
     - Trigger assessment (if rule specifies)
  7. Update vendor timeline
  8. Emit alert.created event
```

#### Report Generation

```
Job: reports.generate
Queue: report-generation
Trigger: API request or scheduled
Priority: normal
Concurrency: 3 workers
Timeout: 5 minutes
Retry: 2 attempts

Process:
  1. Load report template and parameters
  2. Collect data for each template section
  3. For AI narrative sections: call LLM via platform-core/llm-abstraction
  4. Assemble report document (PDF/PPTX via python-pptx/reportlab)
  5. Upload to S3
  6. Update generated_reports record
  7. If scheduled delivery: queue email delivery job
```

#### Framework Update Check (Scheduled -- Daily)

```
Job: frameworks.update_check
Queue: framework-maintenance
Schedule: CRON 0 6 * * * (daily at 06:00 UTC)
Concurrency: 1
Retry: 2 attempts

Process:
  1. Check RSS/Atom feeds for NIST, ISO, CSA, CIS
  2. For each detected update:
     a. Download updated catalog (OSCAL if available)
     b. Diff against current version (clause-level)
     c. Create framework_versions record with diff
     d. Flag affected control_mappings for re-verification
     e. Identify affected tenants and assessments
     f. Generate notification for affected tenants
  3. Log results
```

#### Certificate Expiry Check (Scheduled -- Daily)

```
Job: evidence.cert_expiry_check
Queue: evidence-maintenance
Schedule: CRON 0 7 * * * (daily at 07:00 UTC)
Concurrency: 1
Retry: 2 attempts

Process:
  1. Query evidence WHERE valid_until IS NOT NULL
     AND valid_until BETWEEN NOW() AND NOW() + INTERVAL '90 days'
     AND expiry_notified = FALSE
  2. For each expiring evidence:
     a. Determine notification threshold (90d, 60d, 30d, 14d, 7d)
     b. If threshold crossed: send notification to vendor contact + internal owner
     c. Create vendor timeline entry
     d. For certificates within 30d of expiry: create P2 alert
  3. Check for expired evidence (valid_until < NOW()):
     a. Update freshness_status (handled by generated column)
     b. Trigger vendor score recalculation
     c. Flag in dashboard
```

#### Scheduled Monitoring (BullMQ Repeatable)

```
Job: monitoring.scheduled_poll
Queue: monitoring-scheduled
Schedule: dynamic per vendor tier and signal source
  - Tier 1: every 4 hours
  - Tier 2: every 24 hours
  - Tier 3: every 7 days
  - Tier 4: every 30 days
Concurrency: 10
Retry: 3 attempts

Process:
  1. For each (vendor, source) combination due for polling:
     a. Call external API (SecurityScorecard, BitSight, HIBP, etc.)
     b. Compare with previous signal for this vendor+source
     c. If delta exceeds threshold: create monitoring_signal
     d. Update monitoring_configs.last_poll_at, next_poll_at
```

---

## 5. Event System

### 5.1 Event Bus Architecture

Redis Streams with consumer groups for durable, at-least-once delivery.

- **Stream per domain**: `velora:events:{domain}` (e.g., `velora:events:vendor`, `velora:events:assessment`)
- **Consumer groups per subscriber**: each subscribing module has its own consumer group
- **Message retention**: 7 days (configurable)
- **Dead letter queue**: failed messages after 3 retries routed to `velora:events:dlq`

### 5.2 Event Catalog

| Event Name | Stream | Payload Schema | Publisher | Subscribers |
|------------|--------|----------------|-----------|-------------|
| `vendor.created` | `velora:events:vendor` | `{ "tenant_id": UUID, "vendor_id": UUID, "name": str, "domain": str, "created_by": UUID }` | Vendor Module | AI Module (enrichment), Monitoring Module (initial config), Audit Module |
| `vendor.updated` | `velora:events:vendor` | `{ "tenant_id": UUID, "vendor_id": UUID, "changes": dict }` | Vendor Module | Scoring Module (recalc if tier-relevant), Search Module (reindex), Audit Module |
| `vendor.enriched` | `velora:events:vendor` | `{ "tenant_id": UUID, "vendor_id": UUID, "sources_completed": list[str], "enrichment_id": UUID }` | AI Module | Scoring Module (recalculate tier), Vendor Module (update fields), Search Module (reindex) |
| `vendor.tier_changed` | `velora:events:vendor` | `{ "tenant_id": UUID, "vendor_id": UUID, "old_tier": str, "new_tier": str }` | Scoring Module | Monitoring Module (adjust frequency), Assessment Module (adjust template), Comms Module (notify) |
| `vendor.status_changed` | `velora:events:vendor` | `{ "tenant_id": UUID, "vendor_id": UUID, "old_status": str, "new_status": str }` | Vendor Module | All relevant modules depending on transition |
| `assessment.created` | `velora:events:assessment` | `{ "tenant_id": UUID, "assessment_id": UUID, "vendor_id": UUID, "template_id": UUID, "type": str }` | Assessment Module | Audit Module, Vendor Module (timeline) |
| `assessment.distributed` | `velora:events:assessment` | `{ "tenant_id": UUID, "assessment_id": UUID, "vendor_id": UUID, "deadline": datetime, "vendor_contact_id": UUID }` | Assessment Module | Comms Module (send email), Portal Module (grant access), Vendor Module (timeline) |
| `assessment.submitted` | `velora:events:assessment` | `{ "tenant_id": UUID, "assessment_id": UUID, "vendor_id": UUID, "response_count": int }` | Assessment Module | AI Module (validate responses), Scoring Module (preliminary score), Comms Module (notify reviewer) |
| `assessment.completed` | `velora:events:assessment` | `{ "tenant_id": UUID, "assessment_id": UUID, "vendor_id": UUID, "composite_score": float, "findings_count": int }` | Assessment Module | Scoring Module (full recalculate), Vendor Module (update last_assessment_at, timeline), Comms Module (notify stakeholders) |
| `evidence.uploaded` | `velora:events:evidence` | `{ "tenant_id": UUID, "evidence_id": UUID, "vendor_id": UUID, "file_name": str, "document_type": str }` | Evidence Module | AI Module (parsing pipeline) |
| `evidence.parsed` | `velora:events:evidence` | `{ "tenant_id": UUID, "evidence_id": UUID, "vendor_id": UUID, "document_type": str, "control_mappings_count": int, "confidence": float }` | AI Module | Assessment Module (update evidence scores), Scoring Module (recalculate), Vendor Module (timeline), Search Module (index) |
| `evidence.expired` | `velora:events:evidence` | `{ "tenant_id": UUID, "evidence_id": UUID, "vendor_id": UUID, "document_type": str, "expired_at": date }` | Evidence Module (cert expiry job) | Scoring Module (recalculate), Comms Module (notify), Vendor Module (timeline) |
| `alert.created` | `velora:events:monitoring` | `{ "tenant_id": UUID, "alert_id": UUID, "vendor_id": UUID, "priority": str, "signal_ids": list[UUID], "title": str }` | Monitoring Module | Comms Module (send notifications), Vendor Module (timeline), Scoring Module (if score-relevant) |
| `alert.resolved` | `velora:events:monitoring` | `{ "tenant_id": UUID, "alert_id": UUID, "vendor_id": UUID, "resolution_notes": str }` | Monitoring Module | Vendor Module (timeline), Scoring Module (recalculate if needed) |
| `score.changed` | `velora:events:scoring` | `{ "tenant_id": UUID, "vendor_id": UUID, "old_score": float, "new_score": float, "old_tier": str, "new_tier": str, "triggered_by": str }` | Scoring Module | Vendor Module (update fields, timeline), Comms Module (notify if threshold crossed), Report Module (dashboard refresh) |
| `finding.created` | `velora:events:finding` | `{ "tenant_id": UUID, "finding_id": UUID, "vendor_id": UUID, "severity": str, "assessment_id": UUID, "title": str }` | Assessment Module | Comms Module (notify vendor + internal owner), Vendor Module (timeline), Portal Module (make visible) |
| `finding.closed` | `velora:events:finding` | `{ "tenant_id": UUID, "finding_id": UUID, "vendor_id": UUID, "resolution": str }` | Assessment Module | Scoring Module (recalculate), Vendor Module (timeline), Comms Module (notify) |
| `config.updated` | `velora:events:config` | `{ "tenant_id": UUID, "config_type": str, "version": int }` | Tenant Module | All modules (cache invalidation), Scoring Module (recalculate if scoring config changed) |
| `report.generated` | `velora:events:report` | `{ "tenant_id": UUID, "report_id": UUID, "report_type": str, "generated_by": UUID }` | Report Module | Comms Module (delivery if scheduled), Audit Module |

---

## 6. Configuration Schema

Full JSON Schema definitions for each `tenant_configs.config_type`.

### 6.1 Scoring Configuration (`config_type = 'scoring'`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["default_model_id", "inherent_risk", "risk_thresholds", "normalization"],
  "properties": {
    "default_model_id": {
      "type": "string",
      "format": "uuid",
      "description": "UUID of the default scoring_model"
    },
    "inherent_risk": {
      "type": "object",
      "required": ["method", "factors", "tier_thresholds"],
      "properties": {
        "method": { "enum": ["weighted_average", "multiplicative"] },
        "factors": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "weight", "source"],
            "properties": {
              "name": { "type": "string" },
              "weight": { "type": "number", "minimum": 0, "maximum": 1 },
              "source": { "type": "string" },
              "scale": {
                "type": "object",
                "additionalProperties": { "type": "number" }
              },
              "scale_min": { "type": "number" },
              "scale_max": { "type": "number" }
            }
          }
        },
        "tier_thresholds": {
          "type": "object",
          "required": ["tier_1", "tier_2", "tier_3", "tier_4"],
          "properties": {
            "tier_1": { "type": "number" },
            "tier_2": { "type": "number" },
            "tier_3": { "type": "number" },
            "tier_4": { "type": "number" }
          }
        }
      }
    },
    "composite_risk": {
      "type": "object",
      "required": ["method", "dimensions"],
      "properties": {
        "method": { "enum": ["weighted_average", "multiplicative"] },
        "residual_method": { "enum": ["subtraction", "multiplication"], "default": "multiplication" },
        "dimensions": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["name", "weight", "source"],
            "properties": {
              "name": { "type": "string" },
              "weight": { "type": "number", "minimum": 0, "maximum": 1 },
              "source": { "type": "string" }
            }
          }
        }
      }
    },
    "risk_thresholds": {
      "type": "object",
      "required": ["critical", "high", "medium", "low"],
      "properties": {
        "critical": { "type": "number", "default": 85 },
        "high": { "type": "number", "default": 70 },
        "medium": { "type": "number", "default": 40 },
        "low": { "type": "number", "default": 0 }
      }
    },
    "normalization": {
      "type": "object",
      "properties": {
        "securityscorecard": {
          "type": "object",
          "properties": {
            "input_range": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2, "default": [0, 100] },
            "output_range": { "type": "array", "items": { "type": "number" }, "minItems": 2, "maxItems": 2, "default": [0, 100] },
            "curve": { "enum": ["linear", "logarithmic", "custom"], "default": "linear" }
          }
        },
        "bitsight": {
          "type": "object",
          "properties": {
            "input_range": { "type": "array", "default": [250, 900] },
            "output_range": { "type": "array", "default": [0, 100] },
            "curve": { "enum": ["linear", "logarithmic", "custom"], "default": "linear" }
          }
        }
      }
    },
    "fair": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean", "default": false },
        "default_scenario": { "type": "string" },
        "loss_tables": {
          "type": "object",
          "properties": {
            "primary_loss_per_record": { "type": "number", "default": 164 },
            "regulatory_fine_multiplier": { "type": "number", "default": 1.5 },
            "reputation_loss_percentage": { "type": "number", "default": 0.02 }
          }
        }
      }
    }
  }
}
```

### 6.2 Workflow Configuration (`config_type = 'workflows'`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "assessment_approval": {
      "type": "object",
      "properties": {
        "enabled": { "type": "boolean", "default": true },
        "chain": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["role", "condition"],
            "properties": {
              "role": { "type": "string" },
              "condition": { "type": "string", "description": "e.g., 'vendor.tier in [tier_1, tier_2]'" },
              "timeout_hours": { "type": "integer", "default": 48 },
              "auto_approve_on_timeout": { "type": "boolean", "default": false }
            }
          }
        }
      }
    },
    "vendor_onboarding": {
      "type": "object",
      "properties": {
        "steps": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "name", "required"],
            "properties": {
              "id": { "type": "string" },
              "name": { "type": "string" },
              "description": { "type": "string" },
              "required": { "type": "boolean" },
              "assigned_role": { "type": "string" },
              "checklist_items": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          },
          "default": [
            { "id": "intake", "name": "Intake Request", "required": true, "assigned_role": "risk_analyst" },
            { "id": "inherent_risk", "name": "Inherent Risk Assessment", "required": true, "assigned_role": "risk_analyst" },
            { "id": "approval", "name": "Onboarding Approval", "required": true, "assigned_role": "tprm_manager" },
            { "id": "contract_review", "name": "Contract Review", "required": false, "assigned_role": "vrm" },
            { "id": "dpa_tracking", "name": "DPA Review", "required": false, "assigned_role": "privacy" }
          ]
        }
      }
    },
    "vendor_offboarding": {
      "type": "object",
      "properties": {
        "checklist": {
          "type": "array",
          "items": { "type": "string" },
          "default": [
            "Revoke all system access",
            "Confirm data return/destruction",
            "Decommission integrations",
            "Update risk register",
            "Archive vendor documentation",
            "Final risk score snapshot"
          ]
        }
      }
    },
    "assessment_deadline_defaults": {
      "type": "object",
      "properties": {
        "sig_core_days": { "type": "integer", "default": 30 },
        "sig_lite_days": { "type": "integer", "default": 14 },
        "caiq_v4_days": { "type": "integer", "default": 30 },
        "caiq_lite_days": { "type": "integer", "default": 14 },
        "fast_track_days": { "type": "integer", "default": 7 },
        "custom_days": { "type": "integer", "default": 21 }
      }
    },
    "reminder_cadence": {
      "type": "object",
      "properties": {
        "reminders": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "day": { "type": "integer" },
              "escalate_to": { "type": "string", "description": "role or specific user" },
              "tone": { "enum": ["gentle", "firm", "final"], "default": "gentle" }
            }
          },
          "default": [
            { "day": 7, "tone": "gentle" },
            { "day": 14, "escalate_to": "vendor_manager", "tone": "firm" },
            { "day": 21, "tone": "final" }
          ]
        }
      }
    },
    "finding_sla": {
      "type": "object",
      "properties": {
        "critical_days": { "type": "integer", "default": 30 },
        "high_days": { "type": "integer", "default": 60 },
        "medium_days": { "type": "integer", "default": 90 },
        "low_days": { "type": "integer", "default": 120 }
      }
    }
  }
}
```

### 6.3 Escalation Configuration (`config_type = 'escalation'`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "rules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "trigger", "conditions", "escalation_chain"],
        "properties": {
          "id": { "type": "string" },
          "name": { "type": "string" },
          "trigger": {
            "enum": [
              "vendor_non_response", "critical_finding", "active_breach",
              "rating_drop", "cert_expiry", "sla_breach", "risk_acceptance_request"
            ]
          },
          "conditions": {
            "type": "object",
            "properties": {
              "min_severity": { "type": "string" },
              "vendor_tier": { "type": "array", "items": { "type": "string" } },
              "days_overdue": { "type": "integer" }
            }
          },
          "escalation_chain": {
            "type": "array",
            "items": {
              "type": "object",
              "required": ["level", "role", "sla_hours"],
              "properties": {
                "level": { "type": "integer" },
                "role": { "type": "string" },
                "specific_user_id": { "type": "string", "format": "uuid" },
                "sla_hours": { "type": "integer" },
                "channels": {
                  "type": "array",
                  "items": { "enum": ["email", "slack", "teams", "in_app", "sms"] }
                }
              }
            }
          },
          "is_active": { "type": "boolean", "default": true }
        }
      },
      "default": [
        {
          "id": "vendor_non_response",
          "name": "Vendor Non-Response Escalation",
          "trigger": "vendor_non_response",
          "conditions": { "days_overdue": 30 },
          "escalation_chain": [
            { "level": 1, "role": "risk_analyst", "sla_hours": 120, "channels": ["email", "in_app"] },
            { "level": 2, "role": "procurement_lead", "sla_hours": 120, "channels": ["email", "in_app"] },
            { "level": 3, "role": "business_owner", "sla_hours": 120, "channels": ["email", "slack"] },
            { "level": 4, "role": "ciso", "sla_hours": 120, "channels": ["email", "slack", "sms"] }
          ]
        },
        {
          "id": "critical_finding",
          "name": "Critical Finding Escalation",
          "trigger": "critical_finding",
          "conditions": { "min_severity": "critical" },
          "escalation_chain": [
            { "level": 1, "role": "risk_analyst", "sla_hours": 4, "channels": ["email", "slack", "in_app"] },
            { "level": 2, "role": "ciso", "sla_hours": 24, "channels": ["email", "slack", "sms"] },
            { "level": 3, "role": "business_owner", "sla_hours": 24, "channels": ["email"] }
          ]
        },
        {
          "id": "active_breach",
          "name": "Active Vendor Breach",
          "trigger": "active_breach",
          "conditions": {},
          "escalation_chain": [
            { "level": 1, "role": "incident_response", "sla_hours": 1, "channels": ["email", "slack", "sms"] },
            { "level": 2, "role": "ciso", "sla_hours": 1, "channels": ["email", "slack", "sms"] },
            { "level": 3, "role": "legal", "sla_hours": 4, "channels": ["email"] },
            { "level": 4, "role": "executive", "sla_hours": 4, "channels": ["email"] }
          ]
        }
      ]
    }
  }
}
```

### 6.4 Notification Configuration (`config_type = 'notifications'`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "channels": {
      "type": "object",
      "properties": {
        "email": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": true },
            "provider": { "enum": ["sendgrid", "ses", "smtp"], "default": "sendgrid" },
            "from_address": { "type": "string", "format": "email" },
            "from_name": { "type": "string" },
            "reply_to": { "type": "string", "format": "email" }
          }
        },
        "slack": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "webhook_url": { "type": "string", "format": "uri" },
            "default_channel": { "type": "string" },
            "bot_token_vault_ref": { "type": "string" }
          }
        },
        "teams": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "webhook_url": { "type": "string", "format": "uri" }
          }
        },
        "sms": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "provider": { "enum": ["twilio"], "default": "twilio" },
            "from_number": { "type": "string" },
            "restricted_to_priorities": {
              "type": "array",
              "items": { "enum": ["p0", "p1"] },
              "default": ["p0"]
            }
          }
        }
      }
    },
    "rules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["event", "channels", "recipients"],
        "properties": {
          "event": { "type": "string" },
          "conditions": { "type": "object" },
          "channels": {
            "type": "array",
            "items": { "enum": ["email", "slack", "teams", "in_app", "sms"] }
          },
          "recipients": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "type": { "enum": ["role", "user", "vendor_contact", "dynamic"] },
                "value": { "type": "string" }
              }
            }
          },
          "template_slug": { "type": "string" },
          "digest": { "type": "boolean", "default": false },
          "digest_frequency": { "enum": ["hourly", "daily", "weekly"] }
        }
      }
    }
  }
}
```

### 6.5 Monitoring Configuration (`config_type = 'monitoring'`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "default_frequencies": {
      "type": "object",
      "description": "Monitoring frequency in minutes per vendor tier",
      "properties": {
        "tier_1": {
          "type": "object",
          "properties": {
            "security_rating": { "type": "integer", "default": 1440 },
            "breach_monitoring": { "type": "integer", "default": 240 },
            "dark_web": { "type": "integer", "default": 1440 },
            "dns_ssl": { "type": "integer", "default": 1440 },
            "news": { "type": "integer", "default": 1440 },
            "cve": { "type": "integer", "default": 10080 }
          }
        },
        "tier_2": {
          "type": "object",
          "properties": {
            "security_rating": { "type": "integer", "default": 10080 },
            "breach_monitoring": { "type": "integer", "default": 1440 },
            "dark_web": { "type": "integer", "default": 10080 },
            "dns_ssl": { "type": "integer", "default": 10080 },
            "news": { "type": "integer", "default": 10080 },
            "cve": { "type": "integer", "default": 20160 }
          }
        },
        "tier_3": {
          "type": "object",
          "properties": {
            "security_rating": { "type": "integer", "default": 43200 },
            "breach_monitoring": { "type": "integer", "default": 1440 },
            "dark_web": { "type": "integer", "default": 43200 },
            "dns_ssl": { "type": "integer", "default": 43200 },
            "news": { "type": "integer", "default": 43200 }
          }
        },
        "tier_4": {
          "type": "object",
          "properties": {
            "security_rating": { "type": "integer", "default": 129600 },
            "breach_monitoring": { "type": "integer", "default": 10080 }
          }
        }
      }
    },
    "signal_sources": {
      "type": "object",
      "description": "Configuration per monitoring signal source",
      "properties": {
        "securityscorecard": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "api_key_vault_ref": { "type": "string" },
            "rating_drop_threshold": { "type": "integer", "default": 5 },
            "critical_drop_threshold": { "type": "integer", "default": 15 }
          }
        },
        "bitsight": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "api_key_vault_ref": { "type": "string" },
            "rating_drop_threshold": { "type": "integer", "default": 25 },
            "critical_drop_threshold": { "type": "integer", "default": 75 }
          }
        },
        "hibp": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": true },
            "api_key_vault_ref": { "type": "string" },
            "monitor_domains": { "type": "boolean", "default": true }
          }
        },
        "breach_intel": {
          "type": "object",
          "properties": {
            "enabled": { "type": "boolean", "default": false },
            "provider": { "enum": ["breachsense", "spycloud"] },
            "api_key_vault_ref": { "type": "string" }
          }
        }
      }
    },
    "deduplication": {
      "type": "object",
      "properties": {
        "window_hours": { "type": "integer", "default": 24 },
        "correlation_window_hours": { "type": "integer", "default": 48 },
        "correlation_escalation_threshold": { "type": "integer", "default": 3 }
      }
    }
  }
}
```

### 6.6 Branding Configuration (`config_type = 'branding'`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "logo_url": { "type": "string", "format": "uri" },
    "logo_s3_key": { "type": "string" },
    "favicon_url": { "type": "string", "format": "uri" },
    "primary_color": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$", "default": "#0F172A" },
    "secondary_color": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$", "default": "#3B82F6" },
    "accent_color": { "type": "string", "pattern": "^#[0-9a-fA-F]{6}$" },
    "portal_domain": { "type": "string", "description": "Custom domain for vendor portal, e.g. security.company.com" },
    "portal_title": { "type": "string", "default": "Vendor Security Portal" },
    "email_header_html": { "type": "string" },
    "email_footer_html": { "type": "string" },
    "report_cover_logo_url": { "type": "string", "format": "uri" },
    "report_company_name": { "type": "string" }
  }
}
```

### 6.7 Roles Configuration (`config_type = 'roles'`)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "custom_roles": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "display_name", "permissions"],
        "properties": {
          "name": { "type": "string", "pattern": "^[a-z_]+$" },
          "display_name": { "type": "string" },
          "description": { "type": "string" },
          "permissions": {
            "type": "array",
            "items": { "type": "string" }
          },
          "inherits_from": { "type": "string", "description": "base role to inherit permissions from" }
        }
      }
    },
    "abac_policies": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "condition", "effect", "action"],
        "properties": {
          "id": { "type": "string" },
          "description": { "type": "string" },
          "condition": { "type": "string", "description": "Expression: resource.risk_level == 'critical' && user.role != 'ciso'" },
          "effect": { "enum": ["deny", "require_approval"] },
          "action": { "type": "string" },
          "resource_type": { "type": "string" },
          "is_active": { "type": "boolean", "default": true }
        }
      }
    }
  }
}
```

---

## 7. AI Pipeline Specifications

### 7.1 RAG Pipeline for Framework Intelligence

**Ingestion (one-time per framework version)**:

| Parameter | Value |
|-----------|-------|
| Chunk strategy | Clause-level (one clause = one chunk). No arbitrary text splitting. |
| Chunk size | Varies by clause (typically 50-500 tokens). Each clause is atomic. |
| Overlap | None (clauses are discrete units) |
| Embedding model | `text-embedding-3-large` (1536 dimensions) via platform-core/llm-abstraction |
| Embedding batch size | 100 clauses per API call |
| Storage | pgvector (framework_clauses.embedding column) |
| Metadata stored with vector | framework_id, version, section_path, domain, keywords, parent_clause_id |

**Query pipeline**:

| Step | Component | Configuration |
|------|-----------|---------------|
| 1. Query embedding | `text-embedding-3-large` | Same model as ingestion |
| 2. Vector search | pgvector | Top 50 candidates, cosine similarity, filter by applicable frameworks |
| 3. Keyword search | Typesense | Top 50 candidates, query-time boosting by framework and domain fields |
| 4. Merge + dedup | Application | Union of vector and keyword results, deduplicated by clause_id |
| 5. Re-rank | Cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-12-v2`) or LLM-based | Score merged results by relevance to original query |
| 6. Select top-k | Application | k=10 default, configurable per pipeline |
| 7. Context assembly | Application | Top-k clauses + parent clause context + cross-framework mappings |
| 8. LLM generation | Claude (primary) or GPT-4o (fallback) | System prompt with output format instructions, max 2000 output tokens |
| 9. Confidence scoring | Composite scorer | See 7.5 |
| 10. Citation extraction | Post-processing | Extract clause_id references from LLM output, validate against context |

**System prompt template (framework query)**:
```
You are a compliance framework expert. Answer the user's question using ONLY the provided
framework clause context. For each claim, cite the specific clause ID (e.g., [ISO 27001:2022 A.8.9]).

Rules:
- Only reference clauses provided in the context
- If the context does not contain sufficient information, say so explicitly
- Provide your confidence level (high/medium/low) for each claim
- Structure your response with clear sections

Context:
{assembled_clauses}

Question: {user_query}
```

### 7.2 Evidence Parser Pipeline

**Document classification**:

| Parameter | Value |
|-----------|-------|
| Input | First 2 pages of document text + filename + metadata |
| Model | Claude (primary), GPT-4o (fallback) |
| Output | `document_type` enum + confidence score |
| Token budget | 500 input tokens (pages), 100 output tokens |
| Temperature | 0.0 (deterministic) |

**Classification prompt template**:
```
Classify this document into one of these categories:
- soc2_type1: SOC 2 Type I audit report
- soc2_type2: SOC 2 Type II audit report
- iso27001_cert: ISO 27001 certificate
- pentest_report: Penetration testing report
- vuln_scan: Vulnerability scan report
- policy_document: Security/privacy policy
- insurance_cert: Cyber insurance certificate
- bcp_plan: Business continuity plan
- other: None of the above

Document filename: {filename}
First pages:
{first_pages_text}

Respond with JSON: { "document_type": "...", "confidence": 0.XX, "reasoning": "..." }
```

**Extraction prompts (type-specific)**:

SOC 2 Type II extraction prompt:
```
Extract the following fields from this SOC 2 Type II report. Use exact values from the document.
For each field, provide a confidence score (0.0-1.0).

Required fields:
1. audit_period_start (date)
2. audit_period_end (date)
3. opinion_type (unqualified/qualified/adverse/disclaimer)
4. auditor_firm (string)
5. exceptions (array of { control: string, description: string })
6. control_statuses (array of { control_id: string, control_name: string, status: effective/ineffective/not_tested })
7. cuecs (array of strings - Complementary User Entity Controls)
8. subservice_organizations (array of { name: string, method: carve_out/inclusive })
9. scope_description (string)

Document content:
{parsed_layout_text}

Respond with JSON matching the schema above. Include a "confidence" field (0.0-1.0) for each extracted value.
```

**Document parsing service config**:

| Parameter | Value |
|-----------|-------|
| Primary parser | Azure Document Intelligence (prebuilt-layout model) |
| Fallback parser | AWS Textract (AnalyzeDocument) |
| Max file size | 50 MB |
| Supported formats | PDF, DOCX, PNG, JPG, TIFF |
| Table reconstruction | Enabled (Azure DI table extraction) |
| OCR | Enabled for scanned documents |
| Timeout | 180 seconds per document |

### 7.3 Vendor Enrichment Pipeline

| Step | Data Source | Timeout | Output |
|------|------------|---------|--------|
| Firmographics | Clearbit Enrichment API or ZoomInfo | 30s | industry, employee_count, revenue_range, hq_location, tech_stack, founded_year |
| Security rating | SecurityScorecard Portfolio API or BitSight Ratings API | 30s | score, grade, risk_factors (array), last_updated |
| Certifications | IAF CertSearch (web scrape) + CSA STAR Registry | 60s | iso27001_status, soc2_status, star_level, validity_dates |
| Breach history | HIBP API (breachedaccount endpoint) | 15s | breaches (array), breach_count, most_recent_breach |
| Trust center | Custom web scraper on /security, /trust, /compliance paths | 60s | trust_center_url, docs_available (array), security_page_content |
| DNS/SSL | Direct DNS queries + SSL Labs API | 15s | ssl_grade, cert_expiry, spf, dkim, dmarc, open_ports |

**AI synthesis prompt**:
```
Analyze the following enrichment data for vendor "{vendor_name}" ({vendor_domain}).
Synthesize a risk profile with the following:

1. inferred_tech_stack: technologies likely used (based on DNS, web tech, job postings)
2. risk_signals: array of { signal: string, severity: high/medium/low, confidence: 0.0-1.0 }
3. data_handling_assessment: inferred data handling practices
4. overall_risk_summary: 2-3 sentence summary
5. recommended_tier: tier_1/tier_2/tier_3/tier_4 based on overall profile
6. confidence: overall confidence in this assessment (0.0-1.0)

Enrichment data:
{all_enrichment_data_json}

Respond with JSON matching the schema above.
```

### 7.4 Questionnaire Auto-Fill Pipeline

| Step | Description | Configuration |
|------|-------------|---------------|
| 1. Gather sources | Collect all available data for vendor | Prior responses (all historical), evidence corpus (parsed_content), trust center data, public information, enrichment data |
| 2. For each question | Generate answer candidate | See prompt below |
| 3. Citation linking | Attach source references | Link to specific evidence IDs, page numbers, prior assessment IDs |
| 4. Confidence scoring | Score each answer | Composite of: source count, source quality, answer consistency |
| 5. Classification | Route by confidence | >85%: auto-fill with AI badge. 60-85%: fill but flag for review. <60%: leave blank, flag for manual |

**Auto-fill prompt template (per question)**:
```
You are pre-filling a security questionnaire for vendor "{vendor_name}".

Question: {question_text}
Question type: {question_type}
Options: {options_if_applicable}
Expected evidence: {evidence_expected}

Available context:
--- Prior Responses ---
{prior_responses_for_this_question_or_similar}

--- Evidence Extractions ---
{relevant_evidence_parsed_content}

--- Trust Center Data ---
{trust_center_content}

--- Enrichment Data ---
{relevant_enrichment_data}

Instructions:
1. Provide the most accurate answer based ONLY on the provided context
2. Cite your sources: [PRIOR:assessment_id], [EVIDENCE:evidence_id:page], [TRUST:url], [ENRICHMENT:source]
3. If sources conflict, note the conflict and use the most recent/authoritative source
4. Provide your confidence (0.0-1.0) and reasoning

Respond with JSON:
{
  "answer_value": "...",
  "answer_text": "...",
  "citations": [{ "source_type": "...", "source_id": "...", "text": "..." }],
  "confidence": 0.XX,
  "reasoning": "...",
  "conflicts_detected": []
}
```

**Token budget per question**: 3000 input tokens (context), 500 output tokens.

### 7.5 Confidence Scoring

All AI outputs use a composite confidence scorer:

```
Composite Confidence = (
    retrieval_relevance * 0.35 +
    source_coverage    * 0.25 +
    llm_self_assessment * 0.20 +
    historical_accuracy * 0.20
)
```

| Signal | Calculation | Range |
|--------|-------------|-------|
| `retrieval_relevance` | Average cosine similarity of top-k retrieved chunks to query | 0.0 - 1.0 |
| `source_coverage` | Number of distinct source types cited / total available source types. Multi-source answers score higher. | 0.0 - 1.0 |
| `llm_self_assessment` | Parsed from LLM output's explicit confidence field | 0.0 - 1.0 |
| `historical_accuracy` | Rolling accuracy for this pipeline + query category, calibrated from human review feedback (last 100 reviewed items) | 0.0 - 1.0 (starts at 0.7 before calibration data) |

**Routing thresholds (per domain, configurable per tenant)**:

| Domain | Auto-Approve | Human Review | Reject/Manual |
|--------|-------------|-------------|---------------|
| Questionnaire auto-fill | > 0.85 | 0.60 - 0.85 | < 0.60 |
| Evidence-to-control mapping | > 0.90 | 0.70 - 0.90 | < 0.70 |
| Vendor risk scoring | > 0.80 | 0.50 - 0.80 | < 0.50 |
| Cross-framework mapping | > 0.90 | 0.70 - 0.90 | < 0.70 |
| Document classification | > 0.90 | 0.70 - 0.90 | < 0.70 |
| Report narrative generation | Always human review | N/A | N/A |

---

*End of Low-Level Design Document*
