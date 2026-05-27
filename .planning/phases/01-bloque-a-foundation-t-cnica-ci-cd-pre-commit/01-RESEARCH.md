# Phase 1 — Research

**Researched:** 2026-05-27
**Researcher:** gsd-phase-researcher
**Inputs:**
- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` (CI — Bloque A, CI-01..08)
- `.planning/ROADMAP.md` (Phase 1)
- `.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/01-CONTEXT.md` (D-01..D-16)
- `docs/55_PRE_FASE_2_FOUNDATION.md` (referenced indirectly via REQs)
- `CLAUDE.md` (project) + `~/.claude/CLAUDE.md` (global)
- `pyproject.toml` (existing black/isort/dev config)
- `addons/l10n_py_base/__manifest__.py` + `addons/l10n_py_account/__manifest__.py`
- `addons/l10n_py_base/tests/test_ruc_validation.py`, `test_company_setup.py`
- `addons/l10n_py_account/tests/test_pyme_e2e.py`
- `references/l10n-brazil/.pre-commit-config.yaml`
- `references/l10n-brazil/.github/workflows/pre-commit.yml`
- `references/l10n-brazil/.github/workflows/test.yml`
- `references/l10n-brazil/.copier-answers.yml`
- `references/oca-addons-repo-template/src/.pre-commit-config.yaml.jinja`
- `references/oca-addons-repo-template/src/.github/workflows/pre-commit.yml.jinja`
- `references/oca-addons-repo-template/src/.github/workflows/test.yml.jinja`
- `references/oca-addons-repo-template/.github/dependabot.yml`
- Web (HIGH confidence — official repos): `github.com/OCA/odoo-pre-commit-hooks@v0.0.33`, `github.com/OCA/maintainer-tools@b89f767`, `github.com/OCA/pylint-odoo@v9.1.3`, `github.com/wagoid/commitlint-github-action`, `github.com/codecov/codecov-action`, `docs.github.com` dependabot reference

---

## Summary

- **`oca-fix-manifest-version` does NOT exist** in the OCA hook ecosystem at the pinned versions (D-02). REQ CI-01's literal text contains an error — likely a conflation with `oca-fix-manifest-website` (exists, fixes the `website` field) and `manifest-version-format` (a **read-only check** inside `pylint-odoo`). Current manifests (`18.0.1.1.0` and `18.0.1.0.0`) already match the format `pylint-odoo` validates. **D-08 is moot — no auto-bump hook exists.** Plan should swap `oca-fix-manifest-version` for the pair `oca-fix-manifest-website` + (implicit) `pylint-odoo` `manifest-version-format` check.
- **`oca-checks-odoo-module`** (from `OCA/odoo-pre-commit-hooks v0.0.33`) is the right hook for OCA module structural checks. It is read-only (no auto-fix).
- **OCA Brazil 18.0 actually uses `ruff` (not black+isort+flake8)** and a Python **3.10** OCA-CI container (`ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`) with **PostgreSQL 12**. D-11 says Python 3.11 × PG 16; the OCA-standard path collides with this. Recommendation: **follow OCA-standard** (3.10 + PG 12) for CI to maximize compatibility with `oca_install_addons` / `oca_run_tests` helpers — runtime in production can still be 3.11+/PG15+. Flagged as a config decision the planner should confirm with the user (one-line clarify).
- **Test tag pattern is already consistent**: every test in both addons uses `@tagged("post_install", "-at_install", "l10n_py")` literal. D-10's proposed default tag selector `--test-tags=l10n_py,-l10n_py_external,-standard` is correct — but with the OCA-CI runner the env var the script reads is `INCLUDE`/`EXCLUDE`, not raw `--test-tags`. Equivalent setup documented below.
- **`commitlint`** standard pin = `wagoid/commitlint-github-action@v6` (latest stable, single-action — no node deps locally).
- **Codecov action** at production-recommended is `codecov/codecov-action@v5` (Brazil pins `@v4`; v5 is current major).

## Resolutions

### R-01: D-08 oca-fix-manifest-version edge

- **Decision:** **The hook does not exist. Replace with the pair `oca-fix-manifest-website` (auto-fix, sets the `website` URL) + `pylint-odoo`'s read-only `manifest-version-format` check (already in stack via pylint-odoo).** No version auto-bump will happen anywhere. CI-01's literal `oca-fix-manifest-version` is a typo/conflation that must be documented in the plan (it should NOT be silently included as a hook id — pre-commit will fail with "hook not found").
- **Evidence:**
  - `references/l10n-brazil/.pre-commit-config.yaml:51-55` — `oca/maintainer-tools @ b89f767` exposes `oca-update-pre-commit-excluded-addons`, `oca-fix-manifest-website`, `oca-gen-addon-readme`, `oca-gen-external-dependencies`. **No `oca-fix-manifest-version`.**
  - WebFetch `github.com/OCA/maintainer-tools/blob/b89f767.../.pre-commit-hooks.yaml` — confirms hook list above; no manifest-version hook.
  - WebFetch `github.com/OCA/odoo-pre-commit-hooks/tree/v0.0.33` README — only `oca-checks-odoo-module` and `oca-checks-po` are exposed at this tag.
  - WebFetch `github.com/OCA/pylint-odoo` docs — check id `manifest-version-format` (C8106) enforces regex `(...|18.0|19.0)\.\d+\.\d+\.\d+$` and is **read-only**.
  - `addons/l10n_py_base/__manifest__.py:4` — `"version": "18.0.1.1.0"` matches the regex.
  - `addons/l10n_py_account/__manifest__.py:4` — `"version": "18.0.1.0.0"` matches the regex.
- **Config snippet** (what gets used instead of the non-existent hook):
  ```yaml
  - repo: https://github.com/oca/maintainer-tools
    rev: b89f767503be6ab2b11e4f50a7557cb20066e667
    hooks:
      - id: oca-fix-manifest-website
        args: ["https://github.com/Ezcareaga/l10n-paraguay"]
  # The version-format guarantee comes from pylint-odoo (separate repo, below)
  - repo: https://github.com/OCA/pylint-odoo
    rev: v9.1.3
    hooks:
      - id: pylint_odoo
        args: ["--rcfile=.pylintrc-mandatory"]
        # manifest-version-format (C8106) is mandatory by default in this rcfile
  ```
- **Planner note:** Update REQ CI-01 acceptance check to list `oca-fix-manifest-website` + `manifest-version-format (via pylint-odoo)` instead of `oca-fix-manifest-version`. The REQ text itself stays locked, but the verification step must point to what actually exists.

### R-02: D-09 OCA action de install Odoo

- **Decision:** Use the OCA-CI **container image** approach (not a marketplace action). Brazil's `test.yml` runs the job inside `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`, which ships `oca_install_addons`, `oca_init_test_database`, `oca_run_tests`, and `manifestoo`. There is no separate `oca/oca-ci` action — `oca-ci` IS the container.
- **Evidence:**
  - `references/l10n-brazil/.github/workflows/test.yml:30-67` — job runs in `container: ${{ matrix.container }}` with values from `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`. Steps invoke `oca_install_addons`, `oca_init_test_database`, `oca_run_tests` (binaries inside the image).
  - `references/oca-addons-repo-template/src/.github/workflows/test.yml.jinja:13-39` — canonical IMAGES dict; `18.0 → ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`, also `py3.10-ocb18.0` for OCB (Odoo Community Backports).
  - Image source: `github.com/OCA/oca-ci` (verified URL pattern matches the published GHCR namespace).
- **Container handles deps automatically** via `oca_install_addons` which scans manifests; for our case it will resolve `l10n_latam_base` and `l10n_latam_invoice_document` from the OCA `l10n-latam` repo if its `requirements.txt` / `test-requirements.txt` is configured. We don't have those yet — script will fall back to `apt`/`pip` resolution; manifests already declare the deps so they get installed from the bundled Odoo source tree if available, or via `pip` from a sibling repo.
- **Required inputs/secrets:**
  - `CODECOV_TOKEN` — repo secret, free Codecov account (D-15).
  - No other secrets for the green-path test job. `GIT_PUSH_TOKEN` only required for the `oca_export_and_push_pot` step (skipped for our repo — not OCA-owned yet).
- **Fallback if the container becomes unmaintained:** Switch to direct pip install (`pip install odoo==18.0.* psycopg2`), bind-mount the addons path, run `odoo --test-enable --stop-after-init -i l10n_py_base,l10n_py_account --test-tags=...`. Verbose YAML but no external dep. Document fallback in `.github/workflows/test.yml` as a comment near the container line.
- **Python/PG mismatch with D-11:** OCA-CI image is **py3.10 + PG12**, D-11 specified 3.11 + PG16. Two options:
  - **A (recommended):** Drop D-11 in favor of OCA-CI defaults (3.10 / PG12) — same versions Brazil tests against; lowest divergence cost; aligns with future OCA upstreaming.
  - **B:** Override container's Python by `apt`/`uv` step OR run pure pip-install (skip container entirely). Higher maintenance cost, breaks alignment with OCA tooling.
  - Planner: surface this as a planner question to user before committing the test.yml. Provided literal YAML below uses **Option A** as the default.

### R-03: Test tags audit (supports D-10)

- **Evidence — `addons/l10n_py_base/tests/test_ruc_validation.py:10`:**
  ```python
  @tagged("post_install", "-at_install", "l10n_py")
  class TestRucValidation(TransactionCase):
  ```
- **Evidence — `addons/l10n_py_base/tests/test_company_setup.py:10`:**
  ```python
  @tagged("post_install", "-at_install", "l10n_py")
  class TestCompanySetup(TransactionCase):
  ```
- **Evidence — `addons/l10n_py_account/tests/test_pyme_e2e.py:10`:**
  ```python
  @tagged("post_install", "-at_install", "l10n_py")
  class TestPymeE2E(L10nPyAccountTestCase):
  ```
- **Conclusion:** D-10's proposed tags `("l10n_py", "post_install", "-at_install")` are **already in use** across all 97 tests. No code change needed on the test side. The CI test-tags selector `--test-tags=l10n_py,-l10n_py_external,-standard`:
  - `l10n_py` → matches our local tests ✓
  - `-l10n_py_external` → excludes any future test marked `l10n_py_external` (not yet present; Fase 2 EDI will add them)
  - `-standard` → excludes Odoo core's default suite (everything that doesn't carry our `l10n_py` tag is implicitly excluded already; `-standard` is the safe canonical exclude string for OCA addons)
- **OCA-CI invocation:** Inside `oca_run_tests`, the test-tags string is read from env var `INCLUDE` and `EXCLUDE` (see `oca-addons-repo-template` test.yml jinja lines 42-48 for the `rebel_module_groups` pattern). For a single-job (non-rebel) setup, simply pass extra args via `OCA_TEST_TAGS` is not the canonical mechanism — `oca_run_tests` defaults to running every test in installed addons. Recommendation: set `OCA_ENABLE_CHECKLOG_ODOO=1` (per Brazil) and override the `--test-tags` value via `ODOO_TEST_TAGS` env var (consumed by `oca_run_tests` per `oca-ci` source convention). If the env var isn't honored, fallback is to invoke `odoo --test-tags=...` directly after `oca_init_test_database`.

### R-04: `.coveragerc` final (D-16)

- **Decision:** Per D-16 — scope `addons/l10n_py_*` only, exclude tests/data/manifests/inits/scripts/bin.
- **Literal content:** see Deliverables § `.coveragerc` below.
- **Output dirs:** `coverage.xml` at repo root (for codecov upload) + `htmlcov/` for local exploration.

### R-05: `.pre-commit-config.yaml` hand-roll

- **Decision:** Hand-roll from `references/l10n-brazil/.pre-commit-config.yaml` pruning to CI-01 set, adding codespell + yamllint (NOT in Brazil), keeping prettier+plugin-xml, dropping eslint+whool+oca-gen-addon-readme+ruff (per D-03 — CI-01 lists black/isort/flake8 separate, not ruff).
- **Pins (all sourced from `oca-addons-repo-template@v1.41` `odoo_version < 19` block, lines 79-98):**
  - `oca/maintainer-tools` → `b89f767503be6ab2b11e4f50a7557cb20066e667` ([line 88](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L88))
  - `OCA/odoo-pre-commit-hooks` → `v0.0.33` ([line 90](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L90))
  - `OCA/pylint-odoo` → `v9.1.3` ([line 94](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L94))
  - `pre-commit/pre-commit-hooks` → `v4.6.0` ([line 91](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L91))
  - `psf/black` → `22.8.0` ([line 81](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L81))
  - `PyCQA/isort` → `5.12.0` ([line 87](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L87))
  - `PyCQA/flake8` → `3.9.2` ([line 84](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L84))
  - `prettier` → `3.3.3`, `@prettier/plugin-xml` → `3.4.1` ([lines 92-93](references\oca-addons-repo-template\src\.pre-commit-config.yaml.jinja#L92))
  - `codespell` → `v2.4.2` (verified via WebFetch `github.com/codespell-project/codespell` — latest stable as of 2026-03-05)
  - `yamllint` → `v1.38.0` (verified via WebFetch `github.com/adrienverge/yamllint` — latest stable as of 2026-01-13)
- **Literal content:** see Deliverables § `.pre-commit-config.yaml` below.
- **`pyproject.toml` reuse:** `[tool.black]` and `[tool.isort]` already in `pyproject.toml` lines 53-62. The pre-commit hooks for black and isort pick up these settings automatically (black reads `[tool.black]`, isort reads `[tool.isort]`).

### R-06: 3 workflow YAML files

- **Triggers (all 3 workflows):** `pull_request: branches: [main]` + `push: branches: [main]` per D-12.
- **`pre-commit.yml`:** thin clone of Brazil's `pre-commit.yml` (`references/l10n-brazil/.github/workflows/pre-commit.yml`) — `actions/checkout@v4`, `actions/setup-python@v5` with Python 3.12 (matches `default_language_version` of the OCA template at `repo_rev.python = python3.12` for `18.0`-pinned ecosystem), pip cache, pre-commit run with `--show-diff-on-failure`. Drops the `SKIP: oca-gen-addon-readme` env (we don't run that hook).
- **`test.yml`:** thin clone of Brazil's `test.yml` running inside `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest` (per R-02). One job (matrix `include` with a single entry — matches D-11's "1 job in matrix"). Services: `postgres:12` (per OCA template line 127). Steps: checkout → `oca_install_addons` → `manifestoo` license/dev-status checks → `oca_init_test_database` → `oca_run_tests` (with `OCA_TEST_TAGS=/l10n_py,-l10n_py_external,-standard` env var per R-03) → `codecov/codecov-action@v5` (per WebFetch — current recommended). Drops `oca_export_and_push_pot` (only relevant for OCA-owned repos pushing translations back).
- **`commitlint.yml`:** standalone job using `wagoid/commitlint-github-action@v6` (verified WebFetch — latest stable). Validates the **commits in the PR** (`HEAD..origin/main`) and the **PR title** separately.
- **Literal content:** see Deliverables § workflows below.

### R-07: `commitlint.config.js`

- **Standard:** `@commitlint/config-conventional` extends with the type list spec'd in user's question (feat, fix, refactor, test, docs, chore, style, perf, build, ci, revert). Scopes are **enforced as enum** (so we cap to the requested set: `l10n_py_base`, `l10n_py_account`, `pre-commit`, `ci`, `docs`, plus empty `""` via `subject-empty: [0]` style scope-empty rule).
- **No node_modules needed locally:** `wagoid/commitlint-github-action` ships its own commitlint runtime, but the `commitlint.config.js` must be valid CommonJS in the repo root.
- **Literal content:** see Deliverables § `commitlint.config.js` below.

### R-08: `.github/dependabot.yml`

- **Per D-15 + GitHub docs (WebFetch `docs.github.com`):**
  - Ecosystem 1: `pip` (for `pyproject.toml`) — `directory: "/"`, weekly Monday morning. **Note:** OCA template uses `uv` ecosystem (newer); we use `pip` per CI-05 wording and because the repo doesn't have a `uv.lock`. WebFetch confirmed both are valid for pyproject.toml.
  - Ecosystem 2: `github-actions` — `directory: "/"`, weekly Monday morning.
- **Groups per ecosystem:** Per D-15 — one group per ecosystem to consolidate weekly PRs. Pip → "python-deps" group; github-actions → "actions-deps" group.
- **No auto-merge** (deferred per CONTEXT § Deferred Ideas).
- **Schedule day:** Monday is the safe default — early-week PR triage; weekend updates are batched.
- **Literal content:** see Deliverables § `dependabot.yml` below.

### R-09: CI-07 branch protection — required status check names

The `job:` block names from the 3 workflows are the canonical status check identifiers GitHub Branch Protection requires.

- `pre-commit.yml` → job name **`pre-commit`** (top-level `jobs.pre-commit`).
- `test.yml` → job name **`test`** (top-level `jobs.test`), but matrix expansion produces a display name like `test (test with Odoo)` from the `name: ${{ matrix.name }}` field. With a single matrix entry, GitHub will report the check as `test / test (test with Odoo)`. **Branch protection requires the exact display name.**
- `commitlint.yml` → job name **`commitlint`** (top-level `jobs.commitlint`).

**Suggested required checks list in branch protection UI:**
- `pre-commit` (from `pre-commit` job)
- `test (test with Odoo)` (from `test` job, matrix-expanded display)
- `commitlint` (from `commitlint` job)

**`gh` CLI snippet to set protection programmatically:**
```bash
gh api -X PUT repos/Ezcareaga/l10n-paraguay/branches/main/protection \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "pre-commit"},
      {"context": "test (test with Odoo)"},
      {"context": "commitlint"}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
