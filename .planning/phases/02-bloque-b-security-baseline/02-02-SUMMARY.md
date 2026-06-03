---
phase: 02-bloque-b-security-baseline
plan: 02
subsystem: ci-security
tags: [ci, security, gitleaks, bandit, dependency-review, sarif]
requires:
  - 02-01 (LICENSE + SECURITY.md merged in Wave 1)
provides:
  - .github/workflows/security.yml (3 parallel jobs: gitleaks, bandit, dependency-review)
  - SARIF results visible in GitHub Security tab under categories "gitleaks" and "bandit"
  - Required-status-check names (for Plan 03 branch-protection update): gitleaks, bandit, dependency-review
affects:
  - SEC-03 (closed — 2026-06-02)
tech-stack:
  added:
    - gitleaks/gitleaks-action@v3
    - actions/dependency-review-action@v4
    - github/codeql-action/upload-sarif@v3
    - bandit[sarif]==1.9.4
  patterns:
    - parallel-jobs CI workflow with conservative triggers (PR + push to main, no schedule, no workflow_dispatch)
    - SARIF distinct-category upload to prevent Security tab overwrite (mandatory since GH July 2025)
    - bandit fail-gate scoped to HIGH severity + HIGH confidence (`-lll -iii`) per D-02
    - dependency-review restricted to pull_request via `if:` (action does not support push triggers)
key-files:
  created:
    - .github/workflows/security.yml
  modified: []
decisions:
  - "D-01 enforced: 1 workflow with 3 parallel jobs (gitleaks/bandit/dependency-review)"
  - "D-02 enforced: bandit -lll -iii (HIGH severity + HIGH confidence only)"
  - "D-03 enforced: SARIF upload via github/codeql-action/upload-sarif@v3 with distinct category per job"
  - "D-04 enforced: no workflow_dispatch, no schedule:; PR diff + push to main only"
  - "A-02 enforced: gitleaks/gitleaks-action@v3 (never @v2 — Node 20 EOL ~Sep 2026)"
  - "Risk 3 mitigation: actions/dependency-review-action@v4 (v5 requires runner v2.327.1+)"
  - "runs-on: ubuntu-22.04 in all 3 jobs (matches Phase 1 standard; never ubuntu-latest)"
metrics:
  duration: "~10 min (Task 02-02-01 + Task 02-02-02 manual checkpoint)"
  completed: 2026-06-02
  tasks_completed: 2
  tasks_total: 2
  files_created: 1
  files_modified: 0
status: complete
---

# Phase 2 Plan 02-02: CI Security Workflow — Summary

**One-liner:** Security workflow `security.yml` con 3 jobs paralelos (gitleaks @v3, bandit 1.9.4 HIGH-only, dependency-review @v4) que publica SARIF al Security tab con categorías distintas; Dependency Graph + Dependabot alerts ya estaban habilitados en GitHub Settings (checkpoint aprobado).

## Status

**Complete.**

Task 02-02-01 ejecutado y commiteado. Task 02-02-02 (manual UI step en GitHub Settings) verificado por el owner del repo (`@Ezcareaga`) el 2026-06-02 — Dependency Graph + Dependabot alerts ya estaban habilitados desde antes (resume-signal: "approved — already enabled").

La verificación end-to-end del job `dependency-review` (que la action no falla con "Dependency graph not enabled") sucede en el primer PR run después del push de `feat/sec-03-security-workflow` a GitHub — queda capturada como UAT item del Wave 2, no bloqueante del cierre del plan.

## Completed Tasks

| Task     | Name                                             | Commit    | Files                                  | Status                                                       |
| -------- | ------------------------------------------------ | --------- | -------------------------------------- | ------------------------------------------------------------ |
| 02-02-01 | Author `.github/workflows/security.yml` (3 jobs) | `e393fd5` | `.github/workflows/security.yml` (new) | Done                                                         |
| 02-02-02 | Enable Dependency Graph + Dependabot alerts (UI) | n/a       | (none — GitHub Settings)               | Approved 2026-06-02 (toggles already enabled per repo admin) |

## What Was Built

`.github/workflows/security.yml` — workflow GitHub Actions con 3 jobs paralelos, todos disparados por `pull_request: branches:[main]` + `push: branches:[main]` (sin `workflow_dispatch`, sin `schedule:` — D-04).

### Job `gitleaks`

- `runs-on: ubuntu-22.04`, `permissions: contents:read + security-events:write`.
- `actions/checkout@v4` con `fetch-depth: 0` (necesario para scan de history).
- `gitleaks/gitleaks-action@v3` (A-02 — supersede mention de @v2) con env:
  - `GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}`
  - `GITLEAKS_ENABLE_COMMENTS: "false"` (D-01 — evita ruido en PR comments).
  - `GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false"` (usamos `upload-sarif` explícito).
- `github/codeql-action/upload-sarif@v3` con `if: always()`, `sarif_file: results.sarif`, `category: gitleaks` (D-03).

### Job `bandit`

- `runs-on: ubuntu-22.04`, `permissions: contents:read + security-events:write`.
- `actions/setup-python@v5` con `python-version: "3.11"` + `cache: "pip"`.
- `pip install "bandit[sarif]==1.9.4"`.
- Run scan: `bandit -r addons/ -lll -iii -f sarif -o bandit.sarif` con `continue-on-error: true` (D-02 — HIGH severity + HIGH confidence only).
- `upload-sarif@v3` con `if: always()`, `category: bandit` (distinta de gitleaks — D-03).
- Final fail step: re-corre `bandit -r addons/ -lll -iii` sin `continue-on-error` para gating del PR.

