---
source: Extracted from ÑandeFact CLAUDE.md, section "MODELO DE DOMINIO"
fetched_at: 2026-05-19
summary: Modelo de dominio conceptual (actores, entidades, value objects, agregados, puertos) heredado de ÑandeFact. En Odoo se mapea a modelos ORM con `_inherit`.
priority: important
---

# Modelo de Dominio — referencia conceptual

> Este documento describe el **modelo de dominio** que ÑandeFact (Node/TS) implementó
> con arquitectura hexagonal. En Odoo NO replicamos la arquitectura hexagonal
> literalmente — usamos el patrón "modelos ORM + servicios delgados" que es idiomático
> Odoo. Pero las **invariantes y relaciones de dominio** se conservan tal cual.

## 1. Actores

| Actor | Descripción | Mapeo Odoo |
|-------|-------------|-----------|
| Comerciante | Usa el sistema para facturar. Usuario principal. | `res.users` con grupos de `l10n_py_*` |
| Cliente / Comprador | Recibe la factura. Identificado (CI/RUC) o innominado. | `res.partner` (con `l10n_latam_identification_type`) |
| DNIT / SIFEN | Valida y aprueba las facturas electrónicas. | External service vía `account.edi.format` |
| Admin | Onboarding comerciantes, monitoreo del sistema. | `res.users` con `base.group_system` |

## 2. Entidades centrales

### Comercio
Negocio del comerciante. RUC, razón social, timbrado, CCFE. Puede tener múltiples
usuarios.

**Mapeo Odoo:** `res.company` extendido con campos:
- `l10n_py_ruc` (Char)
- `l10n_py_dv_ruc` (Char)
- `l10n_py_nombre_fantasia` (Char)
- `l10n_py_tipo_contribuyente` (Selection: persona_fisica / persona_juridica)
- `l10n_py_tipo_regimen` (Many2one a catálogo SIFEN)
- `l10n_py_actividad_economica_ids` (One2many a `l10n_py.actividad_economica`)
- `l10n_py_ccfe_certificate` (Binary, encrypted)
- `l10n_py_ccfe_password` (Char, encrypted)
- `l10n_py_csc` (Char, encrypted)
- `l10n_py_csc_id` (Char)
- `l10n_py_environment` (Selection: test / production)

### Producto
Lo que vende el comerciante. Nombre, precio, IVA, unidad de medida.

**Mapeo Odoo:** `product.template` / `product.product` extendido con:
- `l10n_py_unit_measure` (Many2one a catálogo SIFEN — códigos 77/83/87/etc)
- IVA mapeado a `account.tax` (que ya existe en core)

### Cliente
Destinatario de la factura. CI/RUC identificado o innominado. Los frecuentes se
guardan para autocompletado.

**Mapeo Odoo:** `res.partner` extendido con:
- `l10n_latam_identification_type_id` (de `l10n_latam_base`)
- `vat` (RUC o CI, según identification_type)
- `l10n_py_enviar_whatsapp` (Boolean, opcional para flujo POS)

### Factura
Documento principal. CDC único 44 dígitos, items, montos IVA, estado SIFEN.

**Mapeo Odoo:** `account.move` extendido con:
- `l10n_latam_document_type_id` (de `l10n_latam_invoice_document`)
- `l10n_latam_document_number` (de `l10n_latam_invoice_document`)
- `l10n_py_cdc` (Char 44, computed/stored)
- `l10n_py_codigo_seguridad` (Char 9, computed)
- `l10n_py_tipo_emision` (Selection: normal / contingencia)
- `l10n_py_qr_url` (Char, computed)
- `l10n_py_xml_signed` (Binary, computed/stored — se obtiene del `edi_document_ids`)
- `l10n_py_kude_pdf` (Binary, generated por QWeb)
- Estado SIFEN reutiliza el `edi_state` del framework `account.edi.document`

