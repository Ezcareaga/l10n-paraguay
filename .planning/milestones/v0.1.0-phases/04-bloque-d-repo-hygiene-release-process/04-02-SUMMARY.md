---
phase: 04-bloque-d-repo-hygiene-release-process
plan: 02
subsystem: repo-hygiene
tags: [github-meta, codeowners, release-notes, pr-template, contributing]
requires:
  - "CONTRIBUTING.md (Phase 3 DOC-03) — provides the '## Release process' placeholder to replace"
  - "SECURITY.md / branch protection (Phase 2) — context for review routing"
provides:
  - ".github/CODEOWNERS — global review owner @Ezcareaga + inert area stubs"
  - ".github/PULL_REQUEST_TEMPLATE.md — soft-reminder PR checklist"
  - ".github/release.yml — label→category release-notes map + bot/skip-changelog exclusion"
  - "CONTRIBUTING.md §Release process — documented manual 4-step release"
affects:
  - "Plan 04-03 (creates the labels referenced by release.yml)"
  - "Plan 04-04 (publishes v0.1.0 release using these files + documented steps)"
tech_stack:
  added: []
  patterns:
    - "GitHub native meta-files (no custom actions/scripts)"
    - "Keep a Changelog + Conventional Commit label taxonomy"
key_files:
  created:
    - ".github/CODEOWNERS"
    - ".github/PULL_REQUEST_TEMPLATE.md"
    - ".github/release.yml"
  modified:
    - "CONTRIBUTING.md"
decisions:
  - "CODEOWNERS global rule `* @Ezcareaga` placed on physical line 1 (not under a comment header) to satisfy the plan's literal verify (`head -n 1 | grep -qv '^#'`); explanatory comments + commented area stubs follow below — last-match-wins semantics preserved"
  - 'release.yml uses 7 categories ending in a `"*"` catch-all so no labeled PR is silently dropped'
  - "Manual release process documented (D-01) — no semantic-release; reassess after several releases"
metrics:
  duration: "~6min"
  completed: "2026-06-09"
  tasks: 2
  files: 4
  commits: 2
---

# Phase 04 Plan 02: PR-hygiene + Release-categorization layer Summary

Created the PR-hygiene and release-categorization meta-files — `CODEOWNERS`
(global `@Ezcareaga` + commented area stubs), `release.yml` (PR-label→Keep-a-Changelog
category map with bot/skip-changelog exclusion), `PULL_REQUEST_TEMPLATE.md`
(soft-reminder checklist), and replaced the CONTRIBUTING.md "Release process"
placeholder with the documented manual 4-step process + label→category table.
This completes the final local-file content needed before the v0.1.0 rollback point.

## What was built

### Task 1 — CODEOWNERS + PR template (commit `76eac19`)

- `.github/CODEOWNERS`: `* @Ezcareaga` on line 1 (global owner, last-match-wins),
  followed by an explanatory comment block and commented-out future area stubs
  (`# /addons/l10n_py_base/`, `l10n_py_account`, `l10n_py_edi`, `/docs/`, `/.github/`).
  The stubs are inert until uncommented — zero effect on current review routing.
- `.github/PULL_REQUEST_TEMPLATE.md`: `## Description` (with "Closes #N" HTML-comment
  prompt), `## Type of change` checkbox list (fix/feat/docs/refactor/ci-build/other),
  and `## Checklist` of soft reminders (tests `pytest addons/ -x`, pre-commit,
  Conventional Commits, docs-if-behavior-changed, ADR/DOC-09 if architectural,
  CHANGELOG if release-worthy). Soft reminders only — branch protection enforces CI.

### Task 2 — release.yml + CONTRIBUTING release section (commit `b46f4df`)

- `.github/release.yml`: `changelog:` with `exclude` (`skip-changelog` label,
  `dependabot[bot]` author) and 7 ordered categories — Added (`feat`/`enhancement`),
  Fixed (`bug`/`fix`), Changed (`changed`/`refactor`/`chore`), Security (`security`),
  Documentation (`documentation`/`docs`), Dependencies (`dependencies`), and Other
  (`"*"` catch-all last). yamllint green.
