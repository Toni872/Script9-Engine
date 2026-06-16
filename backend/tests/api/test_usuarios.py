"""Tests del endpoint ``/api/v1/usuarios/me``.

Cubre los 3 escenarios del spec ``#321``:

- ``GET /me`` devuelve el perfil del usuario autenticado.
- ``PATCH /me`` con ``{"nombre": "Nuevo"}`` actualiza ``nombre`` en la BD.
- ``PATCH /me`` con email inválido retorna 422 (Pydantic validation).

Spec/code gap
-------------

El tercer test (``test_patch_me_rejects_invalid_email``) está marcado
como ``xfail`` porque la spec exige 422 ante email malformado pero
``app/schemas/usuario.py:UsuarioUpdate`` declara ``email: str | None``
(en vez de ``EmailStr``), por lo que ``"not-an-email"`` pasa validación
y se guarda como 200. La spec y la proposal están alineadas en
esperar 422; agregar la validación al schema es trabajo de producción
fuera de este PR (la proposal #308 dice: "No production code
modified except pyproject.toml script wiring"). El test queda armado
y reportando como ``xfail`` para cuando se arregle el schema.
"""

from collections.abc import Awaitable, Callable

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Usuario


async def test_get_me_returns_profile(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
    usuario_factory: Callable[..., Awaitable[Usuario]],
) -> None:
    """GET /me → 200 con email, nombre, firebase_uid, plan_suscripcion."""
    uid = mock_firebase(uid="profile-uid")
    await usuario_factory(firebase_uid=uid, email="profile@test.local", nombre="Carlos")

    response = await client.get(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["email"] == "profile@test.local"
    assert body["nombre"] == "Carlos"
    assert body["firebase_uid"] == uid
    assert body["plan_suscripcion"] == "trial"


async def test_patch_me_updates_nombre(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
    usuario_factory: Callable[..., Awaitable[Usuario]],
    db_session: AsyncSession,
) -> None:
    """PATCH /me con ``{"nombre": "Nuevo"}`` → 200 y la BD refleja el cambio."""
    uid = mock_firebase(uid="patch-uid")
    await usuario_factory(firebase_uid=uid, email="patch@test.local", nombre="Carlos")

    response = await client.patch(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
        json={"nombre": "Nuevo"},
    )

    assert response.status_code == 200
    assert response.json()["nombre"] == "Nuevo"

    # La fila persistida tiene el nuevo nombre
    result = await db_session.execute(select(Usuario).where(Usuario.firebase_uid == uid))
    usuario = result.scalar_one()
    assert usuario.nombre == "Nuevo"


@pytest.mark.xfail(
    reason=(
        "Spec/code gap: app/schemas/usuario.py:UsuarioUpdate uses `str` (not "
        "EmailStr) so 'not-an-email' passes validation. Fix the schema in a "
        "follow-up PR. See apply-progress for step-6-testing."
    ),
    strict=True,
)
async def test_patch_me_rejects_invalid_email(
    client: AsyncClient,
    mock_firebase: Callable[..., str],
    usuario_factory: Callable[..., Awaitable[Usuario]],
) -> None:
    """PATCH /me con email malformado → 422 (Pydantic EmailStr validation)."""
    uid = mock_firebase(uid="invalid-email-uid")
    await usuario_factory(firebase_uid=uid, email="valid@test.local")

    response = await client.patch(
        "/api/v1/usuarios/me",
        headers={"Authorization": "Bearer test-token"},
        json={"email": "not-an-email"},
    )

    assert response.status_code == 422
