# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Timbrado DNIT — autorización para emitir DTE.

MT v150 C001-C010: número de 8 dígitos, fecha inicio vigencia obligatoria,
fecha fin opcional ("el timbrado no manejará una fecha de fin de vigencia" — p.60).
Convención operacional DNIT: un timbrado vigente por contribuyente a la vez.
"""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class L10nPyTimbrado(models.Model):
    _name = "l10n_py.timbrado"
    _description = "Paraguay - Timbrado DNIT"
    _order = "date_from desc, name"

    name = fields.Char(
        string="Número",
        required=True,
        size=8,
        help="8 dígitos otorgados por DNIT (MT v150 C004 dNumTim)",
    )
    date_from = fields.Date(
        string="Vigencia desde",
        required=True,
        help="MT v150 C008 dFeIniT",
    )
    date_to = fields.Date(
        string="Vigencia hasta",
        help="MT v150 C009 dFeFinT. Vacío = indefinido (DNIT moderno).",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda s: s.env.company,
    )
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("active", "Vigente"),
            ("expired", "Vencido"),
        ],
        default="draft",
        required=True,
    )

    _sql_constraints = [
        ("name_uniq", "unique(name, company_id)", "Timbrado único por empresa"),
    ]

    @api.constrains("state", "company_id")
    def _check_single_active(self):
        for rec in self.filtered(lambda r: r.state == "active"):
            others = self.search(
                [
                    ("company_id", "=", rec.company_id.id),
                    ("state", "=", "active"),
                    ("id", "!=", rec.id),
                ]
            )
            if others:
                raise ValidationError(
                    _("Solo puede haber un timbrado vigente por empresa.")
                )

    @api.constrains("name")
    def _check_name_format(self):
        for rec in self:
            if not (rec.name and rec.name.isdigit() and len(rec.name) == 8):
                raise ValidationError(
                    _("El timbrado debe ser exactamente 8 dígitos numéricos.")
                )
