"""
Servicio de notificaciones a Slack.

Notifica al canal de ventas cuando un lead tiene score alto (≥ 70).
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass

logger = structlog.get_logger(__name__)


@dataclass
class LeadNotification:
    """Datos del lead para la notificación de Slack."""

    nombre: str
    email: str
    empresa: str
    telefono: str | None
    mensaje: str
    score: int
    slug: str
    form_url: str


async def notify_lead_to_slack(notification: LeadNotification) -> bool:
    """
    Envía un mensaje al canal de Slack con los datos del lead.

    Args:
        notification: Datos del lead captado.

    Returns:
        True si se envió correctamente, False si falló.
    """
    from app.config import settings

    if not settings.slack_webhook_url:
        logger.warning(
            "slack_webhook_not_configured",
            lead_email=notification.email,
            slug=notification.slug,
        )
        return False

    score_emoji = (
        "🔴"
        if notification.score >= 85
        else "🟠"
        if notification.score >= 70
        else "🟡"
    )

    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{score_emoji} Nuevo lead capturado — {notification.empresa}",
                    "emoji": True,
                },
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Nombre:*\n{notification.nombre}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Email:*\n{notification.email}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Empresa:*\n{notification.empresa}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Teléfono:*\n{notification.telefono or 'No proporcionado'}",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Score:*\n`{notification.score}/100`",
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Formulario:*\n{notification.form_url}",
                    },
                ],
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Mensaje:*\n>{notification.mensaje}",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Lead desde script-9.com/l/{notification.slug} • Score: {notification.score}/100",
                    }
                ],
            },
        ],
    }

    try:
        import httpx

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                settings.slack_webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            logger.info(
                "slack_notification_sent",
                lead_email=notification.email,
                score=notification.score,
                status=response.status_code,
            )
            return True
    except Exception as e:
        logger.error(
            "slack_notification_failed",
            lead_email=notification.email,
            error=str(e),
        )
        return False