- `CONTRIBUTING.md` §Release process: replaced the `> **Deferred to Phase 4**`
  blockquote with the "Decision: manual releases" rationale, a numbered 4-step
  process (compile CHANGELOG → merge to main w/ 6 checks → `git tag -a` + push →
  `gh release create --notes-file --latest`), and the PR-label→category mapping
  table. The `## Release process` heading and surrounding `---` separators were kept.

## Verification

- Task 1 automated verify: PASS (`* @Ezcareaga` line 1, `## Checklist` + `ADR` present).
- Task 2 automated verify: PASS (`changelog:`, `dependabot[bot]`, `skip-changelog`,
  `"*"` present; `## Release process` present; "Deferred to Phase 4" gone; `git tag`
  present; `pre-commit run yamllint --files .github/release.yml` green).
- `grep -c 'title:' .github/release.yml` → 7 categories (matches plan §verification).
- Pre-commit hooks ran green on both commits (codespell, yamllint, prettier, EOF, etc.).
- No accidental file deletions; no stray untracked files introduced.

Remaining smoke checks are GitHub-UI/manual and deferred to post-merge (open a test
PR → template auto-populates + `@Ezcareaga` auto-requested as reviewer). These are
inherently platform-side and cannot be validated from the local tree.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] CODEOWNERS first-line ordering to satisfy literal verify**

- **Found during:** Task 1 verification.
- **Issue:** The plan's automated verify includes `head -n 1 .github/CODEOWNERS | grep -qv '^#'`,
  which requires the FIRST physical line to be a non-comment line. The first draft
  led with a comment header block, so the `* @Ezcareaga` rule (though the first
  _non-comment_ line, per the acceptance criteria wording) was not on physical line 1.
- **Fix:** Moved `* @Ezcareaga` to physical line 1; the explanatory comments and the
  commented area stubs now follow below it. Last-match-wins semantics are unchanged
  (the global rule is still first; stubs remain commented/inert).
- **Files modified:** `.github/CODEOWNERS`
- **Commit:** `76eac19`

## Threat Model Disposition

- **T-04-04 (CODEOWNERS, mitigate):** `* @Ezcareaga` verified as the first rule;
  handle matches the repo owner (`@Ezcareaga`, per STATE.md / PROJECT.md). Existing
  branch protection (6 checks) still gates CODEOWNER review.
- **T-04-05 (release.yml, mitigate):** bot/skip-changelog exclusion present; `"*"`
  catch-all ensures no labeled PR is silently dropped from notes.
- **T-04-06 (release.yml read from default branch, accept):** satisfied by wave order
  — this is Wave 1, the v0.1.0 tag is a later plan; release.yml will be on `main` first.

No new security surface introduced beyond the planned threat register.

## Known Stubs

CODEOWNERS area stubs are intentionally commented out (D-04) — they are inert until
contributors join and are activated per-area. This is the documented design, not an
incomplete implementation. The release.yml labels (`feat`, `fix`, `changed`,
`security`, `docs`, `skip-changelog`, etc.) do not yet exist in the repo; Plan 04-03
creates them. The file is valid YAML and applies correctly once labels exist.

## Requirements satisfied

- **REL-02** — `PULL_REQUEST_TEMPLATE.md` checklist (tests, docs, ADR, Conventional Commits).
- **REL-03** — `CODEOWNERS` global `@Ezcareaga` + commented area stubs.
- **REL-04** — `release.yml` label→category map + bot/skip-changelog exclusion.
- **REL-06** — manual release process documented in CONTRIBUTING; placeholder removed.

## Self-Check: PASSED

All 3 created files exist (`.github/CODEOWNERS`, `.github/PULL_REQUEST_TEMPLATE.md`,
`.github/release.yml`), the CONTRIBUTING.md edit is in place (`## Release process`
present, placeholder gone), and both commits (`76eac19`, `b46f4df`) are in the git log.
