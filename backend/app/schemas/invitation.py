"""
Schemas Pydantic para invitaciones.
"""
from __future__ import annotations

import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class InvitationCreate(BaseModel):
    """Payload para crear una invitación."""
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    app: str = "script9"
    plan_interno: str = Field(..., description="starter | professional | enterprise")
    precio_eur: Decimal = Field(..., ge=0, decimal_places=2)
    notas_admin: str | None = None


class InvitationResponse(BaseModel):
    """Respuesta con los datos de la invitación creada."""
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    email: str
    app: str
    plan_interno: str
    precio_eur: Decimal
    token: str
    aceptada: bool
    expires_at: datetime.datetime
    creado_en: datetime.datetime
