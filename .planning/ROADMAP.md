# ROADMAP — Milestone Pre-Fase 2 Foundation

**Milestone:** Pre-Fase 2 — Foundation & Housekeeping
**Created:** 2026-05-26
**Source spec:** [`docs/55_PRE_FASE_2_FOUNDATION.md`](../docs/55_PRE_FASE_2_FOUNDATION.md)
**Requirements:** [`.planning/REQUIREMENTS.md`](REQUIREMENTS.md)
**Granularity:** standard
**Mode:** standard (Horizontal Layers — cada Bloque es una capa de foundation, NO un slice de end-user feature)
**Coverage:** 35/35 v1 requirements mapped

---

## Core Value

Llevar el repo de "side project con código" a "proyecto OCA-ready" — CI/CD,
security baseline, docs operacionales, repo hygiene, decisiones multi-rubro —
**antes** de tocar firma digital + CCFE en Fase 2 (`l10n_py_edi` MVP, 8-12
semanas).

## Audiencia

Maintainers + contribuidores futuros + reviewers OCA. NO clientes finales.
La "user story" implícita por REQ: _"como maintainer / contribuidor / reviewer,
puedo X sin fricción"_.

---

## Phases

- [ ] **Phase 1: Bloque A — Foundation técnica (CI/CD + pre-commit)** — Activar pre-commit OCA + GitHub Actions (lint, test, dependabot, commitlint) + branch protection en `main`
- [ ] **Phase 2: Bloque B — Security baseline** — LICENSE + SECURITY.md + workflow `security.yml` (gitleaks + Bandit) + docs/60-61 (security baseline + compliance Ley 6534)
- [ ] **Phase 3: Bloque C — Documentación operacional** — README real + CHANGELOG + CONTRIBUTING + CODE_OF_CONDUCT + docs/70-72 (ARCHITECTURE, DEPLOYMENT, RUNBOOK) + ADRs 0001-0005
- [ ] **Phase 4: Bloque D — Repo hygiene + Release process** — Issue/PR templates + CODEOWNERS + release.yml + tag `v0.1.0` + decisión semantic-release vs manual
- [ ] **Phase 5: Bloque E — Multi-rubro foundation** — ADR-0004 + docs/80 multi-rubro roadmap + auditoría grep rubro-agnosticismo + guía mínima `l10n_py_industry_*`

---

## Phase Details

### Phase 1: Bloque A — Foundation técnica (CI/CD + pre-commit)

**Goal**: Cualquier push o PR a este repo dispara automáticamente lint + tests y `main` está protegido contra merges sin checks verdes.
**Depends on**: Nothing (Fase 1 ya está cerrada en `main`; esta phase desbloquea el resto del milestone).
**Requirements**: CI-01, CI-02, CI-03, CI-04, CI-05, CI-06, CI-07, CI-08 (8 REQs)
**Complexity**: large (8 REQs, 3-4 días — la phase más cargada de infra de la milestone)
**Internal sequencing** (no se puede paralelizar dentro de la phase):

1. CI-01 (configurar `.pre-commit-config.yaml`)
2. CI-02 (commit baseline `chore: apply pre-commit fixes baseline` — 100+ cambios cosméticos absorbidos en UN commit)
3. CI-04 (activar `lint.yml` que corre el pre-commit ya estabilizado)
4. CI-03 + CI-05 + CI-06 en paralelo (test workflow, dependabot, commitlint son independientes entre sí)
5. CI-07 (branch protection) — necesita que los status checks ya existan en GitHub para poder marcarlos como required
6. CI-08 (PR de prueba `chore: ci sanity check`) — verificación final end-to-end
   **Success Criteria** (what must be TRUE):
7. `pre-commit run --all-files` corre limpio sobre todo el repo (hooks OCA: black, isort, flake8, pylint-odoo, oca-checks-odoo-module, oca-fix-manifest-version, codespell, yamllint)
8. Push directo a `main` (incluso desde la cuenta owner `@Ezcareaga`) es rechazado por GitHub con mensaje de branch protection
9. Una PR de prueba (`chore: ci sanity check`) dispara workflows `lint.yml` + `test.yml` y ambos terminan verdes antes de poder mergearse
10. Dependabot abre PRs automáticas semanales cuando hay updates de Python deps o GitHub Actions versions
11. Commit message que viola Conventional Commits (ej. `fixed bug`) es rechazado por el GitHub Action de commitlint
    **Plans**: TBD
    **UI hint**: no

### Phase 2: Bloque B — Security baseline

