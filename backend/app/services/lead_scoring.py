"""
Servicio de puntuación de leads (lead scoring).

Función pura, sin dependencias HTTP ni de base de datos.
Directamente testeable con pytest.

Escala: 0-100 puntos.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Dominios de email corporativo conocidos (alta señal comercial)
# ---------------------------------------------------------------------------

_DOMINIOS_EMPRESA_CONOCIDOS: frozenset[str] = frozenset(
    {
        # Big tech / cloud
        "google.com", "microsoft.com", "amazon.com", "apple.com", "meta.com",
        "salesforce.com", "hubspot.com", "oracle.com", "sap.com", "ibm.com",
        # Bancos y finanzas
        "bbva.com", "santander.com", "caixabank.com", "ing.com", "bankia.es",
        # Telco
        "telefonica.com", "vodafone.com", "orange.es",
        # Retail / industria española
        "inditex.com", "mercadona.es", "el-corte-ingles.es", "repsol.com",
        # Consultoría
        "accenture.com", "deloitte.com", "pwc.com", "kpmg.com", "mckinsey.com",
    }
)

# ---------------------------------------------------------------------------
# Palabras clave de alto valor en mensajes
# ---------------------------------------------------------------------------

_KEYWORDS_ALTO_VALOR: frozenset[str] = frozenset(
    {
        "presupuesto", "budget", "contrato", "contract",
        "integración", "integration", "api", "enterprise",
        "automatizar", "automate", "crm", "erp",
        "facturación", "billing", "suscripción", "subscription",
        "urgente", "urgent", "piloto", "pilot", "poc",
    }
)

# ---------------------------------------------------------------------------
# Patrones de detección de idioma español
# ---------------------------------------------------------------------------

_REGEX_ESPANOL: re.Pattern[str] = re.compile(
    r"\b(que|de|la|el|en|es|los|del|con|para|una|un|por|su|al|más|también|qué|cómo)\b",
    re.IGNORECASE | re.UNICODE,
)


# ---------------------------------------------------------------------------
# Función principal
# ---------------------------------------------------------------------------

def score_lead(
    email: str,
    mensaje: str,
    telefono: str | None = None,
) -> int:
    """
    Calcula el score de un lead en una escala de 0 a 100.

    Reglas de puntuación:
    - Email de empresa conocida        → +30 pts
    - Mensaje con palabras clave       → +40 pts
    - Idioma español detectado         → +20 pts
    - Teléfono presente                → +10 pts

    Args:
        email: Dirección de email del lead.
        mensaje: Texto libre del mensaje del formulario.
        telefono: Número de teléfono (None si no se proporcionó).

    Returns:
        Entero entre 0 y 100.
    """
    puntos: int = 0

    # ── Regla 1: email de empresa conocida (+30) ─────────────────────────────
    dominio = _extraer_dominio(email)
    if dominio in _DOMINIOS_EMPRESA_CONOCIDOS:
        puntos += 30

    # ── Regla 2: palabras clave de alto valor en el mensaje (+40) ────────────
    mensaje_lower = mensaje.lower()
    for keyword in _KEYWORDS_ALTO_VALOR:
        if keyword in mensaje_lower:
            puntos += 40
            break  # basta con encontrar una para sumar los 40

    # ── Regla 3: idioma español (+20) ────────────────────────────────────────
    coincidencias = _REGEX_ESPANOL.findall(mensaje)
    if len(coincidencias) >= 3:  # umbral mínimo: 3 palabras españolas
        puntos += 20

    # ── Regla 4: teléfono presente (+10) ─────────────────────────────────────
    if telefono and telefono.strip():
        puntos += 10

    return min(puntos, 100)


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _extraer_dominio(email: str) -> str:
    """Extrae el dominio en minúsculas de una dirección de email."""
    try:
        return email.split("@", 1)[1].lower().strip()
    except IndexError:
        return ""
