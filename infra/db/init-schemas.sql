-- =================================================================
-- Velora TPRM — PostgreSQL Schema-Per-Service Initialization
-- =================================================================
-- Mounted by docker-compose as an init script.
-- Creates isolated schemas and per-service database users.
-- =================================================================

-- Service schemas
CREATE SCHEMA IF NOT EXISTS auth_svc;
CREATE SCHEMA IF NOT EXISTS vendor_svc;
CREATE SCHEMA IF NOT EXISTS assessment_svc;
CREATE SCHEMA IF NOT EXISTS framework_svc;
CREATE SCHEMA IF NOT EXISTS scoring_svc;
CREATE SCHEMA IF NOT EXISTS evidence_svc;
CREATE SCHEMA IF NOT EXISTS monitoring_svc;
CREATE SCHEMA IF NOT EXISTS finding_svc;
CREATE SCHEMA IF NOT EXISTS comms_svc;
CREATE SCHEMA IF NOT EXISTS reporting_svc;
CREATE SCHEMA IF NOT EXISTS admin_svc;
CREATE SCHEMA IF NOT EXISTS ai_svc;
CREATE SCHEMA IF NOT EXISTS workflow_svc;
CREATE SCHEMA IF NOT EXISTS dashboard_read;  -- CQRS materialized read model

-- =================================================================
-- Per-service users with schema-scoped privileges
-- =================================================================

-- auth_svc_user
DO $$ BEGIN
  CREATE USER auth_svc_user WITH PASSWORD 'auth_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA auth_svc TO auth_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA auth_svc TO auth_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT ALL ON TABLES TO auth_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT ALL ON SEQUENCES TO auth_svc_user;

-- vendor_svc_user
DO $$ BEGIN
  CREATE USER vendor_svc_user WITH PASSWORD 'vendor_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA vendor_svc TO vendor_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA vendor_svc TO vendor_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA vendor_svc GRANT ALL ON TABLES TO vendor_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA vendor_svc GRANT ALL ON SEQUENCES TO vendor_svc_user;

-- assessment_svc_user
DO $$ BEGIN
  CREATE USER assessment_svc_user WITH PASSWORD 'assessment_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA assessment_svc TO assessment_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA assessment_svc TO assessment_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA assessment_svc GRANT ALL ON TABLES TO assessment_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA assessment_svc GRANT ALL ON SEQUENCES TO assessment_svc_user;

-- framework_svc_user
DO $$ BEGIN
  CREATE USER framework_svc_user WITH PASSWORD 'framework_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA framework_svc TO framework_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA framework_svc TO framework_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA framework_svc GRANT ALL ON TABLES TO framework_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA framework_svc GRANT ALL ON SEQUENCES TO framework_svc_user;

-- scoring_svc_user
DO $$ BEGIN
  CREATE USER scoring_svc_user WITH PASSWORD 'scoring_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA scoring_svc TO scoring_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA scoring_svc TO scoring_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA scoring_svc GRANT ALL ON TABLES TO scoring_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA scoring_svc GRANT ALL ON SEQUENCES TO scoring_svc_user;

-- evidence_svc_user
DO $$ BEGIN
  CREATE USER evidence_svc_user WITH PASSWORD 'evidence_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA evidence_svc TO evidence_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA evidence_svc TO evidence_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA evidence_svc GRANT ALL ON TABLES TO evidence_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA evidence_svc GRANT ALL ON SEQUENCES TO evidence_svc_user;

-- monitoring_svc_user
DO $$ BEGIN
  CREATE USER monitoring_svc_user WITH PASSWORD 'monitoring_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA monitoring_svc TO monitoring_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA monitoring_svc TO monitoring_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA monitoring_svc GRANT ALL ON TABLES TO monitoring_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA monitoring_svc GRANT ALL ON SEQUENCES TO monitoring_svc_user;

-- finding_svc_user
DO $$ BEGIN
  CREATE USER finding_svc_user WITH PASSWORD 'finding_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA finding_svc TO finding_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA finding_svc TO finding_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA finding_svc GRANT ALL ON TABLES TO finding_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA finding_svc GRANT ALL ON SEQUENCES TO finding_svc_user;

