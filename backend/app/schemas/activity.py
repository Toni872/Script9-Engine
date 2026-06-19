"""
Schemas Pydantic para ActivityEvent.

Solo se exponen response schemas; los eventos se crean internamente
mediante activity_service.log_event(), nunca desde endpoints públicos.
"""

from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class ActivityEventResponse(BaseModel):
    """Representación de un único evento de actividad."""

    model_config = ConfigDict(extra="forbid", from_attributes=True, populate_by_name=True)

    id: int
    user_id: int
    app: str
    tipo: str
    payload: dict[str, Any] = Field(alias="metadata", serialization_alias="metadata")
    creado_en: datetime.datetime


class ActivityFeedResponse(BaseModel):
    """Feed paginado de eventos de actividad."""

    model_config = ConfigDict(extra="forbid")

    total: int = Field(..., ge=0, description="Total de eventos en el período")
    days: int = Field(..., ge=1, description="Ventana de tiempo consultada (días)")
    events: list[ActivityEventResponse]
