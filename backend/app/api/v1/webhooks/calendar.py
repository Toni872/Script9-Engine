"""
Webhook para recibir eventos de Cal.com.

- POST /webhooks/calendar — maneja BOOKING_CREATED, BOOKING_CONFIRMED, BOOKING_CANCELLED
"""
from __future__ import annotations

import hashlib
import hmac
import structlog
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.dependencies.tenant import TenantFilter, get_tenant_filter
from app.models import ActivityEvent, Lead, Meeting
from app.services.activity_service import log_event

router = APIRouter(prefix="/calendar", tags=["webhooks-calendar"])

logger = structlog.get_logger(__name__)


def _verify_calcom_signature(payload: bytes, signature: str | None, secret: str) -> bool:
    """
    Verifica la firma de Cal.com usando HMAC-SHA256.

    Cal.com firma el payload con el secret del webhook usando HMAC-SHA256.
    """
    if not signature:
        return False

    expected = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected}", signature)


async def _get_tenant_from_lead(db: AsyncSession, external_id: str) -> TenantFilter | None:
    """Busca el tenant asociado a un meeting por external_id."""
    stmt = (
        select(Meeting)
        .where(Meeting.external_id == external_id)
        .limit(1)
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()

    if meeting:
        return TenantFilter(tenant_id=meeting.app, user_id=meeting.user_id)
    return None


@router.post("")
async def handle_calendar_webhook(
    request: Request,
    x_cal_com_signature: str | None = Header(default=None, alias="x-cal-com-signature"),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """
    Procesa webhooks de Cal.com.

    Tipos de evento:
    - BOOKING_CREATED: nueva reunión propuesta
    - BOOKING_CONFIRMED: reunión confirmada
    - BOOKING_CANCELLED: reunión cancelada
    """
    body = await request.body()

    # Verificar firma si está configurada
    if settings.stripe_webhook_secret and x_cal_com_signature:
        if not _verify_calcom_signature(body, x_cal_com_signature, settings.stripe_webhook_secret):
            logger.warning("webhook.calcom.invalid_signature")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Firma inválida",
            )

    try:
        event: dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JSON inválido",
        )

    event_type = event.get("type") or event.get("eventType")
    payload = event.get("payload", {})

    logger.info(
        "webhook.calcom.received",
        event_type=event_type,
        booking_id=payload.get("uid"),
    )

    external_id = payload.get("uid") or payload.get("bookingId")
    if not external_id:
        return {"status": "ignored"}

    # Buscar reunión existente
    stmt = (
        select(Meeting)
        .where(Meeting.external_id == external_id)
        .limit(1)
    )
    result = await db.execute(stmt)
    meeting = result.scalar_one_or_none()

    if event_type in ("BOOKING_CREATED", "BOOKING_REQUESTED"):
        # Nueva reunión — crear si no existe
        if not meeting:
            # Necesitamos user_id y app — buscar por email del organizador o lead
            # Por ahora solo logueamos y retornamos
            logger.info("webhook.calcom.booking_created.ignored", reason="no_matching_user")
            return {"status": "created_ignored"}

        meeting.status = "proposed"
        await db.flush()

        await log_event(
            db,
            user_id=meeting.user_id,
            app=meeting.app,
            tipo="meeting_scheduled",
            metadata={
                "meeting_id": meeting.id,
                "external_id": external_id,
                "source": "calcom",
            },
        )

    elif event_type == "BOOKING_CONFIRMED":
        if meeting:
            old_status = meeting.status
            meeting.status = "confirmed"
            await db.flush()

            if old_status != "confirmed":
                await log_event(
                    db,
                    user_id=meeting.user_id,
                    app=meeting.app,
                    tipo="meeting_confirmed",
                    metadata={
                        "meeting_id": meeting.id,
                        "lead_id": meeting.lead_id,
                        "source": "calcom",
                    },
                )

    elif event_type == "BOOKING_CANCELLED":
        if meeting:
            old_status = meeting.status
            meeting.status = "cancelled"
            await db.flush()

            if old_status != "cancelled":
                await log_event(
                    db,
                    user_id=meeting.user_id,
                    app=meeting.app,
                    tipo="meeting_cancelled",
                    metadata={
                        "meeting_id": meeting.id,
                        "lead_id": meeting.lead_id,
                        "source": "calcom",
                    },
                )

    else:
        logger.info("webhook.calcom.unknown_event_type", event_type=event_type)

    return {"status": "ok"}
