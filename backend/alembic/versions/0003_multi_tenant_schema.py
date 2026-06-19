"""0002_multi_tenant_schema

Revisión: 0002
Anterior: 0002 (webhook_events)

Cambios:
1. Añade columna `tenant_id` a tabla `usuarios` (default "script9")
2. Crea tabla `cotizaciones` con índice único (user_id, app)
3. Crea tabla `leads` con índice compuesto (user_id, app, creado_en)
4. Crea tabla `meetings` con índice compuesto (user_id, app)
5. Crea tabla `activity_events` con índice compuesto (user_id, app, creado_en)
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# ---------------------------------------------------------------------------
# Metadatos de revisión Alembic
# ---------------------------------------------------------------------------

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | None = None
depends_on: str | None = None


# ---------------------------------------------------------------------------
# upgrade
# ---------------------------------------------------------------------------

def upgrade() -> None:
    # ── 1. tenant_id en usuarios ─────────────────────────────────────────────
    op.add_column(
        "usuarios",
        sa.Column(
            "tenant_id",
            sa.String(length=100),
            nullable=False,
            server_default="script9",
            comment="Discriminador de app/tenant para filtrado multi-tenant",
        ),
    )
    op.create_index(
        op.f("ix_usuarios_tenant_id"),
        "usuarios",
        ["tenant_id"],
        unique=False,
    )

    # ── 2. Tabla cotizaciones ─────────────────────────────────────────────────
    op.create_table(
        "cotizaciones",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("app", sa.String(length=100), nullable=False, server_default="script9"),
        sa.Column("plan_interno", sa.String(length=50), nullable=False),
        sa.Column("precio_eur", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("stripe_price_id", sa.String(length=255), nullable=True),
        sa.Column("stripe_subscription_id", sa.String(length=255), nullable=True),
        sa.Column("valido_hasta", sa.Date(), nullable=True),
        sa.Column("notas_admin", sa.Text(), nullable=True),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=False),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=False),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_cotizaciones_app"),
        "cotizaciones",
        ["app"],
        unique=False,
    )
    op.create_unique_constraint(
        "uq_cotizacion_user_app",
        "cotizaciones",
        ["user_id", "app"],
    )

    # ── 3. Tabla leads ────────────────────────────────────────────────────────
    op.create_table(
        "leads",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("app", sa.String(length=100), nullable=False, server_default="script9"),
        sa.Column("slug", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("nombre", sa.String(length=255), nullable=False),
        sa.Column("empresa", sa.String(length=255), nullable=False),
        sa.Column("mensaje", sa.Text(), nullable=False),
        sa.Column("telefono", sa.String(length=50), nullable=True),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estado", sa.String(length=50), nullable=False, server_default="new"),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=False),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_leads_app"),
        "leads",
        ["app"],
        unique=False,
    )
    op.create_index(
        "ix_lead_user_app_creado",
        "leads",
        ["user_id", "app", "creado_en"],
        unique=False,
    )

    # ── 4. Tabla meetings ─────────────────────────────────────────────────────
    op.create_table(
        "meetings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("lead_id", sa.Integer(), nullable=False),
        sa.Column("app", sa.String(length=100), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="proposed"),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=False),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["lead_id"], ["leads.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_meetings_app"),
        "meetings",
        ["app"],
        unique=False,
    )
    op.create_index(
        "ix_meeting_user_app",
        "meetings",
        ["user_id", "app"],
        unique=False,
    )

    # ── 5. Tabla activity_events ──────────────────────────────────────────────
    op.create_table(
        "activity_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("app", sa.String(length=100), nullable=False),
        sa.Column("tipo", sa.String(length=100), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default="{}",
        ),
        sa.Column(
            "creado_en",
            sa.DateTime(timezone=False),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_activity_events_app"),
        "activity_events",
        ["app"],
        unique=False,
    )
    op.create_index(
        "ix_activity_user_app_creado",
        "activity_events",
        ["user_id", "app", "creado_en"],
        unique=False,
    )


# ---------------------------------------------------------------------------
# downgrade
# ---------------------------------------------------------------------------

def downgrade() -> None:
    # Eliminar en orden inverso (FK constraints)
    op.drop_index("ix_activity_user_app_creado", table_name="activity_events")
    op.drop_index(op.f("ix_activity_events_app"), table_name="activity_events")
    op.drop_table("activity_events")

    op.drop_index("ix_meeting_user_app", table_name="meetings")
    op.drop_index(op.f("ix_meetings_app"), table_name="meetings")
    op.drop_table("meetings")

    op.drop_index("ix_lead_user_app_creado", table_name="leads")
    op.drop_index(op.f("ix_leads_app"), table_name="leads")
    op.drop_table("leads")

    op.drop_unique_constraint("uq_cotizacion_user_app", "cotizaciones")
    op.drop_index(op.f("ix_cotizaciones_app"), table_name="cotizaciones")
    op.drop_table("cotizaciones")

    op.drop_index(op.f("ix_usuarios_tenant_id"), table_name="usuarios")
    op.drop_column("usuarios", "tenant_id")
