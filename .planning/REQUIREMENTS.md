# Requirements: l10n-paraguay — Milestone Pre-Fase 2 Foundation

**Defined:** 2026-05-26
**Milestone:** Pre-Fase 2 — Foundation & Housekeeping
**Source spec:** [`docs/55_PRE_FASE_2_FOUNDATION.md`](../docs/55_PRE_FASE_2_FOUNDATION.md)
**Core Value:** Llevar el repo de "side project con código" a "proyecto OCA-ready" — CI/CD, security baseline, docs operacionales, repo hygiene, decisiones multi-rubro — antes de tocar firma digital + CCFE en Fase 2.

> **Audiencia de este milestone:** maintainers + contribuidores futuros + reviewers OCA. La "user story" implícita en cada REQ es *"como maintainer / contribuidor / reviewer, puedo X sin fricción"*.

---

## v1 Requirements

### CI — Bloque A: Foundation técnica (CI/CD + pre-commit)

- [ ] **CI-01**: Pre-commit config (`.pre-commit-config.yaml`) con hooks OCA completos (black, isort, flake8, pylint-odoo, oca-checks-odoo-module, oca-fix-manifest-version, codespell, yamllint) corre limpio sobre todo el repo
- [ ] **CI-02**: Commit baseline `chore: apply pre-commit fixes baseline` aplicado antes de activar pre-commit en CI (mitigación de 100+ cambios cosméticos del primer run)
- [ ] **CI-03**: GitHub Actions workflow `test.yml` ejecuta tests Odoo en matriz Python 3.11 + PostgreSQL 16 + Odoo 18.0, con tags `-standard,l10n_py` (skip external SIFEN)
- [ ] **CI-04**: GitHub Actions workflow `lint.yml` corre pre-commit en cada PR contra `main`
- [ ] **CI-05**: `.github/dependabot.yml` configurado para Python deps + GitHub Actions versions con frecuencia semanal
- [ ] **CI-06**: `commitlint.config.js` + GitHub Action validan Conventional Commits en cada PR
- [ ] **CI-07**: Branch protection en `main` configurado: PR required (incluso owner), status checks (lint + tests) must pass, conversation resolution required, no force push
- [ ] **CI-08**: PR de prueba (`chore: ci sanity check`) verifica que push directo a `main` es rechazado y que el workflow completo (lint+test) corre verde

### SEC — Bloque B: Security baseline

- [ ] **SEC-01**: `LICENSE` file con texto completo AGPL-3.0 en la raíz, referenciado desde `__manifest__.py` de cada módulo (`l10n_py_base`, `l10n_py_account`)
- [ ] **SEC-02**: `SECURITY.md` documenta versiones soportadas, canal de reporte de vulnerabilidades (email + PGP opcional), SLA (72h confirmación / 30d fix), Hall of Fame
- [ ] **SEC-03**: GitHub Actions workflow `security.yml` corre `gitleaks` (secrets scan) + `Bandit` (SAST Python en `addons/`) + Dependency Review en cada PR
- [ ] **SEC-04**: `gitleaks` no encuentra secrets en history; si hay false positives, documentar en `.gitleaksignore`. Tokens reales detectados se rotan (NO se reescribe git history)
- [ ] **SEC-05**: `Bandit` pasa en todos los addons sin warnings críticos (HIGH severity)
- [ ] **SEC-06**: `docs/60_SECURITY_BASELINE.md` documenta: auth/2FA strategy admin Odoo, password policy, audit logs (qué, retention, GDPR/LGPD), backup strategy (frequency, retention, monthly restore test), CCFE encryption strategy (Fernet + key rotation 90d), network security (firewall rules VPS)
- [ ] **SEC-07**: `docs/61_COMPLIANCE_LEY_6534.md` documenta Ley 6534/2020 PY Protección Datos Personales: qué aplica, DPO si aplica, consent management para datos de clientes

### DOC — Bloque C: Documentación operacional