**Goal**: Quien clone el repo encuentra LICENSE + SECURITY.md visibles, los workflows de security corren en CI rechazando secrets y código vulnerable, y existe estrategia escrita de cómo se va a manejar CCFE/datos personales en producción.
**Depends on**: Phase 1 (los workflows de seguridad necesitan la infra CI/Actions ya levantada; sin Phase 1 no hay donde correr `security.yml`).
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-06, SEC-07 (7 REQs)
**Complexity**: medium (7 REQs, 2-3 días — mezcla rápido de archivos config + escritura densa de docs/60-61)
**Success Criteria** (what must be TRUE):

1. `LICENSE` (AGPL-3.0 texto completo) existe en raíz y `__manifest__.py` de `l10n_py_base` y `l10n_py_account` referencia `license="AGPL-3"` consistente
2. `gitleaks` corriendo en CI no encuentra secrets en HEAD; cualquier falso positivo está documentado en `.gitleaksignore` con razón
3. `Bandit` corre en `addons/` sin un solo warning de severidad HIGH (warnings MEDIUM/LOW pueden quedar como tech debt documentada)
4. `SECURITY.md` describe versiones soportadas, canal de reporte (email + PGP opcional), SLA (72h confirmación / 30d fix) y Hall of Fame
5. `docs/60_SECURITY_BASELINE.md` documenta los 6 ejes: auth/2FA admin, password policy, audit logs (retention + GDPR/LGPD), backup (frequency + retention + monthly restore test), CCFE encryption (Fernet + key rotation 90d), network security (firewall VPS)
6. `docs/61_COMPLIANCE_LEY_6534.md` cubre Ley 6534/2020 PY: qué aplica al proyecto, criterio DPO, consent management para datos de clientes
   **Plans**: TBD
   **UI hint**: no

### Phase 3: Bloque C — Documentación operacional

**Goal**: Un dev externo (sin contexto previo) puede levantar el proyecto local + entender la arquitectura + saber cómo se despliega + qué hacer ante los 10 incidentes más probables, leyendo solo lo que está en raíz + `docs/`.
**Depends on**: Phase 2 (DOC-06 DEPLOYMENT referencia la backup strategy definida en SEC-06; DOC-08 ADR-0005 hosting strategy referencia network security de SEC-06).
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04, DOC-05, DOC-06, DOC-07, DOC-08, DOC-09, DOC-10 (10 REQs)
**Complexity**: large (10 REQs, 4-5 días — la phase más grande del milestone, escribir docs densos: ARCHITECTURE C4 + DEPLOYMENT + RUNBOOK + 5 ADRs)
**Parallelizable with**: Phase 5 (Bloque E es independiente del bloque doc operacional excepto por la cross-ref ADR-0004; si `parallelization=true` ambas phases pueden ejecutarse simultáneamente, sincronizando solo al momento de mergear el ADR-0004).
**Success Criteria** (what must be TRUE):

1. `README.md` raíz refleja estado real (no contiene "TODO" en módulos terminados), incluye badges (CI, license), quick start funcional con docker-compose y links operativos a `docs/`
2. `CHANGELOG.md` formato Keep a Changelog con entry `v0.1.0` documentando Fase 0 (bootstrap) + Fase 1a (`l10n_py_base`) + Fase 1b (`l10n_py_account`)
3. `CONTRIBUTING.md` cubre los 6 ejes: setup dev env, branch naming, Conventional Commits, code review, testing (cobertura ≥80% en código nuevo), pre-commit; e incluye la regla DOC-09 "cambio arquitectónico = nuevo ADR en el mismo PR"
4. `docs/70_ARCHITECTURE.md` contiene C4 Context (actores DNIT/SET/Bancos), C4 Container (módulos `l10n_py_*` + deps OCA + Odoo core), sequence diagram emisión FE end-to-end, state machine ciclo DTE (draft→posted→sent→approved→cancelled)
5. `docs/71_DEPLOYMENT.md` describe VPS requirements, Docker Compose prod, Caddy reverse proxy SSL, backup Postgres automatizado, health checks, update procedure; y `docs/72_RUNBOOK.md` cubre ≥10 incidentes (SIFEN timeout, Postgres disk full, SSL expira, CCFE expira, migración catálogos DNIT, etc.) con resolución y escalation path
6. `docs/adr/` contiene ADRs 0001 (Odoo Community), 0002 (OCA-style desde día 1), 0003 (DNIT catalogs como source of truth), 0004 (multi-rubro strategy — cross-ref con IND-01 de Phase 5), 0005 (hosting strategy preliminar sin commit a vendor)
7. Smoke test humano (DOC-10): un dev externo levanta el proyecto siguiendo SOLO `CONTRIBUTING.md`, sin pedir contexto extra
   **Plans**: TBD
   **UI hint**: no

