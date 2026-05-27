---
source: https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html
fetched_at: 2026-05-19
summary: Referencia del ORM de Odoo 18 — model classes, field types, recordsets, environment, decorators, inheritance patterns.
priority: important
---

# Odoo 18 — ORM Guide

> Referencia condensada del ORM de Odoo. Documentación oficial completa:
> https://www.odoo.com/documentation/18.0/developer/reference/backend/orm.html

## 1. Model classes

Tres clases base — cada modelo hereda de una:

| Clase                   | Propósito                       | Tabla DB                  | Cuándo usar                                                |
| ----------------------- | ------------------------------- | ------------------------- | ---------------------------------------------------------- |
| `models.Model`          | Modelo persistido estándar      | Sí                        | 90% de casos (entidades de negocio)                        |
| `models.TransientModel` | Datos temporales auto-limpiados | Sí (con cron de limpieza) | Wizards, formularios multi-step                            |
| `models.AbstractModel`  | Mixin sin tabla propia          | No                        | Compartir lógica entre múltiples modelos (ej: mail.thread) |

### Atributos de configuración del modelo

```python
class L10nPyTimbrado(models.Model):
    _name = 'l10n_py.timbrado'                    # Identifier único del modelo
    _description = 'Paraguay Timbrado DNIT'        # Nombre human-readable
    _table = 'l10n_py_timbrado'                    # Custom (default: _name con _)
    _auto = True                                   # Auto-crear tabla (default True)
    _log_access = True                             # create/write_uid/_date (default True)
    _rec_name = 'name'                             # Field para display name (default 'name')
    _order = 'date_from desc, name'                # Default ordering
    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id)', 'Timbrado number must be unique per company.'),
    ]
```

### Inheritance config

| Atributo                                    | Tipo            | Significado                                                      |
| ------------------------------------------- | --------------- | ---------------------------------------------------------------- |
| `_inherit = 'model.name'`                   | str o list[str] | Extiende modelo(s) existente(s) — mismo `_name`                  |
| `_inherit = ['mail.thread']`                | list            | Mixin (sin cambiar `_name`)                                      |
| `_inherits = {'res.partner': 'partner_id'}` | dict            | **Delegation** — campos del padre accesibles directamente vía FK |

## 2. Field types

### Campos básicos

```python
name = fields.Char(string="Name", size=100)
description = fields.Text()
quantity = fields.Integer(default=0)
price = fields.Float(digits=(10, 2))                                     # (precision, scale)
amount = fields.Monetary(currency_field='currency_id')
is_active = fields.Boolean(default=True)
state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')])
attachment = fields.Binary(attachment=True)                              # attachment=True almacena en filestore
content = fields.Html()
order_date = fields.Date()
created_at = fields.Datetime()
```

### Campos relacionales

```python
partner_id = fields.Many2one('res.partner', string="Customer", ondelete='restrict')
order_lines = fields.One2many('sale.order.line', 'order_id', string='Lines')
tags = fields.Many2many('product.tag', string="Tags")
document = fields.Reference([('sale.order', 'Sale'), ('purchase.order', 'Purchase')])
```

- `ondelete`: `'cascade'` | `'restrict'` | `'set null'`
- `Many2many` crea junction table automáticamente (custom: `relation='...'`)

### Campos especiales

```python
# Related: shortcut a un campo de un Many2one (NO se almacena por default)
customer_name = fields.Char(related='partner_id.name', readonly=True, store=False)

# Computed: calculado dinámicamente
@api.depends('lines.amount')
def _compute_total(self):
    for record in self:
        record.total = sum(record.lines.mapped('amount'))

total = fields.Float(compute='_compute_total', store=True)  # store=True = persistido + filtrable

# Computed con inverso (escribir el computed actualiza la fuente)
def _inverse_total(self):
    for record in self:
        # lógica para distribuir el total en lines
        pass

total = fields.Float(compute='_compute_total', inverse='_inverse_total', store=True)
```

### Parámetros comunes

- `string`: label (default: capitaliza el field name)
- `default`: valor estático o callable: `default=lambda self: self.env.company`
- `required`: bool
- `readonly`: bool
- `copy`: bool (cuando se duplica record con `copy()`) — `False` típico para sequence/keys únicas
- `index`: bool — crea índice DB
- `help`: tooltip
- `tracking`: int (orden) — log changes en chatter (requiere `mail.thread`)

### Campos automáticos del ORM

Si `_log_access = True` (default), Odoo crea:

- `id`, `create_date`, `create_uid`, `write_date`, `write_uid`

## 3. Recordset operations

Un **recordset** es una colección ordenada de records del mismo modelo. **Todo método
de instancia opera sobre un recordset** (puede ser de 1 o N records).

### CRUD

