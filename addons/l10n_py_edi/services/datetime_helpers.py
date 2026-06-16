# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Helpers de fecha/hora para el DE SIFEN (Manual v150).

Acoplamiento CDC / dFeEmiDE
---------------------------
El CDC (Código de Control, 44 dígitos, §3 del Manual v150) codifica la fecha de
emisión como ``YYYYMMDD`` en las posiciones 26-33 (1-based).  El campo XML
``dFeEmiDE`` usa el tipo XSD ``fecHhmmss`` cuyo patrón exacto es::

    \\d{4}-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\d   →   YYYY-MM-DDThh:mm:ss

(verificado en docs/original/xsd/DE_Types_v150.xsd, líneas 343-352).

La porción de FECHA de ``dFeEmiDE`` (los 10 primeros caracteres, ``YYYY-MM-DD``)
debe representar el MISMO día calendárico que los 8 dígitos del CDC.  Los dos
campos usan formatos distintos, pero SIFEN rechaza el DE si la fecha del CDC y
la fecha embebida en ``dFeEmiDE`` difieren.

Este módulo centraliza el formateo para que no puedan divergir: ambos derivan de
la misma fuente (un ``datetime`` único) pasada a ``format_cdc_date`` y
``format_de_datetime``.

Contrato de zona horaria para ``format_de_datetime``
----------------------------------------------------
- ``datetime`` **naive**: se asume que ya está en hora local de Paraguay
  (``America/Asuncion``); se emite tal cual, sin conversión.
- ``datetime`` **tz-aware**: se convierte a ``America/Asuncion`` y se emite la
  hora local resultante (naive, sin sufijo de zona).  No se hardcodea el offset
  porque Paraguay cambió sus reglas de horario de verano.
- Un objeto ``datetime.date`` plano (no ``datetime``) levanta ``TypeError``:
  no hay hora de referencia para ``dFeEmiDE``, por lo que inventar T00:00:00
  sería un error silencioso.

Importable sin registry: este módulo NO importa de ``odoo``.
"""
import datetime
from zoneinfo import ZoneInfo

_PY_TZ = ZoneInfo("America/Asuncion")

# Formato CDC: 8 dígitos YYYYMMDD (Manual v150 §3, posiciones 26-33 del CDC)
_CDC_DATE_FMT = "%Y%m%d"

# Formato dFeEmiDE: patrón XSD fecHhmmss (DE_Types_v150.xsd líneas 343-352)
_DE_DATETIME_FMT = "%Y-%m-%dT%H:%M:%S"


def format_cdc_date(value: "datetime.date | datetime.datetime") -> str:
    """Formatea una fecha para el campo CDC (posiciones 26-33).

    :param value: :class:`datetime.date` o :class:`datetime.datetime`.
        Si es ``datetime`` **naive**, usa su componente ``.date()`` directamente
        (se asume que ya está en hora local de Paraguay).
        Si es ``datetime`` **tz-aware**, convierte primero a ``America/Asuncion``
        y extrae la fecha local resultante — consistente con ``format_de_datetime``,
        garantizando que CDC y dFeEmiDE reflejen el mismo día calendárico (TD-008).
    :returns: Cadena ``YYYYMMDD`` (8 dígitos, sin separadores).
    :raises TypeError: si ``value`` no es ``date`` ni ``datetime``.
    """
    if isinstance(value, datetime.datetime):
        if value.tzinfo is not None:
            value = value.astimezone(_PY_TZ)
        value = value.date()
    if not isinstance(value, datetime.date):
        raise TypeError(
            "format_cdc_date espera datetime.date o datetime.datetime, "
            "llegó %r" % type(value)
        )
    return value.strftime(_CDC_DATE_FMT)


def parse_cdc_date(text: str) -> datetime.date:
    """Parsea la porción de fecha del CDC (``YYYYMMDD``) a :class:`datetime.date`.

    :param text: 8 dígitos en formato ``YYYYMMDD``.
    :returns: :class:`datetime.date` correspondiente.
    :raises ValueError: si el texto no es exactamente 8 dígitos, o si
        la fecha resultante es inválida (p. ej. mes 13, día 32).
    """
    if len(text) != 8 or not (text.isascii() and text.isdigit()):
        raise ValueError("parse_cdc_date espera 8 dígitos YYYYMMDD, llegó %r" % text)
    return datetime.datetime.strptime(text, _CDC_DATE_FMT).date()


def format_de_datetime(value: datetime.datetime) -> str:
    """Formatea un datetime para el campo XML ``dFeEmiDE`` (tipo ``fecHhmmss``).

    El patrón XSD es ``\\d{4}-\\d\\d-\\d\\dT\\d\\d:\\d\\d:\\d\\d``
    (ejemplo oficial: ``2020-05-07T15:03:57``).

    - Microsegundos se descartan.
    - Si ``value`` es tz-aware, se convierte a ``America/Asuncion`` antes
      de emitir (sin sufijo de zona en el resultado).
    - Si ``value`` es naive, se emite tal cual (se asume hora local PY).

    :param value: :class:`datetime.datetime`.
    :returns: Cadena ``YYYY-MM-DDThh:mm:ss`` sin zona horaria ni fracciones.
    :raises TypeError: si ``value`` es un :class:`datetime.date` plano (no
        ``datetime``).  Inventar T00:00:00 sería un error silencioso.
    """
    # isinstance(datetime, date) == True en Python, por eso primero datetime
    if not isinstance(value, datetime.datetime):
        raise TypeError(
            "format_de_datetime espera datetime.datetime, llegó %r" % type(value)
        )
    if value.tzinfo is not None:
        value = value.astimezone(_PY_TZ).replace(tzinfo=None)
    return value.replace(microsecond=0).strftime(_DE_DATETIME_FMT)


def parse_de_datetime(text: str) -> datetime.datetime:
    """Parsea ``dFeEmiDE`` (``YYYY-MM-DDThh:mm:ss``) a :class:`datetime.datetime` naive.

    :param text: Cadena en formato ``YYYY-MM-DDThh:mm:ss`` (sin zona horaria).
    :returns: :class:`datetime.datetime` naive correspondiente.
    :raises ValueError: si el texto no cumple el patrón exacto o la fecha/hora
        resultante es inválida.
    """
    try:
        return datetime.datetime.strptime(text, _DE_DATETIME_FMT)
    except (ValueError, TypeError) as exc:
        raise ValueError(
            "parse_de_datetime espera 'YYYY-MM-DDThh:mm:ss', llegó %r" % text
        ) from exc
