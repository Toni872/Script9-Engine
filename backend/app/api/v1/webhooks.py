"""Endpoints de webhooks externos (Stripe, etc.)."""

from fastapi import APIRouter, Request

router = APIRouter(tags=["webhooks"])


@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request) -> dict[str, bool]:
    """Placeholder para webhook de Stripe.

    TODO: verificar firma con stripe_webhook_secret y procesar evento.
    """
    _payload = await request.body()
    return {"received": True}
