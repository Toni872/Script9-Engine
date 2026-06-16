"""Tests del endpoint de health check.

Verifica que ``GET /api/v1/health`` responde 200 con ``status="ok"`` y
que echa el ``environment`` desde ``settings``. No requiere autenticación.

Desviación del spec: la spec ``#321`` asume ``GET /health`` en la raíz,
pero el production code (``app/api/v1/router.py``) monta el router de
health bajo el prefijo ``/api/v1``, por lo que la ruta real es
``/api/v1/health``. El test ejercita la ruta real; flag en
apply-progress para que ``sdd-verify`` lo registre.
"""

from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient) -> None:
    """GET /api/v1/health → 200 con status="ok" y environment del settings."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body == {"status": "ok", "environment": "local"}


async def test_health_requires_no_auth(client: AsyncClient) -> None:
    """GET /api/v1/health sin Authorization → 200 (no 401)."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.status_code != 401