```python
# Create (siempre devuelve recordset del record creado)
record = self.env['sale.order'].create({
    'name': 'SO001',
    'partner_id': partner.id,
})

# Create múltiple (preferido — usa `@api.model_create_multi`)
records = self.env['sale.order'].create([
    {'name': 'SO001'},
    {'name': 'SO002'},
])

# Write — actualiza todos los records del recordset
records.write({'state': 'confirmed'})

# Read (lista de dicts)
data = records.read(['name', 'amount'])

# Unlink (delete)
records.unlink()

# Browse (recupera por ID, no busca)
record = self.env['sale.order'].browse(42)
records = self.env['sale.order'].browse([1, 2, 3])
```

### Search

```python
# search (recordset)
records = self.env['sale.order'].search([
    ('state', '=', 'draft'),
    ('amount', '>', 1000),
])

# search_count (int, sin fetchear datos)
n = self.env['sale.order'].search_count(domain)

# search_read (lista de dicts, fusiona search+read en 1 query)
data = self.env['sale.order'].search_read(domain, ['name', 'amount'], limit=10, order='date desc')
```

### Search domains

Tuplas `(field, operator, value)`:

```python
[('state', 'in', ['draft', 'confirmed']),
 '|',
 ('priority', '>', 5),
 ('partner_id.country_id.code', '=', 'PY')]
```

Operadores: `=`, `!=`, `>`, `<`, `>=`, `<=`, `in`, `not in`, `like`, `ilike`,
`=like`, `=ilike`, `child_of`, `parent_of`, `any`, `not any`.

Lógicos prefix: `&` (AND, default), `|` (OR), `!` (NOT).

### Inspección y manipulación

```python
# exists()
if record.exists():
    record.write({...})

# ensure_one() — raise si recordset != 1 record
single = records.ensure_one()

# copy()
duplicate = record.copy({'name': 'Copy of Original'})

# filtered() / filtered_domain()
draft = records.filtered(lambda r: r.state == 'draft')
draft = records.filtered('state', 'draft')
draft = records.filtered_domain([('state', '=', 'draft')])

# mapped()
names = records.mapped('name')                  # list de strings
partners = records.mapped('partner_id')         # recordset de partners (deduplicado)
amounts = records.mapped(lambda r: r.amount * 1.1)

# sorted()
sorted_records = records.sorted(key='amount', reverse=True)
sorted_records = records.sorted(key=lambda r: (r.partner_id.id, r.date))

# Aritmética de recordsets
union = recs_a | recs_b              # union (dedup)
inter = recs_a & recs_b              # intersection
diff = recs_a - recs_b               # difference
```

### Grouping

```python
groups = self.env['sale.order'].read_group(
    domain=[('state', '=', 'done')],
    fields=['amount_total:sum'],
    groupby=['partner_id'],
)
# Resultado: [{'partner_id': (1, 'Acme'), 'amount_total': 1500, '__count': 3}, ...]
```

## 4. Environment & context

`self.env` provee acceso al runtime:

```python
self.env.user                  # res.users actual
self.env.cr                    # database cursor (psycopg2)
self.env.context               # dict de contexto (lang, tz, etc)
self.env.company               # res.company actual
self.env.companies             # res.company que el user puede ver
self.env.uid                   # user id (int)
self.env.lang                  # 'es_PY', etc.
self.env.su                    # bool: True si en sudo
self.env.ref('module.xml_id')  # recordset por external ID
self.env['model.name']         # recordset vacío del modelo (para search/create)
```

### Context manipulation (no mutates — devuelve nuevo recordset)

```python
# Cambiar idioma temporalmente
records.with_context(lang='es_PY').name      # name traducido al español

# Cambiar usuario
records.with_user(other_user).read(...)

# Cambiar company
records.with_company(other_company).create(...)

# Bypass security (¡cuidado!)
records.sudo().write(...)

# Combinar
records.with_context(tracking_disable=True).sudo().write(...)
```

## 5. Method decorators

### `@api.depends('field1', 'rel.field2')`

Marca dependencias de un computed field. Esencial para `compute=` + `store=True`.

```python
@api.depends('partner_id', 'lines.amount')
def _compute_totals(self):
    for record in self:
        record.amount = sum(record.lines.mapped('amount'))
```

### `@api.constrains('field1', 'field2')`

Validación post-write. Si raises `ValidationError`, rollback de la transacción.

```python
@api.constrains('price')
def _check_price(self):
    for record in self:
        if record.price < 0:
            raise ValidationError("Price cannot be negative")
```

### `@api.onchange('field')`

Triggered cuando el usuario cambia el campo en el form (NO en write a DB).
Usado para pre-llenar otros campos.

```python
@api.onchange('partner_id')
def _onchange_partner(self):
    if self.partner_id:
        self.payment_term_id = self.partner_id.property_payment_term_id
```

### `@api.model`

Classmethod-like. Recibe `cls`-equivalente pero opera sin recordset específico.

```python
@api.model
def create_from_template(self, template_name):
    return self.create({'name': template_name})
```

### `@api.model_create_multi` (preferido sobre solo `@api.model` en create)

