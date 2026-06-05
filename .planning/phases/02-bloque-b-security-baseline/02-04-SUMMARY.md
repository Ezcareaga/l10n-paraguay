---
phase: 02-bloque-b-security-baseline
plan: 04
subsystem: docs / security-baseline
tags: [security, baseline, ccfe, fernet, audit-logs, backup, sec-06]
dependency_graph:
  requires: [02-02]
  provides:
    - docs/60_SECURITY_BASELINE.md
    - scripts/restore-smoke.sh
    - README.md (security badge + Seguridad section)
  affects:
    - docs/61_COMPLIANCE_LEY_7593.md (cross-refs from Plan 02-05 resolve post-merge)
    - l10n_py_edi Phase 2 EDI (CCFE blueprint consumer)
tech_stack:
  added: []
  patterns:
    [
      operational-blueprint,
      ccfe-fernet-multifernet,
      systemd-creds,
      ir-config-parameter,
      oca-auditlog,
      pg_dump-b2-restore-cycle,
    ]
key_files:
  created:
    - docs/60_SECURITY_BASELINE.md
    - scripts/restore-smoke.sh
  modified:
    - README.md
    - .codespellrc
decisions:
  - "D-09 enforced: cada comando lleva el marker `> Note: validar en Pre-Fase 3 cuando exista deploy real` (14 ocurrencias verificadas)"
  - "D-10 enforced: CCFE encryption blueprint Fernet + MultiFernet + systemd-creds + ir.config_parameter — pseudo-código marcado `NO ejecutar en Phase 2`; código real vive en l10n_py_edi"
  - "D-11 enforced: audit log table cubre res.partner (vat, l10n_py_dv, l10n_latam_identification_type_id), res.company (vat), l10n_py.timbrado (name, state, expiry_date), l10n_latam.document.type (code, internal_type), account.move (post-Fase 2 EDI); retention 7 años archivado + 1 año online (Ley 125/91 PY base)"
  - "D-12 enforced: backup = pg_dump local + Backblaze B2 offsite + monthly restore test referenciando scripts/restore-smoke.sh"
  - "README touch minimal: 1 badge + 1 sección 'Seguridad' de 2 líneas — full refactor diferido a Phase 3 DOC-01"
  - "Rule 3 auto-fix: `anual` y `alternativos` agregados a .codespellrc ignore-words-list — Spanish false positives bloqueando pre-commit (misma política aplicada por Plan 02-05 para la sigla de Unión Europea + `anual`)"
metrics:
  duration: "interrupted (executor stalled post-Task-3 commit; SUMMARY completed inline by orchestrator 2026-06-04)"
  completed: 2026-06-04
  tasks: 3
  files_created: 2
  files_modified: 2
  commits: 3
requirements:
  - SEC-06
status: complete
---

# Phase 02 Plan 04: Bloque B Security Baseline — SEC-06 Security Baseline Doc + Restore Smoke Stub Summary

Documento operacional `docs/60_SECURITY_BASELINE.md` (555 líneas) que cierra SEC-06 con los 6 ejes de baseline de seguridad + blueprint CCFE Fernet consumible por Fase 2 EDI, más el stub ejecutable `scripts/restore-smoke.sh` y un toque mínimo a README (badge security + sección Seguridad de 2 líneas).

## One-liner

Baseline doc de 6 ejes (auth/2FA, password policy, OCA auditlog, pg_dump+B2, CCFE Fernet blueprint, red security) marcado "validar en Pre-Fase 3", stub restore-smoke.sh + README badge — todo dentro del scope del plan, sin tocar `l10n_py_edi`.

## Tasks Completed

| Task ID  | Description                                                       | Files                                                           | Commit    |
| -------- | ----------------------------------------------------------------- | --------------------------------------------------------------- | --------- |
| 02-04-01 | Author docs/60_SECURITY_BASELINE.md (6 ejes + CCFE blueprint)     | `docs/60_SECURITY_BASELINE.md` (new), `.codespellrc` (modified) | `ed01bac` |
| 02-04-02 | Add scripts/restore-smoke.sh stub for monthly restore test (D-12) | `scripts/restore-smoke.sh` (new)                                | `b2cc9cc` |
| 02-04-03 | Add security workflow badge + "Seguridad" section to README       | `README.md` (modified)                                          | `8286cd0` |

## Output Spec

