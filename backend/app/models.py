"""Modelos SQLAlchemy para Script9 Engine."""

from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

    # ── Nuevo campo multi-tenant ──────────────────────────────────────────────
    tenant_id: Mapped[str] = mapped_column(
        String(100),
        default="script9",
        nullable=False,
        index=True,
        comment="Discriminador de app/tenant para filtrado multi-tenant",
    )
    # ─────────────────────────────────────────────────────────────────────────

    # Relaciones multi-tenant
    cotizaciones: Mapped[list[Cotizacion]] = relationship(back_populates="usuario")
    leads: Mapped[list[Lead]] = relationship(back_populates="usuario")
    meetings: Mapped[list[Meeting]] = relationship(back_populates="usuario")
    activity_events: Mapped[list[ActivityEvent]] = relationship(back_populates="usuario")


class WebhookEvent(Base):
    """Log de eventos recibidos — para idempotencia de webhooks de Stripe.

    Stripe puede reenviar el mismo evento varias veces (5xx, timeouts).
    Guardamos el event_id para evitar procesar el mismo evento dos veces.
    """

    __tablename__ = "webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    event_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    provider: Mapped[str] = mapped_column(String(50), default="stripe")
    processed_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Cotizacion
# ---------------------------------------------------------------------------

class Cotizacion(Base):
    """
    Cotización comercial de un usuario para una app específica.

    Restricción única: un usuario solo puede tener una cotización activa
    por app (índice unique en user_id + app).
    """

    __tablename__ = "cotizaciones"
    __table_args__ = (
        UniqueConstraint("user_id", "app", name="uq_cotizacion_user_app"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    app: Mapped[str] = mapped_column(
        String(100), nullable=False, default="script9", index=True
    )
    plan_interno: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="starter | professional | enterprise"
    )
    precio_eur: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stripe_price_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    valido_hasta: Mapped[datetime.date | None] = mapped_column(Date, nullable=True)
    notas_admin: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="Notas privadas visibles solo para Antonio"
    )
    creado_en: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )
    actualizado_en: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    usuario: Mapped[Usuario] = relationship(back_populates="cotizaciones")


# ---------------------------------------------------------------------------
# Lead
# ---------------------------------------------------------------------------

class Lead(Base):
    """
    Lead capturado desde un formulario público.

    El campo `slug` identifica qué formulario/landing originó el lead.
    El campo `score` (0-100) se calcula mediante lead_scoring.py.
    """

    __tablename__ = "leads"
    __table_args__ = (
        Index("ix_lead_user_app_creado", "user_id", "app", "creado_en"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    app: Mapped[str] = mapped_column(
        String(100), nullable=False, default="script9", index=True
    )
    slug: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="Identificador del formulario, ej: 'mi-empresa'"
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    mensaje: Mapped[str] = mapped_column(Text, nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(50), nullable=True)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    estado: Mapped[str] = mapped_column(
        String(50),
        default="new",
        nullable=False,
        comment="new | qualified | rejected | converted",
    )
    creado_en: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    usuario: Mapped[Usuario] = relationship(back_populates="leads")
    meetings: Mapped[list[Meeting]] = relationship(back_populates="lead")


# ---------------------------------------------------------------------------
# Meeting
# ---------------------------------------------------------------------------

class Meeting(Base):
    """
    Reunión agendada vinculada a un lead.

    `external_id` almacena el ID de Cal.com / Calendly para reconciliación
    con webhooks externos.
    """

    __tablename__ = "meetings"
    __table_args__ = (
        Index("ix_meeting_user_app", "user_id", "app"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    lead_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    app: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    scheduled_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(50),
        default="proposed",
        nullable=False,
        comment="proposed | confirmed | cancelled",
    )
    external_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="ID externo de Cal.com o Calendly",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    usuario: Mapped[Usuario] = relationship(back_populates="meetings")
    lead: Mapped[Lead] = relationship(back_populates="meetings")


# ---------------------------------------------------------------------------
# ActivityEvent
# ---------------------------------------------------------------------------

class ActivityEvent(Base):
    """
    Registro de actividad del sistema para un usuario y app específicos.

    El campo `metadata` (JSONB) almacena datos enriquecidos según el `tipo`
    del evento, sin esquema fijo.
    """

    __tablename__ = "activity_events"
    __table_args__ = (
        Index("ix_activity_user_app_creado", "user_id", "app", "creado_en"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False
    )
    app: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment=(
            "lead_captured | meeting_scheduled | meeting_confirmed"
            " | crm_synced | subscription_activated"
        ),
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        "metadata",  # nombre real de columna en PostgreSQL
        JSONB,
        nullable=False,
        default=dict,
    )
    creado_en: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=False), server_default=func.now(), nullable=False
    )

    usuario: Mapped[Usuario] = relationship(back_populates="activity_events")
