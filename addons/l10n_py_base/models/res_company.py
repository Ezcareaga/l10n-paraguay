# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión de res.company para identidad fiscal paraguaya."""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from . import modulo11


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_py_taxpayer_type_id = fields.Many2one(
        comodel_name="l10n_py.taxpayer.type",
        string="Tipo de Contribuyente",
        help="Persona Física o Jurídica (D205 iTiContRec).",
    )
    l10n_py_regime_id = fields.Many2one(
        comodel_name="l10n_py.regime",
        string="Régimen Tributario",
        help="Régimen tributario DNIT (D104 cTipReg).",
    )
    l10n_py_economic_activity_ids = fields.Many2many(
        comodel_name="l10n_py.economic_activity",
        string="Actividades Económicas",
        help="Una empresa puede tener múltiples actividades. Una se marca como principal en el XML del DE.",
    )
    l10n_py_nombre_fantasia = fields.Char(
        string="Nombre de Fantasía",
        help="Nombre comercial alternativo (campo D102 dNomFanEmi en SIFEN).",
    )
    l10n_py_dv = fields.Char(
        string="DV RUC",
        size=1,
        compute="_compute_l10n_py_dv",
        store=True,
        help="Dígito verificador del RUC (último dígito).",
    )

    @api.depends("vat", "country_id")
    def _compute_l10n_py_dv(self):
        for company in self:
            if company.country_id and company.country_id.code == "PY" and company.vat:
                _cuerpo, dv = modulo11.split_ruc(company.vat)
                company.l10n_py_dv = str(dv) if dv is not None else False
            else:
                company.l10n_py_dv = False

    @api.constrains("vat", "country_id")
    def _check_l10n_py_company_ruc(self):
        """Valida RUC paraguayo de la company (módulo 11)."""
        for company in self:
            if not (company.country_id and company.country_id.code == "PY"):
                continue
            if not company.vat:
                # RUC opcional al crear company nueva; se exigirá al postear DE en Fase 2
                continue
            if not modulo11.validate_ruc(company.vat):
                raise ValidationError(
                    _(
                        "El RUC %(vat)s de la empresa %(name)s no es válido "
                        "(DV módulo 11 incorrecto o formato inválido).",
                        vat=company.vat,
                        name=company.name,
                    )
                )
