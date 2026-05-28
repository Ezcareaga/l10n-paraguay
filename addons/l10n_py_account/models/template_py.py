# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Chart template loader para Paraguay (Odoo 18 API moderna)."""
from odoo import models

from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("py")
    def _get_py_template_data(self):
        return {
            "property_account_receivable_id": "py_1010301",  # Deudores por Ventas
            "property_account_payable_id": "py_2010101",  # Proveedores Locales
            # py_4010101 y py_5010101 no existen en el PUC generado por extract_puc_rg49.py
            # (el script solo activa códigos nivel-3 bajo 4.01/5.01).
            # Se usan los códigos nivel-4 disponibles más cercanos.
            # Revisar en Task 17 si se requiere ajustar ACTIVE_CODES del script.
            # py_4100103 = Ventas A Clientes Locales
            "property_account_income_categ_id": "py_4100103",
            # py_5100103 = Costo De Ventas A Clientes Locales
            "property_account_expense_categ_id": "py_5100103",
            "bank_account_code_prefix": "1010104",
            "cash_account_code_prefix": "1010102",
            "transfer_account_code_prefix": "1010103",
            # code_digits NO se setea: PUC RG 49/14 tiene códigos de longitud
            # variable (2-11 dígitos). Padding uniforme distorsiona los códigos
            # canónicos DNIT y rompe búsquedas por código exacto.
        }

    @template("py", "res.company")
    def _get_py_res_company(self):
        return {
            self.env.company.id: {
                "account_fiscal_country_id": "base.py",
                "account_sale_tax_id": "tax_iva_venta_10",
                "account_purchase_tax_id": "tax_iva_compra_10",
            },
        }

    @template("py", "account.journal")
    def _get_py_account_journal(self):
        return {
            "sale": {"name": "001-001 Facturación"},
        }
