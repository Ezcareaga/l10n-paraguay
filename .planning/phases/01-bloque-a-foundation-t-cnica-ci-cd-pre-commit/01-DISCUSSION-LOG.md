# Phase 1: Bloque A — Foundation técnica (CI/CD + pre-commit) - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-05-27
**Phase:** 1-bloque-a-foundation-t-cnica-ci-cd-pre-commit
**Areas discussed:** Stack base hooks, Baseline CI-02, Odoo en test.yml, Coverage gate

---

## Stack base hooks

### Q1 — Approach al stack de linters

| Option | Description | Selected |
|--------|-------------|----------|
| Hand-roll estilo OCA Brazil | Tomar el .pre-commit-config.yaml de l10n-brazil 18.0 como base, podarlo a lo que pide CI-01, mantener compatibilidad de migración futura al copier sin pisarse ahora. | ✓ |
| Render aislado del .jinja | Correr `copier copy` en branch desechable, copiar manualmente los archivos relevantes al repo. Más fiel a OCA pero requiere reconciliar a mano con archivos existentes. | |
| Stack moderno uv+ruff | Adoptar uv + ruff (reemplaza black/isort/flake8). Divergente de OCA actual pero alineado con la dirección donde van. | |

**User's choice:** Hand-roll estilo OCA Brazil

### Q2 — Pinning de versiones

| Option | Description | Selected |
|--------|-------------|----------|
| Pin a versiones Brazil 18.0 | Refs exactas: oca/maintainer-tools b89f7675, OCA/odoo-pre-commit-hooks v0.0.33, etc. Probadas en producción contra Odoo 18.0. | ✓ |
| Pin a latest stable hoy | Versiones más nuevas estables al 2026-05-26. Bugfixes recientes, posibles incompatibilidades. | |
| Mixto: Brazil para OCA, latest para resto | OCA-specific pinneados a Brazil; python tools standalone a latest. | |
| Vos decidís | Que researcher en plan-phase valide. | |

**User's choice:** Pin a versiones Brazil 18.0

### Q3 — Hooks extras (prettier-xml, eslint, whool, readme-gen)

| Option | Description | Selected |
|--------|-------------|----------|
| Drop todos los extras | Quedarse SOLO con CI-01. Mínima superficie, primer baseline más rápido. | |
| Sumar prettier-xml + readme gen | Agregar prettier+plugin-xml + oca-gen-addon-readme. | |
| Solo prettier-xml | Solo prettier+plugin-xml por el diff sanity en vistas XML; readme-gen overkill ahora. | ✓ |
| Vos decidís | Que el planner balancee. | |

**User's choice:** Solo prettier-xml (drop eslint, whool, oca-gen-addon-readme)

### Q4 — Exclusiones

