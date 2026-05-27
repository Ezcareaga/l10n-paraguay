---
source: Brainstorming Fase 1b — sesión 2026-05-25 con Claude (Opus 4.7)
fetched_at: 2026-05-25
summary: Diseño consolidado de Fase 1b — l10n_py_account (PUC RG 49/14 + taxes IVA + document types SIFEN + timbrado + punto de emisión + extensión journal). Incluye bump l10n_py_base→1.1.0.
priority: critical
status: approved (sin gate externo — iteración por feedback post-release)
---

# Fase 1b — `l10n_py_account` + bump `l10n_py_base` 1.1.0

## 0. Contexto y objetivo

Fase 1a (`l10n_py_base` 18.0.1.0.0) cerró el 2026-05-22 con 21 tests verdes
cubriendo identification types, regímenes, taxpayer types, recipient natures,
departamentos/distritos/ciudades y validación CI/RUC en `res.partner`.

Fase 1b cubre la mitad **contable** del scope original de Fase 1 (roadmap §1):
plan de cuentas, taxes IVA, document types `l10n_latam.document.type`, modelos
de timbrado + punto de emisión + extensiones de `account.journal` y
`account.move`. Cierra el gap en `l10n_py_base` (extensión `res.company` que se
había diferido) bumpeando a `18.0.1.1.0`.

**Out of scope (explícitamente diferido):**

- Generación de CDC (44 dígitos) → Fase 2 `l10n_py_edi`.
- Firma XAdES + cliente SOAP SIFEN → Fase 2.
- Serie alfabética del timbrado (AA-ZZ) → Fase 2.
- Retenciones IVA/IRE/IRP → Fase 5 `l10n_py_withholding`.
- Modelo `l10n_py.economic_activity` autopopulado vía WS SET → Fase 2 (en 1b
  queda con UI carga manual + ejemplo demo).
- `l10n_latam.document.type` "Futuro" (códigos 2/3/8: export, import, retención)
  → habilitarlos cuando DNIT los active.
- Nota de Remisión (código 7) flujo funcional con stock → futuro `l10n_py_stock`.

## 1. Arquitectura general

### 1.1. Dos módulos tocados

**`l10n_py_base` → bump `18.0.1.1.0`** (cierra gap de Fase 1a):

- Modelo nuevo `l10n_py.economic_activity` (catálogo SIFEN; vacío por defecto,
  se llenará vía WS SET en Fase 2; UI permite carga manual con 1-2 records demo).
- Extensión `res.company`:
  - `l10n_py_taxpayer_type_id` (M2O `l10n_py.taxpayer.type`)
  - `l10n_py_regime_id` (M2O `l10n_py.regime`)
  - `l10n_py_economic_activity_ids` (M2M)
  - `l10n_py_nombre_fantasia` (Char)
  - `l10n_py_dv` (Char(1), computed desde `vat`, store=True)
  - Validación módulo 11 del RUC análoga a la del partner (reutiliza
    `models/modulo11.py` ya existente en base).
- Views: sección "Paraguay" en form de company; tree/form/menu de
  economic_activity bajo "Catálogos PY".
- Sin migration script (campos nuevos solo; `_post_init_hook` actual se mantiene
  idempotente).

**`l10n_py_account` → nuevo módulo `18.0.1.0.0`**:

- Manifest: `countries=['py']`, `auto_install=['account']`,
  `depends=['l10n_py_base', 'account', 'l10n_latam_invoice_document']`.
- PUC RG 49/14 (subset comercio/servicios activo, resto inactive).
- 6 taxes IVA + 1 tax group + modelo `l10n_py.afectacion_iva`.
- 5 records `l10n_latam.document.type` (FE, AF, NC, ND, NR).
- Modelos: `l10n_py.timbrado`, `l10n_py.point_of_emission`,
  `l10n_py.afectacion_iva`.
- Extensiones: `res.company` (`_localization_use_documents()`),
  `account.journal` (PoE + require_emission), `account.move`
  (`_get_starting_sequence`, `_get_last_sequence_domain`, `_post` defensive
  check), `l10n_latam.document.type` (`_format_document_number`).
- Wizard `l10n.py.account.migration.wizard` (clean install / mapeo asistido /
  coexistir).

### 1.2. Por qué dos módulos

- `res.company` vive en módulo `base` → la extensión con campos fiscales no
  requiere `account`. Mantenerlos en `l10n_py_base` permite que un addon
  futuro (ej. CRM PY) consuma RUC + régimen sin instalar contabilidad.
- Patrón validado: `l10n_ec_base` OCA depende de `l10n_ec` core + `account`;
  Odoo core `l10n_ec` depende de `l10n_latam_base` + `l10n_latam_invoice_document`
  - `account`. Mismo split de responsabilidades.

### 1.3. Dependencias (DAG)

```
base ─┬─ contacts ─┬─ base_address_extended ─┐
      │            │                          │
      └─ account ──┴── l10n_latam_base ──────┴── l10n_latam_invoice_document
                                                          │
                                                  l10n_py_base (1.1.0)
                                                          │
                                                  l10n_py_account (1.0.0)
```

## 2. PUC RG 49/14 + Taxes IVA

### 2.1. PUC: estándar de facto paraguayo

**Decisión:** seguir literal la estructura del Anexo de la **Resolución General
DNIT 49/14** (`data/catalogs/_verification/dnit_rg_49_14_anexos.xls`,
hojas "1_Balance General" 232 filas y "2_Estado de Resultados" 181 filas).

