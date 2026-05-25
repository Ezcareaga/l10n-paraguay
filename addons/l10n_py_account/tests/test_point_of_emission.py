# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del modelo l10n_py.point_of_emission."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestPointOfEmission(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _make_poe(self, **kwargs):
        defaults = {
            "establishment_code": "001",
            "code": "001",
            "address_id": self.company.partner_id.id,
            "company_id": self.company.id,
        }
        defaults.update(kwargs)
        return self.env["l10n_py.point_of_emission"].create(defaults)

    def test_create_poe_ok(self):
        poe = self._make_poe()
        self.assertEqual(poe.name, "001-001")

    def test_unique_establishment_point_per_company(self):
        self._make_poe(establishment_code="001", code="001")
        with self.assertRaises(Exception):
            self._make_poe(establishment_code="001", code="001")

    def test_two_points_in_same_establishment_allowed(self):
        self._make_poe(establishment_code="001", code="001")
        # No raise
        self._make_poe(establishment_code="001", code="002")

    def test_codes_must_be_numeric(self):
        with self.assertRaises(ValidationError):
            self._make_poe(establishment_code="abc")

    def test_codes_max_3_digits(self):
        with self.assertRaises(ValidationError):
            self._make_poe(establishment_code="1234")

    def test_compute_name_pads_with_zeros(self):
        poe = self._make_poe(establishment_code="1", code="2")
        self.assertEqual(poe.name, "001-002")
