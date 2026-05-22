# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de integración: validación CI/RUC en res.partner."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_py_base.models import modulo11


@tagged("post_install", "-at_install", "l10n_py")
class TestRucValidation(TransactionCase):
    """Verifica el constraint `_check_l10n_py_identification` en res.partner."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.id_type_ruc = cls.env.ref("l10n_py_base.id_type_py_ruc")
        cls.id_type_cedula = cls.env.ref("l10n_py_base.id_type_py_cedula_paraguaya")
        cls.id_type_pasaporte = cls.env.ref("l10n_py_base.id_type_py_pasaporte")

    def _make_partner(self, **vals):
        defaults = {"name": "Test PY Partner", "country_id": self.country_py.id}
        defaults.update(vals)
        return self.env["res.partner"].create(defaults)

    def test_valid_ruc_passes(self):
        cuerpo = "80069563"
        dv = modulo11.calculate_dv(cuerpo, basemax=11)
        partner = self._make_partner(
            l10n_latam_identification_type_id=self.id_type_ruc.id,
            vat=f"{cuerpo}-{dv}",
        )
        self.assertEqual(partner.l10n_py_dv, str(dv))

    def test_invalid_ruc_raises(self):
        cuerpo = "80069563"
        wrong_dv = (modulo11.calculate_dv(cuerpo, basemax=11) + 1) % 10
        with self.assertRaises(ValidationError):
            self._make_partner(
                l10n_latam_identification_type_id=self.id_type_ruc.id,
                vat=f"{cuerpo}-{wrong_dv}",
            )

    def test_valid_cedula_passes(self):
        partner = self._make_partner(
            l10n_latam_identification_type_id=self.id_type_cedula.id,
            vat="1234567",
        )
        self.assertTrue(partner.id)

    def test_cedula_with_letters_raises(self):
        with self.assertRaises(ValidationError):
            self._make_partner(
                l10n_latam_identification_type_id=self.id_type_cedula.id,
                vat="123ABC7",
            )

    def test_pasaporte_no_strict_validation(self):
        """Pasaporte no tiene validación de formato específica."""
        partner = self._make_partner(
            l10n_latam_identification_type_id=self.id_type_pasaporte.id,
            vat="AB-12345-XYZ",
        )
        self.assertTrue(partner.id)

    def test_non_py_partner_skips_validation(self):
        """Partner sin país=PY y sin tipo PY: validación no aplica."""
        country_us = self.env.ref("base.us")
        # Crea un tipo de identificación no-PY (usa el más típico de l10n_latam_base)
        partner = self.env["res.partner"].create(
            {
                "name": "Foreign Partner",
                "country_id": country_us.id,
                "vat": "invalidruc-fake",
            }
        )
        self.assertTrue(partner.id)

    def test_dv_computed_only_for_ruc(self):
        partner_cedula = self._make_partner(
            l10n_latam_identification_type_id=self.id_type_cedula.id,
            vat="1234567",
        )
        self.assertFalse(partner_cedula.l10n_py_dv)
