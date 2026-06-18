"""GET /plans — devuelve el catálogo de planes desde Stripe."""

import json
import time
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/plans", tags=["plans"])

# ── Cache ───────────────────────────────────────────────────────────────────────

_CACHE_TTL_SECONDS = 300  # 5 minutos
_cache_key = "script9:plans"
_redis_client = None


def _get_redis():
    """Lazy Redis client — conecta solo cuando se necesita."""
    global _redis_client
    if _redis_client is None:
        try:
            import redis
            from app.config import settings

            _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
            _redis_client.ping()  # verificar conexión
        except Exception:
            _redis_client = None
    return _redis_client

# Lookup keys de los planes en Stripe
PLAN_LOOKUP_KEYS = ["starter_monthly", "pro_monthly", "enterprise_monthly"]

# Fallback: infiere el plan_name desde el lookup_key cuando Stripe no tiene metadata.
# IMPORTANTE: mantener sincronizado con Script9Callbacks._LOOKUP_KEY_TO_PLAN en webhooks.py
_LOOKUP_KEY_TO_PLAN_NAME = {
    "starter_monthly": "starter",
    "pro_monthly": "professional",
    "enterprise_monthly": "enterprise",
}


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
        import logging

        try:
            prices = stripe.Price.list(
                lookup_keys=[lookup_key],
                expand=["data.product"],
                active=True,
                limit=1,
            )
        except Exception as e:
            logging.warning(f"Stripe Price.list failed for '{lookup_key}': {e}")
            continue

        if not prices.data:
            continue

        price = prices.data[0]
        metadata = price.metadata or {}
        product = price.product
        product_metadata = getattr(product, "metadata", {}) if product else {}

        plan_name = metadata.get("plan_name") or product_metadata.get("plan_name")
        if not plan_name:
            # Fallback: usar el mapping known de lookup_key → plan_name
            plan_name = _LOOKUP_KEY_TO_PLAN_NAME.get(lookup_key, "trial")

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


def _get_cached_plans() -> Optional[list[PlanResponse]]:
    """Intenta leer planes desde Redis cache. Devuelve None si no hay cache."""
    redis = _get_redis()
    if redis is None:
        return None
    try:
        cached = redis.get(_cache_key)
        if cached:
            data = json.loads(cached)
            return [PlanResponse(**p) for p in data]
    except Exception:
        return None


def _set_cached_plans(plans: list[PlanResponse]) -> None:
    """Guarda planes en Redis cache por _CACHE_TTL_SECONDS."""
    redis = _get_redis()
    if redis is None:
        return
    try:
        redis.setex(_cache_key, _CACHE_TTL_SECONDS, json.dumps([p.model_dump() for p in plans]))
    except Exception:
        pass


@router.get("", response_model=list[PlanResponse])
async def get_plans() -> list[PlanResponse]:
    """Devuelve todos los planes disponibles.

    Lee de Stripe Products + Prices con cache Redis (5 min).
    Si Stripe no está configurado o falla, devuelve el catálogo por defecto.
    """
    from app.config import settings

    if not settings.stripe_secret_key:
        return _default_plans()

    # Intentar cache primero
    cached = _get_cached_plans()
    if cached is not None:
        return cached

    try:
        plans = _fetch_stripe_plans()
        _set_cached_plans(plans)
        return plans
    except Exception as e:
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
