# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Guard: cuentas RG 49/14 obligatorias para mapeo Hechauka."""
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase

HECHAUKA_REQUIRED_LEAF_ACCOUNTS = [
    # Disponibilidades
    "1010101", "1010102", "1010104",
    # Créditos
    "1010301",                       # Deudores por ventas
    "101030502",                     # Retenciones de IVA (9 dígitos en RG 49/14)
    "101030503",                     # IVA Crédito Fiscal (9 dígitos)
    # Mercaderías
    "101040101", "101040102", "101040103",
    # Pasivo
    "2010101",                       # Proveedores locales
    "201030102",                     # IVA a Pagar
    "201030103",                     # Retenciones a ingresar
    # Patrimonio
    "3010101",                       # Capital integrado
]
HECHAUKA_REQUIRED_GROUPS = [
    "401",   # Ventas mercaderías (grupo, no leaf en RG 49/14)
    "501",   # Costo mercaderías (grupo)
    "19",    # Impuesto a la Renta (grupo top-level)
    "20",    # Resultado neto del ejercicio (grupo)
]


@tagged("post_install", "-at_install", "l10n_py")
class TestHechaukaCriticalAccounts(L10nPyAccountTestCase):

    def test_all_required_leaf_accounts_present(self):
        for code in HECHAUKA_REQUIRED_LEAF_ACCOUNTS:
            account = self.env["account.account"].search([
                ("code", "=", code),
                ("company_ids", "in", self.company.id),
            ])
            self.assertTrue(
                account,
                f"Cuenta {code} requerida por Hechauka RG 49/14 está ausente del PUC",
            )

    def test_all_required_groups_present(self):
        for code in HECHAUKA_REQUIRED_GROUPS:
            group = self.env["account.group"].search([
                ("code_prefix_start", "=", code),
            ])
            self.assertTrue(
                group,
                f"Grupo de cuentas {code} requerido por Hechauka RG 49/14 está ausente",
            )
