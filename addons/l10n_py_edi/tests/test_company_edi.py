# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de los campos EDI encriptados en res.company."""
import base64
import os
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.l10n_py_account.tests.common import L10nPyAccountTestCase
from odoo.addons.l10n_py_edi.services import certificate, crypto
from odoo.addons.l10n_py_edi.tests import fixtures
from odoo.addons.l10n_py_edi.tests.common import TEST_CSC as COMMON_TEST_CSC
from odoo.addons.l10n_py_edi.tests.common import L10nPyEdiTestCase

KEY_ENV = "L10N_PY_EDI_CCFE_KEY"


@tagged("post_install", "-at_install", "l10n_py")
class TestCompanyEdi(L10nPyAccountTestCase):
    @classmethod
    def _restore_key_env(cls):
        """Restaura (o elimina) la env var KEY_ENV al estado previo al test."""
        if cls._original_key_env is None:
            os.environ.pop(KEY_ENV, None)
        else:
            os.environ[KEY_ENV] = cls._original_key_env

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fernet_key = crypto.generate_data_key()
        # Odoo 18's check_attrs() iterates patchers and accesses .target, which
        # _patch_dict objects don't have. Set os.environ directly.
        cls._original_key_env = os.environ.get(KEY_ENV)
        os.environ[KEY_ENV] = cls.fernet_key.decode()
        # Register cleanup immediately after mutation so it runs even if the
        # rest of setUpClass raises (tearDownClass would be skipped in that case).
        cls.addClassCleanup(cls._restore_key_env)
        cls.password = "test-password"
        cls.p12 = fixtures.make_test_p12(password=cls.password)

    def _upload_cert(self, p12=None, password=None):
        self.company.write(
            {
                "l10n_py_ccfe_certificate": base64.b64encode(p12 or self.p12),
                "l10n_py_ccfe_password": password or self.password,
            }
        )

    def test_environment_default_test(self):
        self.assertEqual(self.company.l10n_py_edi_environment, "test")

    def test_upload_certificate_stores_encrypted(self):
        self._upload_cert()
        token = self.company.l10n_py_ccfe_certificate_token
        self.assertTrue(token)
        # El token NO es el p12 plano ni su base64:
        self.assertNotIn(base64.b64encode(self.p12).decode(), token)
        # Pero descifra al p12 original:
        self.assertEqual(
            crypto.decrypt_secret(token.encode(), self.fernet_key), self.p12
        )
        # Password también encriptada:
        self.assertEqual(
            crypto.decrypt_secret(
                self.company.l10n_py_ccfe_password_token.encode(),
                self.fernet_key,
            ).decode(),
            self.password,
        )

    def test_upload_certificate_sets_metadata(self):
        self._upload_cert()
        self.assertEqual(self.company.l10n_py_ccfe_ruc, "80069563-1")
        self.assertTrue(self.company.l10n_py_ccfe_valid_from)
        self.assertTrue(self.company.l10n_py_ccfe_valid_until)
        self.assertTrue(self.company.l10n_py_ccfe_loaded)

    def test_upload_without_password_raises(self):
        with self.assertRaises(UserError):
            self.company.write({"l10n_py_ccfe_certificate": base64.b64encode(self.p12)})

    def test_upload_wrong_password_raises(self):
        with self.assertRaises(UserError):
            self._upload_cert(password="wrong")

    def test_upload_expired_certificate_raises(self):
        expired = fixtures.make_expired_p12(password=self.password)
        with self.assertRaises(UserError):
            self._upload_cert(p12=expired)

    def test_upload_without_fernet_key_raises(self):
        with patch.dict("os.environ", {KEY_ENV: ""}):
            with self.assertRaises(UserError):
                self._upload_cert()

    def test_upload_with_malformed_fernet_key_raises(self):
        # Key inválida (no es base64 de 32 bytes) → UserError claro, no ValueError crudo.
        with patch.dict("os.environ", {KEY_ENV: "not-a-valid-key"}):
            with self.assertRaises(UserError):
                self._upload_cert()

    def test_get_certificate_roundtrip(self):
        self._upload_cert()
        p12_bytes, password = self.company._l10n_py_edi_get_certificate()
        self.assertEqual(p12_bytes, self.p12)
        self.assertEqual(password, self.password)
        info = self.company._l10n_py_edi_get_certificate_info()
        self.assertIsInstance(info, certificate.CertificateInfo)
        self.assertEqual(info.ruc, "80069563-1")

    def test_get_certificate_without_upload_raises(self):
        with self.assertRaises(UserError):
            self.company._l10n_py_edi_get_certificate()

    def test_csc_encrypted_roundtrip(self):
        self.company.write({"l10n_py_csc": COMMON_TEST_CSC, "l10n_py_csc_id": "0001"})
        self.assertTrue(self.company.l10n_py_csc_token)
        self.assertNotIn(COMMON_TEST_CSC, self.company.l10n_py_csc_token)
        self.assertEqual(self.company._l10n_py_edi_get_csc(), COMMON_TEST_CSC)
        self.assertEqual(self.company.l10n_py_csc_id, "0001")

    def test_inputs_are_write_only(self):
        self._upload_cert()
        # Los campos de input no persisten el secreto en claro:
        self.assertFalse(self.company.l10n_py_ccfe_certificate)
        self.assertFalse(self.company.l10n_py_ccfe_password)
        self.assertFalse(self.company.l10n_py_csc)

    def test_tokens_not_copied_on_duplicate(self):
        # Odoo 18 raises UserError on company.copy() — verify copy=False at
        # the field-definition level instead, which guarantees the ORM will
        # not carry tokens to any duplicated record.
        token_field = self.company._fields["l10n_py_ccfe_certificate_token"]
        self.assertFalse(
            token_field.copy,
            "l10n_py_ccfe_certificate_token debe tener copy=False",
        )
        # l10n_py_ccfe_loaded es compute desde certificate_token (copy=False),
        # por lo que en un registro nuevo siempre devuelve False.
        new_company = self.env["res.company"].create({"name": "Nueva PY"})
        self.assertFalse(new_company.l10n_py_ccfe_loaded)


@tagged("post_install", "-at_install", "l10n_py")
class TestEdiCommon(L10nPyEdiTestCase):
    def test_common_fixture_ready(self):
        self.assertTrue(self.company.l10n_py_ccfe_loaded)
        info = self.company._l10n_py_edi_get_certificate_info()
        self.assertEqual(info.ruc, "80069563-1")
        self.assertEqual(self.company._l10n_py_edi_get_csc(), COMMON_TEST_CSC)
