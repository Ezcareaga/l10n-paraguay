# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión de l10n_latam.identification.type para Paraguay.

Agrega los códigos SIFEN del campo D208 iTipIDRec (Manual Técnico v150) y un
flag booleano para identificar el tipo RUC (que no es parte de D208 — se maneja
por separado vía el campo D201 iNatRec).
"""
from odoo import fields, models


class L10nLatamIdentificationType(models.Model):
    _inherit = "l10n_latam.identification.type"

    l10n_py_sifen_code = fields.Char(
        string="Código SIFEN (D208)",
        size=2,
        help=(
            "Valor del campo D208 iTipIDRec del Manual Técnico SIFEN v150 "
            "(1=CI paraguaya, 2=Pasaporte, 3=CI extranjera, 4=Carnet de residencia, "
            "5=Innominado, 6=Tarjeta Diplomática, 9=Otro)."
        ),
    )
    l10n_py_is_ruc = fields.Boolean(
        string="Es RUC",
        default=False,
        help=(
            "Marca el tipo de identificación que representa el RUC paraguayo. "
            "Cuando True, el partner se valida vía algoritmo módulo 11."
        ),
    )
