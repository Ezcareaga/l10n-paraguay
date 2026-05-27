# Phase 1: Bloque A — Foundation técnica (CI/CD + pre-commit) - Context

**Gathered:** 2026-05-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Activar el aparato de calidad automatizado del repo: cualquier push o PR
dispara automáticamente lint + tests, y `main` queda protegido contra merges
sin checks verdes. Cubre 8 REQs (CI-01..08) que en conjunto dejan listos:
`.pre-commit-config.yaml`, `.github/workflows/{lint,test,commitlint}.yml`,
`.github/dependabot.yml`, commitlint config y branch protection en `main`.

Esta phase NO escribe LICENSE/SECURITY (Phase 2), NO escribe docs operacionales
(Phase 3), NO escribe templates `.github/ISSUE_TEMPLATE` (Phase 4) ni audita
multi-rubro (Phase 5). Cualquier idea sobre esos bloques va a Deferred.

Sequencing interno (locked en ROADMAP.md Phase 1 details, NO paralelizable):

1. CI-01 `.pre-commit-config.yaml`
2. CI-02 commit baseline (absorber cambios cosméticos del primer run)
3. CI-04 lint workflow
4. CI-03 + CI-05 + CI-06 en paralelo (test workflow, dependabot, commitlint)
5. CI-07 branch protection en `main` (necesita los status checks ya creados)
6. CI-08 PR de prueba `chore: ci sanity check`

</domain>

<decisions>
## Implementation Decisions

### Stack base hooks

- **D-01: Hand-roll desde l10n-brazil 18.0 como base.** Partir del
  `.pre-commit-config.yaml` que usa OCA Brazil (único OCA latam vivo en 18.0)
  y podarlo al set CI-01: black, isort, flake8, pylint-odoo,
  oca-checks-odoo-module, oca-fix-manifest-version, codespell, yamllint. NO
  correr `copier copy gh:OCA/oca-addons-repo-template .` (prohibido en
  `docs/55_PRE_FASE_2_FOUNDATION.md` — defer a Fase 6 OCA).
  _Razón:_ mantiene migración futura al copier sin pisarse ahora; deja config
  editable; alineado con la `pyproject.toml` que ya tiene `[tool.black]` y
  `[tool.isort]` configurados con secciones OCA.

- **D-02: Pin a versiones Brazil 18.0.** Refs exactas:
  `oca/maintainer-tools @ b89f767503be6ab2b11e4f50a7557cb20066e667`,
  `OCA/odoo-pre-commit-hooks v0.0.33`. Black/isort/codespell/yamllint también
  a la versión que Brazil tiene. _Razón:_ probadas en producción contra Odoo
  18.0; menor riesgo de incompatibilidad que latest stable.

- **D-03: Agregar SOLO `prettier + @prettier/plugin-xml` como extra.** Brazil
  trae también eslint, whool, oca-gen-addon-readme — los tres se descartan:
  no hay JS de OWL todavía, no se necesita build wheel, readme generator
  vendrá en Phase 3 DOC cuando exista `readme/` tree por addon.

- **D-04: Exclusiones explícitas.** Excluir del scope de los hooks:
  `references/**` (prohibido tocar por CLAUDE.md, ~190MB de terceros),
  `addons/**/data/*.csv` (catálogos DNIT generados por `scripts/`),
  `.planning/PROJECT.md` (formato custom GSD). `scripts/`, `bin/`, `docs/`,
  `pyproject.toml` y `addons/l10n_py_*/**/*.py|xml|yml` sí entran al scope.

### Baseline CI-02

- **D-05: Dos commits separados por capa.**

  - Commit A — cosmético: `black + isort + prettier+plugin-xml`.
  - Commit B — semántico: `codespell + oca-fix-manifest-version + yamllint
    - oca-checks-odoo-module`.

  Razon: `git blame` post-baseline queda legible (Quien cambio esto: layout
  o logica?). Costo 2x setup, vale la trazabilidad en un repo con 2 addons
  vivos.

- **D-06: Push directo a `main`.** Aprovechar que CI-07 (branch protection)
  todavía no existe en ese punto del sequencing. _Override de la regla
  global CLAUDE.md "nunca commit directo a main":_ aceptable porque la regla
  todavía no está enforced en CI, y la alternativa (PR formal contra `main`
  sin branch protection) es ceremonial. Para los siguientes commits ya entra
  el patrón PR.

