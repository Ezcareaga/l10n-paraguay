# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Guard: cuentas RG 49/14 obligatorias para mapeo Hechauka."""
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase

# Códigos sin puntos (RG 49/14 Anexos.xls). Si alguno desaparece del PUC,
# Hechauka no se podrá declarar correctamente.
HECHAUKA_REQUIRED_CODES = [
    # Disponibilidades
    "1010101", "1010102", "1010104",
    # Créditos
    "1010301",                       # Deudores por ventas
    "10103050102",                   # Retenciones de IVA
    "10103050103",                   # IVA Crédito Fiscal
    # Mercaderías
    "101040101", "101040102", "101040103",
    # Pasivo
    "2010101",                       # Proveedores locales
    "201030102",                     # IVA a Pagar
    "201030103",                     # Retenciones a ingresar
    # Patrimonio
    "3010101",                       # Capital integrado
    # Ingresos
    "401",                           # Ventas mercaderías
    # Costos
    "501",                           # Costo mercaderías
    # Resultado
    "19",                            # Impuesto a la Renta
    "20",                            # Resultado neto del ejercicio
]


@tagged("post_install", "-at_install", "l10n_py")
class TestHechaukaCriticalAccounts(L10nPyAccountTestCase):

    def test_all_required_codes_present(self):
        for code in HECHAUKA_REQUIRED_CODES:
            account = self.env["account.account"].search([
                ("code", "=", code),
                ("company_id", "=", self.company.id),
            ])
            self.assertTrue(
                account,
                f"Cuenta {code} requerida por Hechauka RG 49/14 está ausente del PUC",
            )
