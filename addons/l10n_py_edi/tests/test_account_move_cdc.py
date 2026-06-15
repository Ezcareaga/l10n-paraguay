# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la asignación de CDC al postear documentos SIFEN."""
import datetime

import psycopg2.errors

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.l10n_py_account.tests.common import L10nPyAccountTestCase
from odoo.addons.l10n_py_edi.services import cdc as cdc_service


@tagged("post_install", "-at_install", "l10n_py")
class TestAccountMoveCdc(L10nPyAccountTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.company.partner_id
        partner.l10n_latam_identification_type_id = cls.env.ref(
            "l10n_py_base.id_type_py_ruc"
        )
        partner.vat = "80069563-1"
        cls.company.l10n_py_taxpayer_type_id = cls.env.ref(
            "l10n_py_base.taxpayer_type_2"
        )

    def _post_invoice(self, move_type="out_invoice", invoice_date=None):
        move = self.init_invoice(
            move_type,
            partner=self.partner_a,
            invoice_date=invoice_date or datetime.date(2026, 6, 11),
            products=self.product_a,
        )
        move.action_post()
        return move

    def test_cdc_assigned_on_post(self):
        move = self._post_invoice()
        self.assertTrue(move.l10n_py_cdc)
        self.assertEqual(len(move.l10n_py_cdc), 44)
        self.assertTrue(cdc_service.validate_cdc(move.l10n_py_cdc))
        parsed = cdc_service.parse_cdc(move.l10n_py_cdc)
        self.assertEqual(parsed["document_type"], "01")
        self.assertEqual(parsed["ruc"], "80069563")
        self.assertEqual(parsed["ruc_dv"], "1")
        self.assertEqual(parsed["establishment"], "001")
        self.assertEqual(parsed["expedition_point"], "001")
        self.assertEqual(parsed["taxpayer_type"], "2")
        self.assertEqual(parsed["issue_date"], move.invoice_date)
        self.assertEqual(parsed["emission_type"], "1")
        # El número del CDC sale del name EEE-PPP-NNNNNNN:
        self.assertEqual(parsed["document_number"], move.name.split("-")[2])
        # Security code persistido y consistente con el CDC:
        self.assertEqual(parsed["security_code"], move.l10n_py_security_code)

    def test_emission_type_default_normal(self):
        move = self._post_invoice()
        self.assertEqual(move.l10n_py_emission_type, "1")

    def test_credit_note_gets_doc_type_05(self):
        move = self._post_invoice("out_refund")
        parsed = cdc_service.parse_cdc(move.l10n_py_cdc)
        self.assertEqual(parsed["document_type"], "05")

    def test_cdc_reused_on_repost_without_changes(self):
        """Regla docs/02: corrección que no toca campos del CDC -> mismo CDC."""
        move = self._post_invoice()
        original_cdc = move.l10n_py_cdc
        original_code = move.l10n_py_security_code
        move.button_draft()
        move.action_post()
        self.assertEqual(move.l10n_py_cdc, original_cdc)
        self.assertEqual(move.l10n_py_security_code, original_code)

    def test_cdc_recomposed_when_component_changes(self):
        """Si cambia un componente (fecha), el CDC cambia pero el security
        code se conserva (la regla solo exige no regenerarlo)."""
        move = self._post_invoice(invoice_date=datetime.date(2026, 6, 1))
        original_cdc = move.l10n_py_cdc
        original_code = move.l10n_py_security_code
        move.button_draft()
        move.invoice_date = datetime.date(2026, 6, 10)
        move.action_post()
        self.assertNotEqual(move.l10n_py_cdc, original_cdc)
        self.assertEqual(move.l10n_py_security_code, original_code)
        parsed = cdc_service.parse_cdc(move.l10n_py_cdc)
        self.assertEqual(parsed["issue_date"], datetime.date(2026, 6, 10))

    def test_cdc_not_copied_on_duplicate(self):
        move = self._post_invoice()
        copy = move.copy()
        self.assertFalse(copy.l10n_py_cdc)
        self.assertFalse(copy.l10n_py_security_code)

    def test_cdc_unique_constraint(self):
        move = self._post_invoice()
        other = self.init_invoice(
            "out_invoice",
            partner=self.partner_a,
            invoice_date=datetime.date(2026, 6, 11),
            products=self.product_a,
        )

        def _write_dup():
            other.write({"l10n_py_cdc": move.l10n_py_cdc})
            self.env.cr.flush()

        with self.assertRaises(psycopg2.errors.UniqueViolation), mute_logger(
            "odoo.sql_db"
        ), self.env.cr.savepoint():
            _write_dup()

    def test_missing_taxpayer_type_raises(self):
        self.company.l10n_py_taxpayer_type_id = False
        with self.assertRaises(UserError):
            self._post_invoice()

    def test_invalid_company_ruc_raises(self):
        self.company.partner_id.vat = False
        with self.assertRaises(UserError):
            self._post_invoice()

    def test_no_cdc_for_purchase_documents(self):
        """Los documentos de compra (vendor bills) no generan CDC propio.

        Deviation: init_invoice("in_invoice") con l10n_latam_use_documents=True
        requiere l10n_latam_document_number antes de save() — el form view lo
        valida y lanza AssertionError en el test runner de Odoo.
        Se verifica el invariante directamente sobre un move creado vía ORM
        (sin form view) y sobre _l10n_py_edi_is_sifen_document().
        """
        purchase_journal = self.env["account.journal"].search(
            [("type", "=", "purchase"), ("company_id", "=", self.company.id)],
            limit=1,
        )
        # Verificación directa del invariante: purchase journal → no es DE SIFEN.
        # Creamos un move mínimo para poder llamar el método sin levantar un
        # invoice completo (evita la validación de l10n_latam_document_number).
        move = self.env["account.move"].new(
            {
                "move_type": "in_invoice",
                "journal_id": purchase_journal.id,
                "company_id": self.company.id,
            }
        )
        self.assertFalse(
            move._l10n_py_edi_is_sifen_document(),
            "Un in_invoice en journal de compra no debe ser un DE SIFEN.",
        )
