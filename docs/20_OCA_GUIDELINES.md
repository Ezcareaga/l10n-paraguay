---
source: https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst
fetched_at: 2026-05-19
summary: Convenciones OCA — naming de módulos, manifest, layout, XML/Python style, XML IDs, commits, PRs, testing, localizaciones.
priority: critical
---

# OCA Module Development Guidelines

> Convenciones de la **Odoo Community Association** que `l10n-paraguay` sigue al
> pie de la letra. Fuente: `OCA/odoo-community.org/CONTRIBUTING.rst`.

## 1. Naming de módulos

### Reglas generales

- **Singular** en nombres (excepciones: `multi_*` o nombres ya plurales en Odoo)
- Prefix `base_` para módulos que sirven de base a otros (ej: `base_location_nuts`)
- Prefix `l10n_CC_` para localizaciones, donde **CC = ISO 3166-1 alpha-2** del país
  (ej: `l10n_es_pos`, `l10n_py_base`)
- Prefix con nombre del módulo Odoo extendido cuando aplica (ej: `mail_forward`)
- Combinación Odoo + OCA: nombre Odoo primero (ej: `crm_partner_firstname`)

### Para este repo (Paraguay)

- `l10n_py_base` — RUC, regímenes, departamentos
- `l10n_py_account` — Plan de cuentas, taxes, document types, timbrado
- `l10n_py_edi` — XML SIFEN, firma, SOAP, eventos
- `l10n_py_reports` — Libros IVA, Hechauka
- `l10n_py_pos` — POS con SIFEN
- `l10n_py_withholding` — Retenciones IVA/IRE/IRP

## 2. Manifest (`__manifest__.py`)

### Campos esenciales

- `license`: requerido — **AGPL-3** para módulos OCA-pure, LGPL-3 a veces para
  módulos sin copyleft fuerte. Para este repo: **AGPL-3** en todos.
- `author`: termina **siempre** con `, Odoo Community Association (OCA)`
- `website`: `https://github.com/OCA/<repo>` o el repo específico del addon path
- **No keys vacíos**
- **Nunca** logos de empresa (los authors y contributors bastan)

### External deps

```python
'external_dependencies': {
    'bin': ['wkhtmltopdf'],
    'python': ['signxml>=3.2'],
},
```

### Version numbers

Semver con prefijo Odoo: `<ODOO>.x.y.z`

- **x (major)**: cambios significativos de schema/data — requiere migración
- **y (minor)**: nuevas features no-breaking — requiere upgrade del módulo
- **z (patch)**: bug fixes — típicamente solo restart

Primera release de 18.0: `18.0.1.0.0`.

## 3. Layout de carpetas

```
module_name/
├── controllers/
├── data/
├── demo/
├── examples/
├── i18n/
├── migrations/
├── models/
├── readme/                       ← OCA-specific (genera README.rst)
│   ├── CONTRIBUTORS.rst
│   ├── DESCRIPTION.rst
│   ├── USAGE.rst
│   ├── INSTALL.rst
│   ├── CONFIGURE.rst
│   ├── CREDITS.rst
│   ├── ROADMAP.rst
│   └── HISTORY.rst
├── reports/
├── security/
├── static/
├── tests/
├── views/
├── wizards/
├── README.rst                    ← auto-generado, NO editar
├── __init__.py
├── __manifest__.py
├── exceptions.py
└── hooks.py
```

### Convención de archivos

- Splitting por modelo:
  - `models/<model_name>.py`
  - `views/<model_name>_views.xml`
  - `demo/<model_name>_demo.xml`
- Static assets:
  - `static/js/<module_name>.js`
  - `static/css/<module_name>.css`
- Naming: lowercase + underscore (`[a-z0-9_]`)
- Permisos: carpetas 755, archivos 644

## 4. Hooks de instalación

En `hooks.py` raíz del módulo, con manifest:

```python
{
    'pre_init_hook': 'pre_init_hook',
    'post_init_hook': 'post_init_hook',
    'uninstall_hook': 'uninstall_hook',
    'post_load': 'post_load',          # monkey patches al cargar el módulo
}
```

Reglas:

- Solo cuando NO se puede hacer con XML data files
- `post_load` solo para monkey patches (raro)

## 5. XML conventions

### Formato

- Indentación: **4 espacios**
- En `<record>`: `id` antes que `model`
- En `<field>`: `name` primero, luego `value`/`eval`, luego otros atributos
- Records agrupados por modelo cuando posible

### Naming de XML IDs

> **Patrón:** `<model_with_underscores>_<descriptor>`. Sin prefijo del módulo
> dentro del mismo módulo.

