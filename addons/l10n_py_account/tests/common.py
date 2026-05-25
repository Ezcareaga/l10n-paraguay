# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Fixture compartido para tests con chart 'py' cargado."""
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class L10nPyAccountTestCase(AccountTestInvoicingCommon):
    """Fixture: company PY + chart 'py' + timbrado active + PoE + sale journal con PoE."""

    @classmethod
    def setUpClass(cls, chart_template_ref="py"):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.company_data["company"]
        cls.country_py = cls.env.ref("base.py")
        cls.company.country_id = cls.country_py
        cls.company.account_fiscal_country_id = cls.country_py
        cls.timbrado = cls.env["l10n_py.timbrado"].create({
            "name": "12345678",
            "date_from": "2026-01-01",
            "state": "active",
            "company_id": cls.company.id,
        })
        cls.poe = cls.env["l10n_py.point_of_emission"].create({
            "establishment_code": "001",
            "code": "001",
            "address_id": cls.company.partner_id.id,
            "company_id": cls.company.id,
        })
        cls.sale_journal = cls.env["account.journal"].search([
            ("type", "=", "sale"), ("company_id", "=", cls.company.id),
        ], limit=1)
        # Asignar PoE antes de activar use_documents (que ya viene True por chart)
        cls.sale_journal.l10n_py_point_of_emission_id = cls.poe
