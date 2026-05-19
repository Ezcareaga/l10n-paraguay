# l10n-paraguay

[![License: AGPL-3](https://img.shields.io/badge/license-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![Odoo](https://img.shields.io/badge/Odoo-18.0%20Community-714B67.svg)](https://www.odoo.com/)
[![Status: Bootstrap](https://img.shields.io/badge/status-bootstrap-orange.svg)](#estado)

Suite de módulos **Odoo Community 18** para la localización fiscal de **Paraguay**
(DNIT / SIFEN — facturación electrónica, plan de cuentas, retenciones, libros IVA).

> Este repositorio es **OCA-style** (mismo layout, manifest y convenciones que
> [OCA/l10n-peru](https://github.com/OCA/l10n-peru) o
> [OCA/l10n-argentina](https://github.com/OCA/l10n-argentina)). Está pensado para ser
> consumible vía `pip` o usable como submódulo en un addons path estándar de Odoo.

## Módulos planificados

| Módulo | Propósito | Estado |
|---|---|---|
| `l10n_py_base` | RUC, regímenes, departamentos/distritos, datos del país | TODO |
| `l10n_py_account` | Plan de cuentas, impuestos, tipos de documento, timbrado | TODO |
| `l10n_py_edi` | XML SIFEN, firma XAdES, SOAP DNIT, CDC, KuDE, eventos | TODO |
| `l10n_py_reports` | Libros IVA, Hechauka, RG90, declaraciones | TODO |
| `l10n_py_pos` | POS con integración SIFEN | TODO |
| `l10n_py_withholding` | Retenciones IVA / IRE / IRP | TODO |

Roadmap completo → [`docs/50_MODULES_ROADMAP.md`](docs/50_MODULES_ROADMAP.md).

## Quick start (para colaboradores)

```powershell
# 1. Clonar
git clone https://github.com/Ezcareaga/l10n-paraguay
cd l10n-paraguay

# 2. (Opcional) Crear venv con tooling de desarrollo
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"

# 3. Clonar los repos de referencia (~190 MB — NO están en este repo)
.\scripts\setup_references.ps1   # PowerShell (Windows)
# o:  ./scripts/setup_references.sh   # bash (Linux/macOS/Git Bash)

# 4. Construir el índice de código (codegraph)
python scripts/build_index.py

# 5. Buscar
.\bin\codegraph.ps1 search "account edi format inheritance"
.\bin\codegraph.ps1 symbol L10nLatamDocumentType
.\bin\codegraph.ps1 file "references/odoo-18.0/addons/l10n_ar/models/account_journal.py"
```

## Documentación

Toda la documentación técnica vive en [`docs/`](docs/). El archivo
[`CLAUDE.md`](CLAUDE.md) es solo un manifiesto corto con objetivo + tabla de
contenido — **no contiene** documentación técnica.

Entradas recomendadas según rol:

- **Nuevo al proyecto** → [`docs/00_OBJECTIVE.md`](docs/00_OBJECTIVE.md)
- **Desarrollando módulos Odoo** → [`docs/10_ODOO_MODULE_STRUCTURE.md`](docs/10_ODOO_MODULE_STRUCTURE.md)
- **Implementando SIFEN** → [`docs/01_SIFEN_KNOWLEDGE_BASE.md`](docs/01_SIFEN_KNOWLEDGE_BASE.md)
- **Revisando para OCA** → [`docs/20_OCA_GUIDELINES.md`](docs/20_OCA_GUIDELINES.md)

## Repos de referencia indexados

En [`references/`](references/) se mantienen *shallow clones* de Odoo core y
otras localizaciones LATAM, indexados para queries via el CLI `codegraph`.
**No leer manualmente** — usar el índice (mucho más rápido y barato en contexto).

| Repo | Propósito |
|---|---|
| `odoo-18.0/` | Sparse checkout de addons clave (`account`, `account_edi`, `l10n_latam_*`, `l10n_pe`, `l10n_pe_edi`, `l10n_ec`, `l10n_ar`, `point_of_sale`, …) |
| `l10n-peru/`, `l10n-ecuador/`, `l10n-argentina/`, `l10n-brazil/` | Repos OCA de localizaciones vecinas |
| `oca-addons-repo-template/` | Template oficial OCA — fuente de `.copier-answers.yml` |
| `nandefact/` | Sistema previo SIFEN en Node/TS del mismo autor — referencia conceptual de dominio |

## Licencia

[AGPL-3.0](LICENSE). Cada módulo individual hereda esta licencia vía su
`__manifest__.py`.

## Autoría

**Careaga Dev** ([@Ezcareaga](https://github.com/Ezcareaga)) + comunidad OCA.

## Estado

Bootstrap inicial completado. Aún no hay código de módulos publicado — el
trabajo activo está en preparar la base de conocimiento y las referencias.
Ver [`docs/50_MODULES_ROADMAP.md`](docs/50_MODULES_ROADMAP.md) para el plan.
