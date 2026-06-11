18.0.1.1.1 (2026-06-11)
~~~~~~~~~~~~~~~~~~~~~~~~

* Fix modulo 11 DV mapping: resto 1 now maps to DV 0 per official SET
  routine (RUCs previously accepted with DV 1 for resto-1 bodies are now
  rejected; the correct DV 0 variant is now accepted)

18.0.1.1.0 (2026-05-25)
~~~~~~~~~~~~~~~~~~~~~~~~

* Add ``l10n_py.economic_activity`` catalog model (manual load; SET WS in Fase 2)
* Extend ``res.company`` with PY fiscal identity fields:
  ``l10n_py_taxpayer_type_id``, ``l10n_py_regime_id``,
  ``l10n_py_economic_activity_ids``, ``l10n_py_nombre_fantasia``, ``l10n_py_dv``
* Add modulo 11 RUC validation to company (mirrors partner validation)
* Add "Paraguay (Fiscal)" section in company form view

18.0.1.0.0 (2026-05-22)
~~~~~~~~~~~~~~~~~~~~~~~~

* Initial release: catalogs (departments, districts, cities, regimes, taxpayer types,
  identification types) + CI/RUC validation
