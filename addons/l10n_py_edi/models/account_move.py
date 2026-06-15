# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""CDC (Código de Control SIFEN) en account.move.

El CDC se genera al postear, después de que el core asigne el name definitivo
(``EEE-PPP-NNNNNNN``) y el invoice_date. Regla de reutilización (docs/02 §3):
el security code se genera una sola vez por documento; si al re-postear ningún
componente cambió, el CDC resultante es idéntico y no se toca.
"""
import re

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_py_base.models import modulo11

from ..services import cdc as cdc_service

# name paraguayo: establecimiento-punto-número (l10n_py_account
# _get_starting_sequence garantiza el formato EEE-PPP-NNNNNNN).
PY_DOCUMENT_NAME = re.compile(r"^(\d{3})-(\d{3})-(\d{7})$")
# Tipos de DE que emitimos desde account.move (FE / NC / ND). Autofactura (4)
# es purchase-side y Nota de Remisión (7) no nace de un asiento contable.
SIFEN_EDOC_CODES = ("1", "5", "6")


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_py_cdc = fields.Char(
        string="CDC",
        size=44,
        copy=False,
        readonly=True,
        index="btree_not_null",
        help="Código de Control SIFEN de 44 dígitos. Se genera al postear.",
    )
    l10n_py_security_code = fields.Char(
        string="Código de seguridad SIFEN",
        size=9,
        copy=False,
        readonly=True,
        help="Componente aleatorio del CDC (posiciones 35-43). Se genera una "
        "sola vez por documento para permitir reutilizar el CDC tras un "
        "rechazo que no altere sus componentes.",
    )
    l10n_py_emission_type = fields.Selection(
        selection=[("1", "Normal"), ("2", "Contingencia")],
        string="Tipo de emisión SIFEN",
        default="1",
        copy=False,
        help="Posición 34 del CDC. Contingencia solo cuando SIFEN está caído.",
    )

    _sql_constraints = [
        (
            "l10n_py_cdc_uniq",
            "unique(l10n_py_cdc)",
            "Ya existe un documento con ese CDC.",
        ),
    ]

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        for move in posted:
            if move._l10n_py_edi_is_sifen_document():
                move._l10n_py_edi_assign_cdc()
        return posted

    def _l10n_py_edi_is_sifen_document(self):
        """True si este move es un DE SIFEN que emitimos nosotros."""
        self.ensure_one()
        return (
            self.company_id.account_fiscal_country_id.code == "PY"
            and self.journal_id.type == "sale"
            and self.l10n_latam_use_documents
            and self.l10n_latam_document_type_id.code in SIFEN_EDOC_CODES
        )

    def _l10n_py_edi_cdc_components(self):
        """Componentes del CDC extraídos del move (sin security code).

        :raises UserError: configuración incompleta (RUC, tipo de
            contribuyente, PoE o name fuera de formato).
        """
        self.ensure_one()
        company = self.company_id
        ruc, ruc_dv = modulo11.split_ruc(company.partner_id.vat)
        if not ruc or not modulo11.validate_ruc(company.partner_id.vat):
            raise UserError(
                _(
                    "La compañía %(company)s no tiene un RUC válido configurado "
                    "en su contacto (campo NIF/RUC).",
                    company=company.display_name,
                )
            )
        taxpayer_type = company.l10n_py_taxpayer_type_id.code
        if not taxpayer_type:
            raise UserError(
                _(
                    "La compañía %(company)s no tiene Tipo de Contribuyente "
                    "(PF/PJ) configurado. Es necesario para el CDC.",
                    company=company.display_name,
                )
            )
        poe = self.journal_id.l10n_py_point_of_emission_id
        if not poe:
            raise UserError(
                _(
                    "El diario %(journal)s no tiene Punto de Emisión " "configurado.",
                    journal=self.journal_id.display_name,
                )
            )
        match = PY_DOCUMENT_NAME.match(self.name or "")
        if not match:
            raise UserError(
                _(
                    "El número %(name)s no tiene el formato paraguayo "
                    "EEE-PPP-NNNNNNN; no se puede componer el CDC.",
                    name=self.name or "?",
                )
            )
        return {
            "document_type": self.l10n_latam_document_type_id.code,
            "ruc": ruc,
            "ruc_dv": ruc_dv,
            "establishment": poe.establishment_code,
            "expedition_point": poe.code,
            "document_number": match.group(3),
            "taxpayer_type": taxpayer_type,
            # IMPORTANTE: esta fecha (posiciones 26-33 del CDC) debe ser
            # byte-idéntica al campo dFeEmiDE del XML del DE. Cuando se escriba
            # el XML builder (Fase 2), extraer un helper _l10n_py_edi_issue_date()
            # compartido para que CDC y XML no puedan divergir. Ver TD-008.
            "issue_date": self.invoice_date or self.date,
            "emission_type": self.l10n_py_emission_type or "1",
        }

    def _l10n_py_edi_assign_cdc(self):
        """Compone y persiste el CDC, reutilizando el security code si existe."""
        self.ensure_one()
        components = self._l10n_py_edi_cdc_components()
        security_code = (
            self.l10n_py_security_code or cdc_service.generate_security_code()
        )
        try:
            new_cdc = cdc_service.compose_cdc(security_code=security_code, **components)
        except cdc_service.CdcError as exc:
            raise UserError(
                _("No se pudo generar el CDC: %(reason)s", reason=exc)
            ) from exc
        if new_cdc != self.l10n_py_cdc:
            self.write(
                {
                    "l10n_py_cdc": new_cdc,
                    "l10n_py_security_code": security_code,
                }
            )