```
- `enforce_admins: true` enforces the rule on `@Ezcareaga` too (CI-07 requirement: "incluso owner").
- `required_approving_review_count: 0` — solo dev, no second reviewer mandatory; conversation resolution still required.
- Run this **after** the 3 workflows have appeared at least once in GitHub Actions UI (otherwise the API returns "Check 'X' is not registered yet"). CI-08 PR de prueba doubles as the trigger.

### R-10: CI-08 PR de prueba scope

- **Recommendation:** Add a one-line entry to a new file `CHANGES.rst` at the **repo root**, content `- Initial CI sanity check (Phase 1 / chore: ci sanity check).` and commit on branch `chore/ci-sanity-check`. PR title: `chore: ci sanity check`. Body: 2 lines.
- **Why this over editing a manifest comment:**
  - Adding `CHANGES.rst` is **net-neutral semantically** (no addon behavior change) — pre-commit hooks won't reformat it aggressively (rst trailing whitespace + EOF newline is all).
  - Touching `__manifest__.py` would trigger `oca-fix-manifest-website` re-write if the URL drifts, possibly re-running `pylint-odoo` checks. PR could fail for an unrelated reason.
  - `CHANGES.rst` is a **convention OCA expects** for addons at the repo level when not bundling with copier — it slots in cleanly with Phase 3 DOC-02 future work (CHANGELOG.md per addon vs. root CHANGES.rst).
- **Alternative if user prefers minimal:** A comment-only edit to `pyproject.toml` (e.g., add a `# ci sanity check` line) — also net-neutral; pre-commit ignores comments.