### File created — `docs/60_SECURITY_BASELINE.md` (555 lines)

**H2 sections (8 total: 1 scope intro + 6 ejes mandatorios + 1 cross-refs):**

1. `## Alcance del documento` — qué es el doc, qué NO es (no es deploy guide, no es código ejecutable), audiencia (Pre-Fase 3 operator + autor del helper CCFE de Fase 2 EDI).
2. `## 1. Autenticación y 2FA` — `auth_totp` OCA, password policy 12+ chars + complexity, session timeout.
3. `## 2. Política de contraseñas` — `password_security` OCA o `auth_password_policy`, MFA mandatory para users con `groups_id` de admin.
4. `## 3. Audit logs (OCA auditlog)` — tabla D-11 con modelos auditados (res.partner, res.company, l10n_py.timbrado, l10n_latam.document.type, account.move post-Fase 2), retention policy 7 años archivado + 1 año online (Ley 125/91 PY base).
5. `## 4. Backup strategy` — D-12: pg_dump local nightly + Backblaze B2 offsite encryption-at-rest + monthly restore test referenciando `scripts/restore-smoke.sh`.
6. `## 5. CCFE encryption blueprint (D-10)` — Fernet + MultiFernet blueprint completo: envelope schema, encrypt/decrypt/rotate pseudo-código, systemd-creds para master key, `ir.config_parameter` para `wrap_key_id`. Todo el code-block marcado `# NO ejecutar en Phase 2` — el código real vive en `l10n_py_edi` (Fase 2 EDI).
7. `## 6. Seguridad de red` — ufw firewall rules, fail2ban para SSH, Caddy reverse proxy con TLS 1.3.
8. `## Cross-references` — links bidireccionales a `docs/61_COMPLIANCE_LEY_7593.md` (parallel artifact de Plan 02-05) y `scripts/restore-smoke.sh`.

### File created — `scripts/restore-smoke.sh` (45 lines)

Stub ejecutable: shebang `#!/usr/bin/env bash` + `set -euo pipefail` + `SCRIPT_DIR/REPO_ROOT` boilerplate (matching `scripts/setup_references.sh` pattern) + comentarios en español documentando los 5 pasos reales (xz -d → docker run postgres:16 → psql restore → SELECT count → cleanup) deferidos a Pre-Fase 3 + `exit 0` para no romper pre-commit/CI.

### File modified — `README.md` (+6 lines / -0)

- 1 nuevo badge `Security` (link a `workflows/security.yml/badge.svg?branch=main`) insertado entre `pre-commit` y `codecov`, preservando el grouping visual (CI-workflows-first → external-service → static-info).
- 1 nueva sección H2 `## Seguridad` justo antes de `## Licencia` con 2 líneas: link a `SECURITY.md` + nota sobre el workflow de seguridad en cada PR.
- Sin refactor de otras secciones (el refactor real del README es Phase 3 DOC-01).

### File modified — `.codespellrc` (Rule 3 auto-fix)

Agregados `anual` (palabra española correcta para "annual") y `alternativos` (palabra española correcta) a `ignore-words-list`. Bundled en el commit `ed01bac` del Task 1 (codespell hook los flagó al committear `docs/60` por contener prosa española). Política del repo (documentada en el header del `.codespellrc`) es explícita: agregar tokens cuando codespell los flagea. Mismo patrón aplicado por Plan 02-05 en paralelo (la sigla de Unión Europea + `anual`) — colisión esperada en el merge, lista de tokens unificable.

## Acceptance Criteria Verification

