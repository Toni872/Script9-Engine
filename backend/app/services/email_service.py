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
        "bcc": ["contact@script-9.com"],
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
    """Construye el HTML del email de propuesta profesional."""
    nombre = proposal.lead_nombre
    empresa = proposal.empresa
    url = proposal.agendador_url
    propuesta = (
        proposal.propuesta_texto
        or (
            f"Hola, {nombre}. Gracias por tu interés en Script9 Engine. "
            f"Nos encantaría agendar una llamada para conocerte mejor y mostrarte "
            f"cómo podemos ayudar a <strong>{empresa}</strong>."
        )
    )

    year = 2026

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <meta name="format-detection" content="telephone=no" />
  <title>Propuesta Script9 Engine</title>
  <!--[if mso]>
  <style type="text/css">
    table {{ border-collapse: collapse; }}
    .button {{ padding: 14px 0 !important; }}
  </style>
  <![endif]-->
</head>
<body style="margin:0;padding:0;background-color:#020617;font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,Helvetica,Arial,sans-serif;color:#e2e8f0;">

  <!-- Preview text (hidden) -->
  <div style="display:none;max-height:0;overflow:hidden;">
    Automatización IA para equipos comerciales · Script9 Engine
  </div>

  <!-- Wrapper -->
  <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#020617;">
    <tr>
      <td align="center" style="padding:48px 20px;">

        <!-- Main card -->
        <table width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;">

          <!-- ── Header ── -->
          <tr>
            <td style="background-color:#0f172a;border-radius:20px 20px 0 0;padding:48px 48px 40px;text-align:center;">
              <!-- Logo wordmark -->
              <div style="margin-bottom:12px;">
                <span style="font-size:26px;font-weight:800;color:#ffffff;letter-spacing:-0.5px;">
                  Script9
                </span>
                <span style="font-size:26px;font-weight:300;color:#10b981;letter-spacing:-0.5px;">
                  Engine
                </span>
              </div>
              <!-- Tagline -->
              <p style="margin:0;font-size:13px;font-weight:500;color:#10b981;letter-spacing:2px;text-transform:uppercase;opacity:0.9;">
                Automatización IA para equipos comerciales
              </p>
            </td>
          </tr>

          <!-- ── Body ── -->
          <tr>
            <td style="background-color:#0f172a;padding:0 48px 48px;">

              <!-- Divider -->
              <div style="height:1px;background:linear-gradient(to right,transparent,#1e293b,transparent);margin-bottom:40px;"></div>

              <!-- Greeting -->
              <p style="margin:0 0 28px;font-size:22px;font-weight:600;color:#f8fafc;line-height:1.3;">
                Buenos días, {nombre}.
              </p>

              <!-- Proposal text -->
              <p style="margin:0 0 36px;font-size:15px;line-height:1.8;color:#94a3b8;">
                {propuesta}
              </p>

              <!-- CTA -->
              <table width="100%" cellpadding="0" cellspacing="0" border="0">
                <tr>
                  <td align="center">
                    <!--[if mso]>
                    <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word"
                      href="{url}" style="height:52px;v-text-anchor:middle;width:220px;" arcsize="14%" strokecolor="#10b981" fillcolor="#10b981">
                      <w:anchorlock/>
                      <center style="color:#020617;font-family:sans-serif;font-size:15px;font-weight:700;">Agendar mi llamada →</center>
                    </v:roundrect>
                    <![endif]-->
                    <!--[if !mso]><!-->
                    <a href="{url}"
                       style="display:inline-block;background-color:#10b981;color:#020617;font-size:15px;font-weight:700;
                              padding:16px 40px;border-radius:10px;text-decoration:none;letter-spacing:0.3px;">
                      Agendar mi llamada →
                    </a>
                    <!--<![endif]-->
                  </td>
                </tr>
              </table>

              <!-- Expiry note -->
              <p style="margin:24px 0 0;font-size:12px;color:#475569;text-align:center;">
                El enlace expira en 7 días.
              </p>

              <!-- Divider -->
              <div style="height:1px;background:linear-gradient(to right,transparent,#1e293b,transparent);margin:40px 0;"></div>

              <!-- Alt contact -->
              <p style="margin:0;font-size:13px;color:#64748b;text-align:center;line-height:1.6;">
                ¿No puedes asistir? Responde a este email y buscaremos otro horario que te convenga.
              </p>

            </td>
          </tr>

          <!-- ── Footer ── -->
          <tr>
            <td style="background-color:#0f172a;border-radius:0 0 20px 20px;padding:28px 48px;text-align:center;">
              <p style="margin:0;font-size:12px;color:#334155;">
                © {year} Script9 Engine ·
                <a href="https://www.script-9.com" style="color:#10b981;text-decoration:none;">script-9.com</a>
              </p>
            </td>
          </tr>

        </table>
        <!-- /Main card -->

      </td>
    </tr>
  </table>
  <!-- /Wrapper -->

</body>
</html>
"""


def _build_proposal_text(proposal: MeetingProposalEmail) -> str:
    """Construye texto plano del email."""
    url = proposal.agendador_url
    propuesta = (
        proposal.propuesta_texto
        or (
            f"Hola, {proposal.lead_nombre}. Gracias por tu interés en Script9 Engine. "
            f"Nos encantaría agendar una llamada para conocerte mejor y mostrarte "
            f"cómo podemos ayudar a {proposal.empresa}."
        )
    )
    year = 2026
    return f"""Buenos días, {proposal.lead_nombre}.

{propuesta}

👉 Agendar mi llamada: {url}

El enlace expira en 7 días.

¿No puedes asistir? Responde a este email y buscaremos otro horario que te convenga.

© {year} Script9 Engine · script-9.com
"""
