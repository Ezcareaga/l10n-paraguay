# l10n-paraguay

Suite de módulos Odoo Community 18 para la localización fiscal de Paraguay
(DNIT/SIFEN).

## Objetivo

Construir el primer set serio de módulos OCA-style para Paraguay, cubriendo:

- Plan de cuentas, impuestos, RUC, regímenes (`l10n_py_base`)
- Tipos de documento, timbrado, secuencias (`l10n_py_account`)
- SIFEN: XML, firma XAdES, SOAP DNIT, CDC, KuDE, eventos (`l10n_py_edi`)
- Libros IVA, Hechauka, RG90 (`l10n_py_reports`)
- POS con SIFEN integrado (`l10n_py_pos`)
- Retenciones IVA/IRE/IRP (`l10n_py_withholding`)

**Audiencia inicial:** PyMEs paraguayas con punto de venta físico (minimarkets,
comercios de barrio, gastronomía pequeña).

## Principios

- Código en inglés, comentarios en español
- Tests obligatorios: unit para lógica de dominio, integration para adaptadores SIFEN
- OCA conventions estrictas (manifest, naming `l10n_py_*`, AGPL-3.0)
- Modelos delgados + helpers Python puros (testables sin levantar Odoo) —
  no arquitecturas paralelas a Odoo
- Documentación viva: cualquier cambio de arquitectura se refleja en `docs/`

## Stack

- Odoo Community 18 (NO Enterprise)
- Python 3.11+
- PostgreSQL 15+
- Librerías SIFEN en Python: `lxml`, `signxml`, `zeep`, `cryptography`, `qrcode`,
  `requests-pkcs12`

## Documentación

TODA la documentación vive en [`docs/`](docs/). Este archivo NO contiene
documentación técnica — solo objetivo + tabla de contenido.

| Sección | Ruta |
|---|---|
| Objetivo extendido | [docs/00_OBJECTIVE.md](docs/00_OBJECTIVE.md) |
| Reglas SIFEN (conceptual) | [docs/01_SIFEN_KNOWLEDGE_BASE.md](docs/01_SIFEN_KNOWLEDGE_BASE.md) |
| Referencia técnica SIFEN | [docs/02_SIFEN_REFERENCIA_COMPLETA.md](docs/02_SIFEN_REFERENCIA_COMPLETA.md) |
| Modelo de dominio | [docs/03_DOMAIN_MODEL.md](docs/03_DOMAIN_MODEL.md) |
| Casos de uso | [docs/04_USE_CASES.md](docs/04_USE_CASES.md) |
| Modelo de datos | [docs/05_DATA_MODEL.md](docs/05_DATA_MODEL.md) |
| Estructura módulo Odoo | [docs/10_ODOO_MODULE_STRUCTURE.md](docs/10_ODOO_MODULE_STRUCTURE.md) |
| ORM Odoo | [docs/11_ODOO_ORM_GUIDE.md](docs/11_ODOO_ORM_GUIDE.md) |
| Vistas Odoo | [docs/12_ODOO_VIEWS_GUIDE.md](docs/12_ODOO_VIEWS_GUIDE.md) |
| Seguridad Odoo | [docs/13_ODOO_SECURITY_GUIDE.md](docs/13_ODOO_SECURITY_GUIDE.md) |
| Testing Odoo | [docs/14_ODOO_TESTING_GUIDE.md](docs/14_ODOO_TESTING_GUIDE.md) |
| Framework `account_edi` | [docs/15_ODOO_ACCOUNT_EDI_FRAMEWORK.md](docs/15_ODOO_ACCOUNT_EDI_FRAMEWORK.md) |
| OCA guidelines | [docs/20_OCA_GUIDELINES.md](docs/20_OCA_GUIDELINES.md) |
| OCA development book | [docs/21_OCA_DEVELOPMENT_BOOK.md](docs/21_OCA_DEVELOPMENT_BOOK.md) |
| `l10n_latam_base` | [docs/30_L10N_LATAM_BASE.md](docs/30_L10N_LATAM_BASE.md) |
| `l10n_latam_invoice_document` | [docs/31_L10N_LATAM_INVOICE_DOCUMENT.md](docs/31_L10N_LATAM_INVOICE_DOCUMENT.md) |
| `l10n_pe` (Peru — patrón EDI) | [docs/32_L10N_PERU_REFERENCE.md](docs/32_L10N_PERU_REFERENCE.md) |
| `l10n_ec` (Ecuador — patrón más cercano) | [docs/33_L10N_ECUADOR_REFERENCE.md](docs/33_L10N_ECUADOR_REFERENCE.md) |
| `l10n_ar` (Argentina — doc types) | [docs/34_L10N_ARGENTINA_REFERENCE.md](docs/34_L10N_ARGENTINA_REFERENCE.md) |
| Librerías Python | [docs/40_PYTHON_LIBRARIES.md](docs/40_PYTHON_LIBRARIES.md) |
| Roadmap de módulos | [docs/50_MODULES_ROADMAP.md](docs/50_MODULES_ROADMAP.md) |

