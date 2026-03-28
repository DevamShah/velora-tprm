"""Dashboard, communications, findings, and admin tables.

Revision ID: 006_dashboard_comms_admin
Revises: 005_evidence_monitoring
Create Date: 2026-03-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "006_dashboard_comms_admin"
down_revision: Union[str, None] = "005_evidence_monitoring"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_dashboard_configs() -> None:
    """Create the dashboard_configs table."""
    op.create_table(
        "dashboard_configs",
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
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "dashboard_type",
            sa.Text,
            nullable=False,
            server_default="executive",
        ),
        sa.Column("widget_layout", JSONB, nullable=True),
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
        "ix_dashboard_configs_tenant_id",
        "dashboard_configs",
        ["tenant_id"],
    )
    op.create_index(
        "ix_dashboard_configs_user_id",
        "dashboard_configs",
        ["user_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_dashboard_configs_updated_at
        BEFORE UPDATE ON dashboard_configs
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_report_templates() -> None:
    """Create the report_templates table."""
    op.create_table(
        "report_templates",
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
            "template_type", sa.Text, nullable=False
        ),
        sa.Column("sections", JSONB, nullable=True),
        sa.Column(
            "is_system",
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
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_report_templates_tenant_id",
        "report_templates",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_report_templates_updated_at
        BEFORE UPDATE ON report_templates
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_generated_reports() -> None:
    """Create the generated_reports table."""
    op.create_table(
        "generated_reports",
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
            "template_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "report_templates.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "title", sa.String(500), nullable=False
        ),
        sa.Column(
            "format",
            sa.String(10),
            nullable=False,
            server_default="pdf",
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "s3_key", sa.String(1000), nullable=True
        ),
        sa.Column(
            "generated_by",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
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
        "ix_generated_reports_tenant_id",
        "generated_reports",
        ["tenant_id"],
    )
    op.create_index(
        "ix_generated_reports_status",
        "generated_reports",
        ["status"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_generated_reports_updated_at
        BEFORE UPDATE ON generated_reports
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_notifications() -> None:
    """Create the notifications table."""
    op.create_table(
        "notifications",
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
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "title", sa.String(500), nullable=False
        ),
        sa.Column("message", sa.Text, nullable=False),
        sa.Column(
            "channel",
            sa.String(20),
            nullable=False,
            server_default="in_app",
        ),
        sa.Column(
            "read",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "read_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "entity_type", sa.Text, nullable=True
        ),
        sa.Column(
            "entity_id",
            UUID(as_uuid=True),
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
        "ix_notifications_tenant_id",
        "notifications",
        ["tenant_id"],
    )
    op.create_index(
        "ix_notifications_user_id",
        "notifications",
        ["user_id"],
    )
    op.create_index(
        "ix_notifications_read",
        "notifications",
        ["user_id", "read"],
    )


def _create_notification_preferences() -> None:
    """Create the notification_preferences table."""
    op.create_table(
        "notification_preferences",
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
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "category", sa.String(100), nullable=False
        ),
        sa.Column(
            "channel_config", JSONB, nullable=True
        ),
        sa.Column(
            "quiet_hours_start",
            sa.String(5),
            nullable=True,
        ),
        sa.Column(
            "quiet_hours_end",
            sa.String(5),
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
        "ix_notification_prefs_tenant_id",
        "notification_preferences",
        ["tenant_id"],
    )
    op.create_index(
        "ix_notification_prefs_user_id",
        "notification_preferences",
        ["user_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_notification_prefs_updated_at
        BEFORE UPDATE ON notification_preferences
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_email_templates() -> None:
    """Create the email_templates table."""
    op.create_table(
        "email_templates",
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
            "subject_template",
            sa.Text,
            nullable=False,
        ),
        sa.Column(
            "body_template", sa.Text, nullable=False
        ),
        sa.Column("variables", JSONB, nullable=True),
        sa.Column(
            "is_system",
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
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_email_templates_tenant_id",
        "email_templates",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_email_templates_updated_at
        BEFORE UPDATE ON email_templates
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_communication_logs() -> None:
    """Create the communication_logs table."""
    op.create_table(
        "communication_logs",
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
            "channel", sa.String(50), nullable=False
        ),
        sa.Column(
            "recipient", sa.String(500), nullable=False
        ),
        sa.Column(
            "subject", sa.String(500), nullable=True
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="sent",
        ),
        sa.Column(
            "sent_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "error_message", sa.Text, nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_communication_logs_tenant_id",
        "communication_logs",
        ["tenant_id"],
    )
    op.create_index(
        "ix_communication_logs_status",
        "communication_logs",
        ["status"],
    )


def _create_findings() -> None:
    """Create the findings table."""
    op.create_table(
        "findings",
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
            "title", sa.String(500), nullable=False
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column(
            "severity",
            sa.String(20),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="open",
        ),
        sa.Column(
            "affected_controls",
            ARRAY(sa.Text),
            nullable=True,
        ),
        sa.Column(
            "remediation_guidance",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "sla_due_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "assigned_to",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "closed_at",
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
        "ix_findings_tenant_id",
        "findings",
        ["tenant_id"],
    )
    op.create_index(
        "ix_findings_vendor_id",
        "findings",
        ["vendor_id"],
    )
    op.create_index(
        "ix_findings_severity_status",
        "findings",
        ["severity", "status"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_findings_updated_at
        BEFORE UPDATE ON findings
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_remediation_actions() -> None:
    """Create the remediation_actions table."""
    op.create_table(
        "remediation_actions",
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
            "finding_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "findings.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "action_type",
            sa.String(100),
            nullable=False,
        ),
        sa.Column(
            "description", sa.Text, nullable=False
        ),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "effort_estimate",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "completed_at",
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
        "ix_remediation_actions_tenant_id",
        "remediation_actions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_remediation_actions_finding_id",
        "remediation_actions",
        ["finding_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_remediation_actions_updated_at
        BEFORE UPDATE ON remediation_actions
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_audit_logs() -> None:
    """Create the audit_logs table."""
    op.create_table(
        "audit_logs",
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
            "user_id",
            UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("action", sa.Text, nullable=False),
        sa.Column(
            "entity_type", sa.Text, nullable=True
        ),
        sa.Column(
            "entity_id",
            UUID(as_uuid=True),
            nullable=True,
        ),
        sa.Column("details", JSONB, nullable=True),
        sa.Column(
            "ip_address", sa.Text, nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_audit_logs_tenant_id",
        "audit_logs",
        ["tenant_id"],
    )
    op.create_index(
        "ix_audit_logs_user_id",
        "audit_logs",
        ["user_id"],
    )
    op.create_index(
        "ix_audit_logs_action",
        "audit_logs",
        ["action"],
    )
    op.create_index(
        "ix_audit_logs_entity",
        "audit_logs",
        ["entity_type", "entity_id"],
    )
    op.create_index(
        "ix_audit_logs_created_at",
        "audit_logs",
        ["created_at"],
    )


def _enable_rls() -> None:
    """Enable RLS policies on all new tenant-scoped tables."""
    tables = [
        "dashboard_configs",
        "report_templates",
        "generated_reports",
        "notifications",
        "notification_preferences",
        "email_templates",
        "communication_logs",
        "findings",
        "remediation_actions",
        "audit_logs",
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
    """Create dashboard, comms, findings, admin tables with RLS."""
    _create_dashboard_configs()
    _create_report_templates()
    _create_generated_reports()
    _create_notifications()
    _create_notification_preferences()
    _create_email_templates()
    _create_communication_logs()
    _create_findings()
    _create_remediation_actions()
    _create_audit_logs()
    _enable_rls()


def downgrade() -> None:
    """Drop all tables created in this migration."""
    tenant_tables = [
        "audit_logs",
        "remediation_actions",
        "findings",
        "communication_logs",
        "email_templates",
        "notification_preferences",
        "notifications",
        "generated_reports",
        "report_templates",
        "dashboard_configs",
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
