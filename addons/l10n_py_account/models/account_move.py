# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""account.move PY: sequence per (journal, doc_type) + defensive PoE check."""
from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_starting_sequence(self):
        self.ensure_one()
        if (
            self.journal_id.country_code == "PY"
            and self.journal_id.l10n_latam_use_documents
        ):
            poe = self.journal_id.l10n_py_point_of_emission_id
            if not poe:
                raise UserError(
                    _(
                        "El diario '%(journal)s' usa documentos paraguayos pero no "
                        "tiene Punto de Emisión configurado. Configure el PoE en "
                        "Contabilidad → Configuración → Diarios antes de postear.",
                        journal=self.journal_id.name,
                    )
                )
            return f"{poe.establishment_code.zfill(3)}-{poe.code.zfill(3)}-0000000"
        return super()._get_starting_sequence()

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super()._get_last_sequence_domain(relaxed)
        if (
            self.company_id.account_fiscal_country_id.code == "PY"
            and self.l10n_latam_use_documents
        ):
            where_string += (
                " AND l10n_latam_document_type_id = %(l10n_latam_document_type_id)s"
            )
            param["l10n_latam_document_type_id"] = (
                self.l10n_latam_document_type_id.id or 0
            )
        return where_string, param

    def _post(self, soft=True):
        for move in self.filtered(
            lambda m: m.company_id.account_fiscal_country_id.code == "PY"
            and m.l10n_latam_use_documents
        ):
            if not move.journal_id.l10n_py_point_of_emission_id:
                raise UserError(
                    _(
                        "El diario '%(journal)s' no tiene Punto de Emisión configurado.",
                        journal=move.journal_id.name,
                    )
                )
        return super()._post(soft=soft)
