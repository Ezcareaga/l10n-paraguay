# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestTaxes(L10nPyAccountTestCase):

    def _tax_by_xmlid(self, xmlid):
        return self.env.ref(f"account.{self.company.id}_{xmlid}")

    def test_iva_venta_10_cabled_to_iva_a_pagar(self):
        tax = self._tax_by_xmlid("tax_iva_venta_10")
        tax_lines = tax.invoice_repartition_line_ids.filtered(
            lambda r: r.repartition_type == "tax"
        )
        self.assertEqual(len(tax_lines), 1)
        self.assertEqual(tax_lines.account_id.code, "201030102")

    def test_iva_compra_10_cabled_to_iva_credito(self):
        tax = self._tax_by_xmlid("tax_iva_compra_10")
        tax_lines = tax.invoice_repartition_line_ids.filtered(
            lambda r: r.repartition_type == "tax"
        )
        self.assertEqual(len(tax_lines), 1)
        self.assertEqual(tax_lines.account_id.code, "101030503")

    def test_iva_venta_5_amount(self):
        tax = self._tax_by_xmlid("tax_iva_venta_5")
        self.assertEqual(tax.amount, 5.0)

    def test_iva_venta_exenta_amount_zero(self):
        tax = self._tax_by_xmlid("tax_iva_venta_exenta")
        self.assertEqual(tax.amount, 0.0)

    def test_iva_export_amount_zero_and_gravado(self):
        tax = self._tax_by_xmlid("tax_iva_venta_export")
        self.assertEqual(tax.amount, 0.0)
        # Export es gravado al 0%, no exento
        self.assertEqual(
            tax.l10n_py_afectacion_iva_id,
            self.env.ref("l10n_py_account.afectacion_iva_1"),
        )

    def test_afectacion_iva_fk_on_iva_taxes(self):
        for xmlid in ["tax_iva_venta_10", "tax_iva_venta_5", "tax_iva_compra_10",
                      "tax_iva_compra_5"]:
            tax = self._tax_by_xmlid(xmlid)
            self.assertEqual(
                tax.l10n_py_afectacion_iva_id.code, "1", f"{xmlid} debe ser Gravado",
            )

    def test_compute_amount_iva_10(self):
        tax = self._tax_by_xmlid("tax_iva_venta_10")
        result = tax.compute_all(price_unit=100.0)
        self.assertEqual(result["total_excluded"], 100.0)
        self.assertEqual(result["total_included"], 110.0)

    def test_compute_amount_iva_5(self):
        tax = self._tax_by_xmlid("tax_iva_venta_5")
        result = tax.compute_all(price_unit=100.0)
        self.assertEqual(result["total_included"], 105.0)

    def test_compute_amount_iva_exenta(self):
        tax = self._tax_by_xmlid("tax_iva_venta_exenta")
        result = tax.compute_all(price_unit=100.0)
        self.assertEqual(result["total_included"], 100.0)

    def test_taxes_have_correct_tax_group(self):
        for xmlid in ["tax_iva_venta_10", "tax_iva_venta_5", "tax_iva_venta_exenta",
                      "tax_iva_venta_export", "tax_iva_compra_10", "tax_iva_compra_5"]:
            tax = self._tax_by_xmlid(xmlid)
            self.assertEqual(tax.tax_group_id.name, "IVA Paraguay")
