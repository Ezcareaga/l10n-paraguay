---
source: https://www.odoo.com/documentation/18.0/developer/reference/backend/security.html
fetched_at: 2026-05-19
summary: Seguridad Odoo 18 — ACL (ir.model.access), record rules (ir.rule), groups (res.groups), sudo/with_user, autenticación HTTP.
priority: important
---

# Odoo 18 — Security Guide

> Dos capas de seguridad en Odoo:
> 1. **Model-level (ACL)** — quién puede leer/escribir/crear/borrar registros de un modelo.
> 2. **Record-level (Record Rules)** — qué registros específicos puede ver/editar (filtro por dominio).
>
> A ambas se les agrega el sistema de **groups** (`res.groups`) que asigna permisos a usuarios.

## 1. Access Rights — `ir.model.access`

Permisos CRUD a nivel de modelo. Se definen típicamente en
`security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_l10n_py_timbrado_user,l10n_py.timbrado.user,model_l10n_py_timbrado,base.group_user,1,0,0,0
access_l10n_py_timbrado_manager,l10n_py.timbrado.manager,model_l10n_py_timbrado,account.group_account_manager,1,1,1,1
access_l10n_py_inutilizacion_admin,l10n_py.inutilizacion.admin,model_l10n_py_inutilizacion_range,base.group_system,1,1,1,1
```

### Reglas clave

- `model_id:id` se resuelve a `model_<dotted_name>` con puntos como underscores
  (`l10n_py.timbrado` → `model_l10n_py_timbrado`)
- `group_id:id` puede ser vacío → todos los usuarios autenticados
- Permisos son **aditivos**: si el user está en varios groups con distintos
  permisos, gana la UNIÓN
- Sin **ningún** access record que aplique al user → no puede acceder al modelo

### Equivalente en XML (raramente usado)

```xml
<record id="access_l10n_py_timbrado_user" model="ir.model.access">
    <field name="name">l10n_py.timbrado.user</field>
    <field name="model_id" ref="model_l10n_py_timbrado"/>
    <field name="group_id" ref="base.group_user"/>
    <field name="perm_read">1</field>
    <field name="perm_write">0</field>
    <field name="perm_create">0</field>
    <field name="perm_unlink">0</field>
</record>
```

## 2. Record Rules — `ir.rule`

Filtran qué records específicos un usuario puede ver/escribir vía un dominio.

```xml
<record id="l10n_py_timbrado_rule_company" model="ir.rule">
    <field name="name">Timbrado: solo de la company del usuario</field>
    <field name="model_id" ref="model_l10n_py_timbrado"/>
    <field name="domain_force">[('company_id', 'in', company_ids)]</field>
    <field name="perm_read" eval="1"/>
    <field name="perm_write" eval="1"/>
    <field name="perm_create" eval="1"/>
    <field name="perm_unlink" eval="1"/>
    <field name="groups" eval="[(4, ref('base.group_user'))]"/>
</record>
```

### Variables disponibles en `domain_force`

| Variable | Significado |
|----------|-------------|
| `user` | recordset del usuario actual (singleton) |
| `user.id` | ID del usuario |
| `company_id` | ID de la company actual (int, no recordset) |
| `company_ids` | lista de IDs de companies a las que el user tiene acceso |
| `time` | módulo `time` de Python |

### Composición de reglas

- **Global rules** (sin `groups`) → siempre se aplican, **intersectan** entre sí
- **Group rules** (con `groups`) → si un user está en varios grupos con rules
  distintas para el mismo modelo, las rules **se unen** (OR) dentro del grupo,
  pero **siempre intersectan con las globales**

```
final_allowed = (global_rule_1 AND global_rule_2 AND ...) AND (group_rule_1 OR group_rule_2 OR ...)
```

### Atributos `perm_*` en las rules

A diferencia de `ir.model.access`, estos atributos en `ir.rule` indican
**qué operaciones disparan la evaluación** del dominio. Si todos son `False`,
la rule no aplica nunca; si todos son `True` (default), aplica para todo CRUD.

## 3. Groups — `res.groups`

Conjuntos de usuarios. Cada user puede estar en múltiples groups. ACL y rules
se asignan a groups, no directamente a usuarios.

```xml
<record id="group_l10n_py_edi_user" model="res.groups">
    <field name="name">Paraguay EDI / User</field>
    <field name="category_id" ref="base.module_category_accounting"/>
    <field name="implied_ids" eval="[(4, ref('account.group_account_invoice'))]"/>
</record>

<record id="group_l10n_py_edi_manager" model="res.groups">
    <field name="name">Paraguay EDI / Manager</field>
    <field name="category_id" ref="base.module_category_accounting"/>
    <field name="implied_ids" eval="[(4, ref('group_l10n_py_edi_user')),
                                     (4, ref('account.group_account_manager'))]"/>
</record>
```

### Campos importantes

- `name` — display
- `category_id` — `ir.module.category` — agrupa por app/módulo en Settings → Users
- `implied_ids` — si estás en este grupo, automáticamente estás en estos otros también
- `users` — One2many a `res.users` (usar `implied_ids` en lugar de asignar usuarios)

### Patrón "User + Manager"

Casi todos los módulos OCA exponen 2 groups:
- `module_group_user` — operación cotidiana
- `module_group_manager` — admin/configuración

El `manager` siempre `implies` al `user`. Los record rules típicamente solo se
escriben para `user` (porque manager ya las hereda).

## 4. Controllers — autenticación HTTP

