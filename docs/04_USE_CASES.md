---
source: Extracted from ÑandeFact CLAUDE.md, section "CASOS DE USO MVP" + flujo técnico
fetched_at: 2026-05-19
summary: Casos de uso del sistema heredados de ÑandeFact, adaptados al modelo Odoo (account.move + account.edi.document + wizards).
priority: important
---

# Casos de Uso — adaptados a Odoo

> Adaptación de los casos de uso de ÑandeFact al ecosistema Odoo. En Odoo, los
> "casos de uso" se materializan como **métodos del modelo** (`action_*`), **wizards**
> (`models.TransientModel`), o **subclases de `account.edi.format`**.

## 1. Facturación (core)

### CU-01: Crear Factura

**Trigger:** Usuario en módulo `account` o POS → crea una `account.move` de tipo
`out_invoice` y la postea.

**Flujo Odoo:**

1. Usuario completa form de `account.move` con `partner_id`, `invoice_line_ids`.
2. `account.move.action_post()` (core) ejecuta validaciones generales.
3. `l10n_py_edi` extiende `_post()` para validar datos SIFEN obligatorios:
   - Partner tiene `l10n_latam_identification_type_id` + `vat`
   - Company tiene CCFE, timbrado activo, CSC
   - Todos los items tienen tax con `l10n_py_iva_*` configurado
4. Si pasa validaciones → genera `l10n_py_cdc` (computed `store=True`).
5. Marca `edi_document_ids` con `state='to_send'` para SIFEN.
6. Confirmación inmediata al usuario (no espera respuesta SIFEN).

**Quién lo hace:** Cualquier usuario con grupo `account.group_account_invoice`
(y `l10n_py_edi.group_l10n_py_user` que crearemos).

**Done when:** `account.move.state == 'posted'` + `edi_state == 'to_send'`.

### CU-02: Enviar DE a SIFEN

**Trigger:** Cron de `account.edi.document._cron_process_documents()` (cada 1h
por default) **o** botón manual "Send Now" en la vista de la factura.

**Flujo Odoo:**

1. Cron recoge `account.edi.document` con `state='to_send'` para formato `'py_dnit_sifen'`.
2. `account.edi.format._post_invoice_edi(invoices)` se llama por cada batch.
3. Para cada `invoice`:
   - Construye XML (`l10n_py_edi/services/xml_builder.py`)
   - Firma con CCFE (`l10n_py_edi/services/xmldsig.py` usando `signxml`)
   - Envía vía SOAP a `siRecepDE` o `siRecepLoteDE` (`l10n_py_edi/services/sifen_client.py` usando `zeep`)
   - Procesa respuesta:
     - Código 0260 → `edi_state='sent'`, attachment XML guardado
     - Códigos 0300-0399 → `edi_state='to_send'` con `error` y `blocking_level`
   - Loguea en `account.move.message_post` para auditoría
4. Si batch >1 invoice → usa endpoint asíncrono y guarda `lote_id` para consultar luego.

**Done when:** `edi_state == 'sent'` para invoices aprobadas, `'to_send'` con error
para rechazadas (reintentables).

### CU-03: Consultar resultado de lote (caso asíncrono)

**Trigger:** Cron específico de `l10n_py_edi._cron_consult_lote()` cada 15 min.

**Flujo:**

1. Buscar `account.edi.document` con `lote_id` pendiente y `last_query + 10min < now`.
2. Llamar `siResultLoteDE` con el `lote_id`.
3. Si código 0361 (en procesamiento) → actualizar `last_query`, reintentar.
4. Si código 0362 (concluido) → procesar resultados por CDC, actualizar cada
   `edi_document` correspondiente.
5. Si pasaron 48h sin resultado → fallback a `siConsDE` por cada CDC individual.

### CU-04: Anular Factura (evento de Cancelación SIFEN)

**Trigger:** Usuario presiona botón "Cancelar SIFEN" en una `account.move` ya
`posted` + `edi_state='sent'`.

**Flujo Odoo (wizard):**

1. Abrir wizard `l10n.py.cancellation.wizard` con campo `motivo` (Text, requerido,
   min 5 chars).