## Búsqueda en código de referencia

Los repos en `references/` están indexados con `codegraph` (SQLite + FTS5 + AST
symbol extraction — implementación Python pura, sin deps externas).

```powershell
# Stats del índice
.\bin\codegraph.ps1 stats

# Buscar en code + docs (full-text)
.\bin\codegraph.ps1 search "account edi format inheritance"
.\bin\codegraph.ps1 search "_post_invoice_edi"

# Símbolos Python (clases, funciones, modelos Odoo)
.\bin\codegraph.ps1 symbol L10nLatamDocumentType
.\bin\codegraph.ps1 symbol _post_invoice_edi

# Símbolos de un archivo específico
.\bin\codegraph.ps1 file "references/odoo-18.0/addons/l10n_ar/models/account_journal.py"

# Listar archivos por patrón
.\bin\codegraph.ps1 files "*l10n_pe*"
```

En POSIX shells: usar `./bin/codegraph` (sin `.ps1`).

**NO leer archivos en `references/` manualmente** — usar el índice (mucho más
rápido y barato en contexto).

Para regenerar el índice (después de actualizar references/ o agregar docs):

```powershell
python scripts/build_index.py
```

## Repos de referencia

| Repo | Tamaño | Propósito |
|---|---|---|
| `references/odoo-18.0/` | 151 MB | Sparse checkout de addons clave Odoo 18 community |
| `references/l10n-peru/` (18.0) | <1 MB | OCA Perú (aún sin port a 18.0) |
| `references/l10n-peru-16.0/` | <1 MB | Idem 16.0 (también vacío — Peru OCA poco activo) |
| `references/l10n-ecuador/` (18.0) | <1 MB | OCA Ecuador 18.0 (solo `l10n_ec_base`) |
| `references/l10n-ecuador-17.0/` | <1 MB | OCA Ecuador 17.0 — material útil (`l10n_ec_account_edi`, etc.) |
| `references/l10n-argentina/` (18.0) | <1 MB | OCA Argentina 18.0 (vacío) |
| `references/l10n-argentina-16.0/` | <1 MB | OCA Argentina 16.0 (módulos AFIP) |
| `references/l10n-brazil/` | 32 MB | OCA Brasil 18.0 — único OCA latam con módulos en 18.0 |
| `references/oca-addons-repo-template/` | <1 MB | Template oficial OCA — referencia para regenerar este repo |
| `references/nandefact/` | 4 MB | Sistema previo SIFEN en Node/TS (referencia conceptual) |

## Estado actual

**Bootstrap completado:** 2026-05-19. Próximo paso: empezar `l10n_py_base`
siguiendo [docs/50_MODULES_ROADMAP.md](docs/50_MODULES_ROADMAP.md) **Fase 1**.

## Para Claude Code en futuras sesiones

- Antes de codear: **leer** [`docs/00_OBJECTIVE.md`](docs/00_OBJECTIVE.md) +
  [`docs/50_MODULES_ROADMAP.md`](docs/50_MODULES_ROADMAP.md) + la fase activa.
- Para encontrar patrones en código existente: **usar `bin/codegraph`** — nunca
  abrir archivos en `references/` manualmente.
- Para entender SIFEN: leer
  [`docs/01_SIFEN_KNOWLEDGE_BASE.md`](docs/01_SIFEN_KNOWLEDGE_BASE.md) primero,
  luego [`docs/02_SIFEN_REFERENCIA_COMPLETA.md`](docs/02_SIFEN_REFERENCIA_COMPLETA.md)
  cuando necesités el detalle técnico.
- Para el setup Odoo en sí: docs/10-15.
- Para convenciones OCA: docs/20-21.
- Para patrones latam (lo más cercano): docs/33 (Ecuador) y docs/34 (Argentina).
