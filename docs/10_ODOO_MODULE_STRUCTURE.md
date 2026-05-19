---
source: https://www.odoo.com/documentation/18.0/developer/reference/backend/module.html + data.html
fetched_at: 2026-05-19
summary: Estructura canónica de un módulo Odoo 18 — manifest, layout de carpetas, __init__.py, hooks, archivos de datos XML/CSV, external IDs.
priority: critical
---

# Estructura canónica de un módulo Odoo 18

> Referencia rápida para construir cada uno de los módulos `l10n_py_*`. Fuente:
> documentación oficial Odoo 18 + convenciones OCA aplicadas
> (ver [`20_OCA_GUIDELINES.md`](20_OCA_GUIDELINES.md)).

## 1. Módulo mínimo viable

```
l10n_py_base/
├── __init__.py              # from . import models
├── __manifest__.py          # metadata
├── models/
│   ├── __init__.py
│   └── res_company.py
└── README.rst               # auto-generado por oca-gen-addon-readme
```

Eso es suficiente para que Odoo cargue el módulo (aunque no hace nada). El resto
de carpetas se agregan según necesidad.

## 2. Layout completo (idiomático OCA)

```
l10n_py_edi/
├── __init__.py
├── __manifest__.py
├── README.rst                       # AUTO-GENERADO — no editar manualmente
├── readme/                           # Fragmentos para oca-gen-addon-readme
│   ├── DESCRIPTION.rst              # ¿Qué hace el módulo?
│   ├── INSTALL.rst                  # Pasos de instalación no triviales
│   ├── CONFIGURE.rst                # Configuración post-instalación
│   ├── USAGE.rst                    # Cómo usarlo día a día
│   ├── CONTRIBUTORS.rst             # Lista de personas
│   └── CREDITS.rst                  # Sponsors, traducciones
├── controllers/
│   ├── __init__.py
│   └── main.py                      # @http.route(...)
├── data/
│   ├── ir_cron_data.xml             # Crons programados
│   └── account_edi_format_data.xml  # Records de l10n_py EDI format
├── demo/
│   └── account_move_demo.xml        # Facturas de ejemplo
├── i18n/
│   ├── l10n_py_edi.pot              # Template POT
│   └── es.po                        # Español
├── migrations/                       # Migraciones entre versiones del módulo
│   └── 18.0.1.0.0/
│       └── post-migration.py
├── models/
│   ├── __init__.py
│   ├── account_edi_format.py        # Subclase de account.edi.format
│   ├── account_move.py
│   └── res_company.py
├── reports/
│   ├── __init__.py
│   ├── kude_report.xml              # ir.actions.report
│   └── kude_template.xml            # Template QWeb del KuDE
├── security/
│   ├── ir.model.access.csv          # ACL
│   └── l10n_py_edi_security.xml     # Groups + record rules
├── static/
│   ├── description/
│   │   ├── icon.png                 # 128x128
│   │   └── index.html               # Marketing page
│   └── src/
│       ├── js/                      # OWL components
│       ├── scss/
│       └── xml/                     # QWeb templates de JS
├── tests/
│   ├── __init__.py
│   ├── common.py                    # Test helpers
│   ├── test_account_move_post.py
│   ├── test_sifen_send.py
│   └── test_kude_report.py
├── views/
│   ├── account_move_views.xml       # Inheritance forms/list
│   ├── res_company_views.xml
│   └── menus.xml                    # Menuitems
└── wizards/
    ├── __init__.py
    ├── l10n_py_cancellation_wizard.py
    └── l10n_py_cancellation_wizard_views.xml
```

## 3. `__manifest__.py` — campos esperados

### Convención OCA para `l10n_py_*`

```python
{
    "name": "Paraguay - EDI (DNIT/SIFEN)",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations/EDI",
    "license": "AGPL-3",
    "author": "Careaga Dev, Odoo Community Association (OCA)",
    "website": "https://github.com/Ezcareaga/l10n-paraguay",
    "depends": [
        "account_edi",
        "l10n_latam_base",
        "l10n_latam_invoice_document",
        "l10n_py_account",
    ],
    "external_dependencies": {
        "python": ["lxml", "signxml", "zeep", "cryptography", "qrcode"],
    },
    "data": [
        "security/l10n_py_edi_security.xml",
        "security/ir.model.access.csv",
        "data/account_edi_format_data.xml",
        "data/ir_cron_data.xml",
        "views/account_move_views.xml",
        "views/res_company_views.xml",
        "views/menus.xml",
        "wizards/l10n_py_cancellation_wizard_views.xml",
        "reports/kude_report.xml",
        "reports/kude_template.xml",
    ],
    "demo": [
        "demo/account_move_demo.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
```

### Reglas de oro
- `license` **obligatorio** en todos los módulos OCA
- `author` **debe terminar** en `, Odoo Community Association (OCA)`
- `version` con prefijo `<odoo_version>.x.y.z` (ej: `18.0.1.0.0` — primer release)
- `depends` solo lo necesario; el orden importa para el loader
- `data` también: orden de carga es de arriba a abajo (security ANTES de data)

### Campos opcionales útiles
- `external_dependencies`: bloquea la instalación si falta el paquete Python o binario
- `pre_init_hook` / `post_init_hook` / `uninstall_hook`: funciones en `hooks.py`
  para tareas no expresables en XML
- `auto_install`: `True` (instala si todas las deps están) o lista de modules
  (bridge module pattern)

### Categorías OCA estándar
- `Accounting/Localizations/Account Charts` — para `l10n_py_base` (CoA)
- `Accounting/Localizations/EDI` — para `l10n_py_edi`
- `Accounting/Localizations/Reports` — para `l10n_py_reports`
- `Point of Sale/Localizations` — para `l10n_py_pos`