```python
from odoo import http

class L10nPyController(http.Controller):

    @http.route('/l10n_py/qr/<string:cdc>', auth='public', methods=['GET'], type='http')
    def public_qr_redirect(self, cdc, **kw):
        """Acceso público — cualquier persona con el CDC puede consultar."""
        # Validar CDC, redireccionar a portal e-Kuatia
        return http.request.redirect(f"https://ekuatia.set.gov.py/consultas/qr?Id={cdc}")

    @http.route('/l10n_py/admin/regenerate', auth='user', methods=['POST'], type='json')
    def admin_action(self):
        """Solo usuarios logueados."""
        if not http.request.env.user.has_group('l10n_py_edi.group_l10n_py_edi_manager'):
            return {'error': 'forbidden'}
        # ...
```

### Niveles de `auth`

| Valor | Comportamiento |
|-------|----------------|
| `'user'` | Requiere user logueado; rechaza si no hay sesión |
| `'public'` | Acepta sesión `public` (no logueado) — útil para portal/web |
| `'none'` | Bypass total (raro — solo health checks, webhooks con su propia auth) |

### CSRF protection

Activado por default para POST. En formularios HTML:
```xml
<input type="hidden" name="csrf_token" t-att-value="request.csrf_token()"/>
```

Para webhooks externos (que no pueden enviar CSRF), declarar la route con
`csrf=False` — y agregar firma propia (HMAC, etc.) para autenticidad.

## 5. ORM-level security helpers

### `sudo()` — bypass de access rights y record rules

**Úsalo con cuidado.** Sudo es el escape hatch para situaciones donde la operación
debe suceder sin importar quién lo dispara.

```python
# OK: cron job, hook de instalación
self.env['account.move'].sudo().search([])

# OK: lookup técnico que el user no debe ver completo, pero necesitamos
# para validar algo
partner_exists = self.env['res.partner'].sudo().search_count([('vat', '=', vat)])

# MAL: exponer un endpoint donde el user vea/edite cosas que no debería
def some_method(self):
    self.sudo().write({...})  # ¡ojo!
```

**Regla:** todo `sudo()` debe estar comentado con el porqué.

### `with_user(user)` — ejecutar como otro usuario

```python
admin = self.env.ref('base.user_admin')
records.with_user(admin).action_post()
```

A diferencia de `sudo()`, esto SÍ valida access rights y rules — pero con el
user pasado, no el actual.

### `with_context(...)` — modificar contexto

```python
# Desactivar tracking para una operación masiva
records.with_context(tracking_disable=True).write({...})

# Forzar idioma
records.with_context(lang='es_PY').name
```

## 6. Pitfalls comunes de seguridad

| Riesgo | Cómo evitarlo |
|--------|---------------|
| SQL injection en query custom | Usar **siempre** parámetros: `cr.execute('SELECT ... WHERE id IN %s', (tuple(ids),))` |
| XSS en templates QWeb | QWeb escapea por default; nunca uses `t-raw` con datos de usuario |
| Métodos públicos de model accesibles via RPC | Prefix `_` para métodos privados; los públicos son llamables vía XML-RPC/JSON-RPC |
| Subir archivos sin sanitizar | Validar mimetype, tamaño, contenido antes de guardar |
| Hardcodear secretos | Variables de entorno o `ir.config_parameter` (encriptados si son sensibles) |
| Exponer error stack traces en producción | Modo `--dev=none` (sin stack trace en HTTP responses) |

### `Markup` para HTML seguro

```python
from odoo.tools import Markup
safe = Markup("<b>%s</b>") % user_input  # user_input se escapea
```

## 7. Patrón completo para `l10n_py_edi`

`l10n_py_edi/security/l10n_py_edi_security.xml`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <data noupdate="1">

        <record id="module_category_l10n_py" model="ir.module.category">
            <field name="name">Paraguay EDI</field>
            <field name="sequence">15</field>
        </record>

        <record id="group_l10n_py_edi_user" model="res.groups">
            <field name="name">User</field>
            <field name="category_id" ref="module_category_l10n_py"/>
            <field name="implied_ids" eval="[(4, ref('account.group_account_invoice'))]"/>
        </record>

        <record id="group_l10n_py_edi_manager" model="res.groups">
            <field name="name">Manager</field>
            <field name="category_id" ref="module_category_l10n_py"/>
            <field name="implied_ids" eval="[(4, ref('group_l10n_py_edi_user')),
                                             (4, ref('account.group_account_manager'))]"/>
        </record>

        <!-- Record rule: solo timbrados de las companies del user -->
        <record id="l10n_py_timbrado_rule_company" model="ir.rule">
            <field name="name">Timbrado: per company</field>
            <field name="model_id" ref="model_l10n_py_timbrado"/>
            <field name="domain_force">[('company_id', 'in', company_ids)]</field>
            <field name="groups" eval="[(4, ref('group_l10n_py_edi_user'))]"/>
        </record>

    </data>
</odoo>
```

`l10n_py_edi/security/ir.model.access.csv`:

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_l10n_py_timbrado_user,l10n_py.timbrado.user,model_l10n_py_timbrado,group_l10n_py_edi_user,1,0,0,0
access_l10n_py_timbrado_manager,l10n_py.timbrado.manager,model_l10n_py_timbrado,group_l10n_py_edi_manager,1,1,1,1
access_l10n_py_inutilizacion_manager,l10n_py.inutilizacion.manager,model_l10n_py_inutilizacion_range,group_l10n_py_edi_manager,1,1,1,1
access_l10n_py_cancellation_wizard,l10n_py.cancellation.wizard,model_l10n_py_cancellation_wizard,group_l10n_py_edi_user,1,1,1,1
```

Cargar en el manifest **antes** que las views:
```python
'data': [
    'security/l10n_py_edi_security.xml',     # GROUPS primero
    'security/ir.model.access.csv',          # ACL después
    'views/account_move_views.xml',
    # ...
],
```
