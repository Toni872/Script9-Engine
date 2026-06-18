"""Firebase JWT verification y dependencia get_current_user."""

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials, initialize_app
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Usuario
from app.services.rate_limit import limiter

security = HTTPBearer(auto_error=False)

_firebase_initialized = False


def _ensure_firebase() -> None:
    """Inicializa Firebase Admin SDK una sola vez."""
    global _firebase_initialized
    if not _firebase_initialized and settings.firebase_credentials_path:
        cred = credentials.Certificate(settings.firebase_credentials_path)
        initialize_app(cred)
        _firebase_initialized = True


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Verifica el JWT de Firebase y auto-registra al usuario si no existe."""
    _ensure_firebase()

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado",
        )

    try:
        decoded = firebase_auth.verify_id_token(credentials.credentials, check_revoked=True)
    except firebase_auth.InvalidIDTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        ) from None
    except firebase_auth.ExpiredIDTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
        ) from None
    except firebase_auth.RevokedIDTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token revocado",
        ) from None
    except Exception as e:
        # Error inesperado de Firebase o de red — loguear internamente
        import structlog
        logger = structlog.get_logger()
        logger.error("firebase_verify_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from None

    firebase_uid: str | None = decoded.get("uid")
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
        )

    email: str = decoded.get("email", "")
    nombre: str = decoded.get("name", "")

    result = await db.execute(select(Usuario).where(Usuario.firebase_uid == firebase_uid))
    usuario = result.scalar_one_or_none()

    if not usuario:
        usuario = Usuario(firebase_uid=firebase_uid, email=email, nombre=nombre)
        db.add(usuario)
        try:
            await db.commit()
            await db.refresh(usuario)
        except Exception:
            # Race condition: otro request creó el usuario entre el select y el insert.
            # Re-consultar en vez de fallar.
            await db.rollback()
            result = await db.execute(
                select(Usuario).where(Usuario.firebase_uid == firebase_uid)
            )
            usuario = result.scalar_one()
    elif not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta suspendida",
        )

    return usuario
