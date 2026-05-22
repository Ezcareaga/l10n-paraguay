# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo de naturaleza del receptor (D201 iNatRec - Manual Técnico SIFEN v150)."""
from odoo import fields, models


class L10nPyRecipientNature(models.Model):
    _name = "l10n_py.recipient.nature"
    _description = "Naturaleza del Receptor DNIT/SIFEN"
    _order = "code"

    code = fields.Char(
        string="Código SIFEN",
        required=True,
        size=1,
        help="Valor del campo D201 iNatRec (1=Contribuyente, 2=No contribuyente).",
    )
    name = fields.Char(string="Nombre", required=True, translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("l10n_py_recipient_nature_code_uniq", "unique(code)", "El código SIFEN de la naturaleza del receptor debe ser único."),
    ]

    def name_get(self):
        return [(rec.id, f"[{rec.code}] {rec.name}") for rec in self]
