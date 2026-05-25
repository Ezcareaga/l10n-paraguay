# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestChartTemplate(L10nPyAccountTestCase):

    def test_chart_loaded(self):
        accounts = self.env["account.account"].search([
            ("company_id", "=", self.company.id),
        ])
        self.assertGreater(len(accounts), 50, "PUC debe tener > 50 cuentas cargadas")

    def test_subset_active_around_80(self):
        active = self.env["account.account"].search([
            ("company_id", "=", self.company.id),
            ("active", "=", True),
        ])
        self.assertGreaterEqual(len(active), 60)
        self.assertLessEqual(len(active), 100)

    def test_account_groups_loaded(self):
        groups = self.env["account.group"].search([
            ("company_id", "=", self.company.id),
        ])
        self.assertGreater(len(groups), 30, "Debe haber grupos jerárquicos")

    def test_iva_taxes_loaded(self):
        taxes = self.env["account.tax"].search([
            ("company_id", "=", self.company.id),
            ("tax_group_id.name", "=", "IVA Paraguay"),
        ])
        self.assertEqual(len(taxes), 6, "Deben existir 6 taxes IVA")

    def test_default_sale_tax_is_iva_10(self):
        self.assertEqual(self.company.account_sale_tax_id.amount, 10.0)

    def test_default_purchase_tax_is_iva_10(self):
        self.assertEqual(self.company.account_purchase_tax_id.amount, 10.0)

    def test_sale_journal_use_documents_active(self):
        self.assertTrue(self.sale_journal.l10n_latam_use_documents)

    def test_company_localization_uses_documents(self):
        self.assertTrue(self.company._localization_use_documents())
