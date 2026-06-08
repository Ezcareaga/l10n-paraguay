# l10n-paraguay

[![CI](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/test.yml)
[![pre-commit](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/pre-commit.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/pre-commit.yml)
[![Security](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/security.yml)
[![codecov](https://codecov.io/gh/Ezcareaga/l10n-paraguay/branch/main/graph/badge.svg)](https://codecov.io/gh/Ezcareaga/l10n-paraguay)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Odoo](https://img.shields.io/badge/Odoo-18.0%20Community-714B67.svg)](https://www.odoo.com/)

OCA-style Odoo 18 Community modules for Paraguay fiscal localization (DNIT/SIFEN) —
chart of accounts, IVA taxes, electronic invoicing, withholdings, and IVA books.
97 tests green. AGPL-3.0.

## Available modules

| Module                                       | Version    | Summary                                                                                                                  |
| -------------------------------------------- | ---------- | ------------------------------------------------------------------------------------------------------------------------ |
| [`l10n_py_base`](addons/l10n_py_base/)       | 18.0.1.1.0 | Foundational PY localization: DNIT/SIFEN catalogs, RUC/CI validation (módulo 11), res.company fiscal extension, 23 tests |
| [`l10n_py_account`](addons/l10n_py_account/) | 18.0.1.0.0 | Chart of accounts, IVA taxes (10%/5%/exenta), document types (FE/NC/ND/NR), timbrado, 74 tests                           |
| `l10n_py_edi`                                | planned    | XML SIFEN, XAdES signature, SOAP DNIT, CDC, KuDE, events                                                                 |
| `l10n_py_reports`                            | planned    | IVA books, Hechauka, RG90                                                                                                |
| `l10n_py_pos`                                | planned    | POS with SIFEN integration                                                                                               |
| `l10n_py_withholding`                        | planned    | IVA / IRE / IRP withholdings                                                                                             |

97 tests total (23 + 74). Full roadmap: [`docs/50_MODULES_ROADMAP.md`](docs/50_MODULES_ROADMAP.md).

## Installation

Add `addons/` to your Odoo `addons_path` and install `l10n_py_base` first, then
`l10n_py_account`. Both modules require `l10n_latam_invoice_document` (bundled with
Odoo 18 Community).

```bash
# Example odoo.conf entry
addons_path = /path/to/l10n-paraguay/addons,/path/to/odoo/addons
```

## Quick start

```bash
# 1. Clone
git clone https://github.com/Ezcareaga/l10n-paraguay
cd l10n-paraguay

# 2. Start dev environment
docker compose -f infra/docker-compose.yml up -d

# 3. Create database
# Open http://localhost:8069
# Name: l10n_py_dev | Country: Paraguay | Language: Spanish | Demo data: NO

# 4. Install modules
# Apps menu → search "l10n_py_base" → Install
# Apps menu → search "l10n_py_account" → Install

# 5. Login
# admin / admin  (change on first login)
```

For development setup (pre-commit, references index, running tests) see
[CONTRIBUTING.md](CONTRIBUTING.md).

## Documentation

| Audience                 | Starting point                                                       |
| ------------------------ | -------------------------------------------------------------------- |
| Evaluator / OCA reviewer | [`docs/00_OBJECTIVE.md`](docs/00_OBJECTIVE.md)                       |
| Developer / contributor  | [`CONTRIBUTING.md`](CONTRIBUTING.md)                                 |
| Operator / deployer      | [`docs/71_DEPLOYMENT.md`](docs/71_DEPLOYMENT.md)                     |
| SIFEN implementer        | [`docs/01_SIFEN_KNOWLEDGE_BASE.md`](docs/01_SIFEN_KNOWLEDGE_BASE.md) |
| Architecture overview    | [`docs/70_ARCHITECTURE.md`](docs/70_ARCHITECTURE.md)                 |

Full documentation lives in [`docs/`](docs/).

## Security

To report a vulnerability, see [`SECURITY.md`](SECURITY.md).
The security workflow (gitleaks + Bandit + Dependency Review) runs on every PR.

## License

[AGPL-3.0](LICENSE). Each module inherits this license via its `__manifest__.py`.

## Authorship

**Careaga Dev** ([@Ezcareaga](https://github.com/Ezcareaga)) + OCA community.
