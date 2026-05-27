---
source: Extracted from ÑandeFact CLAUDE.md section "MODELO DE DATOS (PostgreSQL)"
fetched_at: 2026-05-19
summary: Schema PostgreSQL de ÑandeFact como REFERENCIA (no destino). En Odoo se mapea a extensiones de modelos existentes — esta tabla traduce cada tabla nativa al modelo Odoo equivalente.
priority: reference
---

# Modelo de Datos — referencia ÑandeFact → mapeo Odoo

> **IMPORTANTE — leer antes de implementar nada:** El schema PostgreSQL que sigue
> es de **ÑandeFact (Node.js+TS)** y se incluye como referencia conceptual del
> dominio. En Odoo NO replicamos este schema tal cual: el ORM y los addons
> existentes (`account`, `res.partner`, `res.company`, `account.edi.document`)
> ya proveen ~80% de las tablas. Solo agregamos campos faltantes vía `_inherit`
> y creamos modelos nuevos cuando NO hay equivalente en core.

## 1. Tabla de equivalencias rápida

| Tabla PostgreSQL ÑandeFact      | Modelo Odoo equivalente                    | ¿Crear nuevo o extender?                                                                     |
| ------------------------------- | ------------------------------------------ | -------------------------------------------------------------------------------------------- |
| `comercio`                      | `res.company`                              | Extender (campos SIFEN)                                                                      |
| `usuario`                       | `res.users`                                | Extender (PIN opcional para POS)                                                             |
| `producto`                      | `product.product` + `product.template`     | Extender (unidad medida SIFEN)                                                               |
| `cliente`                       | `res.partner`                              | Extender (ya tiene `vat`, agregar `l10n_latam_identification_type_id` vía `l10n_latam_base`) |
| `factura`                       | `account.move` (filtrado por `move_type`)  | Extender (CDC, KuDE, etc)                                                                    |
| `factura_detalle`               | `account.move.line`                        | Extender (`l10n_py_iva_*`)                                                                   |
| `sync_queue`                    | `account.edi.document` + `queue.job` (OCA) | Ya existe (no replicar)                                                                      |
| `usuario_pin` (custom para POS) | `res.users` (`l10n_py_pin_hash` opcional)  | Extender solo si POS requiere                                                                |

## 2. Schema ÑandeFact (referencia conceptual)

> El SQL que sigue es de ÑandeFact tal cual está en el repo previo. No es lo que
> escribimos en Odoo — es lo que las **entidades de dominio** exigen, traducido a
> SQL. Se conserva como referencia.

