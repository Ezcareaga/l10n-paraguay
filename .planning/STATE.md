---
gsd_state_version: 1.0
milestone: v0.1.0
milestone_name: Pre-Fase 2 Foundation
current_phase: "ARCHIVED"
status: "ARCHIVED — shipped 2026-06-10. 35/35 v1 REQs. Archive: .planning/milestones/v0.1.0-ROADMAP.md"
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
- **Active roadmap:** [`.planning/ROADMAP.md`](ROADMAP.md)
- **Milestones:** [`.planning/MILESTONES.md`](MILESTONES.md)

## Current Focus

- **Last milestone:** v0.1.0 Pre-Fase 2 Foundation — **ARCHIVED 2026-06-10**
- **Status:** Milestone v0.1.0 archivado. Next: `/gsd:new-milestone` (Fase 2 — l10n_py_edi MVP)
- **Archive:** [`.planning/milestones/v0.1.0-ROADMAP.md`](milestones/v0.1.0-ROADMAP.md)

---

## Current Position

```text
Milestone: v0.1.0 Pre-Fase 2 Foundation — ARCHIVED 2026-06-10
Status: 35/35 REQs shipped. Repo OCA-ready.
Resume: /gsd:new-milestone  (iniciar Fase 2 — l10n_py_edi MVP)

Módulos en main:
  l10n_py_base    18.0.1.1.0  — 23 tests verdes
  l10n_py_account 18.0.1.0.0  — 74 tests verdes
  Total: 97 tests verdes
```

---

## Accumulated Context

Las decisiones del milestone v0.1.0 están archivadas en:
[`.planning/milestones/v0.1.0-ROADMAP.md`](milestones/v0.1.0-ROADMAP.md) §Milestone Summary → Key Decisions

### Decisions permanentes (aplican a todos los milestones)

- **Subagent override global**: cualquier task de código → subagent. Trigger de escalación: 1 test que falla, 1 traceback no entendido al primer leído, 1 "esto debería funcionar pero...", >2 lecturas seguidas para entender un bug. (Formalizado en CLAUDE.md del repo.)
- **Manual releases**: semantic-release rechazado para proyectos early-stage con historial imperfecto. Proceso: CHANGELOG → PR → tag → `gh release create --notes-file`. (REL-06, CONTRIBUTING.md §Release process.)
- **No reescribir git history** para remover secrets: rotar + documentar en `.gitleaksignore`. Política activa.
- **`--keep-source-digest`** en `.pre-commit-config.yaml` para `oca-gen-addon-readme`: digest drift OS-dependiente (Windows backslash vs Linux). Siempre usar el flag.
- **Ley 7593/2025** (no 6534/2020) es la ley general de protección de datos de Paraguay. ANPDP/MITIC es la autoridad supervisora.

---

## Session Continuity

### How to resume

```
/gsd:new-milestone
```

Lee PROJECT.md (§Next Milestone Goals) → inicia milestone v0.2.0 Fase 2 l10n_py_edi MVP con discuss-phase + plan-phase.

---

## Subagent Defaults

| Fase siguiente     | Subagent primario                                   | Skills sugeridas                                  |
| ------------------ | --------------------------------------------------- | ------------------------------------------------- |
| Fase 2 (EDI / XML) | `python-pro` + `security-auditor` (opus) para XAdES | `superpowers:writing-plans`, `ecc:python-testing` |
| Antes de cada PR   | `voltagent-qa-sec:code-reviewer`                    | `superpowers:verification-before-completion`      |

---

_STATE initialized: 2026-05-26 — initial GSD bootstrap of milestone Pre-Fase 2._
_STATE updated: 2026-06-10 — milestone v0.1.0 archived. Next: Fase 2 l10n_py_edi MVP._
