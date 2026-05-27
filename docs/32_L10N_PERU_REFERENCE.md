---
source: https://www.odoo.com/documentation/18.0/applications/finance/fiscal_localizations/peru.html + análisis local de references/odoo-18.0/addons/l10n_pe + nota importante de scope
fetched_at: 2026-05-19
summary: Localización Peru (l10n_pe + l10n_pe_edi) como referencia para Paraguay. ⚠️ l10n_pe_edi es ENTERPRISE; comunidad usa OCA/l10n-peru (en branches viejos por ahora).
priority: critical
---

# Perú — referencia para diseñar `l10n_py_*`

## ⚠️ Hallazgo crítico de scope

> **`l10n_pe_edi` NO está en Odoo 18 Community.** Es un addon **Enterprise-only**.
> El sparse checkout de `odoo/odoo` 18.0 community contiene solamente:
>
> - `l10n_pe`
> - `l10n_pe_pos`
> - `l10n_pe_website_sale`
>
> Para **patrones EDI comunitarios** referirse a `OCA/l10n-peru` — pero ese repo
> **aún no portó addons a 18.0** al momento de este bootstrap. En 16.0 sí hay
> material (no clonado todavía en este bootstrap).
>
> **Implicación para `l10n_py_edi`:** copiar el patrón de implementación EDI de
> `l10n_ec_edi` (OCA Ecuador, sí está en 17.0+) o de `l10n_mx_edi` / `l10n_cl_edi`
> (Odoo community), no de Perú.

A pesar de eso, la documentación oficial de Perú es **conceptualmente valiosa** —
muestra cómo Odoo abstrae temas que SIFEN también tiene (signature provider,
document types, certificate management, environment toggle test/prod).

## 1. Módulos del paquete Perú (Enterprise)

| Módulo                    | Técnico                 | Propósito                       | Disp. Comm   |
| ------------------------- | ----------------------- | ------------------------------- | ------------ |
| Peru - Accounting         | `l10n_pe`               | CoA, taxes, document types base | ✓            |
| Peru - E-invoicing        | `l10n_pe_edi`           | EDI SUNAT                       | ✗ Enterprise |
| Peru - Accounting Reports | `l10n_pe_reports`       | RVIE, RCE, PLE                  | ✗ Enterprise |
| Peruvian e-Delivery Note  | `l10n_pe_edi_stock`     | Guía de remisión                | ✗ Enterprise |
| Peru - Stock Reports      | `l10n_pe_reports_stock` | PLE inventario                  | ✗ Enterprise |
| Peruvian eCommerce        | `l10n_pe_website_sale`  | Checkout + identification       | ✓            |
| Peruvian POS              | `l10n_pe_pos`           | POS con datos fiscales          | ✓            |

## 2. Setup de empresa (lo que se mapea a `l10n_py_base`)

### Datos de la company

- **Country**: Peru
- **NIF (VAT)**: RUC
- **Address Type Code**: código de establecimiento SUNAT (default 0000)

### Chart of Accounts

Instalación automática con `l10n_pe`. Basado en PCGE peruano + NIIF-compatible.
Incluye cuentas pre-mapeadas para taxes, payable, receivable.

### Equivalente Paraguay

- En `l10n_py_base`: campos `l10n_py_ruc`, `l10n_py_dv_ruc`, `l10n_py_nombre_fantasia`
- En `l10n_py_account`: chart of accounts paraguayo (probablemente PUCE o uno
  custom — investigar el estándar contable PY)
- En `l10n_py_account`: catálogo de taxes (IVA 10%, 5%, exenta)

## 3. Configuración EDI / signature provider

Perú tiene 3 opciones:

### 1. IAP (Odoo In-App Purchase) — recomendado por Odoo SA

- Odoo provee certificado digital
- Envía a OSE (Digiflow) → SUNAT
- Maneja CDR (constancia de recepción)
- Cuesta créditos (~22 EUR / 1000)

### 2. Digiflow directo

- User compra certificado propio
- Firma agreement con Digiflow como OSE
- Provee SOL credentials

### 3. SUNAT directo

- Requiere certificación SUNAT (compleja)
- User maneja cert propio
- SOL credentials directas

### Equivalente Paraguay

**No hay IAP de Odoo para Paraguay.** Único camino: certificado CCFE propio +
conexión directa a SIFEN (siRecepDE / siRecepLoteDE). Análogo al modo "SUNAT
directo" de Perú.

→ En `l10n_py_edi/settings`: solo dos campos relevantes:

- `l10n_py_ccfe_certificate` (Binary, encriptado)
- `l10n_py_ccfe_password` (Char, encriptado)
- `l10n_py_environment` (Selection: test / production)

Sin proveedor intermedio, sin créditos, sin agreements.

## 4. Taxes — patrón

Naming convention en `l10n_pe`:

```
"IGV 18% (Gravada Operación Onerosa)"
"IGV 0% (Exonerada)"
"ICBPER (Bolsas Plásticas)"
```

Cada tax tiene campos EDI específicos:

- Tax type classification (clasificación SUNAT)
- Tax support code (código de afectación IGV)
- Tax grid (para reportes 104, etc.)

### Equivalente Paraguay

Naming en `l10n_py_account`:

```
"IVA 10% (Gravada)"
"IVA 5% (Reducida)"
"IVA Exenta"
"IVA 0% (Exportación)"
```

Campos custom en `account.tax`:

