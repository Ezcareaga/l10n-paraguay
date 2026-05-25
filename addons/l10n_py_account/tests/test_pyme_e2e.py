# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Smoke test: operación PyME completa (compra + venta + cuadre IVA)."""
from odoo import fields
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestPymeE2E(L10nPyAccountTestCase):

    def test_compra_venta_cierre_mes_cuadre_iva(self):
        """Ciclo: compra → venta → IVA Débito - IVA Crédito = IVA a Pagar."""
        partner_proveedor = self.env["res.partner"].create({
            "name": "Proveedor Local",
            "country_id": self.country_py.id,
            "supplier_rank": 1,
        })
        partner_cliente = self.env["res.partner"].create({
            "name": "Cliente Local",
            "country_id": self.country_py.id,
            "customer_rank": 1,
        })

        # 1. Compra: 100 Gs gravada IVA 10% → IVA Crédito = 10
        purchase_journal = self.env["account.journal"].search([
            ("type", "=", "purchase"), ("company_id", "=", self.company.id),
        ], limit=1)
        bill = self.env["account.move"].with_company(self.company).create({
            "move_type": "in_invoice",
            "partner_id": partner_proveedor.id,
            "journal_id": purchase_journal.id,
            "invoice_date": fields.Date.today(),
            "l10n_latam_document_type_id": self.env.ref(
                "l10n_py_account.dt_fe"
            ).id,
            "l10n_latam_document_number": "001-001-0000001",
            "invoice_line_ids": [(0, 0, {
                "name": "Compra mercadería",
                "quantity": 1,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [self.env.ref(
                    f"account.{self.company.id}_tax_iva_compra_10"
                ).id])],
            })],
        })
        bill.action_post()
        self.assertEqual(bill.amount_tax, 10.0)

        # 2. Venta: 200 Gs gravada IVA 10% → IVA Débito = 20
        invoice = self.env["account.move"].with_company(self.company).create({
            "move_type": "out_invoice",
            "partner_id": partner_cliente.id,
            "journal_id": self.sale_journal.id,
            "l10n_latam_document_type_id": self.env.ref(
                "l10n_py_account.dt_fe"
            ).id,
            "invoice_line_ids": [(0, 0, {
                "name": "Venta mercadería",
                "quantity": 1,
                "price_unit": 200.0,
                "tax_ids": [(6, 0, [self.env.ref(
                    f"account.{self.company.id}_tax_iva_venta_10"
                ).id])],
            })],
        })
        invoice.action_post()
        self.assertEqual(invoice.amount_tax, 20.0)

        # 3. Cuadre: IVA Débito (20) - IVA Crédito (10) = IVA a Pagar (10)
        # Odoo 18: account.account.company_ids (m2m) en vez de company_id
        iva_credito = self.env["account.account"].search([
            ("code", "=", "101030503"),
            ("company_ids", "in", self.company.id),
        ])
        iva_a_pagar = self.env["account.account"].search([
            ("code", "=", "201030102"),
            ("company_ids", "in", self.company.id),
        ])
        balance_credito = sum(
            self.env["account.move.line"].search([
                ("account_id", "=", iva_credito.id),
                ("parent_state", "=", "posted"),
            ]).mapped("balance")
        )
        balance_a_pagar = sum(
            self.env["account.move.line"].search([
                ("account_id", "=", iva_a_pagar.id),
                ("parent_state", "=", "posted"),
            ]).mapped("balance")
        )
        # IVA Crédito (activo): débito = +10
        self.assertEqual(balance_credito, 10.0)
        # IVA a Pagar (pasivo): crédito = -20 (convención Odoo)
        self.assertEqual(balance_a_pagar, -20.0)
        # IVA a Pagar neto del periodo = |-20| - 10 = 10
        self.assertEqual(abs(balance_a_pagar) - balance_credito, 10.0)
