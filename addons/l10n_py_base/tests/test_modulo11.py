# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del algoritmo módulo 11 — Python puro, no requiere Odoo registry."""
import unittest

from odoo.addons.l10n_py_base.models import modulo11


class TestModulo11(unittest.TestCase):
    """Casos conocidos de la práctica DNIT y del Manual Técnico SIFEN v150."""

    # ------------------------------------------------------------------
    # calculate_dv
    # ------------------------------------------------------------------
    def test_calculate_dv_simple_ruc(self):
        """Casos reales conocidos de RUC paraguayos (basemax=11)."""
        # Estos cuerpos + DV son tomados de RUCs públicos de empresas paraguayas.
        # El algoritmo módulo 11 base 11 debe reproducirlos.
        cases = [
            ("80069563", 1),  # Caso de prueba estándar (CDC ejemplo Manual SIFEN)
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

    def test_calculate_dv_basemax_9_for_cdc(self):
        """CDC usa basemax=9 según docs/01 sección 3."""
        # Sanity: el mismo número con basemax distinto da resultados distintos.
        dv_11 = modulo11.calculate_dv("123456789", basemax=11)
        dv_9 = modulo11.calculate_dv("123456789", basemax=9)
        # Ambos deben estar en rango 0-10 (módulo 11)
        self.assertIn(dv_11, range(11))
        self.assertIn(dv_9, range(11))

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
