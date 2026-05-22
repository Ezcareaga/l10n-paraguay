# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Hooks de instalación de l10n_py_base."""
import logging

_logger = logging.getLogger(__name__)


def _post_init_hook(env):
    """Configuración post-install.

    Marca el país Paraguay con `vat_label='RUC'` para que la UI muestre
    el label correcto en partners/companies paraguayos.
    """
    country_py = env.ref("base.py", raise_if_not_found=False)
    if country_py:
        country_py.write({"vat_label": "RUC"})
        _logger.info("l10n_py_base: vat_label de Paraguay configurado como 'RUC'.")
