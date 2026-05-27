# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo de regímenes tributarios DNIT (Manual Técnico SIFEN v150, Tabla 1)."""
from odoo import fields, models


class L10nPyRegime(models.Model):
    _name = "l10n_py.regime"
    _description = "Régimen Tributario DNIT/SIFEN"
    _order = "code"

    code = fields.Char(
        string="Código SIFEN",
        required=True,
        size=2,
        help="Valor del campo D104 cTipReg (Manual Técnico SIFEN v150).",
    )
    name = fields.Char(string="Nombre", required=True, translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "l10n_py_regime_code_uniq",
            "unique(code)",
            "El código SIFEN del régimen debe ser único.",
        ),
    ]

    def name_get(self):
        return [(rec.id, f"[{rec.code}] {rec.name}") for rec in self]
