"""
Webhook CRM — envía leads a HubSpot cuando el score >= 70.

- POST /webhooks/crm — triggered internamente después de crear un lead
"""
from __future__ import annotations

import structlog
from typing import Any

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Lead
from app.services.activity_service import log_event

router = APIRouter(prefix="/crm", tags=["webhooks-crm"])

logger = structlog.get_logger(__name__)

# Score mínimo para sincronizar con HubSpot
_HUBSPOT_SCORE_THRESHOLD = 70


async def _sync_lead_to_hubspot(lead: Lead) -> bool:
    """
    Envía un lead a HubSpot via API v3.

    Returns:
        True si se sincronizó correctamente, False si falló o no está configurado.
    """
    if not settings.HUBSPOT_API_KEY:
        logger.debug("webhook.crm.hubspot_not_configured")
        return False

    hubspot_payload = {
        "properties": {
            "email": lead.email,
            "firstname": lead.nombre.split()[0] if lead.nombre else "",
            "lastname": " ".join(lead.nombre.split()[1:]) if lead.nombre else "",
            "company": lead.empresa,
            "phone": lead.telefono or "",
            "lead_score": str(lead.score),
            "lead_status": lead.estado,
            "hs_lead_status": "NEW" if lead.estado == "new" else "OPEN",
        }
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.hubapi.com/crm/v3/objects/contacts",
                headers={
                    "Authorization": f"Bearer {settings.HUBSPOT_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=hubspot_payload,
            )

        if response.status_code in (200, 201):
            logger.info(
                "webhook.crm.hubspot_synced",
                lead_id=lead.id,
                email=lead.email,
                score=lead.score,
            )
            return True

        logger.warning(
            "webhook.crm.hubspot_error",
            lead_id=lead.id,
            status_code=response.status_code,
            detail=response.text[:200],
        )
        return False

    except httpx.TimeoutException:
        logger.warning("webhook.crm.hubspot_timeout", lead_id=lead.id)
        return False
    except Exception as e:
        logger.error("webhook.crm.hubspot_exception", lead_id=lead.id, error=str(e))
        return False


@router.post("")
async def handle_crm_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Endpoint para sincronizar un lead con HubSpot.

    Body:
        lead_id: ID del lead a sincronizar

    Condiciones:
    - El lead debe tener score >= 70
    - HubSpot API key debe estar configurada
    """
    try:
        body: dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JSON inválido",
        )

    lead_id = body.get("lead_id")
    if not lead_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="lead_id requerido",
        )

    # Obtener lead
    stmt = select(Lead).where(Lead.id == lead_id).limit(1)
    result = await db.execute(stmt)
    lead = result.scalar_one_or_none()

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead no encontrado",
        )

    # Verificar score mínimo
    if lead.score < _HUBSPOT_SCORE_THRESHOLD:
        return {
            "status": "skipped",
            "reason": f"score {lead.score} < {_HUBSPOT_SCORE_THRESHOLD}",
        }

    # Sincronizar con HubSpot
    synced = await _sync_lead_to_hubspot(lead)

    if synced:
        # Loguear evento
        await log_event(
            db,
            user_id=lead.user_id,
            app=lead.app,
            tipo="crm_synced",
            metadata={
                "lead_id": lead.id,
                "email": lead.email,
                "score": lead.score,
                "provider": "hubspot",
            },
        )

    return {
        "status": "ok" if synced else "error",
        "lead_id": lead_id,
        "synced": synced,
    }
