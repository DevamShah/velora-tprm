"""
Framework Pydantic v2 request / response schemas.

Handles framework listing, clause trees, control mappings,
and unified control library responses.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# -- Enums ----------------------------------------------------------


class FrameworkStatus(str, Enum):
    """Framework lifecycle states."""

    active = "active"
    deprecated = "deprecated"
    draft = "draft"


class MappingType(str, Enum):
    """Control mapping relationship types."""

    equivalent = "equivalent"
    partial = "partial"
    related = "related"


class SourceType(str, Enum):
    """How the mapping was established."""

    olir = "olir"
    ai = "ai"
    manual = "manual"


# -- Clause Schemas -------------------------------------------------


class ClauseResponse(BaseModel):
    """Single clause within a framework."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    framework_id: uuid.UUID
    parent_clause_id: uuid.UUID | None = None
    clause_number: str
    title: str
    description: str | None = None
    domain_tags: list[str] | None = None
    depth: int = 0
    order_index: int = 0
    created_at: datetime
    updated_at: datetime


class ClauseTreeNode(BaseModel):
    """Hierarchical clause node with children."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    clause_number: str
    title: str
    description: str | None = None
    domain_tags: list[str] | None = None
    depth: int = 0
    order_index: int = 0
    children: list[ClauseTreeNode] = Field(default_factory=list)


# Self-referential model rebuild for forward refs
ClauseTreeNode.model_rebuild()


# -- Mapping Schemas ------------------------------------------------


class MappingResponse(BaseModel):
    """Cross-framework control mapping."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    source_clause_id: uuid.UUID
    target_clause_id: uuid.UUID
    mapping_type: str
    confidence: float
    source_type: str
    verified: bool
    source_clause_number: str | None = None
    source_clause_title: str | None = None
    source_framework_name: str | None = None
    target_clause_number: str | None = None
    target_clause_title: str | None = None
    target_framework_name: str | None = None
    created_at: datetime
    updated_at: datetime


# -- Framework Schemas ----------------------------------------------


class FrameworkResponse(BaseModel):
    """Framework summary for list views."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    version: str | None = None
    description: str | None = None
    framework_type: str | None = None
    source_url: str | None = None
    clause_count: int = 0
    status: str
    created_at: datetime
    updated_at: datetime


class FrameworkDetailResponse(BaseModel):
    """Framework detail with clause tree."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    version: str | None = None
    description: str | None = None
    framework_type: str | None = None
    source_url: str | None = None
    clause_count: int = 0
    status: str
    structure: dict[str, Any] | None = None
    clauses: list[ClauseTreeNode] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class FrameworkListResponse(BaseModel):
    """List of all frameworks."""

    items: list[FrameworkResponse]
    total: int


# -- Unified Controls -----------------------------------------------


class UnifiedControl(BaseModel):
    """Deduplicated control with framework sources."""

    control_id: uuid.UUID
    clause_number: str
    title: str
    description: str | None = None
    domain_tags: list[str] | None = None
    framework_name: str
    mapped_frameworks: list[str] = Field(default_factory=list)
    mapping_count: int = 0
