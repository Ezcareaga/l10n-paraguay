# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión de res.partner para Paraguay: validación CI/RUC y campos SIFEN."""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from . import modulo11


class ResPartner(models.Model):
    _inherit = "res.partner"

    l10n_py_taxpayer_type_id = fields.Many2one(
        comodel_name="l10n_py.taxpayer.type",
        string="Tipo de Contribuyente",
        help="Persona Física o Jurídica (D205 iTiContRec). Solo aplica a partners PY.",
    )
    l10n_py_regime_id = fields.Many2one(
        comodel_name="l10n_py.regime",
        string="Régimen Tributario",
        help="Régimen tributario DNIT (D104 cTipReg). Solo aplica a partners PY.",
    )
    l10n_py_recipient_nature_id = fields.Many2one(
        comodel_name="l10n_py.recipient.nature",
        string="Naturaleza del Receptor",
        help="Contribuyente o No contribuyente (D201 iNatRec). Solo aplica a partners PY.",
    )
    l10n_py_district_id = fields.Many2one(
        comodel_name="l10n_py.district",
        string="Distrito",
        domain="[('state_id', '=?', state_id)]",
        help="Distrito DNIT del partner (relevante para SIFEN).",
    )
    l10n_py_dv = fields.Char(
        string="DV RUC",
        size=1,
        compute="_compute_l10n_py_dv",
        store=True,
        help="Dígito verificador del RUC (último dígito).",
    )

    @api.depends("vat", "l10n_latam_identification_type_id.l10n_py_is_ruc")
    def _compute_l10n_py_dv(self):
        for rec in self:
            if rec.l10n_latam_identification_type_id.l10n_py_is_ruc and rec.vat:
                _cuerpo, dv = modulo11.split_ruc(rec.vat)
                rec.l10n_py_dv = str(dv) if dv is not None else False
            else:
                rec.l10n_py_dv = False

    @api.constrains("vat", "l10n_latam_identification_type_id", "country_id")
    def _check_l10n_py_identification(self):
        """Valida CI y RUC paraguayos cuando aplica.

        Aplica si:
        - El tipo de identificación es PY (l10n_py_sifen_code o l10n_py_is_ruc), o
        - El country_id del partner es Paraguay.
        """
        for rec in self:
            id_type = rec.l10n_latam_identification_type_id
            is_py_partner = rec.country_id and rec.country_id.code == "PY"
            is_py_id_type = bool(id_type and (id_type.l10n_py_sifen_code or id_type.l10n_py_is_ruc))
            if not (is_py_partner or is_py_id_type):
                continue
            if not rec.vat:
                continue
            # RUC: validación módulo 11 obligatoria
            if id_type.l10n_py_is_ruc:
                if not modulo11.validate_ruc(rec.vat):
                    raise ValidationError(
                        _(
                            "El RUC %(vat)s del contacto %(name)s no es válido "
                            "(DV módulo 11 incorrecto o formato inválido).",
                            vat=rec.vat,
                            name=rec.display_name,
                        )
                    )
                continue
            # Cédula paraguaya: solo dígitos, 1-9 caracteres
            if id_type.l10n_py_sifen_code == "1":
                if not modulo11.is_valid_cedula(rec.vat):
                    raise ValidationError(
                        _(
                            "La Cédula paraguaya %(vat)s del contacto %(name)s "
                            "no es válida (solo dígitos, 1 a 9 caracteres).",
                            vat=rec.vat,
                            name=rec.display_name,
                        )
                    )
                continue
            # Cédula extranjera (código 3): solo formato no vacío
            if id_type.l10n_py_sifen_code == "3" and not rec.vat.strip():
                raise ValidationError(
                    _("La Cédula extranjera del contacto %s no puede estar vacía.", rec.display_name)
                )