### R-11: Codecov setup (D-13/D-14/D-15)

- **Brazil's literal usage** (`references/l10n-brazil/.github/workflows/test.yml:75-77`):
  ```yaml
  - uses: codecov/codecov-action@v4
    with:
      token: ${{ secrets.CODECOV_TOKEN }}
  ```
- **Decision:** Pin to **`@v5`** (codecov current major per WebFetch `github.com/codecov/codecov-action` — "@v5 is recommended"). Brazil is one major behind but compat is preserved.
- **Token storage:** Repo secret `CODECOV_TOKEN`. Free tier for private repos: includes 1 repo + unlimited contributors at zero cost. Setup procedure:
  1. Visit `https://app.codecov.io/gh/Ezcareaga/l10n-paraguay` and sign in with GitHub OAuth.
  2. Copy the upload token shown ("Repository Upload Token").
  3. In GitHub: Settings → Secrets and variables → Actions → New repository secret → Name `CODECOV_TOKEN`, value = token from step 2.
- **No coverage gate** (D-13). Codecov posts comments on PRs by default — no `fail_ci_if_error` flag (would convert it from informational to blocking).
- **Coverage file location:** `coverage.xml` at repo root (default from `oca_run_tests`, which calls `coverage xml -o coverage.xml`). Codecov auto-detects.
- **Literal step YAML:**
  ```yaml
  - name: Upload coverage to Codecov
    uses: codecov/codecov-action@v5
    if: ${{ always() }}
    with:
      token: ${{ secrets.CODECOV_TOKEN }}
      files: ./coverage.xml
      flags: unittests
      fail_ci_if_error: false
      verbose: true
  ```
