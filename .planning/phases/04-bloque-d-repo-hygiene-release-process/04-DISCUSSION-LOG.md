# Phase 4: Bloque D — Repo hygiene + Release process - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-09
**Phase:** 4-bloque-d-repo-hygiene-release-process
**Areas discussed:** Release automation (REL-06), Issue intake (REL-01), release.yml categorization (REL-04), CODEOWNERS + PR checklist (REL-02/03), v0.1.0 mechanics (REL-05)

---

## Release automation (REL-06)

| Option                          | Description                                                                                                                                              | Selected |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Manual, documented steps        | Write manual release process in CONTRIBUTING.md (compile CHANGELOG → tag → GitHub release). No .releaserc/workflow. Matches on-disk default + risk note. | ✓        |
| Manual + release-drafter action | Manual publish, but release-drafter auto-drafts notes from merged PRs.                                                                                   |          |
| semantic-release now            | .releaserc.json + workflow; fully automated version+tag+notes from Conventional Commits.                                                                 |          |

**User's choice:** Manual, documented steps.
**Notes:** Honors "cero ceremonia 1-maintainer" + REQUIREMENTS risk note ("empezar manual, automatizar después"). Coincide con el default ya en disco. → D-01. Automation deferred.

---

## Issue intake (REL-01)

| Option                                    | Description                                                                                         | Selected |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------- | -------- |
| Enable Discussions, route questions there | Turn on Discussions; config.yml contact_link → Discussions; DROP question.yml (keep bug + feature). | ✓        |
| 3 forms + Discussions links               | Keep all 3 forms (bug/feature/question) + link Discussions. Matches REL-01 literal.                 |          |
| No Discussions yet, 3 forms only          | No Discussions; config.yml links SECURITY.md/email; keep 3 forms.                                   |          |

**User's choice:** Enable Discussions, route questions there.
**Notes:** Deliberate divergence from REL-01 literal (omits question.yml) → AMENDMENT A-01 in CONTEXT.md. Enabling Discussions is an owner GitHub-settings action. → D-02.

---

## release.yml categorization basis (REL-04)

| Option                       | Description                                                                                | Selected |
| ---------------------------- | ------------------------------------------------------------------------------------------ | -------- |
| Label-based, manual labeling | Categories keyed on PR labels; apply labels by hand. Document label→category map.          | ✓        |
| Label-based + auto-labeler   | actions/labeler or PR-title→label maps Conventional Commit titles to labels automatically. |          |
| Minimal release.yml          | Exclude bots + catch-all categories; rely on Conventional Commit PR titles.                |          |

**User's choice:** Label-based, manual labeling.
**Notes:** GitHub release.yml groups by labels, not commit prefixes. Manual labeling now; auto-labeler deferred with release automation. → D-03.

---

## CODEOWNERS + PR checklist depth (REL-02/03)

| Option                           | Description                                                                                             | Selected |
| -------------------------------- | ------------------------------------------------------------------------------------------------------- | -------- |
| Reminders + commented stubs      | @Ezcareaga global + COMMENTED future-area lines; PR checklist as self-check reminders.                  | ✓        |
| Explicit gates + commented stubs | Same CODEOWNERS; PR checklist worded as required merge criteria (≥80% cov, pre-commit, ADR-in-same-PR). |          |
| Minimal                          | @Ezcareaga global only (no stubs); short checklist.                                                     |          |

**User's choice:** Reminders + commented stubs.
**Notes:** Branch protection already enforces CI gates; checklist need not duplicate. Low friction for solo maintainer. → D-04.

---

## v0.1.0 scope + commit (REL-05)

| Option                                 | Description                                                                                                                                | Selected |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| Foundation milestone state             | Tag at END of Phase 4 on main, after REL-01..04 + Phase 3 docs merged. Notes = modules + Pre-Fase 2 foundation. Matches CHANGELOG [0.1.0]. | ✓        |
| Strict post-Fase-1 only                | Notes describe only 2 modules + 97 tests; trim CHANGELOG entry.                                                                            |          |
| Defer tag until milestone fully closed | Wait until Phase 5 merges before tagging.                                                                                                  |          |

**User's choice:** Foundation milestone state.
**Notes:** Resolves the ROADMAP ("post-Fase 1") vs CHANGELOG [0.1.0] (includes foundation) tension toward the richer, accurate snapshot. → D-05.

---

## v0.1.0 release type (REL-05)

| Option                     | Description                                                                                        | Selected |
| -------------------------- | -------------------------------------------------------------------------------------------------- | -------- |
| Full release, manual notes | Publish v0.1.0 as normal (latest) release; hand-written notes from CHANGELOG. Real rollback point. | ✓        |
| Draft first, then publish  | Create as draft for review, publish after eyeball.                                                 |          |
| Pre-release (v0.1.0)       | Mark as pre-release to signal "foundation, pre-EDI".                                               |          |

**User's choice:** Full release, manual notes.
**Notes:** Not pre-release/draft — it's a real post-Fase-1 rollback point. Date-stamp CHANGELOG [0.1.0] at tag time. → D-05.

---

## Claude's Discretion

- Schema/fields of issue forms beyond bug + feature.
- Exact PR template wording/sections.
- Exact label names + full release.yml category map.
- Exact wording/structure of the CONTRIBUTING "Release process" section.
- Whether GitHub labels are pre-created via `gh` or documented as manual setup.
- config.yml exact contact_link URLs.
- Plan/wave ordering (templates + CODEOWNERS + release.yml + PR template in parallel → CONTRIBUTING release section + CHANGELOG date-stamp → v0.1.0 tag last).
- README version/release badge (optional after v0.1.0).

## Deferred Ideas

- semantic-release (.releaserc.json + release workflow) — automate later.
- Auto-labeler action — deferred with release automation.
- question.yml issue form — superseded by Discussions (A-01).
- CODEOWNERS area activation (uncomment stubs) — when contributors join.
- README version badge — optional after v0.1.0.
- v0.1.x+ release cadence / CHANGELOG maintenance automation — post-milestone.
- Phase 5 (multi-rubro) — separate phase.
- Real deploy (VPS) + docs/71 validation — Pre-Fase 3.