No es ley contable (a diferencia de Colombia 2649/93), pero como toda empresa
PY que declara Hechauka debe mapear sus cuentas a esta estructura, es el
estándar operacional. CCPY usa NIIF 2023 IASB sin emitir PUC modelo propio
(verificado en ccpy.org.py/normas-internacionales). Ediciones Técnicas
Paraguayas tiene un libro "Plan de Cuentas" Ayala Mañotti/Paniagua Balbuena
(Vazpi 2009) que sigue la misma estructura — no contradice RG 49/14.

### 2.2. Patrón Odoo 18 — chart_template API moderna

**❗ Odoo 17 rediseñó el framework de chart templates.** No se usan más
records XML de `account.account.template` + `try_loading` en
post_init_hook. El patrón actual:

- **Templates como métodos Python decorados** con `@template('CODE')` en una
  `AbstractModel` que hereda de `account.chart.template`.
- **CSVs ubicados en `data/template/account.account-<code>.csv`** consumidos
  automáticamente por el framework.
- **Hook `_post_load_data(template_code, company, template_data)`** para
  customizaciones post-load.

Patrón verificado en `references/odoo-18.0/addons/l10n_ec/models/template_ec.py`.

### 2.3. Estructura de archivos del PUC

```
addons/l10n_py_account/
├── data/
│   ├── template/
│   │   ├── account.account-py.csv          # PUC RG 49/14 (~200 cuentas)
│   │   ├── account.group-py.csv            # grupos jerárquicos completos
│   │   ├── account.tax-py.csv              # 6 taxes IVA
│   │   ├── account.tax.group-py.csv        # 1 grupo "IVA Paraguay"
│   │   └── account.fiscal.position-py.csv  # placeholder vacío
│   └── l10n_latam.document.type.csv        # 5 docs
└── models/
    └── template_py.py                       # @template('py') decorators
```

### 2.4. `template_py.py` esqueleto

```python
class AccountChartTemplate(models.AbstractModel):
    _inherit = 'account.chart.template'

    @template('py')
    def _get_py_template_data(self):
        return {
            'property_account_receivable_id': 'py_1010301',      # Deudores por Ventas
            'property_account_payable_id': 'py_2010101',         # Proveedores Locales
            'property_account_income_categ_id': 'py_4010101',    # Ventas Mercaderías 10%
            'property_account_expense_categ_id': 'py_5010101',
            'code_digits': 9,  # max length de códigos sin puntos (1.01.03.05.04 → 101030504)
        }

    @template('py', 'res.company')
    def _get_py_res_company(self):
        return {self.env.company.id: {
            'account_fiscal_country_id': 'base.py',
            'account_sale_tax_id': 'tax_iva_venta_10',
            'account_purchase_tax_id': 'tax_iva_compra_10',
            # Los prefijos siguientes son ejemplos basados en RG 49/14;
            # ajustar durante implementación según los códigos finales del CSV.
            'bank_account_code_prefix': '1010104',   # 1.01.01.04 BANCOS
            'cash_account_code_prefix': '1010102',   # 1.01.01.02 CAJA
        }}

    @template('py', 'account.journal')
    def _get_py_account_journal(self):
        return {'sale': {'name': "001-001 Facturación"}}
```

### 2.5. Convención de códigos

- Almacenados **sin puntos**: `'101030503'` para "1.01.03.05.03 IVA Crédito Fiscal".
- `code_digits=9` (longest hierarchy = 9 chars).
- XML ID `py_<código>`: `py_101030503`, `py_2010301`, etc.
- README incluye tabla de mapeo a notación RG 49/14 con puntos (para el contador).

### 2.6. Subset activo por default (~80 cuentas)

Target inicial: comercio minorista/servicios (minimarket, gastronomía,
servicios profesionales). Cuentas activas por grupo:

| Grupo                    | Cuentas activas                                                                                                                                                                                                    |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1.01 Activo Corriente    | Caja, Banco, Fondos fijos, Recaudaciones, Deudores por ventas, IVA Crédito 10/5%, Retenciones IVA crédito, IRP/IRACIS retenido, Mercaderías 10%/5%/exentas, Anticipos a proveedores, Gastos pagados por adelantado |
| 1.02 Activo No Corriente | Inmuebles, Rodados, Muebles/útiles/enseres, Maquinarias, Equipos, Depreciación acumulada (99)                                                                                                                      |
| 2.01 Pasivo Corriente    | Proveedores locales, Préstamos bancos, IVA a Pagar, IRACIS/IRP a pagar, Retenciones a ingresar, Sueldos a pagar, IPS, Aguinaldo a pagar                                                                            |
| 2.02 Pasivo No Corriente | Préstamos largo plazo                                                                                                                                                                                              |
| 3 Patrimonio             | Capital integrado, Reserva legal, Resultados acumulados, Resultado del ejercicio                                                                                                                                   |
| 4 Ingresos               | Ventas mercaderías 10%/5%/exentas, Ventas servicios gravados, Descuentos concedidos (98), Devoluciones (99)                                                                                                        |
| 5 Costos                 | Costo mercaderías gravadas/exentas, Costo servicios                                                                                                                                                                |
| 8 Otros ingresos         | Intereses ganados, Comisiones cobradas, Descuentos obtenidos, Diferencia de cambio                                                                                                                                 |
| 10/11                    | Sueldos ventas, Publicidad, Fletes; Sueldos admin, Alquileres, Servicios (agua/luz/tel), Honorarios, Seguros, Útiles, Impuestos/patentes                                                                           |
| 13                       | Intereses pagados, Comisiones bancarias, Diferencia cambio                                                                                                                                                         |
| 15                       | Depreciaciones del ejercicio, Amortizaciones del ejercicio                                                                                                                                                         |
| 19/20                    | Impuesto a la Renta, Resultado neto                                                                                                                                                                                |

