---
source: Síntesis de OCA best practices a partir de OCA/maintainer-tools wiki, repos OCA existentes, y el template oca-addons-repo-template
fetched_at: 2026-05-19
summary: OCA development best practices — Copier template, CI, readme tooling, mig15-mig18 patterns, dependency management.
priority: important
---

# OCA Development Book — practices condensadas

> No existe un "OCA Development Book" oficial publicado como libro. Esta es una
> síntesis de las **best practices observadas** en repos OCA maduros (l10n-spain,
> l10n-brazil, web, server-tools) más el template oficial
> `OCA/oca-addons-repo-template` clonado en `references/`.
>
> Para reglas duras de naming/manifest/security ver [`20_OCA_GUIDELINES.md`](20_OCA_GUIDELINES.md).

## 1. Estructura típica de un repo OCA

Lo que se obtiene de `copier copy gh:OCA/oca-addons-repo-template .`:

```
l10n-paraguay/
├── .copier-answers.yml         # Respuestas al template — drives regen
├── .editorconfig
├── .github/
│   ├── workflows/
│   │   ├── pre-commit.yml      # Lint en cada push
│   │   ├── stale.yml           # Cierra issues/PRs inactivos
│   │   └── test.yml            # Tests con varias DB y Odoo versions
│   └── dependabot.yml
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE                     # AGPL-3
├── README.md                   # Index de los addons del repo
├── pyproject.toml              # tooling config (NO el manifest del módulo)
├── requirements.txt            # Externals Python para CI
├── oca_dependencies.txt        # Deps de otros OCA repos
├── setup/                      # Auto-gen para "pip install" individual de cada addon
│   └── _metapackage/
│       ├── README.rst
│       └── setup.py
└── l10n_py_base/              # ← Módulos individuales en la raíz
    ├── __manifest__.py
    └── ...
```

### `setup/` — para distribución pip

OCA permite instalar addons individuales como paquetes pip:

```bash
pip install odoo-addon-l10n-py-base
```

Esto se hace gracias a la carpeta `setup/<module_name>/` que cada PR genera
automáticamente (vía hook de pre-commit `setuptools-odoo`).

## 2. Copier template — uso y regeneración

```bash
# Primera vez
pip install copier
copier copy gh:OCA/oca-addons-repo-template .

# Re-generar (después de cambios en el template upstream)
copier update
```

Preguntas que hace el template (van a `.copier-answers.yml`):

- `odoo_version`: 18.0
- `repo_slug`: l10n-paraguay
- `repo_name`: Paraguay Localization
- `repo_description`: ...
- `include_wkhtmltopdf`: false (solo para CI con PDFs)
- `dependency_installation_mode`: PIP
- `ci`: GitHub
- `convert_readme_fragments_to_markdown`: true (o false si querés RST)
- `github_check_license`: true
- `github_enable_stale_action`: false (recomendado para evitar cerrar issues
  legítimos)

> Este repo tiene un `.copier-answers.yml` placeholder. Cuando arranque la fase
> 1 (`l10n_py_base`), correr `copier copy` para regenerar la estructura
> oficial (verificar que no rompa los archivos custom que ya creamos).

## 3. CI estándar OCA

### `.github/workflows/test.yml`

Corre tests en matrix de:

- PostgreSQL versions soportadas (15, 16)
- Python versions soportadas (3.11, 3.12, 3.13 si Odoo 18 las soporta)
- Con + sin `oca_dependencies.txt` resuelto

Usa la action `OCA/oca-ci`.

### Pre-commit

Bloquea el commit local si:

- flake8 / black / isort fallan
- `oca-gen-addon-readme` detecta drift entre `readme/` y `README.rst`
- pylint-odoo encuentra issues (rule set OCA)
- Setup setup.py outdated
- Manifest "version" no respeta semver Odoo

## 4. Dependencies entre repos OCA

`oca_dependencies.txt`:

```
# repo-name url-opcional branch-opcional
account-financial-tools https://github.com/OCA/account-financial-tools 18.0
queue
```

El CI clona esos repos al setup. Localmente, `setup_dev.sh` (parte del template)
también los traerá.

## 5. Versionado de módulos en el mismo repo

Reglas observadas en repos maduros:

- Cuando agregás un módulo nuevo: `version = '18.0.1.0.0'`
- Bug fix sin cambio funcional: bump z (`1.0.0` → `1.0.1`)
- Feature nueva no-breaking: bump y (`1.0.0` → `1.1.0`)
- Cambio de schema/data requiere migration: bump x (`1.0.0` → `2.0.0`) + script
  en `migrations/2.0.0/`

## 6. Migrations

Cuando una migration es necesaria:

```
l10n_py_edi/
└── migrations/
    └── 18.0.2.0.0/
        ├── pre-migration.py     # ANTES de cargar el módulo (XML data)
        └── post-migration.py    # DESPUÉS de cargar
```

```python
# post-migration.py
from openupgradelib import openupgrade

def migrate(cr, version):
    if not version:
        return
    # Renombrar column
    openupgrade.rename_columns(cr, {
        'account_move': [('l10n_py_cdc_old', 'l10n_py_cdc')],
    })
```

Dependencia: `openupgradelib` (instalada por CI via requirements).

