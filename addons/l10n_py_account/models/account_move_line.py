# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Proporción de IVA gravada (SIFEN para 'gravado parcial')."""
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_py_iva_proporcion = fields.Integer(
        string="Proporción IVA (%)",
        default=100,
        help="Porcentaje (1-100) de la base gravada por IVA. < 100 indica "
        "afectación 'Gravado parcial' SIFEN. Usado por XML builder en Fase 2.",
    )
