# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Paraguay - Base",
    "version": "18.0.1.1.0",
    "category": "Accounting/Localizations",
    "license": "AGPL-3",
    "author": "Careaga Dev, Odoo Community Association (OCA)",
    "website": "https://github.com/Ezcareaga/l10n-paraguay",
    "summary": (
        "Catálogos canónicos DNIT/SIFEN y validaciones de identificación "
        "(CI, RUC) para la localización paraguaya."
    ),
    "depends": [
        "base",
        "contacts",
        "base_address_extended",
        "l10n_latam_base",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/l10n_py_regime_data.xml",
        "data/l10n_py_taxpayer_type_data.xml",
        "data/l10n_py_recipient_nature_data.xml",
        "data/l10n_latam_identification_type_data.xml",
        "data/res_country_state_data.xml",
        "data/l10n_py.district.csv",
        "data/res.city.csv",
        "data/l10n_py_economic_activity_demo.xml",
        "views/l10n_py_regime_views.xml",
        "views/l10n_py_taxpayer_type_views.xml",
        "views/l10n_py_recipient_nature_views.xml",
        "views/l10n_py_district_views.xml",
        "views/l10n_py_economic_activity_views.xml",
        "views/res_partner_views.xml",
        "views/menus.xml",
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "_post_init_hook",
}
