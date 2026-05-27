# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la extensión fiscal en res.company."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_py_base.models import modulo11


@tagged("post_install", "-at_install", "l10n_py")
class TestCompanySetup(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.taxpayer_pf = cls.env.ref("l10n_py_base.taxpayer_type_1")  # Persona Física
        cls.regime_general = cls.env.ref(
            "l10n_py_base.regime_8"
        )  # Turismo (any active)
        cls.activity_minimarket = cls.env.ref("l10n_py_base.economic_activity_1254")

    def _make_company(self, vat=None):
        cuerpo = "80069563"
        if vat is None:
            dv = modulo11.calculate_dv(cuerpo, basemax=11)
            vat = f"{cuerpo}-{dv}"
        return self.env["res.company"].create(
            {
                "name": "Test PY Co",
                "country_id": self.country_py.id,
                "vat": vat,
                "l10n_py_taxpayer_type_id": self.taxpayer_pf.id,
                "l10n_py_regime_id": self.regime_general.id,
                "l10n_py_economic_activity_ids": [
                    (6, 0, [self.activity_minimarket.id])
                ],
                "l10n_py_nombre_fantasia": "Almacén Don Pedro",
            }
        )

    def test_company_valid_ruc_computes_dv(self):
        company = self._make_company()
        cuerpo = "80069563"
        expected_dv = str(modulo11.calculate_dv(cuerpo, basemax=11))
        self.assertEqual(company.l10n_py_dv, expected_dv)

    def test_company_invalid_ruc_raises(self):
        cuerpo = "80069563"
        wrong_dv = (modulo11.calculate_dv(cuerpo, basemax=11) + 1) % 10
        with self.assertRaises(ValidationError):
            self._make_company(vat=f"{cuerpo}-{wrong_dv}")

    def test_company_non_py_country_skips_validation(self):
        # Usar Brasil: base_vat no tiene check_vat_br estricto y l10n_latam_base
        # no bloquea el create de res.company (solo res.partner).
        # El objetivo es verificar que l10n_py_dv no se calcula fuera de PY.
        country_br = self.env.ref("base.br")
        company = self.env["res.company"].create(
            {
                "name": "Test BR Co",
                "country_id": country_br.id,
                "vat": "12345678000195",  # CNPJ válido — no es PY, l10n_py_dv debe ser False
            }
        )
        self.assertFalse(company.l10n_py_dv)

    def test_company_empty_vat_is_allowed(self):
        # Permitir crear company sin RUC (se requerirá al postear DE en Fase 2)
        company = self.env["res.company"].create(
            {
                "name": "Test PY Co Sin RUC",
                "country_id": self.country_py.id,
            }
        )
        self.assertFalse(company.l10n_py_dv)
