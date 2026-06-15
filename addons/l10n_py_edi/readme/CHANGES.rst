18.0.1.1.0 (2026-06-15)
~~~~~~~~~~~~~~~~~~~~~~~~

* Generador de CDC SIFEN: servicio puro ``services/cdc.py`` (composición,
  dígito verificador módulo 11, parse/validate) y asignación automática del
  CDC al postear documentos de venta (FE/NC/ND) con regla de reutilización
  del código de seguridad y constraint de unicidad.

18.0.1.0.0 (2026-06-10)
~~~~~~~~~~~~~~~~~~~~~~~~

* Skeleton inicial del módulo (manifest, estructura de directorios, deps Python).
* Implementación completa en iteraciones siguientes de PR-1.
