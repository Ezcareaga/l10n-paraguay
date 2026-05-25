# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del modelo l10n_py.economic_activity."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestEconomicActivity(TransactionCase):

    def test_create_economic_activity(self):
        """Crear una actividad económica simple."""
        activity = self.env["l10n_py.economic_activity"].create({
            "code": "9999",
            "name": "Actividad económica de prueba",
        })
        self.assertEqual(activity.code, "9999")
        self.assertTrue(activity.active)

    def test_demo_records_loaded(self):
        """Los 2 records demo de actividades económicas deben estar cargados."""
        activities = self.env["l10n_py.economic_activity"].search([])
        self.assertGreaterEqual(len(activities), 2)
