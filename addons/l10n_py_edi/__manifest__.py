# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Paraguay - EDI SIFEN",
    "version": "18.0.1.1.0",
    "category": "Accounting/Localizations/EDI",
    "license": "AGPL-3",
    "author": "Careaga Dev, Odoo Community Association (OCA)",
    "website": "https://github.com/Ezcareaga/l10n-paraguay",
    "countries": ["py"],
    "summary": (
        "Facturación electrónica SIFEN/e-Kuatia: CDC, XML firmado XAdES, "
        "envío a DNIT, KuDE y eventos."
    ),
    "depends": [
        "l10n_py_account",
        "account_edi",
    ],
    "external_dependencies": {
        "python": [
            "lxml",
            "cryptography",
            "signxml",
            "zeep",
            "qrcode",
            "requests_pkcs12",
        ],
    },
    "data": [
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