- **D-07: Gate hard de tests al baseline.** Antes del commit A y después del
  commit B, correr el suite completo: `docker exec ... -d odoo_test
--test-tags l10n_py -i l10n_py_base,l10n_py_account` y verificar **97 tests
  verdes** (l10n_py_base 23 + l10n_py_account 74). Si rompe en cualquier
  punto: `git reset --hard` y debuggear antes de reintentar. Cero tolerancia
  a regresión por cambios cosméticos.

- **D-08: Edge `oca-fix-manifest-version` diferido a researcher.**
  El hook puede auto-bumpear `version=` en los `__manifest__.py` de los
  addons. Researcher en plan-phase 1 debe: leer el código del hook
  (`references/.../odoo-pre-commit-hooks/v0.0.33`), determinar qué git ref
  usa como base, y proponer si aceptamos el bump (con entry en `CHANGES.rst`)
  o lo bloqueamos / revertimos. No decidir aquí sin evidencia.

### Odoo en test.yml

- **D-09: OCA action oficial para install.** Usar la action que l10n-brazil
  18.0 usa para levantar Odoo 18 community + Postgres 16 (probablemente
  `oca/oca-ci` o equivalente — researcher confirma el nombre exacto y versión
  pinneable). NO pip-install nightly manual, NO docker-compose CI. _Razón:_
  alineado con OCA, menos YAML mantenido a mano, action ya resuelve
  `l10n_latam_base` + `l10n_latam_invoice_document` como deps.

- **D-10: Tags por external dependency.**

  - `@tagged('l10n_py', 'post_install', '-at_install')` — todos los tests
    locales que no llaman a red. Los 97 tests existentes ya usan tags
    similares — verificar al ejecutar plan.
  - `@tagged('l10n_py_external')` — tests futuros que llaman a SIFEN test o
    DNIT real (Fase 2 EDI).
  - CI por default: `--test-tags=l10n_py,-l10n_py_external,-standard`. Job
    separado con secrets para correr externals manualmente (Fase 2).

- **D-11: 1 job en matrix.** Python 3.11 × PostgreSQL 16 × Odoo 18 community.
  Matrix multi-Python (3.12/3.13) diferida a Pre-Fase 3 con primer cliente
  real. `pyproject.toml` declara support 3.11-3.13 pero CI mide solo el
  baseline activo. CI-03 lo respalda explícitamente.

- **D-12: Triggers conservadores.** `on: pull_request: branches: [main]` +
  `on: push: branches: [main]`. NO `workflow_dispatch`, NO `schedule`.
  _Razón:_ consumo mínimo CI; corre cuando importa (PR + merge). Si más
  adelante queremos scheduled o manual, se agrega — pero no antes de tener
  señal de que falta.

### Coverage gate

- **D-13: Codecov + badge en README, sin gate hard.** test.yml corre con
  coverage, publica a Codecov, postea comment automático en cada PR mostrando
  delta de cobertura. README incluye badge. NO se falla la PR si coverage
  baja — pura señal informativa. _Razón:_ enforcement social > enforcement
  duro; un gate hard bloquea refactors legítimos donde coverage cae temporal.
  El constraint ≥80% del repo queda como convención reforzada por el badge
  visible.

- **D-14: Codecov sobre Coveralls.** Standard OCA actual; l10n-brazil lo usa.
  UI clara con coverage diff por PR.

- **D-15: Codecov free tier ahora (repo privado).** Suficiente para 1
  colaborador (Ez). Setup ya queda listo para cuando Fase 6 haga el repo
  público en OCA — nada que cambiar. Si crece el team antes de OCA,
  reevaluar pricing.

- **D-16: Scope coverage = `addons/l10n_py_*` solamente.** `.coveragerc`
  apunta a `addons/l10n_py_base/`, `addons/l10n_py_account/` (futuros:
  `l10n_py_edi`, `l10n_py_reports`, `l10n_py_pos`, `l10n_py_withholding`).
  Excluir `addons/**/tests/`, `addons/**/data/`, `__manifest__.py`,
  `__init__.py`. Excluir `scripts/` y `bin/` enteramente (utilities sin tests,
  inflarían denominator). Researcher elabora el `.coveragerc` final.

### Claude's Discretion

Áreas donde el researcher / planner tiene libertad para terminar de
especificar sin reabrir discuss:

- Versión exacta del hook `oca-fix-manifest-version` y comportamiento sobre
  los `version=` de manifests (decidir en plan-phase 1 con evidencia).
- Versión exacta de la OCA action de install Odoo (D-09).
- `.coveragerc` final con paths excluidos y patrones de uncoverable code.
- Layout exacto de los 3 workflows `.github/workflows/{pre-commit,test,commitlint}.yml`
  siguiendo OCA Brazil 18.0 como template.