- `l10n_py_tax_code`: código IVA SIFEN (1=gravado, 3=exento)
- `l10n_py_iva_proporcion_default`: 100 (default), 85, 30, 50

## 5. Identification types (lo que va a `l10n_py_base`)

Perú:

- DNI (Documento Nacional de Identidad)
- RUC (Registro Único de Contribuyentes)
- CE (Carné de Extranjería)
- Pasaporte

### Equivalente Paraguay

- CI (Cédula de Identidad paraguaya) — código DNIT 1
- Pasaporte — código DNIT 2
- CI extranjera — código DNIT 3
- Carnet de residencia — código DNIT 4
- RUC — agregado custom (no es del catálogo de tipos del receptor SIFEN, es el
  identificador de contribuyente)

Estos se cargan como records de `l10n_latam.identification.type` con
`country_id = base.py`. Detalle en [`30_L10N_LATAM_BASE.md`](30_L10N_LATAM_BASE.md).

## 6. Document types (lo que va a `l10n_py_account`)

Perú maneja:

- Factura (01)
- Boleta (03 — para no-contribuyentes)
- Nota de Crédito (07)
- Nota de Débito (08)

Cada uno con su sequence per journal.

### Equivalente Paraguay

Records de `l10n_latam.document.type` con `country_id = base.py`:

- Factura Electrónica (code='01', internal_type='invoice')
- Autofactura (code='04')
- Nota de Crédito Electrónica (code='05', internal_type='credit_note')
- Nota de Débito Electrónica (code='06', internal_type='debit_note')
- Nota de Remisión Electrónica (code='07')

Detalle en [`31_L10N_LATAM_INVOICE_DOCUMENT.md`](31_L10N_LATAM_INVOICE_DOCUMENT.md).

## 7. Journal setup

Perú requiere:

- **Use Documents**: enable (activa l10n_latam_invoice_document)
- **Electronic Data Interchange**: seleccionar "Peru UBL 2.1"

### Equivalente Paraguay

- **Use Documents**: enable
- **Electronic Data Interchange**: seleccionar "SIFEN (DNIT Paraguay)" — record
  creado por `l10n_py_edi`
- **Establishment + Point of Emission**: campos custom — `l10n_py_establishment`,
  `l10n_py_point_of_emission` (Char 3 cada uno) o referencia a
  `l10n_py.point_of_emission`

## 8. Lifecycle de factura electrónica

Perú:

```
draft → posted → sent → accepted/rejected
```

`sent` significa "transmitido a OSE/SUNAT". `accepted` cuando llega CDR.

### Equivalente Paraguay (usando `account.edi.document`)

```
draft → posted → edi_state='to_send' → edi_state='sent' (DTE aprobado)
                                     → edi_state='to_send' con error (corregir)
                                     → edi_state='cancelled' (evento aprobado)
```

El framework `account.edi.document` ya maneja esto — `l10n_py_edi` solo
implementa los hooks (ver [`15_ODOO_ACCOUNT_EDI_FRAMEWORK.md`](15_ODOO_ACCOUNT_EDI_FRAMEWORK.md)).

## 9. Cancellation flow

Perú cancela vía un workflow específico que envía evento a SUNAT.

### Equivalente Paraguay

- Wizard `l10n.py.cancellation.wizard` (TransientModel)
- Pide campo `motivo` obligatorio (>5 chars)
- Llama `account.edi.format._cancel_invoice_edi(invoices)` con el motivo
- Construye XML de evento de cancelación
- Envía a `siRecepEvento`

## 10. Reportes (Fase de `l10n_py_reports`)

Perú tiene un sistema robusto de reportes PLE (Planilla de Libros Electrónicos):

- PLE 5.1 (libro diario)
- PLE 8.4 (registro compras electrónico)
- PLE 14.4 (registro ventas)
- etc.

### Equivalente Paraguay

- **Libro IVA Ventas**
- **Libro IVA Compras**
- **Hechauka** — sistema declaración de DNIT (estructura específica)
- **Reportes RG90** — retenciones
- **DDJJ IVA mensual**

Implementar en `l10n_py_reports` usando el framework `account_reports` (si es
community) o el built-in de `account` (manejo de reports custom). Investigar.

## 11. Take-aways prácticos para Paraguay

1. **No copiar `l10n_pe_edi` literalmente** — es Enterprise. Tomar el approach
   conceptual: clase `AccountEdiFormat` con código específico, XML builder,
   firma, send.
2. **Sí copiar de `l10n_pe`** (community) cómo arma chart of accounts, taxes,
   document types, journals. Es buen modelo.
3. **Para el patrón EDI**: mirar `l10n_ec_edi` (OCA Ecuador) o `l10n_mx_edi`
   (Odoo community) — más cercanos en spirit (auto-firma con cert propio).
4. **No replicar IAP / OSE intermediario** — Paraguay no tiene ese ecosistema,
   conexión directa a SIFEN con cert propio es el único path.
5. **Para sequences de document types**: usar el patrón
   `l10n_latam_invoice_document` (cada document type tiene su sequence por
   journal). Ver detalles en [`31_L10N_LATAM_INVOICE_DOCUMENT.md`](31_L10N_LATAM_INVOICE_DOCUMENT.md).

## Para query del código real

```
codegraph search "l10n_pe chart_template"
codegraph search "l10n_pe.document.type data"
codegraph file references/odoo-18.0/addons/l10n_pe/__manifest__.py
```
