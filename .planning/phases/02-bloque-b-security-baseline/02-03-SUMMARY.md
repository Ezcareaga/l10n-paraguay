---
phase: 02-bloque-b-security-baseline
plan: 03
subsystem: security-baseline
tags: [security, gitleaks, bandit, sast, branch-protection, sec-04, sec-05]
requires:
  - 02-02 (security.yml workflow merged in Wave 2, jobs gitleaks/bandit/dependency-review confirmed)
provides:
  - gitleaks full-history baseline (0 findings — no .gitleaksignore needed)
  - Bandit HIGH gate baseline (0 HIGH/MEDIUM/LOW findings in addons/)
  - Checkpoint handoff for branch protection update on main (task 02-03-03 — blocking-human)
affects:
  - SEC-04 (closed — 2026-06-03; 0 active secrets in full history)
  - SEC-05 (closed — 2026-06-03; 0 HIGH Bandit findings in addons/)
  - SEC-03-protection (pending — task 02-03-03 awaits resume-signal from repo owner)
tech-stack:
  added:
    - bandit==1.9.4 (local-only — already pinned in security.yml CI workflow)
    - gitleaks v8.30.1 (local-only — downloaded native Windows binary, SHA256 verified)
  patterns:
    - rotate-not-rewrite policy enforced (CONTEXT.md D-04 + REQUIREMENTS.md Risks): full-history scan is the trigger, rotation is the action; no .gitleaksignore generated because no findings to allowlist
    - Bandit fail-gate scoped to HIGH severity + HIGH confidence (`-lll -iii`) matches CI security.yml job exactly
    - Full audit pass (`-r addons/` with default thresholds) covers LOW + MEDIUM + HIGH at all confidence levels — used to confirm BUGS_BACKLOG.md needs no MEDIUM/LOW entries
key-files:
  created: []
  modified: []
decisions:
  - "0 gitleaks findings on full-history scan (106 commits, 3.27 MB scanned in 1.48s) — no .gitleaksignore created (policy: file exists only if there is content to allowlist)"
  - "0 Bandit findings at every severity (HIGH/MEDIUM/LOW) and confidence level — no BUGS_BACKLOG.md section appended (policy: append only when there are findings to record)"
  - "Docker Desktop daemon unavailable in this session; fell back to gitleaks native Windows binary v8.30.1 (RESEARCH.md §gitleaks History Strategy lists both invocations as equivalent)"
  - "SHA256 of gitleaks_8.30.1_windows_x64.zip verified against canonical checksums.txt before extraction (d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e)"
  - "No history rewrite executed (`git reflog --all | Select-String 'filter-repo|filter-branch|BFG' -Quiet` returned False) — D-04 policy maintained"
  - "Task 02-03-03 deliberately NOT executed by the agent — `gh api -X PUT repos/.../required_status_checks/contexts` requires admin token the executor does not have; checkpoint returned for repo owner"
metrics:
  duration: "~20 min (env setup + 2 scans + audit + summary)"
  completed: 2026-06-03
  tasks_completed: 2
  tasks_total: 3
  files_created: 0
  files_modified: 0
  commits: 0
status: partial — task 03 pending human verification (branch protection update on main)
---

# Phase 2 Plan 02-03: gitleaks + Bandit triage + branch protection — Summary

**One-liner:** Auditoría local con gitleaks v8.30.1 (full history, 106 commits) y Bandit 1.9.4 (`addons/`) — ambas reportan **0 findings** a todos los niveles; el repo entra a Wave 3 con baseline limpio. La tarea 02-03-03 (branch protection update en `main`) queda pendiente como checkpoint blocking-human para el repo owner.

## Status

**Partial — 2 of 3 tasks complete.**

- Task 02-03-01 (gitleaks full-history scan): **DONE — 0 findings**
- Task 02-03-02 (Bandit HIGH gate + MEDIUM/LOW audit): **DONE — 0 findings at every level**
- Task 02-03-03 (branch protection update on `main`): **CHECKPOINT — awaits resume-signal from repo owner**