```sql
-- ============================
-- Comercio  →  Odoo: res.company
-- ============================
comercio (
    id UUID PK,
    nombre VARCHAR(200),
    ruc VARCHAR(20) UNIQUE,
    razon_social VARCHAR(200),
    nombre_fantasia VARCHAR(200),
    establecimiento VARCHAR(3),         -- → en Odoo va a l10n_py.point_of_emission
    punto_expedicion VARCHAR(3),        -- → idem
    timbrado VARCHAR(15),               -- → en Odoo va a l10n_py.timbrado
    timbrado_fecha_inicio DATE,
    timbrado_fecha_fin DATE,
    direccion TEXT,                     -- → res.partner.street (company tiene partner_id)
    numero_casa VARCHAR(10),
    departamento INT,                   -- → l10n_py.department (FK)
    distrito INT,                       -- → l10n_py.district (FK)
    ciudad INT,                         -- → l10n_py.city (FK)
    telefono VARCHAR(20),
    email VARCHAR(200),
    rubro VARCHAR(100),
    actividad_economica_codigo VARCHAR(10),  -- → l10n_py.economic_activity (FK, m2m)
    actividad_economica_desc VARCHAR(200),
    tipo_contribuyente INT,             -- 1=PF, 2=PJ → res.company.l10n_py_tipo_contribuyente
    tipo_regimen INT,                   -- → l10n_py.tax_regime (FK)
    zona_mercado VARCHAR(50),
    ccfe_certificado BYTEA,             -- Encriptado AES-256
    ccfe_clave BYTEA,                   -- Encriptado AES-256
    csc VARCHAR(64),                    -- CSC encriptado
    csc_id VARCHAR(10),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- Usuario  →  Odoo: res.users (PIN opcional para POS)
-- ============================
usuario (
    id UUID PK,
    comercio_id UUID FK → comercio,
    nombre VARCHAR(100),
    telefono VARCHAR(20) UNIQUE,
    pin_hash VARCHAR(256),              -- PIN 4-6 dígitos hasheado
    rol ENUM('dueño', 'empleado'),
    activo BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
-- Odoo: el login es por usuario+password estándar; PIN solo si se hace módulo
-- l10n_py_pos con campo `l10n_py_pin_hash` en res.users.

-- ============================
-- Producto  →  Odoo: product.template + product.product
-- ============================
producto (
    id UUID PK,
    comercio_id UUID FK → comercio,     -- → product.template.company_id
    nombre VARCHAR(200),                 -- → product.template.name
    codigo VARCHAR(50),                  -- → product.template.default_code
    precio_unitario BIGINT,              -- → product.template.list_price (Float)
    unidad_medida VARCHAR(10),           -- → product.template.uom_id + l10n_py_unit_measure (SIFEN code)
    iva_tipo ENUM('10%', '5%', 'exenta'),-- → product.template.taxes_id (account.tax)
    categoria VARCHAR(100),              -- → product.category_id
    activo BOOLEAN DEFAULT true,         -- → product.template.active
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- Cliente  →  Odoo: res.partner
-- ============================
cliente (
    id UUID PK,
    comercio_id UUID FK → comercio,
    nombre VARCHAR(200),                 -- → res.partner.name
    ruc_ci VARCHAR(20),                  -- → res.partner.vat
    tipo_documento ENUM('RUC','CI','pasaporte','innominado'),
                                          -- → res.partner.l10n_latam_identification_type_id
    telefono VARCHAR(20),                -- → res.partner.phone
    email VARCHAR(200),                  -- → res.partner.email
    direccion TEXT,                      -- → res.partner.street
    frecuente BOOLEAN DEFAULT false,    -- → no se replica; query por uso es OK
    enviar_whatsapp BOOLEAN DEFAULT true,-- → res.partner.l10n_py_enviar_whatsapp (si se hace POS)
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- Factura  →  Odoo: account.move (move_type in invoice/refund) + account.edi.document
-- ============================
factura (
    id UUID PK,
    comercio_id UUID FK → comercio,     -- → account.move.company_id
    usuario_id UUID FK → usuario,        -- → account.move.create_uid o invoice_user_id
    cliente_id UUID FK → cliente,        -- → account.move.partner_id

    -- Datos SIFEN (→ account.move + l10n_py_edi)
    cdc VARCHAR(44) UNIQUE,              -- → account.move.l10n_py_cdc
    numero BIGINT,                       -- → l10n_latam_invoice_document.l10n_latam_document_number
    tipo_documento INT,                  -- → l10n_latam_invoice_document.l10n_latam_document_type_id
    establecimiento VARCHAR(3),          -- → account.journal.l10n_py_establishment (via journal_id)
    punto_expedicion VARCHAR(3),         -- → account.journal.l10n_py_point_of_emission

    -- Montos (en Odoo: ya calculados por account.move + account.tax)
    total_bruto BIGINT,                  -- → account.move.amount_untaxed (en Float, no BIGINT)
    total_iva_10 BIGINT,                 -- → computed desde tax_totals
    total_iva_5 BIGINT,                  -- → computed desde tax_totals
    total_exenta BIGINT,                 -- → computed desde tax_totals
    total_iva BIGINT,                    -- → account.move.amount_tax
    total_neto BIGINT,                   -- → account.move.amount_total

    -- Condición de pago
    condicion_pago ENUM('contado','credito'),  -- → account.move.invoice_payment_term_id + helper l10n_py_condicion_pago

    -- Estado SIFEN (→ account.edi.document.state)
    estado_sifen ENUM('pendiente','enviado','aprobado','rechazado','contingencia'),
    sifen_respuesta TEXT,                -- → account.edi.document.error (parcial) + ir.attachment con XML respuesta
    sifen_codigo_respuesta VARCHAR(10),  -- → custom field si se necesita filtrar (l10n_py_sifen_response_code)
    sifen_fecha_envio TIMESTAMP,
    sifen_fecha_aprobacion TIMESTAMP,

    -- Envío cliente
    whatsapp_enviado BOOLEAN DEFAULT false,  -- → opcional, solo si hay módulo WhatsApp
    whatsapp_fecha TIMESTAMP,

    -- PDF KuDE → ir.attachment ligado al move
    kude_pdf_path VARCHAR(500),

    -- Sync offline (Odoo no necesita esto si está siempre online; relevante si
    -- se implementa un POS offline-first con queue local)
    sync_id UUID,
    created_offline BOOLEAN DEFAULT false,
    synced_at TIMESTAMP,

    -- Nota de crédito referencia
    factura_referencia_id UUID FK → factura NULL,  -- → account.move.reversed_entry_id (core)

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================
-- Detalle Factura  →  Odoo: account.move.line (con extensiones)
-- ============================
factura_detalle (
    id UUID PK,
    factura_id UUID FK → factura,        -- → account.move.line.move_id
    producto_id UUID FK → producto,      -- → account.move.line.product_id
    descripcion VARCHAR(200),            -- → account.move.line.name
    cantidad BIGINT,                     -- → account.move.line.quantity (Float)
    precio_unitario BIGINT,              -- → account.move.line.price_unit (Float)
    subtotal BIGINT,                     -- → account.move.line.price_subtotal (computed)
    iva_tipo INT,                        -- → l10n_py_iva_tipo (Selection: 'gravado'/'parcial'/'exento')
    iva_tasa INT,                        -- → derivable de account.move.line.tax_ids
    iva_proporcion INT DEFAULT 100,      -- → l10n_py_iva_proporcion (Integer 1-100)
    iva_base BIGINT,                     -- → computed o price_subtotal según tipo
    iva_monto BIGINT                     -- → computed
);

-- ============================
-- Cola de Sincronización  →  Odoo: account.edi.document + (opcional) queue.job de OCA
-- ============================
sync_queue (
    id UUID PK,
    comercio_id UUID FK → comercio,
    tipo ENUM('factura','evento'),
    payload JSONB,
    estado ENUM('pendiente','procesando','completado','error'),
    intentos INT DEFAULT 0,
    max_intentos INT DEFAULT 5,
    ultimo_error TEXT,
    proximo_intento TIMESTAMP,           -- backoff exponencial
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP
);
-- Odoo: NO replicar. El framework account.edi.document ya maneja:
--   - estado: state ('to_send', 'sent', 'cancel', 'to_cancel')
--   - reintentos: blocking_level + retry via cron
--   - payload: attachment_id (XML) + edi_format_id
-- Si se quiere paralelismo / prioridades: instalar OCA queue_job.
```

