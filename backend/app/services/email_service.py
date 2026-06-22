"""
Servicio de email — stub.

Script9 Engine es un servicio B2B backend. No envía emails directamente.
Los emails se gestionan desde la web oficial de Script9 (Script9-Project).
Este módulo existe como interfaz para poder extenderlo via webhook/API
en el futuro si se necesita.
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
    Stub — solo loguea. La gestión de emails está en Script9-Project.
    """
    logger.info(
        "email.invitation_sent",
        to=email,
        url=invitation_url,
        note="Email handled by Script9-Project",
    )


async def send_meeting_proposal_email(proposal: MeetingProposalEmail) -> bool:
    """
    Stub — solo loguea que se habría enviado un email.

    En producción esto podría enviar un webhook a la web oficial de Script9
    para que ella se encargue del envío real del email.
    """
    logger.info(
        "email.meeting_proposal_pending",
        lead_email=proposal.lead_email,
        lead_nombre=proposal.lead_nombre,
        empresa=proposal.empresa,
        agendador_url=proposal.agendador_url,
        note="Email delivery handled by Script9-Project",
    )
    return True
