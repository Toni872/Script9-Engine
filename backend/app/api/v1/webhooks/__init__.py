"""
Webhook router — agrupa todos los webhooks bajo /api/v1/webhooks.
"""
from fastapi import APIRouter

from app.api.v1.webhooks.calendar import router as calendar_router
from app.api.v1.webhooks.crm import router as crm_router

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

router.include_router(calendar_router)
router.include_router(crm_router)
