---
phase: 04-bloque-d-repo-hygiene-release-process
reviewed: 2026-06-09T18:32:40Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - .github/ISSUE_TEMPLATE/bug_report.yml
  - .github/ISSUE_TEMPLATE/config.yml
  - .github/ISSUE_TEMPLATE/feature_request.yml
  - .github/PULL_REQUEST_TEMPLATE.md
  - .github/release.yml
  - .github/CODEOWNERS
  - CONTRIBUTING.md
  - CHANGELOG.md
findings:
  critical: 0
  warning: 4
  info: 4
  total: 8
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-06-09T18:32:40Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the Phase 04 repo-hygiene artifacts: two GitHub issue forms, issue
template config, PR template, release-notes categorization (`release.yml`),
CODEOWNERS, CONTRIBUTING.md, and the date-stamped CHANGELOG.md.

Verification performed against live repo state:

- All four YAML files parse cleanly (`yaml.safe_load`).
- All 12 labels referenced in `release.yml` and both issue forms exist in the
  repo (verified via `gh label list`): `bug`, `enhancement`, `feat`, `fix`,
  `changed`, `refactor`, `chore`, `security`, `documentation`, `docs`,
  `dependencies`, `skip-changelog`.
- GitHub Discussions are enabled (`has_discussions: true`), so the
  `config.yml` contact link is live; `SECURITY.md` exists, so the security
  policy URL resolves.
- All files referenced by relative links from CONTRIBUTING.md exist:
  `CODE_OF_CONDUCT.md`, `docs/adr/README.md`, `infra/docker-compose.yml`,
  `scripts/build_index.py`.
- CONTRIBUTING.md status-check table matches actual workflow job names
  (`pre-commit`, `test with Odoo`, `commitlint`, `gitleaks`, `bandit`,
  `dependency-review`).
- CODEOWNERS syntax is valid; `@Ezcareaga` is the repo owner; the "last
  matching rule wins" comment is semantically correct.

No critical issues. Four warnings — all are consistency defects that will
mislead contributors or silently break the documented release-notes flow —
plus four informational items.

## Warnings

### WR-01: PR template prescribes a test command that does not work in this project

**File:** `.github/PULL_REQUEST_TEMPLATE.md:18`
**Issue:** The checklist item reads `Tests pass locally (\`pytest addons/ -x\`)`.
This project's tests are Odoo `TransactionCase`tests that require a running
Odoo registry — CONTRIBUTING.md (lines 148–154) documents the actual runner:`docker compose ... exec odoo odoo --test-enable --stop-after-init ...`.
Plain `pytest addons/ -x`will fail at import time (no`odoo`package on the
host) or collect zero tests. There is no`pytest-odoo` setup anywhere in the
repo. Every contributor following the template will run a broken command, and
the checkbox becomes meaningless.
**Fix:** Align the checklist with CONTRIBUTING.md:

```markdown
- [ ] Tests pass locally (see [Testing](https://github.com/Ezcareaga/l10n-paraguay/blob/main/CONTRIBUTING.md#testing) — `docker compose -f infra/docker-compose.yml exec odoo odoo --test-enable ...`)
```

### WR-02: Relative Markdown link in PR template will 404 when rendered in the PR body

**File:** `.github/PULL_REQUEST_TEMPLATE.md:23`
**Issue:** `[Release process](CONTRIBUTING.md#release-process)` — GitHub
resolves relative links only inside rendered repository files (blobs/READMEs).
In issue and PR bodies, relative links are resolved against the current page
URL and produce broken links (e.g.
`https://github.com/Ezcareaga/l10n-paraguay/pull/CONTRIBUTING.md`). The PR
template renders inside the PR body, so this link is broken for every PR
opened against the repo.
**Fix:** Use an absolute URL:

```markdown
- [ ] CHANGELOG.md updated (if this is a release-worthy change — see [Release process](https://github.com/Ezcareaga/l10n-paraguay/blob/main/CONTRIBUTING.md#release-process))
```

### WR-03: release.yml "Dependencies" category is dead code — dependabot PRs are excluded by author

