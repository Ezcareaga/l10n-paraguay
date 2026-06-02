---
phase: 02-bloque-b-security-baseline
plan: "01"
subsystem: infra
tags: [license, agpl, security, disclosure, github-advisories]

requires:
  - phase: 01-bloque-a-foundation-tecnica-ci-cd-pre-commit
    provides: Branch protection + pre-commit hooks already active; commits run full hook chain

provides:
  - LICENSE AGPL-3.0 canonical file at repo root (SHA256 verified)
  - SECURITY.md vulnerability disclosure policy at repo root

affects:
  - 02-02 (security.yml workflow — references SECURITY.md existence as context)
  - 03 (Phase 3 README update will add link to SECURITY.md)
  - GitHub Security tab (SECURITY.md activates "Report a vulnerability" affordance)

tech-stack:
  added: []
  patterns:
    - "AGPL-3.0 LICENSE from https://www.gnu.org/licenses/agpl-3.0.txt — download directly, verify SHA256, never edit"
    - "SECURITY.md sections order: Supported Versions, Reporting a Vulnerability, Security Update Process, Acknowledgements"

key-files:
  created:
    - LICENSE
    - SECURITY.md
  modified: []

key-decisions:
  - "D-05 applied: GitHub Security Advisories as primary channel (private + CVE-ready); careagaezz@gmail.com as fallback only"
  - "D-06 applied: no PGP section — GH Advisories provides TLS; low report-volume threat model accepted"
  - "D-07 applied: no manual Hall of Fame table — link to /security/advisories (GH updates automatically)"
  - "D-08 applied: only 18.0.x supported — single-maintainer realistic policy"
  - "LICENSE downloaded verbatim from canonical URL, SHA256 verified before commit — zero manual edits"

patterns-established:
  - "License verification: always check SHA256 against RESEARCH.md canonical value before committing"
  - "SECURITY.md: use RESEARCH.md skeleton verbatim; run negative checks (PGP, HoF, regulators) before commit"

requirements-completed:
  - SEC-01
  - SEC-02

duration: 15min
completed: "2026-06-02"
---

# Phase 2 Plan 01: Visible Meta Files (LICENSE + SECURITY.md) Summary

**AGPL-3.0 LICENSE (canonical SHA256-verified) + SECURITY.md vulnerability disclosure policy added at repo root, enabling GitHub Security Advisory flow and OCA license compliance**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-06-02T00:00:00Z
- **Completed:** 2026-06-02
- **Tasks:** 2
- **Files created:** 2 (LICENSE, SECURITY.md)
- **Files modified:** 0

## Accomplishments

- Downloaded canonical AGPL-3.0 LICENSE from `https://www.gnu.org/licenses/agpl-3.0.txt`; SHA256 `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0` verified (34,523 bytes)
- Created SECURITY.md with 4 required sections per skeleton from 02-RESEARCH.md, GitHub Security Advisories as primary channel, SLA 72h/30d, no PGP, no manual HoF table
- Confirmed `license="AGPL-3"` already present in both manifests (l10n_py_base + l10n_py_account) and `pyproject.toml` — no edits required

## Task Commits

1. **Task 02-01-01: Download canonical AGPL-3.0 LICENSE and verify SHA256** — `de5de11` (feat(sec))
2. **Task 02-01-02: Create SECURITY.md with vulnerability disclosure policy** — `c365ea1` (docs(sec))

## Files Created/Modified

- `LICENSE` — GNU AGPL-3.0 full text, canonical from gnu.org, SHA256 verified (34,523 bytes)
- `SECURITY.md` — Vulnerability disclosure policy with GH Security Advisories primary channel, email fallback, SLA 72h/30d, supported versions 18.0.x only, acknowledgements link to /security/advisories

## Decisions Made

Applied plan decisions as specified (D-05 through D-08 from 02-CONTEXT.md):

- GH Security Advisories as primary channel over PGP (D-05, D-06)
- No manual Hall of Fame — GH advisory native flow (D-07)
- Only 18.0.x supported — single-maintainer policy (D-08)

## Regression Guards Verified

