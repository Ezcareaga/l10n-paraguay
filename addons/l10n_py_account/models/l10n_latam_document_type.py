# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Override _format_document_number para Paraguay: EEE-PPP-NNNNNNN."""
from odoo import _, models
from odoo.exceptions import UserError


class L10nLatamDocumentType(models.Model):
    _inherit = "l10n_latam.document.type"

    def _format_document_number(self, document_number):
        if self.country_id.code != "PY":
            return super()._format_document_number(document_number)
        if not document_number:
            return document_number
        parts = document_number.split("-")
        if len(parts) != 3:
            raise UserError(_("Formato número PY: EEE-PPP-NNNNNNN (3-3-7 dígitos)"))
        est, poe, num = parts
        if not (est.isdigit() and poe.isdigit() and num.isdigit()):
            raise UserError(_("El número solo puede contener dígitos y guiones"))
        if len(est) > 3 or len(poe) > 3 or len(num) > 7:
            raise UserError(_("Máximo EEE=3, PPP=3, NNNNNNN=7 dígitos"))
        return f"{est:>03s}-{poe:>03s}-{num:>07s}"
