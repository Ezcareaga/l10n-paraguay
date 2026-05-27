# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""account.move PY: sequence per (journal, doc_type) + defensive PoE check."""
from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.sql import drop_index


class AccountMove(models.Model):
    _inherit = "account.move"

    def _auto_init(self):
        # Reemplaza el índice único de l10n_latam_invoice_document para soportar
        # secuencias independientes por doc_type en ventas paraguayas.
        # Paraguay: el "name" (e.g. "001-001-0000001") puede repetirse en el mismo
        # journal entre diferentes doc_types (FE/NC/ND) — la unicidad real es por
        # (name, journal_id, l10n_latam_document_type_id).
        res = super()._auto_init()
        # Forzar recreación: drop si ya existe el viejo (sin doc_type), crear el nuevo.
        self.env.cr.execute(
            """SELECT indexdef FROM pg_indexes
               WHERE indexname = 'account_move_unique_name' AND tablename = 'account_move'"""
        )
        row = self.env.cr.fetchone()
        if (
            row
            and "l10n_latam_document_type_id"
            not in row[0].split("USING btree")[1].split("WHERE")[0]
        ):
            drop_index(self.env.cr, "account_move_unique_name", self._table)
            self.env.cr.execute(
                """
                CREATE UNIQUE INDEX account_move_unique_name
                                 ON account_move(name, journal_id, l10n_latam_document_type_id)
                              WHERE (state = 'posted' AND name != '/'
                                AND (l10n_latam_document_type_id IS NULL OR move_type NOT IN ('in_invoice', 'in_refund', 'in_receipt')));
                """
            )
        return res

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

    def _get_sequence_cache(self):
        """Scope sequence cache per doc_type para journals PY con use_documents.

        El core usa cache key `(format_string.format(seq=0), journal_id)`. En
        Paraguay, FE/NC/ND comparten el mismo format `EEE-PPP-{seq:07d}`, por lo
        que colisionan en la cache cuando se postean en la misma transacción.
        Aislamos el cache bucket por doc_type para que cada tipo de documento
        mantenga su propia secuencia.
        """
        cache = super()._get_sequence_cache()
        if (
            self.company_id.account_fiscal_country_id.code == "PY"
            and self.l10n_latam_use_documents
            and self.l10n_latam_document_type_id
        ):
            bucket_key = (
                "l10n_py_account.doc_type",
                self.l10n_latam_document_type_id.id,
            )
            return cache.setdefault(bucket_key, {})
        return cache

    def _post(self, soft=True):
        # PoE solo aplica a journals SALE (documentos que YO emito a clientes).
        # Para purchase/bill, el PoE viene del proveedor en su propio documento.
        for move in self.filtered(
            lambda m: m.company_id.account_fiscal_country_id.code == "PY"
            and m.l10n_latam_use_documents
            and m.journal_id.type == "sale"
        ):
            if not move.journal_id.l10n_py_point_of_emission_id:
                raise UserError(
                    _(
                        "El diario '%(journal)s' no tiene Punto de Emisión configurado.",
                        journal=move.journal_id.name,
                    )
                )
        return super()._post(soft=soft)
