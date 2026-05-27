---
source: https://www.odoo.com/documentation/18.0/applications/finance/fiscal_localizations/argentina.html + análisis local references/odoo-18.0/addons/l10n_ar + references/l10n-argentina-16.0/
fetched_at: 2026-05-19
summary: Localización Argentina (l10n_ar + l10n_ar_edi en community) — patrón maduro de l10n_latam_invoice_document. Útil sobre todo para tipos de documento y document letters.
priority: important
---

# Argentina — referencia patrón `l10n_latam_invoice_document`

> Argentina es el ejemplo **más maduro y completo** de uso del framework
> `l10n_latam_invoice_document` en Odoo community. Para Paraguay tomamos de aquí
> el patrón de gestión de document types y numeración por punto de emisión.
>
> **Disponible en Odoo 18 community:** `l10n_ar`, `l10n_ar_edi`, `l10n_ar_reports`,
> `l10n_ar_withholding`, `l10n_ar_website_sale`. Sparse-checked en
> `references/odoo-18.0/addons/l10n_ar`.

## 1. Módulos

| Módulo                 | Disp. Community 18.0                                                                               |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| `l10n_ar`              | ✓                                                                                                  |
| `l10n_ar_edi`          | ✓                                                                                                  |
| `l10n_ar_reports`      | (probablemente Enterprise — verificar)                                                             |
| `l10n_ar_withholding`  | (idem)                                                                                             |
| `l10n_ar_website_sale` | (idem)                                                                                             |
| **OCA addons**         | en `references/l10n-argentina-16.0/` (16.0 tiene módulos; 17.0 y 18.0 OCA aún vacíos al bootstrap) |

## 2. Chart of Accounts

Argentina ofrece 3 packages por responsabilidad AFIP:

- **Monotributista** (227 cuentas)
- **IVA Exento** (290 cuentas)
- **Responsable Inscripto** (298 cuentas)

Se elige uno durante el setup inicial de la company.

### Equivalente Paraguay

Probablemente un solo chart of accounts paraguayo basado en el **Plan Único de
Cuentas (PUC)** o un estándar OCA-friendly. Investigar si DNIT/SET prescribe
algo o si la práctica común usa un PUC adaptado.

## 3. AFIP Electronic Invoicing — separación test/prod

```
Test (Prueba)     ←  certs específicos del ambiente test, no transferibles
Producción        ←  certs específicos del ambiente producción
```

### Equivalente Paraguay

Mismo modelo:

- `sifen-test.set.gov.py` con CCFE de test
- `sifen.set.gov.py` con CCFE de producción

En `l10n_py_edi`: campo `l10n_py_environment` (Selection: test / production)
en `res.company` controla a qué URL apuntar.

## 4. Certificate management — workflow Argentina

1. Generar **CSR** (Certificate Sign Request) en Odoo (`.csr` file)
2. Llevar el `.csr` al portal AFIP
3. AFIP devuelve certificate + private key
4. Upload de ambos a Odoo (Settings → Argentinean Localization)

### Equivalente Paraguay

1. Comprar CCFE de prestador autorizado (Documenta, eFirmar, IDOK, etc.)
2. Recibir `.p12` + password
3. Upload via wizard en Odoo (`l10n_py_base/wizards/ccfe_upload_wizard.py`)
4. Encriptar y guardar

**Diferencia:** Paraguay NO genera CSR desde Odoo — el `.p12` viene completo del
prestador. Más simple que Argentina.

## 5. Document Types Framework — clave para `l10n_py_account`

> Argentina es el **patrón maestro** para uso de `l10n_latam_invoice_document` —
> estudiar este código antes de implementar Paraguay.

### Letters (clasificación AFIP)

| Letter | Uso                                                                              |
| ------ | -------------------------------------------------------------------------------- |
| A      | B2B entre vendedores registrados (responsable inscripto a responsable inscripto) |
| B      | B2C / retail (a consumidor final)                                                |
| C      | Monotributista emite                                                             |
| E      | Exportación                                                                      |
| M      | Casos especiales                                                                 |

### Document types comunes

- **Factura** (FA-A, FA-B, FA-C, FA-E)
- **Nota de Crédito** (NC-A, NC-B, etc.)
- **Nota de Débito** (ND-A, ND-B, etc.)
- **Ticket** (TKT-A, TKT-B — POS)

Cada uno con AFIP code numérico (1=Factura A, 6=Factura B, 11=Factura C, etc.)
y `l10n_latam.document.type` record.

### Patrón a copiar para Paraguay

En `l10n_py_account/data/l10n_latam_document_type_data.xml`:

```xml
<record id="l10n_py_doc_type_01" model="l10n_latam.document.type">
    <field name="name">Factura Electrónica</field>
    <field name="code">01</field>
    <field name="doc_code_prefix">FE</field>
    <field name="country_id" ref="base.py"/>
    <field name="internal_type">invoice</field>
    <field name="active">True</field>
</record>

<record id="l10n_py_doc_type_05" model="l10n_latam.document.type">
    <field name="name">Nota de Crédito Electrónica</field>
    <field name="code">05</field>
    <field name="doc_code_prefix">NC</field>
    <field name="country_id" ref="base.py"/>
    <field name="internal_type">credit_note</field>
    <field name="active">True</field>
</record>

<record id="l10n_py_doc_type_06" model="l10n_latam.document.type">
    <field name="name">Nota de Débito Electrónica</field>
    <field name="code">06</field>
    <field name="doc_code_prefix">ND</field>
    <field name="country_id" ref="base.py"/>
    <field name="internal_type">debit_note</field>
    <field name="active">True</field>
</record>
```

