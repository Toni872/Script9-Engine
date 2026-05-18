"""Schemas Pydantic v2 para el módulo de usuarios."""

from datetime import datetime

from pydantic import BaseModel


class UsuarioRead(BaseModel):
    """Schema de lectura del perfil de usuario."""

    id: int
    firebase_uid: str
    email: str
    nombre: str
    plan_suscripcion: str
    stripe_customer_id: str | None = None
    activo: bool
    creado_en: datetime
    actualizado_en: datetime

    model_config = {"from_attributes": True}


class UsuarioUpdate(BaseModel):
    """Schema para actualización parcial del perfil."""

    nombre: str | None = None
    email: str | None = None