- Commitlint tool pick: `commitlint-cli + wagoid/commitlint-github-action` o
  alternativa. Sin preferencia del usuario, planner elige la estándar (probable
  wagoid action por ser CI-first sin requerir node deps locales).
- Dependabot grouping policy: grupos por ecosistema (`python` group, `actions`
  group) con schedule weekly. Auto-merge minor/patch deferido a Pre-Fase 3.
- CI-08 PR de prueba scope: el cambio trivial que dispara el sanity check
  (probablemente edit a un comment en `__manifest__.py` o agregar línea en
  `CHANGELOG.md` si ya existe).

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source spec del milestone

- `docs/55_PRE_FASE_2_FOUNDATION.md` §"Bloque A — Foundation técnica (CI/CD +
  pre-commit)" — output esperado del bloque, DoD, riesgos identificados
  (incluido el riesgo del baseline cosmético que motiva CI-02), restricción
  explícita "OCA copier real se defiere a Fase 6"
- `.planning/REQUIREMENTS.md` §"CI — Bloque A" — los 8 REQs CI-01..08 con
  texto literal (locked)
- `.planning/ROADMAP.md` §"Phase 1" — goal, dependencies, sequencing interno
  no-paralelizable, success criteria, estimación complexity=large 3-4 días
- `.planning/PROJECT.md` §"Active" + §"Constraints" — milestone activo y
  constraints de coverage ≥80% / OCA-strict / pre-commit OCA activo

### OCA references (qué imitar)

- `references/oca-addons-repo-template/src/.pre-commit-config.yaml.jinja` —
  template canónico OCA. NO ejecutar el copier; usar como referencia para
  qué hooks usa el ecosistema
- `references/oca-addons-repo-template/src/.github/workflows/pre-commit.yml.jinja`
  — lint workflow OCA-style
- `references/oca-addons-repo-template/src/.github/workflows/test.yml.jinja`
  — test workflow OCA-style con matrix Odoo+Python
- `references/oca-addons-repo-template/.github/dependabot.yml` — dependabot
  config OCA
- `references/l10n-brazil/.pre-commit-config.yaml` — único OCA latam 18.0
  vivo; base directa del hand-roll D-01
- `references/l10n-brazil/.github/workflows/pre-commit.yml` — lint workflow
  real corriendo en repo OCA 18.0
- `references/l10n-brazil/.github/workflows/test.yml` — test workflow real
  corriendo en repo OCA 18.0 (debería revelar la OCA action de install
  para D-09)
- `references/l10n-brazil/.copier-answers.yml` — confirma qué versión del
  template OCA usa Brazil; ayuda a alinear pins en D-02

### Estado actual del repo

- `pyproject.toml` — ya define `[tool.black]` (line-length 88, py311),
  `[tool.isort]` (profile=black, sections OCA), `[project.optional-dependencies.dev]`
  (pre-commit, pylint-odoo, black, isort, flake8, pytest, pytest-odoo).
  Reusar estos settings en `.pre-commit-config.yaml`
- `addons/l10n_py_base/__manifest__.py` — `version="18.0.1.1.0"`, target del
  D-08 edge sobre oca-fix-manifest-version
- `addons/l10n_py_account/__manifest__.py` — `version="18.0.1.0.0"`, target
  del D-08 edge sobre oca-fix-manifest-version
- `docker-compose.yml` (raíz) — entorno dev operacional con Odoo 18 +
  Postgres 16; referencia para test-tags y entrypoint usados por los 97
  tests existentes

### OCA guidelines

- `docs/20_OCA_GUIDELINES.md` — manifest conventions, license, naming
- `docs/21_OCA_DEVELOPMENT_BOOK.md` — pre-commit philosophy OCA

### Knowledge base interna

- `docs/60_FASE_1_RETROSPECTIVA.md` — lecciones del baseline anterior;
  posibles regresiones a vigilar en el gate D-07

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- **`pyproject.toml` `[tool.black]` + `[tool.isort]`** — configuración ya
  presente, no rehacer. `.pre-commit-config.yaml` referenciará los argumentos
  alineados con estas secciones; researcher verifica match.
