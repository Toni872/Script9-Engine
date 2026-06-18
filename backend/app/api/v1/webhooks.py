"""Webhook handlers para integración externa (Stripe).

Usa script9-billing como procesador compartido de webhooks.
"""


from fastapi import APIRouter, Depends, HTTPException, Request
from script9_billing.core import configure
from script9_billing.models import WebhookEvent as BillingWebhookEvent
from script9_billing.webhook import process_webhook
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Usuario, WebhookEvent

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class Script9Callbacks:
    """Callbacks de Script9 Engine para eventos de Stripe."""

    # Fallback cuando Stripe no tiene metadata.plan_name configurado
    _LOOKUP_KEY_TO_PLAN = {
        "starter_monthly": "starter",
        "pro_monthly": "professional",
        "enterprise_monthly": "enterprise",
    }

    def _resolve_plan_name(self, event: BillingWebhookEvent) -> str:
        """Resuelve el nombre del plan interno desde el evento de Stripe.

        Prioridad:
        1. event.plan_name (viene de Stripe price metadata — lo correcto)
        2. Fallback por lookup_key (retrocompatibilidad)
        3. "trial" si no hay nada
        """
        if event.plan_name:
            return event.plan_name
        if event.lookup_key:
            return self._LOOKUP_KEY_TO_PLAN.get(event.lookup_key, "trial")
        return "trial"

    async def on_checkout_completed(self, event: BillingWebhookEvent, db: AsyncSession) -> None:
        """Vincula customer + suscripción al usuario."""
        await self._handle_checkout(event, db)

    async def _handle_checkout(self, event: BillingWebhookEvent, db: AsyncSession) -> None:
        if not event.user_id:
            return

        result = await db.execute(select(Usuario).where(Usuario.firebase_uid == event.user_id))
        usuario = result.scalar_one_or_none()
        if not usuario:
            return

        usuario.stripe_customer_id = event.customer_id
        usuario.subscription_id = event.subscription_id
        usuario.subscription_status = event.subscription_status
        usuario.plan_suscripcion = self._resolve_plan_name(event)

        if event.current_period_end:
            usuario.current_period_end = event.current_period_end

        await db.commit()

    async def on_subscription_updated(self, event: BillingWebhookEvent, db: AsyncSession) -> None:
        """Sincroniza cambios de plan y estado."""
        await self._handle_subscription_update(event, db)

    async def _handle_subscription_update(self, event: BillingWebhookEvent, db: AsyncSession) -> None:
        if not event.customer_id:
            return

        result = await db.execute(
            select(Usuario).where(Usuario.stripe_customer_id == event.customer_id)
        )
        usuario = result.scalar_one_or_none()
        if not usuario:
            return

        usuario.subscription_id = event.subscription_id
        usuario.subscription_status = event.subscription_status
        usuario.plan_suscripcion = self._resolve_plan_name(event)

        if event.current_period_end:
            usuario.current_period_end = event.current_period_end

        await db.commit()

    async def on_subscription_deleted(self, event: BillingWebhookEvent, db: AsyncSession) -> None:
        """Revierte a trial cuando se cancela la suscripción."""
        await self._handle_subscription_deleted(event, db)

    async def _handle_subscription_deleted(self, event: BillingWebhookEvent, db: AsyncSession) -> None:
        if not event.customer_id:
            return

        result = await db.execute(
            select(Usuario).where(Usuario.stripe_customer_id == event.customer_id)
        )
        usuario = result.scalar_one_or_none()
        if not usuario:
            return

        usuario.plan_suscripcion = "trial"
        usuario.subscription_status = "canceled"
        usuario.subscription_id = None

        await db.commit()


from typing import Any

@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """Maneja eventos de Stripe usando el procesador compartido.

    Idempotencia: si Stripe reenvía el mismo evento, lo detectamos
    vía el event_id y lo ignoramos (devolvemos 200 sin reprocesar).
    """
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook no configurado")

    configure(settings.stripe_secret_key)

    body = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Firma Stripe requerida")

    try:
        event = process_webhook(
            body=body,
            sig_header=sig_header,
            webhook_secret=settings.stripe_webhook_secret,
            callbacks=Script9Callbacks(),
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        # Error de firma o procesamiento — no guardamos en log de eventos
        raise HTTPException(status_code=400, detail="Evento inválido") from e

    # ── Idempotencia ────────────────────────────────────────────────────
    stripe_event_id = event.raw.get("id")
    if stripe_event_id:
        existing = await db.execute(
            select(WebhookEvent).where(WebhookEvent.event_id == stripe_event_id)
        )
        if existing.scalar_one_or_none():
            # Ya procesado — devolver 200 sin reprocesar
            return {"received": True, "type": event.type, "duplicate": True}

        # Marcar como procesado ANTES de retornar
        # (así si Stripe reenvía mientras procesamos, el segundo request ve el registro)
        db.add(WebhookEvent(event_id=stripe_event_id, event_type=event.type, provider="stripe"))
        await db.commit()

    return {"received": True, "type": event.type}