- [ ] **DOC-01**: `README.md` raíz refleja estado real (no "TODO" en módulos terminados), badges (CI, license), quick start funcional con docker-compose, links a docs/
- [ ] **DOC-02**: `CHANGELOG.md` formato Keep a Changelog con `v0.1.0` inicial documentando Fase 0 (bootstrap) + Fase 1 (base + account)
- [ ] **DOC-03**: `CONTRIBUTING.md` cubre: setup dev environment, branch naming (`feat/`, `fix/`, `refactor/`, `docs/`), Conventional Commits, code review process, testing requirements (cobertura ≥80% en código nuevo), pre-commit hooks
- [ ] **DOC-04**: `CODE_OF_CONDUCT.md` (OCA Code of Conduct boilerplate o Contributor Covenant 2.1)
- [ ] **DOC-05**: `docs/70_ARCHITECTURE.md` (overview vivo): C4 Context (actores externos DNIT/SET/Bancos), C4 Container (módulos `l10n_py_*` + dependencies OCA + Odoo core), Sequence diagram emisión FE end-to-end, State machine ciclo DTE (draft→posted→sent→approved→cancelled)
- [ ] **DOC-06**: `docs/71_DEPLOYMENT.md`: VPS requirements (specs, OS, ports), Docker Compose prod, Caddy reverse proxy SSL automático, Postgres backup automatizado (pg_dump + rsync S3), health checks, update procedure
- [ ] **DOC-07**: `docs/72_RUNBOOK.md` cubre ≥10 incidentes comunes con resolución: SIFEN timeout, Postgres disk full, SSL cert expira, CCFE expira, migración catálogos DNIT, escalation path
- [ ] **DOC-08**: `docs/adr/` inicializado con ADRs 0001-0005: 0001 Odoo Community no Enterprise, 0002 OCA-style from day one, 0003 DNIT catalogs as source of truth, 0004 Multi-rubro strategy (cross-ref con IND-01), 0005 Hosting strategy preliminar (sin commit a vendor)
- [ ] **DOC-09**: Regla en `CONTRIBUTING.md` — cambio arquitectónico = nuevo ADR en el mismo PR (prevención de ADR rot)
- [ ] **DOC-10**: Smoke test docs (validación humana): cualquier dev externo puede levantar el proyecto siguiendo solo `CONTRIBUTING.md`

### REL — Bloque D: Repo hygiene + Release process

- [ ] **REL-01**: `.github/ISSUE_TEMPLATE/` con templates: `bug_report.yml`, `feature_request.yml`, `question.yml`, `config.yml` con links a Discussions
- [ ] **REL-02**: `.github/PULL_REQUEST_TEMPLATE.md` con checklist (tests, docs, ADR si aplica, conventional commits)
- [ ] **REL-03**: `.github/CODEOWNERS` con `@Ezcareaga` para todo el repo por ahora; estructura preparada para agregar contribuidores por área futuro
- [ ] **REL-04**: `.github/release.yml` con categorías auto para release notes (feat→Added, fix→Fixed, etc.)
- [ ] **REL-05**: Release `v0.1.0` publicado en GitHub: tag `v0.1.0`, release notes manuales del primer release, asociado al estado actual post-Fase 1
- [ ] **REL-06**: Decisión semantic-release vs manual documentada y release process escrito en `CONTRIBUTING.md`. Si SÍ semantic-release: `.releaserc.json` + workflow correspondiente. Si NO: pasos manuales documentados

### IND — Bloque E: Multi-rubro foundation

- [ ] **IND-01**: `docs/adr/0004-multi-rubro-strategy.md` formaliza decisión: `l10n_py_base` y `l10n_py_account` son **rubro-agnósticos**, NO contienen asunciones de minimarket/gastronomía/servicios; rubros específicos se construyen como módulos `l10n_py_industry_*` (retail, hospitality, services, ecommerce) que extienden `l10n_py_pos` (Fase 4) con presets, demo data, vistas
- [ ] **IND-02**: `docs/80_MULTI_RUBRO_ROADMAP.md`: cuándo se construye cada `l10n_py_industry_*` (post Fase 6 OCA), demo data por rubro, hardware compatibility matrix por rubro (lector de barras retail, impresora térmica hospitality), onboarding wizard que pregunta rubro y aplica presets
- [ ] **IND-03**: Auditoría del código actual confirma rubro-agnosticismo: `grep -r "minimarket\|gastronom\|hospedaje\|comercio\|restaurante" addons/` no encuentra strings que asuman rubro. Si encuentra, refactorizar o documentar como tech debt en `BUGS_BACKLOG.md`
- [ ] **IND-04**: Documentación de cómo crear un `l10n_py_industry_*` nuevo (template mínimo, qué hereda de base, qué agrega)

