"""
Schemas Pydantic para Meeting.

El campo `app` se inyecta desde el usuario autenticado; nunca viene del body.
"""

from __future__ import annotations

import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Tipos internos
# ---------------------------------------------------------------------------

StatusMeeting = Literal["proposed", "confirmed", "cancelled"]


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class MeetingCreate(BaseModel):
    """Payload para agendar una reunión asociada a un lead existente."""

    model_config = ConfigDict(extra="forbid")

    lead_id: int
    scheduled_at: datetime.datetime
    status: StatusMeeting = "proposed"
    external_id: str | None = Field(default=None, max_length=255)


class MeetingUpdate(BaseModel):
    """Payload para actualizar estado o datos de una reunión."""

    model_config = ConfigDict(extra="forbid")

    scheduled_at: datetime.datetime | None = None
    status: StatusMeeting | None = None
    external_id: str | None = Field(default=None, max_length=255)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class MeetingResponse(BaseModel):
    """Representación completa de una reunión."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    user_id: int
    lead_id: int
    app: str
    scheduled_at: datetime.datetime
    status: str
    external_id: str | None
    created_at: datetime.datetime
