Plan de cuentas paraguayo basado en la **Resolución General DNIT 49/14** (estándar
de facto para reporting Hechauka), impuestos IVA (10%, 5%, exenta, exportación 0%),
5 tipos de documento electrónico SIFEN (Factura, Autofactura, Notas de Crédito,
Débito y Remisión) con formato de numeración ``EEE-PPP-NNNNNNN``, modelos de
**Timbrado** y **Punto de Emisión**, y extensiones a ``account.journal`` y
``account.move`` para numeración independiente por (journal, tipo de documento).

Este módulo cierra la fase contable previa al EDI SIFEN (Fase 2 - ``l10n_py_edi``).