---

## v2 Requirements

Deferidos a Pre-Fase 3 o post-deployment (NO en este milestone — ver "Lo que NO está en Pre-Fase 2" en `docs/55_PRE_FASE_2_FOUNDATION.md`):

### Monitoring & Observability (Pre-Fase 3)

- **MON-01**: Sentry configuration para captura de errores en producción
- **MON-02**: Better Stack o equivalente para logs agregados
- **MON-03**: Uptime monitoring (statuspage o equivalente)

### Deploy real (Pre-Fase 3)

- **DEP-01**: VPS provisionado (Hetzner / Render / similar)
- **DEP-02**: Docker Compose producción funcionando con Caddy + Postgres + Odoo
- **DEP-03**: Primera implementación de homologación SIFEN (CCFE de prueba)

### OCA-ready completo (Fase 6)

- **OCA-01**: `copier copy gh:OCA/oca-addons-repo-template .` aplicado (decisión postponer — riesgo de pisar custom files)
- **OCA-02**: PRs a `OCA/l10n-paraguay` (proponer creación del repo)
- **OCA-03**: Anuncio en mailing list OCA + Odoo Paraguay community

### Vendibilidad / SaaS (Fase 8)

- **BIZ-01**: Landing page / docs site público
- **BIZ-02**: Pricing tiers
- **BIZ-03**: Hardware compatibility matrix completo (lector código, balanza, etc.)
- **BIZ-04**: Training plan para usuarios PyME no técnicos

---

## Out of Scope

Excluido explícitamente de este milestone con razonamiento (prevención de scope creep):

| Feature | Razón |
|---|---|
| Monitoring avanzado (Sentry, Better Stack) | Pre-Fase 3 — antes de primer cliente real. Sin clientes en prod aún, monitoring sería ruido |
| VPS deploy real | Pre-Fase 3 — depende de Pre-Fase 2 completa primero (CI/security/docs) |
| Onboarding wizard / presets por rubro | Fase 7 multi-rubro — requiere `l10n_py_pos` (Fase 4) en pie primero |
| Landing page / docs site público | Fase 8 vendibilidad — sin features completas no hay qué vender |
| Pricing tiers / SaaS model | Fase 8 — proyecto target self-hosted, SaaS viene después de validación con clientes |
| Hardware compatibility matrix completo | Con primer cliente real — sin hardware en mano, matrix es especulativa |
| Training plan PyME | Con primer cliente real — UX se valida con usuarios, no en doc previo |
| OCA copier real (`copier copy gh:OCA/oca-addons-repo-template .`) | Fase 6 — riesgo de pisar archivos custom. Si decide aplicar en Pre-Fase 2 Bloque A, hacer en branch separada con review cuidadoso |
| `l10n_py_industry_retail` (o cualquier rubro específico) | Post Fase 2 EDI — tentación a empezar para "amiga del minimarket" explícitamente rechazada en spec |
| Reescribir git history para sacar tokens viejos | Rompe forks. Estrategia: documentar, rotar, NO reescribir |
| Optimización exhaustiva pre-commit (todos los hooks OCA en su versión más nueva) | Empezar con minimum viable, iterar después con uso real |
| C4 Code (nivel 4) en ARCHITECTURE.md | Overkill para overview vivo. Container + Component suficiente |
| Tests E2E contra SIFEN test real | Bloque B (`security`) NO incluye homologación. Eso es Fase 2 propiamente |

---

## Traceability

> Esta sección la llena `gsd-roadmapper` al crear `ROADMAP.md`. Cada REQ-ID se mapea a exactamente una phase.

