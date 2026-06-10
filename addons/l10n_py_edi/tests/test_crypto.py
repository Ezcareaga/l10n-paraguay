# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de los helpers Fernet — Python puro, no requiere Odoo registry."""
from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_edi.services import crypto


@tagged("standard", "l10n_py")
class TestCrypto(BaseCase):
    def test_generate_data_key_is_valid_fernet_key(self):
        key = crypto.generate_data_key()
        # Una key Fernet válida permite cifrar sin levantar excepción.
        token = crypto.encrypt_secret(b"payload", key)
        self.assertIsInstance(token, bytes)

    def test_roundtrip(self):
        key = crypto.generate_data_key()
        secret = b"\x00\x01binary p12 bytes\xff"
        token = crypto.encrypt_secret(secret, key)
        self.assertNotEqual(token, secret)
        self.assertEqual(crypto.decrypt_secret(token, key), secret)

    def test_decrypt_with_wrong_key_raises(self):
        token = crypto.encrypt_secret(b"data", crypto.generate_data_key())
        with self.assertRaises(crypto.DecryptionError):
            crypto.decrypt_secret(token, crypto.generate_data_key())

    def test_decrypt_garbage_token_raises(self):
        with self.assertRaises(crypto.DecryptionError):
            crypto.decrypt_secret(b"not-a-token", crypto.generate_data_key())

    def test_rotate_secret(self):
        old_key = crypto.generate_data_key()
        new_key = crypto.generate_data_key()
        token = crypto.encrypt_secret(b"ccfe", old_key)
        new_token = crypto.rotate_secret(token, old_key, new_key)
        self.assertEqual(crypto.decrypt_secret(new_token, new_key), b"ccfe")
        with self.assertRaises(crypto.DecryptionError):
            crypto.decrypt_secret(new_token, old_key)
