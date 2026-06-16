# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del helper de fecha/hora SIFEN — Python puro, no requiere Odoo registry.

Cubre:
- format_cdc_date / parse_cdc_date (formato CDC YYYYMMDD, Manual v150 §3)
- format_de_datetime / parse_de_datetime (fecHhmmss, patrón XSD fecHhmmss de
  DE_Types_v150.xsd §343-352)
- TEST DE ACOPLAMIENTO TD-008: la porción de fecha del dFeEmiDE debe coincidir con
  el CDC, o SIFEN rechaza el DE.
"""
import datetime
import re
from zoneinfo import ZoneInfo

from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_edi.services import datetime_helpers

_PY_TZ = ZoneInfo("America/Asuncion")
_UTC_TZ = ZoneInfo("UTC")
_UTC_DT_TZ = datetime.timezone.utc

# Patrón XSD fecHhmmss (DE_Types_v150.xsd §343-352)
_XSD_PATTERN = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d$")


@tagged("standard", "l10n_py")
class TestDatetimeHelpers(BaseCase):
    # ------------------------------------------------------------------
    # format_cdc_date
    # ------------------------------------------------------------------
    def test_format_cdc_date_from_date(self):
        """date(2022,1,6) -> '20220106' (ejemplo oficial CDC)."""
        result = datetime_helpers.format_cdc_date(datetime.date(2022, 1, 6))
        self.assertEqual(result, "20220106")

    def test_format_cdc_date_from_datetime(self):
        """datetime con hora -> usa .date(), devuelve '20220106'."""
        result = datetime_helpers.format_cdc_date(datetime.datetime(2022, 1, 6, 14, 30))
        self.assertEqual(result, "20220106")

    def test_format_cdc_date_length(self):
        """Siempre 8 dígitos."""
        result = datetime_helpers.format_cdc_date(datetime.date(2022, 1, 6))
        self.assertEqual(len(result), 8)
        self.assertTrue(result.isdigit())

    # ------------------------------------------------------------------
    # parse_cdc_date
    # ------------------------------------------------------------------
    def test_parse_cdc_date_ok(self):
        """'20220106' -> date(2022,1,6)."""
        result = datetime_helpers.parse_cdc_date("20220106")
        self.assertEqual(result, datetime.date(2022, 1, 6))

    def test_parse_cdc_date_round_trip(self):
        """format_cdc_date y parse_cdc_date son inversas."""
        original = datetime.date(2022, 1, 6)
        self.assertEqual(
            datetime_helpers.parse_cdc_date(datetime_helpers.format_cdc_date(original)),
            original,
        )

    def test_parse_cdc_date_invalid_month_13(self):
        """Mes 13 imposible -> ValueError."""
        with self.assertRaises(ValueError):
            datetime_helpers.parse_cdc_date("20221306")

    def test_parse_cdc_date_wrong_length(self):
        """7 dígitos (un dígito de menos) -> ValueError."""
        with self.assertRaises(ValueError):
            datetime_helpers.parse_cdc_date("2022010")

    def test_parse_cdc_date_non_digits(self):
        """Texto no numérico -> ValueError."""
        with self.assertRaises(ValueError):
            datetime_helpers.parse_cdc_date("2022-1-6")

    # ------------------------------------------------------------------
    # format_de_datetime
    # ------------------------------------------------------------------
    def test_format_de_datetime_official_xsd_example(self):
        """Ejemplo oficial del XSD: datetime(2020,5,7,15,3,57) -> '2020-05-07T15:03:57'."""
        result = datetime_helpers.format_de_datetime(
            datetime.datetime(2020, 5, 7, 15, 3, 57)
        )
        self.assertEqual(result, "2020-05-07T15:03:57")

    def test_format_de_datetime_drops_microseconds(self):
        """Microsegundos deben descartarse silenciosamente."""
        result = datetime_helpers.format_de_datetime(
            datetime.datetime(2020, 5, 7, 15, 3, 57, 123456)
        )
        self.assertEqual(result, "2020-05-07T15:03:57")

    def test_format_de_datetime_matches_xsd_pattern(self):
        """El output debe satisfacer el patrón XSD fecHhmmss."""
        result = datetime_helpers.format_de_datetime(
            datetime.datetime(2022, 1, 6, 14, 30, 0)
        )
        self.assertRegex(result, _XSD_PATTERN)

    def test_format_de_datetime_tz_aware_converts_to_asuncion(self):
        """datetime tz-aware UTC se convierte a America/Asuncion antes de emitir.

        No hardcodeamos el offset (Paraguay cambió reglas DST).
        Verificamos: (a) coincide el patrón XSD, (b) round-trips con parse_de_datetime,
        (c) el resultado esperado computado via astimezone en el test mismo.
        """
        # 2022-01-06T18:00:00 UTC = hora local PY (sin DST en enero)
        utc_dt = datetime.datetime(2022, 1, 6, 18, 0, 0, tzinfo=_UTC_TZ)
        expected_local = utc_dt.astimezone(_PY_TZ).replace(tzinfo=None)
        expected_str = expected_local.strftime("%Y-%m-%dT%H:%M:%S")

        result = datetime_helpers.format_de_datetime(utc_dt)

        self.assertRegex(result, _XSD_PATTERN)
        self.assertEqual(result, expected_str)
        # round-trip
        self.assertEqual(
            datetime_helpers.parse_de_datetime(result),
            expected_local.replace(microsecond=0),
        )

    def test_format_de_datetime_rejects_plain_date(self):
        """Un date plano (no datetime) debe levantar TypeError."""
        with self.assertRaises(TypeError):
            datetime_helpers.format_de_datetime(datetime.date(2022, 1, 6))

    # ------------------------------------------------------------------
    # parse_de_datetime
    # ------------------------------------------------------------------
    def test_parse_de_datetime_ok(self):
        """'2020-05-07T15:03:57' -> datetime(2020,5,7,15,3,57) naive."""
        result = datetime_helpers.parse_de_datetime("2020-05-07T15:03:57")
        self.assertEqual(result, datetime.datetime(2020, 5, 7, 15, 3, 57))
        self.assertIsNone(result.tzinfo)  # naive

    def test_parse_de_datetime_round_trip(self):
        """format_de_datetime y parse_de_datetime son inversas."""
        original = datetime.datetime(2020, 5, 7, 15, 3, 57)
        self.assertEqual(
            datetime_helpers.parse_de_datetime(
                datetime_helpers.format_de_datetime(original)
            ),
            original,
        )

    def test_parse_de_datetime_invalid_raises(self):
        """Formato incorrecto levanta ValueError."""
        bad_cases = [
            "2020-05-07",  # falta hora
            "20200507T150357",  # sin guiones/colones
            "2020-05-07T15:03",  # falta segundos
            "not-a-date",
        ]
        for text in bad_cases:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    datetime_helpers.parse_de_datetime(text)

    # ------------------------------------------------------------------
    # TEST DE ACOPLAMIENTO TD-008 (CRÍTICO)
    # ------------------------------------------------------------------
    def test_cdc_date_equals_de_datetime_date_portion(self):
        """La porción de fecha de dFeEmiDE debe coincidir con la fecha del CDC.

        SIFEN rechaza el DE si la fecha codificada en el CDC y el campo dFeEmiDE
        del XML no corresponden al mismo día. Este test es el regression guard
        del propósito de TD-008: un único helper centralizado garantiza que no
        puedan divergir.

        Fórmula: format_cdc_date(dt) == format_de_datetime(dt)[:10].replace("-", "")
        """
        test_datetimes = [
            datetime.datetime(2022, 1, 6, 14, 30, 0),
            datetime.datetime(2020, 5, 7, 15, 3, 57),
            datetime.datetime(2025, 12, 31, 23, 59, 59),
            # Caso edge UTC: la fecha local PY difiere de la UTC
            # 00:30 UTC del 2022-01-01 = 31-dic-2021 en PY (UTC-3 verano)
            datetime.datetime(2022, 1, 1, 0, 30, 0, tzinfo=_UTC_DT_TZ),
        ]
        for dt in test_datetimes:
            with self.subTest(dt=dt):
                cdc_date_str = datetime_helpers.format_cdc_date(dt)
                de_date_str = datetime_helpers.format_de_datetime(dt)[:10].replace(
                    "-", ""
                )
                self.assertEqual(
                    cdc_date_str,
                    de_date_str,
                    msg=(
                        f"Divergencia CDC/dFeEmiDE para {dt}: "
                        f"CDC={cdc_date_str!r}, dFeEmiDE fecha={de_date_str!r}"
                    ),
                )

    def test_format_cdc_date_normalizes_aware_to_py_local(self):
        """format_cdc_date con tz-aware debe usar la fecha local PY, no la UTC.

        00:30 UTC del 2022-01-01 corresponde al 2021-12-31 en America/Asuncion
        (Paraguay en horario de verano, UTC-3). El CDC debe reflejar la fecha
        local PY para alinearse con dFeEmiDE y no ser rechazado por SIFEN.
        """
        aware_dt = datetime.datetime(2022, 1, 1, 0, 30, 0, tzinfo=_UTC_DT_TZ)
        # Computar el esperado vía conversión explícita para no hardcodear offset
        expected = (
            aware_dt.astimezone(ZoneInfo("America/Asuncion")).date().strftime("%Y%m%d")
        )
        result = datetime_helpers.format_cdc_date(aware_dt)
        self.assertEqual(result, expected)
        # Documentar la intención: la fecha UTC no debe filtrarse al CDC
        self.assertNotEqual(result, "20220101")
