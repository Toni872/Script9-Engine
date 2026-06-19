"""
Endpoints para gestión de cotizaciones del usuario autenticado.

- GET /cotizaciones/me — protegido
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.tenant import TenantFilter, get_tenant_filter
from app.models import Cotizacion
from app.schemas.cotizacion import CotizacionResponse

router = APIRouter(prefix="/cotizaciones", tags=["cotizaciones"])


@router.get("/me", response_model=CotizacionResponse)
async def get_my_cotizacion(
    tenant: TenantFilter = Depends(get_tenant_filter),
    db: AsyncSession = Depends(get_db),
) -> CotizacionResponse:
    """
    Devuelve la cotización del usuario autenticado para su app/tenant.

    Retorna 404 si no existe ninguna cotización.
    """
    stmt = (
        select(Cotizacion)
        .where(Cotizacion.user_id == tenant.user_id)
        .where(Cotizacion.app == tenant.tenant_id)
        .order_by(Cotizacion.creado_en.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    cotizacion = result.scalar_one_or_none()

    if not cotizacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sin cotización asociada",
        )

    return cotizacion