## 4. `__init__.py` patterns

### Top-level del módulo
```python
# l10n_py_edi/__init__.py
from . import controllers
from . import models
from . import wizards
# from . import hooks   # solo si hay hooks.py
```

### `models/__init__.py`
```python
from . import account_edi_format
from . import account_move
from . import account_move_line
from . import res_company
from . import res_partner
```

**Orden importa** cuando un módulo `_inherits` de otro definido en el mismo paquete
— importa primero el base.

### Hooks (opcional, si manifest los declara)
```python
# l10n_py_edi/hooks.py
def post_init_hook(env):
    """Configura el EDI format para Paraguay en companies existentes."""
    py_format = env.ref('l10n_py_edi.edi_format_py_dnit_sifen')
    py_companies = env['res.company'].search([('country_id.code', '=', 'PY')])
    py_companies.write({'edi_format_ids': [(4, py_format.id)]})

def uninstall_hook(env):
    """Cleanup opcional al desinstalar."""
    pass
```

## 5. Data files (XML)

### Esqueleto básico
```xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
    <record id="some_xml_id" model="ir.model.name">
        <field name="name">Some name</field>
    </record>
</odoo>
```

### `noupdate="1"` — datos que NO se sobreescriben en update
```xml
<odoo>
    <data noupdate="1">
        <!-- Demo data, configuración inicial editable por el usuario -->
        <record id="default_partner" model="res.partner">
            <field name="name">My Company</field>
        </record>
    </data>
</odoo>
```

**Sin `noupdate`:** el record se reescribe en cada `-u modulo`. Usá esto para
**configuración del módulo** que NUNCA debe editarse.

**Con `noupdate="1"`:** el record solo se crea la primera vez. Usá esto para
**plantillas / demo / defaults** que el usuario puede editar.

### `<field>` con `ref` (referencias a otros XML IDs)
```xml
<record id="my_view" model="ir.ui.view">
    <field name="name">my.view</field>
    <field name="model">res.partner</field>
    <field name="inherit_id" ref="base.view_partner_form"/>
    <field name="arch" type="xml">
        ...
    </field>
</record>
```

### `<field>` con `eval` (expresiones Python)
```xml
<field name="groups_id" eval="[(4, ref('base.group_user'))]"/>
<field name="start_date" eval="datetime.date.today()"/>
<field name="amount" eval="100 * 1.21"/>
```

Vars disponibles: `time`, `datetime`, `timedelta`, `relativedelta`, `ref()`, `obj`.

### Shortcuts útiles
```xml
<menuitem id="menu_l10n_py" name="Paraguay" parent="account.menu_finance"/>
<menuitem id="menu_l10n_py_timbrado"
          name="Timbrados" parent="menu_l10n_py"
          action="action_l10n_py_timbrado"/>

<delete model="ir.ui.view" id="some.legacy_view"/>

<function model="account.move" name="some_method"
          eval="[[ref('some.move_id')]]"/>
```

## 6. Data files (CSV)

Formato:
```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_l10n_py_timbrado_user,l10n_py.timbrado.user,model_l10n_py_timbrado,base.group_user,1,0,0,0
access_l10n_py_timbrado_manager,l10n_py.timbrado.manager,model_l10n_py_timbrado,account.group_account_manager,1,1,1,1
```

- Primera fila: nombres de campos
- `model_id:id` se resuelve a `model_<dotted_name_with_underscores>`
  (ej: `l10n_py.timbrado` → `model_l10n_py_timbrado`)
- External IDs entre módulos: `module.xml_id` (ej: `base.group_user`)

## 7. External IDs — convención OCA

Patrón: `<model_with_underscores>_<descriptor>`

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| Data record | `<model>_<descriptor>` | `res_users_admin` |
| View | `<model>_view_<type>` | `account_move_view_form` |
| Action | `<model>_action` | `account_move_action` |
| Menu | `<model>_menu` | `account_move_menu` |
| Security group | `<model>_group_<name>` | `account_move_group_manager` |
| Rule | `<model>_rule_<group>` | `account_move_rule_company` |
| Demo | append `_demo` | `res_partner_demo_customer_demo` |

Usar el XML ID sin prefijo del módulo dentro del propio módulo (`my_view`).
Usar `module.xml_id` para referencias cross-module (`base.view_partner_form`).

## 8. Proceso de carga del módulo

1. **Dependency resolution**: Odoo carga el módulo solo después de que todas
   las `depends` están instaladas.
2. **Python imports**: archivos en `models/`, `wizards/`, `controllers/`
   se ejecutan en orden de `__init__.py`.
3. **Model registration**: el ORM descubre y registra todas las clases `models.*`.
4. **`pre_init_hook`** (si existe): se ejecuta ANTES de cargar data files.
5. **Data loading**: archivos en `data` del manifest cargan en orden declarado.
6. **`post_init_hook`** (si existe): se ejecuta DESPUÉS de cargar data.
7. **Demo loading**: archivos en `demo` solo si `demo=True` en config.
8. **Asset bundling**: archivos `static/` se agrupan en bundles según `assets`
   del manifest.

## 9. Verificación rápida del módulo

Después de crear un módulo, verificá con:

```bash
# Lint OCA
pre-commit run --all-files

# Pylint con reglas Odoo
pylint --load-plugins=pylint_odoo -d all -e odoolint <module_path>

# Cargar en una instancia de prueba
odoo-bin -d test_db --addons-path=/path/to/addons -i l10n_py_edi --stop-after-init
```

Ver detalles de testing en [`14_ODOO_TESTING_GUIDE.md`](14_ODOO_TESTING_GUIDE.md).
