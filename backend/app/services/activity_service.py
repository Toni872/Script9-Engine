"""
Servicio de actividad — registro y consulta de ActivityEvent.

Todas las funciones son async y reciben una SQLAlchemy AsyncSession.
El filtrado por (user_id, app) garantiza el aislamiento multi-tenant.
"""

from __future__ import annotations

import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ActivityEvent


# ---------------------------------------------------------------------------
# Tipos internos
# ---------------------------------------------------------------------------

TipoEvento = str  # "lead_captured" | "meeting_scheduled" | ... (open string para extensibilidad)


# ---------------------------------------------------------------------------
# Funciones públicas
# ---------------------------------------------------------------------------

async def log_event(
    session: AsyncSession,
    *,
    user_id: int,
    app: str,
    tipo: TipoEvento,
    metadata: dict[str, Any] | None = None,
) -> ActivityEvent:
    """
    Inserta un nuevo ActivityEvent en la base de datos.

    Args:
        session: Sesión async de SQLAlchemy (inyectada por FastAPI).
        user_id: ID del usuario propietario del evento.
        app: Discriminador de app/tenant.
        tipo: Tipo de evento (ej: "lead_captured").
        metadata: Datos enriquecidos del evento (opcional, default={}).

    Returns:
        El objeto ActivityEvent recién creado y persistido.
    """
    event = ActivityEvent(
        user_id=user_id,
        app=app,
        tipo=tipo,
        metadata=metadata or {},
        creado_en=datetime.datetime.utcnow(),
    )
    session.add(event)
    await session.flush()   # obtiene el ID sin commit (deja el control al caller)
    await session.refresh(event)
    return event


async def get_feed(
    session: AsyncSession,
    *,
    user_id: int,
    app: str,
    days: int = 7,
) -> list[ActivityEvent]:
    """
    Devuelve los ActivityEvent del usuario/app en los últimos `days` días.

    Los resultados se ordenan del más reciente al más antiguo.

    Args:
        session: Sesión async de SQLAlchemy.
        user_id: ID del usuario propietario.
        app: Discriminador de app/tenant.
        days: Ventana de tiempo en días (default=7).

    Returns:
        Lista de ActivityEvent ordenados por creado_en DESC.
    """
    desde = datetime.datetime.utcnow() - datetime.timedelta(days=days)

    stmt = (
        select(ActivityEvent)
        .where(
            ActivityEvent.user_id == user_id,
            ActivityEvent.app == app,
            ActivityEvent.creado_en >= desde,
        )
        .order_by(ActivityEvent.creado_en.desc())
    )

    result = await session.execute(stmt)
    return list(result.scalars().all())
