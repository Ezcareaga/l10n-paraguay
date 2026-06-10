---
phase: 03
slug: bloque-c-documentaci-n-operacional
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-05
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property               | Value                                                                                                            |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Framework**          | grep-based doc validation + Odoo built-in test runner (regression guard, 97 tests)                               |
| **Config file**        | `.github/workflows/test.yml` (env `ODOO_TEST_TAGS: "l10n_py"`)                                                   |
| **Quick run command**  | `grep -c "TODO" README.md; grep "\[0.1.0\]" CHANGELOG.md; grep "INSERT CONTACT" CODE_OF_CONDUCT.md \|\| echo OK` |
| **Full suite command** | `pre-commit run --all-files` + grep audit across all new doc files                                               |
| **Estimated runtime**  | ~30 seconds                                                                                                      |

---

## Sampling Rate

- **After every task commit:** Run quick grep checks on the files touched by the task
- **After every plan wave:** Full grep audit across all new files of the wave + `pre-commit run --all-files`
- **Before `/gsd:verify-work`:** Phase gate green — `ls docs/70_ARCHITECTURE.md docs/71_DEPLOYMENT.md docs/72_RUNBOOK.md docs/adr/000*.md` returns 8 files; `grep -c "TODO" README.md` returns 0; `pre-commit run --all-files` clean
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type     | Automated Command                                             | File Exists         | Status     |
| ------- | ---- | ---- | ----------- | ---------- | --------------- | ------------- | ------------------------------------------------------------- | ------------------- | ---------- |
| TBD     | —    | —    | DOC-01      | —          | N/A             | grep          | `grep -c "TODO" README.md` (expect 0)                         | ✅ README.md exists | ⬜ pending |
| TBD     | —    | —    | DOC-02      | —          | N/A             | grep          | `grep "\[0.1.0\]" CHANGELOG.md`                               | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-03      | —          | N/A             | grep          | grep 6 ejes en CONTRIBUTING.md                                | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-04      | —          | N/A             | grep          | `grep "INSERT CONTACT" CODE_OF_CONDUCT.md \|\| echo OK`       | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-05      | —          | N/A             | manual render | Mermaid blocks render in GitHub PR preview                    | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-06      | —          | N/A             | grep          | `grep -c "Caddy\|backup\|health check" docs/71_DEPLOYMENT.md` | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-07      | —          | N/A             | grep          | `grep -c "^### Incidente" docs/72_RUNBOOK.md` (expect ≥10)    | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-08      | —          | N/A             | ls            | `ls docs/adr/000*.md \| wc -l` (expect 5)                     | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-09      | —          | N/A             | grep          | `grep -c "ADR" CONTRIBUTING.md` (regla mismo PR presente)     | ❌ W0               | ⬜ pending |
| TBD     | —    | —    | DOC-10      | —          | N/A             | manual        | GitHub issue smoke test creado; async UAT                     | ❌ W4               | ⬜ pending |

_Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky_
_Task IDs to be filled by gsd-planner._

---

## Wave 0 Requirements

All 10 target files are new (none exist yet). No test framework changes needed — validation is grep-based, not test-runner-based.

- [ ] `CHANGELOG.md` — covers DOC-02
- [ ] `CONTRIBUTING.md` — covers DOC-03, DOC-09
- [ ] `CODE_OF_CONDUCT.md` — covers DOC-04
- [ ] `docs/70_ARCHITECTURE.md` — covers DOC-05
- [ ] `docs/71_DEPLOYMENT.md` — covers DOC-06
- [ ] `docs/72_RUNBOOK.md` — covers DOC-07
- [ ] `docs/adr/README.md` + `docs/adr/0001-0005-*.md` — covers DOC-08

---

## Manual-Only Verifications

| Behavior                           | Requirement | Why Manual                                                                              | Test Instructions                                                                                     |
| ---------------------------------- | ----------- | --------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Mermaid C4 blocks render on GitHub | DOC-05      | C4 syntax is experimental in GitHub's Mermaid — only a live PR preview proves rendering | Abrir el PR de docs/70 en github.com y verificar que los bloques `C4Context`/`C4Container` renderizan |
| Smoke test dev externo             | DOC-10      | Requiere humano externo siguiendo CONTRIBUTING.md sin contexto                          | Crear GitHub issue con checklist; dev externo reporta resultado (async UAT)                           |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
