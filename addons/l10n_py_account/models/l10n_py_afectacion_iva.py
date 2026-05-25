# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo SIFEN TABLA 6 — Códigos de Afectación IVA (campo E731 iAfecIVA)."""
from odoo import fields, models


class L10nPyAfectacionIva(models.Model):
    _name = "l10n_py.afectacion_iva"
    _description = "Paraguay - Afectación IVA (SIFEN E731)"
    _order = "code"

    code = fields.Char(required=True, size=2)
    name = fields.Char(required=True, translate=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "El código de afectación IVA debe ser único"),
    ]