No file changes were produced by tasks 01 and 02 (both auditorías limpias). This SUMMARY itself is the only commit-worthy artifact of the plan execution so far. Tasks 01 and 02 closed SEC-04 and SEC-05; SEC-03-protection (branch protection arm) closes only when task 03 is verified.

## Completed Tasks

| Task     | Name                                                                                               | Commit | Files                                            | Status                                         |
| -------- | -------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------ | ---------------------------------------------- |
| 02-03-01 | gitleaks full-history scan + rotate any live tokens + write .gitleaksignore if needed              | n/a    | (none — 0 findings → no .gitleaksignore created) | Done                                           |
| 02-03-02 | Bandit `-lll -iii` HIGH gate on addons/ + document MEDIUM/LOW in BUGS_BACKLOG.md if any            | n/a    | (none — 0 findings at any severity)              | Done                                           |
| 02-03-03 | Add `gitleaks`, `bandit`, `dependency-review` to required status checks for branch protection main | n/a    | (none — GitHub Settings UI / `gh api`)           | Checkpoint pending (blocking-human, see below) |

## Task 02-03-01 — gitleaks full-history scan

### What was done

1. **Tool selection.** Docker daemon (`docker info` against `desktop-linux` and `default` contexts) was unavailable in this session. Per RESEARCH.md §"Cómo ejecutar gitleaks localmente en Windows" — which lists both Docker invocation and native Windows binary as equivalent — fell back to the native binary path.
2. **Download + integrity verification.**
   - URL: `https://github.com/gitleaks/gitleaks/releases/download/v8.30.1/gitleaks_8.30.1_windows_x64.zip` (latest stable; the `@v3` GitHub Action wraps this same upstream).
   - Expected SHA256 (from canonical `gitleaks_8.30.1_checksums.txt`): `d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e`.
   - Computed SHA256 of the local zip: identical match — verified before extraction.
