# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestAccountMoveDefensive(L10nPyAccountTestCase):

    def _make_invoice(self):
        partner = self.env["res.partner"].create({
            "name": "Cliente", "country_id": self.country_py.id,
        })
        return self.env["account.move"].with_company(self.company).create({
            "move_type": "out_invoice",
            "partner_id": partner.id,
            "journal_id": self.sale_journal.id,
            "l10n_latam_document_type_id": self.env.ref("l10n_py_account.dt_fe").id,
            "invoice_line_ids": [(0, 0, {"name": "X", "quantity": 1, "price_unit": 100})],
        })

    def test_post_without_poe_raises_user_error(self):
        # Quitar PoE del journal
        self.sale_journal.l10n_latam_use_documents = False
        self.sale_journal.l10n_py_point_of_emission_id = False
        self.sale_journal.l10n_latam_use_documents = True
        invoice = self._make_invoice()
        with self.assertRaises(UserError) as ctx:
            invoice.action_post()
        self.assertIn("Punto de Emisión", str(ctx.exception))

    def test_post_with_poe_works(self):
        invoice = self._make_invoice()
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_starting_sequence_without_poe_raises(self):
        self.sale_journal.l10n_latam_use_documents = False
        self.sale_journal.l10n_py_point_of_emission_id = False
        self.sale_journal.l10n_latam_use_documents = True
        invoice = self._make_invoice()
        with self.assertRaises(UserError):
            invoice._get_starting_sequence()
