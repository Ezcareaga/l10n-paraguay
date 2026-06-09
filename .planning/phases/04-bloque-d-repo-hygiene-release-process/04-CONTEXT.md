# Phase 4: Bloque D — Repo hygiene + Release process - Context

**Gathered:** 2026-06-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Llevar el repo a "contributor-ready" + crear el primer punto de rollback
verificable. Cubre 6 REQs (REL-01..06):

- `.github/ISSUE_TEMPLATE/` (issue forms) + `config.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`
- `.github/release.yml` (categorías auto para release notes)
- Release `v0.1.0` taggeado y publicado en GitHub
- Decisión release semantic-release vs manual + proceso escrito en
  `CONTRIBUTING.md` (reemplaza el placeholder dejado en Phase 3)

Esta phase **NO** crea contenido nuevo de docs operacionales (Phase 3, ya
mergeado), **NO** escribe el ADR-0004 multi-rubro ni la auditoría grep
(Phase 5), **NO** automatiza el release con semantic-release (diferido —
ver Deferred), **NO** provisiona deploy real (Pre-Fase 3). Toda idea sobre
esos bloques va a Deferred.

Complejidad: **small** (6 REQs, mayoría boilerplate `.github/*`). El único
peso real está en REL-05 (release v0.1.0, outward-facing) y REL-06 (escribir
el proceso manual en CONTRIBUTING).

</domain>

<decisions>
## Implementation Decisions

### Release automation (REL-06)