### Job `dependency-review`

- `runs-on: ubuntu-22.04`, `permissions: contents:read`.
- `if: github.event_name == 'pull_request'` (action no soporta push — RESEARCH §"dependency-review-action solo corre en pull_request").
- `actions/dependency-review-action@v4` (NO v5 — RESEARCH §Risk 3, v5 requiere runner v2.327.1+) con `fail-on-severity: high`.

## Verification

### Acceptance Criteria Results (PowerShell)

| Check                                           | Result                 |
| ----------------------------------------------- | ---------------------- | ---------------------- |
| `Test-Path .github/workflows/security.yml`      | True                   |
| `name: security` count                          | 1 (expected 1)         |
| `gitleaks/gitleaks-action@v3` count             | 1 (expected ≥1)        |
| `gitleaks/gitleaks-action@v2` count             | 0 (expected 0)         |
| `actions/dependency-review-action@v4` count     | 1 (expected ≥1)        |
| `github/codeql-action/upload-sarif@v3` count    | 2 (expected ≥2)        |
| `bandit[sarif]==1.9.4` count                    | 1 (expected ≥1)        |
| `bandit -r addons/ -lll -iii` count             | 2 (expected ≥1)        |
| `category: (gitleaks                            | bandit)` total matches | 2 (expected 2)         |
| `if: github.event_name == 'pull_request'` count | 1 (expected ≥1)        |
| `GITLEAKS_ENABLE_COMMENTS: "false"` count       | 1 (expected 1)         |
| `runs-on: ubuntu-22.04` count                   | 3 (expected 3)         |
| `(workflow_dispatch                             | schedule:)` present    | False (expected False) |

All 13 acceptance criteria for Task 02-02-01 passed.

### Pre-commit

`pre-commit run --files .github/workflows/security.yml` → all hooks Passed/Skipped (codespell, yamllint, prettier, trim trailing whitespace, fix end of files, check for case conflicts, check for merge conflicts, check for broken symlinks, mixed line ending).

### Plan automated verify

```powershell
$f = '.github/workflows/security.yml'; $ok = (Test-Path $f) -and ((Select-String -Path $f -Pattern 'gitleaks/gitleaks-action@v3' -Quiet) -eq $true) -and (((Select-String -Path $f -Pattern 'gitleaks/gitleaks-action@v2' | Measure-Object).Count) -eq 0) -and ((Select-String -Path $f -Pattern 'actions/dependency-review-action@v4' -Quiet) -eq $true) -and (((Select-String -Path $f -Pattern 'category:\s*(gitleaks|bandit)' -AllMatches).Matches.Count) -eq 2)
```

Result: `OK`.

## Checkpoint 02-02-02 — Approved 2026-06-02

Task 02-02-02 (manual UI step en GitHub Settings) verificado por el owner del repo `@Ezcareaga`. Resume-signal: **"Approved — already enabled"** — las toggles ya estaban habilitadas desde antes.

Estado esperado en GitHub Settings → Security → Code security and analysis:

- **Dependency graph** → Enabled
- **Dependabot alerts** → Enabled
- **Dependabot security updates** → Enabled (opcional, recomendado)

### UAT item para el Wave 2 PR

Cuando se abra el PR de `feat/sec-03-security-workflow` a `main`:

- Confirmar que el job `dependency-review` reporta `success` (no falla con "Dependency graph is not enabled").
- Confirmar que SARIF de `gitleaks` y `bandit` aparece en GitHub Security → Code scanning con categorías distintas.
- Confirmar que los 3 jobs (`gitleaks`, `bandit`, `dependency-review`) corren y figuran como checks separados en el PR.

Esto NO bloquea el cierre del plan — es smoke verification del primer run real del workflow, que Plan 03 va a usar como insumo para sumar required-status-checks a branch protection.

## Deviations from Plan

None. Task 02-02-01 ejecutado exactamente como el plan especifica (canonical workflow body de RESEARCH §"Action Pins & SARIF Wiring" + PATTERNS §".github/workflows/security.yml" Full canonical structure). Single commit, Conventional Commits message del plan.

## Threat Flags

Ninguna nueva surface de seguridad introducida fuera del threat model. El workflow `security.yml` ES el control para `T-SEC-03-noscan`, `T-SEC-03-supply`, `T-SEC-03-sarif`, `T-SEC-03-prcomment` (todos mitigados según el threat model del plan).

## Known Stubs

Ninguno. El workflow está completamente cableado — no hay placeholders ni datos hardcoded en mock.

## Required-Status-Check Names (for Plan 03)

Tras el primer run verde en main, Plan 03 debe sumar estos 3 nombres a branch protection de `main`:

- `gitleaks`
- `bandit`
- `dependency-review`

(Estos son los valores de `name:` a nivel de job, NO el `name:` del workflow.)

## Self-Check: PASSED

- `.github/workflows/security.yml` → FOUND
- commit `e393fd5` → FOUND in `git log --all`

Validado con:

```bash
[ -f ".github/workflows/security.yml" ] && echo "FOUND" || echo "MISSING"
git log --oneline --all | grep -q "e393fd5" && echo "FOUND" || echo "MISSING"
```
