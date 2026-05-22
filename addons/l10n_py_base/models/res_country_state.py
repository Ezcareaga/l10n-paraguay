# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión de res.country.state para departamentos paraguayos."""
from odoo import fields, models


class ResCountryState(models.Model):
    _inherit = "res.country.state"

    l10n_py_sifen_code = fields.Char(
        string="Código SIFEN",
        size=2,
        help=(
            "Código del departamento según DNIT (Manual Técnico SIFEN v150). "
            "Solo aplica a departamentos paraguayos."
        ),
    )
