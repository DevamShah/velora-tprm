"""Vendor domain tables — vendors, vendor_contacts, vendor_tags, vendor_enrichment.

Revision ID: 002_vendors
Revises: 001_initial_schema
Create Date: 2026-03-27
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID

revision: str = "002_vendors"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _create_vendors_table() -> None:
    """Create the vendors table with all columns and indexes."""
    op.create_table(
        "vendors",
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
            "domain", sa.String(255), nullable=True
        ),
        sa.Column(
            "description", sa.Text, nullable=True
        ),
        sa.Column(
            "status",
            sa.String(50),
            nullable=False,
            server_default="discovered",
        ),
        sa.Column(
            "tier",
            sa.String(50),
            nullable=False,
            server_default="unclassified",
        ),
        sa.Column(
            "industry", sa.String(255), nullable=True
        ),
        sa.Column(
            "country", sa.String(100), nullable=True
        ),
        sa.Column(
            "employee_count", sa.Integer, nullable=True
        ),
        sa.Column(
            "annual_revenue", sa.Numeric(18, 2), nullable=True
        ),
        sa.Column(
            "data_classification",
            sa.String(50),
            nullable=True,
        ),
        sa.Column(
            "business_criticality",
            sa.String(50),
            nullable=True,
        ),
        sa.Column(
            "contract_start_date",
            sa.Date,
            nullable=True,
        ),
        sa.Column(
            "contract_end_date",
            sa.Date,
            nullable=True,
        ),
        sa.Column(
            "contract_value",
            sa.Numeric(18, 2),
            nullable=True,
        ),
        sa.Column(
            "primary_contact_name",
            sa.String(255),
            nullable=True,
        ),
        sa.Column(
            "primary_contact_email_encrypted",
            sa.Text,
            nullable=True,
        ),
        sa.Column(
            "primary_contact_email_hash",
            sa.String(64),
            nullable=True,
        ),
        sa.Column(
            "tags",
            ARRAY(sa.Text),
            nullable=True,
            server_default="{}",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column(
            "inherent_risk_score",
            sa.Float,
            nullable=True,
        ),
        sa.Column(
            "residual_risk_score",
            sa.Float,
            nullable=True,
        ),
        sa.Column(
            "external_rating_score",
            sa.Float,
            nullable=True,
        ),
        sa.Column(
            "external_rating_provider",
            sa.String(100),
            nullable=True,
        ),
        sa.Column(
            "last_assessed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "next_assessment_due",
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
        sa.Column(
            "deleted_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )
    _create_vendor_indexes()


def _create_vendor_indexes() -> None:
    """Add performance indexes on vendors table."""
    op.create_index(
        "ix_vendors_tenant_id", "vendors", ["tenant_id"]
    )
    op.create_index(
        "ix_vendors_name", "vendors", ["name"]
    )
    op.create_index(
        "ix_vendors_domain", "vendors", ["domain"]
    )
    op.create_index(
        "ix_vendors_status", "vendors", ["status"]
    )
    op.create_index(
        "ix_vendors_tier", "vendors", ["tier"]
    )
    op.create_index(
        "ix_vendors_deleted_at", "vendors", ["deleted_at"]
    )
    op.create_index(
        "ix_vendors_tags",
        "vendors",
        ["tags"],
        postgresql_using="gin",
    )
    op.execute(
        """
        CREATE TRIGGER trg_vendors_updated_at
        BEFORE UPDATE ON vendors
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_vendor_contacts_table() -> None:
    """Create the vendor_contacts table."""
    op.create_table(
        "vendor_contacts",
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
            sa.ForeignKey("vendors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "first_name", sa.String(100), nullable=False
        ),
        sa.Column(
            "last_name", sa.String(100), nullable=False
        ),
        sa.Column(
            "email_encrypted", sa.Text, nullable=True
        ),
        sa.Column(
            "email_hash", sa.String(64), nullable=True
        ),
        sa.Column(
            "phone_encrypted", sa.Text, nullable=True
        ),
        sa.Column(
            "phone_hash", sa.String(64), nullable=True
        ),
        sa.Column(
            "role", sa.String(100), nullable=True
        ),
        sa.Column(
            "is_primary",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "portal_access",
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
        "ix_vendor_contacts_tenant_id",
        "vendor_contacts",
        ["tenant_id"],
    )
    op.create_index(
        "ix_vendor_contacts_vendor_id",
        "vendor_contacts",
        ["vendor_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_vendor_contacts_updated_at
        BEFORE UPDATE ON vendor_contacts
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _create_vendor_tags_table() -> None:
    """Create the vendor_tags table."""
    op.create_table(
        "vendor_tags",
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
            "name", sa.String(100), nullable=False
        ),
        sa.Column(
            "color", sa.String(7), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_vendor_tags_tenant_id",
        "vendor_tags",
        ["tenant_id"],
    )
    op.execute(
        """
        CREATE UNIQUE INDEX ix_vendor_tags_tenant_name
        ON vendor_tags (tenant_id, name);
        """
    )


def _create_vendor_enrichment_table() -> None:
    """Create the vendor_enrichment table."""
    op.create_table(
        "vendor_enrichment",
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
            sa.ForeignKey("vendors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "source", sa.String(100), nullable=False
        ),
        sa.Column("data", JSONB, nullable=True),
        sa.Column(
            "confidence", sa.Float, nullable=True
        ),
        sa.Column(
            "is_current",
            sa.Boolean,
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "enriched_at",
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
        "ix_vendor_enrichment_tenant_id",
        "vendor_enrichment",
        ["tenant_id"],
    )
    op.create_index(
        "ix_vendor_enrichment_vendor_id",
        "vendor_enrichment",
        ["vendor_id"],
    )
    op.execute(
        """
        CREATE TRIGGER trg_vendor_enrichment_updated_at
        BEFORE UPDATE ON vendor_enrichment
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
        """
    )


def _enable_rls() -> None:
    """Enable RLS policies on all vendor tables."""
    tables = [
        "vendors",
        "vendor_contacts",
        "vendor_tags",
        "vendor_enrichment",
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
    """Create vendor domain tables with indexes and RLS."""
    _create_vendors_table()
    _create_vendor_contacts_table()
    _create_vendor_tags_table()
    _create_vendor_enrichment_table()
    _enable_rls()


def downgrade() -> None:
    """Drop vendor domain tables and their RLS policies."""
    tables = [
        "vendor_enrichment",
        "vendor_tags",
        "vendor_contacts",
        "vendors",
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
