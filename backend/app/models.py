"""Modelos SQLAlchemy para Script9 Engine."""

import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Usuario(Base):
    """Modelo de usuario vinculado a Firebase Auth."""

    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    firebase_uid: Mapped[str] = mapped_column(String(128), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255))
    nombre: Mapped[str] = mapped_column(String(255), default="")
    plan_suscripcion: Mapped[str] = mapped_column(String(50), default="trial")
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subscription_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    current_period_end: Mapped[datetime.datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    actualizado_en: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
