"""Servicio de integración con Stripe para suscripciones."""

import stripe
from app.config import settings


def ensure_stripe() -> None:
    """Inicializa la API key de Stripe (idempotente)."""
    if stripe.api_key:
        return
    stripe.api_key = settings.stripe_secret_key


async def create_checkout_session(
    customer_id: str, price_id: str, success_url: str, cancel_url: str
) -> str:
    """Crea una Checkout Session de Stripe y devuelve la URL."""
    ensure_stripe()
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


async def create_customer_portal_session(customer_id: str, return_url: str) -> str:
    """Crea una sesión del Customer Portal de Stripe y devuelve la URL."""
    ensure_stripe()
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


async def get_or_create_stripe_customer(
    email: str, nombre: str, firebase_uid: str
) -> str:
    """Obtiene un cliente existente en Stripe o crea uno nuevo."""
    ensure_stripe()
    customers = stripe.Customer.list(email=email, limit=1)
    if customers.data:
        return customers.data[0].id
    customer = stripe.Customer.create(
        email=email,
        name=nombre,
        metadata={"firebase_uid": firebase_uid},
    )
    return customer.id
