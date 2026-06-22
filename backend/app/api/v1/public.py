"""
Endpoints públicos — sin autenticación.

- POST /public/leads — captura un lead desde un formulario público
  El slug identifica al propietario del formulario. scoring ≥ 70 → email + Slack.
"""

from __future__ import annotations

import structlog
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Lead, Usuario
from app.schemas.lead import LeadCreate
from app.services.activity_service import log_event
from app.services.email_service import MeetingProposalEmail, send_meeting_proposal_email
from app.services.lead_scoring import score_lead
from app.services.slack_service import LeadNotification, notify_lead_to_slack

router = APIRouter(prefix="/public", tags=["public"])
logger = structlog.get_logger(__name__)

# Score mínimo para considerar un lead como "cualificado" y enviar notificaciones
SCORE_THRESHOLD = 70


async def _process_lead_notifications(
    lead: Lead,
    usuario: Usuario,
    slug: str,
) -> dict[str, Any]:
    """
    Background task: score alto → notifica Slack + envía email de propuesta.

    Se ejecuta después de commit para no bloquear la respuesta.
    """
    results: dict[str, Any] = {}

    if lead.score < SCORE_THRESHOLD:
        logger.info(
            "lead_captured_low_score",
            lead_id=lead.id,
            score=lead.score,
            threshold=SCORE_THRESHOLD,
        )
        return results

    # Notificación a Slack
    notification = LeadNotification(
        nombre=lead.nombre,
        email=lead.email,
        empresa=lead.empresa,
        telefono=lead.telefono,
        mensaje=lead.mensaje,
        score=lead.score,
        slug=slug,
        form_url=f"https://script-9.com/l/{slug}",
    )
    slack_ok = await notify_lead_to_slack(notification)
    results["slack_notified"] = slack_ok

    # Email de propuesta de reunión al lead
    # El agendador_url puede personalizarse por usuario en el futuro
    from app.config import settings

    proposal = MeetingProposalEmail(
        lead_nombre=lead.nombre,
        lead_email=lead.email,
        empresa=lead.empresa,
        agendador_url=f"{settings.script9_url}/schedule",
    )
    email_ok = await send_meeting_proposal_email(proposal)
    results["email_sent"] = email_ok

    logger.info(
        "lead_high_score_notifications",
        lead_id=lead.id,
        score=lead.score,
        slack=slack_ok,
        email=email_ok,
    )

    return results


@router.post(
    "/leads",
    status_code=status.HTTP_201_CREATED,
    summary="Capturar lead desde formulario público",
)
async def capture_public_lead(
    request: Request,
    payload: LeadCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Endpoint público para capturar un lead.

    Flujo:
    1. Busca el usuario propietario por public_slug (slug del formulario).
    2. Crea el lead asociado a ese usuario.
    3. Calcula el score automáticamente.
    4. Si score >= 70: en background envía notificación Slack y email de propuesta.

    Rate limit: 10 requests/minuto por IP (aplicado vía middleware global en main.py).
    """
    # Buscar propietario del formulario
    result = await db.execute(select(Usuario).where(Usuario.public_slug == payload.slug))
    usuario = result.scalar_one_or_none()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Formulario no encontrado",
        )

    # Calcular score
    calculated_score = score_lead(
        email=payload.email,
        mensaje=payload.mensaje,
        telefono=payload.telefono,
    )

    # Crear lead
    lead = Lead(
        user_id=usuario.id,
        app=usuario.tenant_id,
        slug=payload.slug,
        email=payload.email,
        nombre=payload.nombre,
        empresa=payload.empresa,
        mensaje=payload.mensaje,
        telefono=payload.telefono,
        score=calculated_score,
        estado="new",
    )
    db.add(lead)
    await db.flush()
    await db.refresh(lead)

    # Log de evento
    await log_event(
        db,
        user_id=usuario.id,
        app=usuario.tenant_id,
        tipo="lead_captured",
        metadata={
            "lead_id": lead.id,
            "email": lead.email,
            "empresa": lead.empresa,
            "score": calculated_score,
            "slug": payload.slug,
            "high_value": calculated_score >= SCORE_THRESHOLD,
        },
    )
    await db.commit()

    # Notificaciones en background si score alto
    if calculated_score >= SCORE_THRESHOLD:
        background_tasks.add_task(
            _process_lead_notifications,
            lead=lead,
            usuario=usuario,
            slug=payload.slug,
        )

    return {
        "success": True,
        "lead_id": lead.id,
        "score": calculated_score,
        "qualified": calculated_score >= SCORE_THRESHOLD,
    }
