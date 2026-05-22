# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests que verifican que los catálogos SIFEN cargaron correctamente."""
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestDataLoaded(TransactionCase):

    def test_regimes_loaded(self):
        regimes = self.env["l10n_py.regime"].search([])
        self.assertEqual(len(regimes), 8, "Debe haber 8 regímenes (Tabla 1 SIFEN v150).")
        self.assertTrue(self.env.ref("l10n_py_base.regime_1").name)

    def test_taxpayer_types_loaded(self):
        taxpayer_types = self.env["l10n_py.taxpayer.type"].search([])
        self.assertEqual(len(taxpayer_types), 2, "Debe haber 2 tipos de contribuyente (PF + PJ).")

    def test_recipient_natures_loaded(self):
        natures = self.env["l10n_py.recipient.nature"].search([])
        self.assertEqual(len(natures), 2)

    def test_identification_types_loaded(self):
        py_id_types = self.env["l10n_latam.identification.type"].search(
            [("country_id.code", "=", "PY")]
        )
        # 1 RUC + 7 D208 (CI, Pasaporte, CI extranjera, Carnet, Innominado, Diplomática, Otro)
        self.assertEqual(len(py_id_types), 8)
        ruc_types = py_id_types.filtered("l10n_py_is_ruc")
        self.assertEqual(len(ruc_types), 1, "Solo un tipo marcado como RUC.")

    def test_departments_loaded(self):
        deps = self.env["res.country.state"].search(
            [("country_id.code", "=", "PY"), ("l10n_py_sifen_code", "!=", False)]
        )
        self.assertEqual(len(deps), 18, "Capital + 17 departamentos (SIFEN v150).")

    def test_districts_loaded(self):
        districts = self.env["l10n_py.district"].search([])
        self.assertGreater(len(districts), 250, "Debe haber ~270 distritos.")

    def test_cities_loaded(self):
        cities = self.env["res.city"].search(
            [("country_id.code", "=", "PY"), ("l10n_py_sifen_code", "!=", False)]
        )
        self.assertGreater(len(cities), 6000, "Debe haber ~6400 ciudades.")

    def test_district_has_state(self):
        """Cada distrito debe tener un departamento asignado."""
        districts_without_state = self.env["l10n_py.district"].search([("state_id", "=", False)])
        self.assertFalse(districts_without_state, "Todos los distritos deben tener departamento.")

    def test_city_has_district(self):
        cities_without_district = self.env["res.city"].search(
            [("country_id.code", "=", "PY"), ("l10n_py_sifen_code", "!=", False), ("l10n_py_district_id", "=", False)]
        )
        self.assertFalse(cities_without_district, "Todas las ciudades PY deben tener distrito.")

    def test_post_init_hook_sets_vat_label(self):
        country_py = self.env.ref("base.py")
        self.assertEqual(country_py.vat_label, "RUC")