### Phase 4: Bloque D — Repo hygiene + Release process

**Goal**: Cualquier contribuidor externo abre issues y PRs llenando templates pre-armados, las release notes se generan con categorías auto, y existe `v0.1.0` taggeado en GitHub como punto de rollback verificable post-Fase 1.
**Depends on**: Phase 3 (REL-06 documenta el release process _dentro_ de `CONTRIBUTING.md`, que se creó en Phase 3 DOC-03).
**Requirements**: REL-01, REL-02, REL-03, REL-04, REL-05, REL-06 (6 REQs)
**Complexity**: small (6 REQs, 1-2 días — mayoría son archivos boilerplate `.github/*`)
**Success Criteria** (what must be TRUE):

1. `.github/ISSUE_TEMPLATE/` contiene `bug_report.yml` + `feature_request.yml` + `question.yml` + `config.yml` con links a Discussions; abrir un issue nuevo en GitHub fuerza al usuario a elegir template
2. `.github/PULL_REQUEST_TEMPLATE.md` se autocompleta al abrir una PR, e incluye checklist (tests, docs, ADR si aplica, Conventional Commits)
3. `.github/CODEOWNERS` asigna `@Ezcareaga` como owner por defecto de todo el repo, con estructura preparada para agregar áreas (`addons/l10n_py_*/`, `docs/`, `.github/`) sin reescribir el archivo
4. `.github/release.yml` mapea automáticamente labels/Conventional Commits a categorías de release notes (`feat:` → Added, `fix:` → Fixed, etc.)
5. Tag `v0.1.0` existe en GitHub Releases con notes manuales que describen el estado post-Fase 1 (l10n_py_base 18.0.1.1.0 + l10n_py_account 18.0.1.0.0, 97 tests verdes)
6. La sección "Release process" de `CONTRIBUTING.md` documenta explícitamente la decisión semantic-release vs manual: si semantic-release ON, hay `.releaserc.json` + workflow funcionando; si OFF, los pasos manuales están enumerados paso a paso
   **Plans**: TBD
   **UI hint**: no

### Phase 5: Bloque E — Multi-rubro foundation

**Goal**: La decisión de que `l10n_py_base` + `l10n_py_account` son rubro-agnósticos está formalizada en ADR + roadmap doc + auditoría grep verificable; cualquier dev futuro sabe cómo construir un módulo `l10n_py_industry_*` sin tener que adivinar la frontera.
**Depends on**: Phase 1 (la auditoría grep es liviana, pero el commit que cierra esta phase asume pre-commit y CI activos para no introducir regresiones cosméticas).
**Parallelizable with**: Phase 3 (Bloque E es independiente de los docs operacionales excepto por la cross-ref ADR-0004; con `parallelization=true` puede correr en paralelo a Phase 3, sincronizando solo en el merge del ADR-0004 que Phase 3 también referencia en DOC-08). También puede correr en paralelo a Phase 4.
**Requirements**: IND-01, IND-02, IND-03, IND-04 (4 REQs)
**Complexity**: small (4 REQs, 1-2 días — la phase más chica del milestone)
**Success Criteria** (what must be TRUE):

1. `docs/adr/0004-multi-rubro-strategy.md` formaliza explícitamente: `l10n_py_base` + `l10n_py_account` son rubro-agnósticos y los rubros se construyen como módulos `l10n_py_industry_*` (retail, hospitality, services, ecommerce) que extienden `l10n_py_pos` de Fase 4
2. `docs/80_MULTI_RUBRO_ROADMAP.md` documenta cuándo se construye cada `l10n_py_industry_*` (post Fase 6 OCA), demo data por rubro, hardware compatibility matrix por rubro (lector barras retail, impresora térmica hospitality), onboarding wizard que pregunta rubro y aplica presets
3. `grep -r "minimarket\|gastronom\|hospedaje\|comercio\|restaurante" addons/` no encuentra strings que asuman rubro; si encuentra, está refactorizado o documentado como tech debt explícita en `BUGS_BACKLOG.md`
4. Existe una sección/doc operativo (en `docs/80_*` o doc complementaria) que describe el template mínimo de un módulo `l10n_py_industry_*` nuevo: qué hereda de base/account, qué agrega, dónde van presets y demo data
   **Plans**: TBD
   **UI hint**: no

---

## Phase Dependency Graph