| Option | Description | Selected |
|--------|-------------|----------|
| Exclude references/ + scripts/ + bin/ | references/ + scripts/ + bin/. Pyproject + addons + .planning + docs sí entran. | |
| Exclude solo references/ | Solo excluir references/. scripts/ + bin/ sí se barren. | |
| Exclude references/ y data CSVs generados | references/ + addons/**/data/*.csv + .planning/PROJECT.md. | ✓ |
| Vos decidís | Que researcher mire pattern OCA. | |

**User's choice:** Exclude references/ + addons/**/data/*.csv generados + .planning/PROJECT.md

---

## Baseline CI-02

### Q1 — Scope del baseline commit

| Option | Description | Selected |
|--------|-------------|----------|
| Sweep completo de un saque | Una sola corrida con TODOS los hooks. Un solo commit. Diff potencialmente grande mezclando capas. | |
| Dos commits separados por capa | A: formato cosmético; B: hooks semánticos. Blame más legible. | ✓ |
| Tres commits: cosmético + manifest + textual | A: black+isort+prettier-xml; B: manifest version; C: codespell+yamllint+oca-checks. Overkill para 2 addons. | |

**User's choice:** Dos commits separados por capa

### Q2 — Delivery channel

| Option | Description | Selected |
|--------|-------------|----------|
| PR formal contra main | Branch chore/pre-commit-baseline + PR + self-review + merge. Establece hábito antes de CI-07. | |
| Push directo a main | Aprovechar que branch protection todavía no existe. Más rápido, rompe regla global "nunca commit a main" pero aceptable en este punto. | ✓ |
| PR pero con merge directo del owner | Branch + PR + merge sin review formal. Compromiso intermedio. | |

**User's choice:** Push directo a main

### Q3 — Edge: oca-fix-manifest-version bump

| Option | Description | Selected |
|--------|-------------|----------|
| Aceptar el bump silencioso | Si el hook bumpea, aceptar y reflejar en CHANGES.rst. | |
| Revertir el bump | Si el hook bumpea, revertir manualmente en commit C. | |
| Investigar y decidir en plan | Researcher verifica qué hace el hook y propone estrategia. | ✓ |
| Vos decidís | Acepto el bump si pasa, documento, sigo. | |

**User's choice:** Investigar y decidir en plan

### Q4 — Tests gate

| Option | Description | Selected |
|--------|-------------|----------|
| Gate: 97 verdes pre + post | Correr suite completo antes y después de cada commit baseline. Cero tolerancia a regresión. | ✓ |
| Smoke check, no full gate | Solo después del commit B final. | |
| Trust the hooks | Los hooks no cambian semántica. No correr tests durante baseline. | |

**User's choice:** Gate hard: 97 tests verdes pre + post-baseline; rollback si rompe

---

## Odoo en test.yml

### Q1 — Install pattern

| Option | Description | Selected |
|--------|-------------|----------|
| OCA action (oca/oca-ci o equiv) | GitHub Action OCA que sabe levantar Odoo + Postgres + tests por addon. l10n-brazil lo usa. | ✓ |
| pip install Odoo nightly + pytest-odoo | pip install desde nightly.odoo.com + service postgres + pytest-odoo. Más explícito, más control. | |
| Docker compose espejo de dev | Reusar docker-compose.yml del repo. Máxima paridad dev/CI, más lento en CI. | |
| Vos decidís + researcher valida | Que el plan-phase researcher compare. | |

**User's choice:** OCA action oficial (oca/oca-ci o equivalente)

### Q2 — Test tags + discovery

| Option | Description | Selected |
|--------|-------------|----------|
| Tags Odoo nativos por addon | @tagged('l10n_py', 'post_install', '-at_install'). CI corre --test-tags=l10n_py,-standard. | |
| Tags por external dependency | Tag separado l10n_py_external para tests que tocan red. CI base corre -external. Future-proof Fase 2 EDI. | ✓ |
| Marker pytest + tags Odoo combinados | @pytest.mark.external + @tagged('l10n_py'). Discovery dual. | |
| Vos decidís | Que researcher mire los 97 tests actuales. | |

**User's choice:** Tags por external dependency

### Q3 — Matrix

| Option | Description | Selected |
|--------|-------------|----------|
| 1 job: Py3.11 x PG16 x Odoo18 | Una sola combinación, más simple, más rápido. | |
| Matrix Py 3.11 + 3.12 contra PG 16 | 2 jobs paralelos. Detecta breakage Python adelante. | |
| Solo 3.11/PG16 ahora, ampliar después | Empezar con 1 job, sumar 3.12 en Pre-Fase 3 con primer cliente real. YAGNI. | ✓ |

**User's choice:** Solo 3.11/PG16 ahora, ampliar después

### Q4 — Triggers

| Option | Description | Selected |
|--------|-------------|----------|
| PR contra main + push a main | Standard. Corre en cada PR y al merge. | ✓ |
| PR + push main + manual dispatch | + workflow_dispatch para correr a mano. | |
| PR + push + scheduled nightly | + scheduled cron para detectar upstream breakage. | |
| Vos decidís | Que researcher proponga lo que OCA usa. | |

**User's choice:** PR contra main + push a main

---

## Coverage gate

### Q1 — Enforcement en CI

| Option | Description | Selected |
|--------|-------------|----------|
| Solo medir local, no publicar | Honor system, costo cero CI. | |
| Calcular en CI, publicar artifact | Coverage HTML como GitHub artifact. No gate. Informativo. | |
| Codecov/Coveralls + badge en README | Tercero, badge, comment automático en PR. No gate hard. Standard OCA. | ✓ |
| Gate duro: PR falla si coverage <80% | Status check bloquea PR si cae <80% o delta >2%. Máxima disciplina, bloquea refactors legítimos. | |

**User's choice:** Codecov/Coveralls + badge en README

### Q2 — Codecov vs Coveralls

| Option | Description | Selected |
|--------|-------------|----------|
| Codecov | Standard OCA, l10n-brazil lo usa, free para repos públicos. | ✓ |
| Coveralls | Alternativa clásica, menos adoptada en OCA recientemente. | |
| Vos decidís + researcher valida | Que el researcher verifique. | |

**User's choice:** Codecov

### Q3 — Repo privado + Codecov free tier

| Option | Description | Selected |
|--------|-------------|----------|
| Codecov ahora (free tier OK) | Free tier privado permite hasta 5 colaboradores. Setup listo para cuando se haga público en Fase 6. | ✓ |
| Coverage artifact ahora, Codecov cuando público | Phase 1 solo artifact HTML; Phase 6 agrega Codecov. | |
| Hacer repo público ahora | Scope creep — va contra docs/55. | |
| Vos decidís en plan | Diferir a researcher. | |

**User's choice:** Codecov ahora (free tier OK)

### Q4 — Coverage scope

| Option | Description | Selected |
|--------|-------------|----------|
| Solo addons/l10n_py_* | .coveragerc apunta a addons. Excluir tests/data/manifest. La métrica que importa. | ✓ |
| addons/ + scripts/ | Sumar scripts/. Inflarían denominator. | |
| Solo modelos + servicios, excluir wizards y reports | Concentra métrica en lo importante. | |
| Vos decidís + researcher define | Que researcher mire OCA pattern. | |

**User's choice:** Solo addons/l10n_py_*

---

## Claude's Discretion

Áreas explícitamente delegadas (locked en CONTEXT.md §"Claude's Discretion"):

- Comportamiento exacto de `oca-fix-manifest-version` sobre `version=` en
  manifests — researcher lee código del hook en plan-phase 1
- Nombre + versión exacta de la OCA action de install Odoo en CI (D-09)
- `.coveragerc` final con paths excluidos
- Layout de los 3 workflows `.github/workflows/*.yml` siguiendo Brazil 18.0
- Commitlint tool pick (commitlint-cli + wagoid action probable default)
- Dependabot grouping policy (grupos por ecosistema, weekly, sin auto-merge)
- CI-08 PR sanity check scope (cambio trivial específico)

## Deferred Ideas

Capturados en CONTEXT.md §"Deferred" — no se pierden:

- Matrix multi-Python (3.12/3.13) → Pre-Fase 3 con primer cliente real
- Scheduled nightly test run → evaluar tras 1 mes de CI activo
- Auto-merge minor/patch en dependabot → Pre-Fase 3
- Coverage gate hard ≥80% → escalar si badge social no alcanza
- OCA copier `copier copy gh:OCA/oca-addons-repo-template .` → Fase 6 OCA
- Migración a uv + ruff → cuando OCA en su conjunto migre
- Eslint + whool + oca-gen-addon-readme → cuando haya JS de OWL / publish
  wheels / `readme/` trees por addon (Phase 3 DOC en adelante)
