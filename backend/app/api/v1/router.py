"""Agrupación de todos los routers de la API v1."""

from fastapi import APIRouter

from app.api.v1 import (
    activity,
    cotizaciones,
    health,
    invitations,
    leads,
    meetings,
    plans,
    public,
    stripe,
    usuarios,
    webhooks,
)

router = APIRouter(prefix="/api/v1")
router.include_router(health.router)
router.include_router(usuarios.router)
router.include_router(stripe.router)
router.include_router(plans.router)
router.include_router(leads.router)
router.include_router(meetings.router)
router.include_router(activity.router)
router.include_router(invitations.router)
router.include_router(cotizaciones.router)
router.include_router(public.router)

# Webhooks sin prefijo /api/v1 para compatibilidad con Stripe
webhook_router = APIRouter()
webhook_router.include_router(webhooks.router)
