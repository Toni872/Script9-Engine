"""
Schemas Pydantic para Cotizacion.

Separación request/response explícita.
Regla: extra="forbid" en todos los schemas de request.
"""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Tipos internos
# ---------------------------------------------------------------------------

PlanInterno = Literal["starter", "professional", "enterprise"]


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class CotizacionCreate(BaseModel):
    """Payload para crear una nueva cotización. El campo `app` se resuelve del usuario autenticado."""

    model_config = ConfigDict(extra="forbid")

    plan_interno: PlanInterno
    precio_eur: Decimal = Field(..., ge=0, decimal_places=2)
    stripe_price_id: str | None = None
    stripe_subscription_id: str | None = None
    valido_hasta: datetime.date | None = None
    notas_admin: str | None = None


class CotizacionUpdate(BaseModel):
    """Payload para actualizar campos de una cotización existente. Todos los campos son opcionales."""

    model_config = ConfigDict(extra="forbid")

    plan_interno: PlanInterno | None = None
    precio_eur: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    stripe_price_id: str | None = None
    stripe_subscription_id: str | None = None
    valido_hasta: datetime.date | None = None
    notas_admin: str | None = None


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class CotizacionResponse(BaseModel):
    """Representación pública de una cotización."""

    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: int
    user_id: int
    app: str
    plan_interno: str
    precio_eur: Decimal
    stripe_price_id: str | None
    stripe_subscription_id: str | None
    valido_hasta: datetime.date | None
    notas_admin: str | None
    creado_en: datetime.datetime
    actualizado_en: datetime.datetime
