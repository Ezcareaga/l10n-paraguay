# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del generador CDC — Python puro, no requiere Odoo registry."""
import datetime

from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_edi.services import cdc

# Ejemplo oficial del Manual Técnico SIFEN v150 (docs/02 sección 3).
OFFICIAL_CDC = "01800695631001003000013712022010619364760029"


@tagged("standard", "l10n_py")
class TestCdc(BaseCase):
    def _official_kwargs(self, **overrides):
        kwargs = {
            "document_type": "1",
            "ruc": "80069563",
            "ruc_dv": 1,
            "establishment": "1",
            "expedition_point": "3",
            "document_number": "137",
            "taxpayer_type": "1",
            "issue_date": datetime.date(2022, 1, 6),
            "emission_type": "1",
            "security_code": "936476002",
        }
        kwargs.update(overrides)
        return kwargs

    # ------------------------------------------------------------------
    # cdc_check_digit
    # ------------------------------------------------------------------
    def test_check_digit_official_example(self):
        self.assertEqual(cdc.cdc_check_digit(OFFICIAL_CDC[:43]), 9)

    def test_check_digit_wrong_length_raises(self):
        with self.assertRaises(cdc.CdcError):
            cdc.cdc_check_digit("123")
        with self.assertRaises(cdc.CdcError):
            cdc.cdc_check_digit(OFFICIAL_CDC)  # 44 != 43

    def test_check_digit_non_digits_raises(self):
        with self.assertRaises(cdc.CdcError):
            cdc.cdc_check_digit("a" * 43)

    # ------------------------------------------------------------------
    # compose_cdc
    # ------------------------------------------------------------------
    def test_compose_official_example(self):
        self.assertEqual(cdc.compose_cdc(**self._official_kwargs()), OFFICIAL_CDC)

    def test_compose_accepts_padded_inputs(self):
        """Los componentes pueden venir ya zero-padded o sin pad."""
        result = cdc.compose_cdc(
            **self._official_kwargs(
                document_type="01",
                establishment="001",
                expedition_point="003",
                document_number="0000137",
            )
        )
        self.assertEqual(result, OFFICIAL_CDC)

    def test_compose_generates_security_code_when_missing(self):
        result = cdc.compose_cdc(**self._official_kwargs(security_code=None))
        self.assertEqual(len(result), 44)
        self.assertTrue(result.isdigit())
        self.assertTrue(cdc.validate_cdc(result))

    def test_compose_datetime_accepted(self):
        """datetime.datetime también sirve como issue_date (usa .date())."""
        result = cdc.compose_cdc(
            **self._official_kwargs(issue_date=datetime.datetime(2022, 1, 6, 14, 30))
        )
        self.assertEqual(result, OFFICIAL_CDC)

    def test_compose_invalid_inputs_raise(self):
        bad_cases = [
            {"document_type": "100"},  # > 2 dígitos
            {"document_type": "x"},
            {"ruc": "123456789"},  # > 8 dígitos
            {"ruc": ""},
            {"ruc_dv": 12},  # > 1 dígito
            {"establishment": "1234"},  # > 3 dígitos
            {"expedition_point": ""},
            {"document_number": "12345678"},  # > 7 dígitos
            {"taxpayer_type": "3"},  # solo 1/2
            {"emission_type": "9"},  # solo 1/2
            {"security_code": "12345"},  # != 9 dígitos
            {"security_code": "12345678a"},
            {"issue_date": "2022-01-06"},  # str no aceptado
        ]
        for overrides in bad_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(cdc.CdcError):
                    cdc.compose_cdc(**self._official_kwargs(**overrides))

    # ------------------------------------------------------------------
    # generate_security_code
    # ------------------------------------------------------------------
    def test_generate_security_code_format(self):
        for _ in range(20):
            code = cdc.generate_security_code()
            self.assertEqual(len(code), 9)
            self.assertTrue(code.isdigit())

    def test_generate_security_code_varies(self):
        codes = {cdc.generate_security_code() for _ in range(10)}
        self.assertGreater(len(codes), 1)

    # ------------------------------------------------------------------
    # parse_cdc / validate_cdc
    # ------------------------------------------------------------------
    def test_parse_official_example(self):
        parsed = cdc.parse_cdc(OFFICIAL_CDC)
        self.assertEqual(parsed["document_type"], "01")
        self.assertEqual(parsed["ruc"], "80069563")
        self.assertEqual(parsed["ruc_dv"], "1")
        self.assertEqual(parsed["establishment"], "001")
        self.assertEqual(parsed["expedition_point"], "003")
        self.assertEqual(parsed["document_number"], "0000137")
        self.assertEqual(parsed["taxpayer_type"], "1")
        self.assertEqual(parsed["issue_date"], datetime.date(2022, 1, 6))
        self.assertEqual(parsed["emission_type"], "1")
        self.assertEqual(parsed["security_code"], "936476002")
        self.assertEqual(parsed["check_digit"], "9")

    def test_parse_invalid_raises(self):
        with self.assertRaises(cdc.CdcError):
            cdc.parse_cdc("123")  # largo incorrecto
        # DV adulterado:
        with self.assertRaises(cdc.CdcError):
            cdc.parse_cdc(OFFICIAL_CDC[:43] + "5")

    def test_validate_cdc(self):
        self.assertTrue(cdc.validate_cdc(OFFICIAL_CDC))
        self.assertFalse(cdc.validate_cdc(OFFICIAL_CDC[:43] + "5"))
        self.assertFalse(cdc.validate_cdc("abc"))
        self.assertFalse(cdc.validate_cdc(""))
        self.assertFalse(cdc.validate_cdc(None))
