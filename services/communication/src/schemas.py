"""
Communications Pydantic v2 request / response schemas.

Handles notifications, preferences, email templates,
and communication logs.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

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
    read_at: Optional[datetime] = None
    entity_type: Optional[str] = None
    entity_id: Optional[uuid.UUID] = None
    created_at: datetime


class NotificationListResponse(BaseModel):
    """Paginated notification list."""

    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int


# -- Notification Preferences --------------------------------------


class PreferenceResponse(BaseModel):
    """Notification preference response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    category: str
    channel_config: Optional[Dict[str, Any]] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class PreferenceUpdate(BaseModel):
    """Update notification preferences."""

    category: str = Field(min_length=1, max_length=100)
    channel_config: Optional[Dict[str, Any]] = None
    quiet_hours_start: Optional[str] = Field(
        None, max_length=5
    )
    quiet_hours_end: Optional[str] = Field(
        None, max_length=5
    )


# -- Email Template Schemas -----------------------------------------


class EmailTemplateCreate(BaseModel):
    """Create an email template."""

    name: str = Field(min_length=1, max_length=255)
    subject_template: str = Field(min_length=1)
    body_template: str = Field(min_length=1)
    variables: Optional[Dict[str, Any]] = None
    is_system: bool = False


class EmailTemplateUpdate(BaseModel):
    """Update an email template."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255
    )
    subject_template: Optional[str] = None
    body_template: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class EmailTemplateResponse(BaseModel):
    """Email template response."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    subject_template: str
    body_template: str
    variables: Optional[Dict[str, Any]] = None
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
    subject: Optional[str] = None
    status: str
    sent_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime


class CommLogListResponse(BaseModel):
    """Paginated communication log list."""

    items: List[CommLogResponse]
    total: int
    page: int
    page_size: int
