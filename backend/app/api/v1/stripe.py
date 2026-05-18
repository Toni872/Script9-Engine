"""Endpoints para integración con Stripe."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Usuario
from app.schemas.stripe import CheckoutRequest, CheckoutResponse, PortalResponse
from app.services.stripe_service import (
    create_checkout_session,
    create_customer_portal_session,
    get_or_create_stripe_customer,
)

router = APIRouter(prefix="/stripe", tags=["stripe"])


@router.post("/checkout", response_model=CheckoutResponse)
async def checkout(
    req: CheckoutRequest,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not settings.stripe_secret_key:
        raise HTTPException(status_code=503, detail="Stripe no configurado")

    if not usuario.stripe_customer_id:
        customer_id = await get_or_create_stripe_customer(
            email=usuario.email,
            nombre=usuario.nombre,
            firebase_uid=usuario.firebase_uid,
        )
        usuario.stripe_customer_id = customer_id
        await db.commit()
    else:
        customer_id = usuario.stripe_customer_id

    success_url = f"{settings.frontend_url}/dashboard?checkout=success"
    cancel_url = f"{settings.frontend_url}/pricing?checkout=canceled"

    url = await create_checkout_session(
        customer_id=customer_id,
        price_id=req.price_id,
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return CheckoutResponse(url=url)


@router.post("/portal", response_model=PortalResponse)
async def portal(
    usuario: Usuario = Depends(get_current_user),
):
    if not usuario.stripe_customer_id:
        raise HTTPException(status_code=400, detail="Sin suscripción activa")

    return_url = f"{settings.frontend_url}/settings"

    url = await create_customer_portal_session(
        customer_id=usuario.stripe_customer_id,
        return_url=return_url,
    )
    return PortalResponse(url=url)
