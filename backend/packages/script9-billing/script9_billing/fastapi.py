"""Router FastAPI opcional para plug-and-play en apps hijas.

Montá esto en tu app FastAPI y tenés los 3 endpoints listos.
Cada app hija inyecta sus dependencias (get_current_user, get_db, callbacks).

Uso:
    from fastapi import FastAPI, Depends
    from script9_billing.fastapi import create_billing_router

    app = FastAPI()

    router = create_billing_router(
        app_name="tempos",
        get_current_user=get_current_user,
        get_db=get_db,
        callbacks=MisCallbacks(),
    )
    app.include_router(router)
"""

from collections.abc import Callable
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from script9_billing.core import create_checkout_session, create_portal_session
from script9_billing.models import CheckoutRequest, CheckoutResult, PortalResult
from script9_billing.webhook import StripeCallbacks, process_webhook


class _CheckoutBody(BaseModel):
    lookup_key: str = Field(
        ...,
        description="Identificador del plan en Stripe (ej: starter_monthly)",
    )


class _PortalBody(BaseModel):
    pass


class _CallbacksWrapper:
    """Wrapper mutable que permite cambiar los callbacks después de crear el router.

    Necesario porque las dependencias de FastAPI se resuelven en cada request,
    pero las clases se instancian al crear el router.
    """

    def __init__(self) -> None:
        self.callbacks: Optional[StripeCallbacks] = None


def create_billing_router(
    app_name: str = "script9",
    get_current_user: Optional[Callable] = None,
    get_db: Optional[Callable] = None,
    callbacks: Optional[StripeCallbacks] = None,
    success_url_template: str = "https://www.script-9.com/pago-exitoso",
    cancel_url_template: str = "https://www.script-9.com/dashboard",
    return_url_template: str = "https://www.script-9.com/dashboard",
    prefix: str = "/api/v1/billing",
    tags: Optional[list[str]] = None,
    stripe_webhook_secret_getter: Optional[Callable[[], str]] = None,
) -> APIRouter:
    """Crea un router FastAPI con los endpoints de facturación.

    Args:
        app_name: Nombre de la app (se inyecta en metadata de Stripe).
        get_current_user: Dependencia FastAPI que resuelve el usuario autenticado.
                          Debe retornar un objeto con: uid, email, stripe_customer_id.
        get_db: Dependencia FastAPI que resuelve la sesión de base de datos.
        callbacks: Instancia de StripeCallbacks para procesar webhooks.
                   Si no se provee, el webhook procesa el evento pero no llama a nada.
        success_url_template: Template URL de éxito (se le concatena ?app={app_name}).
        cancel_url_template: URL de cancelación.
        return_url_template: URL de retorno del Customer Portal.
        prefix: Prefijo del router (default: /api/v1/billing).
        tags: Tags de OpenAPI.
        stripe_webhook_secret_getter: Callable que retorna el webhook secret.
            Necesario para el endpoint de webhook. Si no se provee,
            el endpoint de webhook no se incluye.

    Returns:
        APIRouter de FastAPI listo para montar.
    """
    if tags is None:
        tags = ["billing"]

    router = APIRouter(prefix=prefix, tags=tags)

    # Necesitamos un wrapper mutable porque el callbacks puede ser None
    # y setearse después. El router guarda la referencia al wrapper.
    callbacks_wrapper = _CallbacksWrapper()
    callbacks_wrapper.callbacks = callbacks

    # ── Helpers para resolver dependencias ──────────────────────────────

    def _resolve_user():
        if get_current_user is None:
            raise HTTPException(
                status_code=501,
                detail="get_current_user no configurado en el router de billing",
            )
        return get_current_user()

    def _resolve_db():
        if get_db is None:
            return None
        return get_db()

    # ── Checkout Session ────────────────────────────────────────────────

    @router.post("/create-checkout-session", response_model=CheckoutResult)
    async def _checkout(
        body: _CheckoutBody,
        usuario: Any = Depends(_resolve_user),
    ):
        if not stripe_webhook_secret_getter:
            # Es solo una comprobación de que stripe está configurado
            pass

        try:
            stripe_customer_id = getattr(usuario, "stripe_customer_id", None)
            user_email = getattr(usuario, "email", "")
            user_uid = getattr(usuario, "uid", None) or getattr(
                usuario, "firebase_uid", ""
            )

            success_url = f"{success_url_template}?app={app_name}"
            cancel_url = cancel_url_template

            url = create_checkout_session(
                lookup_key=body.lookup_key,
                user_uid=user_uid,
                user_email=user_email,
                app_name=app_name,
                stripe_customer_id=stripe_customer_id,
                success_url=success_url,
                cancel_url=cancel_url,
            )
            return CheckoutResult(url=url)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error de Stripe: {e}")

    # ── Customer Portal ─────────────────────────────────────────────────

    @router.post("/create-portal-session", response_model=PortalResult)
    async def _portal(
        usuario: Any = Depends(_resolve_user),
    ):
        customer_id = getattr(usuario, "stripe_customer_id", None)
        if not customer_id:
            raise HTTPException(
                status_code=400,
                detail="No tenés un ID de cliente de Stripe. Suscribite a un plan primero.",
            )

        try:
            return_url = return_url_template
            url = create_portal_session(
                customer_id=customer_id,
                return_url=return_url,
            )
            return PortalResult(url=url)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Error de Stripe: {e}")

    # ── Webhook ─────────────────────────────────────────────────────────

    if stripe_webhook_secret_getter:

        @router.post("/webhook")
        async def _webhook(
            request: Request,
            db: Any = Depends(_resolve_db),
        ):
            body = await request.body()
            sig_header = request.headers.get("stripe-signature")

            if not sig_header:
                raise HTTPException(
                    status_code=400,
                    detail="Firma Stripe requerida (stripe-signature header)",
                )

            webhook_secret = stripe_webhook_secret_getter()
            if not webhook_secret:
                raise HTTPException(
                    status_code=503,
                    detail="Stripe webhook no configurado",
                )

            try:
                event = process_webhook(
                    body=body,
                    sig_header=sig_header,
                    webhook_secret=webhook_secret,
                    callbacks=callbacks_wrapper.callbacks,
                    db=db,
                )
                return {"received": True, "type": event.type}
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error de firma: {e}")

    return router