| Tipo           | Patrón                                       | Ejemplo                          |
| -------------- | -------------------------------------------- | -------------------------------- |
| Data record    | `<model>_<name>`                             | `res_users_important_person`     |
| View           | `<model>_view_<type>`                        | `res_partner_view_form`          |
| Action         | `<model>_action` o `<model>_action_<detail>` | `sale_order_action_child_list`   |
| Menu           | `<model>_menu`                               | `account_invoice_menu`           |
| Security group | `<model>_group_<name>`                       | `sale_order_group_manager`       |
| Rule           | `<model>_rule_<group>`                       | `account_invoice_rule_company`   |
| Demo record    | append `_demo`                               | `res_partner_demo_customer_demo` |

### Herencia de vistas

- Un módulo solo debe heredar una vista UNA vez (consolidar todos los cambios)
- Preservar nombres originales para consistencia
- **Evitar `position="replace"`** — usar priority >100 con comentario explicativo
- Alternativa: `invisible="1"` para esconder en lugar de remover

## 6. Python conventions

### Import order

1. Standard library
2. Third-party libraries conocidas
3. Odoo imports (`from odoo import ...`)
4. Odoo addon imports (raro — solo cuando heredás de otro addon explícitamente)
5. Local relative imports (`from . import ...`)
6. Third-party libraries no-estándar

Alfabético dentro de cada grupo.

### PEP8 + flake8

- Seguir PEP8
- Excepción: `F401` (imports no usados) permitido en `__init__.py`
- Strings: preferir `%` formatting sobre `.format()` (usar **named placeholders**
  para safety en traducciones)
- **Readability > conciseness**

### Naming de métodos

- `_compute_<field>` — para `compute=` de fields
- `_inverse_<field>` — para `inverse=` de fields computed
- `_search_<field>` — para search en computed sin store
- `_default_<field>` — para `default=` callable
- `_onchange_<field>` — para `@api.onchange`
- `_check_<constraint>` — para `@api.constrains`
- `action_<name>` — métodos invocados desde botones de UI

### Orden dentro de la clase

1. Atributos privados (`_name`, `_inherit`, `_description`, `_order`, etc.)
2. Field declarations
3. SQL constraints
4. Default methods y `_default_get`
5. Compute / search methods
6. Constraints y onchange methods
7. CRUD overrides (`create`, `write`, `unlink`)
8. Action methods (`action_*`)
9. Business methods

### Naming de fields

- Many2one: sufijo `_id` (`partner_id`)
- One2many / Many2many: sufijo `_ids` (`line_ids`, `tag_ids`)
- Omitir `string=` si el nombre técnico es claro (Odoo capitaliza
  automáticamente: `field_name` → "Field Name")

### Variables

- `snake_case`
- Nombres significativos (no letras sueltas excepto loops/lambdas)
- No sufijo `_id`/`_ids` salvo que realmente contengan IDs
- Constantes globales: `UPPERCASE_WITH_UNDERSCORES`

### SQL safety

- **NUNCA** concatenar input de usuario en queries SQL
- **Siempre** parametrizadas: `cr.execute('SELECT ... WHERE id IN %s', (tuple(ids),))`
- **NUNCA** `cr.commit()` fuera del control del framework — usar `cr.savepoint()`
  o transacciones aisladas

### Exception handling

- No `pass` desnudo en `except`
- Log mínimo: `_logger.debug('mensaje', exc_info=1)`
- Usar `odoo.exceptions.UserError` / `ValidationError`

## 7. Git commits

### Formato del mensaje

**Título** (≤50 chars, sin prefijo):

```
Fix incorrect tax calculation for service items
```

**Body** (80 chars por línea, ~5-10 líneas):

```
[FIX] account: correct tax calculation for service items

Service items were incorrectly applying product tax rates.
Updated computation logic to check item type before tax
application. Affects invoice and quotation reports.
```

### Convenciones

- **Presente imperativo:** "Fix formatting", no "Fixes" ni "Fixed"
- Incluir nombre del módulo en el body
- **Un cambio lógico por commit** (no "Fix pep8" follow-ups)
- Referenciar issues cuando relevante
- Tags: `[FIX]`, `[IMP]`, `[REF]`, `[MIG]` (para migraciones)

> En este repo (l10n-paraguay) usamos **Conventional Commits** (`feat:`, `fix:`,
> `refactor:`, `test:`, `docs:`, `chore:`) — compatible con el espíritu OCA
> aunque el formato difiere.

## 8. Pull Request & Code Review

### Antes de submit

