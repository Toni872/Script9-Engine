"""Fixtures compartidas para los tests de Script9 Engine.

Este módulo define los fixtures base que usan todos los tests. Cualquier
cambio aquí afecta el contrato del harness completo (ver spec #321).

Importante: el módulo ``app.api.v1.auth`` DEBE mantener el import
``from firebase_admin import auth as firebase_auth`` y referenciar
``firebase_auth.verify_id_token`` en el módulo (no como dependencia
FastAPI). Si eso cambia, el fixture ``mock_firebase`` deja de funcionar
silenciosamente.
"""

from collections.abc import AsyncGenerator, Awaitable, Callable
from typing import TYPE_CHECKING
from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.database import get_db
from app.models import Base

if TYPE_CHECKING:
    from app.models import Usuario

# Base de datos en memoria para tests
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def engine_test() -> AsyncGenerator[AsyncEngine, None]:
    """Motor SQLite async para la sesión de tests.

    Usa ``StaticPool`` para que la conexión sea única durante toda la
    sesión de pytest: con ``sqlite:///:memory:`` cada conexión abre su
    propia BD en memoria, y sin un pool compartido la data se pierde
    entre tests. ``check_same_thread=False`` es necesario porque
    aiosqlite corre el adapter en el event loop principal.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine_test: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    """Sesión de BD aislada por test con nested-savepoint isolation.

    Patrón: la sesión se ata a una conexión explícita cuya transacción
    externa se inicia antes y se hace ``rollback`` después. Los
    ``commit()`` que haga el código bajo test (e.g. ``get_current_user``
    en el auto-registro) terminan el estado interno de la sesión pero
    **no** la transacción de la conexión, así que el rollback al
    teardown deshace todo. Esto resuelve el pollution-flagged risk
    en la proposal (#308).
    """
    async with engine_test.connect() as connection:
        await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        async with session_factory() as session:
            yield session
        await connection.rollback()


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP con BD de test inyectada."""
    from app.main import app

    app.dependency_overrides[get_db] = lambda: db_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _disable_firebase_init(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita que ``_ensure_firebase()`` intente cargar credenciales en tests.

    El ``.env`` apunta ``FIREBASE_CREDENTIALS_PATH`` a un archivo que no
    existe en CI/dev. Este fixture autouse vacía el setting para que
    ``_ensure_firebase()`` sea un no-op. No toca código de producción.
    """
    monkeypatch.setattr(settings, "firebase_credentials_path", "")


@pytest.fixture
def mock_firebase(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[..., str]:
    """Mock parametrizable de ``firebase_admin.auth.verify_id_token``.

    Uso::

        mock_firebase()                          # uid por defecto
        mock_firebase(uid="alice")               # uid específico
        mock_firebase(raises=ValueError("bad"))  # simula token inválido

    Retorna la ``uid`` configurada para encadenar aserciones.
    """

    def _patch(uid: str = "test-firebase-uid-123", *, raises: Exception | None = None) -> str:
        if raises is not None:
            mock_verify = MagicMock(side_effect=raises)
        else:
            mock_verify = MagicMock(
                return_value={
                    "uid": uid,
                    "email": f"{uid}@test.local",
                    "name": "Test User",
                }
            )
        monkeypatch.setattr("app.api.v1.auth.firebase_auth.verify_id_token", mock_verify)
        return uid

    return _patch


@pytest.fixture
def sample_firebase_token() -> str:
    """Bearer string listo para el header ``Authorization``."""
    return "Bearer test-token"


@pytest.fixture
def mock_redis(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """No-op patch forward-compat para ``app.services.cache_service.redis``.

    El módulo ``app.services.cache_service`` aún no existe; cuando se
    introduzca, este fixture parchará ``redis`` por un ``MagicMock``.
    Mientras tanto, devuelve un ``MagicMock`` para que los tests que
    lo pidan no fallen. No hay código de producción que lo use todavía.
    """
    try:
        monkeypatch.setattr("app.services.cache_service.redis", MagicMock())
    except (AttributeError, ModuleNotFoundError):
        pass
    return MagicMock()


@pytest.fixture
def usuario_factory(
    db_session: AsyncSession,
) -> Callable[..., Awaitable["Usuario"]]:
    """Factory para crear y persistir un ``Usuario`` en la BD de test.

    Acepta los mismos kwargs que ``UsuarioFactory.build()`` más cualquier
    override (``suspended=True`` para ``activo=False``, etc.). Persiste
    usando la ``db_session`` activa, de modo que el ``rollback`` al
    final del test deshace los cambios y deja la siguiente prueba limpia.

    factory-boy 3.3.3 NO expone ``AsyncSQLAlchemyModelFactory``; el
    fallback documentado en la proposal (#308) es construir el modelo
    con el factory sync y persistir manualmente con la sesión async.
    """
    from tests.factories import UsuarioFactory

    async def _make(**kwargs: object) -> "Usuario":
        instance: Usuario = UsuarioFactory.build(**kwargs)
        db_session.add(instance)
        await db_session.commit()
        await db_session.refresh(instance)
        return instance

    return _make