## 7. `readme/` — fragmentos para `oca-gen-addon-readme`

| Fragmento          | Contenido                                                              |
| ------------------ | ---------------------------------------------------------------------- |
| `DESCRIPTION.rst`  | 1-2 párrafos, qué hace el módulo                                       |
| `INSTALL.rst`      | Solo si hay pasos no-triviales (instalar dep Python, etc.)             |
| `CONFIGURE.rst`    | Setup post-instalación: certificados, credenciales, configuración      |
| `USAGE.rst`        | Cómo usarlo día a día — capturas de pantalla con `static/description/` |
| `CONTRIBUTORS.rst` | Lista de personas (formato fijo OCA)                                   |
| `CREDITS.rst`      | Sponsors / créditos especiales / traductores                           |
| `ROADMAP.rst`      | TODO list pública                                                      |
| `HISTORY.rst`      | Changelog (manual o auto vía towncrier)                                |

### Plantilla `CONTRIBUTORS.rst`

```rst
* Alberto Ezequiel Careaga <careagaezz@gmail.com>
* Odoo Community Association (OCA)
```

## 8. Patterns para módulos puente (bridge modules)

Cuando dos addons existen independientemente pero al instalar ambos
necesitan integración:

```python
# l10n_py_pos/__manifest__.py — bridge entre l10n_py_edi y point_of_sale
{
    'name': 'Paraguay POS — SIFEN',
    'depends': ['l10n_py_edi', 'point_of_sale'],
    'auto_install': True,   # ← instala automáticamente si los 2 deps están
    # ...
}
```

`auto_install=True` (sin lista) significa: "instalar si todas las deps están
satisfechas". Si querés más granularidad: `auto_install=['point_of_sale']`
significa "instalar cuando point_of_sale esté instalado".

## 9. i18n workflow

```bash
# Generar .pot (template) para todos los módulos
odoo-bin --i18n-export=l10n_py_edi/i18n/l10n_py_edi.pot --modules=l10n_py_edi --stop-after-init

# Luego Weblate (translation.odoo-community.org) sincroniza automáticamente
# los .po files contra el .pot
```

OCA conventions:

- Solo commitear `.pot` (template) en PRs
- `.po` (traducciones) los maneja Weblate
- Excepción: módulos nuevos pueden incluir `.po` inicial para idiomas críticos

## 10. Testing patterns observados en repos OCA

| Pattern                                        | Repos donde se ve                        | Cuándo usarlo                                        |
| ---------------------------------------------- | ---------------------------------------- | ---------------------------------------------------- |
| `AccountTestInvoicingCommon` base              | l10n-spain, l10n-brazil, l10n-france     | Cualquier test de accounting/localizations           |
| `MagicMock` para WS externos                   | l10n-spain (SII), l10n-brazil (NFe)      | EDI / SOAP / REST clients                            |
| `@tagged('-standard', 'external_l10n')`        | Todos los OCA con integración real       | Tests E2E contra servicios test reales               |
| Fixture XML en `tests/fixtures/`               | l10n-brazil, account-financial-reporting | Inputs/outputs complejos (XML, JSON, PDFs esperados) |
| `@freeze_time` para fechas determinísticas     | server-tools, sale-workflow              | Sequences, expiration dates, etc.                    |
| `cls.env = cls.env(context=...)` en setUpClass | account-financial-tools                  | Pre-set context (tracking_disable, lang, etc.)       |

## 11. Buenas prácticas misceláneas

### Logging

```python
import logging
_logger = logging.getLogger(__name__)

_logger.debug('SIFEN response: %s', response_dict)
_logger.warning('Reintentando envío de %s', invoice.name)
_logger.error('Falló envío de %s: %s', invoice.name, error, exc_info=True)
```

Reglas:

- `__name__` (no nombre hardcoded)
- Lazy formatting (`%s`, no f-strings) para no formatear si el log level lo descarta
- **Nunca** logguear secretos (CCFE password, tokens, contenidos de cert)

### Performance

- Usar `prefetch_fields` cuando iterás muchos records: `for r in records.with_prefetch():`
- Para reportes pesados: `read_group()` o queries SQL crudas (con parámetros)
- Para batch processing: chunks de 1000 records con `cr.commit()` solo si está OK
  (raro — preferir queue_job de OCA)

### Money / Currency

- `fields.Monetary` exige `currency_field=` y usa la precision de la currency
- Para PYG (sin decimales): la currency Odoo ya tiene `decimal_places=0` —
  asegurar que `res.currency` para PYG está cargada con esta config en
  `l10n_py_base`

## 12. Recursos OCA

| Recurso               | URL                                             |
| --------------------- | ----------------------------------------------- |
| OCA org               | https://github.com/OCA                          |
| Web site              | https://odoo-community.org                      |
| Maintainer tools wiki | https://github.com/OCA/maintainer-tools/wiki    |
| Pre-commit hooks      | https://github.com/OCA/odoo-pre-commit-hooks    |
| Pylint-odoo           | https://github.com/OCA/pylint-odoo              |
| Copier template       | https://github.com/OCA/oca-addons-repo-template |
| Weblate               | https://translation.odoo-community.org          |
| Runboat (CI preview)  | https://runboat.odoo-community.org              |
