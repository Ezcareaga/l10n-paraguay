# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Fixture compartido para tests con chart 'py' cargado."""
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class L10nPyAccountTestCase(AccountTestInvoicingCommon):
    """Fixture: company PY + chart 'py' + timbrado active + PoE + sale journal con PoE."""

    @classmethod
    @AccountTestInvoicingCommon.setup_chart_template("py")
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.company_data["company"]
        cls.country_py = cls.env.ref("base.py")
        # setup_chart_template setea account_fiscal_country_id via @template;
        # acá fijamos country_id (residencia) para que matchee.
        cls.company.country_id = cls.country_py
        cls.timbrado = cls.env["l10n_py.timbrado"].create(
            {
                "name": "12345678",
                "date_from": "2026-01-01",
                "state": "active",
                "company_id": cls.company.id,
            }
        )
        cls.poe = cls.env["l10n_py.point_of_emission"].create(
            {
                "establishment_code": "001",
                "code": "001",
                "address_id": cls.company.partner_id.id,
                "company_id": cls.company.id,
            }
        )
        cls.sale_journal = cls.env["account.journal"].search(
            [
                ("type", "=", "sale"),
                ("company_id", "=", cls.company.id),
            ],
            limit=1,
        )
        # Asignar PoE antes de activar use_documents (que ya viene True por chart)
        cls.sale_journal.l10n_py_point_of_emission_id = cls.poe
        # RUC y tipo de contribuyente mínimos para que _l10n_py_edi_assign_cdc()
        # no levante UserError cuando l10n_py_edi está instalado y se postea
        # cualquier documento de venta SIFEN (FE/NC/ND).
        partner = cls.company.partner_id
        partner.l10n_latam_identification_type_id = cls.env.ref(
            "l10n_py_base.id_type_py_ruc"
        )
        partner.vat = "80069563-1"
        cls.company.l10n_py_taxpayer_type_id = cls.env.ref(
            "l10n_py_base.taxpayer_type_2"
        )
