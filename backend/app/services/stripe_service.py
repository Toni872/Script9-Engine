"""Servicio de integración con Stripe para suscripciones."""

import stripe
from app.config import settings

_stripe_client = None


def get_stripe_client() -> stripe.Stripe:
    global _stripe_client
    if _stripe_client is None:
        stripe.api_key = settings.stripe_secret_key
        _stripe_client = stripe
    return _stripe_client


async def create_checkout_session(
    customer_id: str, price_id: str, success_url: str, cancel_url: str
) -> str:
    """Crea una Checkout Session de Stripe y devuelve la URL."""
    stripe_client = get_stripe_client()
    session = stripe_client.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
    )
    return session.url


async def create_customer_portal_session(customer_id: str, return_url: str) -> str:
    """Crea una sesión del Customer Portal de Stripe y devuelve la URL."""
    stripe_client = get_stripe_client()
    session = stripe_client.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return session.url


async def get_or_create_stripe_customer(
    email: str, nombre: str, firebase_uid: str
) -> str:
    """Obtiene un cliente existente en Stripe o crea uno nuevo."""
    stripe_client = get_stripe_client()
    customers = stripe_client.Customer.list(email=email, limit=1)
    if customers.data:
        return customers.data[0].id
    customer = stripe_client.Customer.create(
        email=email,
        name=nombre,
        metadata={"firebase_uid": firebase_uid},
    )
    return customer.id