2. Usuario ingresa motivo (ej: "Operación anulada por cliente — duplicado").
3. Wizard llama `account.edi.format._cancel_invoice_edi(invoices)` con el motivo.
4. Construye XML de evento de cancelación (estructura `<rEnvioEvento>`).
5. Firma y envía a `siRecepEvento`.
6. Si aprobada:
   - Marca `account.move` como `cancel` (estado Odoo nativo)
   - `edi_state='cancelled'`
   - Crea entrada en chatter con motivo y respuesta SIFEN

**Restricciones:**

- DTE debe haber sido aprobado por SIFEN (`edi_state='sent'`)
- Solo permitido dentro del plazo SIFEN (consultar Manual Técnico vigente)
- Una vez cancelado, **inmutable** — para revertir, emitir Nota de Crédito

### CU-05: Inutilización de rango de numeración

**Trigger:** Usuario abre wizard `l10n.py.inutilizacion.wizard` desde menú
"l10n PY / Eventos / Inutilizar Rango".

**Flujo Odoo:**

1. Wizard pide: tipo_documento, establecimiento, punto_expedicion, numero_desde,
   numero_hasta, motivo.
2. Validaciones: rango debe ser correlativo no usado, motivo min 5 chars.
3. Construye XML de evento de inutilización.
4. Firma y envía a `siRecepEvento`.
5. Si aprobada: guarda en modelo `l10n_py.inutilizacion_range` para auditoría.

**Nota:** Este flujo NO tiene una `account.move` asociada — es un evento
independiente.

### CU-06: Generar KuDE (representación gráfica)

**Trigger:** Automático después de `edi_state='sent'`, **o** botón manual
"Imprimir KuDE" en la factura.

**Flujo Odoo:**

1. Reporte QWeb `l10n_py_edi.action_report_kude` (`ir.actions.report` con
   `report_type='qweb-pdf'`) ejecutado con `docids=invoice.ids`.
2. Template QWeb (`l10n_py_edi/reports/kude_template.xml`) renderiza:
   - Header con datos del emisor (extraídos de `company_id`)
   - Items (de `invoice_line_ids`)
   - Totales por tasa IVA (computed de `tax_totals` de Odoo)
   - QR generado con `qrcode` library (URL armada con CDC + CSC hash)
3. PDF se devuelve al usuario (download) y se attacha al `account.move` vía
   `_get_default_attachments()` para futuras descargas.

## 2. Setup inicial

### CU-07: Configurar Comercio (Company)

**Trigger:** Admin va a Settings → Companies → edita company.

**Datos a completar (nuevos campos de `l10n_py_base`):**

- RUC + DV
- Razón social, nombre fantasía
- Tipo contribuyente (PF/PJ)
- Tipo régimen (catálogo SIFEN)
- Actividades económicas (One2many)
- Dirección (departamento/distrito/ciudad — catálogos SIFEN)

**Validaciones:**

- RUC válido (DV módulo 11)
- Departamento/distrito/ciudad consistentes con catálogo SIFEN

### CU-08: Cargar Certificado Digital (CCFE)

**Trigger:** Admin va a Settings → l10n PY → Certificado.

**Flujo:**

1. Wizard `l10n.py.ccfe.upload.wizard` con campos: archivo (.p12), password.
2. Validación: archivo es PKCS#12 válido, password descifra correctamente.
3. Extrae RUC del certificado (SerialNumber o SubjectAlternativeName) → verifica
   que coincida con `company.l10n_py_ruc`.
4. Encripta archivo + password con `cryptography.fernet` (key en env var).
5. Guarda en `company.l10n_py_ccfe_certificate` (Binary encrypted) y
   `company.l10n_py_ccfe_password` (Char encrypted).

**Restricciones:**

- Solo admin (`base.group_system`)
- NUNCA loguear el contenido descifrado
- NUNCA exponer en read/list views — solo en form de configuración

### CU-09: Configurar Timbrado

**Trigger:** Admin va a Settings → l10n PY → Timbrados → New.

**Datos:**

- Número de timbrado (Char 15)
- Fecha desde, fecha hasta
- Estado (active/inactive)
- Company

**Validaciones:**

- Solo un timbrado `active=True` por company a la vez
- Fechas: `date_from < date_to`, ambas en futuro al crear
- Al activar, automáticamente desactivar el anterior

### CU-10: Configurar Punto de Emisión

