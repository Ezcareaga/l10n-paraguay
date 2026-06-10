# MILESTONES — l10n-paraguay

Registro de milestones completados. Cada entry apunta al archive con el detalle completo.

---

## v0.1.0 — Pre-Fase 2 Foundation

**Shipped:** 2026-06-10
**Tag:** `v0.1.0` (publicado en GitHub Releases 2026-06-09)
**Archive:** [`.planning/milestones/v0.1.0-ROADMAP.md`](milestones/v0.1.0-ROADMAP.md)
**Requirements archive:** [`.planning/milestones/v0.1.0-REQUIREMENTS.md`](milestones/v0.1.0-REQUIREMENTS.md)
**Phase dirs:** [`.planning/milestones/v0.1.0-phases/`](milestones/v0.1.0-phases/)

| Stat      | Valor                                        |
| --------- | -------------------------------------------- |
| Phases    | 5 (Bloques A → E)                            |
| Plans GSD | 16 (14 formales + 2 ejecuciones directas)    |
| REQs v1   | 35/35 completados                            |
| Duración  | 2026-05-26 → 2026-06-10 (15 días calendario) |

### Accomplishments

- **CI/CD + pre-commit OCA activos**: `lint.yml` + `test.yml` + `commitlint` + dependabot + branch protection en `main` (6 required status checks). Push directo a `main` rechazado incluso para el owner.
- **Security baseline completo**: `gitleaks` (0 findings en 106 commits) + `Bandit` (0 findings en 2228 LOC) + Dependency Review en CI; `LICENSE` AGPL-3.0; `SECURITY.md`; `docs/60_SECURITY_BASELINE.md` (6 ejes); `docs/61_COMPLIANCE_LEY_7593.md` (Ley 7593/2025 PY, split vendor/operador, ARCO, matriz 10 filas).
- **Docs operacionales completas**: `README.md` real con badges + quick start; `CHANGELOG.md` Keep a Changelog; `CONTRIBUTING.md` (6 ejes + regla ADR); `CODE_OF_CONDUCT.md`; `docs/70_ARCHITECTURE.md` C4 + diagrams; `docs/71_DEPLOYMENT.md`; `docs/72_RUNBOOK.md` (10+ incidentes); 5 ADRs (`docs/adr/0001-0005`).
- **Repo hygiene completo**: `.github/ISSUE_TEMPLATE/` (bug_report + feature_request + config); `.github/PULL_REQUEST_TEMPLATE.md`; `.github/CODEOWNERS`; `.github/release.yml` (7 categorías).
- **Release v0.1.0 publicado**: tag `v0.1.0` en `01fe470` + GitHub Release publicado 2026-06-09T18:14:48Z como Latest; primer punto de rollback verificable del proyecto.
- **Multi-rubro foundation**: ADR-0004 aceptado (rubro-agnosticismo formalizado); `docs/80_MULTI_RUBRO_ROADMAP.md`; auditoría grep limpia (`addons/` sin strings de rubro); template mínimo `l10n_py_industry_*` documentado.

### Módulos en `main` al cierre

| Módulo            | Versión    | Tests         |
| ----------------- | ---------- | ------------- |
| `l10n_py_base`    | 18.0.1.1.0 | 23 verdes     |
| `l10n_py_account` | 18.0.1.0.0 | 74 verdes     |
| **Total**         | —          | **97 verdes** |

---

_Este archivo se actualiza al cierre de cada milestone._
_Creado: 2026-06-10_
