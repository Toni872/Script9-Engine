"""GET /plans — devuelve el catálogo de planes desde Stripe."""

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/plans", tags=["plans"])

# Lookup keys de los planes en Stripe
PLAN_LOOKUP_KEYS = ["starter_monthly", "pro_monthly", "enterprise_monthly"]


class PlanFeature(BaseModel):
    text: str


class PlanResponse(BaseModel):
    id: str  # plan_name interno (ej: "starter")
    lookup_key: str  # lookup key en Stripe (ej: "starter_monthly")
    name: str  # nombre para mostrar (ej: "Starter")
    price: Optional[int] = None  # precio en USD, null = custom
    currency: str = "usd"
    features: list[str]
    popular: bool = False
    contact_sales: bool = False


def _fetch_stripe_plans() -> list[PlanResponse]:
    """Llama a Stripe y arma la lista de planes desde Products + Prices.

    Cada Price en Stripe tiene metadata con:
      - plan_name: nombre interno (starter, professional, enterprise)
      - display_name: nombre para mostrar
      - automations_limit: límite de automatizaciones
      - executions_limit: límite de ejecuciones
      - is_popular: "true" para marcar como popular
    """
    from script9_billing.core import configure

    from app.config import settings

    configure(settings.stripe_secret_key)

    import stripe

    plans: list[PlanResponse] = []

    for lookup_key in PLAN_LOOKUP_KEYS:
        try:
            prices = stripe.Price.list(
                lookup_keys=[lookup_key],
                expand=["data.product"],
                active=True,
                limit=1,
            )
        except Exception:
            continue

        if not prices.data:
            continue

        price = prices.data[0]
        metadata = price.metadata or {}
        product = price.product
        product_metadata = getattr(product, "metadata", {}) if product else {}

        plan_name = metadata.get("plan_name") or product_metadata.get("plan_name")
        if not plan_name:
            # Fallback: inferir del lookup_key si no está en metadata
            plan_name = lookup_key.replace("_monthly", "").replace("_", "-")

        display_name = metadata.get(
            "display_name"
        ) or product_metadata.get("display_name") or plan_name.title()
        automations = metadata.get("automations_limit", "")
        executions = metadata.get("executions_limit", "")
        is_popular = metadata.get("is_popular", "").lower() == "true"

        features: list[str] = []
        if automations:
            features.append(f"{automations} automatizaciones activas")
        if executions:
            features.append(f"{executions} ejecuciones/mes")
        if metadata.get("support_email"):
            features.append("Soporte por email")
        if metadata.get("support_priority"):
            features.append("Soporte prioritario")
        if metadata.get("basic_dashboard"):
            features.append("Panel de control básico")
        if metadata.get("advanced_dashboard"):
            features.append("Panel de control avanzado")
        if metadata.get("premium_integrations"):
            features.append("Integraciones premium")
        if metadata.get("history_90_days"):
            features.append("Historial 90 días")
        if metadata.get("unlimited_automations"):
            features.append("Automatizaciones ilimitadas")
        if metadata.get("unlimited_executions"):
            features.append("Ejecuciones ilimitadas")
        if metadata.get("dedicated_support"):
            features.append("Soporte dedicado 24/7")
        if metadata.get("on_premise"):
            features.append("On-premise disponible")
        if metadata.get("sla_guaranteed"):
            features.append("SLA garantizado")
        if metadata.get("audit_compliance"):
            features.append("Auditoría y compliance")

        plan_price: Optional[int] = None
        if price.unit_amount is not None:
            plan_price = round(price.unit_amount / 100)  # Stripe usa centavos

        plans.append(
            PlanResponse(
                id=plan_name,
                lookup_key=lookup_key,
                name=display_name,
                price=plan_price,
                currency=price.currency,
                features=features,
                popular=is_popular,
                contact_sales=(plan_name == "enterprise"),
            )
        )

    return plans


@router.get("", response_model=list[PlanResponse])
async def get_plans() -> list[PlanResponse]:
    """Devuelve todos los planes disponibles.

    Lee de Stripe Products + Prices. Si Stripe no está configurado
    (sin API key), devuelve un catálogo por defecto con los 3 planes.
    """
    from app.config import settings

    if not settings.stripe_secret_key:
        # Stripe no configurado — devolver catálogo por defecto
        return _default_plans()

    try:
        return _fetch_stripe_plans()
    except Exception as e:
        # Si Stripe falla, devolver fallback para no romper la UI
        import logging

        logging.warning(f"Failed to fetch plans from Stripe: {e}")
        return _default_plans()


def _default_plans() -> list[PlanResponse]:
    """Catálogo por defecto cuando Stripe no está disponible."""
    return [
        PlanResponse(
            id="starter",
            lookup_key="starter_monthly",
            name="Starter",
            price=29,
            currency="usd",
            features=[
                "5 automatizaciones activas",
                "100 ejecuciones/mes",
                "Soporte por email",
                "Panel de control básico",
            ],
            popular=False,
            contact_sales=False,
        ),
        PlanResponse(
            id="professional",
            lookup_key="pro_monthly",
            name="Professional",
            price=99,
            currency="usd",
            features=[
                "25 automatizaciones activas",
                "1,000 ejecuciones/mes",
                "Soporte prioritario",
                "Panel de control avanzado",
                "Integraciones premium",
                "Historial 90 días",
            ],
            popular=True,
            contact_sales=False,
        ),
        PlanResponse(
            id="enterprise",
            lookup_key="enterprise_monthly",
            name="Enterprise",
            price=None,
            currency="usd",
            features=[
                "Automatizaciones ilimitadas",
                "Ejecuciones ilimitadas",
                "Soporte dedicado 24/7",
                "On-premise disponible",
                "SLA garantizado",
                "Auditoría y compliance",
            ],
            popular=False,
            contact_sales=True,
        ),
    ]
