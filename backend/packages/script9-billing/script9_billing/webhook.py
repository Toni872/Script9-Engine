"""Procesador de Webhooks de Stripe con callbacks para apps hijas.

Cada app hija registra sus propios callbacks y el módulo se encarga
de parsear, validar la firma, y llamar al callback correspondiente.

Uso:
    from script9_billing.webhook import process_webhook, StripeCallbacks

    class MisCallbacks(StripeCallbacks):
        def on_checkout_completed(self, event, db):
            # activar premium en mi DB
            ...

    event = process_webhook(body, sig_header, webhook_secret, MisCallbacks(), db)
"""

from datetime import datetime, timezone
from typing import Any, Optional, Protocol

import stripe

from script9_billing.models import WebhookEvent


class StripeCallbacks(Protocol):
    """Interfaz que cada app hija implementa para recibir eventos de Stripe.

    Todos los métodos son OPCIONALES — implementá solo los que necesites.
    """

    def on_checkout_completed(self, event: WebhookEvent, db: Any) -> None:
        """Se dispara cuando un checkout se completa exitosamente.

        Acá activás premium para el usuario en tu base de datos.
        """

    def on_subscription_created(self, event: WebhookEvent, db: Any) -> None:
        """Se dispara cuando se crea una suscripción nueva."""

    def on_subscription_updated(self, event: WebhookEvent, db: Any) -> None:
        """Se dispara cuando una suscripción cambia (upgrade, downgrade, renovación)."""

    def on_subscription_deleted(self, event: WebhookEvent, db: Any) -> None:
        """Se dispara cuando una suscripción se cancela.

        Acá revertís al usuario a trial.
        """

    def on_invoice_paid(self, event: WebhookEvent, db: Any) -> None:
        """Se dispara cuando una factura se paga exitosamente (renovación)."""

    def on_invoice_payment_failed(self, event: WebhookEvent, db: Any) -> None:
        """Se dispara cuando el pago de una factura falla."""


class _DefaultCallbacks:
    """Callbacks por defecto que no hacen nada — para que no rompa si no se implementan."""

    def on_checkout_completed(self, event: WebhookEvent, db: Any) -> None:
        pass

    def on_subscription_created(self, event: WebhookEvent, db: Any) -> None:
        pass

    def on_subscription_updated(self, event: WebhookEvent, db: Any) -> None:
        pass

    def on_subscription_deleted(self, event: WebhookEvent, db: Any) -> None:
        pass

    def on_invoice_paid(self, event: WebhookEvent, db: Any) -> None:
        pass

    def on_invoice_payment_failed(self, event: WebhookEvent, db: Any) -> None:
        pass


def _extract_event(event: dict) -> WebhookEvent:
    """Extrae un WebhookEvent tipado desde el objeto crudo de Stripe."""
    data = event.get("data", {}).get("object", {})
    event_type = event.get("type", "")

    metadata = data.get("metadata", {})

    # Intentar obtener userId de metadata, o del client_reference_id
    user_id = metadata.get("userId", "")
    if not user_id:
        user_id = data.get("client_reference_id", "")

    app_name = metadata.get("appName", "")

    customer_id = data.get("customer", "")
    subscription_id = data.get("subscription") or data.get("id", "")

    subscription_status = data.get("status")
    current_period_end_ts = data.get("current_period_end")

    current_period_end = None
    if current_period_end_ts:
        current_period_end = datetime.fromtimestamp(
            current_period_end_ts, tz=timezone.utc
        )

    # Resolver price_id y lookup_key desde los items de la suscripción
    price_id: Optional[str] = None
    lookup_key: Optional[str] = None

    items = data.get("items", {})
    items_data = items.get("data", [])
    if not items_data:
        # Para checkout.session.completed, los items están en line_items
        line_items_data = data.get("line_items", {}).get("data", [])
        if line_items_data:
            price_data = line_items_data[0].get("price", {})
            price_id = price_data.get("id")
            lookup_key = price_data.get("lookup_key", price_data.get("lookup_key"))
    else:
        price_data = items_data[0].get("price", {})
        price_id = price_data.get("id")
        lookup_key = price_data.get("lookup_key")

    return WebhookEvent(
        type=event_type,
        user_id=user_id,
        app_name=app_name,
        customer_id=customer_id,
        subscription_id=subscription_id,
        subscription_status=subscription_status,
        price_id=price_id,
        lookup_key=lookup_key,
        current_period_end=current_period_end,
        raw=data,
    )


def process_webhook(
    body: bytes,
    sig_header: str,
    webhook_secret: str,
    callbacks: Optional[StripeCallbacks] = None,
    db: Any = None,
) -> WebhookEvent:
    """Procesa un webhook entrante de Stripe.

    1. Verifica la firma criptográfica.
    2. Construye el evento tipado.
    3. Dispara el callback correspondiente según el tipo de evento.

    Args:
        body: Body crudo (bytes) del request.
        sig_header: Header ``stripe-signature`` del request.
        webhook_secret: Secreto del webhook (whsec_xxx).
        callbacks: Instancia con los callbacks de la app hija.
        db: Contexto de base de datos para pasar a los callbacks.

    Returns:
        El evento procesado (ya tipado como WebhookEvent).

    Raises:
        ValueError: Si el body no es válido.
        stripe.error.SignatureVerificationError: Si la firma no es válida.
    """
    if callbacks is None:
        callbacks = _DefaultCallbacks()

    # Verificar firma
    try:
        event = stripe.Webhook.construct_event(
            payload=body,
            sig_header=sig_header,
            secret=webhook_secret,
        )
    except ValueError as e:
        raise ValueError(f"Body inválido: {e}") from e
    except stripe.error.SignatureVerificationError as e:
        raise stripe.error.SignatureVerificationError(
            f"Firma inválida: {e}"
        ) from e

    webhook_event = _extract_event(event)

    # Disparar el callback correspondiente
    event_type = webhook_event.type
    handlers = {
        "checkout.session.completed": "on_checkout_completed",
        "customer.subscription.created": "on_subscription_created",
        "customer.subscription.updated": "on_subscription_updated",
        "customer.subscription.deleted": "on_subscription_deleted",
        "invoice.paid": "on_invoice_paid",
        "invoice.payment_failed": "on_invoice_payment_failed",
    }

    handler_name = handlers.get(event_type)
    if handler_name:
        handler = getattr(callbacks, handler_name, None)
        if handler:
            handler(webhook_event, db)

    return webhook_event
