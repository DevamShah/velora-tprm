"""
Reports domain SQLAlchemy models.

Three tables: dashboard_configs, report_templates, generated_reports.
All tenant-scoped via TenantBase for RLS isolation.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    ForeignKey,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import TenantBase


class DashboardConfig(TenantBase):
    """User-specific dashboard layout configuration."""

    __tablename__ = "dashboard_configs"

    user_id: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
            index=True,
        )
    )
    dashboard_type: Mapped[str] = mapped_column(
        Text, nullable=False, default="executive"
    )
    widget_layout: Mapped[dict | None] = (
        mapped_column(JSONB, nullable=True)
    )


class ReportTemplate(TenantBase):
    """Reusable report template with section definitions."""

    __tablename__ = "report_templates"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    template_type: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    sections: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )


class GeneratedReport(TenantBase):
    """Report generation record with output file reference."""

    __tablename__ = "generated_reports"

    template_id: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey(
                "report_templates.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        )
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    format: Mapped[str] = mapped_column(
        String(10), nullable=False, default="pdf"
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )
    s3_key: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )
    generated_by: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
