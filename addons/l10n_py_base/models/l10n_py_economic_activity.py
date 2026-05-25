# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo SIFEN de actividades económicas.

Vacío por default; se llenará vía WS SET en Fase 2 (l10n_py_edi). En Fase 1b
se permite carga manual desde la UI.
"""
from odoo import fields, models


class L10nPyEconomicActivity(models.Model):
    _name = "l10n_py.economic_activity"
    _description = "Paraguay - Actividad Económica DNIT"
    _order = "code"

    code = fields.Char(required=True, help="Código de la actividad económica DNIT (ej: 1254)")
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "El código de actividad económica debe ser único"),
    ]
