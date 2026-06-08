# Contributing to l10n-paraguay

Thank you for your interest in contributing! This guide covers everything you
need to get started, from setting up the development environment to opening
a pull request.

---

## Development setup

### Prerequisites

- Docker 24+ and Docker Compose v2
- Python 3.11+ (for pre-commit tooling)
- git 2.40+

### First-time setup

```bash
# 1. Clone the repository
git clone https://github.com/Ezcareaga/l10n-paraguay
cd l10n-paraguay

# 2. Start Odoo 18 + PostgreSQL 16 (dev environment)
docker compose -f infra/docker-compose.yml up -d

# 3. Create the dev database (browser)
#    Open http://localhost:8069
#    Name: l10n_py_dev | Country: Paraguay | Language: Spanish | Demo data: NO

# 4. Install modules
#    Apps menu → search "l10n_py_base" → Install
#    Apps menu → search "l10n_py_account" → Install (installs l10n_py_base first)

# 5. Install pre-commit hooks
pip install pre-commit
pre-commit install
```

### Reference index (codegraph)

The `references/` directory contains 190+ MB of Odoo and OCA source code indexed
with a local SQLite + FTS5 + AST engine. **Do not read files in `references/`
manually** — use the codegraph CLI instead:

```powershell
# Stats
.\bin\codegraph.ps1 stats

# Full-text search across code + docs
.\bin\codegraph.ps1 search "account edi format inheritance"
.\bin\codegraph.ps1 search "_post_invoice_edi"

# Python symbol lookup (classes, functions, Odoo models)
.\bin\codegraph.ps1 symbol L10nLatamDocumentType
.\bin\codegraph.ps1 symbol _post_invoice_edi

# List files matching a pattern
.\bin\codegraph.ps1 files "*l10n_pe*"
```

On POSIX shells: use `./bin/codegraph` (without `.ps1`).

To rebuild the index after updating `references/` or adding new docs:

```bash
python scripts/build_index.py
```

---

## CI environment vs local runtime

> The GitHub Actions CI matrix uses `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`
> (Python 3.10, PostgreSQL 12 — OCA standard image). Local development uses the
> `odoo:18.0` upstream image (Python 3.12) with `postgres:16`, as configured in
> `infra/docker-compose.yml`.
>
> Both are supported. If a test passes locally but fails in CI, check for:
>
> - Python 3.10 vs 3.12 syntax differences (e.g., `match` statement not in 3.10)
> - PostgreSQL 12 vs 16 behavior differences (JSON operators, index hints, etc.)

---

## Branch naming

```
feature/* | fix/* | refactor/* | docs/* | chore/*
```

- Branch from `main`.
- Keep branches open **less than 48 hours** — merge or discard.
- One logical change per branch.

---

## Commit messages

Follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
<type>(<scope>): <description>
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`, `style`.

**Examples for this project:**

```
feat(l10n_py_base): add economic_activity model with SIFEN catalog
fix(timbrado): correct expiry_date validation for single-active constraint
docs(contributing): add ADR rule for architectural changes
test(l10n_py_account): cover journal timbrado extension (3 cases)
chore(pre-commit): activate oca-gen-addon-readme baseline
```

Use the module name (e.g., `l10n_py_base`, `l10n_py_account`) or area (e.g.,
`timbrado`, `sifen`, `edi`) as the scope.

---

## Code review

All changes require a pull request against `main`. The PR must pass the following
status checks before merge:

| Status check        | What it verifies                              |
| ------------------- | --------------------------------------------- |
| `pre-commit`        | black, isort, pylint-odoo, flake8, OCA hooks  |
| `test with Odoo`    | 97+ tests green (OCA py3.10/PG12 matrix)      |
| `commitlint`        | Conventional Commits format on all PR commits |
| `gitleaks`          | No secrets committed                          |
| `bandit`            | No HIGH-severity Python security issues       |
| `dependency-review` | No known-vulnerable dependencies introduced   |

All 6 status checks must be green. Resolve all review conversations before
requesting re-review.

---

## Testing

- **Minimum 80% line coverage** for new logic in `models/` and `tools/`.
- Write unit tests in `tests/test_*.py` using `TransactionCase`.
- Run the test suite before every commit:

```bash
docker compose -f infra/docker-compose.yml exec odoo \
  odoo --test-enable --stop-after-init \
  -d l10n_py_dev \
  --test-tags=l10n_py \
  -i l10n_py_base,l10n_py_account
```

- Pre-commit runs linting automatically. Fix all lint errors before pushing.
- Never advance with broken tests — CI will block the PR.

---

## Pre-commit hooks

The following hooks run on every commit:

| Hook ID                      | What it does                                     |
| ---------------------------- | ------------------------------------------------ |
| `black`                      | Python code formatter                            |
| `isort`                      | Import sorter                                    |
| `flake8`                     | PEP 8 style + complexity                         |
| `pylint` (via `pylint-odoo`) | Odoo-specific linting (model naming, api usage)  |
| `oca-gen-addon-readme`       | Regenerates `addons/*/README.rst` from fragments |
| `oca-fix-manifest-website`   | Sets website URL in `__manifest__.py`            |
| Various OCA checks           | Module structure, AGPL-3 header, etc.            |

Install hooks once:

```bash
pip install pre-commit
pre-commit install
```

Run against all files (useful after pulling):

```bash
pre-commit run --all-files
```

---

## Architectural changes

Any change to **module structure**, **data model design**, or **integration strategy**
(including the SIFEN communication layer) requires a new ADR (Architecture Decision
Record) in `docs/adr/` **in the same PR**.

1. Create a new file: `docs/adr/<next-number>-<short-title>.md`
2. Follow the template described in [`docs/adr/README.md`](docs/adr/README.md):
   - If the decision was retroactive and alternatives cannot be reconstructed honestly
     → use Nygard lightweight format
   - If there are real competing options → use MADR format (YAML frontmatter +
     Decision Drivers + Considered Options + Pros/Cons)
3. Set status to `Proposed` when opening the PR; the maintainer changes it to
   `Accepted` after review.
4. Link the ADR from the PR description.

**Examples of architectural changes that require an ADR:**

- Adding a new Odoo model or removing an existing one
- Changing how SIFEN XML is structured or signed
- Switching from one library to another for a core function (e.g., `signxml`)
- Changing the module dependency graph (`depends` in `__manifest__.py`)
- Introducing a new `services/` layer or changing the service contract

---

## Release process

> **Deferred to Phase 4 (REL-06).** The semantic-release vs manual-tag decision
> and the detailed release steps will be documented here once Phase 4 completes.
> For now, releases are tagged manually on `main` after CI passes.

---

## Code of Conduct

This project follows the [Contributor Covenant 2.1](CODE_OF_CONDUCT.md). By
contributing, you agree to abide by its terms.

To report a conduct issue, email `careagaezz@gmail.com` with subject `[CoC]`.
