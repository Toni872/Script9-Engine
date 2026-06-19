FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del proyecto (sin Poetry, pip directo)
RUN pip install --no-cache-dir \
    "fastapi[standard]>=0.115,<0.116" \
    "uvicorn[standard]>=0.32,<0.33" \
    "pydantic>=2.9,<3" \
    "pydantic-settings>=2.6,<3" \
    "sqlalchemy[asyncio]>=2.0,<3" \
    "asyncpg>=0.30,<0.31" \
    "alembic>=1.14,<2" \
    "firebase-admin>=6.6,<7" \
    "stripe>=11.4,<12" \
    "redis>=5.2,<6" \
    "slowapi>=0.1,<1" \
    "structlog>=24.4,<25" \
    "sentry-sdk[fastapi]>=2.18,<3" \
    "httpx>=0.28,<0.29" \
    "PyJWT>=2.8,<3"

# Paquete local script9-billing
COPY packages/ ./packages/
RUN pip install --no-cache-dir -e packages/script9-billing

COPY app/ ./app/

EXPOSE 8081

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8081"]
