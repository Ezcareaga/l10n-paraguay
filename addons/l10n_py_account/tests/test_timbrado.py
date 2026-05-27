# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del modelo l10n_py.timbrado."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestTimbrado(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _make_timbrado(self, **kwargs):
        defaults = {
            "name": "12345678",
            "date_from": "2026-01-01",
            "state": "draft",
            "company_id": self.company.id,
        }
        defaults.update(kwargs)
        return self.env["l10n_py.timbrado"].create(defaults)

    def test_create_timbrado_ok(self):
        t = self._make_timbrado()
        self.assertEqual(t.name, "12345678")
        self.assertEqual(t.state, "draft")

    def test_timbrado_name_must_be_8_digits(self):
        with self.assertRaises(ValidationError):
            self._make_timbrado(name="123")

    def test_timbrado_name_must_be_numeric(self):
        with self.assertRaises(ValidationError):
            self._make_timbrado(name="abcd1234")

    def test_only_one_active_timbrado_per_company(self):
        self._make_timbrado(name="11111111", state="active")
        with self.assertRaises(ValidationError):
            self._make_timbrado(name="22222222", state="active")

    def test_two_drafts_allowed(self):
        self._make_timbrado(name="11111111", state="draft")
        # No raise
        self._make_timbrado(name="22222222", state="draft")

    def test_date_to_is_optional(self):
        t = self._make_timbrado(date_to=False)
        self.assertFalse(t.date_to)

    def test_unique_name_per_company(self):
        self._make_timbrado(name="11111111")
        with self.assertRaises(Exception):  # IntegrityError envuelto
            self._make_timbrado(name="11111111")

    def test_transition_draft_to_active(self):
        t = self._make_timbrado(state="draft")
        t.state = "active"
        self.assertEqual(t.state, "active")