- **D-01: Release manual, pasos documentados. SIN semantic-release.** No se
  crea `.releaserc.json` ni workflow de release automatizado en esta phase.
  El proceso manual se escribe en la sección **"## Release process"** de
  `CONTRIBUTING.md` que Phase 3 dejó como placeholder (líneas ~216-220 — el
  bloque `> Deferred to Phase 4 (REL-06)`). Pasos a documentar (orden):
  1. Compilar/actualizar el entry `[x.y.z]` de `CHANGELOG.md` desde los
     Conventional Commits acumulados (categorías Keep a Changelog) y poner la
     fecha (cierra el `- Unreleased` de D-08 Phase 3).
  2. Mergear a `main` vía PR con los 6 status checks verdes.
  3. `git tag vX.Y.Z` sobre el commit de `main`, push del tag.
  4. Crear el GitHub Release con notas derivadas del CHANGELOG.
  - _Razón:_ "cero ceremonia 1-maintainer" (heredado Phase 2/3) + el risk
    note de REQUIREMENTS ("semantic-release opinionated rompe si commits no
    perfectos → empezar manual, automatizar después"). Coincide con el
    default ya escrito en disco ("releases are tagged manually on main after
    CI passes"). **Trigger de revisión:** después de unos cuantos releases o
    cuando crezca el volumen de contribuidores → reconsiderar
    semantic-release (ver Deferred).

### Issue intake (REL-01)

- **D-02: Habilitar GitHub Discussions; las preguntas van a Discussions.**
  - Issue forms en `.github/ISSUE_TEMPLATE/`: **`bug_report.yml` +
    `feature_request.yml` solamente.** Se **omite `question.yml`**.
  - `config.yml`: `blank_issues_enabled: false`; `contact_links` apuntando a
    GitHub Discussions (Q&A) para preguntas + a `SECURITY.md` para reportes
    de seguridad (los reportes de seguridad van por canal privado, NO como
    issue público).
  - **AMENDMENT A-01 a REL-01:** REL-01 lista literalmente `question.yml`.
    Divergencia deliberada — las preguntas se enrutan a Discussions en vez de
    un issue form (triage más limpio; los issues quedan accionables). La
    aceptación de REL-01 se reinterpreta: "issue templates + config.yml con
    links a Discussions" se cumple; `question.yml` se omite a propósito. El
    verifier NO debe fallar por la ausencia de `question.yml`.
  - **Acción del owner (outward-facing):** habilitar Discussions es un
    setting del repo GitHub. El plan lo marca como paso `autonomous: false`
    (o checkpoint) — requiere acción del maintainer vía UI o `gh`.

### Release notes categorization (REL-04)

- **D-03: `release.yml` basado en LABELS de PR, etiquetado manual.** GitHub
  `release.yml` agrupa las auto-generated release notes por **labels de PR**,
  no por prefijos de commit. Categorías keyed on labels (Keep a Changelog +
  Conventional Commit types): Added (`enhancement`/`feat`), Fixed
  (`bug`/`fix`), Changed, Security, Documentation (`docs`),
  Dependencies (dependabot). `exclude` para PRs de bots y label
  `skip-changelog`. **Etiquetado manual por ahora** — sin auto-labeler
  action. El mapeo label→categoría se documenta en CONTRIBUTING junto al
  release process. Puede requerir crear los labels en el repo (discreción:
  vía `gh` o documentado como setup manual).

### Repo ownership + PR hygiene (REL-02, REL-03)

- **D-04: CODEOWNERS global + stubs comentados; PR checklist como
  recordatorios.**
  - `CODEOWNERS`: `* @Ezcareaga` (owner global) + líneas de área futuras
    **comentadas** (`# /addons/l10n_py_*/ @Ezcareaga`, `# /docs/ ...`,
    `# /.github/ ...`) — estructura lista para activar sin reescribir cuando
    se sumen contribuidores.
  - `PULL_REQUEST_TEMPLATE.md`: checklist como **auto-recordatorios** (no
    hard gates — branch protection ya fuerza CI): tests pasan, docs
    actualizados, ADR en el mismo PR si el cambio es arquitectónico
    (regla DOC-09 de Phase 3), Conventional Commits, pre-commit limpio.
    Baja fricción para maintainer solo.

### Release v0.1.0 (REL-05)

- **D-05: v0.1.0 = estado del milestone foundation; release full, notas
  manuales.**
  - **Qué captura:** los 2 módulos shipped (`l10n_py_base 18.0.1.1.0` +
    `l10n_py_account 18.0.1.0.0`, 97 tests) **MÁS** la foundation Pre-Fase 2
    (CI/CD, security baseline, docs operacionales). Resuelve la tensión
    ROADMAP ("post-Fase 1") vs CHANGELOG `[0.1.0]` (D-08, que incluye la
    foundation) **a favor del snapshot rico y preciso**. Fuente de las notas:
    el entry `CHANGELOG.md [0.1.0]`.
  - **Commit del tag:** al **final de Phase 4**, sobre `main`, después de que
    REL-01..04 + los docs de Phase 3 estén mergeados. El tag es lo último de
    la phase (depende de todo lo demás mergeado).
  - **Tipo de release:** **full release (latest)**, manual notes. NO
    pre-release, NO draft. Es un punto de rollback real post-Fase 1.
  - Date-stamp del entry `CHANGELOG.md [0.1.0]` al taggear (cierra el
    `- Unreleased` de D-08 Phase 3).
  - **Acción del owner (outward-facing):** crear tag + GitHub Release toca
    GitHub. El plan lo marca `autonomous: false` / checkpoint.

### Claude's Discretion

Áreas donde researcher/planner tienen libertad sin reabrir discuss:

- Schema/campos exactos de los issue forms (labels auto, required fields,
  dropdowns, validaciones) más allá de bug + feature.
- Wording/secciones exactas del PR template más allá de los ítems listados.
- Nombres exactos de labels + el mapa completo de categorías de `release.yml`
  (alinear a Conventional Commit types + Keep a Changelog).
- Wording/estructura exacta de la sección "Release process" de
  `CONTRIBUTING.md` (reemplaza el placeholder existente).
- Si los GitHub labels se pre-crean vía `gh` o se documentan como setup
  manual.
- URLs exactas de los `contact_links` de `config.yml`.
- Orden de plans/waves de la phase (planner decide; sugerencia natural:
  templates + CODEOWNERS + release.yml + PR template en paralelo → sección
  release en CONTRIBUTING + date-stamp CHANGELOG → tag v0.1.0 al final como
  paso dependiente de todo mergeado).

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source spec + requirements del milestone

- `.planning/REQUIREMENTS.md` §"REL — Bloque D" — REL-01..06 literales
  (locked) + el risk note "semantic-release opinionated rompe → empezar
  manual, automatizar después" (base de D-01)
- `.planning/ROADMAP.md` §"Phase 4" — goal, success criteria, depends on
  Phase 3 (REL-06 documenta release process DENTRO de CONTRIBUTING creado en
  Phase 3 DOC-03), complexity=small
- `docs/55_PRE_FASE_2_FOUNDATION.md` §"Bloque D — Repo hygiene + Release" —
  output esperado, DoD, riesgo de over-engineering
- `.planning/PROJECT.md` §"Constraints" — idioma (meta files en inglés),
  OCA strict (target final OCA/l10n-paraguay)

### Decisiones heredadas de phases previas (carry-forward)

- `.planning/phases/03-bloque-c-documentaci-n-operacional/03-CONTEXT.md` —
  D-01 (idioma: meta files y `.github/` en **inglés**), D-08 (CHANGELOG
  `[0.1.0]` entry que incluye la foundation), D-09 (CHANGELOG se compila al
  release, no per-PR), Deferred ("Release process en CONTRIBUTING
  semantic-release vs manual — Phase 4 REL-06")
- `.planning/phases/02-bloque-b-security-baseline/02-CONTEXT.md` — D-05/D-06
  (canales SECURITY.md = el `contact_link` de seguridad de `config.yml`);
  "cero ceremonia 1-maintainer"

### Archivos a editar/crear (estado real en disco)

- `CONTRIBUTING.md` §"## Release process" (líneas ~216-220) — **placeholder
  a REEMPLAZAR** con los pasos manuales (REL-06, D-01)
- `CHANGELOG.md` §`[0.1.0] - Unreleased` — entry a **date-stampear** + fuente
  de las release notes de v0.1.0 (REL-05, D-05)
- `SECURITY.md` — canal privado que `config.yml` linkea como `contact_link`
  de seguridad (D-02)
- `.github/` existente: `dependabot.yml` + `workflows/{commitlint,pre-commit,
security,test}.yml` — Phase 4 SUMA `ISSUE_TEMPLATE/`,
  `PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`, `release.yml` (no toca lo
  existente; `release.yml` debe `exclude` PRs de dependabot o mandarlas a
  categoría Dependencies)

### Referencias externas (formato — researcher verifica schema actual)

- GitHub issue forms syntax —
  `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms`
- GitHub config.yml (contact_links / blank_issues_enabled) —
  `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository`
- GitHub automatically generated release notes (`release.yml`) —
  `https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes`
- CODEOWNERS syntax —
  `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners`
- Keep a Changelog 1.1 — `https://keepachangelog.com/en/1.1.0/` (D-05)

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- **`.github/dependabot.yml` + 4 workflows** (commitlint, pre-commit,
  security, test) — `release.yml` debe excluir o categorizar las PRs de
  dependabot; CODEOWNERS cubre `.github/`.
- **`CHANGELOG.md` + `CONTRIBUTING.md`** (creados Phase 3) — Phase 4 los
  **edita**, no los crea. CONTRIBUTING tiene el placeholder de release; el
  CHANGELOG tiene `[0.1.0]` listo para date-stamp.
- **`SECURITY.md`** (Phase 2) — canal de seguridad para `config.yml`.
- **6 badges del README** (CI, pre-commit, security, codecov, license, Odoo)
  — opcionalmente sumar badge de release/version tras v0.1.0 (discreción).

### Established Patterns

- **Conventional Commits** forzados vía commitlint — el mapa label→categoría
  de `release.yml` y los pasos del release process se alinean a los types
  (feat/fix/docs/chore/refactor/test).
- **Branch protection (6 status checks) en `main`** — v0.1.0 se taggea solo
  tras merge de PR con checks verdes; el PR checklist NO duplica los gates de
  CI (ya forzados).
- **Idioma inglés en meta files** (D-01 Phase 3) — todos los `.github/*`
  templates y las release notes en inglés (reviewer OCA primero).
- **Atomic commits + Conventional Commits** — commits `chore(...)`/`docs(...)`;
  trabajo por PR contra `main`.
- **Acciones outward-facing con confirmación** (patrón Phase 3 DOC-10 issue
  #21): habilitar Discussions, crear labels, taggear/publicar release →
  `autonomous: false` o checkpoint con el maintainer.

### Integration Points

- **`.github/ISSUE_TEMPLATE/{bug_report,feature_request}.yml` + `config.yml`**
  (nuevos) — D-02.
- **`.github/PULL_REQUEST_TEMPLATE.md`** (nuevo) — D-04.
- **`.github/CODEOWNERS`** (nuevo) — D-04.
- **`.github/release.yml`** (nuevo) — D-03.
- **`CONTRIBUTING.md`** (editar §Release process) — D-01.
- **`CHANGELOG.md`** (date-stamp `[0.1.0]`) — D-05.
- **GitHub repo settings** (Discussions on, labels) + **tag/Release v0.1.0**
  — acciones del owner.

</code_context>

<specifics>
## Specific Ideas

- **El reviewer OCA sigue ordenando prioridades.** Templates en inglés,
  layout `.github/` estándar, CODEOWNERS canónico: que la migración a
  `OCA/l10n-paraguay` (Fase 6) no requiera retrabajo de meta files.
- **v0.1.0 es el primer punto de rollback verificable** y un ítem del DoD del
  milestone — operacionalmente significativo (estado post-Fase 1 +
  foundation completa), no decorativo.
- **Manual-first honra la mitigación de riesgo documentada** — semantic-release
  rompe con history imperfecto; se automatiza cuando el flujo lo justifique.
- **Discussions sobre question-issues** — mantener los issues accionables
  (bugs + features), las preguntas a un canal de conversación; alineado con
  el triage de bajo overhead de un maintainer solo.

</specifics>

<deferred>
## Deferred Ideas

### Fuera de scope Phase 4 — capturar para phases/milestones futuros

- **semantic-release (`.releaserc.json` + workflow de release)** — REL-06
  explícitamente "automatizar después". Revisar tras unos releases manuales o
  cuando crezca el volumen de contribuidores.
- **Auto-labeler action** (actions/labeler o PR-title→label) — se difiere
  junto con la automatización de release; por ahora etiquetado manual (D-03).
- **`question.yml` issue form** — superado por Discussions (D-02 / A-01);
  reabrir solo si Discussions resulta insuficiente.
- **Activación de áreas en CODEOWNERS** (descomentar los stubs) — cuando se
  sumen contribuidores por área.
- **Badge de versión/release en README** — opcional tras v0.1.0 (discreción
  del planner si aporta).
- **Cadencia de releases v0.1.x+ / automatización de mantenimiento del
  CHANGELOG** — post-milestone.
- **Phase 5 (Bloque E — multi-rubro: ADR-0004, docs/80, auditoría grep)** —
  phase separada, paralelizable.
- **Deploy real (VPS) + validación docs/71** — Pre-Fase 3.

### Reviewed Todos (not folded)

None — `gsd-sdk query todo.match-phase 04` devolvió `todo_count: 0`.

</deferred>

---

_Phase: 4-bloque-d-repo-hygiene-release-process_
_Context gathered: 2026-06-09_
