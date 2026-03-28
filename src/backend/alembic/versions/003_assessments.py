"""Assessment engine tables — templates, question banks, questions, assessments, responses.

Revision ID: 003_assessments
Revises: 002_vendors
Create Date: 2026-03-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "003_assessments"
down_revision: Union[str, None] = "002_vendors"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_assessment_templates() -> None:
    """Create the assessment_templates table."""
    op.create_table(
        "assessment_templates",
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
            "framework_ids",
            ARRAY(UUID(as_uuid=True)),
            nullable=True,
        ),
        sa.Column(
            "tier_applicability",
            ARRAY(sa.Text),
            nullable=True,
        ),
        sa.Column(
            "is_system",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "is_active",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "scoring_weights", JSONB, nullable=True
        ),
        sa.Column(
            "question_count",
            sa.Integer,
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column(
            "estimated_duration_minutes",
            sa.Integer,
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
        "ix_assessment_templates_tenant_id",
        "assessment_templates",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_assessment_templates_updated_at
        BEFORE UPDATE ON assessment_templates
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_question_banks() -> None:
    """Create the question_banks table."""
    op.create_table(
        "question_banks",
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
            "bank_type",
            sa.String(50),
            nullable=False,
            server_default="custom",
        ),
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
        "ix_question_banks_tenant_id",
        "question_banks",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_question_banks_updated_at
        BEFORE UPDATE ON question_banks
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_questions() -> None:
    """Create the questions table."""
    op.create_table(
        "questions",
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
            "question_bank_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "question_banks.id", ondelete="CASCADE"
            ),
            nullable=True,
        ),
        sa.Column(
            "template_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "assessment_templates.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "section", sa.String(255), nullable=True
        ),
        sa.Column(
            "subsection", sa.String(255), nullable=True
        ),
        sa.Column(
            "question_text", sa.Text, nullable=False
        ),
        sa.Column(
            "question_type",
            sa.String(50),
            nullable=False,
            server_default="text",
        ),
        sa.Column(
            "options", JSONB, nullable=True
        ),
        sa.Column(
            "is_required",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "weight",
            sa.Float,
            nullable=False,
            server_default=sa.text("1.0"),
        ),
        sa.Column(
            "risk_domain",
            sa.String(100),
            nullable=True,
        ),
        sa.Column(
            "guidance_text", sa.Text, nullable=True
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
        "ix_questions_tenant_id",
        "questions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_questions_template_id",
        "questions",
        ["template_id"],
    )
    op.create_index(
        "ix_questions_bank_id",
        "questions",
        ["question_bank_id"],
    )
    op.create_index(
        "ix_questions_order_index",
        "questions",
        ["order_index"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_questions_updated_at
        BEFORE UPDATE ON questions
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_assessments() -> None:
    """Create the assessments table."""
    op.create_table(
        "assessments",
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
            "template_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "assessment_templates.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        ),
        sa.Column(
            "title", sa.String(255), nullable=False
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="draft",
        ),
        sa.Column(
            "assigned_to",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "distributed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "completed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "due_date",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "reminder_schedule", JSONB, nullable=True
        ),
        sa.Column(
            "overall_score", sa.Float, nullable=True
        ),
        sa.Column(
            "ai_confidence", sa.Float, nullable=True
        ),
        sa.Column(
            "scoring_details", JSONB, nullable=True
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
        "ix_assessments_tenant_id",
        "assessments",
        ["tenant_id"],
    )
    op.create_index(
        "ix_assessments_vendor_id",
        "assessments",
        ["vendor_id"],
    )
    op.create_index(
        "ix_assessments_template_id",
        "assessments",
        ["template_id"],
    )
    op.create_index(
        "ix_assessments_status",
        "assessments",
        ["status"],
    )
    op.create_index(
        "ix_assessments_assigned_to",
        "assessments",
        ["assigned_to"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_assessments_updated_at
        BEFORE UPDATE ON assessments
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_questionnaire_responses() -> None:
    """Create the questionnaire_responses table."""
    op.create_table(
        "questionnaire_responses",
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
            "assessment_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "assessments.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "question_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "questions.id", ondelete="CASCADE"
            ),
            nullable=False,
        ),
        sa.Column(
            "response_value",
            sa.String(500),
            nullable=True,
        ),
        sa.Column(
            "response_text", sa.Text, nullable=True
        ),
        sa.Column(
            "response_options", JSONB, nullable=True
        ),
        sa.Column(
            "ai_prefilled",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "ai_confidence", sa.Float, nullable=True
        ),
        sa.Column(
            "ai_citations", JSONB, nullable=True
        ),
        sa.Column(
            "reviewer_id",
            UUID(as_uuid=True),
            sa.ForeignKey(
                "users.id", ondelete="SET NULL"
            ),
            nullable=True,
        ),
        sa.Column(
            "review_status",
            sa.String(50),
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "reviewer_notes", sa.Text, nullable=True
        ),
        sa.Column(
            "responded_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "reviewed_at",
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
        "ix_qr_tenant_id",
        "questionnaire_responses",
        ["tenant_id"],
    )
    op.create_index(
        "ix_qr_assessment_id",
        "questionnaire_responses",
        ["assessment_id"],
    )
    op.create_index(
        "ix_qr_question_id",
        "questionnaire_responses",
        ["question_id"],
    )
    op.create_index(
        "ix_qr_review_status",
        "questionnaire_responses",
        ["review_status"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_qr_updated_at
        BEFORE UPDATE ON questionnaire_responses
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _enable_rls() -> None:
    """Enable RLS policies on all assessment tables."""
    tables = [
        "assessment_templates",
        "question_banks",
        "questions",
        "assessments",
        "questionnaire_responses",
    ]
    for table in tables:
        op.execute(
            f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;"
        )
        op.execute(
            f"""
            CREATE POLICY {table}_tenant_isolation ON {table}
            USING (
                tenant_id::text
                = current_setting('app.current_tenant_id', true)
            );
            """
        )


def upgrade() -> None:
    """Create assessment engine tables with indexes and RLS."""
    _create_assessment_templates()
    _create_question_banks()
    _create_questions()
    _create_assessments()
    _create_questionnaire_responses()
    _enable_rls()


def downgrade() -> None:
    """Drop assessment engine tables and their RLS policies."""
    tables = [
        "questionnaire_responses",
        "assessments",
        "questions",
        "question_banks",
        "assessment_templates",
    ]
    for table in tables:
        op.execute(
            f"DROP POLICY IF EXISTS {table}_tenant_isolation"
            f" ON {table};"
        )
        op.execute(
            f"ALTER TABLE {table}"
            f" DISABLE ROW LEVEL SECURITY;"
        )
        op.drop_table(table)
