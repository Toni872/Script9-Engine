"""Endpoints de gestión de perfil para el usuario autenticado."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import get_current_user
from app.database import get_db
from app.models import Usuario
from app.schemas.usuario import UsuarioRead, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


@router.get("/me", response_model=UsuarioRead)
async def get_me(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    """Devuelve el perfil del usuario autenticado."""
    return usuario


@router.patch("/me", response_model=UsuarioRead)
async def update_me(
    data: UsuarioUpdate,
    usuario: Usuario = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Actualiza el perfil del usuario autenticado.

    Actualmente solo permite cambiar nombre. El email no se puede cambiar
    por aquí porque requiere re-verificación con Firebase (el usuario debe
    confirmar el nuevo email desde su cuenta de Google.
    """
    if data.nombre is not None:
        usuario.nombre = data.nombre
    # NOTA: email change requires Firebase re-authentication flow.
    # No permitir cambio de email sin verificar con Firebase.
    # future: implementar con get_id_token(force_refresh=True) y verificación.
    await db.commit()
    await db.refresh(usuario)
    return usuario