- **`pyproject.toml` `[project.optional-dependencies.dev]`** — declara
  `pre-commit>=3.6, pylint-odoo>=9.1, black>=24.0, isort>=5.13, flake8>=7.0,
pytest>=8.0, pytest-odoo>=1.1` — sirven como floor para los pins de D-02.
- **97 tests existentes** (l10n*py_base 23 + l10n_py_account 74) usan
  `@tagged(...)`. Researcher debe leer un test representativo (ej.
  `addons/l10n_py_base/tests/test*\*.py`) para confirmar el patrón exacto de
  tags ya en uso, antes de imponer D-10.
- **`docker-compose.yml` + bind mount `addons/`** — entorno dev funciona;
  la OCA action de CI debe replicar el mismo `--addons-path addons/`.

### Established Patterns

- **No leer `references/` manualmente** (CLAUDE.md). Para inspeccionar OCA
  Brazil patterns, usar `bin/codegraph.ps1 search/symbol/file` o leer
  archivos específicos de `references/oca-addons-repo-template/` y
  `references/l10n-brazil/` ya citados arriba como canonical refs.
- **Atomic commits + Conventional Commits** (CLAUDE.md). Los 2 commits del
  baseline (D-05) deben respetar `chore(pre-commit): apply cosmetic baseline`
  - `chore(pre-commit): apply semantic baseline`.
- **Subagent override** (project CLAUDE.md): cualquier task de código va por
  subagent. Para Phase 1 plan-phase, los subagents relevantes:
  `voltagent-dev-exp:git-workflow-manager` (workflow YAML + pre-commit),
  `python-pro` (`.coveragerc` + pylint-odoo config), `code-reviewer` antes de
  push.

### Integration Points

- **`.github/workflows/*.yml`** — directorio nuevo. Researcher diseña 3
  archivos: `pre-commit.yml` (CI-04 lint), `test.yml` (CI-03 tests con
  Codecov), `commitlint.yml` (CI-06 Conventional Commits).
- **`.github/dependabot.yml`** — directorio nuevo. Config grupada por
  ecosistema, weekly.
- **`.pre-commit-config.yaml`** (raíz, nuevo).
- **`commitlint.config.js`** (raíz, nuevo) — REQ-CI-06 lo nombra explícitamente.
- **`.coveragerc`** (raíz, nuevo) — D-16 scope.
- **README.md** — agregar badges (CI status, license, Codecov). NO escribir
  el README real ahora (eso es Phase 3 DOC-01); solo sumar 3 badges si el
  README actual es placeholder.
- **GitHub Settings → Branch protection** — CI-07; configurado vía UI o
  `gh api` desde la consola del owner. Los status check names que se
  requieren tienen que coincidir con los `job: <name>` exactos de los
  workflows — researcher lista los nombres canónicos para que el setup
  manual sea reproducible.

</code_context>

<specifics>
## Specific Ideas

- **Patrón espejo del OCA Brazil 18.0 (con poda).** El usuario eligió la
  opción "hand-roll desde Brazil" sobre las dos alternativas (copier render
  y uv+ruff). Significa que cuando haya dudas durante implementación, la
  resolución default es "mirá cómo lo hace Brazil y replicalo".
- **Codecov badge visible en README.md raíz** (D-13/D-14/D-15). El badge
  funciona como enforcement social del ≥80%. No es decorativo.
- **2 commits chore claramente nombrados en el baseline** (D-05). Aunque
  van directo a main, deben respetar Conventional Commits para que el
  blame y release notes futuras sean consistentes.

</specifics>

<deferred>
## Deferred Ideas

### Fuera de scope Phase 1 — capturar para milestones futuros

- **Matrix multi-Python (3.12/3.13)** — diferido a Pre-Fase 3 cuando haya
  primer cliente real con stack distinto. `pyproject.toml` declara support
  pero CI no lo enforce hasta que tenga señal.
- **Scheduled nightly test run** para detectar upstream breakage (Odoo
  nightly, OCA hooks). Valor incierto; reevaluar después del primer mes
  de CI activo.
- **Auto-merge minor/patch en dependabot** — defer a Pre-Fase 3.
  Por ahora cada PR de dependabot revisada manual.
- **Coverage gate hard ≥80% que falle la PR** — solo señal informativa
  ahora (D-13). Si el badge no resulta suficiente, escalar a gate en
  Pre-Fase 3 con primer cliente.
- **OCA copier (`copier copy gh:OCA/oca-addons-repo-template .`)** — Fase 6.
  Doc fuente `docs/55_PRE_FASE_2_FOUNDATION.md` lo defiere explícitamente.
- **Migración a `uv` + `ruff`** — descartada en favor del stack OCA Brazil
  actual. Reconsiderar cuando OCA en su conjunto migre (Brazil ya tiene
  `.ruff.toml` parcial; señal que viene).