- Commit messages concisos y claros
- Description explica el **POR QUÉ**, no el qué (el diff ya lo muestra)
- Pasos de demo funcional si aplica
- Verificar cumplimiento de todos los guidelines

### Review requirements

- Al menos 1 aprobación de OCA Core Maintainers o PSC
- Áreas chequeadas:
  - Claridad de documentación
  - Approach genérico (utilizable por la comunidad)
  - Sin duplicación con addons existentes
  - Metodología de problem-solving
  - Demo data donde apropiado
  - Sin código de setup hardcoded
  - Commits limpios

### Merge

- Usar mensaje del autor (`--author` flag)
- Preservar autoría original
- PRs inactivos 6+ meses pueden ser cerrados

## 9. Translations

- OCA usa **Weblate**: https://translation.odoo-community.org/
- **Los PRs NO deben modificar `.po` files directamente** — solo Weblate
- Excepción: módulos nuevos pueden incluir `.po` inicial
- Para evitar conflictos: que Weblate maneje todo

## 10. External dependencies

### Manifest

```python
'external_dependencies': {
    'python': ['requests>=2.20'],
    'bin': ['wkhtmltopdf'],
}
```

### Version pinning

- **Nunca** pins exactos
- Lower bounds aceptables para features recientes (ej: `library>1.4`)
- Upper bounds solo si incompatibilidad confirmada e irresoluble

### Import handling

```python
try:
    import external_lib
    BINARY_PATH = tools.find_in_path('binary_name')
except (ImportError, IOError) as err:
    _logger.debug(err)
```

### Documentación

- Explicar instalación en `readme/INSTALL.rst`
- Definir paquetes en `requirements.txt` del repo para CI
- Listar deps OCA en `oca_dependencies.txt` (una por línea, con URL/branch opcional)

## 11. Specific para localizaciones

- **Naming:** `l10n_<cc>_<feature>` (ej: `l10n_be_intrastat`)
- **Team naming:** "<Country> Maintainers" (ej: "Paraguay Maintainers")
- **Repo naming:** `l10n-<cc>` (ej: `l10n-paraguay`)

### Consideraciones especiales

- Seguir todos los OCA standards
- **No asumir contextos single-country** en features que podrían reusarse
- Documentar reglas locales claramente en `readme/DESCRIPTION.rst`

## 12. Backporting de Odoo modules

Si un módulo de Odoo SA se backporta a OCA:

1. **Preservar atribución de licencia** de Odoo SA
2. **Author credit:** OCA como co-author junto con Odoo SA
3. **OCA compatibility:** PEP8, conventions, CI
4. **README disclaimer:**
   > "This module is a backport from Odoo SA and as such, it is not included in
   > the OCA CLA. That means we do not have a copy of the copyright on it like
   > all other OCA modules."

## 13. Pre-commit y herramientas OCA

```yaml
# .pre-commit-config.yaml (estándar OCA — viene en oca-addons-repo-template)
repos:
  - repo: https://github.com/OCA/odoo-pre-commit-hooks
    rev: v0.0.40
    hooks:
      - id: oca-checks-odoo-module
      - id: oca-checks-po
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks: [{ id: black }]
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks: [{ id: isort }]
  - repo: https://github.com/pycqa/flake8
    rev: 7.1.1
    hooks: [{ id: flake8, additional_dependencies: [flake8-bugbear] }]
  - repo: https://github.com/oca/pylint-odoo
    rev: v9.1.5
    hooks: [{ id: pylint_odoo }]
```

Correr antes de cada commit:

```bash
pre-commit run --all-files
```

## 14. README auto-generado

OCA usa `oca-gen-addon-readme` para componer `README.rst` desde fragmentos en
`readme/`. **No editar `README.rst` manualmente** — editar los fragmentos:

```
readme/
├── DESCRIPTION.rst    # Qué hace el módulo
├── INSTALL.rst        # Instalación no trivial (deps externas, etc.)
├── CONFIGURE.rst      # Configuración post-instalación
├── USAGE.rst          # Uso día a día
├── CONTRIBUTORS.rst   # Lista de contribuidores
├── CREDITS.rst        # Sponsors, créditos especiales
├── ROADMAP.rst        # TODO list
└── HISTORY.rst        # Changelog
```

Comando:

```bash
oca-gen-addon-readme --addons-dir=./l10n_py_edi --branch=18.0 --org=Ezcareaga --repo=l10n-paraguay
```

---

**Referencia completa:** [OCA CONTRIBUTING.rst](https://github.com/OCA/odoo-community.org/blob/master/website/Contribution/CONTRIBUTING.rst)
