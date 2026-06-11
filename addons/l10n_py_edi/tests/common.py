# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Fixture compartido para tests EDI: company PY + CCFE de prueba cargado."""
import os

from odoo.addons.l10n_py_account.tests.common import L10nPyAccountTestCase
from odoo.addons.l10n_py_edi.services import crypto
from odoo.addons.l10n_py_edi.tests import fixtures

KEY_ENV = "L10N_PY_EDI_CCFE_KEY"
TEST_CSC = "ABCD0000000000000000000000000000"


class L10nPyEdiTestCase(L10nPyAccountTestCase):
    """Company PY + chart + timbrado + PoE + certificado CCFE self-signed.

    El certificado se genera en runtime (tests/fixtures.py) — nunca hay un
    .p12 real en el repo. La Fernet key se inyecta por env var.

    La key se muta directamente en os.environ (no mock.patch.dict) porque el
    check_attrs del runner de Odoo 18 itera los patchers y falla si _patch_dict
    no expone .target. El cleanup se registra con addClassCleanup inmediatamente
    después de la mutación, garantizando restore incluso si setUpClass falla a
    mitad.
    """

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
        cls.ccfe_password = "test-password"
        cls.ccfe_p12 = fixtures.make_test_p12(password=cls.ccfe_password)
        cls.company.l10n_py_edi_set_certificate(cls.ccfe_p12, cls.ccfe_password)
        cls.company.l10n_py_edi_set_csc(TEST_CSC)
        cls.company.l10n_py_csc_id = "0001"
