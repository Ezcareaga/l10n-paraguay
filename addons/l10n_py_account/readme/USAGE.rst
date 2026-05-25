Una vez configurado, las facturas de venta numeran automáticamente con formato
``EEE-PPP-NNNNNNN`` (ej: ``001-001-0000001``). Cada tipo de documento (Factura,
Nota de Crédito, Nota de Débito) tiene su propia secuencia correlativa dentro
del mismo journal — no comparten numeración (requisito SIFEN).

Para facturas de compra (recibidas del proveedor), el número se ingresa
manualmente en el campo "Número de Documento" del move.

La emisión real al SIFEN (firma XAdES + envío SOAP) está fuera de este módulo
y se implementa en ``l10n_py_edi`` (Fase 2).

**Cobertura por industria:**

* Comercio minorista (minimarket, almacén): cobertura completa.
* Gastronomía: cobertura completa.
* Servicios profesionales: cobertura completa.
* Importador/distribuidor: activar manualmente cuentas exterior (``4.06-4.08``)
  e ``1.01.04.11 Importaciones en curso``.
* Agro/ganadería: activar grupos ``4.02-4.05`` (ventas) y ``5.02-5.05``
  (costos), más activos biológicos.
* Régimen Turismo / Zona Franca / Maquila: activar grupos ``4.10``, ``5.10``
  y cuenta ``1.01.03.05.04 IVA Crédito Fiscal - Régimen Turismo``.
