"""
Servicio de email — envío real via Resend API.

Stubs:
- send_invitation_email: ya existe, loguea nomas
- send_meeting_proposal_email: envía email de propuesta de reunión al lead
"""

from __future__ import annotations

import structlog
from dataclasses import dataclass

logger = structlog.get_logger(__name__)


@dataclass
class MeetingProposalEmail:
    """Datos para el email de propuesta de reunión."""

    lead_nombre: str
    lead_email: str
    empresa: str
    agendador_url: str
    propuesta_texto: str | None = None


async def send_invitation_email(email: str, invitation_url: str) -> None:
    """
    Envía email de invitación (stub — por ahora solo loguea).

    En producción usar Resend con la API key configurada.
    """
    logger.info(
        "email.invitation_sent",
        to=email,
        url=invitation_url,
        subject="Invitación a Script9 Engine",
    )


async def send_meeting_proposal_email(proposal: MeetingProposalEmail) -> bool:
    """
    Envía email de propuesta de reunión a un lead cualificado.

    Args:
        proposal: Datos del lead y del enlace de agendamiento.

    Returns:
        True si se envió correctamente, False si falló.
    """
    from app.config import settings

    if not settings.resend_api_key:
        logger.warning(
            "resend_api_key_not_configured",
            lead_email=proposal.lead_email,
        )
        return False

    import httpx

    payload = {
        "from": "Script9 Engine <noreply@script-9.com>",
        "to": [proposal.lead_email],
        "subject": f"¡{proposal.lead_nombre}! Tienes una propuesta de Script9 Engine",
        "html": _build_proposal_html(proposal),
        "text": _build_proposal_text(proposal),
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.resend.com/emails",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.resend_api_key}",
                    "Content-Type": "application/json",
                },
            )
            response.raise_for_status()
            logger.info(
                "email.meeting_proposal_sent",
                lead_email=proposal.lead_email,
                status=response.status_code,
            )
            return True
    except Exception as e:
        logger.error(
            "email.meeting_proposal_failed",
            lead_email=proposal.lead_email,
            error=str(e),
        )
        return False


def _build_proposal_html(proposal: MeetingProposalEmail) -> str:
    """Construye el HTML del email de propuesta."""
    nombre = proposal.lead_nombre
    empresa = proposal.empresa
    url = proposal.agendador_url
    propuesta = (
        proposal.propuesta_texto
        or f"Hola {nombre}, gracias por tu interés en Script9 Engine. "
        "Nos encantaría agendar una llamada para conocerte mejor y mostrarte cómo podemos ayudar a {empresa}."
    )

    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Propuesta Script9 Engine</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0c;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;color:#e2e8f0;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0a0a0c;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#10b981 0%,#059669 100%);border-radius:16px 16px 0 0;padding:40px;text-align:center;">
              <h1 style="margin:0;font-size:28px;font-weight:800;color:#0a0a0c;font-family:'Space Grotesk',sans-serif;">
                Script9 Engine
              </h1>
              <p style="margin:8px 0 0;color:#0a0a0c;opacity:0.8;font-size:14px;">
                Automatización IA para equipos comerciales
              </p>
            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td style="background:#111827;border-radius:0 0 16px 16px;padding:40px;">

              <p style="margin:0 0 24px;font-size:18px;font-weight:600;color:#f1f5f9;">
                Hola {nombre},
              </p>

              <p style="margin:0 0 24px;font-size:15px;line-height:1.7;color:#94a3b8;">
                {propuesta.replace(empresa, f"<strong>{empresa}</strong>")}
              </p>

              <!-- CTA Button -->
              <div style="text-align:center;margin:32px 0;">
                <a href="{url}"
                   style="display:inline-block;background:#10b981;color:#0a0a0c;font-weight:700;font-size:16px;
                          padding:16px 40px;border-radius:12px;text-decoration:none;">
                  Agendar mi llamada →
                </a>
              </div>

              <p style="margin:0 0 16px;font-size:14px;color:#64748b;text-align:center;">
                El enlace expira en 7 días.
              </p>

              <hr style="border:none;border-top:1px solid #1e293b;margin:32px 0;" />

              <p style="margin:0;font-size:13px;color:#475569;text-align:center;">
                ¿No puedes asistir? Responde a este email y buscaremos otro horario que te convenga.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:24px;text-align:center;">
              <p style="margin:0;font-size:12px;color:#334155;">
                © 2025 Script9 Engine · <a href="https://www.script-9.com" style="color:#10b981;">script-9.com</a>
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def _build_proposal_text(proposal: MeetingProposalEmail) -> str:
    """Construye texto plano del email."""
    url = proposal.agendador_url
    propuesta = (
        proposal.propuesta_texto
        or f"Hola {proposal.lead_nombre}, gracias por tu interés en Script9 Engine. "
        f"Nos encantaría agendar una llamada para conocerte mejor y mostrarte cómo podemos ayudar a {proposal.empresa}."
    )
    return f"""
Script9 Engine — Propuesta para {proposal.lead_nombre}

{propuesta}

👉 Agendar mi llamada: {url}

El enlace expira en 7 días.

¿No puedes asistir? Responde a este email y buscaremos otro horario.

© 2025 Script9 Engine · script-9.com
"""