```
        Phase 1 (CI)
         │
         ├─────────────────┐
         ▼                 ▼
       Phase 2 (SEC)    Phase 5 (Multi-rubro)
         │                 │
         ▼                 │
       Phase 3 (DOC) ◀─────┘ (Phase 3 referencia ADR-0004 producido en Phase 5)
         │
         ▼
       Phase 4 (Release)
```

**Critical path:** Phase 1 → Phase 2 → Phase 3 → Phase 4
**Parallelizable:** Phase 5 puede correr en paralelo a Phase 3 y/o Phase 4 (depende solo de Phase 1).

`parallelization=true` en config.json habilita ejecutar Phase 5 en paralelo a
Phase 3, sincronizando en el ADR-0004 (Phase 5 produce el ADR, Phase 3 lo
referencia desde DOC-08).

---

## Coverage Map

| REQ-ID | Phase   | Bloque | Status  |
| ------ | ------- | ------ | ------- |
| CI-01  | Phase 1 | A      | Pending |
| CI-02  | Phase 1 | A      | Pending |
| CI-03  | Phase 1 | A      | Pending |
| CI-04  | Phase 1 | A      | Pending |
| CI-05  | Phase 1 | A      | Pending |
| CI-06  | Phase 1 | A      | Pending |
| CI-07  | Phase 1 | A      | Pending |
| CI-08  | Phase 1 | A      | Pending |
| SEC-01 | Phase 2 | B      | Pending |
| SEC-02 | Phase 2 | B      | Pending |
| SEC-03 | Phase 2 | B      | Pending |
| SEC-04 | Phase 2 | B      | Pending |
| SEC-05 | Phase 2 | B      | Pending |
| SEC-06 | Phase 2 | B      | Pending |
| SEC-07 | Phase 2 | B      | Pending |
| DOC-01 | Phase 3 | C      | Pending |
| DOC-02 | Phase 3 | C      | Pending |
| DOC-03 | Phase 3 | C      | Pending |
| DOC-04 | Phase 3 | C      | Pending |
| DOC-05 | Phase 3 | C      | Pending |
| DOC-06 | Phase 3 | C      | Pending |
| DOC-07 | Phase 3 | C      | Pending |
| DOC-08 | Phase 3 | C      | Pending |
| DOC-09 | Phase 3 | C      | Pending |
| DOC-10 | Phase 3 | C      | Pending |
| REL-01 | Phase 4 | D      | Pending |
| REL-02 | Phase 4 | D      | Pending |
| REL-03 | Phase 4 | D      | Pending |
| REL-04 | Phase 4 | D      | Pending |
| REL-05 | Phase 4 | D      | Pending |
| REL-06 | Phase 4 | D      | Pending |
| IND-01 | Phase 5 | E      | Pending |
| IND-02 | Phase 5 | E      | Pending |
| IND-03 | Phase 5 | E      | Pending |
| IND-04 | Phase 5 | E      | Pending |

**Coverage:** 35/35 ✓ (0 orphaned, 0 duplicated)

---

## Progress Table

| Phase                                   | Plans Complete | Status      | Completed |
| --------------------------------------- | -------------- | ----------- | --------- |
| 1. Bloque A — Foundation técnica        | 0/0            | Not started | -         |
| 2. Bloque B — Security baseline         | 0/0            | Not started | -         |
| 3. Bloque C — Documentación operacional | 0/0            | Not started | -         |
| 4. Bloque D — Repo hygiene + Release    | 0/0            | Not started | -         |
| 5. Bloque E — Multi-rubro foundation    | 0/0            | Not started | -         |

---

## Milestone-level Definition of Done

Pre-Fase 2 está **complete** cuando (de `REQUIREMENTS.md` § Acceptance Criteria):

1. Todos los 35 REQs marcados `[x]` en `REQUIREMENTS.md`
2. `pre-commit run --all-files` corre limpio en `main`
3. Push directo a `main` rechazado por GitHub branch protection
4. PR de prueba pasa lint + tests + security workflows verdes
5. Release `v0.1.0` publicado en GitHub con notes
6. `gitleaks` no detecta secrets en HEAD
7. Dev externo puede levantar el proyecto siguiendo solo `CONTRIBUTING.md`
8. ADRs 0001-0005 mergeados en `docs/adr/`
9. Auditoría multi-rubro confirma rubro-agnosticismo de base/account

Una vez cumplido, el siguiente milestone es **Fase 2 — `l10n_py_edi` MVP**
(CDC + firma XAdES + SOAP SIFEN + KuDE + eventos, 8-12 semanas).

---

_ROADMAP created: 2026-05-26 by `gsd-roadmapper`_
_Source: `docs/55_PRE_FASE_2_FOUNDATION.md` + `.planning/REQUIREMENTS.md`_
