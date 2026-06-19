"""
Schemas para métricas del dashboard.
"""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class LeadsThisWeekResponse(BaseModel):
    """Métrica: leads capturados esta semana."""
    model_config = ConfigDict(extra="forbid")

    value: int = Field(..., description="Cantidad de leads en los últimos 7 días")
    delta_pct: float = Field(..., description="Variación porcentual vs semana anterior")
    sparkline: list[int] = Field(..., description="7 valores, uno por día")