-- comms_svc_user
DO $$ BEGIN
  CREATE USER comms_svc_user WITH PASSWORD 'comms_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA comms_svc TO comms_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA comms_svc TO comms_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA comms_svc GRANT ALL ON TABLES TO comms_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA comms_svc GRANT ALL ON SEQUENCES TO comms_svc_user;

-- reporting_svc_user
DO $$ BEGIN
  CREATE USER reporting_svc_user WITH PASSWORD 'reporting_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA reporting_svc TO reporting_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA reporting_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA reporting_svc GRANT ALL ON TABLES TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA reporting_svc GRANT ALL ON SEQUENCES TO reporting_svc_user;
-- reporting_svc_user also gets SELECT on dashboard_read for CQRS
GRANT USAGE ON SCHEMA dashboard_read TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA dashboard_read TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA dashboard_read GRANT SELECT ON TABLES TO reporting_svc_user;
-- reporting_svc_user gets SELECT on all service schemas for CQRS population
GRANT USAGE ON SCHEMA auth_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO reporting_svc_user;
GRANT USAGE ON SCHEMA vendor_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA vendor_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA vendor_svc GRANT SELECT ON TABLES TO reporting_svc_user;
GRANT USAGE ON SCHEMA assessment_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA assessment_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA assessment_svc GRANT SELECT ON TABLES TO reporting_svc_user;
GRANT USAGE ON SCHEMA framework_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA framework_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA framework_svc GRANT SELECT ON TABLES TO reporting_svc_user;
GRANT USAGE ON SCHEMA scoring_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA scoring_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA scoring_svc GRANT SELECT ON TABLES TO reporting_svc_user;
GRANT USAGE ON SCHEMA evidence_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA evidence_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA evidence_svc GRANT SELECT ON TABLES TO reporting_svc_user;
GRANT USAGE ON SCHEMA monitoring_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA monitoring_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA monitoring_svc GRANT SELECT ON TABLES TO reporting_svc_user;
GRANT USAGE ON SCHEMA finding_svc TO reporting_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA finding_svc TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA finding_svc GRANT SELECT ON TABLES TO reporting_svc_user;

-- admin_svc_user
DO $$ BEGIN
  CREATE USER admin_svc_user WITH PASSWORD 'admin_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA admin_svc TO admin_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA admin_svc TO admin_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA admin_svc GRANT ALL ON TABLES TO admin_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA admin_svc GRANT ALL ON SEQUENCES TO admin_svc_user;

-- ai_svc_user
DO $$ BEGIN
  CREATE USER ai_svc_user WITH PASSWORD 'ai_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA ai_svc TO ai_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA ai_svc TO ai_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_svc GRANT ALL ON TABLES TO ai_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA ai_svc GRANT ALL ON SEQUENCES TO ai_svc_user;

-- workflow_svc_user
DO $$ BEGIN
  CREATE USER workflow_svc_user WITH PASSWORD 'workflow_svc_dev';
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;
GRANT USAGE, CREATE ON SCHEMA workflow_svc TO workflow_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA workflow_svc TO workflow_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA workflow_svc GRANT ALL ON TABLES TO workflow_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA workflow_svc GRANT ALL ON SEQUENCES TO workflow_svc_user;

-- =================================================================
-- Cross-service read access: all services can read auth_svc
-- (needed for JWT/user validation lookups)
-- =================================================================
GRANT USAGE ON SCHEMA auth_svc TO vendor_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO vendor_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO vendor_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO assessment_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO assessment_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO assessment_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO framework_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO framework_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO framework_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO scoring_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO scoring_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO scoring_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO evidence_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO evidence_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO evidence_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO monitoring_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO monitoring_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO monitoring_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO finding_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO finding_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO finding_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO comms_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO comms_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO comms_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO admin_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO admin_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO admin_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO ai_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO ai_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO ai_svc_user;

GRANT USAGE ON SCHEMA auth_svc TO workflow_svc_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth_svc TO workflow_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA auth_svc GRANT SELECT ON TABLES TO workflow_svc_user;

-- =================================================================
-- dashboard_read schema: reporting and BFF can read
-- =================================================================
GRANT USAGE, CREATE ON SCHEMA dashboard_read TO reporting_svc_user;
GRANT ALL ON ALL TABLES IN SCHEMA dashboard_read TO reporting_svc_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA dashboard_read GRANT ALL ON TABLES TO reporting_svc_user;
