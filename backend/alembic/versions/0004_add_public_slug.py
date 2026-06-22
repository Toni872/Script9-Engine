"""Add public_slug field to usuarios table for public form routing.

Revision ID: 0004_add_public_slug
Revises: 0003_multi_tenant_schema
Create Date: 2026-06-22

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = "0004_add_public_slug"
down_revision = "0003_multi_tenant_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column(
            "public_slug",
            sa.String(255),
            nullable=True,
            unique=True,
            comment="Slug público del formulario, ej: 'toni-lloret' para /l/toni-lloret",
        ),
    )
    # Crear índice para lookup rápido
    op.create_index("ix_usuarios_public_slug", "usuarios", ["public_slug"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_usuarios_public_slug", table_name="usuarios")
    op.drop_column("usuarios", "public_slug")
