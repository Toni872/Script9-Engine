"""Servicio de lógica de negocio para el módulo de usuarios."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Usuario


async def get_usuario_by_firebase_uid(db: AsyncSession, firebase_uid: str) -> Usuario | None:
    """Busca un usuario por su UID de Firebase."""
    result = await db.execute(select(Usuario).where(Usuario.firebase_uid == firebase_uid))
    return result.scalar_one_or_none()


async def create_usuario(
    db: AsyncSession,
    firebase_uid: str,
    email: str,
    nombre: str = "",
) -> Usuario:
    """Crea un nuevo usuario en la base de datos."""
    usuario = Usuario(firebase_uid=firebase_uid, email=email, nombre=nombre)
    db.add(usuario)
    await db.commit()
    await db.refresh(usuario)
    return usuario
