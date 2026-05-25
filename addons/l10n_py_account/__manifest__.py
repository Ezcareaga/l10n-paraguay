# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Paraguay - Accounting",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations/Account Charts",
    "license": "AGPL-3",
    "author": "Careaga Dev, Odoo Community Association (OCA)",
    "website": "https://github.com/Ezcareaga/l10n-paraguay",
    "countries": ["py"],
    "summary": (
        "Plan de cuentas RG 49/14, impuestos IVA, tipos de documento SIFEN, "
        "timbrado y punto de emisión para la localización paraguaya."
    ),
    "depends": [
        "l10n_py_base",
        "account",
        "l10n_latam_invoice_document",
    ],
    "auto_install": ["account"],
    "data": [
        "security/l10n_py_account_security.xml",
        "security/ir.model.access.csv",
        "data/l10n_py.afectacion_iva.csv",
        "data/l10n_latam.document.type.csv",
        "views/l10n_py_afectacion_iva_views.xml",
        "views/l10n_py_timbrado_views.xml",
        "views/l10n_py_point_of_emission_views.xml",
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "views/res_company_views.xml",
        "wizards/account_migration_wizard_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "_post_init_hook",
}