**File:** `.github/release.yml:13-14` and `:36-38`; `CONTRIBUTING.md:272`
**Issue:** `exclude.authors: [dependabot[bot]]` removes every dependabot PR
from auto-generated release notes. But the `dependencies` and
`github-actions` labels are applied (automatically) only by dependabot, and
CONTRIBUTING.md's label map documents `dependencies` → "Dependencies" →
"(dependabot PRs)". The two rules contradict each other: with the author
exclusion in place, no PR will ever land in the "Dependencies" category, and
the documented mapping in CONTRIBUTING.md is false. The maintainer following
that table will expect dependency bumps in release notes and never get them.
**Fix:** Pick one behavior and make both files agree. Either (a) intentionally
hide dependency noise — delete the "Dependencies" category from `release.yml`
and change the CONTRIBUTING.md row to say "(excluded — dependabot author
filter)"; or (b) show dependency bumps — remove `dependabot[bot]` from
`exclude.authors` and keep the category.

### WR-04: CONTRIBUTING.md commit-type list contradicts the enforced commitlint config and the PR template

**File:** `CONTRIBUTING.md:106`
**Issue:** The documented type list is
`feat, fix, docs, test, refactor, chore, perf, style`, but
`commitlint.config.mjs` (`type-enum`, lines 29–45) additionally allows
`build`, `ci`, and `revert` — and the PR template itself offers
"CI/build change (`ci:` / `build:`)" as a change type. A contributor reading
CONTRIBUTING.md will conclude `ci:` and `build:` are invalid and mislabel
CI changes as `chore:`, defeating the type taxonomy the same phase set up.
**Fix:** Update line 106 to the full enforced set:

```markdown
Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`, `style`, `build`, `ci`, `revert`.
```

## Info

### IN-01: Stale comment in release.yml — labels exist now

**File:** `.github/release.yml:6-8`
**Issue:** The comment says "The labels referenced here are created in a later
plan; the file is valid YAML regardless of whether the labels exist yet."
Plan 04-03 already created all referenced labels (verified live via
`gh label list`). The comment now misleads readers into thinking labels may
be missing.
**Fix:** Drop the second sentence or rewrite: "Labels are defined in the repo
(see plan 04-03)."

### IN-02: Release-process step 2 uses check names that don't match the table in the same file

**File:** `CONTRIBUTING.md:234-235`
**Issue:** Step 2 lists the 6 required checks as "(lint, test, security,
commitlint, pre-commit, Dependency Review)". The authoritative table at lines
128–136 (which matches the actual workflow job names) lists `pre-commit`,
`test with Odoo`, `commitlint`, `gitleaks`, `bandit`, `dependency-review`.
"lint" is not a check (it's part of `pre-commit`, already listed separately)
and "security" conflates `gitleaks` + `bandit`, so the parenthetical neither
counts nor names the checks correctly.
**Fix:** Replace the parenthetical with the real names:
"(`pre-commit`, `test with Odoo`, `commitlint`, `gitleaks`, `bandit`,
`dependency-review`)".

### IN-03: CHANGELOG.md missing `[Unreleased]` link definition

**File:** `CHANGELOG.md:7` and `:34`
**Issue:** `## [Unreleased]` uses reference-style brackets but only `[0.1.0]`
has a link definition at the bottom. Keep a Changelog convention (which line 5
claims to follow) defines an `[Unreleased]` compare link so readers can see
pending changes; without it the heading renders as literal bracketed text.
**Fix:** Add below line 34:

```markdown
[Unreleased]: https://github.com/Ezcareaga/l10n-paraguay/compare/v0.1.0...HEAD
```

### IN-04: PR template leaks internal planning identifier "DOC-09"

**File:** `.github/PULL_REQUEST_TEMPLATE.md:22`
**Issue:** "see DOC-09" references an internal GSD planning artifact ID that
has no meaning to external contributors and resolves to nothing in the public
repo (`.planning/` is internal context).
**Fix:** Replace with a link to the public ADR guide:
"see `docs/adr/README.md`".

---

_Reviewed: 2026-06-09T18:32:40Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