### 2.7. Cuentas creadas pero `active=False` por default

Records existen (estructura completa RG 49/14) pero deshabilitadas para no
contaminar el chart de PyMEs simples. Se activan según industria:

- Grupos 4.02-4.08 (agro: soja, maíz, trigo, ganado, frutícolas, forestales)
- Grupos 5.02-5.08 (costos agro/exportación)
- Grupos 4.10, 5.10 (regímenes especiales: turismo, ZF, maquila)
- `1.01.04.09/10` (activos biológicos en producción/desarrollo)
- `1.01.04.11` (importaciones en curso)
- `1.01.03.05.04` (IVA Crédito Fiscal - Régimen Turismo)
- `1.02.04.97/98` (Ley 60/90, arrendamiento financiero)

### 2.8. Cobertura jerárquica garantizada

**Todos los `account.group` records** se crean (no solo grupos donde hay
cuentas activas). Permite que un usuario agregue `1.01.04.02.05 MERCADERÍAS
RÉGIMEN ESPECIAL CUSTOM` sin armar la jerarquía padre.

### 2.9. Taxes IVA — 6 records

| XML ID                 | Code (sale/purchase) | Name                   | Rate | Type     | Afectación | account_id                |
| ---------------------- | -------------------- | ---------------------- | ---- | -------- | ---------- | ------------------------- |
| `tax_iva_venta_10`     | sale                 | IVA Débito Fiscal 10%  | 10   | sale     | gravado    | `2010301` (IVA a Pagar)   |
| `tax_iva_venta_5`      | sale                 | IVA Débito Fiscal 5%   | 5    | sale     | gravado    | `2010301`                 |
| `tax_iva_venta_exenta` | sale                 | IVA Exenta (ventas)    | 0    | sale     | exento     | —                         |
| `tax_iva_venta_export` | sale                 | IVA 0% Exportación     | 0    | sale     | gravado    | —                         |
| `tax_iva_compra_10`    | purchase             | IVA Crédito Fiscal 10% | 10   | purchase | gravado    | `101030503` (IVA Crédito) |
| `tax_iva_compra_5`     | purchase             | IVA Crédito Fiscal 5%  | 5    | purchase | gravado    | `101030503`               |

**`l10n_py.afectacion_iva`** (modelo nuevo en `l10n_py_account`):

- Carga del CSV `data/catalogs/dnit/afectacion_iva.csv` (4 records: Gravado IVA,
  Exonerado, Exento, Gravado parcial).
- Campos: `code` (Char), `name` (Char).
- Cada `account.tax` PY tiene FK `l10n_py_afectacion_iva_id` (M2O).

**Field adicional en `account.move.line`** (en `l10n_py_account`):

- `l10n_py_iva_proporcion` (Integer 1-100, default 100).
- Marca el caso "Gravado parcial" para el constructor XML de Fase 2.
- No afecta cálculo de tax en Fase 1b.

### 2.10. Fiscal positions

Ninguna por ahora. Placeholder vacío en CSV. Se agregan cuando aparezca el
primer caso de uso real (clientes exterior, régimen turismo).

## 3. Document types + numeración

### 3.1. Códigos verificados contra MT v150

Campo **C002 iTiDE** (Manual Técnico SIFEN v150 p.64): tipo `N 1-2`,
**códigos sin padding** (no `01`, `04`, etc.; literal `1`, `4`, ...). Confirmado
por validaciones del Manual p.169: `C002=1` (FE), `C002=7` (NR).

### 3.2. Los 5 records `l10n_latam.document.type`

| XML ID  | code | name                         | doc_code_prefix | report_name                  | internal_type | sequence |
| ------- | ---- | ---------------------------- | --------------- | ---------------------------- | ------------- | -------- |
| `dt_fe` | `1`  | Factura Electrónica          | `""`            | FACTURA ELECTRÓNICA          | `invoice`     | 10       |
| `dt_af` | `4`  | Autofactura Electrónica      | `""`            | AUTOFACTURA ELECTRÓNICA      | `invoice`     | 20       |
| `dt_nc` | `5`  | Nota de Crédito Electrónica  | `""`            | NOTA DE CRÉDITO ELECTRÓNICA  | `credit_note` | 30       |
| `dt_nd` | `6`  | Nota de Débito Electrónica   | `""`            | NOTA DE DÉBITO ELECTRÓNICA   | `debit_note`  | 40       |
| `dt_nr` | `7`  | Nota de Remisión Electrónica | `""`            | NOTA DE REMISIÓN ELECTRÓNICA | `""` (vacío)  | 50       |

**Notas:**

- `doc_code_prefix=""`: SIFEN no usa prefijo textual en el número visible. El
  `move.name` será `001-001-0000123` puro.
- NR (7) con `internal_type=''`: patrón de `dc_aduana` en `l10n_ar`. Queda
  fuera del filtro normal `_get_l10n_latam_documents_domain`. Futura
  `l10n_py_stock` la consume.
- Autofactura (4) `internal_type='invoice'` asociado a purchase journal (la
  empresa la emite). Patrón análogo a "Liquidación de Compras" Ecuador
  (`references/l10n-ecuador-17.0/.../LiquidacionCompra_V1.0.0.xsd`).
