# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo de tipos de contribuyente (D205 iTiContRec - Manual Técnico SIFEN v150)."""
from odoo import fields, models


class L10nPyTaxpayerType(models.Model):
    _name = "l10n_py.taxpayer.type"
    _description = "Tipo de Contribuyente DNIT/SIFEN"
    _order = "code"

    code = fields.Char(
        string="Código SIFEN",
        required=True,
        size=1,
        help="Valor del campo D205 iTiContRec (1=Persona Física, 2=Persona Jurídica).",
    )
    name = fields.Char(string="Nombre", required=True, translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "l10n_py_taxpayer_type_code_uniq",
            "unique(code)",
            "El código SIFEN del tipo de contribuyente debe ser único.",
        ),
    ]

    def name_get(self):
        return [(rec.id, f"[{rec.code}] {rec.name}") for rec in self]
