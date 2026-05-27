# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestDocumentTypes(L10nPyAccountTestCase):
    def _dt(self, xmlid):
        return self.env.ref(f"l10n_py_account.{xmlid}")

    def test_five_doc_types_loaded(self):
        types = self.env["l10n_latam.document.type"].search(
            [
                ("country_id", "=", self.country_py.id),
            ]
        )
        self.assertEqual(len(types), 5)

    def test_codes_are_single_digit(self):
        for xmlid, expected in [
            ("dt_fe", "1"),
            ("dt_af", "4"),
            ("dt_nc", "5"),
            ("dt_nd", "6"),
            ("dt_nr", "7"),
        ]:
            self.assertEqual(self._dt(xmlid).code, expected)

    def test_internal_types(self):
        self.assertEqual(self._dt("dt_fe").internal_type, "invoice")
        self.assertEqual(self._dt("dt_af").internal_type, "invoice")
        self.assertEqual(self._dt("dt_nc").internal_type, "credit_note")
        self.assertEqual(self._dt("dt_nd").internal_type, "debit_note")
        self.assertFalse(self._dt("dt_nr").internal_type)  # NR vacío

    def test_format_normalizes_padding(self):
        dt = self._dt("dt_fe")
        self.assertEqual(dt._format_document_number("1-1-123"), "001-001-0000123")

    def test_format_normalizes_already_padded(self):
        dt = self._dt("dt_fe")
        self.assertEqual(
            dt._format_document_number("001-001-0000123"), "001-001-0000123"
        )

    def test_format_rejects_invalid_segments(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("01-01")  # solo 2 segmentos

    def test_format_rejects_non_numeric(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("001-001-ABC")

    def test_format_rejects_too_many_digits(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("001-001-12345678")  # 8 dígitos > 7

    def test_format_rejects_too_many_est_digits(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("0001-001-0000001")  # est = 4 dígitos

    def test_format_empty_returns_empty(self):
        dt = self._dt("dt_fe")
        self.assertEqual(dt._format_document_number(""), "")
        self.assertFalse(dt._format_document_number(False))

    def test_format_non_py_passes_through(self):
        dt_ar = self.env.ref("l10n_ar.dc_a_f", raise_if_not_found=False)
        if dt_ar:
            # No raise para AR
            self.assertEqual(
                dt_ar._format_document_number("00001-00000001"), "00001-00000001"
            )

    def test_nr_excluded_from_invoice_domain(self):
        # NR no debe aparecer en filtros account porque internal_type=''
        invoice_types = self.env["l10n_latam.document.type"].search(
            [
                ("country_id", "=", self.country_py.id),
                ("internal_type", "in", ["invoice", "debit_note", "credit_note"]),
            ]
        )
        codes = invoice_types.mapped("code")
        self.assertNotIn("7", codes)
        self.assertIn("1", codes)
        self.assertIn("5", codes)
        self.assertIn("6", codes)
