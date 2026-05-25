# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la extensión account.journal para Paraguay."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestJournalExtension(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.company = cls.env["res.company"].create({
            "name": "Test Co PY", "country_id": cls.country_py.id,
            "account_fiscal_country_id": cls.country_py.id,
        })
        cls.poe = cls.env["l10n_py.point_of_emission"].create({
            "establishment_code": "001", "code": "001",
            "address_id": cls.company.partner_id.id,
            "company_id": cls.company.id,
        })

    def _make_journal(self, type_, **kwargs):
        defaults = {
            "name": f"Test {type_} journal",
            "type": type_,
            "code": "TST",
            "company_id": self.company.id,
        }
        defaults.update(kwargs)
        return self.env["account.journal"].with_company(self.company).create(defaults)

    def test_sale_journal_require_emission_true(self):
        journal = self._make_journal("sale", l10n_latam_use_documents=True,
                                      l10n_py_point_of_emission_id=self.poe.id)
        self.assertTrue(journal.l10n_py_require_emission)

    def test_purchase_journal_require_emission_false(self):
        journal = self._make_journal("purchase", l10n_latam_use_documents=True)
        self.assertFalse(journal.l10n_py_require_emission)

    def test_sale_journal_without_poe_raises(self):
        with self.assertRaises(ValidationError):
            self._make_journal("sale", l10n_latam_use_documents=True)

    def test_poe_without_use_documents_raises(self):
        with self.assertRaises(ValidationError):
            self._make_journal("sale", l10n_latam_use_documents=False,
                                l10n_py_point_of_emission_id=self.poe.id)

    def test_non_py_journal_no_constraint(self):
        country_ar = self.env.ref("base.ar")
        company_ar = self.env["res.company"].create({
            "name": "Co AR", "country_id": country_ar.id,
            "account_fiscal_country_id": country_ar.id,
        })
        # No raise: country != PY
        journal = self.env["account.journal"].with_company(company_ar).create({
            "name": "Sale AR", "type": "sale", "code": "VEN",
            "company_id": company_ar.id, "l10n_latam_use_documents": True,
        })
        self.assertFalse(journal.l10n_py_require_emission)

    def test_change_use_documents_off_keeps_poe_raises(self):
        journal = self._make_journal("sale", l10n_latam_use_documents=True,
                                      l10n_py_point_of_emission_id=self.poe.id)
        with self.assertRaises(ValidationError):
            journal.l10n_latam_use_documents = False

    def test_journal_country_code_is_py(self):
        journal = self._make_journal("sale", l10n_latam_use_documents=True,
                                      l10n_py_point_of_emission_id=self.poe.id)
        self.assertEqual(journal.country_code, "PY")
