# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión de res.city: vincula ciudades paraguayas con su distrito DNIT."""
from odoo import fields, models


class ResCity(models.Model):
    _inherit = "res.city"

    l10n_py_district_id = fields.Many2one(
        comodel_name="l10n_py.district",
        string="Distrito",
        ondelete="restrict",
        index=True,
        help="Distrito DNIT al que pertenece la ciudad (solo PY).",
    )
    l10n_py_sifen_code = fields.Char(
        string="Código SIFEN",
        size=5,
        help="Código de ciudad según DNIT (Manual Técnico SIFEN v150).",
    )
