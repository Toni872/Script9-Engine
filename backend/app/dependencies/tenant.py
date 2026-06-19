"""
Filtro multi-tenant automático para FastAPI.

Provee `get_tenant_filter` como dependencia inyectable que extrae
el `tenant_id` del usuario autenticado y lo expone para filtrar queries.

Uso en endpoints:
    @router.get("/leads")
    async def list_leads(
        tenant: TenantFilter = Depends(get_tenant_filter),
        session: AsyncSession = Depends(get_db),
    ):
        stmt = select(Lead).where(*tenant.filters(Lead))
        ...
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from fastapi import Depends
from sqlalchemy import ColumnElement

from app.api.v1.auth import get_current_user
from app.models import Usuario


# ---------------------------------------------------------------------------
# Dataclass de filtro
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class TenantFilter:
    """
    Encapsula el contexto de tenant extraído del usuario autenticado.

    No acepta `app` ni `tenant_id` desde el body del request.
    Siempre se deriva del JWT / sesión del usuario.
    """

    tenant_id: str
    user_id: int

    def filters(self, model: Any) -> list[ColumnElement[bool]]:
        """
        Devuelve cláusulas WHERE listas para aplicar en una query SQLAlchemy.

        Filtra por `app` (tenant_id) y opcionalmente por `user_id`.

        Args:
            model: Clase del modelo SQLAlchemy a filtrar.

        Returns:
            Lista de expresiones booleanas SQLAlchemy.

        Example:
            stmt = select(Lead).where(*tenant.filters(Lead))
        """
        clauses: list[ColumnElement[bool]] = []

        if hasattr(model, "app"):
            clauses.append(model.app == self.tenant_id)

        if hasattr(model, "user_id"):
            clauses.append(model.user_id == self.user_id)

        return clauses


# ---------------------------------------------------------------------------
# Dependencia FastAPI
# ---------------------------------------------------------------------------

async def get_tenant_filter(
    current_user: Usuario = Depends(get_current_user),
) -> TenantFilter:
    """
    Dependencia de FastAPI que construye un TenantFilter desde el usuario
    autenticado en la request actual.

    El `tenant_id` se extrae de `Usuario.tenant_id`.
    El `user_id` se extrae de `Usuario.id`.

    NUNCA usa parámetros del body o query string para determinar el tenant.

    Returns:
        TenantFilter listo para inyectar en endpoints.
    """
    return TenantFilter(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
    )