### Detalle Factura (línea)
Línea individual de la factura (ej: 3kg mandioca @ Gs 5.000/kg = Gs 15.000).

**Mapeo Odoo:** `account.move.line` — las líneas ya existen en core. Solo se
extienden con campos SIFEN necesarios:
- `l10n_py_iva_tipo` (Selection: gravado / parcial / exento)
- `l10n_py_iva_proporcion` (Integer 1-100, default 100)

### Documento Electrónico (DE)
Representación XML para SIFEN. Conceptualmente separado de Factura (modelo negocio
vs formato SIFEN), aunque en Odoo se modela como atributo computado / generado
por el formato EDI.

**Mapeo Odoo:** `account.edi.document` (del módulo `account_edi`) — ya provee
estado, attachments, retries. No requiere modelo nuevo.

## 3. Value Objects

> En Odoo, los value objects suelen modelarse como **campos computed** con
> validaciones (`@api.constrains`) o como métodos estáticos/utilidades.
> No creamos modelos ORM separados para ellos a menos que tengan persistencia.

### CDC
44 dígitos con estructura interna y validación módulo 11. NO es un string simple.
Se genera ANTES de enviar a SIFEN.

**Implementación Odoo:**
- Field `l10n_py_cdc` en `account.move` con `compute='_compute_l10n_py_cdc'` + `store=True`
- Constraint `@api.constrains('l10n_py_cdc')` para validar DV
- Helper en `l10n_py_edi/services/cdc.py`: `build_cdc(values: dict) -> str`, `validate_cdc(cdc: str) -> bool`

### MontoIVA
Calcula base gravada + IVA según tipo (10%, 5%, exenta). En PYG sin decimales.

**Implementación Odoo:**
- El cálculo de IVA ya es responsabilidad de `account.tax._compute_amount()` en core
- Para Paraguay: definir `account.tax` con `amount_type='percent'`, `price_include=True`, `amount=10` o `5`
- La proporción parcial (85%, 30%) requiere taxes "compuestos" o un campo extra en `account.move.line` (`l10n_py_iva_proporcion`)

### RUC
Formato específico paraguayo con dígito verificador.

**Implementación Odoo:**
- Almacenado en `res.partner.vat` cuando `l10n_latam_identification_type_id` = RUC
- Validación: `l10n_py_base/models/res_partner.py:_check_vat_py(self, vat: str) -> bool`
- Patrón estándar de OCA: extender método `check_vat_py` que ya existe en Odoo base si está, sino crear

### Timbrado
Número + rango fechas vigencia. Valida si está vigente al momento de emisión.

**Implementación Odoo:**
- Nuevo modelo `l10n_py.timbrado` con campos: `name` (número), `date_from`, `date_to`, `company_id`, `state`
- Relación con `account.journal`: cada journal de ventas tiene un `l10n_py_timbrado_id` activo
- Constraint: solo un timbrado activo a la vez por (company × establecimiento × punto_expedicion)

### Establecimiento + Punto de Expedición
Códigos de 3 dígitos que identifican sucursal y punto de venta.

**Implementación Odoo:**
- Nuevo modelo `l10n_py.point_of_emission`: `code` (Char 3), `establishment_code` (Char 3), `name`, `company_id`, `journal_ids`
- O alternativamente: campos directos en `account.journal` (`l10n_py_establishment`, `l10n_py_point_of_emission`)

## 4. Agregados

### Agregado Factura (raíz)
```
Factura (account.move)
  ├── DetalleFactura[] (account.move.line de tipo product)
  ├── CDC (computed/stored)
  ├── MontoIVA por línea (delegado a account.tax)
  ├── Totales por tasa IVA (computed)
  └── EstadoSifen (edi_state de account.edi.document)
```