## 3. Modelos NUEVOS a crear en Odoo

Los siguientes modelos NO tienen equivalente directo en core y se crean en
`l10n_py_*`:

### En `l10n_py_base`

```python
# Catálogos SIFEN
class L10nPyDepartment(models.Model):
    _name = 'l10n_py.department'
    _description = 'Paraguay - Departamento'
    code = fields.Integer(required=True)        # 1-17 (SIFEN catalog)
    name = fields.Char(required=True)
    _sql_constraints = [('code_uniq', 'unique(code)', 'Department code must be unique')]

class L10nPyDistrict(models.Model):
    _name = 'l10n_py.district'
    code = fields.Integer(required=True)
    name = fields.Char(required=True)
    department_id = fields.Many2one('l10n_py.department', required=True)

class L10nPyCity(models.Model):
    _name = 'l10n_py.city'
    code = fields.Integer(required=True)
    name = fields.Char(required=True)
    district_id = fields.Many2one('l10n_py.district', required=True)

class L10nPyEconomicActivity(models.Model):
    _name = 'l10n_py.economic_activity'
    code = fields.Char(required=True)           # ej: '1254'
    name = fields.Char(required=True)

class L10nPyTaxRegime(models.Model):
    _name = 'l10n_py.tax_regime'
    code = fields.Integer(required=True)        # 8=Turismo, etc.
    name = fields.Char(required=True)
```

### En `l10n_py_account`

```python
class L10nPyTimbrado(models.Model):
    _name = 'l10n_py.timbrado'
    _description = 'Paraguay - Timbrado DNIT'
    name = fields.Char(string='Número', required=True, size=15)
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    company_id = fields.Many2one('res.company', required=True, default=lambda s: s.env.company)
    state = fields.Selection([('draft','Draft'),('active','Active'),('expired','Expired')], default='draft')

class L10nPyPointOfEmission(models.Model):
    _name = 'l10n_py.point_of_emission'
    _description = 'Paraguay - Punto de Emisión'
    name = fields.Char(compute='_compute_name', store=True)
    establishment_code = fields.Char(required=True, size=3)
    code = fields.Char(string='Point of Emission', required=True, size=3)
    journal_id = fields.Many2one('account.journal', required=True)
    sequence_id = fields.Many2one('ir.sequence', required=True)
    timbrado_id = fields.Many2one('l10n_py.timbrado', required=True)
    company_id = fields.Many2one('res.company', required=True)
```

### En `l10n_py_edi`

```python
class L10nPyInutilizacionRange(models.Model):
    _name = 'l10n_py.inutilizacion_range'
    _description = 'Paraguay - Rango Inutilizado'
    point_of_emission_id = fields.Many2one('l10n_py.point_of_emission', required=True)
    document_type_id = fields.Many2one('l10n_latam.document.type', required=True)
    number_from = fields.Integer(required=True)
    number_to = fields.Integer(required=True)
    motivo = fields.Text(required=True)
    sifen_response = fields.Text()
    state = fields.Selection([('draft','Draft'),('sent','Enviado'),('confirmed','Confirmado')], default='draft')
    user_id = fields.Many2one('res.users', default=lambda s: s.env.user)
    company_id = fields.Many2one('res.company', required=True)
```