| Criterion                                                                                                 | Result                                                              |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| `docs/60_SECURITY_BASELINE.md` exists                                                                     | ✅ True (555 lines, ≥ 200 mandatory)                                |
| 6 H2 ejes en orden plan (Auth/2FA, password, audit logs, backup, CCFE, red)                               | ✅ All 6 present in plan-mandated order                             |
| `## 5. CCFE encryption blueprint` heading present (must_have artifact `contains`)                         | ✅ True                                                             |
| CCFE blueprint includes Fernet + MultiFernet + systemd-creds + ir.config_parameter                        | ✅ Fernet=13, MultiFernet=5, systemd-creds=9, ir.config_parameter=5 |
| Audit log models D-11: res.partner, res.company, l10n_py.timbrado, l10n_latam.document.type, account.move | ✅ all 5 present                                                    |
| Retention 7 años archivado + 1 año online (Ley 125/91)                                                    | ✅ True (Ley 125/91 cited 2x)                                       |
| Backup D-12: pg_dump + Backblaze B2 + monthly restore test                                                | ✅ pg_dump=3, B2/Backblaze=8                                        |
| D-09 marker count: `validar en Pre-Fase 3 cuando exista deploy real`                                      | ✅ 14 ocurrencias (todos los code-blocks)                           |
| "NO ejecutar en Phase 2" marker en CCFE                                                                   | ✅ 2 ocurrencias                                                    |
| `scripts/restore-smoke.sh` exists with shebang + `set -euo pipefail` + exit 0                             | ✅ True (45 lines)                                                  |
| Must_have artifact `scripts/restore-smoke.sh` contains "STUB"                                             | ✅ True                                                             |
| README has security badge (URL contains `security.yml/badge.svg`)                                         | ✅ True (between pre-commit and codecov)                            |
| README has new H2 "Seguridad" section (2 líneas, before "Licencia")                                       | ✅ True (+5 lines incluyendo header)                                |
| README NO full refactor (other sections unchanged)                                                        | ✅ True (+6 / -0, diff localizado)                                  |
| Cross-ref `docs/60 §3 Audit logs` → `docs/61 §3 ARCO`                                                     | ✅ 4 mentions of `61_COMPLIANCE_LEY_7593`                           |
| Cross-ref `docs/60 §4 Backup strategy` → `scripts/restore-smoke.sh`                                       | ✅ 4 mentions of `restore-smoke`                                    |
| Conventional Commits format en los 3 commits                                                              | ✅ `docs(sec-06):`, `feat(sec-06):`, `docs(sec-06):`                |
| Pre-commit pasa todos los hooks (codespell, prettier, yamllint, markdownlint)                             | ✅ All passed at commit time (`ed01bac`, `b2cc9cc`, `8286cd0`)      |

## Deviations from Plan

### Execution-level deviation (orchestrator-initiated)

**Executor agent stalled after Task 3 commit; SUMMARY completed manually.**

- **Found during:** post-Task-3 wait. El background agent `a74c4c4072ea33953` quedó vivo ~17h después del commit `8286cd0` sin escribir `02-04-SUMMARY.md` ni emitir signal de completion. HEAD del worktree estuvo congelado en `8286cd0`, working tree clean.
- **Recovery path:** Opción 2 del workflow `<failure_handling>` (`kill and switch to inline execution`). Orchestrator killed el agent via `TaskStop` y escribió este SUMMARY a partir de los 3 commits ya validados + must_haves del plan + evidencia recopilada por inspección directa de archivos (no transcript replay).
- **No impacto en code:** los 3 task commits (`ed01bac`, `b2cc9cc`, `8286cd0`) ya existían antes del stall y fueron verificados en disk (file content, line counts, marker counts) antes de escribir este SUMMARY. Cero re-ejecución, cero re-commits de tasks.
- **Trade-off:** SUMMARY no incluye el "Threat Flags" cross-check que el executor habría hecho contra el threat model — se cubre en el verify_phase_goal step downstream del orchestrator (gsd-verifier reads VERIFICATION.md against requirements).

### Plan-level deviations

**1. [Rule 3 — Blocking] codespell rejected `anual` y `alternativos` como typos**

- **Found during:** Task 02-04-01 pre-commit run (codespell flagged en docs/60).
- **Fix:** Agregados `anual,alternativos` al `ignore-words-list` de `.codespellrc`. Bundled en el mismo commit del Task 1 (`ed01bac`) — mismo patrón documentado por Plan 02-05.
- **Files modified:** `.codespellrc` (+1 charset, -1 línea reemplazada).
- **Why Rule 3:** Política del repo (en header del `.codespellrc`) es explícita: agregar tokens cuando codespell los flagea — exactamente este caso.

**2. Conventional Commits scope: `docs(sec-06):` en vez de `docs(sec):`**

- Plan sugería `docs(sec): ...` (scope genérico). Executor usó `docs(sec-06):` (scope con REQ ID). Es más específico y match el patrón usado por Plans 02-01 (`docs(sec-01):`), 02-02 (`feat(sec-03):`), 02-03 (`docs(sec-04):`) — consistencia mejorada, no scope creep.

**3. Doc extendió de ≥200 a 555 líneas**