- **README badge** (per D-13 — sumar 3 badges):
  - CI status: `![CI](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/test.yml/badge.svg?branch=main)`
  - Pre-commit lint: `![pre-commit](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/pre-commit.yml/badge.svg?branch=main)`
  - Codecov: `![Coverage](https://codecov.io/gh/Ezcareaga/l10n-paraguay/branch/main/graph/badge.svg)`
  - License: `![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)`
  - These 3-4 badges only — per CONTEXT, the real README rewrite is Phase 3 DOC-01.

---

## Deliverables (literal content for planner)

### `.pre-commit-config.yaml`

```yaml
# Pre-commit configuration for l10n-paraguay (Odoo 18.0 Community)
# Hand-rolled from references/l10n-brazil/.pre-commit-config.yaml (OCA 18.0)
# Pins sourced from OCA copier template @ v1.41 (odoo_version < 19 block).
# CI-01 hook set: black, isort, flake8, pylint-odoo, oca-checks-odoo-module,
# (oca-fix-manifest-version replaced with oca-fix-manifest-website +
#  manifest-version-format via pylint-odoo — see RESEARCH R-01), codespell,
# yamllint, prettier+plugin-xml (D-03 addition).

exclude: |
  (?x)
  # Vendored references — prohibido tocar (CLAUDE.md del repo)
  ^references/|
  # Catálogos DNIT canónicos generados por scripts/
  ^addons/[^/]+/data/.*\.csv$|
  # Formato custom GSD para PROJECT.md
  ^\.planning/PROJECT\.md$|
  # Files we don't want pre-commit to mess with
  \.svg$|
  ^README\.rst$|
  (LICENSE.*|COPYING.*)

default_language_version:
  python: python3.12
  node: "22.9.0"

repos:
  # -- Local fail-fast hooks ----------------------------------------------
  - repo: local
    hooks:
      - id: forbidden-files
        name: forbidden files
        entry: found forbidden files; remove them
        language: fail
        files: "\\.rej$"

  # -- OCA maintainer-tools (manifest website + utility) ------------------
  - repo: https://github.com/oca/maintainer-tools
    rev: b89f767503be6ab2b11e4f50a7557cb20066e667
    hooks:
      - id: oca-fix-manifest-website
        args: ["https://github.com/Ezcareaga/l10n-paraguay"]

  # -- OCA module structural checks (read-only) ---------------------------
  - repo: https://github.com/OCA/odoo-pre-commit-hooks
    rev: v0.0.33
    hooks:
      - id: oca-checks-odoo-module
      - id: oca-checks-po
        args: ["--disable=po-pretty-format"]

  # -- Black (reads [tool.black] from pyproject.toml) ---------------------
  - repo: https://github.com/psf/black
    rev: 22.8.0
    hooks:
      - id: black

  # -- isort (reads [tool.isort] from pyproject.toml) ---------------------
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        name: isort except __init__.py
        args: ["--settings=."]
        exclude: /__init__\.py$

  # -- flake8 -------------------------------------------------------------
  - repo: https://github.com/PyCQA/flake8
    rev: 3.9.2
    hooks:
      - id: flake8
        additional_dependencies: ["flake8-bugbear==21.9.2"]

  # -- pylint-odoo (also enforces manifest-version-format C8106) ---------
  - repo: https://github.com/OCA/pylint-odoo
    rev: v9.1.3
    hooks:
      - id: pylint_odoo
        name: pylint with optional checks (informational)
        args:
          - --rcfile=.pylintrc
          - --exit-zero
        verbose: true
      - id: pylint_odoo
        name: pylint mandatory checks
        args: ["--rcfile=.pylintrc-mandatory"]

  # -- codespell (typos) --------------------------------------------------
  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.2
    hooks:
      - id: codespell
        additional_dependencies: ["tomli"]

  # -- yamllint -----------------------------------------------------------
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        args: ["-c=.yamllint"]

  # -- prettier (with plugin-xml) — D-03 addition -------------------------
  - repo: local
    hooks:
      - id: prettier
        name: prettier (with plugin-xml)
        entry: prettier
        args:
          - --write
          - --list-different
          - --ignore-unknown
        types: [text]
        files: \.(css|htm|html|js|json|jsx|less|md|scss|toml|ts|xml|yaml|yml)$
        language: node
        additional_dependencies:
          - "prettier@3.3.3"
          - "@prettier/plugin-xml@3.4.1"

  # -- Standard pre-commit-hooks (whitespace, EOL, syntax) ----------------
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
        exclude: /README\.rst$|\.pot?$
      - id: end-of-file-fixer
        exclude: /README\.rst$|\.pot?$
      - id: debug-statements
      - id: check-case-conflict
      - id: check-docstring-first
      - id: check-merge-conflict
        exclude: /README\.rst$|^docs/.*\.rst$
      - id: check-symlinks
      - id: check-xml
      - id: mixed-line-ending
        args: ["--fix=lf"]
```

