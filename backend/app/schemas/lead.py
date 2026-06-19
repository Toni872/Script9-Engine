"""
Schemas Pydantic para Lead.

LeadCreate es el schema público (sin autenticación requerida en el POST).
LeadUpdate y LeadResponse son internos (requieren autenticación).
"""

from __future__ import annotations

import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ---------------------------------------------------------------------------
# Tipos internos
# ---------------------------------------------------------------------------

EstadoLead = Literal["new", "qualified", "rejected", "converted"]


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class LeadCreate(BaseModel):
    """
    Payload público para capturar un lead desde un formulario externo.

    Los campos `app`, `user_id` y `score` se resuelven en el backend,
    nunca vienen del cuerpo del request.
    """

    model_config = ConfigDict(extra="forbid")

    slug: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    nombre: str = Field(..., min_length=1, max_length=255)
    empresa: str = Field(..., min_length=1, max_length=255)
    mensaje: str = Field(..., min_length=1)
    telefono: str | None = Field(default=None, max_length=50)


class LeadUpdate(BaseModel):
    """Payload interno para actualizar estado o datos de un lead."""

    model_config = ConfigDict(extra="forbid")

    estado: EstadoLead | None = None
    score: int | None = Field(default=None, ge=0, le=100)
    nombre: str | None = Field(default=None, min_length=1, max_length=255)
    empresa: str | None = Field(default=None, min_length=1, max_length=255)
    telefono: str | None = Field(default=None, max_length=50)


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class LeadResponse(BaseModel):
    """Representación completa de un lead."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    user_id: int
    app: str
    slug: str
    email: str
    nombre: str
    empresa: str
    mensaje: str
    telefono: str | None
    score: int
    estado: str
    creado_en: datetime.datetime