- Tipos "Futuro" (2 export, 3 import, 8 retención): **NO** incluidos en data.
  Documentado en README. Habilitar cuando DNIT los active.

### 3.3. Formato del número: EEE-PPP-NNNNNNN

Verificado MT v150 p.65:

- `C005 dEst` (Establecimiento): tipo `A 3 1-1`, zero-padded a la izquierda.
- `C006 dPunExp` (Punto de Expedición): tipo `A 3 1-1`, zero-padded.
- `C007 dNumDoc` (Número del documento): tipo `A 7 1-1`, zero-padded a 7
  cifras, debe empezar en `0000001` para nuevo timbrado.

### 3.4. Override `_format_document_number`

```python
class L10nLatamDocumentType(models.Model):
    _inherit = 'l10n_latam.document.type'

    def _format_document_number(self, document_number):
        if self.country_id.code != 'PY':
            return super()._format_document_number(document_number)
        if not document_number:
            return document_number
        parts = document_number.split('-')
        if len(parts) != 3:
            raise UserError(_('Formato número PY: EEE-PPP-NNNNNNN (3-3-7 dígitos)'))
        est, poe, num = parts
        if not (est.isdigit() and poe.isdigit() and num.isdigit()):
            raise UserError(_('El número solo puede contener dígitos y guiones'))
        if len(est) > 3 or len(poe) > 3 or len(num) > 7:
            raise UserError(_('Máximo EEE=3, PPP=3, NNNNNNN=7 dígitos'))
        return f"{est:>03s}-{poe:>03s}-{num:>07s}"
```

Normaliza `1-1-123` → `001-001-0000123`.

### 3.5. Mapeo internal_type → journal_type

- `sale` journal: invoice → FE (1), credit_note → NC (5), debit_note → ND (6).
- `purchase` journal:
  - invoice → FE (1) recibida del proveedor (manual numbering)
  - invoice → AF (4) emitida por nosotros — **en Fase 1b: manual numbering**;
    auto-numbering con PoE propio se difiere a Fase 2 cuando exista flujo real
    de emisión (firma + SIFEN). El compute `l10n_py_require_emission` queda
    solo para `type=='sale'` en 1b.
  - credit_note → NC (5) recibida del proveedor (manual numbering)
  - debit_note → ND (6) recibida del proveedor (manual numbering)

**Manual vs auto:**

- Sale journals: auto-numbered (Odoo genera con sequence + override `_get_starting_sequence`).
- Purchase journals: **todos manual en Fase 1b**
  (`_is_manual_document_number` override retorna True para PY purchase). El
  contribuyente carga el número del DTE: si es recibido del proveedor, lo
  copia del comprobante; si es AF que emitimos nosotros, lo gestiona
  externamente hasta que Fase 2 introduzca auto-numbering con PoE propio para
  AF.

### 3.6. Constraint EEE-PPP coincide con PoE del journal

**Diferido a Fase 2.** En 1b confiamos en la captura del usuario. En Fase 2
con XML builder cargado se valida que el número manual matchee el PoE
correspondiente.

## 4. Timbrado + PoE + journal extensions

### 4.1. Hechos del Manual Técnico v150 (p.60-65)

- **Timbrado es por contribuyente (company), no por journal/PoE.** Un solo
  `dNumTim` (8 dígitos numéricos) por DE.
- "El timbrado no manejará una fecha de fin de vigencia" (p.60). Los campos
  `C008 dFeIniT` / `C009 dFeFinT` siguen existiendo (`A 10 1-1` cada uno) pero
  operacionalmente DNIT moderno no fuerza fecha fin — usa **serie alfabética**
  cuando se agota la numeración 9.999.999.
- Serie: 2 letras mayúsculas, range AA-ZZ excluyendo Ñ. Permitida solo cuando
  se agota la numeración del par (estab, punto, doc_type).
- Numeración por combinación (timbrado, establecimiento, punto, tipo_doc,
  serie). Empieza en `0000001` para nuevo timbrado.

### 4.2. Modelo `l10n_py.timbrado`

```python
class L10nPyTimbrado(models.Model):
    _name = 'l10n_py.timbrado'
    _description = 'Paraguay - Timbrado DNIT'

    name = fields.Char(string='Número', required=True, size=8,
                       help='8 dígitos otorgados por DNIT (MT v150 C004 dNumTim)')
    date_from = fields.Date(string='Vigencia desde', required=True,
                            help='MT v150 C008 dFeIniT')
    date_to = fields.Date(string='Vigencia hasta',
                          help='MT v150 C009 dFeFinT. Vacío = indefinido')
    company_id = fields.Many2one('res.company', required=True,
                                  default=lambda s: s.env.company)
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('active', 'Vigente'),
        ('expired', 'Vencido'),
    ], default='draft', required=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Timbrado único por empresa'),
    ]

    @api.constrains('state', 'company_id')
    def _check_single_active(self):
        for rec in self.filtered(lambda r: r.state == 'active'):
            others = self.search([
                ('company_id', '=', rec.company_id.id),
                ('state', '=', 'active'),
                ('id', '!=', rec.id),
            ])
            if others:
                raise ValidationError(_('Solo puede haber un timbrado vigente por empresa.'))

    @api.constrains('name')
    def _check_name_format(self):
        for rec in self:
            if not (rec.name and rec.name.isdigit() and len(rec.name) == 8):
                raise ValidationError(_('El timbrado debe ser exactamente 8 dígitos.'))
```

**Serie alfabética**: TODO documentado en módulo + en Fase 2 roadmap.

