"""
Framework domain SQLAlchemy models.

Three tables: frameworks, framework_clauses, control_mappings.
Frameworks are global reference data (not tenant-scoped).
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Framework(Base):
    """Compliance framework — global reference data."""

    __tablename__ = "frameworks"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    version: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    framework_type: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    source_url: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    clause_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    structure: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )

    # Relationships
    clauses: Mapped[list[FrameworkClause]] = relationship(
        back_populates="framework",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class FrameworkClause(Base):
    """Single clause within a framework, self-referential hierarchy."""

    __tablename__ = "framework_clauses"

    framework_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("frameworks.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_clause_id: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey(
                "framework_clauses.id",
                ondelete="SET NULL",
            ),
            nullable=True,
        )
    )
    clause_number: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    title: Mapped[str] = mapped_column(
        String(500), nullable=False
    )
    description: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )
    domain_tags: Mapped[list[str] | None] = (
        mapped_column(
            ARRAY(Text), nullable=True, default=list
        )
    )
    depth: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )
    order_index: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0
    )

    # Relationships
    framework: Mapped[Framework] = relationship(
        back_populates="clauses"
    )
    children: Mapped[list[FrameworkClause]] = relationship(
        back_populates="parent",
        lazy="selectin",
        remote_side="FrameworkClause.parent_clause_id",
        foreign_keys="FrameworkClause.parent_clause_id",
    )
    parent: Mapped[FrameworkClause | None] = (
        relationship(
            back_populates="children",
            remote_side="FrameworkClause.id",
            foreign_keys="FrameworkClause.parent_clause_id",
        )
    )
    source_mappings: Mapped[list[ControlMapping]] = (
        relationship(
            foreign_keys="ControlMapping.source_clause_id",
            lazy="noload",
            cascade="all, delete-orphan",
        )
    )
    target_mappings: Mapped[list[ControlMapping]] = (
        relationship(
            foreign_keys="ControlMapping.target_clause_id",
            lazy="noload",
            cascade="all, delete-orphan",
        )
    )


class ControlMapping(Base):
    """Cross-framework control mapping between two clauses."""

    __tablename__ = "control_mappings"

    source_clause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "framework_clauses.id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    target_clause_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "framework_clauses.id", ondelete="CASCADE"
        ),
        nullable=False,
    )
    mapping_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="related"
    )
    confidence: Mapped[float] = mapped_column(
        Float, nullable=False, default=0.0
    )
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="manual"
    )
    verified: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    verified_by: Mapped[uuid.UUID | None] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
