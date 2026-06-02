---
phase: 2
slug: bloque-b-security-baseline
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-02
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

| Task ID | Plan | Wave | Requirement | Threat Ref      | Secure Behavior                             | Test Type   | Automated Command                                                                                                             | File Exists | Status     |
| ------- | ---- | ---- | ----------- | --------------- | ------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------------------- | ----------- | ---------- |
| TBD     | 01   | 1    | SEC-01      | —               | LICENSE present in repo root                | file-assert | `Test-Path LICENSE` + SHA256 match agpl-3.0.txt canonical                                                                     | ❌ W0       | ⬜ pending |
| TBD     | 02   | 1    | SEC-02      | T-SEC-02-disc   | Vulnerability reporting channel published   | file-assert | `Select-String -Path SECURITY.md -Pattern 'security/advisories/new'`                                                          | ❌ W0       | ⬜ pending |
| TBD     | 03   | 2    | SEC-03      | T-SEC-03-noscan | CI scans every PR + push to main            | CI-job      | Push to PR branch; verify Actions UI shows 3 green jobs (gitleaks/bandit/dep-rev)                                             | ❌ W0       | ⬜ pending |
| TBD     | 03   | 2    | SEC-04      | T-SEC-04-leak   | gitleaks finds no live secrets in HEAD      | CI-job      | `gitleaks detect --no-banner --redact` exits 0 on PR                                                                          | ❌ W0       | ⬜ pending |
| TBD     | 03   | 2    | SEC-05      | T-SEC-05-sast   | Bandit reports zero HIGH severity findings  | CI-job      | `bandit -r addons/ -lll -iii -f sarif -o bandit.sarif` exits 0                                                                | ❌ W0       | ⬜ pending |
| TBD     | 04   | 3    | SEC-06      | T-SEC-06-doc    | 6 ejes documentados con commands            | doc-assert  | 6× `Select-String -Path docs/60_*.md -Pattern '## (2FA / Password / Audit / Backup / CCFE / Network)'` (one per axis) ≥6 hits | ❌ W0       | ⬜ pending |
| TBD     | 04   | 3    | SEC-07      | T-SEC-07-doc    | Ley 7593/2025 mapping + matriz cumplimiento | doc-assert  | `Select-String -Path docs/61_*.md -Pattern 'Ley 7593'` AND matriz table at file tail                                          | ❌ W0       | ⬜ pending |

_Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky_

> **Note:** Task IDs are placeholders until PLAN.md files are written.
> The plan-checker is expected to verify that every row above is replaced
> with a real Task ID from the corresponding PLAN.md.

---

## Wave 0 Requirements

- [ ] **`security.yml` workflow file** — `.github/workflows/security.yml`
      created and committed (PR triggers CI runs). Without it, no SEC-03/04/05
      verification possible.
- [ ] **`LICENSE` file** — created at repo root with canonical AGPL-3.0 text
      (SHA256 verified — see 02-RESEARCH.md §LICENSE).
- [ ] **`SECURITY.md` file** — created at repo root with the skeleton from
      02-RESEARCH.md §SECURITY.md Skeleton.
- [ ] **GitHub repo settings** — enable Dependency Graph + Dependabot alerts
      (manual UI step, documented in plan). Needed for `dependency-review-action`
      to work.
- [ ] **No new tooling installs required for unit tests** — Phase 2 ships
      zero Python production code, so existing pytest infra (Phase 1) is
      sufficient.

_Wave 0 here means "infrastructure that must exist before any other task can
verify". Since Phase 2 = config + docs, Wave 0 = file scaffolding + repo
settings, not test framework installs._

---

## Manual-Only Verifications

| Behavior                                             | Requirement | Why Manual                                                                                                        | Test Instructions                                                                                                                                                                                                       |
| ---------------------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Branch protection includes `security` status check   | CI-07\*     | GitHub Settings UI; not scriptable without admin token + gh CLI rule editor                                       | After workflow merged, open Settings → Branches → main → Edit, confirm `security` is in required checks. Document command in PLAN.md.                                                                                   |
| Dependency Graph + Dependabot alerts enabled         | SEC-03      | GitHub Settings UI; admin step                                                                                    | Open Settings → Code security and analysis → enable "Dependency graph" + "Dependabot alerts" + "Dependabot security updates"                                                                                            |
| Compliance matrix (D-15) is well-formed and accurate | SEC-07      | Subjective; requires human reading of legal text vs matrix rows                                                   | Reviewer reads `docs/61_COMPLIANCE_LEY_7593.md` final table; cross-checks each "Estado" cell against the actual control linked in docs/60                                                                               |
| CCFE blueprint (D-10) is unambiguous for Fase 2 EDI  | SEC-06      | Subjective; the proof is "Fase 2 EDI can implement without re-deciding". Will be verified retroactively in Fase 2 | Reviewer reads `docs/60` §"CCFE Encryption" and confirms: envelope schema present, rotation script outline present, systemd-creds + ir.config_parameter layout present. Mark as TODO for Fase 2 EDI retro-verification. |

(\*) CI-07 was a Phase 1 REQ; Phase 2 just adds one more check to the list.

---

## Validation Sign-Off

- [ ] Every PLAN.md task has either a `<automated>` verify command OR a row
      in "Manual-Only Verifications" above
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references (LICENSE / SECURITY.md / security.yml
      scaffolding before any verification can run)
- [ ] No watch-mode flags in any `<automated>` block
- [ ] Feedback latency < 180s (local pre-commit < 120s + Bandit/gitleaks CI < 60s)
- [ ] `nyquist_compliant: true` set in frontmatter (after planner fills Task IDs
      and plan-checker confirms every row matches a real task)

**Approval:** pending (will be approved after the plan-checker pass at
plan-phase step 11 or after retroactive Nyquist audit if checker is skipped).
