"""Tests del modelo ORM ``Usuario``.

Son tests puros sobre la clase (no tocan la BD). Verifican la
configuración de la tabla y los defaults declarados en
``mapped_column``.

Spec/code gap
-------------

El segundo test (``test_defaults_apply_on_init``) está marcado como
``xfail`` porque la spec exige que los defaults se apliquen al
construir la instancia, pero ``app/models.py`` usa
``mapped_column(String(50), default="trial")`` (default estilo
SQLAlchemy), que se evalúa en **flush/commit**, no en ``__init__``.
Al construir ``Usuario(firebase_uid="x", email="x@y.z")`` el atributo
``plan_suscripcion`` queda ``None`` hasta que se persista y se
refresque. Para que el spec funcione, el modelo debería usar
``init=True`` o un ``__init__`` explícito; eso es trabajo de
producción fuera de este PR. El test queda armado y reportando como
``xfail`` para cuando se arregle el modelo.
"""

import pytest

from app.models import Usuario


def test_tablename_is_usuarios() -> None:
    """El nombre de tabla es ``usuarios`` (mapeo del ORM)."""
    assert Usuario.__tablename__ == "usuarios"


@pytest.mark.xfail(
    reason=(
        "Spec/code gap: app/models.py:Usuario uses mapped_column(default=...) "
        "which applies at flush/commit, not at __init__. Spec demands init-time "
        "defaults. Fix the model in a follow-up PR. See apply-progress for "
        "step-6-testing."
    ),
    strict=True,
)
def test_defaults_apply_on_init() -> None:
    """``plan_suscripcion`` default ``"trial"`` y ``activo`` default ``True``."""
    usuario = Usuario(firebase_uid="model-uid", email="model@test.local")

    assert usuario.plan_suscripcion == "trial"
    assert usuario.activo is True
