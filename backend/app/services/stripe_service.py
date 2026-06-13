"""Servicio de integración con Stripe para suscripciones.

DELEGADO a script9-billing. Este archivo existe solo para
mantener compatibilidad con importaciones existentes.
"""

from script9_billing.core import create_checkout_session
from script9_billing.core import create_customer_portal_session as create_portal_session

# Conveniencia: re-exportar configure para inicialización lazy
__all__ = [
    "ensure_stripe",
    "create_checkout_session",
    "create_portal_session",

]


def ensure_stripe() -> None:
    """Inicializa Stripe con la API key (wrapper de script9_billing.core.configure)."""
    # La configuración se maneja desde app.config ahora
    pass
