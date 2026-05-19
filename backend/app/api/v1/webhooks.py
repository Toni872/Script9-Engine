"""Webhook handlers para integración externa (Stripe)."""
from datetime import datetime, timezone

import stripe
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Usuario
from app.services.stripe_service import ensure_stripe

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/stripe")
async def stripe_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    """Maneja eventos de Stripe: checkout completado, actualizaciones de suscripción."""

    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook no configurado")

    body = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Firma Stripe requerida")

    try:
        event = stripe.Webhook.construct_event(
            payload=body,
            sig_header=sig_header,
            secret=settings.stripe_webhook_secret,
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Body inválido")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Firma inválida")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await _handle_checkout_completed(data, db)
    elif event_type == "customer.subscription.updated":
        await _handle_subscription_updated(data, db)
    elif event_type == "customer.subscription.deleted":
        await _handle_subscription_deleted(data, db)

    return {"received": True}


async def _handle_checkout_completed(session: dict, db: AsyncSession) -> None:
    """Vincula el customer de Stripe al usuario y asigna suscripción inicial."""
    customer_id = session.get("customer")
    client_ref = session.get("client_reference_id")
    subscription_id = session.get("subscription")

    if not client_ref and not customer_id:
        return

    query = select(Usuario)
    if client_ref:
        query = query.where(Usuario.firebase_uid == client_ref)
    else:
        query = query.where(Usuario.stripe_customer_id == customer_id)

    result = await db.execute(query)
    usuario = result.scalar_one_or_none()

    if not usuario:
        return

    usuario.stripe_customer_id = customer_id

    if subscription_id:
        ensure_stripe()
        subscription = stripe.Subscription.retrieve(subscription_id)
        if subscription.get("items") and subscription["items"].get("data"):
            price_id = subscription["items"]["data"][0]["price"]["id"]
            usuario.subscription_id = subscription_id
            usuario.subscription_status = subscription.get("status")
            usuario.current_period_end = datetime.fromtimestamp(
                subscription.get("current_period_end"),
                tz=timezone.utc,
            )
            plan_map = {
                settings.starter_price_id: "starter",
                settings.professional_price_id: "professional",
                settings.enterprise_price_id: "enterprise",
            }
            usuario.plan_suscripcion = plan_map.get(price_id, "trial")

    await db.commit()


async def _handle_subscription_updated(subscription: dict, db: AsyncSession) -> None:
    """Sincroniza cambios de plan y estado de suscripción."""
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    result = await db.execute(
        select(Usuario).where(Usuario.stripe_customer_id == customer_id)
    )
    usuario = result.scalar_one_or_none()

    if not usuario:
        return

    usuario.subscription_id = subscription.get("id")
    usuario.subscription_status = subscription.get("status")

    if subscription.get("current_period_end"):
        usuario.current_period_end = datetime.fromtimestamp(
            subscription["current_period_end"],
            tz=timezone.utc,
        )

    if subscription.get("items") and subscription["items"].get("data"):
        price_id = subscription["items"]["data"][0]["price"]["id"]
        plan_map = {
            settings.starter_price_id: "starter",
            settings.professional_price_id: "professional",
            settings.enterprise_price_id: "enterprise",
        }
        usuario.plan_suscripcion = plan_map.get(price_id, "trial")

    await db.commit()


async def _handle_subscription_deleted(subscription: dict, db: AsyncSession) -> None:
    """Revierte a trial cuando se cancela la suscripción."""
    customer_id = subscription.get("customer")
    if not customer_id:
        return

    result = await db.execute(
        select(Usuario).where(Usuario.stripe_customer_id == customer_id)
    )
    usuario = result.scalar_one_or_none()

    if not usuario:
        return

    usuario.plan_suscripcion = "trial"
    usuario.subscription_status = "canceled"
    usuario.subscription_id = None

    await db.commit()