**Companion files** required by the config (planner must create them in the same phase):

`.pylintrc` and `.pylintrc-mandatory` — pylint-odoo expects these. Minimal viable: copy from `references/oca-addons-repo-template/src/.pylintrc.jinja` and `.pylintrc-mandatory.jinja` rendered for `odoo_version=18.0` (or copy Brazil's). Researcher recommends copying Brazil's exactly since they live under `references/l10n-brazil/.pylintrc` and `.pylintrc-mandatory` (verify file presence in plan step; if absent there too, render from jinja).

`.yamllint` — minimal config:
```yaml
extends: default
rules:
  line-length:
    max: 120
    level: warning
  truthy:
    check-keys: false  # GitHub Actions uses `on:` key which yamllint flags as truthy
  document-start: disable
```

### `.github/workflows/pre-commit.yml`

```yaml
name: pre-commit

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  pre-commit:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: 'pip'
          cache-dependency-path: '.pre-commit-config.yaml'

      - name: Setup Node.js (for prettier)
        uses: actions/setup-node@v4
        with:
          node-version: "22.9.0"

      - name: Get python version hash
        run: echo "PY=$(python -VV | sha256sum | cut -d' ' -f1)" >> $GITHUB_ENV

      - uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit|${{ env.PY }}|${{ hashFiles('.pre-commit-config.yaml') }}

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Run pre-commit
        run: pre-commit run --all-files --show-diff-on-failure --color=always

      - name: Check that all files generated by pre-commit are in git
        run: |
          newfiles="$(git ls-files --others --exclude-from=.gitignore)"
          if [ "$newfiles" != "" ] ; then
            echo "Please check-in the following files:"
            echo "$newfiles"
            exit 1
          fi
```

### `.github/workflows/test.yml`

```yaml
name: tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-22.04
    container: ${{ matrix.container }}
    name: ${{ matrix.name }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - container: ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest
            name: test with Odoo
    services:
      postgres:
        image: postgres:12
        env:
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
          POSTGRES_DB: odoo
        ports:
          - 5432:5432
    env:
      OCA_ENABLE_CHECKLOG_ODOO: "1"
      # Restrict test selection to l10n_py tests, skip externals + Odoo core
      ODOO_TEST_TAGS: "/l10n_py,-l10n_py_external,-standard"
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - name: Install addons and dependencies
        run: oca_install_addons

      - name: Check licenses
        run: manifestoo -d . check-licenses

      - name: Check development status
        run: manifestoo -d . check-dev-status --default-dev-status=Beta
        continue-on-error: true   # Beta is fine; do not block during Pre-Fase 2

      - name: Initialize test database
        run: oca_init_test_database

      - name: Run tests
        run: oca_run_tests

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v5
        if: ${{ always() }}
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          flags: unittests
          fail_ci_if_error: false
          verbose: true

      - name: Upload screenshots from JS tests (on failure)
        if: ${{ failure() }}
        uses: actions/upload-artifact@v4
        with:
          name: screenshots-${{ matrix.name }}
          path: /tmp/odoo_tests/${{ env.PGDATABASE }}
          if-no-files-found: ignore
```

### `.github/workflows/commitlint.yml`

```yaml
name: commitlint

on:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: read

jobs:
  commitlint:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0   # commitlint needs full history to diff PR commits

      - name: Validate PR commits
        uses: wagoid/commitlint-github-action@v6
        with:
          configFile: commitlint.config.js
          firstParent: false
          failOnWarnings: false
          helpURL: https://www.conventionalcommits.org

      - name: Validate PR title (Conventional Commits)
        uses: wagoid/commitlint-github-action@v6
        with:
          configFile: commitlint.config.js
          # The `title` event is implicit — wagoid validates PR title when
          # github.event_name == 'pull_request'. No extra param needed.
```

### `commitlint.config.js`

```javascript
// Conventional Commits config for l10n-paraguay.
// Consumed by .github/workflows/commitlint.yml (wagoid/commitlint-github-action@v6).
// Locally usable with `npx commitlint --from=origin/main`.

module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [
      2,
      'always',
      [
        'feat',     // new feature
        'fix',      // bug fix
        'refactor', // code change neither feat nor fix
        'test',     // adding / fixing tests
        'docs',     // documentation only
        'chore',    // tooling, infra, no code change
        'style',    // formatting, no semantic change
        'perf',     // performance improvement
        'build',    // build system / dependencies
        'ci',       // CI/CD config
        'revert',   // revert previous commit
      ],
    ],
    'scope-enum': [
      1,  // 1 = warning (not error) — scope is optional
      'always',
      [
        'l10n_py_base',
        'l10n_py_account',
        'pre-commit',
        'ci',
        'docs',
        '',  // allow empty scope
      ],
    ],
    'subject-case': [2, 'never', ['upper-case', 'pascal-case', 'start-case']],
    'header-max-length': [2, 'always', 100],
    'body-leading-blank': [2, 'always'],
    'footer-leading-blank': [2, 'always'],
  },
};
```

**Note:** `@commitlint/config-conventional` is the extends target — the action ships with it built-in (no `package.json` needed at the repo root for CI). If user wants local pre-commit hook later, add `package.json` with `npm install --save-dev @commitlint/{cli,config-conventional}`.

### `.github/dependabot.yml`

```yaml
# Dependabot config for l10n-paraguay.
# Two ecosystems: pip (pyproject.toml dev deps) + github-actions (workflows).
# Weekly schedule, grouped PRs per ecosystem, no auto-merge (deferred to Pre-Fase 3).

version: 2

updates:
  # Python dev dependencies declared in pyproject.toml
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "06:00"
      timezone: "America/Asuncion"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "build"
      include: "scope"
    labels:
      - "dependencies"
      - "python"
    groups:
      python-deps:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"

  # GitHub Actions versions in .github/workflows/*.yml
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "06:00"
      timezone: "America/Asuncion"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "ci"
      include: "scope"
    labels:
      - "dependencies"
      - "github-actions"
    groups:
      actions-deps:
        patterns:
          - "*"
```

### `.coveragerc`

```ini
# Coverage scope (D-16): addons/l10n_py_* only.
# Excludes tests, data files, manifest/init boilerplate, scripts and bin/.

[run]
branch = True
source =
    addons/l10n_py_base
    addons/l10n_py_account
    # Future addons (un-comment as added):
    # addons/l10n_py_edi
    # addons/l10n_py_reports
    # addons/l10n_py_pos
    # addons/l10n_py_withholding
omit =
    addons/*/tests/*
    addons/*/data/*
    addons/*/demo/*
    addons/*/__manifest__.py
    addons/*/__init__.py
    addons/*/migrations/*
    addons/*/wizards/*_views.xml
    scripts/*
    bin/*
parallel = True
relative_files = True

[report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    \.\.\.

[html]
directory = htmlcov
title = l10n-paraguay coverage report

[xml]
output = coverage.xml
```

### Required status check names for CI-07

After the 3 workflows have run **at least once** on `main` (CI-08 PR de prueba triggers this), configure branch protection at `Settings → Branches → Add rule` with these required status checks:

- `pre-commit` (from `.github/workflows/pre-commit.yml` → job `pre-commit`)
- `test (test with Odoo)` (from `.github/workflows/test.yml` → job `test`, expanded with matrix `name: ${{ matrix.name }} = "test with Odoo"`)
- `commitlint` (from `.github/workflows/commitlint.yml` → job `commitlint`)

**`gh api` reproducible snippet:**

```bash
gh api -X PUT repos/Ezcareaga/l10n-paraguay/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "pre-commit"},
      {"context": "test (test with Odoo)"},
      {"context": "commitlint"}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
```

CI-07 explicit knobs translated:
- "PR required (incluso owner)" → `enforce_admins: true` + `required_approving_review_count: 0` (PR required but no second approver mandatory).
- "status checks (lint + tests) must pass" → 3 `checks` listed above.
- "conversation resolution required" → `required_conversation_resolution: true`.
- "no force push" → `allow_force_pushes: false`.

---

## Unresolved / Risks

- **R-02 Python/PG version mismatch (D-11 vs OCA-CI default).** D-11 specifies Python 3.11 × PG 16; OCA-CI 18.0 image is py3.10 + PG12. Recommendation: drop D-11 in favor of OCA defaults (3.10/12) so `oca_install_addons` and `oca_run_tests` work out-of-the-box. **Verification path:** planner adds a short confirmation step or surfaces this to user before locking `test.yml`. If user insists on 3.11 + PG16, fallback YAML uses bare `setup-python@v5` + `services.postgres.image: postgres:16` + manual `pip install odoo psycopg2` (added complexity).
- **R-03 `ODOO_TEST_TAGS` env var convention.** OCA-CI's `oca_run_tests` is documented but its exact env var name for test-tags injection isn't published in the canonical README I could reach via WebFetch. Planner should confirm by either (a) cloning `OCA/oca-ci` and grepping the script, or (b) running the workflow once and adjusting after observing behavior. Fallback: replace `oca_run_tests` step with explicit `odoo --test-enable --test-tags=l10n_py,-l10n_py_external,-standard -i l10n_py_base,l10n_py_account --stop-after-init`.
- **R-05 `.pylintrc` / `.pylintrc-mandatory` not yet inventoried.** The `.pre-commit-config.yaml` references both files but they don't exist in repo. Planner must add a task to copy them from `references/l10n-brazil/.pylintrc(-mandatory)` (if present there) or render from the jinja template under `references/oca-addons-repo-template/src/.pylintrc.jinja` + `.pylintrc-mandatory.jinja` substituting `odoo_version=18.0`.
- **R-01 REQ text inaccuracy.** CI-01 literal text references `oca-fix-manifest-version` which is non-existent in OCA tooling. The REQ remains locked (researcher does not edit REQUIREMENTS.md), but the plan's verification check must reference what actually runs: `oca-fix-manifest-website` + `pylint-odoo manifest-version-format`. Surface to user in plan-checker review if needed.
- **R-06 `commitlint.yml` PR title validation.** `wagoid/commitlint-github-action@v6` validates PR commits by default. PR title validation is a separate use case requiring the `event_name` check — covered by the second action invocation in the literal YAML, but its exact behavior at v6 should be smoke-tested in CI-08 PR de prueba (try a PR with title `fixed bug` and confirm it's rejected).
- **D-08 (CONTEXT) is non-applicable** as researched — no auto-bump hook exists. Planner can mark D-08 as resolved-as-not-needed in the plan instead of allocating implementation effort.

---

*RESEARCH.md created 2026-05-27. Confidence: HIGH for hook pins (sourced from OCA template + Brazil); HIGH for action versions (verified WebFetch); MEDIUM for `ODOO_TEST_TAGS` env var convention (needs smoke-test confirmation); HIGH for `oca-fix-manifest-version` non-existence (verified across 3 canonical OCA repos at the pinned commits).*