| Guard                                                    | Check                                                            | Result |
| -------------------------------------------------------- | ---------------------------------------------------------------- | ------ |
| LICENSE first non-empty line                             | Leading whitespace + "GNU AFFERO GENERAL PUBLIC LICENSE"         | PASS   |
| LICENSE SHA256                                           | 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0 | PASS   |
| LICENSE size                                             | 34,523 bytes                                                     | PASS   |
| SECURITY.md has no PGP/GPG                               | grep count = 0                                                   | PASS   |
| SECURITY.md has no Hall of Fame                          | grep count = 0                                                   | PASS   |
| SECURITY.md has no regulator names (SENAC, ANPDP, MITIC) | grep count = 0                                                   | PASS   |
| l10n_py_base manifest `license="AGPL-3"`                 | grep match found, unmodified                                     | PASS   |
| l10n_py_account manifest `license="AGPL-3"`              | grep match found, unmodified                                     | PASS   |
| No edits to addons/ or pyproject.toml                    | git diff shows only LICENSE + SECURITY.md                        | PASS   |

## Acceptance Criteria Results

| Criterion                                           | Expected        | Result |
| --------------------------------------------------- | --------------- | ------ |
| `Test-Path LICENSE`                                 | True            | PASS   |
| SHA256 of LICENSE                                   | 0d96a4ff...bcb0 | PASS   |
| LICENSE size                                        | 34,523 bytes    | PASS   |
| "GNU AFFERO GENERAL PUBLIC LICENSE" in LICENSE      | True            | PASS   |
| "Version 3, 19 November 2007" in LICENSE            | True            | PASS   |
| `Test-Path SECURITY.md`                             | True            | PASS   |
| `# Security Policy` (H1) in SECURITY.md             | True            | PASS   |
| `## Supported Versions` in SECURITY.md              | True            | PASS   |
| `## Reporting a Vulnerability` in SECURITY.md       | True            | PASS   |
| `## Security Update Process` in SECURITY.md         | True            | PASS   |
| `## Acknowledgements` in SECURITY.md                | True            | PASS   |
| `security/advisories/new` in SECURITY.md (≥1 match) | True            | PASS   |
| `careagaezz@gmail.com` in SECURITY.md (≥1 match)    | True            | PASS   |
| `18.0.x` in SECURITY.md                             | True            | PASS   |
| `72 hours` in SECURITY.md                           | True            | PASS   |
| `30 days` in SECURITY.md                            | True            | PASS   |
| PGP/GPG count in SECURITY.md                        | 0               | PASS   |
| Hall of Fame count in SECURITY.md                   | 0               | PASS   |
| Regulator names count (SENAC/ANPDP/MITIC)           | 0               | PASS   |
| Manifests unmodified                                | 0 diff lines    | PASS   |

## Deviations from Plan

None — plan executed exactly as written. License was downloaded verbatim from canonical URL and verified before commit. SECURITY.md used the RESEARCH.md skeleton verbatim.

## Issues Encountered

None. Pre-commit hooks ran cleanly on both commits (codespell, prettier, trim whitespace, end-of-file all passed for SECURITY.md; LICENSE-only commit skipped all non-applicable hooks).

## User Setup Required

None — no external service configuration required for this plan. After the PR merges to `main`, GitHub will automatically render SECURITY.md in the Security tab and show the "Report a vulnerability" affordance.

## Next Phase Readiness

- SEC-01 and SEC-02 closed. Wave 1 of Phase 2 complete.
- Next: Plan 02-02 (CI security workflow — gitleaks + Bandit + Dependency Review), which depends on Wave 1 completion.
- No blockers.

## Self-Check

- [x] `LICENSE` exists at repo root: confirmed
- [x] `SECURITY.md` exists at repo root: confirmed
- [x] Commit `de5de11` exists: confirmed (feat(sec): add LICENSE AGPL-3.0)
- [x] Commit `c365ea1` exists: confirmed (docs(sec): add SECURITY.md)
- [x] No files outside allowed set modified (LICENSE, SECURITY.md only)
- [x] Both manifests `license="AGPL-3"` confirmed unmodified

---

_Phase: 02-bloque-b-security-baseline_
_Plan: 01_
_Completed: 2026-06-02_
