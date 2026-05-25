# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Wizard para migrar companies PY con chart preexistente."""
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class L10nPyAccountMigrationWizard(models.TransientModel):
    _name = "l10n.py.account.migration.wizard"
    _description = "Paraguay - Asistente Migración Chart"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda s: s.env.company,
    )
    mode = fields.Selection(
        [
            ("clean", "Instalación limpia (reemplazar chart existente)"),
            ("assisted", "Mapeo asistido (mantener cuentas; sugerir merges)"),
            ("coexist", "Coexistir (solo cargar taxes + document types + timbrado)"),
        ],
        required=True,
        default="coexist",
    )
    existing_accounts_count = fields.Integer(
        compute="_compute_existing_accounts_count",
    )
    confirm_destructive = fields.Boolean(
        string="Confirmo: entiendo que esta operación es destructiva",
    )

    def _compute_existing_accounts_count(self):
        for w in self:
            w.existing_accounts_count = self.env["account.account"].search_count([
                ("company_id", "=", w.company_id.id),
            ])

    def action_apply(self):
        self.ensure_one()
        if self.mode == "clean":
            if not self.confirm_destructive:
                raise UserError(_(
                    "Modo 'limpia' requiere confirmar la operación destructiva."
                ))
            self._apply_clean()
        elif self.mode == "assisted":
            self._apply_assisted()
        else:
            self._apply_coexist()
        return {"type": "ir.actions.client", "tag": "reload"}

    def _apply_clean(self):
        # Eliminar todas las cuentas y recargar chart 'py'
        existing = self.env["account.account"].search([
            ("company_id", "=", self.company_id.id),
        ])
        existing.unlink()
        self.env["account.chart.template"].try_loading(
            "py", company=self.company_id,
        )
        _logger.info("Chart 'py' cargado en modo clean para company %s", self.company_id.name)

    def _apply_assisted(self):
        # No destructivo: solo loguea y deja el chart como está; manda activity
        self.company_id.partner_id.message_post(body=_(
            "Modo asistido: chart existente preservado. Revisar manualmente el mapeo "
            "de cuentas IVA a códigos RG 49/14."
        ))

    def _apply_coexist(self):
        # Solo cargar taxes + document types (sin chart). Asumimos que ya existen
        # como data del módulo cargados al instalar.
        pass