Permite que `create()` reciba **list de dicts** además de un solo dict.
Es la forma idiomática moderna.

```python
@api.model_create_multi
def create(self, vals_list):
    for vals in vals_list:
        # pre-procesamiento individual
        pass
    return super().create(vals_list)
```

## 6. Inheritance patterns

### Classical inheritance — `_inherit` mismo `_name`

Extiende un modelo existente. **Misma tabla**.

```python
class AccountMove(models.Model):
    _inherit = 'account.move'  # No definir _name; toma el del padre

    l10n_py_cdc = fields.Char(string='CDC', size=44, copy=False)

    def _post(self, soft=True):
        # Pre-hook
        for move in self:
            if move.country_id.code == 'PY' and not move.l10n_py_cdc:
                move.l10n_py_cdc = self._l10n_py_generate_cdc()
        return super()._post(soft=soft)
```

### Prototype inheritance — `_inherit = ['mixin_1', 'mixin_2']`

Múltiple inheritance desde AbstractModels. **Crea tabla nueva** si `_name` cambia.

```python
class L10nPyTimbrado(models.Model):
    _name = 'l10n_py.timbrado'
    _inherit = ['mail.thread', 'mail.activity.mixin']  # gana chatter y actividades

    name = fields.Char(required=True, tracking=True)
```

### Delegation inheritance — `_inherits`

Crea **tabla nueva** + FK al padre. Los campos del padre **se pueden leer/escribir
como si fueran propios**.

```python
class HrEmployee(models.Model):
    _name = 'hr.employee'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')

# employee.name funciona — delega a partner_id.name
```

Casos típicos: `hr.employee` delega a `res.partner`; `account.account` delega a
`account.account.template` (a veces).

### Combinación: extender Y mixin

```python
class AccountMove(models.Model):
    _inherit = ['account.move', 'mail.thread']   # account.move sí lo declara — esto solo lo refuerza
```

## 7. Ejemplo completo

```python
from odoo import api, fields, models
from odoo.exceptions import ValidationError, UserError

class L10nPyTimbrado(models.Model):
    _name = 'l10n_py.timbrado'
    _description = 'Paraguay - Timbrado DNIT'
    _inherit = ['mail.thread']
    _order = 'date_from desc'
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)',
         'Timbrado number must be unique per company.'),
    ]

    name = fields.Char(string='Number', required=True, size=15, tracking=True)
    date_from = fields.Date(required=True, tracking=True)
    date_to = fields.Date(required=True, tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('expired', 'Expired'),
    ], default='draft', tracking=True)
    company_id = fields.Many2one(
        'res.company', required=True,
        default=lambda self: self.env.company,
    )
    is_current = fields.Boolean(compute='_compute_is_current', store=False)

    @api.depends('date_from', 'date_to', 'state')
    def _compute_is_current(self):
        today = fields.Date.today()
        for record in self:
            record.is_current = (
                record.state == 'active'
                and record.date_from <= today <= record.date_to
            )

    @api.constrains('date_from', 'date_to')
    def _check_dates(self):
        for record in self:
            if record.date_from >= record.date_to:
                raise ValidationError("date_from must be before date_to.")

    @api.constrains('state', 'company_id')
    def _check_single_active(self):
        for record in self:
            if record.state != 'active':
                continue
            others = self.search([
                ('company_id', '=', record.company_id.id),
                ('state', '=', 'active'),
                ('id', '!=', record.id),
            ])
            if others:
                raise ValidationError(
                    "Only one Timbrado can be active per company. "
                    "Currently active: %s" % others.mapped('name')
                )

    def action_activate(self):
        self.ensure_one()
        # Desactivar el previo
        previous = self.search([
            ('company_id', '=', self.company_id.id),
            ('state', '=', 'active'),
        ])
        previous.write({'state': 'expired'})
        self.state = 'active'
        return True
```

## 8. Buenas prácticas

- **Iterar siempre sobre `self`** dentro de métodos de instancia (incluso si `len(self) == 1`):
  ```python
  for record in self:
      record.field = ...
  ```
- **`for record in self`** > `self[0]` o `self.ensure_one()` excepto cuando explícitamente
  querés un único record.
- **`@api.depends`** debe listar TODOS los campos leídos por el compute, incluyendo
  los que se acceden via Many2one (`'partner_id.country_id.code'`).
- **`store=True`** para computed cuando necesitás filtrar o agrupar por ese field.
- **Nunca `cr.commit()`** dentro de un método de modelo (rompe la transacción Odoo).
- **`sudo()` con cuidado** — bypass security. Solo en casos específicos donde el flow
  lo requiere (ej: cron, hooks).
- **Validar input externo** siempre (controllers, wizards) — el ORM SÍ valida
  consistencia pero no semántica de negocio.

Ver convenciones OCA en [`20_OCA_GUIDELINES.md`](20_OCA_GUIDELINES.md).