Detalles del framework: ver [`31_L10N_LATAM_INVOICE_DOCUMENT.md`](31_L10N_LATAM_INVOICE_DOCUMENT.md).

## 6. Sequence management

Argentina:

> "For the first invoice, Odoo synchronizes with the AFIP automatically and
> displays the last sequence used."

Para "Unified Books" (POS preimpreso): docs con misma letter comparten sequence:

- FA-A 0001-00000002
- NC-A 0001-00000003
- ND-A 0001-00000004

### Equivalente Paraguay

NO hay sincronización con SIFEN para sequences — el sistema emisor es la fuente
de verdad. Pero el principio es similar:

- Sequence per `(establishment, point_of_emission, document_type)`
- Si se saltea un número → evento de **Inutilización** obligatorio

Diseño: `l10n_py.point_of_emission` tiene Many2one a `ir.sequence` por document
type. O un `ir.sequence` por `(point, doc_type)` con `_compute` que las arma.

## 7. AFIP Responsibility Types — partner classification

Argentina define:

- **Responsable Inscripto**
- **Monotributista**
- **Consumidor Final**
- **Exento**
- **No Categorizado**

El **responsibility type** del receptor + emisor determina qué letter (A/B/C/E)
puede emitirse.

### Equivalente Paraguay

Paraguay tiene:

- **Persona Física (Contribuyente)**
- **Persona Jurídica (Contribuyente)**
- **Consumidor Final (No Contribuyente)** — recibe factura con CI o innominado

Es **más simple** que Argentina — no hay letters condicionales. La selección del
document type es directa: factura para todo, NC/ND según operación.

Solo restricción: si el receptor tiene tipo_documento=5 (innominado), debe
haber monto límite legal (revisar Manual Técnico vigente).

## 8. Web Services AFIP

Argentina conecta a varios WS según operación:

- **wsfev1** — facturación electrónica estándar (A, B, C, M)
- **wsbfev1** — fiscal bonds (capital goods)
- **wsfexv1** — exportación (E)

Cada uno con WSDL distinto.

### Equivalente Paraguay

SIFEN tiene también varios WS pero **agrupados por operación, no por tipo de
documento**:

- `siRecepDE` — individual
- `siRecepLoteDE` — lote
- `siRecepEvento` — cancelación/inutilización
- `siConsDE`, `siConsRUC`, `siResultLoteDE` — consultas

Más simple: un solo "tipo" de envío, varios endpoints según volumen/operación.

## 9. CAE vs CDC

|                   | Argentina                                    | Paraguay                                              |
| ----------------- | -------------------------------------------- | ----------------------------------------------------- |
| Identificador     | **CAE** (Código de Autorización Electrónica) | **CDC** (Código de Control)                           |
| Generación        | **AFIP lo devuelve** post-aprobación         | **Sistema emisor lo genera** pre-envío                |
| Largo             | 14 dígitos                                   | 44 dígitos                                            |
| Incluye fecha vto | Sí (vto del CAE)                             | No (CDC eterno una vez aprobado)                      |
| Si rechazado      | CAE no se otorga, hay que reintentar         | CDC reutilizable si corrección no toca campos del CDC |

**Implicación clave para diseño:** Paraguay genera el CDC ANTES de enviar (lo
que permite incluirlo en el XML que se firma). Argentina firma sin CAE y lo
recibe en respuesta. Por eso el flujo Python en Paraguay es:

```python
def _post_invoice_edi(self, invoices):
    for invoice in invoices:
        cdc = invoice.l10n_py_cdc  # YA está calculado y guardado
        xml = build_xml(invoice, cdc)
        signed = sign_xml(xml)
        response = send_to_sifen(signed)
        # CDC no cambia aunque la respuesta sea OK o ERROR
```

## 10. Withholdings Argentina

Argentina configura:

- **Earnings (Ganancias)**: income base
- **Earnings Scale**: tablas progresivas
- **IIBB (Ingresos Brutos)**: provincial — total amount + untaxed

Aplicado automáticamente durante creación de pago basado en partner + tipo de op.

### Equivalente Paraguay

Estructura similar (más simple — sin IIBB provincial):

- **Retención IVA**: % sobre IVA en compras
- **Retención IRE/IRP**: % sobre base imponible

Diseño: ver Phase 6 en `50_MODULES_ROADMAP.md`.

## 11. Reportes Argentina

- **VAT Summary** (input vs output, neto)
- **IIBB reports** (por jurisdicción)

### Equivalente Paraguay

Más en [`32_L10N_PERU_REFERENCE.md`](32_L10N_PERU_REFERENCE.md) sección 10 y
en `50_MODULES_ROADMAP.md` Phase 4.

## 12. Take-aways prácticos

1. **`l10n_ar` es el patrón maestro de `l10n_latam_invoice_document`** — copiar
   estructura de:
   - `l10n_ar/data/l10n_latam.document.type.csv` o XML
   - `l10n_ar/models/account_journal.py` para document types selection
   - `l10n_ar/models/account_move.py` para document number computation
2. **No replicar el sistema de letters** (A/B/C/E) — Paraguay no lo necesita
3. **Sí replicar el modelo de sequence per (journal, document_type)** — esencial
   para numeración correlativa SIFEN-compliant
4. **Estudiar `l10n_ar_edi`** para ver cómo conecta a AFIP web services con
   WSAA + WSFEv1 — el patrón Python (zeep + cert management) es muy similar a
   lo que vamos a hacer con SIFEN

## Queries útiles

```
codegraph search "l10n_ar document type data"
codegraph search "l10n_ar_edi WSFEv1"
codegraph file references/odoo-18.0/addons/l10n_ar/models/account_journal.py
codegraph file references/odoo-18.0/addons/l10n_ar_edi/models/account_move.py
```