- **Eslint + whool + oca-gen-addon-readme hooks** — descartados ahora.
  Reactivar cuando: (a) haya JS de OWL (Fase 4 POS o Fase 2 EDI con
  componentes), (b) se quiera publicar wheels, (c) Phase 3 DOC cree
  los `readme/` trees por addon.

### Reviewed Todos (not folded)

No applicable — `gsd-sdk query todo.match-phase 1` devolvió `todo_count: 0`.

</deferred>

---

<addendum>
## Addendum — 2026-05-27 (post-RESEARCH.md)

`gsd-phase-researcher` produjo `01-RESEARCH.md` y dissolvió 2 decisiones lockeadas. User confirmó las resoluciones via AskUserQuestion:

### A-01: D-11 stack OVERRIDDEN → OCA standard (py3.10 + PG12)

- **Origen:** D-11 fijó "1 job en matrix: Python 3.11 × PostgreSQL 16 × Odoo 18 community" basado en suposición de stack manual.
- **Resolución:** Adoptar OCA-CI standard image `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest` + service `postgres:12` (matches Brazil 18.0 + canónico `oca-addons-repo-template`). Habilita `oca_install_addons` / `oca_run_tests` / `manifestoo` out-of-the-box.
- **Impacto en REQs:** CI-03 literal text dice "Python 3.11 + PostgreSQL 16" — REQ NO se amenda (no es typo, fue decisión deliberada superseded por la confirmación de usuario). Divergencia documentada: implementación usa 3.10/PG12 alineado con OCA standard, runtime de producción puede seguir siendo 3.11+/PG15+.
- **Evidence:** RESEARCH.md R-02; user decision via AskUserQuestion 2026-05-27 ("OCA standard 3.10 + PG12").

### A-02: D-08 RESOLVED AS MOOT (no auto-bump hook exists)

- **Origen:** D-08 difirió al researcher leer `oca-fix-manifest-version` para decidir accept/block del auto-bump de `version=`.
- **Resolución:** Hook `oca-fix-manifest-version` NO existe en `OCA/odoo-pre-commit-hooks@v0.0.33` ni en `OCA/maintainer-tools@b89f767`. Es typo en REQ-CI-01 (ahora amendado: `oca-fix-manifest-website` + `manifest-version-format` C8106 via pylint-odoo, ambos read-only / website-only — NO bumpean `version=`). Manifests actuales (`18.0.1.1.0` y `18.0.1.0.0`) ya pasan el check.
- **Evidence:** RESEARCH.md R-01; user decision via AskUserQuestion 2026-05-27 ("Amendar REQ-CI-01").

### A-03: REQ-CI-01 amendado (typo fix)

- **Edit:** `oca-fix-manifest-version` → `oca-fix-manifest-website` + `pylint-odoo C8106 manifest-version-format` + `prettier+plugin-xml` (formalización D-03).
- **Commit:** integrado con esta addendum en `docs(planning): align Phase 1 with RESEARCH.md`.

### A-04: Discretion items resueltos por researcher

- `.coveragerc` final → en `01-RESEARCH.md` Deliverables.
- 3 workflow YAMLs literales → en RESEARCH.md Deliverables.
- `commitlint.config.js` literal → RESEARCH.md.
- `dependabot.yml` literal → RESEARCH.md.
- Required status check names para CI-07 → `pre-commit`, `test (test with Odoo)`, `commitlint`.
- CI-08 PR de prueba scope → agregar 1 línea a `CHANGES.rst` raíz (nuevo).
- Codecov action pin → `codecov/codecov-action@v5` (Brazil usa v4, v5 es current major).

### Pendings que se trasladan a PLAN.md

- **R-03 medium uncertainty:** env var exacto que `oca_run_tests` lee para test-tags (RESEARCH propone `ODOO_TEST_TAGS`). Planner debe agregar smoke-verification step.
- **R-05 dependency:** `.pylintrc` y `.pylintrc-mandatory` no existen en repo; planner agrega task de copiar desde l10n-brazil (o renderizar de jinja).
- **R-06 wagoid behavior:** validación de PR title con `commitlint-github-action@v6` requiere smoke-test en CI-08 (PR con title `fixed bug` debe ser rechazado).
  </addendum>

---

_Phase: 1-bloque-a-foundation-t-cnica-ci-cd-pre-commit_
_Context gathered: 2026-05-27_
_Addendum: 2026-05-27 (post-RESEARCH.md, user-confirmed resolutions)_