### 4.3. Modelo `l10n_py.point_of_emission`

```python
class L10nPyPointOfEmission(models.Model):
    _name = 'l10n_py.point_of_emission'
    _description = 'Paraguay - Punto de Emisión'

    name = fields.Char(compute='_compute_name', store=True)
    establishment_code = fields.Char(string='Establecimiento', required=True, size=3,
                                      help='MT v150 C005 dEst — 3 dígitos zero-padded')
    code = fields.Char(string='Punto de Expedición', required=True, size=3,
                       help='MT v150 C006 dPunExp — 3 dígitos zero-padded')
    address_id = fields.Many2one('res.partner', string='Dirección física',
                                  required=True,
                                  domain="['|', ('id', '=', company_partner_id),"
                                         "('parent_id', '=', company_partner_id)]",
                                  help='Dirección física de la sucursal. Va al XML del DE.')
    company_id = fields.Many2one('res.company', required=True,
                                  default=lambda s: s.env.company)
    company_partner_id = fields.Many2one(related='company_id.partner_id')
    journal_ids = fields.One2many('account.journal', 'l10n_py_point_of_emission_id')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('estab_point_uniq',
         'unique(company_id, establishment_code, code)',
         'Ya existe un punto de emisión con ese establecimiento + punto'),
    ]

    @api.depends('establishment_code', 'code')
    def _compute_name(self):
        for rec in self:
            rec.name = f"{(rec.establishment_code or '').zfill(3)}-{(rec.code or '').zfill(3)}"

    @api.constrains('establishment_code', 'code')
    def _check_codes_numeric(self):
        for rec in self:
            for val, fld in [(rec.establishment_code, 'establecimiento'),
                             (rec.code, 'punto de expedición')]:
                if not (val and val.isdigit() and len(val) <= 3):
                    raise ValidationError(_('Código de %s: 1-3 dígitos numéricos', fld))
```

### 4.4. Extensión `res.company` (en `l10n_py_account`)

```python
class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_py_timbrado_ids = fields.One2many('l10n_py.timbrado', 'company_id')
    l10n_py_active_timbrado_id = fields.Many2one(
        'l10n_py.timbrado',
        compute='_compute_l10n_py_active_timbrado',
        help='Timbrado actualmente vigente (state=active)',
    )

    def _compute_l10n_py_active_timbrado(self):
        for company in self:
            company.l10n_py_active_timbrado_id = self.env['l10n_py.timbrado'].search([
                ('company_id', '=', company.id),
                ('state', '=', 'active'),
            ], limit=1)

    def _localization_use_documents(self):
        self.ensure_one()
        return (self.account_fiscal_country_id.code == 'PY'
                or super()._localization_use_documents())
```

### 4.5. Extensión `account.journal` (en `l10n_py_account`)

```python
class AccountJournal(models.Model):
    _inherit = 'account.journal'

    l10n_py_point_of_emission_id = fields.Many2one(
        'l10n_py.point_of_emission',
        string='Punto de Emisión',
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )
    l10n_py_require_emission = fields.Boolean(
        compute='_compute_l10n_py_require_emission',
        help='True si el journal debe tener PoE (sale + PY + use_documents)',
    )

    @api.depends('type', 'country_code', 'l10n_latam_use_documents')
    def _compute_l10n_py_require_emission(self):
        for journal in self:
            journal.l10n_py_require_emission = (
                journal.type == 'sale'
                and journal.country_code == 'PY'
                and journal.l10n_latam_use_documents
            )

    @api.constrains('l10n_py_point_of_emission_id', 'type', 'country_code',
                    'l10n_latam_use_documents')
    def _check_py_point_of_emission(self):
        for j in self.filtered(lambda x: x.l10n_py_require_emission):
            if not j.l10n_py_point_of_emission_id:
                raise ValidationError(_(
                    'Los journals de ventas paraguayos con documentos requieren un '
                    'Punto de Emisión.'))

    @api.constrains('l10n_py_point_of_emission_id', 'l10n_latam_use_documents')
    def _check_py_poe_requires_use_documents(self):
        for j in self.filtered(lambda x: x.l10n_py_point_of_emission_id):
            if not j.l10n_latam_use_documents:
                raise ValidationError(_(
                    'Un journal con Punto de Emisión PY debe tener "Usar Documentos" '
                    'habilitado.'))
```

### 4.6. Extensión `account.move` — sequence + defensive

```python
class AccountMove(models.Model):
    _inherit = 'account.move'

    def _get_starting_sequence(self):
        self.ensure_one()
        if (self.journal_id.country_code == 'PY'
                and self.journal_id.l10n_latam_use_documents):
            poe = self.journal_id.l10n_py_point_of_emission_id
            if not poe:
                raise UserError(_(
                    "El journal '%(journal)s' usa documentos paraguayos pero no tiene "
                    "Punto de Emisión configurado. Configure el PoE en Configuración → "
                    "Contabilidad → Diarios antes de postear documentos.",
                    journal=self.journal_id.name,
                ))
            return f"{poe.establishment_code.zfill(3)}-{poe.code.zfill(3)}-0000000"
        return super()._get_starting_sequence()

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super()._get_last_sequence_domain(relaxed)
        if (self.company_id.account_fiscal_country_id.code == 'PY'
                and self.l10n_latam_use_documents):
            where_string += " AND l10n_latam_document_type_id = %(l10n_latam_document_type_id)s"
            param['l10n_latam_document_type_id'] = self.l10n_latam_document_type_id.id or 0
        return where_string, param

    def _post(self, soft=True):
        for move in self.filtered(
            lambda m: m.company_id.account_fiscal_country_id.code == 'PY'
                      and m.l10n_latam_use_documents
        ):
            if not move.journal_id.l10n_py_point_of_emission_id:
                raise UserError(_(
                    "El diario '%(journal)s' no tiene Punto de Emisión configurado.",
                    journal=move.journal_id.name,
                ))
        return super()._post(soft=soft)
```

