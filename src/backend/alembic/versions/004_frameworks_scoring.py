"""Framework intelligence and scoring engine tables.

Revision ID: 004_frameworks_scoring
Revises: 003_assessments
Create Date: 2026-03-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "004_frameworks_scoring"
down_revision: Union[str, None] = "003_assessments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_frameworks() -> None:
    """Create the frameworks table (global, not tenant-scoped)."""
    op.create_table(
        "frameworks",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "name", sa.String(255), nullable=False
        ),
        sa.Column(
            "version", sa.String(50), nullable=True
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column(
            "framework_type", sa.Text, nullable=True
        ),
        sa.Column(
            "source_url", sa.Text, nullable=True
        ),
        sa.Column(
            "clause_count",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="active",
        ),
        sa.Column(
            "structure", JSONB, nullable=True
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
    op.execute(
        """
        CREATE TRIGGER trg_frameworks_updated_at
        BEFORE UPDATE ON frameworks
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_framework_clauses() -> None:
    """Create the framework_clauses table (global)."""
    op.create_table(
        "framework_clauses",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "framework_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "frameworks.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "parent_clause_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "framework_clauses.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "clause_number",
            sa.String(50),
            nullable=False,
        ),
        sa.Column(
            "title", sa.String(500), nullable=False
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column(
            "domain_tags",
            ARRAY(sa.Text),
            nullable=True,
        ),
        sa.Column(
            "depth",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "order_index",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
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
        "ix_framework_clauses_framework_order",
        "framework_clauses",
        ["framework_id", "order_index"],
    )
    op.create_index(
        "ix_framework_clauses_parent",
        "framework_clauses",
        ["parent_clause_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_framework_clauses_updated_at
        BEFORE UPDATE ON framework_clauses
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_control_mappings() -> None:
    """Create the control_mappings table (global)."""
    op.create_table(
        "control_mappings",
        sa.Column(
            "id", UUID(as_uuid=True), primary_key=True
        ),
        sa.Column(
            "source_clause_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "framework_clauses.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "target_clause_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "framework_clauses.id",
                ondelete="CASCADE",
            ),
            nullable=False,
        ),
        sa.Column(
            "mapping_type",
            sa.String(50),
            nullable=False,
            server_default="related",
        ),
        sa.Column(
            "confidence",
            sa.Float,
            nullable=False,
            server_default=sa.text("0.0"),
        ),
        sa.Column(
            "source_type",
            sa.String(50),
            nullable=False,
            server_default="manual",
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
        "ix_control_mappings_source",
        "control_mappings",
        ["source_clause_id"],
    )
    op.create_index(
        "ix_control_mappings_target",
        "control_mappings",
        ["target_clause_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_control_mappings_updated_at
        BEFORE UPDATE ON control_mappings
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_scoring_models() -> None:
    """Create the scoring_models table (tenant-scoped)."""
    op.create_table(
        "scoring_models",
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
            "method",
            sa.String(50),
            nullable=False,
            server_default="weighted_average",
        ),
        sa.Column(
            "is_default",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "config", JSONB, nullable=True
        ),
        sa.Column(
            "inherent_risk_factors", JSONB, nullable=True
        ),
        sa.Column(
            "risk_thresholds", JSONB, nullable=True
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
        "ix_scoring_models_tenant_id",
        "scoring_models",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_scoring_models_updated_at
        BEFORE UPDATE ON scoring_models
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_vendor_scores() -> None:
    """Create the vendor_scores table (tenant-scoped)."""
    op.create_table(
        "vendor_scores",
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
            "scoring_model_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "scoring_models.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "overall_score", sa.Float, nullable=False
        ),
        sa.Column(
            "dimension_scores", JSONB, nullable=True
        ),
        sa.Column(
            "inherent_score", sa.Float, nullable=True
        ),
        sa.Column(
            "residual_score", sa.Float, nullable=True
        ),
        sa.Column(
            "external_score", sa.Float, nullable=True
        ),
        sa.Column(
            "input_snapshot", JSONB, nullable=True
        ),
        sa.Column(
            "calculated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
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
        "ix_vendor_scores_tenant_id",
        "vendor_scores",
        ["tenant_id"],
    )
    op.create_index(
        "ix_vendor_scores_vendor_id",
        "vendor_scores",
        ["vendor_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_vendor_scores_updated_at
        BEFORE UPDATE ON vendor_scores
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_score_history() -> None:
    """Create the score_history table (tenant-scoped)."""
    op.create_table(
        "score_history",
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
            "overall_score", sa.Float, nullable=False
        ),
        sa.Column(
            "dimension_scores", JSONB, nullable=True
        ),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_score_history_tenant_id",
        "score_history",
        ["tenant_id"],
    )
    op.create_index(
        "ix_score_history_vendor_recorded",
        "score_history",
        ["vendor_id", "recorded_at"],
    )


def _enable_rls() -> None:
    """Enable RLS policies on tenant-scoped tables."""
    tables = [
        "scoring_models",
        "vendor_scores",
        "score_history",
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
    """Create framework + scoring tables with indexes and RLS."""
    _create_frameworks()
    _create_framework_clauses()
    _create_control_mappings()
    _create_scoring_models()
    _create_vendor_scores()
    _create_score_history()
    _enable_rls()


def downgrade() -> None:
    """Drop framework + scoring tables and RLS policies."""
    tenant_tables = [
        "score_history",
        "vendor_scores",
        "scoring_models",
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

    drop_order = [
        "score_history",
        "vendor_scores",
        "scoring_models",
        "control_mappings",
        "framework_clauses",
        "frameworks",
    ]
    for table in drop_order:
        op.drop_table(table)
