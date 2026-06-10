---
phase: 04-bloque-d-repo-hygiene-release-process
plan: 01
subsystem: infra
tags:
  [github, issue-forms, issue-templates, contact-links, repo-hygiene, REL-01]

# Dependency graph
requires:
  - phase: 02-bloque-b-security-baseline
    provides: SECURITY.md (private security reporting channel surfaced by config.yml contact_link)
provides:
  - GitHub issue intake layer — 2 structured YAML issue forms (Bug Report, Feature Request)
  - config.yml that disables blank issues and routes Q&A to Discussions + security to /security/policy
affects: [04-02, 04-03, 04-04, release-v0.1.0]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "GitHub YAML issue forms (.github/ISSUE_TEMPLATE/*.yml) over Markdown templates"
    - "config.yml contact_links route non-actionable intake (Q&A, security) off the public issue tracker"

key-files:
  created:
    - .github/ISSUE_TEMPLATE/bug_report.yml
    - .github/ISSUE_TEMPLATE/feature_request.yml
    - .github/ISSUE_TEMPLATE/config.yml
  modified: []

key-decisions:
  - "Generic /discussions URL for the Q&A contact_link (Discussions not yet enabled; Plan 03 enables it and may refine to the Q&A category slug) — Pitfall 4 mitigation"
  - "question.yml deliberately omitted (Amendment A-01 to REL-01) — questions route to Discussions, keeping issues actionable"
  - "Default labels bug/enhancement used for auto-labeling (already exist in repo, so auto-tagging works immediately)"

patterns-established:
  - "Pattern 1: GitHub YAML issue forms with required textareas + required checkboxes for structured, actionable intake"
  - "Pattern 2: config.yml blank_issues_enabled:false + two contact_links (Discussions Q&A, /security/policy) as the only non-form intake routes"

requirements-completed: [REL-01]

# Metrics
duration: 8min
completed: 2026-06-09
---

# Phase 4 Plan 01: GitHub Issue Intake Layer Summary

**Two structured YAML issue forms (Bug Report auto-labeling `bug`, Feature Request auto-labeling `enhancement`) plus a `config.yml` that blocks blank issues and routes questions to Discussions and security reports to the private `/security/policy` channel.**

## Performance

- **Duration:** ~8 min
- **Started:** 2026-06-09
- **Completed:** 2026-06-09
- **Tasks:** 2
- **Files modified:** 3 (all created)

## Accomplishments

- Created `bug_report.yml` — structured bug intake with required "What happened?", "Expected behavior", "Steps to reproduce" textareas, a required `odoo_version` input (placeholder `18.0`), an optional `logs` textarea (`render: shell`), and a required checkboxes block (searched existing issues; using Odoo Community 18.0 not Enterprise). Auto-labels `bug`.
- Created `feature_request.yml` — required "Problem or motivation" + "Proposed solution" textareas, optional "Alternatives considered", required checkbox (searched issues and discussions). Auto-labels `enhancement`.
- Created `config.yml` — `blank_issues_enabled: false` plus exactly two `contact_links`: Q&A → GitHub Discussions (generic URL), Report a Security Vulnerability → `/security/policy`. Both full HTTPS URLs.
- `question.yml` deliberately NOT created (Amendment A-01) — questions are routed to Discussions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Create bug_report.yml and feature_request.yml issue forms** - `cfba825` (feat)
2. **Task 2: Create config.yml routing questions to Discussions and security to private policy** - `bf3b1fd` (feat)

**Plan metadata:** committed with SUMMARY + STATE + ROADMAP (docs).

## Files Created/Modified

- `.github/ISSUE_TEMPLATE/bug_report.yml` - Structured bug intake form, auto-labels `bug`.
- `.github/ISSUE_TEMPLATE/feature_request.yml` - Structured feature intake form, auto-labels `enhancement`.
- `.github/ISSUE_TEMPLATE/config.yml` - `blank_issues_enabled: false` + Discussions + security `/security/policy` contact_links.

## Decisions Made

- **Generic `/discussions` URL** for the Q&A contact_link, not the `/discussions/categories/q-a` slug. Rationale: Discussions is not yet enabled at this plan's execution time (Plan 03 enables it). A specific category URL would 404 today, which could push a frustrated user to file a public issue with sensitive content (T-04-03). Plan 03 may refine to the Q&A category slug after enabling.
- **`question.yml` omitted** (Amendment A-01 to REL-01). Questions route to Discussions instead of an issue form — cleaner triage, issues stay actionable. The verifier MUST NOT fail on the absence of `question.yml`.
- **Default labels `bug` / `enhancement`** used for auto-labeling. They already exist in the repo (GitHub defaults), so auto-tagging works immediately without a label-creation step.
- **All content in English** per D-01 (Phase 3 carry-forward — all `.github/*` meta files in English for the OCA reviewer).

## Deviations from Plan

None - plan executed exactly as written.

The RESEARCH Assumption A4 fallback (adding `.yamllint` ignore for `.github/ISSUE_TEMPLATE/`) was NOT needed — the existing `.yamllint` config (`truthy: check-keys: false`, `line-length: level: warning`, `document-start: disable`) already absorbs the GitHub issue-form schema keys. yamllint passed green on all three files on the first run.

## Threat Model Compliance

- **T-04-01 (Information Disclosure — security contact_link):** mitigated. `blank_issues_enabled: false` + security contact_link → canonical `/security/policy` render of SECURITY.md routes vulnerability reports to the private channel.
- **T-04-03 (Information Disclosure — dead Q&A link):** mitigated. Generic `/discussions` URL avoids a 404 dead link while Discussions is not yet enabled.
- **T-04-02 (Tampering — issue-form labels):** accept (per plan). GitHub only auto-applies labels that already exist; `bug`/`enhancement` are defaults, so no arbitrary label injection is possible.

No new security surface introduced beyond what the threat model already covers.

## Issues Encountered

None.

## User Setup Required

None at this plan's level. Note: GitHub Discussions enablement (an outward-facing maintainer action) is handled in a later plan (Plan 03). The generic `/discussions` URL works as a non-404 fallback until then; the chooser UI and security routing are fully functional now.

## Next Phase Readiness

- Issue intake layer complete and lint-clean. The issue chooser will present exactly 2 forms + 2 contact links + no blank-issue option once merged to the default branch.
- Ready for Plan 04-02 (CODEOWNERS / PR template / release.yml per the wave plan) and the later Discussions-enablement + v0.1.0 release steps.
- Post-merge GitHub-UI smoke test (manual, after Plan 03 enables Discussions): open `https://github.com/Ezcareaga/l10n-paraguay/issues/new/choose`.

## Self-Check: PASSED

- FOUND: `.github/ISSUE_TEMPLATE/bug_report.yml`
- FOUND: `.github/ISSUE_TEMPLATE/feature_request.yml`
- FOUND: `.github/ISSUE_TEMPLATE/config.yml`
- CONFIRMED: no `.github/ISSUE_TEMPLATE/question.yml`
- FOUND commit: `cfba825` (Task 1)
- FOUND commit: `bf3b1fd` (Task 2)

---

_Phase: 04-bloque-d-repo-hygiene-release-process_
_Completed: 2026-06-09_