El `_get_last_sequence_domain` override es **crítico**: sin él, FE y NC
comparten numeración en el mismo journal (bug grave SIFEN — cada `(timbrado,
estab, punto, doc_type)` debe tener correlativo independiente).

### 4.7. Auto-activación de `l10n_latam_use_documents`

**Ocurre SOLO al cargar el chart `py`** (vía `try_loading('py', company)` o
durante setup inicial via wizard de migración). El framework
`l10n_latam_invoice_document/models/account_chart_template.py:10-16` ejecuta
`_get_latam_document_account_journal` con context del chart, y si
`company._localization_use_documents()` retorna True (nuestro override lo hace
para PY), setea `l10n_latam_use_documents=True` en los journals
sale/purchase **que el chart crea en ese momento**.

Implicaciones:

- Si el chart se carga en company nueva: journals sale/purchase nacen con
  `use_documents=True`. ✅
- Si el módulo `l10n_py_account` se actualiza con `-u` después de instalado:
  el chart NO se recarga, journals existentes no se tocan. Si se agregaron
  journals manualmente entre installs, el admin debe activar `use_documents`
  a mano (o re-disparar el chart desde el wizard).
- DBs preexistentes con chart custom: `_post_init_hook` desactiva
  `use_documents` en sale journals PY sin PoE (sec 4.8). Wizard de migración
  ayuda a reconfigurar.

### 4.8. Hook `_post_init_hook` defensivo

```python
def _post_init_hook(env):
    """Maneja DBs preexistentes con journals legacy."""
    py_companies = env['res.company'].search([
        ('account_fiscal_country_id.code', '=', 'PY'),
    ])
    for company in py_companies:
        # Caso A: journals sale PY con use_documents=True pero sin PoE
        broken_journals = env['account.journal'].search([
            ('company_id', '=', company.id),
            ('type', '=', 'sale'),
            ('l10n_latam_use_documents', '=', True),
            ('l10n_py_point_of_emission_id', '=', False),
        ])
        if broken_journals:
            broken_journals.write({'l10n_latam_use_documents': False})
            for journal in broken_journals:
                journal.activity_schedule(
                    'mail.mail_activity_data_todo',
                    summary=_('Configurar Punto de Emisión Paraguay'),
                    note=_('Este journal requiere PoE para emitir documentos PY. '
                           'Configure el PoE y reactive "Usar Documentos".'),
                    user_id=env.user.id,
                )

        # Caso B: company PY ya tiene chart cargado distinto al 'py'
        chart = company.chart_template
        existing_accounts = env['account.account'].search_count([
            ('company_id', '=', company.id),
        ])
        if chart and chart != 'py' and existing_accounts > 20:
            _logger.warning(
                "Company %s tiene chart '%s' con %d cuentas. l10n_py_account NO "
                "cargó el chart 'py' automáticamente. Use el wizard de migración.",
                company.name, chart, existing_accounts,
            )
```

## 5. Testing + entregables + Definition of Done

### 5.1. Patrón de tests

Todos en `addons/l10n_py_account/tests/`. `TransactionCase` + `@tagged('post_install', '-at_install')`. Fixture compartido en `tests/common.py`:

```python
class L10nPyAccountTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env['res.company'].create({
            'name': 'Empresa Test PY',
            'country_id': cls.env.ref('base.py').id,
        })
        cls.env['account.chart.template'].try_loading('py', company=cls.company)
        cls.timbrado = cls.env['l10n_py.timbrado'].create({
            'name': '12345678',
            'date_from': '2026-01-01',
            'state': 'active',
            'company_id': cls.company.id,
        })
        cls.poe = cls.env['l10n_py.point_of_emission'].create({
            'establishment_code': '001',
            'code': '001',
            'address_id': cls.company.partner_id.id,
            'company_id': cls.company.id,
        })
        cls.sale_journal = cls.env['account.journal'].search([
            ('type', '=', 'sale'), ('company_id', '=', cls.company.id),
        ], limit=1)
        cls.sale_journal.l10n_py_point_of_emission_id = cls.poe
```

### 5.2. Tests por área

| Archivo                              | Cubre                                                                                                                                         | Tests    |
| ------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `test_chart_template.py`             | Carga PUC; ~80 activas + ~200 totales; account.group jerárquico completo                                                                      | 8        |
| `test_hechauka_critical_accounts.py` | Lista hardcoded de ~25 códigos RG 49/14 obligatorios para Hechauka — todos existen                                                            | 1 (loop) |
| `test_taxes.py`                      | 6 taxes IVA cableados a cuentas correctas; afectacion FK; computo monto                                                                       | 10       |
| `test_document_types.py`             | 5 records cargados; `_format_document_number` normaliza/rechaza; filtro domain por journal+partner                                            | 12       |
| `test_timbrado.py`                   | Single-active; formato 8 dígitos; transición state; date_to opcional                                                                          | 8        |
| `test_point_of_emission.py`          | Unique (company, est, point); validación numérica; compute name; domain address                                                               | 6        |
| `test_journal_extension.py`          | Constraint PoE requerido + bidireccional (PoE↔use_documents); auto-set use_documents                                                         | 7        |
| `test_account_move_sequence.py`      | FE numera `001-001-0000001`, 2ª FE `0000002`; NC en mismo journal arranca de `0000001` (sequence independiente); doc_type change resetea name | 8        |
| `test_account_move_defensive.py`     | Postear sin PoE → UserError con mensaje claro; postear con PoE OK                                                                             | 3        |
| `test_company_extension.py`          | `_localization_use_documents()` True para PY; `l10n_py_active_timbrado_id` compute                                                            | 4        |
| `test_pyme_e2e.py`                   | Smoke test: compra+venta+cierre mes; balance IVA Débito-Crédito = IVA a Pagar                                                                 | 1        |
| `test_post_init_hook.py`             | Legacy journal sin PoE → desactiva use_documents + crea activity; chart custom preexistente → warning, no rompe                               | 2        |
| `test_migration_wizard.py`           | Wizard 3 modos: clean install / mapeo asistido / coexistir                                                                                    | 3        |

