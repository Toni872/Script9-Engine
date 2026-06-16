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
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
        ) from None

    firebase_uid: str = decoded["uid"]
    email: str = decoded.get("email", "")
    nombre: str = decoded.get("name", "")

    result = await db.execute(select(Usuario).where(Usuario.firebase_uid == firebase_uid))
    usuario = result.scalar_one_or_none()

    if not usuario:
        usuario = Usuario(firebase_uid=firebase_uid, email=email, nombre=nombre)
        db.add(usuario)
        await db.commit()
        await db.refresh(usuario)
    elif not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cuenta suspendida",
        )

    return usuario
