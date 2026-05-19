"""Webhook handlers para integración externa (Stripe).

Usa script9-billing como procesador compartido de webhooks.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Usuario
from script9_billing.core import configure
from script9_billing.models import WebhookEvent
from script9_billing.webhook import process_webhook

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class Script9Callbacks:
    """Callbacks de Script9 Engine para eventos de Stripe."""

    def __init__(self) -> None:
        self._db: AsyncSession | None = None

    def _lookup_key_to_plan(self, lookup_key: str | None) -> str:
        """Convierte un lookup_key de Stripe en nombre de plan interno."""
        if not lookup_key:
            return "trial"
        mapping = {
            "starter_monthly": "starter",
            "pro_monthly": "professional",
            "enterprise_monthly": "enterprise",
        }
        return mapping.get(lookup_key, "trial")

    def on_checkout_completed(self, event: WebhookEvent, db: AsyncSession) -> None:
        """Vincula customer + suscripción al usuario."""
        import asyncio
        asyncio.create_task(self._handle_checkout(event, db))

    async def _handle_checkout(self, event: WebhookEvent, db: AsyncSession) -> None:
        if not event.user_id:
            return

        result = await db.execute(
            select(Usuario).where(Usuario.firebase_uid == event.user_id)
        )
        usuario = result.scalar_one_or_none()
        if not usuario:
            return

        usuario.stripe_customer_id = event.customer_id
        usuario.subscription_id = event.subscription_id
        usuario.subscription_status = event.subscription_status
        usuario.plan_suscripcion = self._lookup_key_to_plan(event.lookup_key)

        if event.current_period_end:
            usuario.current_period_end = event.current_period_end

        await db.commit()

    def on_subscription_updated(self, event: WebhookEvent, db: AsyncSession) -> None:
        """Sincroniza cambios de plan y estado."""
        import asyncio
        asyncio.create_task(self._handle_subscription_update(event, db))

    async def _handle_subscription_update(
        self, event: WebhookEvent, db: AsyncSession
    ) -> None:
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
        usuario.plan_suscripcion = self._lookup_key_to_plan(event.lookup_key)

        if event.current_period_end:
            usuario.current_period_end = event.current_period_end

        await db.commit()

    def on_subscription_deleted(self, event: WebhookEvent, db: AsyncSession) -> None:
        """Revierte a trial cuando se cancela la suscripción."""
        import asyncio
        asyncio.create_task(self._handle_subscription_deleted(event, db))

    async def _handle_subscription_deleted(
        self, event: WebhookEvent, db: AsyncSession
    ) -> None:
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


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Maneja eventos de Stripe usando el procesador compartido."""
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
        return {"received": True, "type": event.type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error de webhook: {e}")
