"""Funciones core de Stripe: checkout y portal de facturación.

Estas funciones son independientes del framework. Cualquier app hija
(Tempos, Script9 Engine, etc.) las puede usar directamente.
"""

import stripe

# Variable global para la API key (se setea una vez desde config)
_initialized = False


def configure(api_key: str) -> None:
    """Configura la API key de Stripe (idempotente, solo la primera vez)."""
    global _initialized
    if not _initialized:
        stripe.api_key = api_key
        _initialized = True


def reset() -> None:
    """Resetea la inicialización (útil para tests)."""
    global _initialized
    stripe.api_key = None  # type: ignore[arg-type]
    _initialized = False


# ─── Lookup Key Resolution ───────────────────────────────────────────────


def _resolve_price_id(lookup_key: str) -> tuple[str, str | None]:
    """Resuelve un lookup_key a su price_id real en Stripe.

    Returns:
        Tuple de (price_id, product_name).

    Raises:
        ValueError: Si no se encuentra el precio en Stripe.
    """
    prices = stripe.Price.list(
        lookup_keys=[lookup_key],
        expand=["data.product"],
        active=True,
        limit=1,
    )

    if not prices.data:
        raise ValueError(
            f"No se encontró un precio activo con lookup_key '{lookup_key}' en Stripe. "
            f"Asegurate de haber creado el precio en el Dashboard de Stripe."
        )

    price = prices.data[0]
    product_name = None
    if hasattr(price, "product") and price.product:
        product_name = getattr(price.product, "name", None)

    return price.id, product_name


# ─── Checkout Session ────────────────────────────────────────────────────


def create_checkout_session(
    lookup_key: str,
    user_uid: str,
    user_email: str,
    app_name: str,
    *,
    stripe_customer_id: str | None = None,
    success_url: str = "https://www.script-9.com/pago-exitoso",
    cancel_url: str = "https://www.script-9.com/dashboard",
) -> str:
    """Crea una Checkout Session de Stripe.

    Args:
        lookup_key: Identificador del plan en Stripe (ej: "starter_monthly").
        user_uid: Firebase UID del usuario (se inyecta en metadata).
        user_email: Email del usuario (pre-poblado en el formulario de pago).
        app_name: Nombre de la app que origina el pago (ej: "tempos").
        stripe_customer_id: Si el usuario ya tiene un customer_id, se reusa.
        success_url: URL de redirección post-pago exitoso.
        cancel_url: URL de redirección si el usuario cancela.

    Returns:
        URL de la Checkout Session de Stripe para redirigir al usuario.

    Raises:
        ValueError: Si el lookup_key no existe en Stripe.
        stripe.error.StripeError: Si la API de Stripe falla.
    """
    if not stripe.api_key:
        raise RuntimeError("Stripe no configurado. Llamá script9_billing.core.configure() primero.")

    price_id, _ = _resolve_price_id(lookup_key)

    session_params: dict = {
        "mode": "subscription",
        "line_items": [{"price": price_id, "quantity": 1}],
        "automatic_tax": {"enabled": True},
        "success_url": success_url,
        "cancel_url": cancel_url,
        "metadata": {
            "userId": user_uid,
            "appName": app_name,
        },
    }

    if stripe_customer_id:
        session_params["customer"] = stripe_customer_id
    else:
        session_params["customer_email"] = user_email

    session = stripe.checkout.Session.create(**session_params)
    return str(session.url)


# ─── Customer Portal ─────────────────────────────────────────────────────


def create_portal_session(
    customer_id: str,
    return_url: str = "https://www.script-9.com/dashboard",
) -> str:
    """Crea una sesión del Customer Portal de Stripe.

    Args:
        customer_id: ID del cliente en Stripe (cus_xxx).
        return_url: URL a la que redirigir cuando el usuario cierra el portal.

    Returns:
        URL del Customer Portal de Stripe.

    Raises:
        stripe.error.StripeError: Si la API de Stripe falla.
    """
    if not stripe.api_key:
        raise RuntimeError("Stripe no configurado. Llamá script9_billing.core.configure() primero.")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url,
    )
    return str(session.url)