- Plan exigía min_lines: 200. Doc final tiene 555 (2.7× el mínimo). La extensión está en el blueprint CCFE (§5) — D-10 exigía "tan claro que cuando Fase 2 EDI lo lea, el código se escribe siguiendo el patrón", y eso requiere envelope schema completo + encrypt/decrypt/rotate pseudo-código + rotation procedure paso a paso. Sin scope creep — toda la prosa adicional está justificada por D-10.

## Known Stubs

1. **`scripts/restore-smoke.sh`** — stub explícitamente declarado en el plan (Task 02-04-02). Implementación completa de los 5 pasos reales (xz → docker postgres → psql restore → count → cleanup) deferida a Pre-Fase 3 cuando exista deploy real y backup backend (Backblaze B2 bucket). El stub `exit 0` no rompe pre-commit/CI.

2. **CCFE encryption code (docs/60 §5)** — pseudo-código blueprint, NO código ejecutable. Implementación real vive en `l10n_py_edi` (Fase 2 EDI). Marcado `# NO ejecutar en Phase 2` en cada code-block.

3. **README full refactor** — sólo 1 badge + 1 sección agregados. Refactor completo del README (descriptor del proyecto, install instructions, tabla de módulos, etc.) diferido a Phase 3 DOC-01.

## Threat Flags

Ninguno nuevo. Este plan es docs-only — no introduce nueva surface técnica:

- T-SEC-06-blueprint: el blueprint CCFE en docs/60 §5 está marcado como pseudo-código + `NO ejecutar en Phase 2`. El threat de "alguien copy-pastea el blueprint a prod" se mitiga con el marker explícito + el hecho de que la implementación real vive en `l10n_py_edi`.
- T-SEC-06-stub-exec: `scripts/restore-smoke.sh` `exit 0` es deliberado — el threat de "alguien corre el script en prod creyendo que hace algo" se mitiga con el header explícito "STUB" + comentario "Implementación completa: Pre-Fase 3".
- T-SEC-06-readme: el badge security en README es link-only a workflow runs — no expone secrets ni configuración interna.

## Self-Check

- [x] `docs/60_SECURITY_BASELINE.md` exists en worktree filesystem (555 líneas, verified via `wc -l`)
- [x] `scripts/restore-smoke.sh` exists con shebang + set -euo + exit 0 (45 líneas, verified via `head`)
- [x] `README.md` muestra +6 / -0 con badge security + sección Seguridad (verified via `git show 8286cd0`)
- [x] Commit `ed01bac` exists en `git log` (Task 1)
- [x] Commit `b2cc9cc` exists en `git log` (Task 2)
- [x] Commit `8286cd0` exists en `git log` (Task 3)
- [x] HEAD on `worktree-agent-a74c4c4072ea33953` (worktree-agent-\* namespace, never on protected ref)
- [x] No modifications to `.planning/STATE.md` or `.planning/ROADMAP.md` (orchestrator owns those)
- [x] No accidental deletions: `git diff --diff-filter=D 07fcd0d..HEAD` empty (verified by diff stat: 4 files changed, +607/-1; the -1 is the codespell line replacement, not a deletion)
- [x] All must_haves goals + truths + artifacts verified against actual file content (not transcript claims)

## Self-Check: PASSED

## Wave 4 parallel artifact note

Plan 02-04 ejecutó en paralelo con Plan 02-05 (Wave 4, no file overlap en plan declarations). Este worktree contiene `docs/60_SECURITY_BASELINE.md` + `scripts/restore-smoke.sh` + `README.md` + ajuste a `.codespellrc`. El archivo `docs/61_COMPLIANCE_LEY_7593.md` (de Plan 02-05) no existe en este worktree pero estará presente tras el merge del worktree de Plan 02-05 al feat branch. Los 4 cross-refs a `61_COMPLIANCE_LEY_7593` se resolverán post-merge.

**Codespell collision risk:** ambos worktrees modificaron `.codespellrc` independientemente:

- 02-04 agregó: `anual`, `alternativos`
- 02-05 agregó: la sigla de Unión Europea + `anual`

Hay overlap en `anual` (idéntico token, no causa add/add conflict si el diff three-way es estable). Post-merge esperado: lista final unificada que incluye los 3 tokens nuevos (`alternativos`, `anual`, sigla-UE) más los previos. Si git reporta conflict en `.codespellrc`, resolver manualmente uniendo las dos listas con `anual` deduplicado.
