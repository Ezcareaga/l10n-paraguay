# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión account-level de res.company para Paraguay."""
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_py_timbrado_ids = fields.One2many(
        "l10n_py.timbrado",
        "company_id",
        string="Timbrados",
    )
    l10n_py_active_timbrado_id = fields.Many2one(
        "l10n_py.timbrado",
        string="Timbrado Vigente",
        compute="_compute_l10n_py_active_timbrado",
        help="Timbrado actualmente vigente (state=active)",
    )

    def _compute_l10n_py_active_timbrado(self):
        Timbrado = self.env["l10n_py.timbrado"]
        for company in self:
            company.l10n_py_active_timbrado_id = Timbrado.search([
                ("company_id", "=", company.id),
                ("state", "=", "active"),
            ], limit=1)

    def _localization_use_documents(self):
        self.ensure_one()
        return (
            self.account_fiscal_country_id.code == "PY"
            or super()._localization_use_documents()
        )
