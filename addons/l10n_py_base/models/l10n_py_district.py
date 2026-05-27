# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo de distritos paraguayos (DNIT — Código de Referencia Geográfica)."""
from odoo import api, fields, models


class L10nPyDistrict(models.Model):
    _name = "l10n_py.district"
    _description = "Distrito paraguayo (DNIT)"
    _order = "state_id, code"

    code = fields.Char(
        string="Código SIFEN",
        required=True,
        size=4,
        help="Código de distrito según tabla DNIT (Manual Técnico SIFEN v150).",
    )
    name = fields.Char(string="Nombre", required=True, translate=False)
    state_id = fields.Many2one(
        comodel_name="res.country.state",
        string="Departamento",
        required=True,
        ondelete="restrict",
        domain="[('country_id.code', '=', 'PY')]",
        index=True,
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "l10n_py_district_code_uniq",
            "unique(code)",
            "El código del distrito debe ser único.",
        ),
    ]

    @api.depends("name", "code", "state_id")
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = (
                f"[{rec.code}] {rec.name} ({rec.state_id.name})"
                if rec.state_id
                else f"[{rec.code}] {rec.name}"
            )
