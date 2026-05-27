# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Hook post-install que maneja DBs preexistentes."""
import logging

from odoo import _

_logger = logging.getLogger(__name__)


def _post_init_hook(env):
    """Defensive handling for companies PY with pre-existing journals/charts."""
    py_companies = env["res.company"].search(
        [
            ("account_fiscal_country_id.code", "=", "PY"),
        ]
    )
    for company in py_companies:
        # Caso A: journals sale PY con use_documents pero sin PoE → desactivar + activity
        broken_journals = env["account.journal"].search(
            [
                ("company_id", "=", company.id),
                ("type", "=", "sale"),
                ("l10n_latam_use_documents", "=", True),
                ("l10n_py_point_of_emission_id", "=", False),
            ]
        )
        if broken_journals:
            _logger.warning(
                "Company %s: %d journals sale sin PoE — desactivando use_documents",
                company.name,
                len(broken_journals),
            )
            broken_journals.write({"l10n_latam_use_documents": False})
            for journal in broken_journals:
                try:
                    journal.activity_schedule(
                        "mail.mail_activity_data_todo",
                        summary=_("Configurar Punto de Emisión Paraguay"),
                        note=_(
                            "Este diario requiere Punto de Emisión para emitir "
                            "documentos PY. Configure el PoE y reactive "
                            '"Usar Documentos".'
                        ),
                        user_id=env.user.id,
                    )
                except Exception as exc:
                    _logger.warning("No se pudo crear activity: %s", exc)

        # Caso B: chart custom preexistente
        # Odoo 18: account.account usa company_ids (m2m), no company_id
        existing_accounts = env["account.account"].search_count(
            [
                ("company_ids", "in", [company.id]),
            ]
        )
        chart = company.chart_template
        if chart and chart != "py" and existing_accounts > 20:
            _logger.warning(
                "Company %s tiene chart '%s' con %d cuentas. l10n_py_account NO "
                "cargó el chart 'py' automáticamente. Use Configuración → "
                "Contabilidad → Migración Chart Paraguay.",
                company.name,
                chart,
                existing_accounts,
            )