**Invariantes protegidas (validadas en `_check_*` constraints):**
- Mínimo 1 item (validación core de account.move)
- Total = suma de detalles (validación core)
- IVA cuadra: 10% → base = total / 1.10, IVA = total − base (validación core)
- IVA cuadra: 5% → base = total / 1.05, IVA = total − base (validación core)
- CDC válido (44 dígitos, DV correcto) — `l10n_py_edi` constraint
- Timbrado vigente al momento de emisión — `l10n_py_edi` constraint
- Una vez aprobada por SIFEN (`edi_state == 'sent'`) → **INMUTABLE** (solo cancelable por evento)
- Numeración correlativa por establecimiento + punto de expedición (validación al postear)

### Agregado Comercio
```
Comercio (res.company)
  ├── Usuario[] (res.users a través de res.users.company_ids)
  ├── Timbrado activo (l10n_py.timbrado con state='active')
  ├── PuntoExpedicion[] (l10n_py.point_of_emission)
  └── CertificadoDigital (campo encrypted)
```

## 5. Puertos (interfaces) — adaptación a Odoo

> En arquitectura hexagonal Node/TS, ÑandeFact tenía puertos (interfaces) para
> persistencia, SIFEN, KuDE, etc. En Odoo NO usamos esta separación literal: el
> ORM ES el adaptador de persistencia, y los servicios externos se llaman desde
> métodos del modelo o desde `account.edi.format`.

| Puerto ÑandeFact | Equivalente Odoo |
|------------------|------------------|
| `IFacturaRepository` | `self.env['account.move']` (ORM directo) |
| `IProductoRepository` | `self.env['product.product']` |
| `IClienteRepository` | `self.env['res.partner']` |
| `IComercioRepository` | `self.env['res.company']` |
| `ISifenGateway` | Método `_l10n_py_send_to_sifen(self)` en `account.edi.format` |
| `ICDCGenerator` | Helper en `l10n_py_edi/services/cdc.py` |
| `IKudeGenerator` | Reporte QWeb (`ir.actions.report` con `report_type='qweb-pdf'`) |
| `INotificador` | (Opcional) Servicio en `l10n_py_edi/services/whatsapp.py` o usar `mail.thread.message_post` |
| `IFirmaDigital` | Helper en `l10n_py_edi/services/xmldsig.py` usando `signxml` |
| `IAuthService` | `res.users` + grupos Odoo |

**Por qué no replicar hexagonal en Odoo:**
- El ORM de Odoo ya invierte la dependencia (BL no conoce SQL).
- Multiplicar capas genera fricción con el resto del ecosistema Odoo (otros addons,
  vistas, automated actions) que asumen modelos planos.
- OCA prefiere "modelos delgados + helpers en módulos" sobre arquitecturas
  paralelas a Odoo.

**Lo que SÍ se conserva del enfoque hexagonal:**
- **Lógica de dominio en helpers puros** (`services/cdc.py`, `services/xmldsig.py`)
  testables sin Odoo levantado.
- **Validaciones en `@api.constrains`** en lugar de inline en el método de creación.
- **Adapter pattern** para SIFEN (un único punto de entrada `_l10n_py_send_to_sifen`)
  que permite mockear en tests.

## 6. Estados de la Factura (state machine)

```
draft ─────action_post()────► posted (sin EDI) ────action_send_and_print()────►
                                                                              │
                                                                              ▼
                                                                       edi_state='to_send'
                                                                              │
                                              ┌───────── job sync SIFEN ──────┤
                                              │                               │
                                              ▼                               ▼
                                       edi_state='sent'              edi_state='to_send'
                                       (DTE aprobado)                (con error, reintentar)
                                              │
                       evento de cancelación  │
                                              ▼
                                       cancel + edi_state='cancelled'
```

**Notas:**
- El framework `account.edi.document` maneja la state machine de `to_send` →
  `sent` / `cancel` / `error`. No lo reinventamos.
- "Inutilización" (saltarse números) es un caso especial que NO sigue el flow
  estándar — es un wizard que envía evento sin tener un `account.move` real.
