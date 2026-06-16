"""Tests del servicio de lógica de negocio de ``usuario_service``.

Cubre los 3 escenarios del spec ``#321`` sin pasar por HTTP: las
funciones reciben la sesión directamente.

Aislamiento de BD: con el patrón nested-savepoint del conftest, la
``db_session`` comparte la transacción externa de su conexión. El
``commit()`` de la ``usuario_factory`` libera cambios a esa transacción
(que se rollbackea al final del test). Como tanto la factory como
las funciones del servicio reciben la MISMA ``db_session``, las filas
creadas por la factory son visibles para las queries que haga el
servicio. Esto evita tener que "rebindear" sesiones.
"""

from collections.abc import Awaitable, Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Usuario
from app.services.usuario_service import create_usuario, get_usuario_by_firebase_uid


async def test_get_usuario_by_firebase_uid_found(
    db_session: AsyncSession,
    usuario_factory: Callable[..., Awaitable[Usuario]],
) -> None:
    """Devuelve la instancia de ``Usuario`` cuando el uid existe."""
    await usuario_factory(firebase_uid="abc-uid", email="abc@test.local")

    found = await get_usuario_by_firebase_uid(db_session, "abc-uid")

    assert found is not None
    assert found.firebase_uid == "abc-uid"
    assert found.email == "abc@test.local"


async def test_get_usuario_by_firebase_uid_not_found(
    db_session: AsyncSession,
) -> None:
    """Devuelve ``None`` cuando el uid no existe en la BD."""
    found = await get_usuario_by_firebase_uid(db_session, "missing-uid")

    assert found is None


async def test_create_usuario_applies_defaults(
    db_session: AsyncSession,
) -> None:
    """Crea un ``Usuario`` aplicando los defaults de la BD (``trial``, ``activo=True``)."""
    usuario = await create_usuario(
        db_session,
        firebase_uid="created-uid",
        email="created@test.local",
    )

    assert usuario.firebase_uid == "created-uid"
    assert usuario.email == "created@test.local"
    assert usuario.plan_suscripcion == "trial"
    assert usuario.activo is True
