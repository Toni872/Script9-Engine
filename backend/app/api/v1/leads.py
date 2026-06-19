"""
Endpoints para gestión de leads.

- POST /leads — público con rate limit
- GET /leads — protegido con TenantFilter
- GET /leads/{lead_id} — protegido
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies.tenant import TenantFilter, get_tenant_filter
from app.models import Lead, Usuario
from app.schemas.lead import LeadCreate, LeadResponse
from app.services.activity_service import log_event
from app.services.lead_scoring import score_lead
from app.services.rate_limit import limiter

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def create_lead(
    request: Request,
    payload: LeadCreate,
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """
    Captura un lead público.

    Requiere rate limit: 10 solicitudes por minuto por IP.
    El user_id se resuelve buscando un usuario por email o creando uno nuevo.
    """
    # Buscar usuario existente por email o crear uno nuevo (anonimous lead owner)
    result = await db.execute(select(Usuario).where(Usuario.email == payload.email))
    usuario = result.scalar_one_or_none()

    if not usuario:
        # Crear usuario anónimo para el lead
        usuario = Usuario(
            firebase_uid=f"anonymous_{payload.email}",
            email=payload.email,
            nombre=payload.nombre,
            tenant_id="script9",
        )
        db.add(usuario)
        await db.flush()

    # Calcular score
    score = score_lead(
        email=payload.email,
        mensaje=payload.mensaje,
        telefono=payload.telefono,
    )

    # Crear lead
    lead = Lead(
        user_id=usuario.id,
        app="script9",
        slug=payload.slug,
        email=payload.email,
        nombre=payload.nombre,
        empresa=payload.empresa,
        mensaje=payload.mensaje,
        telefono=payload.telefono,
        score=score,
        estado="new",
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)

    # Loguear evento
    await log_event(
        db,
        user_id=usuario.id,
        app="script9",
        tipo="lead_captured",
        metadata={
            "lead_id": lead.id,
            "email": lead.email,
            "score": score,
            "slug": lead.slug,
        },
    )

    return lead


@router.get("", response_model=list[LeadResponse])
async def list_leads(
    tenant: TenantFilter = Depends(get_tenant_filter),
    db: AsyncSession = Depends(get_db),
) -> list[LeadResponse]:
    """Lista todos los leads del tenant actual."""
    stmt = select(Lead).where(*tenant.filters(Lead)).order_by(Lead.creado_en.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    tenant: TenantFilter = Depends(get_tenant_filter),
    db: AsyncSession = Depends(get_db),
) -> LeadResponse:
    """Obtiene un lead por ID."""
    stmt = (
        select(Lead)
        .where(Lead.id == lead_id)
        .where(*tenant.filters(Lead))
    )
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead no encontrado")

    return lead
