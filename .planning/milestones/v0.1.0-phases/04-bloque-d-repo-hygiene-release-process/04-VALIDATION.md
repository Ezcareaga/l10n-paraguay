---
phase: 04
slug: bloque-d-repo-hygiene-release-process
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-06-09
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

**Phase nature:** This is a **configuration + docs** phase (`.github/*` YAML, CODEOWNERS,
CONTRIBUTING edit, release tag). There is **no application code and no unit-test surface**.
Validation is driven by (a) the existing `pre-commit` / `yamllint` gate for YAML correctness,
(b) `grep`/`gh` source-and-state assertions, and (c) human smoke tests of GitHub-rendered UI
(issue chooser, PR template, release page) that GitHub only renders server-side.

---

## Test Infrastructure

| Property               | Value                                                                               |
| ---------------------- | ----------------------------------------------------------------------------------- |
| **Framework**          | None for this phase. Closest automated gate = `pre-commit` (`yamllint`, OCA hooks). |
| **Config file**        | `.pre-commit-config.yaml` (existing)                                                |
| **Quick run command**  | `pre-commit run yamllint --all-files`                                               |
| **Full suite command** | `pre-commit run --all-files`                                                        |
| **Estimated runtime**  | ~30–60 seconds                                                                      |

_No Wave 0 test scaffolding is required — there is no code under test. The Odoo test suite
(97 green) is unchanged by this phase; a regression run is optional, not gating._

---

## Sampling Rate

- **After every file-creating task commit:** Run `pre-commit run yamllint --all-files` (catches broken `.github/*.yml`).
- **After the `.github/` wave:** Run `pre-commit run --all-files` (full hook set green).
- **Before `/gsd:verify-work`:** All `grep`/`gh` assertions below pass; pre-commit green on `main`.
- **Max feedback latency:** ~60 seconds (pre-commit). GitHub-UI smoke tests are post-merge / outward-facing.

---

## Per-Task Verification Map

> Threat refs map to the §Security gate (this phase ships no auth/secret-handling code; threats
> are supply-chain/process: a release.yml that leaks bot noise, a CODEOWNERS that mis-routes review).

| Task ID  | Plan | Wave | Requirement | Threat Ref | Secure Behavior                                                                   | Test Type     | Automated Command                                                                                                                                                     | File Exists | Status     |
| -------- | ---- | ---- | ----------- | ---------- | --------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------- | ---------- |
| 04-01-\* | 01   | 1    | REL-01      | —          | Blank issues blocked; questions/security routed off public issues                 | auto + manual | `test -f .github/ISSUE_TEMPLATE/bug_report.yml && test -f .github/ISSUE_TEMPLATE/feature_request.yml && test -f .github/ISSUE_TEMPLATE/config.yml` + open-issue smoke | ❌ W0       | ⬜ pending |
| 04-01-\* | 01   | 1    | REL-02      | —          | PR body auto-populates checklist reminders                                        | auto + manual | `test -f .github/PULL_REQUEST_TEMPLATE.md` + open-PR smoke                                                                                                            | ❌ W0       | ⬜ pending |
| 04-01-\* | 01   | 1    | REL-03      | —          | Global owner `@Ezcareaga` auto-requested on PRs to `main`                         | auto + manual | `grep -q '^\* @Ezcareaga' .github/CODEOWNERS` + open-PR smoke                                                                                                         | ❌ W0       | ⬜ pending |
| 04-01-\* | 01   | 1    | REL-04      | —          | `release.yml` valid; excludes bot PRs; labels→categories                          | auto          | `pre-commit run yamllint --files .github/release.yml` + `gh release create --draft --generate-notes` dry test                                                         | ❌ W0       | ⬜ pending |
| 04-0x-\* | 0x   | 2    | REL-06      | —          | CONTRIBUTING §Release process documents manual steps; no placeholder              | auto          | `! grep -q 'Deferred to Phase 4' CONTRIBUTING.md && grep -q '## Release process' CONTRIBUTING.md`                                                                     | ❌ W0       | ⬜ pending |
| 04-0x-\* | 0x   | 3    | REL-05      | —          | `v0.1.0` full release exists with CHANGELOG-sourced notes; CHANGELOG date-stamped | auto + manual | `gh release view v0.1.0` + `! grep -q '\[0.1.0\] - Unreleased' CHANGELOG.md`                                                                                          | ❌ W0       | ⬜ pending |

_Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky_
_"❌ W0" = artifact does not exist yet at plan time (created by the task itself), not a Wave-0 test stub._

---

## Wave 0 Requirements

_Not applicable. This phase creates no code and no test framework. "Existing infrastructure
(pre-commit / yamllint) covers all automatable phase assertions." The remaining assertions are
either `grep`/`gh` source-state checks (no framework needed) or GitHub-UI smoke tests (manual
by nature — GitHub renders the issue chooser / PR template / release page server-side)._

---

## Manual-Only Verifications

| Behavior                                                                                              | Requirement   | Why Manual                                                                                | Test Instructions                                                                                                                                                  |
| ----------------------------------------------------------------------------------------------------- | ------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Issue chooser shows exactly 2 templates + contact_links (Discussions, Security); blank issues blocked | REL-01        | GitHub renders the chooser server-side from `config.yml`; not observable from local files | After merge + Discussions enabled: open `https://github.com/Ezcareaga/l10n-paraguay/issues/new/choose`; verify 2 forms + 2 contact links + no "blank issue" option |
| PR body auto-populates checklist                                                                      | REL-02        | Auto-population is a GitHub web behavior                                                  | Open a test PR via web UI; confirm `PULL_REQUEST_TEMPLATE.md` content appears in the body                                                                          |
| PR to `main` auto-requests review from `@Ezcareaga`                                                   | REL-03        | CODEOWNERS review-request is server-side and depends on branch protection                 | Open a test PR to `main`; confirm `@Ezcareaga` is auto-added as reviewer                                                                                           |
| Discussions enabled; Q&A category exists                                                              | REL-01 (D-02) | Repo setting toggled via `gh`/UI; outward-facing maintainer action                        | `gh repo view --json hasDiscussionsEnabled` returns `true`; Q&A category present                                                                                   |
| Release labels exist in repo                                                                          | REL-04 (D-03) | Labels are repo state, created via `gh label create`; outward-facing                      | `gh label list` includes feat/fix/changed/security/docs/dependencies/skip-changelog                                                                                |
| `v0.1.0` published as full release (latest, not draft/pre-release)                                    | REL-05        | Tag + GitHub Release is an outward-facing publish action (`autonomous: false`)            | `gh release view v0.1.0 --json isLatest,isDraft,isPrerelease` → latest=true, draft=false, prerelease=false                                                         |

---

## Validation Sign-Off

- [x] All tasks have automated (`grep`/`gh`/`pre-commit`) verify OR are documented manual-only GitHub-UI smoke tests
- [x] Sampling continuity: pre-commit runs after every commit; no code path goes unverified
- [x] Wave 0 N/A — no code under test (documented above)
- [x] No watch-mode flags (pre-commit and gh are one-shot)
- [x] Feedback latency < 60s for automatable assertions
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-06-09 (config-phase validation contract — automatable assertions + documented manual GitHub-UI smoke tests)
