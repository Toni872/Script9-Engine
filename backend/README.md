# Script9 Engine — Backend

FastAPI + PostgreSQL + Firebase Auth

## Stack

| Componente | Versión |
|---|---|
| Python | 3.12 |
| FastAPI | ^0.115 |
| SQLAlchemy (async) | ^2.0 |
| PostgreSQL | 16 |
| Firebase Admin SDK | ^6.6 |

## Inicio rápido

```bash
# Copiar variables de entorno
cp .env.example .env

# Instalar dependencias
poetry install

# Levantar la API (puerto 8081)
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload

# Health check
curl http://localhost:8081/health
# → {"status":"ok","environment":"local"}

# Swagger UI (solo en entorno local)
open http://localhost:8081/docs
```

## Comandos de desarrollo

```bash
# Lint
poetry run ruff check app/

# Tipos
poetry run mypy app/

# Tests
poetry run pytest --cov=app

# Exportar OpenAPI
poetry run python scripts/generate_openapi.py
```

## Endpoints

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| GET | `/health` | No | Health check |
| GET | `/api/v1/health` | No | Health check v1 |
| GET | `/api/v1/usuarios/me` | Firebase JWT | Perfil del usuario |
| PATCH | `/api/v1/usuarios/me` | Firebase JWT | Actualizar perfil |
| POST | `/webhooks/stripe` | Firma Stripe | Eventos de Stripe |

## Variables de entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `DATABASE_URL` | PostgreSQL async URL | Sí |
| `FIREBASE_CREDENTIALS_PATH` | Ruta al JSON de credenciales Firebase | Sí (prod) |
| `STRIPE_SECRET_KEY` | Clave secreta de Stripe | No (prod) |
| `STRIPE_WEBHOOK_SECRET` | Secret para verificar webhooks | No (prod) |
| `SENTRY_DSN` | DSN de Sentry para error tracking | No |

## Tests

Suite hermética de pytest sobre Python 3.12. No requiere Postgres, Redis,
Stripe ni acceso a la red — usa SQLite en memoria y mocks de Firebase
Admin. Stripe y el paquete `script9-billing` se cubren en un PR
subsiguiente (`step-6b-stripe-testing`).

```bash
poetry run pytest                       # ejecuta la suite
poetry run pytest --cov=app             # con reporte de cobertura
poetry run pytest tests/api/test_auth.py -v   # un archivo específico
poetry run pytest -k test_health        # por nombre de test
```

**Target de cobertura**: ≥ 80% de líneas combinadas en los módulos
`auth.py` + `usuarios.py` + `health.py` + `usuario_service.py` + `models.py`.
La cobertura es informativa (no se configura `--cov-fail-under`) porque
Stripe y `script9-billing` quedan fuera de este PR.

`asyncio_mode = "auto"` está activo: no se necesitan decoradores
`@pytest.mark.asyncio`.
