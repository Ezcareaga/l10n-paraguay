# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión account.journal — Punto de Emisión obligatorio en sale journals PY."""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_py_point_of_emission_id = fields.Many2one(
        "l10n_py.point_of_emission",
        string="Punto de Emisión",
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )
    l10n_py_require_emission = fields.Boolean(
        compute="_compute_l10n_py_require_emission",
        help="True si el journal debe tener PoE (sale + PY + use_documents).",
    )

    @api.depends("type", "country_code", "l10n_latam_use_documents")
    def _compute_l10n_py_require_emission(self):
        for journal in self:
            journal.l10n_py_require_emission = (
                journal.type == "sale"
                and journal.country_code == "PY"
                and journal.l10n_latam_use_documents
            )

    @api.constrains(
        "l10n_py_point_of_emission_id",
        "type",
        "country_code",
        "l10n_latam_use_documents",
    )
    def _check_py_point_of_emission(self):
        for j in self.filtered(lambda x: x.l10n_py_require_emission):
            if not j.l10n_py_point_of_emission_id:
                raise ValidationError(
                    _("Los diarios de ventas paraguayos con documentos requieren un Punto de Emisión.")
                )

    @api.constrains("l10n_py_point_of_emission_id", "l10n_latam_use_documents")
    def _check_py_poe_requires_use_documents(self):
        for j in self.filtered(lambda x: x.l10n_py_point_of_emission_id):
            if not j.l10n_latam_use_documents:
                raise ValidationError(
                    _('Un diario con Punto de Emisión PY debe tener "Usar Documentos" habilitado.')
                )
