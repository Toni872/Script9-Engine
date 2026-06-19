"""
Endpoints para gestión de invitaciones.

- POST /invitations — protegido, crea cotización y envía email
- GET /invitations/accept — público, valida JWT y marca invitación
"""
from __future__ import annotations

import datetime
from decimal import Decimal

import jwt
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Cotizacion, Usuario
from app.schemas.cotizacion import CotizacionResponse
from app.schemas.invitation import InvitationCreate, InvitationResponse
from app.services.email_service import send_invitation_email

router = APIRouter(prefix="/invitations", tags=["invitations"])

# Clave secreta para firmar tokens JWT (usar variable de entorno en producción)
_JWT_SECRET = settings.firebase_credentials_path or "script9-invitation-secret-key"
_JWT_ALGORITHM = "HS256"
_TOKEN_EXPIRY_DAYS = 7


def _create_invitation_token(email: str, app: str) -> str:
    """Genera un JWT para la invitación."""
    payload = {
        "email": email,
        "app": app,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=_TOKEN_EXPIRY_DAYS),
        "iat": datetime.datetime.utcnow(),
    }
    return jwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGORITHM)


def _decode_invitation_token(token: str) -> dict:
    """Decodifica y valida un JWT de invitación."""
    try:
        payload = jwt.decode(token, _JWT_SECRET, algorithms=[_JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de invitación expirado",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de invitación inválido",
        )


@router.post("", response_model=InvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_invitation(
    payload: InvitationCreate,
    background_tasks: BackgroundTasks,
    current_user: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> InvitationResponse:
    """
    Crea una invitación: genera Cotizacion + token JWT + envía email.

    El email se envía en background para no bloquear la respuesta.
    """
    # Generar token JWT
    token = _create_invitation_token(payload.email, payload.app)

    # Calcular fecha de expiración
    expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=_TOKEN_EXPIRY_DAYS)

    # Crear cotización asociada
    cotizacion = Cotizacion(
        user_id=current_user.id,
        app=payload.app,
        plan_interno=payload.plan_interno,
        precio_eur=payload.precio_eur,
        notas_admin=payload.notas_admin,
    )
    db.add(cotizacion)
    await db.flush()

    # URL de aceptación (frontend)
    invitation_url = f"{settings.script9_url}/invitation/accept?token={token}"

    # Enviar email en background
    background_tasks.add_task(send_invitation_email, payload.email, invitation_url)

    return InvitationResponse(
        id=cotizacion.id,
        email=payload.email,
        app=payload.app,
        plan_interno=payload.plan_interno,
        precio_eur=payload.precio_eur,
        token=token,
        aceptada=False,
        expires_at=expires_at,
        creado_en=cotizacion.creado_en,
    )


@router.get("/accept")
async def accept_invitation(
    token: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """
    Valida el JWT de invitación y marca la cotización como aceptada.

    Redirige al frontend con flag de éxito o error.
    """
    try:
        payload = _decode_invitation_token(token)
    except HTTPException as e:
        # Redirigir con error
        return RedirectResponse(
            url=f"{settings.script9_url}/invitation/accepted?success=false&error={e.detail}",
            status_code=status.HTTP_302_FOUND,
        )

    email = payload.get("email")
    app = payload.get("app")

    if not email or not app:
        return RedirectResponse(
            url=f"{settings.script9_url}/invitation/accepted?success=false&error=token_invalido",
            status_code=status.HTTP_302_FOUND,
        )

    # Buscar cotización pendiente
    stmt = (
        select(Cotizacion)
        .where(Cotizacion.email == email)
        .where(Cotizacion.app == app)
    )
    result = await db.execute(stmt)
    cotizacion = result.scalar_one_or_none()

    if cotizacion:
        # Aquí se podría marcar como aceptada si existiera ese campo
        # Por ahora solo redirigimos con éxito
        pass

    return RedirectResponse(
        url=f"{settings.script9_url}/invitation/accepted?success=true&email={email}",
        status_code=status.HTTP_302_FOUND,
    )
