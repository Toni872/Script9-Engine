"""
Endpoints para feed de actividad y métricas.

- GET /activity/feed — protegido, eventos de los últimos N días
- GET /activity/metric/leads_this_week — protegido, métrica con sparkline
"""
from __future__ import annotations

import datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.tenant import TenantFilter, get_tenant_filter
from app.models import Lead
from app.schemas.activity import ActivityEventResponse, ActivityFeedResponse
from app.schemas.metric import LeadsThisWeekResponse
from app.services.activity_service import get_feed

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("/feed", response_model=ActivityFeedResponse)
async def get_activity_feed(
    days: int = Query(default=7, ge=1, le=90),
    tenant: TenantFilter = Depends(get_tenant_filter),
    db: AsyncSession = Depends(get_db),
) -> ActivityFeedResponse:
    """
    Devuelve el feed de actividad del usuario para los últimos `days` días.

    Los eventos se ordenan del más reciente al más antiguo.
    """
    events = await get_feed(
        db,
        user_id=tenant.user_id,
        app=tenant.tenant_id,
        days=days,
    )

    return ActivityFeedResponse(
        total=len(events),
        days=days,
        events=[
            ActivityEventResponse(
                id=e.id,
                user_id=e.user_id,
                app=e.app,
                tipo=e.tipo,
                payload=e.payload,
                metadata=e.payload,
                creado_en=e.creado_en,
            )
            for e in events
        ],
    )


@router.get("/metric/leads_this_week", response_model=LeadsThisWeekResponse)
async def get_leads_this_week(
    tenant: TenantFilter = Depends(get_tenant_filter),
    db: AsyncSession = Depends(get_db),
) -> LeadsThisWeekResponse:
    """
    Métrica de leads capturados esta semana vs semana anterior.

    Incluye sparkline con conteos diarios de los últimos 7 días.
    """
    now = datetime.datetime.utcnow()
    today = now.date()
    week_ago = now - datetime.timedelta(days=7)
    two_weeks_ago = now - datetime.timedelta(days=14)

    # Total de esta semana
    stmt_this_week = (
        select(Lead)
        .where(Lead.user_id == tenant.user_id)
        .where(Lead.app == tenant.tenant_id)
        .where(Lead.creado_en >= week_ago)
    )
    result_this_week = await db.execute(stmt_this_week)
    leads_this_week = len(list(result_this_week.scalars().all()))

    # Total de semana anterior para calcular delta
    stmt_prev_week = (
        select(Lead)
        .where(Lead.user_id == tenant.user_id)
        .where(Lead.app == tenant.tenant_id)
        .where(Lead.creado_en >= two_weeks_ago)
        .where(Lead.creado_en < week_ago)
    )
    result_prev_week = await db.execute(stmt_prev_week)
    leads_prev_week = len(list(result_prev_week.scalars().all()))

    # Calcular delta porcentual
    if leads_prev_week > 0:
        delta_pct = ((leads_this_week - leads_prev_week) / leads_prev_week) * 100
    else:
        delta_pct = 100.0 if leads_this_week > 0 else 0.0

    # Sparkline: conteo diario de los últimos 7 días
    sparkline: list[int] = []
    for i in range(7):
        day_start = (today - datetime.timedelta(days=6 - i)).isoformat()
        day_end = (today - datetime.timedelta(days=5 - i)).isoformat()

        # Query con raw SQL para obtener conteo por día
        day_query = text(
            """
            SELECT COUNT(*)
            FROM leads
            WHERE user_id = :user_id
              AND app = :app
              AND DATE(creado_en) >= DATE(:day_start)
              AND DATE(creado_en) < DATE(:day_end)
            """
        )
        result = await db.execute(
            day_query,
            {
                "user_id": tenant.user_id,
                "app": tenant.tenant_id,
                "day_start": day_start,
                "day_end": day_end,
            },
        )
        count = result.scalar() or 0
        sparkline.append(int(count))

    return LeadsThisWeekResponse(
        value=leads_this_week,
        delta_pct=round(delta_pct, 2),
        sparkline=sparkline,
    )
