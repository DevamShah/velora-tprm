"""
Communications Pydantic v2 request / response schemas.

Handles notifications, preferences, email templates,
and communication logs.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# -- Enums ----------------------------------------------------------


class NotificationChannel(str, Enum):
    """Supported notification channels."""

    in_app = "in_app"
    email = "email"
    slack = "slack"
    teams = "teams"
    sms = "sms"


class CommLogStatus(str, Enum):
    """Communication log delivery status."""

    sent = "sent"
    delivered = "delivered"
    failed = "failed"
    bounced = "bounced"


# -- Notification Responses -----------------------------------------


class NotificationResponse(BaseModel):
    """Single notification response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    user_id: uuid.UUID
    title: str
    message: str
    channel: str
    read: bool
    read_at: datetime | None = None
    entity_type: str | None = None
    entity_id: uuid.UUID | None = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated notification list."""

    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int


# -- Notification Preferences --------------------------------------


class PreferenceResponse(BaseModel):
    """Notification preference response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: str
    channel_config: dict[str, Any] | None = None
    quiet_hours_start: str | None = None
    quiet_hours_end: str | None = None
    created_at: datetime
    updated_at: datetime


class PreferenceUpdate(BaseModel):
    """Update notification preferences."""

    category: str = Field(min_length=1, max_length=100)
    channel_config: dict[str, Any] | None = None
    quiet_hours_start: str | None = Field(None, max_length=5)
    quiet_hours_end: str | None = Field(None, max_length=5)


# -- Email Template Schemas -----------------------------------------


class EmailTemplateCreate(BaseModel):
    """Create an email template."""

    name: str = Field(min_length=1, max_length=255)
    subject_template: str = Field(min_length=1)
    body_template: str = Field(min_length=1)
    variables: dict[str, Any] | None = None
    is_system: bool = False


class EmailTemplateUpdate(BaseModel):
    """Update an email template."""

    name: str | None = Field(None, min_length=1, max_length=255)
    subject_template: str | None = None
    body_template: str | None = None
    variables: dict[str, Any] | None = None


class EmailTemplateResponse(BaseModel):
    """Email template response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    subject_template: str
    body_template: str
    variables: dict[str, Any] | None = None
    is_system: bool
    created_at: datetime
    updated_at: datetime


# -- Communication Log ----------------------------------------------


class CommLogResponse(BaseModel):
    """Communication log entry response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    channel: str
    recipient: str
    subject: str | None = None
    status: str
    sent_at: datetime | None = None
    error_message: str | None = None
    created_at: datetime


class CommLogListResponse(BaseModel):
    """Paginated communication log list."""

    items: list[CommLogResponse]
    total: int
    page: int
    page_size: int
