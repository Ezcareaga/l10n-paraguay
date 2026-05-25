# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión account.tax con FK a afectación IVA SIFEN."""
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    l10n_py_afectacion_iva_id = fields.Many2one(
        "l10n_py.afectacion_iva",
        string="Afectación IVA (SIFEN E731)",
        help="Código SIFEN de afectación IVA usado en la línea del DE.",
    )