| Requirement | Phase | Status |
|---|---|---|
| CI-01 | TBD | Pending |
| CI-02 | TBD | Pending |
| CI-03 | TBD | Pending |
| CI-04 | TBD | Pending |
| CI-05 | TBD | Pending |
| CI-06 | TBD | Pending |
| CI-07 | TBD | Pending |
| CI-08 | TBD | Pending |
| SEC-01 | TBD | Pending |
| SEC-02 | TBD | Pending |
| SEC-03 | TBD | Pending |
| SEC-04 | TBD | Pending |
| SEC-05 | TBD | Pending |
| SEC-06 | TBD | Pending |
| SEC-07 | TBD | Pending |
| DOC-01 | TBD | Pending |
| DOC-02 | TBD | Pending |
| DOC-03 | TBD | Pending |
| DOC-04 | TBD | Pending |
| DOC-05 | TBD | Pending |
| DOC-06 | TBD | Pending |
| DOC-07 | TBD | Pending |
| DOC-08 | TBD | Pending |
| DOC-09 | TBD | Pending |
| DOC-10 | TBD | Pending |
| REL-01 | TBD | Pending |
| REL-02 | TBD | Pending |
| REL-03 | TBD | Pending |
| REL-04 | TBD | Pending |
| REL-05 | TBD | Pending |
| REL-06 | TBD | Pending |
| IND-01 | TBD | Pending |
| IND-02 | TBD | Pending |
| IND-03 | TBD | Pending |
| IND-04 | TBD | Pending |

**Coverage:**
- v1 requirements: **35 total**
- Mapped to phases: 0 (pending roadmapper)
- Unmapped: 35 ⚠️ (será 0 después de `gsd-roadmapper`)

**v1 breakdown by Bloque:**
| Bloque | Categoría | REQ count |
|---|---|---|
| A — Foundation técnica | CI-01..08 | 8 |
| B — Security baseline | SEC-01..07 | 7 |
| C — Documentación operacional | DOC-01..10 | 10 |
| D — Repo hygiene + Release | REL-01..06 | 6 |
| E — Multi-rubro foundation | IND-01..04 | 4 |
| **Total** | — | **35** |

---

## User Stories

Lean PRD-style summary del valor que cada Bloque entrega:

- **Como maintainer**, al pushear código a una PR, quiero que **CI corra lint + tests automáticamente** y rechace merges con problemas, para no depender de mi disciplina manual *(Bloque A)*.
- **Como future cliente PyME**, al recibir el módulo, quiero que **el manejo de CCFE/firmas digitales tenga estrategia documentada de encriptación, backup y rotación de keys**, para confiar que mis certificados privados están protegidos *(Bloque B)*.
- **Como reviewer OCA**, al evaluar el repo para mergear a `OCA/l10n-paraguay`, quiero ver **README real, CONTRIBUTING.md completo, ADRs versionados, ARCHITECTURE.md, RUNBOOK.md**, para aceptarlo sin pedirme yo mismo todo eso *(Bloque C)*.
- **Como contribuidor externo**, al querer aportar al repo, quiero **issue templates, PR template, CODEOWNERS, release notes**, para saber cómo contribuir sin preguntar *(Bloque D)*.
- **Como dev futuro** que necesita crear un módulo `l10n_py_industry_*`, quiero **estrategia multi-rubro formalizada en un ADR + roadmap doc**, para no duplicar trabajo ni asumir mal qué hace base vs qué hace industry *(Bloque E)*.

## Acceptance Criteria

El milestone Pre-Fase 2 está **complete** cuando:

1. ✅ Todos los 35 REQs marcados como `[x]` (verificados en sus respectivos checkbox tests)
2. ✅ `pre-commit run --all-files` corre limpio en `main`
3. ✅ Push directo a `main` es rechazado por GitHub branch protection
4. ✅ PR de prueba pasa lint + tests + security workflows en verde
5. ✅ Release `v0.1.0` publicado en GitHub con notes
6. ✅ `gitleaks` no detecta secrets en HEAD
7. ✅ Dev externo (test humano, no agente) puede levantar el proyecto siguiendo solo `CONTRIBUTING.md`
8. ✅ ADRs 0001-0005 mergeados en `docs/adr/`
9. ✅ Auditoría multi-rubro confirma rubro-agnosticismo de base/account

