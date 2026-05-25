# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Punto de Emisión — establecimiento + punto de expedición SIFEN.

MT v150 C005 dEst (3 chars zero-padded) + C006 dPunExp (3 chars zero-padded).
"""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class L10nPyPointOfEmission(models.Model):
    _name = "l10n_py.point_of_emission"
    _description = "Paraguay - Punto de Emisión"
    _order = "establishment_code, code"

    name = fields.Char(compute="_compute_name", store=True)
    establishment_code = fields.Char(
        string="Establecimiento",
        required=True,
        help="MT v150 C005 dEst — 1-3 dígitos; se zero-pad a 3 en name",
    )
    code = fields.Char(
        string="Punto de Expedición",
        required=True,
        help="MT v150 C006 dPunExp — 1-3 dígitos; se zero-pad a 3 en name",
    )
    address_id = fields.Many2one(
        "res.partner",
        string="Dirección física",
        required=True,
        domain="['|', ('id', '=', company_partner_id), ('parent_id', '=', company_partner_id)]",
        help="Dirección física de la sucursal. Va al XML del DE.",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda s: s.env.company,
    )
    company_partner_id = fields.Many2one(related="company_id.partner_id")
    journal_ids = fields.One2many(
        "account.journal",
        "l10n_py_point_of_emission_id",
        string="Journals",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "estab_point_uniq",
            "unique(company_id, establishment_code, code)",
            "Ya existe un punto de emisión con ese establecimiento + punto en esta empresa",
        ),
    ]

    @api.depends("establishment_code", "code")
    def _compute_name(self):
        for rec in self:
            est = (rec.establishment_code or "").zfill(3)
            pt = (rec.code or "").zfill(3)
            rec.name = f"{est}-{pt}"

    @api.constrains("establishment_code", "code")
    def _check_codes_numeric(self):
        for rec in self:
            for val, fld in [
                (rec.establishment_code, "establecimiento"),
                (rec.code, "punto de expedición"),
            ]:
                if not (val and val.isdigit() and len(val) <= 3):
                    raise ValidationError(
                        _("Código de %s: 1-3 dígitos numéricos", fld)
                    )
