# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_py_account.hooks import _post_init_hook


@tagged("post_install", "-at_install", "l10n_py")
class TestPostInitHook(TransactionCase):

    def test_legacy_journal_without_poe_gets_disabled(self):
        country_py = self.env.ref("base.py")
        company = self.env["res.company"].create({
            "name": "Legacy PY", "country_id": country_py.id,
            "account_fiscal_country_id": country_py.id,
        })
        # Crear journal sale con use_documents=True pero sin PoE
        # (bypass constraint usando _write directo)
        journal = self.env["account.journal"].with_company(company).create({
            "name": "Sale Legacy", "type": "sale", "code": "VLG",
            "company_id": company.id, "l10n_latam_use_documents": False,
        })
        # Forzar use_documents=True via SQL bypass del constraint
        self.env.cr.execute(
            "UPDATE account_journal SET l10n_latam_use_documents = true WHERE id = %s",
            (journal.id,),
        )
        journal.invalidate_recordset()

        _post_init_hook(self.env)

        journal.invalidate_recordset()
        self.assertFalse(journal.l10n_latam_use_documents,
                          "Hook debe desactivar use_documents")

    def test_company_with_custom_chart_not_overwritten(self):
        country_py = self.env.ref("base.py")
        company = self.env["res.company"].create({
            "name": "Co Custom Chart", "country_id": country_py.id,
            "account_fiscal_country_id": country_py.id,
            "chart_template": "generic_coa",  # chart distinto a 'py'
        })
        # Crear algunas cuentas custom
        # Odoo 18: account.account usa company_ids (m2m), no company_id
        for code in ["1000", "2000", "3000"] * 8:  # >20 cuentas
            self.env["account.account"].create({
                "name": f"Cuenta {code}", "code": code,
                "account_type": "asset_current", "company_ids": [company.id],
            })
        accounts_before = self.env["account.account"].search_count([
            ("company_ids", "in", [company.id]),
        ])

        _post_init_hook(self.env)

        accounts_after = self.env["account.account"].search_count([
            ("company_ids", "in", [company.id]),
        ])
        self.assertEqual(accounts_before, accounts_after,
                          "Hook NO debe tocar cuentas existentes")