## 4. Campos a agregar vía `_inherit`

### `res.company`

```python
class ResCompany(models.Model):
    _inherit = 'res.company'

    l10n_py_ruc = fields.Char(string='RUC')
    l10n_py_dv_ruc = fields.Char(string='DV RUC', size=1)
    l10n_py_nombre_fantasia = fields.Char(string='Nombre Fantasía')
    l10n_py_tipo_contribuyente = fields.Selection([
        ('persona_fisica', 'Persona Física'),
        ('persona_juridica', 'Persona Jurídica'),
    ])
    l10n_py_tax_regime_id = fields.Many2one('l10n_py.tax_regime')
    l10n_py_economic_activity_ids = fields.Many2many('l10n_py.economic_activity')
    l10n_py_ccfe_certificate = fields.Binary(attachment=False)   # NO attachment para encriptar
    l10n_py_ccfe_password = fields.Char()                        # Encriptado (custom getter/setter)
    l10n_py_csc = fields.Char()                                  # Encriptado
    l10n_py_csc_id = fields.Char(size=10)
    l10n_py_environment = fields.Selection([
        ('test', 'Test (Homologación)'),
        ('production', 'Producción'),
    ], default='test')
```

### `res.partner`

```python
class ResPartner(models.Model):
    _inherit = 'res.partner'

    # Reusa l10n_latam_identification_type_id de l10n_latam_base
    # Solo agregamos campos PY-específicos opcionales:
    l10n_py_enviar_whatsapp = fields.Boolean(default=False)
    l10n_py_department_id = fields.Many2one('l10n_py.department')
    l10n_py_district_id = fields.Many2one('l10n_py.district')
    l10n_py_city_id = fields.Many2one('l10n_py.city')
```

### `account.move`

```python
class AccountMove(models.Model):
    _inherit = 'account.move'

    l10n_py_cdc = fields.Char(string='CDC', size=44, compute='_compute_l10n_py_cdc', store=True, copy=False)
    l10n_py_codigo_seguridad = fields.Char(size=9, copy=False)
    l10n_py_tipo_emision = fields.Selection([
        ('normal', 'Normal'),
        ('contingencia', 'Contingencia'),
    ], default='normal')
    l10n_py_qr_url = fields.Char(compute='_compute_l10n_py_qr_url')
    l10n_py_kude_pdf = fields.Binary(compute='_compute_l10n_py_kude_pdf', store=False)
    l10n_py_sifen_response_code = fields.Char(size=10, copy=False)
    l10n_py_lote_id = fields.Char(copy=False)        # Cuando se envía en batch
```

### `account.move.line`

```python
class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    l10n_py_iva_tipo = fields.Selection([
        ('gravado', 'Gravado'),
        ('parcial', 'Parcialmente exento'),
        ('exento', 'Exento'),
    ])
    l10n_py_iva_proporcion = fields.Integer(default=100)  # 1-100
```

### `account.tax`

```python
class AccountTax(models.Model):
    _inherit = 'account.tax'

    l10n_py_tax_code = fields.Char(size=4)  # Código SIFEN del impuesto
```

### `product.template`

```python
class ProductTemplate(models.Model):
    _inherit = 'product.template'

    l10n_py_unit_measure_code = fields.Integer()  # 77, 83, 87, etc (catálogo SIFEN)
```

## 5. Regla de oro: no replicar lo que Odoo ya tiene

| Tentación                    | Por qué NO replicar                                                      | Qué hacer en su lugar                          |
| ---------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------- |
| Crear `l10n_py.invoice`      | `account.move` ya cubre todo el lifecycle (draft/posted/cancel/reversed) | Extender `account.move`                        |
| Crear `l10n_py.invoice_line` | `account.move.line` ya tiene tax + qty + price                           | Extender `account.move.line`                   |
| Crear `l10n_py.sync_queue`   | `account.edi.document` ya tiene state/retry/error/attachment             | Implementar `account.edi.format` para Paraguay |
| Crear `l10n_py.customer`     | `res.partner` es universal en Odoo                                       | Extender `res.partner`                         |
| Crear `l10n_py.product`      | `product.product/template` es universal                                  | Extender `product.template`                    |
| Crear `l10n_py.user`         | `res.users` es universal                                                 | Extender `res.users` (solo si POS exige PIN)   |

Esto NO es solo "mejor código" — es **requisito para que el módulo funcione con
el resto de addons OCA y Enterprise**. Un módulo que crea su propio sistema de
facturación paralelo NO se integra con sale, purchase, point_of_sale, stock, etc.
