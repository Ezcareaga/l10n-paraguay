# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Generador del CDC — Código de Control de 44 dígitos (Manual SIFEN v150 §3).

Estructura (posiciones 1-based):
    01-02  tipo de DE          26-33  fecha emisión YYYYMMDD
    03-10  RUC emisor (sin DV) 34     tipo de emisión (1=normal, 2=contingencia)
    11     DV del RUC          35-43  código de seguridad (9 dígitos aleatorios)
    12-14  establecimiento     44     DV del CDC (módulo 11, basemax=11)
    15-17  punto de expedición
    18-24  número del documento
    25     tipo de contribuyente (1=PF, 2=PJ)

El DV usa la rutina oficial SET vía ``modulo11.calculate_dv(base43, basemax=11)``
(misma que el RUC — verificado contra el ejemplo oficial del manual y las libs
de producción xmlgen/jsifenlib; NO son "pesos 2-9").

Helper Python puro: no requiere registry. El import de ``modulo11`` solo carga
definiciones de módulo, no levanta Odoo.
"""
import datetime
import secrets

from odoo.addons.l10n_py_base.models import modulo11

from . import datetime_helpers

EMISSION_NORMAL = "1"
EMISSION_CONTINGENCY = "2"
TAXPAYER_TYPES = ("1", "2")  # 1=Persona Física, 2=Persona Jurídica
EMISSION_TYPES = (EMISSION_NORMAL, EMISSION_CONTINGENCY)
SECURITY_CODE_LENGTH = 9
CDC_LENGTH = 44


class CdcError(ValueError):
    """Componente inválido para componer o parsear un CDC."""


def _digits(value, length, label, pad=True):
    """Normaliza un componente numérico a ``length`` dígitos zero-padded.

    :raises CdcError: si no es numérico o excede el largo.
    """
    text = str(value if value is not None else "").strip()
    if not text or not (text.isascii() and text.isdigit()):
        raise CdcError("%s inválido: %r (se esperan dígitos)" % (label, value))
    if pad:
        text = text.zfill(length)
    if len(text) != length:
        raise CdcError("%s inválido: %r (largo esperado %d)" % (label, value, length))
    return text


def generate_security_code():
    """Código de seguridad aleatorio de 9 dígitos (CSPRNG, módulo ``secrets``)."""
    return str(secrets.randbelow(10**SECURITY_CODE_LENGTH)).zfill(
        SECURITY_CODE_LENGTH
    )


def cdc_check_digit(base43):
    """DV del CDC: módulo 11 con basemax=11 sobre los primeros 43 dígitos.

    :raises CdcError: si ``base43`` no son exactamente 43 dígitos.
    """
    base43 = str(base43 or "")
    if len(base43) != CDC_LENGTH - 1 or not (base43.isascii() and base43.isdigit()):
        raise CdcError(
            "Base del CDC inválida: se esperan 43 dígitos, llegó %r" % base43
        )
    return modulo11.calculate_dv(base43, basemax=11)


def compose_cdc(
    document_type,
    ruc,
    ruc_dv,
    establishment,
    expedition_point,
    document_number,
    taxpayer_type,
    issue_date,
    emission_type=EMISSION_NORMAL,
    security_code=None,
):
    """Compone el CDC completo de 44 dígitos (43 componentes + DV).

    :param document_type: código del tipo de DE (1=FE, 5=NC, 6=ND...).
    :param ruc: RUC del emisor sin DV (1-8 dígitos).
    :param ruc_dv: dígito verificador del RUC.
    :param establishment: código de establecimiento (1-3 dígitos).
    :param expedition_point: punto de expedición (1-3 dígitos).
    :param document_number: número del documento (1-7 dígitos).
    :param taxpayer_type: "1" (PF) o "2" (PJ).
    :param issue_date: :class:`datetime.date` o :class:`datetime.datetime`.
    :param emission_type: "1" normal (default) o "2" contingencia.
    :param security_code: 9 dígitos; si es None se genera uno aleatorio.
    :return: CDC de 44 dígitos (str).
    :raises CdcError: ante cualquier componente inválido.
    """
    # No coercer a .date() acá: format_cdc_date normaliza tz-aware a hora PY
    # antes de extraer la fecha. Coercer acá tomaría la fecha UTC y rompería
    # el acoplamiento CDC/dFeEmiDE (ver TD-008). datetime es subclase de date,
    # así que este isinstance acepta ambos.
    if not isinstance(issue_date, datetime.date):
        raise CdcError("issue_date debe ser datetime.date, llegó %r" % (issue_date,))
    taxpayer = str(taxpayer_type or "").strip()
    if taxpayer not in TAXPAYER_TYPES:
        raise CdcError(
            "Tipo de contribuyente inválido: %r (solo 1/2)" % (taxpayer_type,)
        )
    emission = str(emission_type or "").strip()
    if emission not in EMISSION_TYPES:
        raise CdcError("Tipo de emisión inválido: %r (solo 1/2)" % (emission_type,))
    if security_code is None:
        security_code = generate_security_code()

    base43 = "".join(
        (
            _digits(document_type, 2, "Tipo de DE"),
            _digits(ruc, 8, "RUC"),
            _digits(ruc_dv, 1, "DV del RUC"),
            _digits(establishment, 3, "Establecimiento"),
            _digits(expedition_point, 3, "Punto de expedición"),
            _digits(document_number, 7, "Número de documento"),
            taxpayer,
            datetime_helpers.format_cdc_date(issue_date),
            emission,
            _digits(security_code, 9, "Código de seguridad", pad=False),
        )
    )
    return base43 + str(cdc_check_digit(base43))


def parse_cdc(cdc_str):
    """Descompone un CDC de 44 dígitos en sus componentes y valida el DV.

    :return: dict con document_type, ruc, ruc_dv, establishment,
        expedition_point, document_number, taxpayer_type, issue_date
        (:class:`datetime.date`), emission_type, security_code, check_digit.
    :raises CdcError: largo/formato/DV inválidos.
    """
    cdc_str = str(cdc_str or "")
    if len(cdc_str) != CDC_LENGTH or not (cdc_str.isascii() and cdc_str.isdigit()):
        raise CdcError("CDC inválido: se esperan 44 dígitos, llegó %r" % cdc_str)
    if int(cdc_str[43]) != cdc_check_digit(cdc_str[:43]):
        raise CdcError("CDC inválido: dígito verificador incorrecto")
    try:
        issue_date = datetime_helpers.parse_cdc_date(cdc_str[25:33])
    except ValueError as exc:
        raise CdcError("CDC inválido: fecha de emisión %r" % cdc_str[25:33]) from exc
    return {
        "document_type": cdc_str[0:2],
        "ruc": cdc_str[2:10],
        "ruc_dv": cdc_str[10:11],
        "establishment": cdc_str[11:14],
        "expedition_point": cdc_str[14:17],
        "document_number": cdc_str[17:24],
        "taxpayer_type": cdc_str[24:25],
        "issue_date": issue_date,
        "emission_type": cdc_str[33:34],
        "security_code": cdc_str[34:43],
        "check_digit": cdc_str[43:44],
    }


def validate_cdc(cdc_str):
    """True si ``cdc_str`` es un CDC bien formado con DV correcto."""
    try:
        parse_cdc(cdc_str)
    except CdcError:
        return False
    return True
