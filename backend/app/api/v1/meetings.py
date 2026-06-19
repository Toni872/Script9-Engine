"""
Endpoints para gestión de reuniones.

- POST /meetings — protegido
- GET /meetings — protegido con TenantFilter
- PATCH /meetings/{id} — protegido, solo owner
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.dependencies.tenant import TenantFilter, get_tenant_filter
from app.models import Lead, Meeting, Usuario
from app.schemas.meeting import MeetingCreate, MeetingResponse, MeetingUpdate
from app.services.activity_service import log_event
from app.services.rate_limit import limiter

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.post("", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_meeting(
    request: Request,
    payload: MeetingCreate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeetingResponse:
    """
    Agenda una reunión asociada a un lead existente.

    El lead debe pertenecer al usuario autenticado.
    """
    # Verificar que el lead existe y pertenece al usuario
    stmt = (
        select(Lead)
        .where(Lead.id == payload.lead_id)
        .where(Lead.user_id == current_user.id)
        .where(Lead.app == current_user.tenant_id)
    )
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead no encontrado o no pertenece al usuario",
        )

    # Crear reunión
    meeting = Meeting(
        user_id=current_user.id,
        lead_id=payload.lead_id,
        app=current_user.tenant_id,
        scheduled_at=payload.scheduled_at,
        status=payload.status,
        external_id=payload.external_id,
    )
    db.add(meeting)
    await db.flush()
    await db.refresh(meeting)

    # Loguear evento
    await log_event(
        db,
        user_id=current_user.id,
        app=current_user.tenant_id,
        tipo="meeting_scheduled",
        metadata={
            "meeting_id": meeting.id,
            "lead_id": lead.id,
            "scheduled_at": meeting.scheduled_at.isoformat(),
        },
    )

    return meeting


@router.get("", response_model=list[MeetingResponse])
async def list_meetings(
    tenant: TenantFilter = Depends(get_tenant_filter),
    db: AsyncSession = Depends(get_db),
) -> list[MeetingResponse]:
    """Lista todas las reuniones del tenant actual."""
    stmt = (
        select(Meeting)
        .where(*tenant.filters(Meeting))
        .order_by(Meeting.scheduled_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    payload: MeetingUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MeetingResponse:
    """
    Actualiza una reunión existente.

    Solo el dueño de la reunión puede actualizarla.
    Al cambiar status a 'confirmed' o 'cancelled' se loguea el evento correspondiente.
    """
    # Obtener reunión existente
    stmt = (
        select(Meeting)
        .where(Meeting.id == meeting_id)
        .where(Meeting.user_id == current_user.id)
        .where(Meeting.app == current_user.tenant_id)
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()

    if not meeting:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reunión no encontrada o no pertenece al usuario",
        )

    # Guardar status anterior para detectar cambios
    old_status = meeting.status

    # Aplicar actualizaciones
    if payload.scheduled_at is not None:
        meeting.scheduled_at = payload.scheduled_at
    if payload.status is not None:
        meeting.status = payload.status
    if payload.external_id is not None:
        meeting.external_id = payload.external_id

    await db.flush()
    await db.refresh(meeting)

    # Loguear cambios de status
    if payload.status is not None and payload.status != old_status:
        event_type = (
            "meeting_confirmed"
            if payload.status == "confirmed"
            else "meeting_cancelled"
            if payload.status == "cancelled"
            else None
        )
        if event_type:
            await log_event(
                db,
                user_id=current_user.id,
                app=current_user.tenant_id,
                tipo=event_type,
                metadata={
                    "meeting_id": meeting.id,
                    "lead_id": meeting.lead_id,
                    "old_status": old_status,
                    "new_status": payload.status,
                },
            )

    return meeting
