"""
Servicio de email — stub para envío de invitaciones.
"""
from __future__ import annotations

import structlog

logger = structlog.get_logger(__name__)


async def send_invitation_email(email: str, invitation_url: str) -> None:
    """
    Envía email de invitación (stub).

    En producción usar Resend (resend.com) con la API key configurada.
    Por ahora solo loguea el email.
    """
    logger.info(
        "email.invitation_sent",
        to=email,
        url=invitation_url,
        subject="Invitación a Script9 Engine",
    )
