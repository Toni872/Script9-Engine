"""Configuración centralizada con Pydantic Settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Variables de entorno validadas al iniciar la app."""

    environment: str = "local"
    debug: bool = True

    # Base de datos
    database_url: str = "postgresql+asyncpg://script9:script9secret@localhost:5432/script9_db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Firebase Admin SDK
    firebase_credentials_path: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""

    # Sentry
    sentry_dsn: str = ""

    @property
    def docs_enabled(self) -> bool:
        return self.environment == "local"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