**Total: ~73 tests** en `l10n_py_account`.

`l10n_py_base` (bump 1.1.0) agrega:
| Archivo | Cubre | Tests |
|---|---|---|
| `test_company_setup.py` | Campos `l10n_py_*` en company; validación RUC módulo 11; DV computed | 4 |
| `test_economic_activity.py` | CRUD modelo; menú accesible; carga manual | 2 |

**Total: 6 tests adicionales** en `l10n_py_base` → suma proyecto = 21 + 6 + 73 = **100 tests**.

### 5.3. Entregables

**PR 1: `l10n_py_base` → 1.1.0** (branch `feat/l10n-py-base-company`)

- Modelo `l10n_py.economic_activity` + UI carga manual + 2 records demo.
- Extensión `res.company` (5 campos + validación RUC).
- Views: company form section + economic activity views + menu.
- 6 tests nuevos.
- `CHANGES.rst` actualizado.
- README actualizado (sección "What's new in 1.1.0").

**PR 2: `l10n_py_account` 18.0.1.0.0** (branch `feat/l10n-py-account`)

- Manifest + estructura completa Odoo 18 chart template API.
- Data: PUC RG 49/14 CSV + groups + 6 taxes + 5 document types + afectacion_iva.
- Modelos nuevos: `l10n_py.timbrado`, `l10n_py.point_of_emission`,
  `l10n_py.afectacion_iva`.
- Extensiones: `res.company`, `account.journal`, `account.move`,
  `l10n_latam.document.type`, `account.move.line` (`l10n_py_iva_proporcion`).
- Wizard `l10n.py.account.migration.wizard` (3 modos).
- Views completas (timbrado, PoE, journal extension, move extension, migration
  wizard, menus).
