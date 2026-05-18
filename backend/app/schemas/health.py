"""Schema Pydantic para el endpoint de health check."""

from pydantic import BaseModel


class HealthResponse(BaseModel):
    """Respuesta del endpoint de salud de la API."""

    status: str
    environment: str
