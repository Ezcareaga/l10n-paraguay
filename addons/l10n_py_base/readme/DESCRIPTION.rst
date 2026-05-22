Foundational module for the Paraguayan localization (DNIT/SIFEN).

Provides:

* Canonical SIFEN catalogs derived from Manual Técnico v150
  (departments, districts, cities, economic regimes, taxpayer types,
  recipient nature, identification types).
* Extension of ``l10n_latam.identification.type`` with the SIFEN code
  (field D208 ``iTipIDRec``) for Paraguayan document types.
* Pure-Python helper implementing the Paraguayan módulo 11 algorithm
  for verification digits (RUC and CDC).
* ``res.partner`` constraints that validate CI and RUC numbers.
