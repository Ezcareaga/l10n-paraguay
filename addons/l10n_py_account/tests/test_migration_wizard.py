# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestMigrationWizard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.company = cls.env["res.company"].create({
            "name": "Co PY", "country_id": cls.country_py.id,
        })

    def test_wizard_coexist_mode_works(self):
        w = self.env["l10n.py.account.migration.wizard"].create({
            "company_id": self.company.id, "mode": "coexist",
        })
        result = w.action_apply()
        self.assertEqual(result["type"], "ir.actions.client")

    def test_wizard_clean_mode_requires_confirm(self):
        w = self.env["l10n.py.account.migration.wizard"].create({
            "company_id": self.company.id, "mode": "clean",
            "confirm_destructive": False,
        })
        with self.assertRaises(UserError):
            w.action_apply()

    def test_existing_accounts_count(self):
        w = self.env["l10n.py.account.migration.wizard"].create({
            "company_id": self.company.id, "mode": "coexist",
        })
        # Cero accounts en company nueva sin chart cargado
        self.assertEqual(w.existing_accounts_count, 0)
