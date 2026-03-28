"""Evidence, monitoring, alerts, and vendor timeline tables.

Revision ID: 005_evidence_monitoring
Revises: 004_frameworks_scoring
Create Date: 2026-03-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "005_evidence_monitoring"
down_revision: Union[str, None] = "004_frameworks_scoring"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_evidence() -> None:
    """Create the evidence table (tenant-scoped)."""
    op.create_table(
        "evidence",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "vendor_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "vendors.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "assessment_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "assessments.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "filename", sa.String(500), nullable=False
        ),
        sa.Column(
            "file_size", sa.Integer, nullable=False
        ),
        sa.Column(
            "mime_type", sa.String(100), nullable=False
        ),
        sa.Column(
            "s3_key", sa.String(1000), nullable=False
        ),
        sa.Column(
            "document_type",
            sa.String(50),
            nullable=False,
            server_default="other",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="uploaded",
        ),
        sa.Column(
            "parsed_content", JSONB, nullable=True
        ),
        sa.Column(
            "extraction_summary", JSONB, nullable=True
        ),
        sa.Column(
            "classification_confidence",
            sa.Float,
            nullable=True,
        ),
        sa.Column(
            "uploaded_by",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_evidence_tenant_id",
        "evidence",
        ["tenant_id"],
    )
    op.create_index(
        "ix_evidence_vendor_id",
        "evidence",
        ["vendor_id"],
    )
    op.create_index(
        "ix_evidence_assessment_id",
        "evidence",
        ["assessment_id"],
    )
    op.create_index(
        "ix_evidence_status",
        "evidence",
        ["status"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_evidence_updated_at
        BEFORE UPDATE ON evidence
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_evidence_control_mappings() -> None:
    """Create the evidence_control_mappings table."""
    op.create_table(
        "evidence_control_mappings",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "evidence.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "clause_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "framework_clauses.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "coverage_type",
            sa.String(50),
            nullable=False,
            server_default="supportive",
        ),
        sa.Column(
            "confidence",
            sa.Float,
            nullable=False,
            server_default=sa.text("0.0"),
        ),
        sa.Column(
            "verified",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "verified_by",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_ecm_tenant_id",
        "evidence_control_mappings",
        ["tenant_id"],
    )
    op.create_index(
        "ix_ecm_evidence_id",
        "evidence_control_mappings",
        ["evidence_id"],
    )
    op.create_index(
        "ix_ecm_clause_id",
        "evidence_control_mappings",
        ["clause_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_ecm_updated_at
        BEFORE UPDATE ON evidence_control_mappings
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_evidence_extractions() -> None:
    """Create the evidence_extractions table."""
    op.create_table(
        "evidence_extractions",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "evidence_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "evidence.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "field_name",
            sa.String(255),
            nullable=False,
        ),
        sa.Column(
            "field_value", sa.Text, nullable=False
        ),
        sa.Column(
            "confidence",
            sa.Float,
            nullable=False,
            server_default=sa.text("0.0"),
        ),
        sa.Column(
            "page_number", sa.Integer, nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_evidence_extractions_tenant_id",
        "evidence_extractions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_evidence_extractions_evidence_id",
        "evidence_extractions",
        ["evidence_id"],
    )


def _create_monitoring_configs() -> None:
    """Create the monitoring_configs table."""
    op.create_table(
        "monitoring_configs",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "vendor_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "vendors.id", ondelete="CASCADE"
            ),
            nullable=True,
        ),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column(
            "frequency_hours",
            sa.Integer,
            nullable=False,
            server_default=sa.text("24"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "last_polled_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_monitoring_configs_tenant_id",
        "monitoring_configs",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_monitoring_configs_updated_at
        BEFORE UPDATE ON monitoring_configs
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_monitoring_signals() -> None:
    """Create the monitoring_signals table."""
    op.create_table(
        "monitoring_signals",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "vendor_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "vendors.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column("source", sa.Text, nullable=False),
        sa.Column(
            "signal_type", sa.Text, nullable=False
        ),
        sa.Column(
            "severity",
            sa.String(50),
            nullable=False,
            server_default="info",
        ),
        sa.Column(
            "title", sa.String(500), nullable=False
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column("raw_data", JSONB, nullable=True),
        sa.Column(
            "dedup_key", sa.Text, nullable=True
        ),
        sa.Column(
            "processed",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_monitoring_signals_tenant_id",
        "monitoring_signals",
        ["tenant_id"],
    )
    op.create_index(
        "ix_monitoring_signals_vendor_id",
        "monitoring_signals",
        ["vendor_id"],
    )
    op.create_index(
        "ix_monitoring_signals_dedup_key",
        "monitoring_signals",
        ["dedup_key"],
    )


def _create_alerts() -> None:
    """Create the alerts table."""
    op.create_table(
        "alerts",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "vendor_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "vendors.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "priority",
            sa.String(20),
            nullable=False,
            server_default="p3",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="new",
        ),
        sa.Column(
            "title", sa.String(500), nullable=False
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column(
            "signal_ids",
            ARRAY(UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column(
            "impact_assessment", JSONB, nullable=True
        ),
        sa.Column(
            "acknowledged_by",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "resolved_by",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "acknowledged_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "resolved_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "resolution_notes", sa.Text, nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_alerts_tenant_id",
        "alerts",
        ["tenant_id"],
    )
    op.create_index(
        "ix_alerts_vendor_id",
        "alerts",
        ["vendor_id"],
    )
    op.create_index(
        "ix_alerts_priority_status",
        "alerts",
        ["priority", "status"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_alerts_updated_at
        BEFORE UPDATE ON alerts
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_alert_rules() -> None:
    """Create the alert_rules table."""
    op.create_table(
        "alert_rules",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "name", sa.String(255), nullable=False
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column(
            "conditions", JSONB, nullable=False
        ),
        sa.Column("actions", JSONB, nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_alert_rules_tenant_id",
        "alert_rules",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_alert_rules_updated_at
        BEFORE UPDATE ON alert_rules
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_vendor_timelines() -> None:
    """Create the vendor_timelines table."""
    op.create_table(
        "vendor_timelines",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "tenant_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "vendor_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "vendors.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "event_type", sa.Text, nullable=False
        ),
        sa.Column(
            "title", sa.String(500), nullable=False
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column("metadata", JSONB, nullable=True),
        sa.Column(
            "actor_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_vendor_timelines_tenant_id",
        "vendor_timelines",
        ["tenant_id"],
    )
    op.create_index(
        "ix_vendor_timelines_vendor_id",
        "vendor_timelines",
        ["vendor_id"],
    )
    op.create_index(
        "ix_vendor_timelines_created_at",
        "vendor_timelines",
        ["vendor_id", "created_at"],
    )


def _enable_rls() -> None:
    """Enable RLS policies on all tenant-scoped tables."""
    tables = [
        "evidence",
        "evidence_control_mappings",
        "evidence_extractions",
        "monitoring_configs",
        "monitoring_signals",
        "alerts",
        "alert_rules",
        "vendor_timelines",
    ]
    for table in tables:
        op.execute(
            f"ALTER TABLE {table}"
            f" ENABLE ROW LEVEL SECURITY;"
        )
        op.execute(
            f"""
            CREATE POLICY {table}_tenant_isolation ON {table}
            USING (
                tenant_id::text
                = current_setting(
                    'app.current_tenant_id', true
                )
            );
            """
        )


def upgrade() -> None:
    """Create evidence + monitoring tables with RLS."""
    _create_evidence()
    _create_evidence_control_mappings()
    _create_evidence_extractions()
    _create_monitoring_configs()
    _create_monitoring_signals()
    _create_alerts()
    _create_alert_rules()
    _create_vendor_timelines()
    _enable_rls()


def downgrade() -> None:
    """Drop evidence + monitoring tables and RLS policies."""
    tenant_tables = [
        "vendor_timelines",
        "alert_rules",
        "alerts",
        "monitoring_signals",
        "monitoring_configs",
        "evidence_extractions",
        "evidence_control_mappings",
        "evidence",
    ]
    for table in tenant_tables:
        op.execute(
            f"DROP POLICY IF EXISTS"
            f" {table}_tenant_isolation ON {table};"
        )
        op.execute(
            f"ALTER TABLE {table}"
            f" DISABLE ROW LEVEL SECURITY;"
        )

    for table in tenant_tables:
        op.drop_table(table)
