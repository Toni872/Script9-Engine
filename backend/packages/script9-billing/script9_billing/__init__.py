"""script9-billing — Módulo compartido de facturación Stripe para el ecosistema Script9.

Uso básico (cualquier framework):
    from script9_billing import create_checkout_session, create_portal_session
    url = create_checkout_session(lookup_key="starter_monthly", ...)

Uso con FastAPI (plug-and-play):
    from script9_billing.fastapi import create_billing_router
    app.include_router(create_billing_router(...))
"""

from script9_billing.core import create_checkout_session, create_portal_session
from script9_billing.models import CheckoutResult, PortalResult, WebhookEvent
from script9_billing.webhook import process_webhook, StripeCallbacks

__all__ = [
    "create_checkout_session",
    "create_portal_session",
    "process_webhook",
    "StripeCallbacks",
    "CheckoutResult",
    "PortalResult",
    "WebhookEvent",
]
