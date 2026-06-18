"""Endpoints para integración con Stripe.

Usa script9-billing como engine de facturación compartido.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from script9_billing.core import configure, create_checkout_session, create_portal_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Usuario
from app.schemas.stripe import CheckoutRequest, CheckoutResult, PortalResult
from app.services.rate_limit import limiter

router = APIRouter(prefix="/stripe", tags=["stripe"])


@router.post("/checkout", response_model=CheckoutResult)
@limiter.limit("10/minute")
async def checkout(
    request: Request,
    req: CheckoutRequest,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CheckoutResult:
    """Crea una Checkout Session de Stripe usando lookup_key (no price_id)."""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe no configurado")

    configure(settings.stripe_secret_key)

    success_url = f"{settings.script9_url}/pago-exitoso?app=script9"
    cancel_url = f"{settings.script9_url}/dashboard"

    try:
        url = create_checkout_session(
            lookup_key=req.lookup_key,
            user_uid=usuario.firebase_uid,
            user_email=usuario.email,
            app_name="script9",
            stripe_customer_id=usuario.stripe_customer_id,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        return CheckoutResult(url=url)
    except ValueError as e:
        # Precio no encontrado, lookup_key inválido — error del cliente
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        # Loguear el error completo internamente; no exponer detalles de Stripe al cliente
        import logging
        import stripe
        if isinstance(e, stripe.error.StripeError):
            logging.error("stripe_error", type=type(e).__name__, user_uid=usuario.firebase_uid, detail=str(e))
        else:
            logging.error("stripe_unexpected_error", user_uid=usuario.firebase_uid, detail=str(e))
        raise HTTPException(status_code=502, detail="Error al procesar el pago. Intenta de nuevo.") from e


@router.post("/portal", response_model=PortalResult)
async def portal(
    usuario: Usuario = Depends(get_current_user),
) -> PortalResult:
    """Crea una sesión del Customer Portal de Stripe."""
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe no configurado")

    if not usuario.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Sin suscripción activa")

    configure(settings.stripe_secret_key)

    return_url = f"{settings.script9_url}/dashboard"

    try:
        url = create_portal_session(
            customer_id=usuario.stripe_customer_id,
            return_url=return_url,
        )
        return PortalResult(url=url)
    except Exception as e:
        import logging
        import stripe
        if isinstance(e, stripe.error.StripeError):
            logging.error("stripe_error", type=type(e).__name__, customer_id=usuario.stripe_customer_id, detail=str(e))
        else:
            logging.error("stripe_unexpected_error", customer_id=usuario.stripe_customer_id, detail=str(e))
        raise HTTPException(status_code=502, detail="Error al abrir el portal de facturación. Intenta de nuevo.") from e
