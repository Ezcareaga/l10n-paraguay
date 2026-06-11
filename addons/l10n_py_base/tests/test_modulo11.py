# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del algoritmo módulo 11 — Python puro, no requiere Odoo registry."""
from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_base.models import modulo11


@tagged("standard", "l10n_py")
class TestModulo11(BaseCase):
    """Casos conocidos de la práctica DNIT y del Manual Técnico SIFEN v150."""

    # ------------------------------------------------------------------
    # calculate_dv
    # ------------------------------------------------------------------
    def test_calculate_dv_simple_ruc(self):
        """Caso de referencia: RUC del ejemplo de CDC del Manual Técnico SIFEN v150."""
        # Cuerpo + DV tomados del ejemplo de CDC del Manual Técnico SIFEN v150.
        # El algoritmo módulo 11 base 11 debe reproducirlo.
        cases = [
            ("80069563", 1),  # RUC ejemplo CDC Manual Técnico SIFEN v150
        ]
        for cuerpo, dv_esperado in cases:
            with self.subTest(cuerpo=cuerpo):
                self.assertEqual(modulo11.calculate_dv(cuerpo, basemax=11), dv_esperado)

    def test_calculate_dv_strips_non_digits(self):
        """El algoritmo ignora separadores no numéricos."""
        self.assertEqual(
            modulo11.calculate_dv("800-695-63", basemax=11),
            modulo11.calculate_dv("80069563", basemax=11),
        )

    def test_calculate_dv_empty_raises(self):
        with self.assertRaises(ValueError):
            modulo11.calculate_dv("")
        with self.assertRaises(ValueError):
            modulo11.calculate_dv("abc")

    def test_calculate_dv_cdc_official_example(self):
        """Ejemplo oficial del Manual Técnico SIFEN v150 (sección CDC).

        CDC completo: 01800695631001003000013712022010619364760029
        Los primeros 43 dígitos producen DV=9 con basemax=11 (verificado
        contra facturacionelectronicapy-xmlgen y rshk-jsifenlib, 2026-06-11).
        """
        base43 = "0180069563100100300001371202201061936476002"
        self.assertEqual(len(base43), 43)
        self.assertEqual(modulo11.calculate_dv(base43, basemax=11), 9)

    def test_calculate_dv_remainder_one_maps_to_zero(self):
        """Rutina oficial SET: resto 0 y resto 1 mapean ambos a DV 0.

        '6' con basemax=11: 6*2=12, 12%11=1 -> DV 0 (no 1).
        """
        self.assertEqual(modulo11.calculate_dv("6", basemax=11), 0)
        # resto == 0 también da 0: '0' -> suma 0
        self.assertEqual(modulo11.calculate_dv("0", basemax=11), 0)

    # ------------------------------------------------------------------
    # split_ruc
    # ------------------------------------------------------------------
    def test_split_ruc_with_dash(self):
        cuerpo, dv = modulo11.split_ruc("80069563-1")
        self.assertEqual(cuerpo, "80069563")
        self.assertEqual(dv, 1)

    def test_split_ruc_without_dash(self):
        cuerpo, dv = modulo11.split_ruc("800695631")
        self.assertEqual(cuerpo, "80069563")
        self.assertEqual(dv, 1)

    def test_split_ruc_too_short(self):
        self.assertEqual(modulo11.split_ruc(""), (None, None))
        self.assertEqual(modulo11.split_ruc("1"), (None, None))
        self.assertEqual(modulo11.split_ruc(None), (None, None))

    # ------------------------------------------------------------------
    # validate_ruc
    # ------------------------------------------------------------------
    def test_validate_ruc_valid_with_dash(self):
        # RUC sintético cuyo DV coincide con el cálculo módulo 11.
        cuerpo = "80069563"
        dv = modulo11.calculate_dv(cuerpo, basemax=11)
        self.assertTrue(modulo11.validate_ruc(f"{cuerpo}-{dv}"))

    def test_validate_ruc_valid_without_dash(self):
        cuerpo = "12345678"
        dv = modulo11.calculate_dv(cuerpo, basemax=11)
        self.assertTrue(modulo11.validate_ruc(f"{cuerpo}{dv}"))

    def test_validate_ruc_invalid_dv(self):
        # Si forzamos un DV distinto, debe fallar.
        cuerpo = "80069563"
        wrong_dv = (modulo11.calculate_dv(cuerpo, basemax=11) + 1) % 10
        self.assertFalse(modulo11.validate_ruc(f"{cuerpo}-{wrong_dv}"))

    def test_validate_ruc_remainder_one_body(self):
        """Cuerpo con resto 1: DV correcto es 0, no 1 (fix 18.0.1.1.1)."""
        self.assertTrue(modulo11.validate_ruc("80000003-0"))
        self.assertFalse(modulo11.validate_ruc("80000003-1"))

    def test_validate_ruc_garbage(self):
        self.assertFalse(modulo11.validate_ruc(""))
        self.assertFalse(modulo11.validate_ruc(None))
        self.assertFalse(modulo11.validate_ruc("abc"))

    # ------------------------------------------------------------------
    # is_valid_cedula
    # ------------------------------------------------------------------
    def test_is_valid_cedula_ok(self):
        self.assertTrue(modulo11.is_valid_cedula("1234567"))
        self.assertTrue(modulo11.is_valid_cedula("1"))
        self.assertTrue(modulo11.is_valid_cedula("123456789"))

    def test_is_valid_cedula_invalid(self):
        self.assertFalse(modulo11.is_valid_cedula(""))
        self.assertFalse(modulo11.is_valid_cedula(None))
        self.assertFalse(modulo11.is_valid_cedula("12345678a"))
        # Demasiado larga (>9 dígitos)
        self.assertFalse(modulo11.is_valid_cedula("1234567890"))