**Trigger:** Admin va a Settings → l10n PY → Puntos de Emisión → New.

**Datos:**

- Establecimiento (Char 3)
- Punto de expedición (Char 3)
- Journal asociado (`account.journal`)
- Sequence de numeración (Many2one a `ir.sequence`)
- Company

**Validación:**

- Unique constraint: (company, establishment, point_of_emission)

### CU-11: Gestionar Productos y Clientes

Usa CRUD nativo de Odoo (`product.product`, `res.partner`). Solo se extienden
con campos SIFEN específicos (ver CU-01 validaciones).

## 3. Flujo UX de facturación (POS)

En `l10n_py_pos` el flujo se compacta:

1. Cajero abre sesión POS (con journal que tiene timbrado + punto de emisión vinculado).
2. Cajero arma orden (selecciona productos + cantidades).
3. Cajero selecciona cliente o deja "Consumidor Final" (innominado, hasta cierto monto).
4. Cajero toca "Pagar" → POS valida y postea la `pos.order`.
5. Al cerrar sesión: las `pos.order` generan `account.move`s correspondientes.
6. Cada `account.move` dispara el flujo CU-02 (envío SIFEN).
7. Si SIFEN online en el momento del cobro → envío inmediato; sino → cola hasta sync.

**Detalle de "innominado":** Existe un monto límite legal (consultar Manual Técnico
vigente) sobre el cual una factura puede emitirse sin identificar al receptor. Por
encima de ese monto, **es obligatorio** capturar CI o RUC.

## 4. Manejo de errores y reintentos

### Rechazos SIFEN (códigos 0300-0399)

- Si el error es **corregible sin cambiar CDC** (ej: típo en razón social del receptor):
  - Usuario edita los campos en la `account.move`
  - El framework `account.edi.document` reintenta automáticamente con el mismo CDC
- Si el error **invalida el CDC** (ej: cambio de fecha de emisión):
  - Se debe **emitir nuevo DE** con CDC nuevo
  - Inutilizar el rango del DE rechazado vía CU-05

### Errores técnicos (red, TLS, timeout)

- `edi_state='to_send'` queda con `error` no-blocking
- Cron sigue reintentando con backoff exponencial (configuración en `ir.config_parameter`)
- Después de N reintentos sin éxito → notificación al admin vía `mail.activity`

### Contingencia (SIFEN caído confirmado)

- Wizard manual para marcar `tipo_emision=2` (Contingencia) en la próxima emisión
- Esto cambia el dígito 34 del CDC
- Una vez SIFEN se recupera, las DE contingencia se envían igual
- Validación: contingencia solo permitida si SIFEN reporta downtime oficial
  (no es un atajo para evitar envíos)

## 5. Tests por caso de uso

| Caso de uso                    | Test type                               | Archivo sugerido                           |
| ------------------------------ | --------------------------------------- | ------------------------------------------ |
| CU-01 (Crear)                  | TransactionCase unit                    | `l10n_py_edi/tests/test_invoice_post.py`   |
| CU-02 (Enviar)                 | TransactionCase integration (mock SOAP) | `l10n_py_edi/tests/test_sifen_send.py`     |
| CU-03 (Consultar lote)         | TransactionCase (mock SOAP)             | `l10n_py_edi/tests/test_lote_consult.py`   |
| CU-04 (Cancelar)               | TransactionCase + wizard                | `l10n_py_edi/tests/test_cancellation.py`   |
| CU-05 (Inutilización)          | TransactionCase + wizard                | `l10n_py_edi/tests/test_inutilizacion.py`  |
| CU-06 (KuDE)                   | TransactionCase + render PDF            | `l10n_py_edi/tests/test_kude_report.py`    |
| CU-07/08/09/10 (Setup)         | TransactionCase                         | `l10n_py_base/tests/test_company_setup.py` |
| Flujo POS                      | HttpCase + tour JS                      | `l10n_py_pos/tests/test_pos_flow.py`       |
| End-to-end con SIFEN test real | `@tagged('-standard', 'external')`      | `l10n_py_edi/tests/test_e2e_sifen.py`      |

Ver convenciones de testing en [`14_ODOO_TESTING_GUIDE.md`](14_ODOO_TESTING_GUIDE.md).
