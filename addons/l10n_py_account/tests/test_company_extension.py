# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la extensión account-level de res.company."""
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestCompanyExtension(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.company = cls.env["res.company"].create(
            {
                "name": "Test Co PY",
                "country_id": cls.country_py.id,
                "account_fiscal_country_id": cls.country_py.id,
            }
        )

    def test_localization_use_documents_true_for_py(self):
        self.assertTrue(self.company._localization_use_documents())

    def test_localization_use_documents_false_for_non_py(self):
        country_ar = self.env.ref("base.ar")
        company_ar = self.env["res.company"].create(
            {
                "name": "Test Co AR",
                "country_id": country_ar.id,
                "account_fiscal_country_id": country_ar.id,
            }
        )
        self.assertFalse(company_ar._localization_use_documents())

    def test_active_timbrado_returns_active_one(self):
        self.env["l10n_py.timbrado"].create(
            {
                "name": "11111111",
                "date_from": "2026-01-01",
                "state": "draft",
                "company_id": self.company.id,
            }
        )
        active = self.env["l10n_py.timbrado"].create(
            {
                "name": "22222222",
                "date_from": "2026-01-01",
                "state": "active",
                "company_id": self.company.id,
            }
        )
        self.assertEqual(self.company.l10n_py_active_timbrado_id, active)

    def test_active_timbrado_empty_when_none(self):
        self.assertFalse(self.company.l10n_py_active_timbrado_id)
