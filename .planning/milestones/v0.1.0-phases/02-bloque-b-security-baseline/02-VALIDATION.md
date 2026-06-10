---
phase: 2
slug: bloque-b-security-baseline
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-06-02
updated: 2026-06-02
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.
> Phase 2 ships CI workflows + docs + LICENSE/SECURITY.md. There is no
> new Odoo Python code, so most validations are CI-job-based or
> file-existence/file-content assertions rather than unit tests.

---

## Test Infrastructure

| Property               | Value                                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| **Framework**          | pre-commit hooks (existing) + GitHub Actions `security.yml` (new in this phase) + manual file-content assertions via `grep`/`Read` |
| **Config file**        | `.pre-commit-config.yaml` (existing); `.github/workflows/security.yml` (new — SEC-03)                                              |
| **Quick run command**  | `pre-commit run --files <changed-files>` (PowerShell: same)                                                                        |
| **Full suite command** | `pre-commit run --all-files`                                                                                                       |
| **Estimated runtime**  | ~120 seconds (pre-commit) + CI security.yml ~60-180 seconds in Actions                                                             |

---

## Sampling Rate

- **After every task commit:** Run `pre-commit run --files <touched-files>`.
  For workflow YAML changes (SEC-03): additionally `actionlint .github/workflows/security.yml`
  if installed, otherwise rely on Actions UI dry-run after push.
- **After every plan wave:** Run `pre-commit run --all-files`. After wave that
  introduces `security.yml`, push to a PR branch and confirm all 3 jobs
  (gitleaks, bandit, dependency-review) report green in Actions.
- **Before `/gsd:verify-work`:** Full pre-commit must be green. `security.yml`
  must have run at least once on a PR and report no HIGH findings (Bandit)
  or live secrets (gitleaks).
- **Max feedback latency:** ~120s local (pre-commit) + ~3 min for CI on PR.

---

## Per-Task Verification Map

> Filled by the planner after PLAN.md generation. Each PLAN task gets
> one row mapping the task to its REQ-ID, the threat reference (if any),
> the verification command, and the proof artifact.

| Task ID  | Plan | Wave | Requirement | Threat Ref          | Secure Behavior                                                                     | Test Type     | Automated Command                                                                                                                                                              | File Exists | Status     |
| -------- | ---- | ---- | ----------- | ------------------- | ----------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------- | ---------- |
| 02-01-01 | 01   | 1    | SEC-01      | T-SEC-01-license    | LICENSE present in repo root with canonical SHA256                                  | file-assert   | `(Get-FileHash LICENSE -Algorithm SHA256).Hash.ToLower() -eq '0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0'`                                               | ❌ W0       | ⬜ pending |
| 02-01-02 | 01   | 1    | SEC-02      | T-SEC-02-disc       | Vulnerability reporting channel published                                           | file-assert   | `Select-String -Path SECURITY.md -Pattern 'security/advisories/new' -Quiet`                                                                                                    | ❌ W0       | ⬜ pending |
| 02-02-01 | 02   | 2    | SEC-03      | T-SEC-03-noscan     | security.yml has 3 jobs pinned to gitleaks@v3, dep-rev@v4, upload-sarif@v3          | CI-job + file | `Select-String -Path .github/workflows/security.yml -Pattern 'gitleaks/gitleaks-action@v3' -Quiet` AND green `gh run list --workflow=security.yml`                             | ❌ W0       | ⬜ pending |
| 02-02-02 | 02   | 2    | SEC-03      | T-SEC-03-supply     | Dependency Graph + Dependabot alerts enabled at GitHub Settings                     | manual UI     | `gh api repos/Ezcareaga/l10n-paraguay --jq '.security_and_analysis.dependabot_alerts.status'` equals `"enabled"`                                                               | n/a         | ⬜ pending |
| 02-03-01 | 03   | 3    | SEC-04      | T-SEC-04-leak       | gitleaks full-history scan executed; tokens rotated; .gitleaksignore (if any) dated | CI-job + log  | gitleaks job in security.yml exits 0 on PR AND `git reflog --all` shows NO filter-repo/filter-branch/BFG                                                                       | n/a         | ⬜ pending |
| 02-03-02 | 03   | 3    | SEC-05      | T-SEC-05-sast       | Bandit reports zero HIGH severity findings                                          | CI-job        | `bandit -r addons/ -lll -iii` exits 0                                                                                                                                          | ❌ W0       | ⬜ pending |
| 02-03-03 | 03   | 3    | SEC-03      | T-SEC-03-protection | Branch protection on main includes the 3 security job names                         | manual UI     | `gh api repos/Ezcareaga/l10n-paraguay/branches/main/protection/required_status_checks --jq '.contexts'` array contains `gitleaks`, `bandit`, `dependency-review`               | n/a         | ⬜ pending |
| 02-04-01 | 04   | 4    | SEC-06      | T-SEC-06-doc        | 6 ejes documentados + CCFE blueprint dense for Fase 2 EDI                           | doc-assert    | `(Select-String -Path docs/60_SECURITY_BASELINE.md -Pattern '^## [1-6]\. ' \| Measure-Object).Count` ≥ 6 AND `Select-String 'NO ejecutar en Phase 2' -Quiet` returns True      | ❌ W0       | ⬜ pending |
| 02-04-02 | 04   | 4    | SEC-06      | T-SEC-06-stub       | restore-smoke.sh exists as executable stub, parses, exits 0                         | script-assert | `bash -n scripts/restore-smoke.sh` exits 0 AND `git ls-files --stage scripts/restore-smoke.sh` shows mode `100755`                                                             | ❌ W0       | ⬜ pending |
| 02-04-03 | 04   | 4    | SEC-06      | —                   | README has 1 new security badge + 1 new Seguridad section                           | file-assert   | `(Select-String -Path README.md -Pattern 'security\.yml/badge\.svg' \| Measure-Object).Count` equals 1 AND `Select-String '^## Seguridad$' -Quiet` returns True                | ✓           | ⬜ pending |
| 02-05-01 | 05   | 4    | SEC-07      | T-SEC-07-doc        | docs/61 named \_LEY_7593.md (NOT \_LEY_6534.md); ANPDP authority; vendor/operador   | doc-assert    | `Test-Path docs/61_COMPLIANCE_LEY_7593.md` AND `Test-Path docs/61_COMPLIANCE_LEY_6534.md` is False AND `Select-String 'ANPDP' -Quiet` True AND `Select-String 'SENAC'` count 0 | ❌ W0       | ⬜ pending |

_Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky_

> **Note:** Task IDs filled in 2026-06-02 by `gsd-phase-planner`. Every row
> matches a task in 02-NN-PLAN.md.

---

## Wave 0 Requirements

- [ ] **`security.yml` workflow file** — `.github/workflows/security.yml`
      created and committed (PR triggers CI runs). Without it, no SEC-03/04/05
      verification possible. Created by Task 02-02-01.
- [ ] **`LICENSE` file** — created at repo root with canonical AGPL-3.0 text
      (SHA256 verified — see 02-RESEARCH.md §LICENSE). Created by Task 02-01-01.
- [ ] **`SECURITY.md` file** — created at repo root with the skeleton from
      02-RESEARCH.md §SECURITY.md Skeleton. Created by Task 02-01-02.
- [ ] **GitHub repo settings** — enable Dependency Graph + Dependabot alerts
      (manual UI step, documented in plan). Needed for `dependency-review-action`
      to work. Performed by Task 02-02-02.
- [ ] **No new tooling installs required for unit tests** — Phase 2 ships
      zero Python production code, so existing pytest infra (Phase 1) is
      sufficient.

_Wave 0 here means "infrastructure that must exist before any other task can
verify". Since Phase 2 = config + docs, Wave 0 = file scaffolding + repo
settings, not test framework installs._

---

## Manual-Only Verifications

| Behavior                                             | Requirement | Why Manual                                                                                                        | Test Instructions                                                                                                                                                                                                                                                           |
| ---------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Branch protection includes 3 security status checks  | SEC-03      | GitHub Settings UI; not scriptable without admin token + gh CLI rule editor                                       | After workflow merged, open Settings → Branches → main → Edit, confirm `gitleaks`, `bandit`, `dependency-review` are in required checks. Verify via `gh api repos/Ezcareaga/l10n-paraguay/branches/main/protection/required_status_checks --jq '.contexts'`. Task 02-03-03. |
| Dependency Graph + Dependabot alerts enabled         | SEC-03      | GitHub Settings UI; admin step                                                                                    | Open Settings → Code security and analysis → enable "Dependency graph" + "Dependabot alerts" + "Dependabot security updates". Task 02-02-02.                                                                                                                                |
| Compliance matrix (D-15) is well-formed and accurate | SEC-07      | Subjective; requires human reading of legal text vs matrix rows                                                   | Reviewer reads `docs/61_COMPLIANCE_LEY_7593.md` final table; cross-checks each "Estado" cell against the actual control linked in docs/60. Optional: legal counsel review.                                                                                                  |
| CCFE blueprint (D-10) is unambiguous for Fase 2 EDI  | SEC-06      | Subjective; the proof is "Fase 2 EDI can implement without re-deciding". Will be verified retroactively in Fase 2 | Reviewer reads `docs/60_SECURITY_BASELINE.md` §5 "CCFE Encryption" and confirms: envelope schema present, rotation script outline present, systemd-creds + ir.config_parameter layout present. Mark as TODO for Fase 2 EDI retro-verification.                              |
| Token rotation completed for any gitleaks finding    | SEC-04      | Requires admin access to external services (GitHub, Codecov, etc.); only the owner can verify rotation worked     | For each real-secret finding from Task 02-03-01: confirm in the external service dashboard that the old token is revoked and a new one issued; new token works in CI (test workflow still green); record rotation date in `.gitleaksignore` comment.                        |

---

## Validation Sign-Off

- [x] Every PLAN.md task has either a `<automated>` verify command OR a row
      in "Manual-Only Verifications" above (2026-06-02: all 11 tasks have one or the other)
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
      (manual UI tasks 02-02-02 and 02-03-03 are interleaved with auto tasks)
- [x] Wave 0 covers all MISSING references (LICENSE / SECURITY.md / security.yml
      scaffolding before any verification can run)
- [x] No watch-mode flags in any `<automated>` block
- [x] Feedback latency < 180s (local pre-commit < 120s + Bandit/gitleaks CI < 60s)
- [x] `nyquist_compliant: true` set in frontmatter (planner filled all Task IDs; checker confirms in plan-phase step 11)

**Approval:** ready for plan-checker pass.
