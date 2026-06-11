# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del loader PKCS#12 — Python puro, no requiere Odoo registry."""
import datetime

from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_edi.services import certificate
from odoo.addons.l10n_py_edi.tests import fixtures


@tagged("standard", "l10n_py")
class TestCertificate(BaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password = "test-password"
        cls.p12 = fixtures.make_test_p12(password=cls.password)

    def test_load_pkcs12_ok(self):
        info = certificate.load_pkcs12(self.p12, self.password)
        self.assertIsNotNone(info.certificate)
        self.assertIsNotNone(info.private_key)
        self.assertEqual(info.ruc, "80069563-1")
        self.assertLess(info.not_valid_before, info.not_valid_after)

    def test_load_pkcs12_wrong_password(self):
        with self.assertRaises(certificate.CertificateLoadError):
            certificate.load_pkcs12(self.p12, "wrong")

    def test_load_pkcs12_garbage(self):
        with self.assertRaises(certificate.CertificateLoadError):
            certificate.load_pkcs12(b"garbage-not-a-p12", self.password)

    def test_extract_ruc_without_hyphen(self):
        """serialNumber RUC800695631 (sin guión) → RUC canónico '80069563-1'."""
        p12_no_hyphen = fixtures.make_test_p12(password=self.password, ruc="800695631")
        info = certificate.load_pkcs12(p12_no_hyphen, self.password)
        self.assertEqual(info.ruc, "80069563-1")

    def test_ruc_missing_serial_number(self):
        p12 = fixtures.make_test_p12(password=self.password, serial_number_attr=False)
        info = certificate.load_pkcs12(p12, self.password)
        self.assertIsNone(info.ruc)

    def test_check_validity_ok(self):
        info = certificate.load_pkcs12(self.p12, self.password)
        # No debe lanzar:
        certificate.check_validity(info)
        self.assertTrue(certificate.is_valid(info))

    def test_check_validity_expired(self):
        p12 = fixtures.make_expired_p12(password=self.password)
        info = certificate.load_pkcs12(p12, self.password)
        with self.assertRaises(certificate.CertificateExpiredError):
            certificate.check_validity(info)
        self.assertFalse(certificate.is_valid(info))

    def test_check_validity_not_yet_valid(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        p12 = fixtures.make_test_p12(
            password=self.password,
            not_before=now + datetime.timedelta(days=10),
            not_after=now + datetime.timedelta(days=375),
        )
        info = certificate.load_pkcs12(p12, self.password)
        with self.assertRaises(certificate.CertificateNotYetValidError):
            certificate.check_validity(info)

    def test_check_validity_at_explicit_date(self):
        info = certificate.load_pkcs12(self.p12, self.password)
        future = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            days=400
        )
        with self.assertRaises(certificate.CertificateExpiredError):
            certificate.check_validity(info, at=future)
