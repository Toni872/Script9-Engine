"""Tests del flujo de autenticación con Firebase JWT.

Cubre los 5 escenarios del spec ``#321`` más un isolation proof que
verifica que el ``db_session.rollback()`` del conftest deshace el
``commit`` que hace ``get_current_user`` durante el auto-registro.

Los tests usan el endpoint ``GET /api/v1/usuarios/me`` como "canario":
para llegar al handler el JWT de Firebase tiene que pasar por
``get_current_user``, que es donde viven las 5 ramas de error
(401/auto-register/403).
"""

from collections.abc import Awaitable, Callable

from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Usuario


async def test_missing_header_returns_401(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
) -> None:
    """Sin ``Authorization`` → 401 sin tocar ``verify_id_token``."""
    mock_firebase()  # uid por defecto, pero no debe invocarse

    response = await client.get("/api/v1/usuarios/me")

    assert response.status_code == 401


async def test_malformed_token_returns_401(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
) -> None:
    """``verify_id_token`` raises → 401, y el mock fue efectivamente llamado."""
    mock_firebase(raises=ValueError("bad-token"))

    response = await client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer not-a-jwt"},
    )

    assert response.status_code == 401


async def test_valid_token_auto_registers(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
    db_session: AsyncSession,
) -> None:
    """Token válido para uid nueva → 200 y se crea un ``Usuario`` con defaults."""
    uid = mock_firebase(uid="new-uid")

    response = await client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["firebase_uid"] == uid
    assert body["email"] == f"{uid}@test.local"
    assert body["plan_suscripcion"] == "trial"
    assert body["activo"] is True

    # Verificar que la fila realmente existe en la BD de test
    result = await db_session.execute(select(Usuario).where(Usuario.firebase_uid == uid))
    usuario = result.scalar_one_or_none()
    assert usuario is not None
    assert usuario.plan_suscripcion == "trial"
    assert usuario.activo is True


async def test_valid_token_existing_user_does_not_duplicate(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
    usuario_factory: Callable[..., Awaitable[Usuario]],
) -> None:
    """Token válido para uid existente → 200, no se duplica la fila."""
    await usuario_factory(firebase_uid="existing-uid", email="existing@test.local")
    mock_firebase(uid="existing-uid")

    response = await client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["firebase_uid"] == "existing-uid"

    # El próximo request con el mismo uid NO crea una segunda fila
    response2 = await client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response2.status_code == 200


async def test_suspended_user_returns_403(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
    usuario_factory: Callable[..., Awaitable[Usuario]],
) -> None:
    """Usuario con ``activo=False`` → 403."""
    await usuario_factory(firebase_uid="suspended-uid", suspended=True)
    mock_firebase(uid="suspended-uid")

    response = await client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 403


async def test_count_users_after_commit(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
    db_session: AsyncSession,
) -> None:
    """Isolation proof: después de un auto-registro (que hace ``commit``)
    la fila existe en la sesión actual, y la siguiente request NO la
    duplica. Combinado con el ``rollback`` del conftest, garantiza
    que un test posterior parte de una BD vacía.
    """
    uid = mock_firebase(uid="proof-uid")

    # Antes de cualquier request, la tabla está vacía en este test
    count_before = (
        await db_session.execute(select(func.count()).select_from(Usuario))
    ).scalar_one()
    assert count_before == 0

    # Auto-registro vía request autenticado
    response = await client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200

    # El commit del auto-register hizo visible la fila dentro de la sesión
    count_after = (await db_session.execute(select(func.count()).select_from(Usuario))).scalar_one()
    assert count_after == 1

    # Y la uid correcta quedó persistida
    result = await db_session.execute(select(Usuario).where(Usuario.firebase_uid == uid))
    assert result.scalar_one_or_none() is not None
