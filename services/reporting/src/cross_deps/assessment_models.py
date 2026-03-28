"""
Assessment engine SQLAlchemy models.

Five tables: assessment_templates, question_banks, questions,
assessments, questionnaire_responses.
All tenant-scoped tables use TenantBase for RLS isolation.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from velora_common.models import TenantBase


class AssessmentTemplate(TenantBase):
    """Reusable assessment template with scoring configuration."""

    __tablename__ = "assessment_templates"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    framework_ids: Mapped[Optional[List[uuid.UUID]]] = (
        mapped_column(
            ARRAY(UUID(as_uuid=True)), nullable=True
        )
    )
    tier_applicability: Mapped[Optional[List[str]]] = (
        mapped_column(ARRAY(Text), nullable=True)
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    scoring_weights: Mapped[Optional[Dict]] = mapped_column(
        JSONB, nullable=True
    )
    question_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    estimated_duration_minutes: Mapped[Optional[int]] = (
        mapped_column(Integer, nullable=True)
    )

    # Relationships
    questions: Mapped[List["Question"]] = relationship(
        back_populates="template",
        lazy="noload",
        cascade="all, delete-orphan",
    )
    assessments: Mapped[List["Assessment"]] = relationship(
        back_populates="template",
        lazy="noload",
    )


class QuestionBank(TenantBase):
    """Grouped question bank with a type classification."""

    __tablename__ = "question_banks"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    bank_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="custom"
    )
    is_system: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # Relationships
    questions: Mapped[List["Question"]] = relationship(
        back_populates="question_bank",
        lazy="noload",
        cascade="all, delete-orphan",
    )


class Question(TenantBase):
    """Individual assessment question with scoring weight."""

    __tablename__ = "questions"

    question_bank_id: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey(
                "question_banks.id", ondelete="CASCADE"
            ),
            nullable=True,
            index=True,
        )
    )
    template_id: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey(
                "assessment_templates.id",
                ondelete="SET NULL",
            ),
            nullable=True,
            index=True,
        )
    )
    section: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    subsection: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    question_text: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    question_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="text"
    )
    options: Mapped[Optional[Dict]] = mapped_column(
        JSONB, nullable=True
    )
    is_required: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )
    weight: Mapped[float] = mapped_column(
        Float, default=1.0, nullable=False
    )
    risk_domain: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    guidance_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    order_index: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Relationships
    question_bank: Mapped[Optional["QuestionBank"]] = (
        relationship(back_populates="questions")
    )
    template: Mapped[Optional["AssessmentTemplate"]] = (
        relationship(back_populates="questions")
    )
    responses: Mapped[List["QuestionnaireResponse"]] = (
        relationship(
            back_populates="question",
            lazy="noload",
        )
    )


class Assessment(TenantBase):
    """Vendor assessment instance with lifecycle state machine."""

    __tablename__ = "assessments"

    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("vendors.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    template_id: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey(
                "assessment_templates.id",
                ondelete="SET NULL",
            ),
            nullable=True,
            index=True,
        )
    )
    title: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft"
    )
    assigned_to: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    distributed_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )
    submitted_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )
    completed_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    reminder_schedule: Mapped[Optional[Dict]] = (
        mapped_column(JSONB, nullable=True)
    )
    overall_score: Mapped[Optional[float]] = (
        mapped_column(Float, nullable=True)
    )
    ai_confidence: Mapped[Optional[float]] = (
        mapped_column(Float, nullable=True)
    )
    scoring_details: Mapped[Optional[Dict]] = (
        mapped_column(JSONB, nullable=True)
    )

    # Relationships
    vendor: Mapped[Any] = relationship(
        "Vendor",
        lazy="selectin",
        foreign_keys=[vendor_id],
    )
    template: Mapped[Optional["AssessmentTemplate"]] = (
        relationship(
            back_populates="assessments",
            lazy="selectin",
        )
    )
    responses: Mapped[
        List["QuestionnaireResponse"]
    ] = relationship(
        back_populates="assessment",
        lazy="noload",
        cascade="all, delete-orphan",
    )


class QuestionnaireResponse(TenantBase):
    """Individual response to an assessment question."""

    __tablename__ = "questionnaire_responses"

    assessment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    response_value: Mapped[Optional[str]] = mapped_column(
        String(500), nullable=True
    )
    response_text: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    response_options: Mapped[Optional[Dict]] = (
        mapped_column(JSONB, nullable=True)
    )
    ai_prefilled: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    ai_confidence: Mapped[Optional[float]] = (
        mapped_column(Float, nullable=True)
    )
    ai_citations: Mapped[Optional[Dict]] = mapped_column(
        JSONB, nullable=True
    )
    reviewer_id: Mapped[Optional[uuid.UUID]] = (
        mapped_column(
            UUID(as_uuid=True),
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        )
    )
    review_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )
    reviewer_notes: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True
    )
    responded_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )
    reviewed_at: Mapped[Optional[datetime]] = (
        mapped_column(
            DateTime(timezone=True), nullable=True
        )
    )

    # Relationships
    assessment: Mapped["Assessment"] = relationship(
        back_populates="responses"
    )
    question: Mapped["Question"] = relationship(
        back_populates="responses",
        lazy="selectin",
    )
