"""Modelos Pydantic compartidos para facturación Stripe."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class PlanTier(str, Enum):
    starter = "starter"
    professional = "professional"
    enterprise = "enterprise"
    trial = "trial"


class CheckoutRequest(BaseModel):
    """Payload para crear una Checkout Session.

    En vez de price_id (frágil), usamos lookup_key
    que Stripe resuelve dinámicamente.
    """

    lookup_key: str = Field(
        ...,
        description="Identificador del plan en Stripe (ej: starter_monthly)",
        examples=["starter_monthly", "pro_monthly", "enterprise_monthly"],
    )


class CheckoutResult(BaseModel):
    """Resultado de crear una Checkout Session."""

    url: str = Field(
        ...,
        description="URL de Stripe Checkout para redirigir al usuario",
    )


class PortalResult(BaseModel):
    """Resultado de crear una sesión del Customer Portal."""

    url: str = Field(
        ...,
        description="URL del Customer Portal de Stripe",
    )


class WebhookEvent(BaseModel):
    """Evento procesado del webhook de Stripe.

    Este es el objeto que recibe cada app hija en sus callbacks.
    """

    type: str = Field(
        ...,
        description="Tipo de evento Stripe (checkout.session.completed, etc.)",
    )
    user_id: str = Field(
        "",
        description="Firebase UID del usuario (extraído de metadata)",
    )
    app_name: str = Field(
        "",
        description="Nombre de la app origen (extraído de metadata)",
    )
    customer_id: str = Field(
        "",
        description="ID del cliente en Stripe (cus_xxx)",
    )
    subscription_id: Optional[str] = Field(
        None,
        description="ID de la suscripción en Stripe (sub_xxx)",
    )
    subscription_status: Optional[str] = Field(
        None,
        description="Estado de la suscripción (active, past_due, canceled, etc.)",
    )
    price_id: Optional[str] = Field(
        None,
        description="ID del precio en Stripe asociado a la suscripción",
    )
    lookup_key: Optional[str] = Field(
        None,
        description="Lookup key del plan (resuelto desde price_id)",
    )
    plan_name: Optional[str] = Field(
        None,
        description="Nombre interno del plan (ej: starter, professional) leído de Stripe price metadata",
    )
    current_period_end: Optional[datetime] = Field(
        None,
        description="Fin del período actual de facturación",
    )
    raw: dict = Field(
        default_factory=dict,
        description="Objeto crudo del evento Stripe (para acceso a campos no mapeados)",
    )