3. **Scan invocation** (from the main-repo `.git` directory, where full history is materialized; the worktree's `.git` file points to the same git-dir, so the scan covers identical history):
   ```powershell
   cd C:\Proyectos\odoo-l10n-paraguay
   C:\Users\alcareaga\AppData\Local\Temp\gitleaks-bin\gitleaks.exe `
     detect --source . --no-git=false `
     --report-format sarif `
     --report-path gitleaks-local-baseline.sarif `
     --exit-code 0
   ```
4. **Scan result.**
   ```
   2:25PM INF 106 commits scanned.
   2:25PM INF scanned ~3268662 bytes (3.27 MB) in 1.48s
   2:25PM INF no leaks found
   ```
   SARIF parsed programmatically:
   ```powershell
   ((Get-Content gitleaks-local-baseline.sarif -Raw | ConvertFrom-Json).runs[0].results | Measure-Object).Count
   # → 0
   ```
5. **No `.gitleaksignore` created.** Per plan acceptance criteria: "If `.gitleaksignore` is created: header comment includes date + reason for each entry … No findings: DO NOT create `.gitleaksignore`. The file exists ONLY if there is content to allowlist." Worktree remains clean.
6. **Temp artifact cleanup.** `gitleaks-local-baseline.sarif` deleted from the main repo path before any commit. Verified via `Test-Path` returning `False` against both the main repo path and the worktree path.

### Rotation log

**None required.** Zero findings → zero tokens to rotate → zero `.gitleaksignore` entries.

### Acceptance criteria — verification

| Criterion                                                                                                             | Result                                                                                                    |
| --------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `gitleaks detect --source . --no-git=false --report-format sarif --report-path …` ran to completion                   | PASS — exit code 0, "no leaks found" reported                                                             |
| For every real-secret finding, token rotated at external service                                                      | N/A — 0 findings                                                                                          |
| `Test-Path gitleaks-local-baseline.sarif` returns `False` after cleanup                                               | PASS — `REMOVED` reported by cleanup step                                                                 |
| `.gitleaksignore` (if created) header comment includes date + reason; format `<sha>:<path>:<rule-id>:<line>` per line | N/A — not created (0 findings)                                                                            |
| `git filter-repo` / `git filter-branch` / BFG were NOT executed                                                       | PASS — `git reflog --all 2>&1 \| Select-String 'filter-repo\|filter-branch\|BFG' -Quiet` returned `False` |
| `git log --oneline main..HEAD \| Measure-Object -Line` shows no rewrite of historical commits                         | PASS — worktree HEAD still at base `65ae012` (no commits added or rewritten for this task)                |
| Future CI run of `gitleaks` job returns `success`                                                                     | DEFERRED — verified at next PR run (Wave 3 PR); local baseline 0 findings means CI will trivially pass    |

### Done criterion

> "Full-history gitleaks scan executed; any live secrets rotated; `.gitleaksignore` created only if needed with dated reasons; no history rewrite."

Met. **SEC-04 closed.**

## Task 02-03-02 — Bandit HIGH gate + MEDIUM/LOW audit

### What was done

1. **Install.** `pip install "bandit[sarif]==1.9.4"` (idempotent — already-satisfied deps reported; new packages `attrs`, `pbr`, `sarif-om`, `jschema-to-python`, `jsonpickle`, `setuptools` installed). Version confirmed:
   ```
   bandit 1.9.4
     python version = 3.13.13 (tags/v3.13.13:01104ce, Apr  7 2026, 19:25:48) [MSC v.1944 64 bit (AMD64)]
   ```
   Same pin used by `security.yml` CI job — local baseline therefore equals what CI will compute.
2. **HIGH gate pass** (D-02 fail-gate — must be 0):
   ```bash
   bandit -r addons/ -lll -iii -f screen
   ```
   Result:
   ```
   Total lines of code: 2228
   Total lines skipped (#nosec): 0
   Total issues (by severity): Undefined: 0  Low: 0  Medium: 0  High: 0
   Total issues (by confidence): Undefined: 0  Low: 0  Medium: 0  High: 0
   EXIT_CODE=0
   ```
3. **MEDIUM audit pass** (informational):
   ```bash
   bandit -r addons/ -ll -ii -f screen
   ```
   Result: 0 findings at MEDIUM+ severity and MEDIUM+ confidence.
4. **Full audit pass** (LOW + MEDIUM + HIGH, all confidence):
   ```bash
   bandit -r addons/ -f screen
   ```
   Result: 0 findings — same numbers across all three passes.

### Findings catalogue

**Total Bandit findings on `addons/` at scan date 2026-06-03 (bandit 1.9.4):**

| Severity | Count | Action               |
| -------- | ----- | -------------------- |
| HIGH     | 0     | Gate cumplido (D-02) |
| MEDIUM   | 0     | Nothing to defer     |
| LOW      | 0     | Nothing to defer     |

**`BUGS_BACKLOG.md` was NOT modified.** Per plan: "If there are zero MEDIUM/LOW findings, no append needed — record '0 MEDIUM/LOW findings' in the plan SUMMARY." That is what this section records.

Note for future scans: when MEDIUM/LOW findings appear, the section to add is:

```markdown
## Phase 2 — Bandit MEDIUM/LOW findings (deferred per D-02)

> Audit run: <YYYY-MM-DD> with bandit 1.9.4 (`-r addons/`)

- [ ] **B<test-id>** in <file>:<line> — <issue-text>. Confidence: <conf>. Defer rationale: <one-line>. Reassess: post-Fase 2 EDI per CONTEXT.md §Deferred.
```

This template is documented here so a future executor encountering findings on a re-scan can apply it consistently.

### Acceptance criteria — verification

| Criterion                                                                                                   | Result                                                                                                                                 |
| ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `bandit -r addons/ -lll -iii` returns exit code 0 (0 HIGH-severity + HIGH-confidence findings — D-02 gate)  | PASS — `EXIT_CODE=0`, "No issues identified"                                                                                           |
| If MEDIUM/LOW findings exist, `BUGS_BACKLOG.md` contains section `^## Phase 2 — Bandit MEDIUM/LOW findings` | N/A — 0 findings; no section appended (plan-specified behavior)                                                                        |
| For every MEDIUM/LOW finding, a bullet entry references Bandit test ID + file + line                        | N/A — 0 findings                                                                                                                       |
| `Select-String -Path BUGS_BACKLOG.md -Pattern 'bandit 1\.9\.4'` returns ≥1 match                            | N/A — no audit section added because 0 findings; if any had been added the version line would have been included as the section header |
| Bandit job in `security.yml`, when re-run on next PR, returns `success`                                     | DEFERRED — verified at next PR run; local baseline 0 HIGH means CI's matching `-lll -iii` re-run will also return 0                    |
| Commit message follows `chore(sec): triage bandit findings …`                                               | N/A — no file change to commit; result documented here in SUMMARY (which is committed)                                                 |

### Done criterion

> "0 HIGH Bandit findings in addons/; any MEDIUM/LOW documented in BUGS_BACKLOG.md with deferred rationale per D-02."

Met. **SEC-05 closed.**

## Task 02-03-03 — CHECKPOINT: branch protection update on main

**Type:** `checkpoint:human-verify`
**Gate:** `blocking-human`
**Status:** Not executed by agent — handoff returned to orchestrator/repo owner.

This task requires `repo admin` scope on a token that the executor does not hold by default. Per plan: "DO NOT attempt to run `gh api -X PUT ...` yourself — the executor does not have admin token by default."

The full checkpoint handoff (verbatim sections from PLAN.md task 02-03-03) is returned in the agent's final message to the orchestrator. The orchestrator forwards it to the user; the user performs the GitHub Settings change and types the resume-signal.

The agent ran tasks 01 and 02 to completion (atomic from a logical standpoint even though both produced 0 file changes), committed this SUMMARY, and stops. STATE.md and ROADMAP.md updates are deferred to the orchestrator after merge (worktree-isolation rule).

## Deviations from Plan

### Auto-fixed — Rule 3 (blocking issue): Docker daemon unavailable → fell back to native gitleaks binary

- **Found during:** Task 02-03-01 setup.
- **Issue:** `docker info` against both `desktop-linux` and `default` contexts failed with `failed to connect to the docker API at npipe:////./pipe/…`. The plan's primary invocation in `<action>` uses `docker run --rm -v "${PWD}:/repo" ghcr.io/gitleaks/gitleaks:latest …`.
- **Fix:** Used the alternative invocation explicitly enumerated by RESEARCH.md §"Cómo ejecutar gitleaks localmente en Windows" — native Windows binary downloaded from the canonical GitHub release. SHA256 verified against the official `gitleaks_8.30.1_checksums.txt` before extraction (`d29144deff3a68aa93ced33dddf84b7fdc26070add4aa0f4513094c8332afc4e`). Behavior is equivalent: same gitleaks version family scans the same git history with the same SARIF output schema.
- **Why this is Rule 3, not Rule 4:** The fix is a known, plan-blessed alternative (RESEARCH.md lists both Docker and native binary as valid paths). No architectural change — just a different way to run the same tool. No package substitution (Rule 3 exclusion does not apply because we did not switch to a "similarly-named" or different tool, just changed the delivery mechanism for the identical upstream).
- **Files modified:** None (the binary lives in `%LOCALAPPDATA%\Temp\gitleaks-bin\`, outside the repo).
- **Commit:** N/A (no in-repo files changed).

### Auto-fixed — Rule 1 (cosmetic, not behavioural): worktree base-check guard false-positive

- **Found during:** Initial `<worktree_branch_check>` execution.
- **Issue:** The guard compared `git merge-base HEAD 65ae012` (always full 40-char SHA) against the literal short `65ae012` and triggered an unnecessary `git reset --hard 65ae012`. The reset was a no-op (HEAD already at that commit) and the post-check `[ "$(git rev-parse HEAD)" != "65ae012" ]` similarly compared full vs short SHA, then exited 1.
- **Real state after the false-positive:** worktree HEAD is at the correct base, on the correct branch (`worktree-agent-ab8b154bfd93aa155`), with no uncommitted changes.
- **Fix:** Verified actual state manually (`git rev-parse HEAD`, `git rev-parse --abbrev-ref HEAD`, `git status --short`, `git rev-parse --show-toplevel`) and continued. No code change to the guard — that lives in the orchestrator's spawn prompt, outside this plan's scope.
- **Files modified:** None.
- **Commit:** N/A.

No other deviations.

## Authentication Gates

**None encountered.** The local gitleaks binary needed no auth (it operates on the local repo). Bandit needed no auth. The only operation that requires an admin token is task 02-03-03 (`gh api -X PUT … /required_status_checks/contexts`) — and that is the explicit handoff (not a gate hit by the agent).

## Threat Model Coverage

| Threat ID           | Disposition | This plan's mitigation                                                                                                                                       |
| ------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| T-SEC-04-leak       | mitigate    | Full-history gitleaks scan executed; 0 findings; no `.gitleaksignore` because nothing to allowlist                                                           |
| T-SEC-05-sast       | mitigate    | Bandit `-lll -iii` returns 0 findings; full audit (`-r addons/`) returns 0 findings at every severity                                                        |
| T-SEC-04-replay     | accept      | N/A — no rotated tokens (no tokens found)                                                                                                                    |
| T-SEC-03-protection | mitigate    | Deferred to task 02-03-03 (checkpoint); the 3 job names (`gitleaks`, `bandit`, `dependency-review`) are confirmed and ready to add to required status checks |

No new surface introduced. The 0-finding result is the strongest possible mitigation for T-SEC-04-leak and T-SEC-05-sast.

## Threat Flags

None. This plan added no new security-relevant surface — it only audited existing surface. The auditing artifacts (binaries, SARIF) live outside the repo.

## Known Stubs

None.

## Deferred Issues

None at the 3-attempt fix limit. Both auditorías were one-shot passes.

## Self-Check: PASSED

- `.planning/phases/02-bloque-b-security-baseline/02-03-SUMMARY.md` → FOUND (this file)
- gitleaks scan result `no leaks found` → captured in transcript above + SARIF result count = 0 confirmed programmatically
- Bandit HIGH gate exit code 0 → captured in transcript above with full severity/confidence breakdown
- No history rewrite verification (`git reflog --all | Select-String 'filter-repo|filter-branch|BFG' -Quiet`) → returned `False`
- Worktree base still at `65ae012` (no commits added by tasks 01/02 because both produced 0 file changes) → confirmed via `git log --oneline -3`

Validated with:

```powershell
Test-Path '.planning/phases/02-bloque-b-security-baseline/02-03-SUMMARY.md'  # → True
((Get-Content gitleaks-local-baseline.sarif -Raw | ConvertFrom-Json).runs[0].results | Measure-Object).Count  # → 0 (file already deleted but count was captured pre-delete)
bandit -r addons/ -lll -iii  # → exit 0, "No issues identified"
git reflog --all 2>&1 | Select-String 'filter-repo|filter-branch|BFG' -Quiet  # → False
git rev-parse HEAD  # → 65ae01291b0fec5adb86b846ab0b3f8845f23bc7 (base unchanged for tasks 01/02; this commit will advance only when SUMMARY is committed)
```