- Security: grupo `group_l10n_py_account_user` + ACLs todos los modelos nuevos.
- 73 tests.
- README OCA-style (DESCRIPTION, CONFIGURE, USAGE, ROADMAP, "Cobertura por
  industria", "Configuración inicial post-install", "Migración desde chart
  custom").
- `CHANGES.rst` inicial.

### 5.4. Definition of Done

1. ✅ `python -m pytest addons/l10n_py_base addons/l10n_py_account -v` → 100 tests verdes.
2. ✅ Instalación limpia DB nueva: `docker compose exec odoo odoo -i l10n_py_account -d test_py_account --stop-after-init` sin warnings/tracebacks.
3. ✅ Demo data: company PY + timbrado active + PoE + partner local CI válido + producto con tax IVA 10% → crear FE → postear → `move.name == "001-001-0000001"`.
4. ✅ Crear NC referenciando esa FE → `move.name == "001-001-0000001"` (intencional: la NC tiene sequence independiente por doc_type — FE y NC arrancan ambas en 0000001 dentro del mismo journal, no se pisan porque el override `_get_last_sequence_domain` filtra por `l10n_latam_document_type_id`), `reversed_entry_id` apunta a la FE.
5. ✅ Pre-commit limpio en ambos módulos.
6. ✅ README OCA-style ambos módulos.
7. ✅ Conventional Commits, branches `feat/l10n-py-base-company` y `feat/l10n-py-account` mergeadas a `dev`.
8. ✅ Sin gate de contador. PUC se ajusta vía patches `18.0.1.0.x` cuando
   feedback del primer uso real (interno o cliente beta) detecte gaps.
   Tracking en `BUGS_BACKLOG.md` o issues GitHub.

### 5.5. Cronograma estimado

- PR1 (base 1.1.0): 3-5 días.
- PR2 (account): 12-18 días (PUC + groups CSVs es lo más laborioso).
- Sin gate externo. Patches post-release según feedback.

Total Fase 1b: ~3 semanas calendario.

## 6. Riesgos y mitigaciones

### Riesgo 1 — PUC RG 49/14 incompleto para industrias específicas

**Mitigaciones:**

1. Cobertura jerárquica completa (todos los `account.group` records aunque las cuentas hoja estén inactive).
2. Test `test_hechauka_critical_accounts.py` con ~25 códigos obligatorios hardcoded.
3. Smoke test `test_pyme_e2e.py` con operación real (compra+venta+cierre).
4. Matriz de cobertura por industria en README (verificable, no aspiracional).
5. **Iteración por feedback post-release**: shipping sin gate de contador.
   El primer uso real (interno o cliente beta) detecta gaps; ajustes salen en
   patches `18.0.1.0.1`, `1.0.2`, etc. Aceptamos el riesgo de que cuentas
   faltantes se descubran en producción a cambio de no bloquear cronograma de
   Fase 2 (EDI/SIFEN).

### Riesgo 2 — `_get_starting_sequence` falla con journals sin PoE

**Mitigaciones:**

1. Defensive check explícito en `_get_starting_sequence` con `UserError` claro y accionable.
2. Constraint en `account.move._post()` (validación temprana antes de generar name).
3. Constraint bidireccional en `account.journal` (PoE↔use_documents).
4. Hook `_post_init_hook` desactiva use_documents en journals legacy sin PoE + crea `mail.activity` notificando admin.
5. Tests específicos: `test_move_post_without_poe_raises_clear_error`, `test_post_init_handles_legacy_journals`.

### Riesgo 3 — `use_documents` interfiere con DBs con chart custom

**Mitigaciones:**

1. Detección pre-load en `@template('py')`: warning si company tiene >20 cuentas preexistentes.
2. Wizard de migración 3 modos (clean install / mapeo asistido / coexistir) — el admin elige.
3. `_post_init_hook` loguea warning + crea activity si detecta chart distinto.
4. README sección "Migración desde chart custom" con matriz paso a paso.
5. Test `test_install_on_company_with_existing_accounts`.

### Riesgo 4 — API `account.chart.template` cambia en Odoo 19

**Mitigación:** fuera de scope. Cuando salga Odoo 19 se migra (al menos 12 meses por delante).

## 7. Fuentes verificadas

- **Manual Técnico SIFEN v150** (`docs/original/sifen_manual_tecnico_v150.pdf`):
  - p.60-61 "Manejo del timbrado y Numeración" (serie alfabética).
  - p.64 campo C002 iTiDE (códigos `1, 4, 5, 6, 7` sin padding).
  - p.65 campos C004-C010 (timbrado 8 dígitos, dEst/dPunExp 3 chars, dNumDoc 7 chars zero-padded).
  - p.169 validaciones E010/E012 (confirma `C002=1` formato).
- **Resolución General DNIT 49/14 Anexos**
  (`data/catalogs/_verification/dnit_rg_49_14_anexos.xls`):
  - Hoja "1_Balance General" 232 filas.
  - Hoja "2_Estado de Resultados" 181 filas.
  - Cuentas IVA exactas: `1.01.03.05.02` Retenciones IVA, `1.01.03.05.03` IVA-Crédito, `2.01.03.01.02` IVA a Pagar.
- **Odoo 18 core**:
  - `references/odoo-18.0/addons/l10n_ec/models/template_ec.py` (patrón `@template`).
  - `references/odoo-18.0/addons/l10n_ec/models/account_journal.py` (PoE pattern).
  - `references/odoo-18.0/addons/l10n_ar/models/account_move.py:267-280` (`_get_starting_sequence` + `_get_last_sequence_domain`).
  - `references/odoo-18.0/addons/l10n_ar/data/l10n_latam.document.type.csv` (patrón `dc_aduana` con `internal_type=''`).
  - `references/odoo-18.0/addons/l10n_latam_invoice_document/models/account_chart_template.py:10-16` (auto-set `use_documents`).
  - `references/odoo-18.0/addons/l10n_latam_invoice_document/models/res_company.py:9` (`_localization_use_documents`).
  - `references/odoo-18.0/addons/account/models/account_journal.py:134` (`country_code` field).
- **OCA Ecuador 17.0** (`references/l10n-ecuador-17.0/`):
  - `l10n_ec_base/__manifest__.py` (patrón split base/account).
  - `l10n_ec_account_edi/data/xsd/LiquidacionCompra_V1.0.0.xsd` (referencia autofactura).
- **CCPY** (https://www.ccpy.org.py/normas-internacionales): Paraguay usa NIIF 2023 IASB; sin PUC modelo emitido por CCPY.
- **Catálogos DNIT** (`data/catalogs/dnit/`): afectacion_iva (4 records), tipo_documento (D208 — receptor, no confundir con C002 iTiDE).

## 8. Decisiones de scope (consolidado)

| Decisión                         | Resolución                                                    |
| -------------------------------- | ------------------------------------------------------------- |
| PUC estrategia                   | A2 anclado a RG 49/14 (estándar de facto paraguayo)           |
| `res.company` extension          | En `l10n_py_base` 1.1.0 (campos identidad fiscal)             |
| `_localization_use_documents`    | En `l10n_py_account` (depende de l10n_latam_invoice_document) |
| CDC field/algoritmo              | Todo en `l10n_py_edi` (Fase 2)                                |
| Códigos documento                | `1, 4, 5, 6, 7` sin padding (verificado MT v150)              |
| NR (7) `internal_type`           | Vacío (patrón `dc_aduana`); futura `l10n_py_stock` la consume |
| Tipos "Futuro" (2, 3, 8)         | No incluidos en data                                          |
| Autofactura (4)                  | Purchase journal, sequence propia, `internal_type='invoice'`  |
| Timbrado fields                  | `name` (8 chars), `date_from` requerido, `date_to` opcional   |
| Single active timbrado           | Constraint sí (convención DNIT operacional)                   |
| Serie alfabética timbrado        | TODO Fase 2                                                   |
| Journal-PoE relación             | 1:1 (un journal = un PoE) — patrón Ecuador                    |
| Sequence per (journal, doc_type) | Sí, vía `_get_last_sequence_domain` override                  |
| code_digits PUC                  | 9 (cuentas sin puntos, max length de jerarquía)               |
| Contador gate                    | Sin gate. Iteración por feedback post-release (patches 1.0.x) |