## Definition of Done

> Release criteria para considerar el milestone shipeable y avanzar a Fase 2 EDI.

| Categoría | Criterio | Cómo se verifica |
|---|---|---|
| CI | Lint + test workflow verde en `main` desde hace ≥3 PRs consecutivos | GitHub Actions history |
| CI | Branch protection bloquea push directo a `main` | Test manual: `git push origin main` rechazado |
| Sec | `gitleaks` + Bandit verdes en CI | Workflow run latest |
| Sec | `LICENSE` AGPL-3.0 en raíz + en manifests | `cat LICENSE` + `grep license addons/*/  __manifest__.py` |
| Docs | README sin "TODO" en módulos completados | Grep `TODO` en README |
| Docs | CHANGELOG `v0.1.0` con entries reales | Manual read |
| Docs | ARCHITECTURE + DEPLOYMENT + RUNBOOK + ADRs 0001-0005 presentes | `ls docs/70*.md docs/71*.md docs/72*.md docs/adr/000*.md` |
| Rel | Issue templates + PR template + CODEOWNERS presentes | `ls .github/` |
| Rel | Tag `v0.1.0` en GitHub Releases con notes | `gh release view v0.1.0` |
| Rubro | ADR 0004 + docs/80 + auditoría grep verde | Manual read + grep |
| Coverage | Cobertura tests ≥80% en código nuevo (módulos existentes baseline) | `coverage report` |
| Process | Cualquier PR pasa Conventional Commits validation | commitlint workflow |

---

## Risks & Dependencies

**Risks (de la spec `docs/55_PRE_FASE_2_FOUNDATION.md` sección "Riesgos generales"):**

| Riesgo | Mitigación |
|---|---|
| Procastinación: "estoy ansioso por empezar Fase 2 EDI" | Recordar: deuda técnica de empezar Fase 2 sin foundation cuesta 10x después. Cerrar Pre-Fase 2 antes de tocar EDI |
| Over-engineering en docs operacionales | Empezar con minimum viable docs, iterar después con uso real |
| Pre-commit OCA genera 100+ cambios cosméticos | Commit baseline ANTES de activar en CI (CI-02 explícito) |
| Auditoría multi-rubro encuentra acoplamientos | Documentar como tech debt en `BUGS_BACKLOG.md`, refactor en Fase 6 (no acá) |
| Security baseline parece exagerado | No lo es. Vas a manejar CCFE — nivel banco. SEC-06 establece la baseline |
| Tentación a empezar `l10n_py_industry_retail` durante Bloque E | Explícito en spec: primer rubro se construye DESPUÉS de Fase 2 EDI, no antes |
| `gitleaks` encuentra tokens en history | Documentar + rotar tokens. NO reescribir history (rompe forks) |
| `semantic-release` opinionated rompe si commits no perfectos | Empezar manual (REL-06), automatizar después |

**Dependencies:**

- **Hard**: PR2 mergeado a `main` (Fase 1 completa). ✅ Cumplido (`3fc654a docs(claude): harden subagent rule + Fase 1 retrospectiva consolidada`)
- **Soft**: Subagents VoltAgent instalados (`voltagent-lang`, `voltagent-qa-sec`, `voltagent-dev-exp`, `voltagent-meta`). Crítico para Bloque B (`security-auditor` opus) y C (`documentation-engineer`). Verificar con `ls ~/.claude/agents/voltagent-*` antes de Bloque B.
- **External**: Repo configurado en GitHub con permisos de admin (para configurar branch protection — CI-07). Owner = `@Ezcareaga`. ✅ Cumplido.
- **External**: Cuenta GitHub permite ejecutar GitHub Actions (free tier alcanza con 2k min/mes — verificar).

---

*Requirements defined: 2026-05-26*
*Source: `docs/55_PRE_FASE_2_FOUNDATION.md`*
*Last updated: 2026-05-26 after initial definition (pre-roadmapper)*
