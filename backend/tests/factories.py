"""Factories de factory-boy para los tests de Script9 Engine.

Nota de implementación
----------------------

El design de ``step-6-testing`` (ver ``#322``) asumía que ``factory-boy``
exponía ``AsyncSQLAlchemyModelFactory`` para que la factory pudiera
persistir directamente sobre la sesión async. Esa clase **no existe**
en ``factory-boy 3.3.3`` (la última versión de la rama 3.x): la API
pública de ``factory.alchemy`` solo expone ``SQLAlchemyModelFactory``.

El fallback documentado en la proposal ``#308`` (risk: *factory-boy
async API varies by version*) es construir el modelo con la factory
sincrónica y persistir manualmente desde la fixture. Por eso este
módulo exporta una ``UsuarioFactory`` que **solo construye** instancias
y el fixture ``usuario_factory`` de ``conftest.py`` se encarga de
``add()`` + ``commit()`` + ``refresh()`` sobre la ``db_session`` del
test. Esto mantiene la transacción compartida con el resto del test
(visible para los asserts y deshecha por el ``rollback`` al final).
"""

import factory

from app.models import Usuario


class UsuarioFactory(factory.Factory):
    """Factory sync para construir instancias de ``Usuario``.

    Usar siempre vía el fixture ``usuario_factory`` (no instanciar
    directamente). El fixture persiste sobre la ``db_session`` del
    test y devuelve la instancia refrescada.
    """

    class Meta:
        model = Usuario

    firebase_uid = factory.Sequence(lambda n: f"test-uid-{n}")
    email = factory.LazyAttribute(lambda o: f"{o.firebase_uid}@test.local")
    nombre = factory.Faker("name")
    plan_suscripcion = "trial"
    activo = True

    class Params:
        suspended = factory.Trait(activo=False)
