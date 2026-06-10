---
gsd_state_version: 1.0
milestone: v0.1.0
milestone_name: milestone
current_phase: 05
status: "MILESTONE COMPLETE — Phase 05 Bloque E done 2026-06-10 (IND-01..04 closed, ejecución directa sin plans GSD). 35/35 v1 REQs. Next: /gsd:complete-milestone → Fase 2 l10n_py_edi."
last_updated: "2026-06-10T00:00:00.000Z"
progress:
  total_phases: 5
  completed_phases: 5
  total_plans: 16
  completed_plans: 14
  percent: 100
---

# STATE — l10n-paraguay

> Project memory. Updated at phase transitions, plan execution checkpoints, and milestone boundaries.

---

## Project Reference

- **Project name:** l10n-paraguay
- **Repo:** [`Ezcareaga/l10n-paraguay`](https://github.com/Ezcareaga/l10n-paraguay) (private, será OCA cuando Fase 6)
- **Owner:** Alberto Ezequiel Careaga (`@Ezcareaga`)
- **Core value:** Hacer cumplimiento SIFEN posible sin SaaS pago ni soluciones cerradas — módulos AGPL-3 reutilizables, conexión directa DNIT.
- **Project doc:** [`.planning/PROJECT.md`](PROJECT.md)
- **Active requirements:** [`.planning/REQUIREMENTS.md`](REQUIREMENTS.md)
- **Active roadmap:** [`.planning/ROADMAP.md`](ROADMAP.md)
- **Source spec del milestone:** [`docs/55_PRE_FASE_2_FOUNDATION.md`](../docs/55_PRE_FASE_2_FOUNDATION.md)

## Current Focus

- **Active milestone:** Pre-Fase 2 — Foundation & Housekeeping — **COMPLETE**
- **Current phase:** 05 (COMPLETE)
- **Active plan:** Phase 05 COMPLETE (IND-01..04 cerrados, ejecución directa sin plans GSD). Milestone Pre-Fase 2 COMPLETE 35/35 REQs.
- **Status:** MILESTONE COMPLETE — Phase 05 Bloque E done 2026-06-10 (IND-01..04 closed, ejecución directa sin plans GSD). 35/35 v1 REQs. Next: `/gsd:complete-milestone` → Fase 2 `l10n_py_edi`.
- **Last action:** Phase 05 Bloque E ejecutada directamente (2026-06-10, documentation-engineer subagent) — ADR-0004 aceptado con auditoría grep (IND-01, IND-03), `docs/80_MULTI_RUBRO_ROADMAP.md` creado (IND-02, IND-04), tracking docs sincronizados a 35/35 REQs.
- **Previous phase:** Phase 4 — Bloque D Repo hygiene + Release — COMPLETE (2026-06-09); Phase 3 — Bloque C Docs operacionales — COMPLETE (2026-06-08); Phase 2 — Security baseline — COMPLETE (PR #19 merged 2026-06-05); Phase 1 — CI/CD + pre-commit — CLOSED 2026-05-28

---

## Current Position

```text
Milestone: Pre-Fase 2 Foundation — COMPLETE
Phase: 05 (bloque-e-multi-rubro-foundation) — COMPLETE
Plan: Phase 05 COMPLETE (ejecución directa sin plans GSD)
Status: MILESTONE COMPLETE — 35/35 REQs
Resume: /gsd:complete-milestone

Progress:
[██████████] 100%
[x] Phase 1: Bloque A — CI/CD + pre-commit          (8/8 REQs)
[x] Phase 2: Bloque B — Security baseline           (7/7 REQs — PR #19 merged)
[x] Phase 3: Bloque C — Docs operacionales          (10/10 REQs implemented; DOC-10 = async UAT via issue #21, non-blocking)
[x] Phase 4: Bloque D — Repo hygiene + Release      (6/6 REQs — REL-01..06 all closed; v0.1.0 tagged + released 2026-06-09)
[x] Phase 5: Bloque E — Multi-rubro foundation      (4/4 REQs — IND-01..04 closed 2026-06-10)

Total: 35/35 v1 REQs implemented (milestone Pre-Fase 2 COMPLETE)
```

---

## Repo State Snapshot (2026-06-02)

| Item                                         | State                                                                                                              |
| -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Branch activa                                | `main` + topic branch `docs/phase-2-context` (en flight PR)                                                        |
| Último commit en `main`                      | `acd9a64 fix: close TD-005 (resolve flake8-bugbear opinionated checks) (#13)`                                      |
| Módulos productivos                          | `addons/l10n_py_base 18.0.1.1.0` + `addons/l10n_py_account 18.0.1.0.0`                                             |
| Tests acumulados                             | 97 verdes (l10n_py_base 23 + l10n_py_account 74)                                                                   |
| PRs mergeados a `main` (Phase 1)             | #3 (pre-commit), #4 (test+codecov), #5 (dependabot), #6 (commitlint), #8 (sanity), #10 (chore), #11-#13 (TD fixes) |
| Docker Compose dev                           | Operacional (bind mount `addons/` resuelto)                                                                        |
| codegraph index                              | Activo, 12k+ símbolos                                                                                              |
| CI/CD                                        | ✅ Activo (lint + test + commitlint workflows en main)                                                             |
| Pre-commit                                   | ✅ Activo (commit baseline 3a10fc7+abd7395 aplicado)                                                               |
| Branch protection en `main`                  | ✅ Activa (CI-07 cerrado)                                                                                          |
| LICENSE file                                 | ✅ `LICENSE` AGPL-3.0 en raíz (SHA256 verified, Plan 02-01)                                                        |
| SECURITY.md / CONTRIBUTING.md / CHANGELOG.md | ✅ `SECURITY.md` creado (Plan 02-01); CONTRIBUTING/CHANGELOG en Phase 3                                            |
| Security workflow `security.yml`             | ✅ Activo en main (3 runs verdes — PRs #18 + push baseline); job names: gitleaks, bandit, dependency-review        |
| Dependency Graph + Dependabot alerts (GH)    | ✅ Enabled (approved 2026-06-02, ya estaban activos)                                                               |
| Branch protection — security checks          | ✅ required_status_checks en `main` = 6 contexts (Phase 1 + Phase 2 security) — confirmado 2026-06-03 vía gh api   |
| gitleaks baseline (full-history)             | ✅ 0 findings en 106 commits (gitleaks v8.30.1, 2026-06-03 local) → SEC-04 cerrado                                 |
| Bandit baseline (`addons/`)                  | ✅ 0 findings any severity en 2228 LOC (bandit 1.9.4 `-lll -iii`, 2026-06-03 local) → SEC-05 cerrado               |
| docs/60 + docs/61                            | ❌ Inexistentes (Phase 2 Wave 4 los crea)                                                                          |
| Issue/PR templates                           | ❌ Inexistentes (Phase 4)                                                                                          |
| Release `v0.1.0`                             | ❌ Sin taggear (Phase 4)                                                                                           |

---

## Performance Metrics

| Métrica                           | Baseline (entry milestone) | Phase 1 exit (2026-05-28)                          | Target (exit milestone) |
| --------------------------------- | -------------------------- | -------------------------------------------------- | ----------------------- |
| Tests verdes                      | 97                         | 97 (no regresión)                                  | ≥97                     |
| Cobertura tests                   | TBD                        | Medida via Codecov (badge en README)               | ≥80% en código nuevo    |
| Lint warnings (pre-commit)        | n/a                        | 0 (baseline 3a10fc7+abd7395 absorbió 100+ cambios) | 0                       |
| Security warnings HIGH (Bandit)   | n/a                        | n/a (Phase 2 lo mide)                              | 0                       |
| Secrets en HEAD (gitleaks)        | n/a                        | n/a (Phase 2 lo mide)                              | 0                       |
| Push directo a `main`             | Permitido                  | Rechazado (CI-07/08 cerrados)                      | Rechazado               |
| ADRs en `docs/adr/`               | 0                          | 0 (Phase 3)                                        | 5 (0001-0005)           |
| Docs operacionales (`docs/70-72`) | 0                          | 0 (Phase 3)                                        | 3                       |

---

### Execution metrics — Phase 04

| Plan         | Duration | Tasks   | Files touched             |
| ------------ | -------- | ------- | ------------------------- |
| Phase 04 P01 | 8min     | 2 tasks | 3 files                   |
| Phase 04 P02 | 6min     | 2 tasks | 4 files                   |
| Phase 04 P03 | 20min    | 3 tasks | 0 files (GitHub API only) |
| Phase 04 P04 | 30min    | 2 tasks | 1 file (CHANGELOG.md)     |

## Accumulated Context

### Decisions to date (este milestone)

- **2026-05-26 — Estructura 1 milestone, 5 phases.** Una phase por Bloque (A→E). Justificación: cada Bloque es coherente, tiene DoD propio, y la dependencia es lineal con una excepción (Phase 5 paralelizable con Phase 3/4). NO subdividir ni unificar. (Decisión usuario.)
- **2026-05-26 — Modo standard (Horizontal Layers).** Cada Bloque es una capa de foundation horizontal, no un slice de end-user feature. Justificación: la audiencia es maintainers/reviewers, no end-users. (Decisión usuario.)
- **2026-05-26 — Mapeo REQ↔Phase fijo por categoría.** CI→1, SEC→2, DOC→3, REL→4, IND→5. Sin re-shuffling entre phases. (Decisión usuario.)
- **2026-05-26 — Phase 1 sequencing interno NO paralelizable.** CI-01 → CI-02 (baseline commit) → CI-04 (lint workflow) son secuenciales obligatorias. CI-03/05/06 paralelos. CI-07 después de tener status checks. CI-08 al final. (De spec `docs/55` "Riesgos" — mitigación del commit baseline.)
- **2026-06-02 — Phase 2 D-01..D-15.** 15 decisiones lockeadas en 02-CONTEXT.md. Highlights: (a) `security.yml` = 1 workflow con 3 jobs paralelos; (b) Bandit fail-gate HIGH only; (c) SARIF al Security tab; (d) GH Security Advisories como canal primario + PGP publicado; (e) CCFE encryption helper diferido a Fase 2 EDI (docs/60 deja blueprint); (f) OCA `auditlog` para audit retention 7y/1y; (g) Backup S3-compatible (Backblaze B2 default) + filesystem; (h) docs/61 split vendor/operador con matriz de cumplimiento Ley 6534. (Decisión usuario via discuss-phase 2.)
- **2026-06-02 — Plan 02-01 executed.** LICENSE AGPL-3.0 descargado de canonical URL (SHA256 verified). SECURITY.md creado con skeleton de RESEARCH.md (GH Advisories primary, email fallback, SLA 72h/30d, sin PGP, sin HoF manual). Manifests ya tenían `license="AGPL-3"` — sin cambios. SEC-01 + SEC-02 cerrados. Wave 1 Phase 2 completa.
- **2026-06-02 — Plan 02-02 executed.** `.github/workflows/security.yml` creado en worktree isolation, fast-forward merge a `feat/sec-03-security-workflow`. 3 jobs: gitleaks @v3 (no @v2 — A-02), bandit HIGH-only (`-lll -iii`, D-02), dependency-review @v4 (NO v5 — runner compat). SARIF con categorías distintas (D-03). Triggers conservadores: PR + push a main only (D-04). Checkpoint 02-02-02 approved — Dependency Graph + Dependabot alerts ya estaban habilitados. SEC-03 cerrado. Wave 2 Phase 2 completa. Required-status-check names para Plan 03: `gitleaks`, `bandit`, `dependency-review`.
- **2026-06-09 — Plan 04-01 executed.** GitHub issue intake layer creado en `.github/ISSUE_TEMPLATE/`: `bug_report.yml` (textareas required What happened?/Expected/Steps + input `odoo_version` + checkboxes Odoo Community 18.0; auto-labels `bug`), `feature_request.yml` (Problem/Solution required + Alternatives optional; auto-labels `enhancement`), `config.yml` (`blank_issues_enabled:false` + 2 contact_links: Q&A → generic `/discussions` URL [Pitfall 4 — Discussions aún no habilitado, Plan 03 lo habilita], security → `/security/policy`). `question.yml` omitido deliberadamente (Amendment A-01 a REL-01 — preguntas van a Discussions; el verifier NO debe fallar por su ausencia). yamllint verde en los 3 archivos (el `.yamllint` existente absorbe las keys del schema de issue-forms; fallback A4 no necesario). Sin deviations. Threat model: T-04-01 + T-04-03 mitigados, T-04-02 accept. Commits `cfba825` (forms) + `bf3b1fd` (config). REL-01 cerrado.
- **2026-06-09 — Plan 04-02 executed.** PR-hygiene + release-categorization meta-files. `.github/CODEOWNERS`: `* @Ezcareaga` on physical line 1 (last-match-wins) + commented future area stubs (`l10n_py_base/account/edi`, `/docs/`, `/.github/`) — inert until contributors join (D-04). `.github/PULL_REQUEST_TEMPLATE.md`: soft-reminder checklist (tests `pytest addons/ -x`, pre-commit, Conventional Commits, docs-if-behavior-changed, ADR/DOC-09 if architectural, CHANGELOG if release-worthy) + `## Type of change` + `## Description` (D-04 — soft reminders, not hard gates; branch protection already forces CI). `.github/release.yml`: 7 categories (Added `feat`/`enhancement`, Fixed `bug`/`fix`, Changed `changed`/`refactor`/`chore`, Security, Documentation `documentation`/`docs`, Dependencies, Other `"*"` catch-all last) + `exclude` (`skip-changelog` label, `dependabot[bot]` author) (D-03). yamllint verde. `CONTRIBUTING.md` §Release process: placeholder `> Deferred to Phase 4` reemplazado por rationale "manual releases" + 4 pasos manuales (compile CHANGELOG → merge a main con 6 checks → `git tag -a` + push → `gh release create --notes-file --latest`) + tabla PR-label→categoría (D-01, REL-06); se conservaron el heading y los `---`. Deviation (Rule 3 — blocking): la regla global de CODEOWNERS se movió a la línea física 1 para satisfacer el verify literal del plan (`head -n 1 | grep -qv '^#'`); semántica last-match-wins intacta. Sin deletions, sin untracked espurios. Threat model: T-04-04 + T-04-05 mitigados, T-04-06 accept (wave order). Commits `76eac19` (CODEOWNERS+PR template) + `b46f4df` (release.yml+CONTRIBUTING). REL-02, REL-03, REL-04, REL-06 cerrados. Labels de release.yml aún no existen → Plan 04-03 los crea.
- **2026-06-03 — Plan 02-03 executed.** Worktree isolation, merge `--no-ff` a `feat/sec-04-sec-05-baseline`. gitleaks v8.30.1 native Windows binary (Docker daemon no estaba; fallback pre-aprobado en RESEARCH.md) corrió full history (106 commits, 3.27 MB, 1.48s) — **0 findings**. Bandit 1.9.4 (`-lll -iii` y full audit en `addons/`, 2228 LOC) — **0 findings any severity/confidence**. No `.gitleaksignore`, no `BUGS_BACKLOG.md` append (política: archivos sólo existen si hay contenido que registrar). Checkpoint 02-03-03 cerrado por el repo owner: `gh api … required_status_checks --jq '.contexts'` ahora retorna `["gitleaks","bandit","dependency-review","pre-commit","test with Odoo","commitlint"]` — los 6 contexts en main. SEC-04, SEC-05, T-SEC-03-protection cerrados. Política D-04 (rotate-not-rewrite) mantenida — `git reflog --all | Select-String 'filter-repo|filter-branch|BFG'` returned False.

### Open todos / next steps

- [x] User aprobó `ROADMAP.md` (implícito al ejecutar Phase 1 y Phase 2 discuss)
- [x] Phase 1 completada (8/8 REQs CI-01..08)
- [x] Mergear PR `docs/phase-2-context` (CONTEXT + DISCUSSION-LOG + STATE update)
- [x] `/gsd:plan-phase 2` para decomponer Phase 2 (Bloque B) en plans ejecutables
- [x] Plan 02-01 ejecutado: LICENSE + SECURITY.md creados (SEC-01, SEC-02 cerrados) — 2026-06-02
- [x] Plan 02-02 ejecutado: `.github/workflows/security.yml` creado (SEC-03 cerrado); Dependency Graph + Dependabot alerts approved — 2026-06-02
- [x] Plan 02-03 ejecutado: gitleaks history scan + Bandit baseline + branch protection update (SEC-04, SEC-05, T-SEC-03-protection cerrados) — 2026-06-03
- [x] Push `feat/sec-04-sec-05-baseline` y abrir PR (Wave 3 PR) — completado vía PR #19 (merged 2026-06-05)
- [x] Ejecutar Wave 4 (Plans 02-04 + 02-05): docs/60 + docs/61 + restore-smoke stub + README badge — completado vía PR #19 (SEC-06/07 cerrados)
- [x] Verificar subagent `voltagent-dev-exp:documentation-engineer` — Phase 3 ejecutada y cerrada (PR #22, 2026-06-08)
- [x] Phase 5 Bloque E completada — IND-01..04 cerrados vía ejecución directa (2026-06-10)

### Blockers actuales

Ninguno. Phase 1 cerrada en `main` (último commit Phase 1: `0208748 chore: ci sanity check (#8)` + cleanup #10-#13). CONTEXT de Phase 2 listo.

### Risks watch list (de `REQUIREMENTS.md` § Risks)

- Procastinación hacia Fase 2 EDI antes de cerrar Pre-Fase 2 → recordar costo 10x deuda técnica
- Pre-commit OCA genera 100+ cambios cosméticos → mitigado por CI-02 commit baseline
- `gitleaks` puede encontrar tokens en history → política documentada: rotar + documentar, NO reescribir history
- Tentación a empezar `l10n_py_industry_retail` durante Phase 5 → explícito en spec: primer rubro post Fase 2 EDI
- `semantic-release` opinionated rompe con commits no perfectos → REL-06 empezar manual, automatizar después

---

## Session Continuity

### Last session (2026-06-03) — Plan 02-03 executed (Wave 3)

- **Command:** `/gsd:execute-phase 2 --wave 3`
- **Inputs:** `02-03-PLAN.md`, `02-CONTEXT.md` (D-02 + D-04 + Deferred), `02-RESEARCH.md` (gitleaks Windows fallback), `.github/workflows/security.yml`
- **Outputs:**
  - `.planning/phases/02-bloque-b-security-baseline/02-03-SUMMARY.md` — gitleaks 0 findings, Bandit 0 findings, branch protection now 6 contexts on main (commits `e40b8fa` initial + `69e2b90` checkpoint closure on branch `feat/sec-04-sec-05-baseline`)
  - **Repo settings:** GitHub branch protection on `main` `required_status_checks.contexts` extended to include `gitleaks`, `bandit`, `dependency-review` (alongside Phase 1 `pre-commit`, `test with Odoo`, `commitlint`)
- **Branch:** `feat/sec-04-sec-05-baseline` (worktree-merged `--no-ff`; pending push + PR)
- **REQs closed:** SEC-04, SEC-05, T-SEC-03-protection (the branch-protection arm of SEC-03)
- **Next session:** `/gsd:execute-phase 2 --wave 4` (Plans 02-04 + 02-05 in parallel — docs/60 + docs/61 + restore-smoke stub + README badge)

### Previous session (2026-06-02) — Plan 02-01 + Plan 02-02 executed

- **Commands:** `/gsd:execute-phase 2` (Plan 02-01) → `/gsd:execute-phase 2 --wave 2` (Plan 02-02)
- **Outputs:**
  - `LICENSE` AGPL-3.0 canonical text, SHA256 verified (commit `de5de11`); `SECURITY.md` GH Advisories channel (commit `c365ea1`); 02-01-SUMMARY (commit `be7d166`). Wave 1 PR #16 merged.
  - `.github/workflows/security.yml` 3 jobs (gitleaks @v3, bandit `-lll -iii`, dependency-review @v4); 02-02-SUMMARY + STATE/ROADMAP updates. Wave 2 PR #18 merged. Dependency Graph + Dependabot alerts approved.
- **REQs closed:** SEC-01, SEC-02, SEC-03

### Previous session (2026-06-02) — CONTEXT + PLAN

- **Command:** `/gsd:discuss-phase 2` (resumed from checkpoint dejado 2026-05-28)
- **Outputs:** `02-CONTEXT.md` (15 decisiones), `02-DISCUSSION-LOG.md`
- **Next was:** `/gsd:plan-phase 2` → created `02-01-PLAN.md` through `02-05-PLAN.md`

### Previous session (2026-05-28)

- **Phase 1 cerrada en `main`** vía PRs #3-#6, #8, #10-#13. CI/CD + pre-commit + branch protection activos.
- **Cleanup TDs:** TD-004/005/006/007 cerrados en PRs #11-#13.
- **Checkpoint discuss-phase 2** dejado parcial (1 de 4 áreas) — retomado hoy.

### Previous session (2026-05-27)

- **Command:** `/gsd:discuss-phase 1`
- **Output:** `01-CONTEXT.md` + `01-DISCUSSION-LOG.md` (16 decisiones D-01..D-16) + Commit `7e6c30a docs(01): capture phase context`

### How to resume

```
/gsd:resume-work
```

Lee STATE.md → identifica current focus (Phase 2 Plans 02-01 + 02-02 + 02-03 complete, Waves 1+2+3 done) → sugiere próximo comando (`/gsd:execute-phase 2 --wave 4` para Plans 02-04 + 02-05 en paralelo).

---

## Subagent Defaults (override CLAUDE.md proyecto, §"Skills + subagents")

Subagents disponibles relevantes para este milestone (verificar con `ls ~/.claude/agents/voltagent-*`):

| Phase                 | Subagent primario                                       | Skills sugeridas                                           |
| --------------------- | ------------------------------------------------------- | ---------------------------------------------------------- |
| Phase 1 (CI)          | `voltagent-dev-exp:git-workflow-manager` + `python-pro` | `superpowers:writing-plans`, `superpowers:executing-plans` |
| Phase 2 (Sec)         | `voltagent-qa-sec:security-auditor` (opus)              | `ecc:security-review`                                      |
| Phase 3 (Docs)        | `voltagent-dev-exp:documentation-engineer`              | `superpowers:writing-plans`                                |
| Phase 4 (Release)     | `voltagent-dev-exp:git-workflow-manager`                | —                                                          |
| Phase 5 (Multi-rubro) | `architect-reviewer` (opus) para ADR-0004               | `superpowers:brainstorming` antes de ADR                   |
| Antes de cada PR      | `voltagent-qa-sec:code-reviewer`                        | `superpowers:verification-before-completion`               |

---

_STATE initialized: 2026-05-26 — initial GSD bootstrap of milestone Pre-Fase 2._
_STATE updated: 2026-06-02 — Phase 1 closed, Phase 2 CONTEXT.md ready, awaiting plan-phase._
_STATE updated: 2026-06-02 — Plan 02-01 complete (SEC-01, SEC-02 closed). Wave 1 Phase 2 done. Next: Plan 02-02._
_STATE updated: 2026-06-02 — Plan 02-02 complete (SEC-03 closed). Wave 2 Phase 2 done. Next: Plan 02-03 (Wave 3)._
_STATE updated: 2026-06-03 — Plan 02-03 complete (SEC-04, SEC-05, T-SEC-03-protection closed). Wave 3 Phase 2 done. Next: Wave 4 = Plans 02-04 + 02-05 in parallel._
_STATE updated: 2026-06-09 — Plan 04-01 complete (REL-01 closed). GitHub issue intake layer (`.github/ISSUE_TEMPLATE/{bug_report,feature_request,config}.yml`). Next: Plan 04-02._
_STATE updated: 2026-06-09 — Plan 04-02 complete (REL-02, REL-03, REL-04, REL-06 closed). PR-hygiene + release-categorization meta-files (`.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/release.yml`) + CONTRIBUTING.md §Release process documented. Commits `76eac19` + `b46f4df`. Next: Plan 04-03 (create release.yml labels)._
_STATE updated: 2026-06-09 — Plan 04-04 complete (REL-05 closed). CHANGELOG [0.1.0] date-stamped (50834d4), PR #25 merged to main (01fe470, 9 CI checks green), annotated tag v0.1.0 pushed, GitHub Release v0.1.0 published (Latest, isDraft=false, isPrerelease=false). Phase 04 Bloque D COMPLETE (4/4 plans). Next: Phase 05 (Bloque E — Multi-rubro foundation) via `/gsd:plan-phase 5`._
_STATE updated: 2026-06-10 — Phase 05 complete (IND-01..04 closed via direct execution, ADR-0004 accepted, docs/80 created, grep audit clean). Milestone Pre-Fase 2 COMPLETE 35/35 REQs._
