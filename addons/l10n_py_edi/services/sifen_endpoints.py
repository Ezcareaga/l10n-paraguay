# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""URLs de los Web Services SIFEN (SOAP 1.2) — Manual Técnico v150 §6.

Cada constante expone la URL completa del WSDL para un entorno (test/prod).
El cliente SOAP (``sifen_client.SifenClient``) recibe la URL del WSDL en
construcción; estas constantes son la fuente canónica para las operaciones
estándar.

URLs tomadas de docs/02_SIFEN_REFERENCIA_COMPLETA.md (confirmadas contra el
Manual Técnico SIFEN v150 §6 — Web Services):

    Base test: https://sifen-test.set.gov.py/de/ws/
    Base prod: https://sifen.set.gov.py/de/ws/

TODO (PR-5 abierto): verificar paths exactos contra los WSDLs reales
descargados de sifen-test y versionar en ``wsdl/``; confirmar que los paths
de producción son idénticos a los de test excepto por el dominio.
"""

# ── Entorno de homologación (sifen-test) ─────────────────────────────────────

_TEST_BASE = "https://sifen-test.set.gov.py/de/ws"

# siRecepDE — recepción síncrona de un DE individual
SIFEN_TEST_RECEP_DE = f"{_TEST_BASE}/sync/recibe.wsdl"

# siRecepLoteDE — recepción asíncrona de lote (hasta 50 DE del mismo tipo)
SIFEN_TEST_RECEP_LOTE_DE = f"{_TEST_BASE}/async/recibe-lote.wsdl"

# siResultLoteDE — consulta resultado de procesamiento de lote
SIFEN_TEST_RESULT_LOTE_DE = f"{_TEST_BASE}/consultas/consulta-lote.wsdl"

# siConsDE — consulta DE individual por CDC
SIFEN_TEST_CONS_DE = f"{_TEST_BASE}/consultas/consulta.wsdl"

# siRecepEvento — recepción de eventos (cancelación, inutilización)
SIFEN_TEST_RECEP_EVENTO = f"{_TEST_BASE}/eventos/evento.wsdl"

# siConsRUC — consulta datos de contribuyente por RUC
SIFEN_TEST_CONS_RUC = f"{_TEST_BASE}/consultas/consulta-ruc.wsdl"

# ── Entorno de producción ─────────────────────────────────────────────────────

_PROD_BASE = "https://sifen.set.gov.py/de/ws"

# siRecepDE — recepción síncrona de un DE individual (producción)
SIFEN_PROD_RECEP_DE = f"{_PROD_BASE}/sync/recibe.wsdl"

# siRecepLoteDE — recepción asíncrona de lote (producción)
SIFEN_PROD_RECEP_LOTE_DE = f"{_PROD_BASE}/async/recibe-lote.wsdl"

# siResultLoteDE — consulta resultado de lote (producción)
SIFEN_PROD_RESULT_LOTE_DE = f"{_PROD_BASE}/consultas/consulta-lote.wsdl"

# siConsDE — consulta DE individual (producción)
SIFEN_PROD_CONS_DE = f"{_PROD_BASE}/consultas/consulta.wsdl"

# siRecepEvento — recepción de eventos (producción)
SIFEN_PROD_RECEP_EVENTO = f"{_PROD_BASE}/eventos/evento.wsdl"

# siConsRUC — consulta datos de contribuyente (producción)
SIFEN_PROD_CONS_RUC = f"{_PROD_BASE}/consultas/consulta-ruc.wsdl"

# ── Helpers ───────────────────────────────────────────────────────────────────

ENVIRONMENT_TEST = "test"
ENVIRONMENT_PROD = "prod"

_ENDPOINTS = {
    ENVIRONMENT_TEST: {
        "recep_de": SIFEN_TEST_RECEP_DE,
        "recep_lote_de": SIFEN_TEST_RECEP_LOTE_DE,
        "result_lote_de": SIFEN_TEST_RESULT_LOTE_DE,
        "cons_de": SIFEN_TEST_CONS_DE,
        "recep_evento": SIFEN_TEST_RECEP_EVENTO,
        "cons_ruc": SIFEN_TEST_CONS_RUC,
    },
    ENVIRONMENT_PROD: {
        "recep_de": SIFEN_PROD_RECEP_DE,
        "recep_lote_de": SIFEN_PROD_RECEP_LOTE_DE,
        "result_lote_de": SIFEN_PROD_RESULT_LOTE_DE,
        "cons_de": SIFEN_PROD_CONS_DE,
        "recep_evento": SIFEN_PROD_RECEP_EVENTO,
        "cons_ruc": SIFEN_PROD_CONS_RUC,
    },
}


def get_wsdl_url(operation: str, environment: str) -> str:
    """Devuelve la URL del WSDL para la operación y entorno dados.

    Args:
        operation: una de las claves del dict interno (``recep_de``,
            ``recep_lote_de``, ``result_lote_de``, ``cons_de``,
            ``recep_evento``, ``cons_ruc``).
        environment: ``"test"`` o ``"prod"``.

    Returns:
        URL completa del WSDL (str).

    Raises:
        ValueError: si ``environment`` u ``operation`` no son válidos.
    """
    if environment not in _ENDPOINTS:
        raise ValueError(
            "Entorno inválido: %r (usar %r o %r)"
            % (environment, ENVIRONMENT_TEST, ENVIRONMENT_PROD)
        )
    env_map = _ENDPOINTS[environment]
    if operation not in env_map:
        raise ValueError(
            "Operación inválida: %r (válidas: %s)"
            % (operation, ", ".join(sorted(env_map)))
        )
    return env_map[operation]
