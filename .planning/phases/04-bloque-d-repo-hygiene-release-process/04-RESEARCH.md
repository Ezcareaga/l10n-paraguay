# Phase 4: Bloque D — Repo hygiene + Release process - Research

**Researched:** 2026-06-09
**Domain:** GitHub repository meta-files — issue forms, release notes, CODEOWNERS, PR template, tag/release workflow
**Confidence:** HIGH (all schemas verified against live GitHub docs and current gh CLI manual)

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

**D-01 — Release process (REL-06):** Manual release, documented steps. NO semantic-release, NO
`.releaserc.json`. Write manual steps into CONTRIBUTING.md §"## Release process" (placeholder
at lines ~216-220). Four ordered steps: compile CHANGELOG entry → merge to main via PR (6 checks
green) → `git tag vX.Y.Z` + push → create GitHub Release from CHANGELOG.

**D-02 — Issue intake (REL-01):** GitHub Discussions enabled. Issue forms: `bug_report.yml` +
`feature_request.yml` ONLY. `question.yml` is deliberately omitted (Amendment A-01). `config.yml`:
`blank_issues_enabled: false`, `contact_links` → Discussions (Q&A) + SECURITY.md (security).
Outward-facing (enable Discussions, create labels) = `autonomous: false` / checkpoint.

**D-03 — Release notes (REL-04):** `release.yml` based on PR labels, manual labeling. Categories:
Added (`enhancement`/`feat`) / Fixed (`bug`/`fix`) / Changed / Security / Documentation (`documentation`/`docs`) /
Dependencies (`dependencies`). Exclude bot PRs (`dependabot[bot]`) and `skip-changelog` label.

**D-04 — Ownership (REL-02, REL-03):** `CODEOWNERS`: global `* @Ezcareaga` + commented-out area
stubs. `PULL_REQUEST_TEMPLATE.md`: checklist as soft reminders (not hard gates).

**D-05 — Release v0.1.0 (REL-05):** Full release (latest), manual notes from CHANGELOG `[0.1.0]`
entry. Tag at end of Phase 4, on `main`, after everything else merged. Date-stamp `[0.1.0] - Unreleased`
entry to actual date. Outward-facing = `autonomous: false` / checkpoint.

### Claude's Discretion

- Exact schema/fields of issue forms (labels, required fields, dropdowns, validations).
- Exact wording of PR template sections beyond the listed checklist items.
- Exact label names + full category map for `release.yml` (align to Conventional Commit + Keep a Changelog).
- Whether labels are pre-created via `gh` or documented as manual setup.
- Exact URLs for `contact_links` in `config.yml`.
- Order of plans/waves (natural: templates + CODEOWNERS + release.yml + PR template in parallel →
  CONTRIBUTING release section + CHANGELOG date-stamp → tag v0.1.0 last, dependent).

### Deferred Ideas (OUT OF SCOPE)

- semantic-release (`.releaserc.json` + release workflow) — after a few manual releases.
- Auto-labeler action — deferred with release automation.
- `question.yml` issue form — superseded by Discussions.
- Activating CODEOWNERS area stubs — when contributors join.
- Badge de version/release en README — optional post-v0.1.0.
- Cadencia releases v0.1.x+ / CHANGELOG automation — post-milestone.
- Phase 5 (Bloque E — multi-rubro) — separate phase.
- VPS deploy / Pre-Fase 3.

</user_constraints>

<phase_requirements>

## Phase Requirements

| ID     | Description                                                                                                                                                       | Research Support                         |
| ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------- |
| REL-01 | `.github/ISSUE_TEMPLATE/` with `bug_report.yml`, `feature_request.yml`, `config.yml` with Discussions links (Amendment A-01: `question.yml` deliberately omitted) | §Issue Forms Schema + §config.yml Schema |
| REL-02 | `.github/PULL_REQUEST_TEMPLATE.md` with checklist (tests, docs, ADR if applicable, Conventional Commits)                                                          | §PR Template Schema                      |
| REL-03 | `.github/CODEOWNERS` with `@Ezcareaga` global + commented area stubs                                                                                              | §CODEOWNERS Syntax                       |
| REL-04 | `.github/release.yml` with label→category mapping for auto-generated release notes                                                                                | §release.yml Schema                      |
| REL-05 | Release `v0.1.0` published: tag, full release (latest), manual notes from CHANGELOG `[0.1.0]`                                                                     | §Release v0.1.0 Workflow                 |
| REL-06 | "Release process" section in `CONTRIBUTING.md` — manual 4-step process documented                                                                                 | §CONTRIBUTING Release Section            |

</phase_requirements>

---

## Summary

Phase 4 is a config/docs phase — no application code. All 6 requirements are GitHub meta-file
operations. The phase creates 5 new files in `.github/` (2 issue forms + `config.yml` + `CODEOWNERS`

- `release.yml` + `PULL_REQUEST_TEMPLATE.md`) and edits 2 existing files (`CONTRIBUTING.md` placeholder
  replacement + `CHANGELOG.md` date-stamp). One outward-facing GitHub operation (enable Discussions +
  create labels) and one milestone operation (tag + publish `v0.1.0`) require maintainer checkpoint.

All GitHub YAML schemas were verified against current official documentation. Key findings:

1. **Issue forms labels caveat:** [VERIFIED] If a label does not already exist in the repo, GitHub
   silently skips auto-applying it — the issue is still created but without the label. Labels must
   be pre-created before issue forms can auto-apply them.

2. **`release.yml` reads from default branch only:** [VERIFIED] The `.github/release.yml` file is
   only read from the repository's default branch (`main`). This is not a limitation for this project
   (all work merges to `main`), but it means `release.yml` must be merged to `main` before `v0.1.0`
   tag is created for it to apply.

3. **`contact_links` URL must be HTTP/HTTPS:** [VERIFIED] File paths are not supported. Use
   `https://github.com/Ezcareaga/l10n-paraguay/security/policy` to link to `SECURITY.md` via GitHub's
   canonical security policy URL. GitHub renders `SECURITY.md` at this path automatically.

4. **Discussions can be enabled via `gh` CLI:** [VERIFIED] `gh repo edit --enable-discussions` is
   a confirmed flag in the current `gh` CLI. No web UI required.

5. **`--generate-notes` respects `release.yml` categories:** [VERIFIED] When running
   `gh release create --generate-notes`, GitHub reads `.github/release.yml` from `main` and applies
   the category configuration to organize PR entries. For `v0.1.0`, the plan uses `--notes-file`
   instead of `--generate-notes` (manual notes from CHANGELOG are richer for a foundation release).

6. **Default labels in the repo:** [VERIFIED via `gh label list`] The repo currently has only the 9
   GitHub defaults: `bug`, `documentation`, `duplicate`, `enhancement`, `good first issue`,
   `help wanted`, `invalid`, `question`, `wontfix`. The labels needed for `release.yml` and
   `dependabot.yml` (`dependencies`, `github-actions`, `feat`, `fix`, `docs`, `security`,
   `changed`, `skip-changelog`) do NOT yet exist and must be created.

**Primary recommendation:** Create all 5 new `.github/` files and edit CONTRIBUTING.md + CHANGELOG.md in
Wave 1 (parallelizable file creation) → create labels + enable Discussions (maintainer checkpoint) →
tag and publish `v0.1.0` (maintainer checkpoint, last step).

---

## Architectural Responsibility Map

| Capability                    | Primary Tier                        | Secondary Tier             | Rationale                                                 |
| ----------------------------- | ----------------------------------- | -------------------------- | --------------------------------------------------------- |
| Issue intake routing          | GitHub platform                     | —                          | `config.yml` + form YAML processed by GitHub UI           |
| PR ownership enforcement      | GitHub platform (branch protection) | `.github/CODEOWNERS`       | Branch protection reads CODEOWNERS at review request time |
| Release notes generation      | GitHub platform                     | `.github/release.yml`      | GitHub API reads `release.yml` from default branch        |
| Release tagging               | Git + GitHub CLI                    | —                          | `git tag` + `gh release create`                           |
| Release process documentation | `CONTRIBUTING.md`                   | —                          | Plain Markdown, no automation                             |
| Discussions routing           | GitHub platform                     | `config.yml` contact_links | Requires Discussions feature enabled on repo              |

---

## Standard Stack

### Core

No new external packages — this phase is entirely GitHub meta-file configuration.

| Tool     | Version             | Purpose                                                                     | Source                            |
| -------- | ------------------- | --------------------------------------------------------------------------- | --------------------------------- |
| `gh` CLI | current (installed) | `gh repo edit --enable-discussions`, `gh label create`, `gh release create` | [VERIFIED: cli.github.com/manual] |
| `git`    | current             | `git tag v0.1.0`, `git push origin v0.1.0`                                  | [VERIFIED]                        |

### No Package Legitimacy Audit Required

This phase installs zero external packages. The `## Package Legitimacy Audit` section is omitted.

---

## Architecture Patterns

### System Architecture Diagram

```
Contributor
    |
    v
[GitHub Issue / PR creation UI]
    |
    +---> ISSUE_TEMPLATE/bug_report.yml    --> Issue labeled 'bug'
    |     ISSUE_TEMPLATE/feature_request.yml --> Issue labeled 'enhancement'
    |     ISSUE_TEMPLATE/config.yml         --> blank_issues_enabled:false
    |                                            contact_links:
    |                                              Q&A → GitHub Discussions
    |                                              Security → /security/policy
    |
    +---> PULL_REQUEST_TEMPLATE.md          --> PR body pre-populated
    |
    +---> branch protection (existing)      --> requires CODEOWNERS review
              |
              v
          CODEOWNERS: * @Ezcareaga
              |
              v
         PR merged to main
              |
              v
         release.yml (reads PR labels)
              |
              v
         gh release create --tag v0.1.0 --notes-file CHANGELOG_EXTRACT.md
              |
              v
         GitHub Release v0.1.0 (latest, full)
```

### Recommended Project Structure

New files to create (all in `.github/`):

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml          # REL-01 — bug intake form
│   ├── feature_request.yml     # REL-01 — feature request form
│   └── config.yml              # REL-01 — blank_issues:false + contact_links
├── PULL_REQUEST_TEMPLATE.md    # REL-02 — PR checklist
├── CODEOWNERS                  # REL-03 — ownership
├── release.yml                 # REL-04 — release note categories
├── dependabot.yml              # (existing — untouched)
└── workflows/                  # (existing — untouched)
```

Edited files:

```
CONTRIBUTING.md     # REL-06 — replace §"Release process" placeholder (lines ~216-220)
CHANGELOG.md        # REL-05 — date-stamp [0.1.0] entry
```

---

## Pattern 1: GitHub Issue Form YAML Schema

[VERIFIED: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms]

**Top-level keys:**

| Key           | Required | Type         | Notes                                        |
| ------------- | -------- | ------------ | -------------------------------------------- |
| `name`        | yes      | string       | Unique; shown in template chooser            |
| `description` | yes      | string       | Subtitle in template chooser                 |
| `body`        | yes      | array        | Input elements                               |
| `title`       | no       | string       | Pre-fills issue title                        |
| `labels`      | no       | array/string | Auto-applied IF label already exists in repo |
| `assignees`   | no       | array/string | Auto-assigned                                |

**CRITICAL GOTCHA:** If a label listed in `labels` does not exist in the repository, GitHub
silently skips it — the issue is still created but without the label. Labels must be created
BEFORE issue forms are merged. This affects the plan wave order: create labels checkpoint must
precede or coincide with the form files being effective. [VERIFIED]

**Body element types:**

```yaml
# markdown — static display text (no user input)
- type: markdown
  attributes:
    value: "Explanatory text here."

# input — single-line text field
- type: input
  id: unique_id
  attributes:
    label: "Field label"
    description: "Helper text"
    placeholder: "e.g. example value"
  validations:
    required: true # boolean

# textarea — multi-line text
- type: textarea
  id: unique_id
  attributes:
    label: "Field label"
    description: "Helper text"
    placeholder: "Describe in detail..."
    value: "" # optional pre-fill
    render: shell # optional: syntax highlight (shell, python, etc.)
  validations:
    required: true

# dropdown
- type: dropdown
  id: unique_id
  attributes:
    label: "Field label"
    description: "Choose one"
    options:
      - "Option A"
      - "Option B"
    default: 0 # index of default option
    multiple: false # allow multi-select
  validations:
    required: true

# checkboxes
- type: checkboxes
  id: unique_id
  attributes:
    label: "Checklist"
    description: "Please confirm"
    options:
      - label: "I searched existing issues"
        required: true # individual option can be required
      - label: "I read CONTRIBUTING.md"
        required: false
```

**Skeleton — `bug_report.yml`:**

```yaml
name: Bug Report
description: Something is not working as expected.
title: "[Bug]: "
labels: ["bug"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for taking the time to fill out this bug report.
        Please search existing issues before submitting.

  - type: textarea
    id: description
    attributes:
      label: What happened?
      description: A clear and concise description of the bug.
      placeholder: Describe the unexpected behavior...
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected behavior
      placeholder: What did you expect to happen?
    validations:
      required: true

  - type: textarea
    id: steps
    attributes:
      label: Steps to reproduce
      placeholder: |
        1. Go to ...
        2. Click on ...
        3. See error
    validations:
      required: true

  - type: input
    id: odoo_version
    attributes:
      label: Odoo version
      placeholder: "18.0"
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Relevant log output
      description: Paste any Odoo server logs or tracebacks.
      render: shell

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: I searched existing issues for duplicates.
          required: true
        - label: I am using Odoo Community 18.0 (not Enterprise).
          required: true
```

**Skeleton — `feature_request.yml`:**

```yaml
name: Feature Request
description: Suggest a new feature or enhancement.
title: "[Feature]: "
labels: ["enhancement"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for your suggestion! Please describe the feature clearly.

  - type: textarea
    id: problem
    attributes:
      label: Problem or motivation
      description: What problem does this feature solve?
      placeholder: I'm frustrated when...
    validations:
      required: true

  - type: textarea
    id: solution
    attributes:
      label: Proposed solution
      description: How would you like this to work?
    validations:
      required: true

  - type: textarea
    id: alternatives
    attributes:
      label: Alternatives considered
      description: Any workarounds or other approaches you considered?

  - type: checkboxes
    id: checklist
    attributes:
      label: Checklist
      options:
        - label: I searched existing issues and discussions for similar requests.
          required: true
```

---

## Pattern 2: `.github/ISSUE_TEMPLATE/config.yml` Schema

[VERIFIED: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository]

```yaml
blank_issues_enabled: false
contact_links:
  - name: Q&A — GitHub Discussions
    url: https://github.com/Ezcareaga/l10n-paraguay/discussions/categories/q-a
    about: Ask questions, share tips, or discuss usage. Please open a Discussion instead of an issue for questions.
  - name: Report a Security Vulnerability
    url: https://github.com/Ezcareaga/l10n-paraguay/security/policy
    about: For security vulnerabilities, use our private reporting channel. Do NOT open a public issue.
```

**URL notes:**

- `contact_links[].url` MUST be a full HTTP/HTTPS URL. Relative paths are not supported. [VERIFIED]
- GitHub renders `SECURITY.md` at `https://github.com/{owner}/{repo}/security/policy` automatically.
  This is the canonical URL to link to the security policy. [VERIFIED via multiple GitHub repos]
- GitHub Discussions Q&A category URL: the `/discussions/categories/q-a` path exists once Discussions
  is enabled and a "Q&A" category is created. [ASSUMED — URL slug depends on category name chosen
  when enabling Discussions]. Fallback: use `https://github.com/Ezcareaga/l10n-paraguay/discussions`
  if Q&A category URL is not yet known.
- `blank_issues_enabled: false` forces all new issues through a template or contact_link. Verified
  behavior: the "New issue" button shows only the template chooser + contact_links list. [VERIFIED]

---

## Pattern 3: `.github/release.yml` Schema

[VERIFIED: docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes]

**Critical constraints:**

1. `release.yml` is read **only from the default branch** (`main`). Must be merged before first
   tagged release for it to apply. [VERIFIED]
2. Uses **PR labels** — not commit message prefixes. Labels are matched at the time the release
   is generated. [VERIFIED]
3. `labels: ['*']` is the catch-all — matches PRs not matched by previous categories. Must appear
   in at least one category if you want uncategorized PRs to show up. [VERIFIED]
4. Categories are processed in order; first matching category wins. [ASSUMED — docs show sequential
   processing but do not explicitly state "first match wins"]
5. `changelog.exclude.authors` accepts bot handles including `dependabot[bot]`. [VERIFIED]

**Schema:**

```yaml
changelog:
  exclude:
    labels:
      - skip-changelog
    authors:
      - dependabot[bot]
  categories:
    - title: title_string # required
      labels: # required — list of label strings; '*' is catch-all
        - label_name
      exclude: # optional per-category override
        labels:
          - label_name
        authors:
          - handle
```

**Concrete `release.yml` for this project** (aligned to Keep a Changelog + Conventional Commits):

```yaml
changelog:
  exclude:
    labels:
      - skip-changelog
    authors:
      - dependabot[bot]
  categories:
    - title: "Added"
      labels:
        - feat
        - enhancement
    - title: "Fixed"
      labels:
        - bug
        - fix
    - title: "Changed"
      labels:
        - changed
        - refactor
        - chore
    - title: "Security"
      labels:
        - security
    - title: "Documentation"
      labels:
        - documentation
        - docs
    - title: "Dependencies"
      labels:
        - dependencies
    - title: "Other"
      labels:
        - "*"
```

**Label inventory (what exists vs what needs creating):**

| Label            | In repo now?                                                             | Needed for                                            | Action                                                                                  |
| ---------------- | ------------------------------------------------------------------------ | ----------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `bug`            | YES (default)                                                            | `release.yml` Fixed, `bug_report.yml` auto-label      | none                                                                                    |
| `enhancement`    | YES (default)                                                            | `release.yml` Added, `feature_request.yml` auto-label | none                                                                                    |
| `documentation`  | YES (default)                                                            | `release.yml` Documentation                           | none                                                                                    |
| `dependencies`   | YES (dependabot.yml uses it, so it exists if dependabot PRs were opened) | `release.yml` Dependencies                            | **VERIFY** — dependabot adds the label on the PR but the label itself may not pre-exist |
| `feat`           | NO                                                                       | `release.yml` Added                                   | CREATE                                                                                  |
| `fix`            | NO                                                                       | `release.yml` Fixed                                   | CREATE                                                                                  |
| `changed`        | NO                                                                       | `release.yml` Changed                                 | CREATE                                                                                  |
| `refactor`       | NO                                                                       | `release.yml` Changed                                 | CREATE                                                                                  |
| `chore`          | NO                                                                       | `release.yml` Changed                                 | CREATE                                                                                  |
| `security`       | NO                                                                       | `release.yml` Security                                | CREATE                                                                                  |
| `docs`           | NO                                                                       | `release.yml` Documentation                           | CREATE                                                                                  |
| `skip-changelog` | NO                                                                       | `release.yml` exclude                                 | CREATE                                                                                  |
| `github-actions` | NO                                                                       | dependabot.yml labels it                              | CREATE                                                                                  |

**Note on `dependencies`:** Dependabot labels its PRs with `dependencies` (configured in
`dependabot.yml`). If dependabot has not yet opened any PRs, this label may not exist as a
pre-existing repo label. It must be explicitly created. [ASSUMED — verify via `gh label list`
before the labels-creation step]

**gh label create commands** (one per label, can be scripted):

```bash
gh label create "feat"          --description "New feature (Conventional Commit: feat:)" --color "0075ca"
gh label create "fix"           --description "Bug fix (Conventional Commit: fix:)"      --color "d73a4a"
gh label create "changed"       --description "Changed behavior or API"                  --color "e4e669"
gh label create "refactor"      --description "Code refactoring (no behavior change)"    --color "fef2c0"
gh label create "chore"         --description "Build process or maintenance"             --color "cfd3d7"
gh label create "security"      --description "Security fix or improvement"              --color "ee0701"
gh label create "docs"          --description "Documentation-only changes"               --color "0075ca"
gh label create "skip-changelog" --description "Exclude this PR from release notes"      --color "ffffff"
gh label create "dependencies"  --description "Dependency updates" --color "0366d6" --force
gh label create "github-actions" --description "GitHub Actions updates" --color "0366d6" --force
```

`--force` on `dependencies` and `github-actions` is safe: creates if absent, updates if exists.

---

## Pattern 4: `.github/CODEOWNERS` Syntax

[VERIFIED: docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners]

**Placement priority (GitHub searches in order, uses first found):**

1. `.github/CODEOWNERS`
2. `CODEOWNERS` (root)
3. `docs/CODEOWNERS`

For this project, use `.github/CODEOWNERS` (consistent with all other meta-files). [VERIFIED]

**Syntax rules:**

- Lines starting with `#` are always comments — cannot be escaped.
- Pattern matching follows gitignore rules (with exceptions: no `!` negation, no `[ ]` ranges).
- `* @Ezcareaga` = global fallback owner for any path not matched by a more specific rule.
- **Last matching rule wins** (not first). More specific rules below the global override it.
  Commented-out stubs are inert — they have zero effect until uncommented. [VERIFIED]
- Owner must be a GitHub username prefixed with `@` or a team `@org/team`.

**Concrete CODEOWNERS for this project:**

```
# Global owner — all files not matched by a more specific rule
* @Ezcareaga

# Uncomment area stubs as contributors join:
# /addons/l10n_py_base/   @Ezcareaga
# /addons/l10n_py_account/ @Ezcareaga
# /addons/l10n_py_edi/    @Ezcareaga
# /docs/                  @Ezcareaga
# /.github/               @Ezcareaga
```

**Solo-maintainer + branch protection behavior:** With `* @Ezcareaga` and branch protection
requiring code owner review, every PR automatically requests a review from `@Ezcareaga`. For a
solo maintainer, this means the maintainer must approve their own PR (if the PR is from a fork)
or can self-approve (if branch protection allows owner bypass). Verify branch protection settings:
if "Dismiss stale reviews" is on, a force-push after approval removes it. This is existing
behavior; CODEOWNERS does not change it. [VERIFIED behavior per docs]

---

## Pattern 5: `.github/PULL_REQUEST_TEMPLATE.md` Schema

[VERIFIED: docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository]

**Placement:** `.github/PULL_REQUEST_TEMPLATE.md` (preferred; keeps meta-files together). File name
is case-sensitive on Linux; GitHub accepts `PULL_REQUEST_TEMPLATE.md` (uppercase). [VERIFIED]

**Behavior:**

- Auto-populates the PR body field in the GitHub web UI when a PR is opened. [VERIFIED]
- Must be merged into the default branch to become active. Templates on feature branches are not
  served. [VERIFIED]
- The `gh pr create` CLI does NOT auto-populate the template in `--body` mode; it does open the
  template in `$EDITOR` if no `--body` is passed and stdin is a TTY. For automated PR creation
  (GitHub Actions), the template is not automatically applied — the body must be passed explicitly.
  [ASSUMED — not explicitly stated in docs; consistent with observed community behavior]

**Checklist items (per CONTEXT D-04 + CONTRIBUTING.md rules):**

```markdown
## Checklist

- [ ] Tests pass locally (`pytest addons/ -x`)
- [ ] Pre-commit hooks pass (`pre-commit run --all-files`)
- [ ] Conventional Commit message format followed (`feat:`, `fix:`, `docs:`, etc.)
- [ ] Docs updated if behavior changed (README, CONTRIBUTING, relevant `docs/`)
- [ ] If this changes architecture: a new ADR is included in this PR (`docs/adr/`)
- [ ] CHANGELOG.md updated (if this is a release-worthy change — see [Release process](CONTRIBUTING.md#release-process))

## Description

<!-- Describe the change and its motivation. Link related issues with "Closes #N". -->

## Type of change

- [ ] Bug fix (`fix:`)
- [ ] New feature (`feat:`)
- [ ] Documentation update (`docs:`)
- [ ] Refactor (`refactor:`)
- [ ] CI/build change (`ci:`/`build:`)
- [ ] Other (describe): \_\_\_
```

---

## Pattern 6: Release v0.1.0 Workflow

[VERIFIED: cli.github.com/manual/gh_release_create + gh label list output]

### Step-by-step command sequence

**Step 1 — All Phase 4 changes merged to `main`.**
(Prerequisite — not a command.)

**Step 2 — Date-stamp CHANGELOG.md `[0.1.0]` entry:**

Edit `CHANGELOG.md` line 9:

```
## [0.1.0] - Unreleased (see Phase 4 REL-05 for tag date)
```

Replace with:

```
## [0.1.0] - 2026-06-09
```

(Use actual date of tagging.)

**Step 3 — Commit the date-stamp:**

```bash
git add CHANGELOG.md
git commit -m "chore(release): date-stamp CHANGELOG [0.1.0] for v0.1.0 tag"
git push origin main
```

**Step 4 — Create the annotated tag:**

```bash
git tag -a v0.1.0 -m "Release v0.1.0 — foundation milestone (l10n_py_base + l10n_py_account + Pre-Fase 2)"
git push origin v0.1.0
```

**Step 5 — Extract CHANGELOG notes to a temp file:**

```bash
# Extract the [0.1.0] section from CHANGELOG.md for release notes body
# (manual edit or awk/sed to extract lines between ## [0.1.0] and the next ## heading)
```

**Step 6 — Publish the GitHub Release:**

```bash
gh release create v0.1.0 \
  --title "v0.1.0 — Foundation milestone" \
  --notes-file CHANGELOG_SECTION.md \
  --latest
```

**Flags explained:**

| Flag           | Value                               | Meaning                                                             |
| -------------- | ----------------------------------- | ------------------------------------------------------------------- |
| `--latest`     | (default true)                      | Marks as "Latest release" — the one shown on the repo homepage      |
| `--notes-file` | path to extracted CHANGELOG section | Manual notes; richer than `--generate-notes` for foundation release |
| `--prerelease` | NOT used                            | `v0.1.0` is a full release, not a pre-release                       |
| `--draft`      | NOT used                            | Publish immediately                                                 |

**On `--generate-notes` vs `--notes-file`:**

For `v0.1.0`, use `--notes-file` with the CHANGELOG `[0.1.0]` section. The `--generate-notes`
flag generates notes from PRs merged since the previous tag — since there is no previous tag, it
may include all PRs ever merged, which is noisy. Manual notes from CHANGELOG are the right choice
for the foundation release. [VERIFIED: `--generate-notes` uses PR history since previous tag]

**Note on `--generate-notes` + `release.yml` interaction:** For future releases after `v0.1.0`,
`gh release create --generate-notes` WILL read `.github/release.yml` and apply category grouping.
Manual notes can be prepended with `--notes "prepended text"` when combined with `--generate-notes`.
[VERIFIED: gh CLI manual]

---

## Pattern 7: Enabling GitHub Discussions + Creating Labels

### Enable Discussions

```bash
gh repo edit --enable-discussions
```

[VERIFIED: cli.github.com/manual/gh_repo_edit — `--enable-discussions` is an explicit flag]

**Current state (verified):** `hasDiscussionsEnabled: false` on `Ezcareaga/l10n-paraguay`.
This is an outward-facing action → `autonomous: false` / maintainer checkpoint.

**After enabling:** GitHub creates default discussion categories (Announcements, General, Ideas,
Polls, Q&A, Show and tell). The "Q&A" category is created by default; its URL slug will be
`/discussions/categories/q-a`. [ASSUMED — default categories may vary; verify after enabling]

### Create Required Labels

**Current state (verified via `gh label list`):** Only 9 default labels exist. The following
custom labels need to be created before the issue forms are effective:

```bash
# Labels needed for release.yml categories (non-default):
gh label create "feat"          --description "New feature (feat: commit type)"           --color "0075ca"
gh label create "fix"           --description "Bug fix (fix: commit type)"                --color "d73a4a"
gh label create "changed"       --description "Changed or improved behavior"              --color "e4e669"
gh label create "refactor"      --description "Code refactoring without behavior change"  --color "fef2c0"
gh label create "chore"         --description "Build, tooling, or maintenance task"       --color "cfd3d7"
gh label create "security"      --description "Security fix or hardening"                 --color "ee0701"
gh label create "docs"          --description "Documentation-only change"                 --color "0075ca"
gh label create "skip-changelog" --description "Exclude from auto-generated release notes" --color "ffffff"
# Labels used by dependabot.yml (ensure they exist):
gh label create "dependencies"  --description "Dependency updates"     --color "0366d6" --force
gh label create "github-actions" --description "GitHub Actions updates" --color "0366d6" --force
```

These 10 `gh label create` commands can be run as a script in a single step.

---

## Pattern 8: CONTRIBUTING.md "Release process" Section

The placeholder at lines ~216-220 of `CONTRIBUTING.md`:

```markdown
## Release process

> **Deferred to Phase 4 (REL-06).** The semantic-release vs manual-tag decision
> and the detailed release steps will be documented here once Phase 4 completes.
> For now, releases are tagged manually on `main` after CI passes.
```

Replace entirely with (keeping ENGLISH per D-01 Phase 3):

````markdown
## Release process

Releases are tagged manually on `main`. No automated release tooling is used
(semantic-release is deferred — see the project roadmap).

### Decision: manual releases

Rationale: single-maintainer project with early-stage history; automated release
tools (semantic-release, release-please) require a perfect Conventional Commits
history to generate clean changelogs. Starting manual allows iterating the process
before automating. Reassess after several releases or when contributor volume grows.

### Steps (for maintainer `@Ezcareaga`)

1. **Compile the CHANGELOG entry** — update `CHANGELOG.md`: move items from
   `[Unreleased]` into a new `[X.Y.Z]` section, add the release date, and verify
   all notable changes since the last release are documented (format: Keep a Changelog).

2. **Merge to `main` via PR** — open a PR titled `chore(release): vX.Y.Z`, get all
   6 status checks green (lint, test, security, commitlint, pre-commit, Dependency Review),
   then merge.

3. **Tag the release commit** — on the merged `main` commit:

   ```bash
   git pull origin main
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin vX.Y.Z
   ```

4. **Publish the GitHub Release** — extract the `[X.Y.Z]` section from `CHANGELOG.md`
   to a file, then:
   ```bash
   gh release create vX.Y.Z --title "vX.Y.Z" --notes-file CHANGELOG_SECTION.md --latest
   ```
   Or use `--generate-notes` for future releases to auto-categorize merged PRs by their
   labels (configured in `.github/release.yml`).

### PR label → release notes category map

Apply these labels to PRs before merging so release notes are auto-categorized:

| PR label         | release.yml category | Conventional Commit type |
| ---------------- | -------------------- | ------------------------ |
| `feat`           | Added                | `feat:`                  |
| `enhancement`    | Added                | `feat:`                  |
| `bug`            | Fixed                | `fix:`                   |
| `fix`            | Fixed                | `fix:`                   |
| `changed`        | Changed              | `refactor:`/`perf:`      |
| `refactor`       | Changed              | `refactor:`              |
| `chore`          | Changed              | `chore:`                 |
| `security`       | Security             | (any security fix)       |
| `documentation`  | Documentation        | `docs:`                  |
| `docs`           | Documentation        | `docs:`                  |
| `dependencies`   | Dependencies         | (dependabot PRs)         |
| `skip-changelog` | (excluded)           | (any)                    |
````

---

## Don't Hand-Roll

| Problem                            | Don't Build                           | Use Instead                                                  | Why                                                                        |
| ---------------------------------- | ------------------------------------- | ------------------------------------------------------------ | -------------------------------------------------------------------------- |
| Issue routing for security reports | Custom GitHub Action or webhook       | `config.yml` `contact_links`                                 | GitHub renders contact links natively in the issue chooser; no code needed |
| Release note generation            | Custom script parsing commit messages | `.github/release.yml` + `gh release create --generate-notes` | Native GitHub feature, reads PR labels, no maintenance overhead            |
| Enabling Discussions               | Clicking through UI manually in CI    | `gh repo edit --enable-discussions`                          | Single CLI command, scriptable, auditable in plan                          |
| Label creation                     | Manual web UI click per label         | `gh label create` script                                     | 10 labels × 3 clicks each = 30+ clicks; script is reproducible             |

**Key insight:** This entire phase is "configure GitHub's built-in features correctly." Every
hand-rolled solution here would be strictly worse — more code, more maintenance, less reliable.

---

## Common Pitfalls

### Pitfall 1: Labels not pre-existing when issue forms merge

**What goes wrong:** `bug_report.yml` has `labels: ["bug"]` — if the label `bug` did not exist,
GitHub would silently skip it. Here `bug` is a default label so it's fine. But `feat` and `fix`
are custom — if forms reference them and they don't exist, auto-labeling breaks silently.

**Why it happens:** GitHub does not create missing labels; it skips them without error.

**How to avoid:** The plan's maintainer checkpoint (create labels) must execute BEFORE the PR
with `.github/ISSUE_TEMPLATE/` files is effectively serving users. Labels can be created before
OR after the files are merged (GitHub checks label existence at issue-creation time, not at form
parse time). In practice: create labels as part of the same wave as file creation.

**Warning signs:** Open a test issue after deployment; the issue arrives without expected labels.

### Pitfall 2: `release.yml` file merged AFTER first tag

**What goes wrong:** If `v0.1.0` is tagged before `release.yml` is merged to `main`, the auto-
generated release notes will not be categorized. The file must be in `main` at tag time.

**Why it happens:** GitHub reads `release.yml` from the default branch at release creation time.

**How to avoid:** Wave ordering — merge all `.github/` files to `main` FIRST, then create the
tag. This is already the natural plan order (tag is the last step).

### Pitfall 3: `config.yml` `contact_links` URL is not HTTP/HTTPS

**What goes wrong:** Using a relative path like `SECURITY.md` or `./SECURITY.md` in a
`contact_link.url` field. GitHub will reject the config with a validation error.

**Why it happens:** `contact_links` are designed for external URLs, not in-repo file paths.

**How to avoid:** Use the canonical security policy URL:
`https://github.com/Ezcareaga/l10n-paraguay/security/policy`. GitHub renders `SECURITY.md` at
this URL automatically.

### Pitfall 4: Discussions Q&A URL in `config.yml` points to non-existent category

**What goes wrong:** `contact_links[0].url` points to `/discussions/categories/q-a` but
Discussions has not been enabled yet (or the Q&A category was renamed or deleted). Users click
the link and get a 404.

**Why it happens:** The URL is constructed before Discussions is enabled.

**How to avoid:** Enable Discussions FIRST (maintainer checkpoint), confirm the Q&A category
exists and its URL slug, THEN write `config.yml` with the correct URL. OR: use the generic
`/discussions` URL as a fallback until the specific category URL is confirmed.

**Mitigation:** Use `https://github.com/Ezcareaga/l10n-paraguay/discussions` (generic) until
Discussions is enabled and the Q&A slug is confirmed. Update to the specific category URL
after enabling.

### Pitfall 5: `CODEOWNERS` pattern specificity ordering

**What goes wrong:** Putting a specific rule BEFORE the global `* @Ezcareaga`. The last matching
rule wins, so the global `*` would override any specific rule placed before it.

**Why it happens:** CODEOWNERS uses last-match-wins, unlike gitignore (which uses first-match
for some contexts).

**How to avoid:** Always put `* @Ezcareaga` FIRST (most general), specific rules AFTER. The
commented stubs are already in this order in the pattern above.

### Pitfall 6: `v0.1.0` tag on a non-`main` commit

**What goes wrong:** Tagging a commit from a feature branch or the last commit before the
Phase 4 docs are merged. The release points to an incomplete state.

**Why it happens:** Rushing to create the tag before the PR is merged.

**How to avoid:** Verify `git log --oneline -1` shows the merge commit for Phase 4 PR before
tagging. The CONTEXT explicitly requires: "tag at end of Phase 4, on `main`, after REL-01..04
and Phase 3 docs are merged."

### Pitfall 7: PR template not auto-populating for `gh pr create`

**What goes wrong:** Developer uses `gh pr create --body ""` and expects the template to appear.
It does not — `gh` CLI uses the template only if no `--body` is passed AND the editor is
interactive.

**Why it happens:** PR templates are a GitHub web UI feature. CLI must handle it explicitly.

**How to avoid:** Document in `CONTRIBUTING.md` that `gh pr create` (without `--body`) opens
`$EDITOR` with the template pre-loaded, or use `--web` flag to open the browser-based PR form.
This is an informational note — the template file itself is correct.

---

## State of the Art

| Old Approach                                                      | Current Approach                                           | When Changed | Impact                                                                                                               |
| ----------------------------------------------------------------- | ---------------------------------------------------------- | ------------ | -------------------------------------------------------------------------------------------------------------------- |
| Markdown issue templates (`.github/ISSUE_TEMPLATE/bug_report.md`) | YAML issue forms (`.github/ISSUE_TEMPLATE/bug_report.yml`) | GitHub 2021  | Forms have structured fields, validations, required fields, dropdowns — much better UX                               |
| Manual release notes (always)                                     | `release.yml` auto-categorization via PR labels            | GitHub 2022  | Auto-generated notes still need `release.yml` for categories; pure auto-generation without config produces flat list |
| `gh repo edit` without `--enable-discussions`                     | `gh repo edit --enable-discussions` available              | gh CLI v2.x  | Can script Discussions enablement; no web UI required                                                                |

**Deprecated/outdated:**

- Markdown issue templates (`.md` files in `ISSUE_TEMPLATE/`): Still work but lack validation,
  required fields, structured fields. Use YAML forms instead.
- `release-drafter`: Popular alternative to `release.yml` that predates GitHub's native support.
  Not needed — GitHub native `release.yml` is sufficient for this project's needs.

---

## Validation Architecture

**Note:** This phase has no automated test infrastructure — it is configuration files. Validation
is human-smoke-test driven:

### Phase Requirements → Test Map

| Req ID | Behavior                                                                     | Test Type              | Verification Method                                             |
| ------ | ---------------------------------------------------------------------------- | ---------------------- | --------------------------------------------------------------- |
| REL-01 | Issue chooser shows 2 templates + 2 contact_links; blank issues blocked      | manual                 | Open new issue on GitHub; verify chooser UI                     |
| REL-02 | PR body auto-populates with checklist on web PR creation                     | manual                 | Open a PR via GitHub web UI; verify template appears            |
| REL-03 | PR on `main` auto-requests review from `@Ezcareaga`                          | manual                 | Open a test PR; verify review request                           |
| REL-04 | `release.yml` parses without error; categories appear in future releases     | automated (indirectly) | `gh release create --generate-notes --draft` test               |
| REL-05 | `gh release view v0.1.0` returns full release with notes                     | automated              | `gh release view v0.1.0` in verification step                   |
| REL-06 | `CONTRIBUTING.md §Release process` no longer contains "Deferred" placeholder | automated              | `grep -n "Deferred to Phase 4" CONTRIBUTING.md` returns nothing |

### YAML Linting (pre-commit)

The existing pre-commit hook includes `yamllint`. All new `.github/*.yml` files will be linted
on commit. The `yamllint` config must not reject the GitHub-specific fields. Verify:

```bash
pre-commit run yamllint --all-files
```

If yamllint raises on `release.yml` or issue form YAML (due to GitHub-specific keys), add a
`.yamllint.yml` exclusion for `.github/ISSUE_TEMPLATE/` (issue forms use GitHub-specific schema
not covered by standard YAML lint rules). [ASSUMED — verify after creating files]

---

## Environment Availability

| Dependency               | Required By                                        | Available                        | Version        | Fallback                                     |
| ------------------------ | -------------------------------------------------- | -------------------------------- | -------------- | -------------------------------------------- |
| `gh` CLI                 | Enable Discussions, create labels, publish release | verified via `gh label list` run | current        | Web UI (slower, same outcome)                |
| `git`                    | Create and push tag                                | yes                              | system         | none needed                                  |
| GitHub repo write access | All GitHub operations                              | yes (`@Ezcareaga` is owner)      | —              | —                                            |
| `yamllint`               | Pre-commit validation of new YAML files            | yes (pre-commit hook active)     | via pre-commit | none needed                                  |
| GitHub Discussions       | `config.yml` Q&A contact_link                      | NOT ENABLED (verified)           | —              | Use generic `/discussions` URL until enabled |

**Missing dependencies with fallback:**

- GitHub Discussions not yet enabled: `config.yml` can reference the generic
  `/discussions` URL until `gh repo edit --enable-discussions` is run.

---

## Security Domain

Security enforcement is enabled for this project. For this phase specifically:

### Applicable ASVS Categories

| ASVS Category         | Applies | Notes                                                        |
| --------------------- | ------- | ------------------------------------------------------------ |
| V2 Authentication     | No      | No auth logic in this phase                                  |
| V3 Session Management | No      | No session logic                                             |
| V4 Access Control     | Partial | CODEOWNERS enforces PR review ownership; no new code         |
| V5 Input Validation   | No      | GitHub validates issue form input; no custom validation code |
| V6 Cryptography       | No      | No crypto in this phase                                      |

### Known Threat Patterns

| Pattern                                | Concern                                          | Mitigation                                                                                                                       |
| -------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| Issue form label injection             | Attacker opens issue to add unexpected labels    | Labels auto-applied from `labels:` field are limited to what exists in the repo; no arbitrary label injection possible via forms |
| Public security reports via issue form | Sensitive vulnerability reported as public issue | `config.yml` `blank_issues_enabled: false` + contact_link to `/security/policy` routes reports to private channel                |
| Tag pushed to wrong commit             | `v0.1.0` points to non-`main` state              | Verification step: `git log v0.1.0 --oneline -1` must match `git log main --oneline -1` before publishing release                |

---

## Wave Decomposition Recommendation

The CONTEXT suggests (and this research confirms) the natural ordering:

**Wave 1 — File creation (parallelizable):**
All `.github/` files can be created in one PR. `CONTRIBUTING.md` placeholder replacement
can be in the same PR or a separate one (different concern; separating keeps atomic commits).

- Create `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create `.github/ISSUE_TEMPLATE/config.yml`
- Create `.github/CODEOWNERS`
- Create `.github/release.yml`
- Create `.github/PULL_REQUEST_TEMPLATE.md`
- Edit `CONTRIBUTING.md` §Release process (replace placeholder)

**Wave 2 — Maintainer checkpoint (outward-facing, `autonomous: false`):**

- `gh repo edit --enable-discussions` (enable Discussions)
- Confirm Q&A category URL slug; update `config.yml` if needed
- Run label creation script (10 `gh label create` commands)
- Verify `gh label list` matches expected labels

**Wave 3 — Release (dependent on Wave 1 + 2, `autonomous: false`):**

- Edit `CHANGELOG.md`: date-stamp `[0.1.0] - Unreleased` → `[0.1.0] - YYYY-MM-DD`
- Commit + push + open PR; merge with 6 checks green
- `git tag -a v0.1.0 -m "..."` + `git push origin v0.1.0`
- `gh release create v0.1.0 --title "..." --notes-file ... --latest`
- Verify with `gh release view v0.1.0`

**Wave 1 can be a single PR** (all `.github/` files + CONTRIBUTING.md edit). Wave 2 and Wave 3
are sequential human actions. Total work: 1 PR + 2 maintainer checkpoints.

---

## Assumptions Log

| #   | Claim                                                                                                                     | Section                 | Risk if Wrong                                                                                                                             |
| --- | ------------------------------------------------------------------------------------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| A1  | GitHub Discussions creates a "Q&A" category by default when enabled; URL slug is `/discussions/categories/q-a`            | Pattern 2 (config.yml)  | `config.yml` contact_link may point to wrong URL; mitigation: use generic `/discussions` URL in initial commit, update after enabling     |
| A2  | Categories in `release.yml` are first-match (sequential order matters, first wins)                                        | Pattern 3 (release.yml) | If last-match: category ordering in the file would be reversed; risk is low since labels are mutually exclusive in this config            |
| A3  | `gh pr create` without `--body` opens `$EDITOR` with PR template pre-loaded on interactive TTY                            | Pattern 5 (PR template) | If false: contributors using `gh pr create` would need `--web` flag for template; informational note in CONTRIBUTING.md                   |
| A4  | `yamllint` pre-commit hook may reject GitHub issue form YAML schema fields                                                | Validation Architecture | If true: add `.yamllint.yml` exclusion for `.github/ISSUE_TEMPLATE/`; test with `pre-commit run yamllint --all-files` after file creation |
| A5  | `dependencies` label may not pre-exist (dependabot labels are applied to PRs but the label itself may not be pre-created) | Pattern 3 (label table) | If dependabot has opened PRs, `dependencies` label exists; if not, label creation with `--force` is safe regardless                       |

---

## Open Questions

1. **Discussions Q&A category URL slug**

   - What we know: GitHub creates a "Q&A" category by default; its URL is typically `/discussions/categories/q-a`
   - What's unclear: The exact slug may differ if the category was renamed or if GitHub changed defaults
   - Recommendation: Use `https://github.com/Ezcareaga/l10n-paraguay/discussions` in the initial `config.yml` commit. After maintainer enables Discussions and confirms the Q&A category URL, update `config.yml` in a follow-up commit if needed.

2. **yamllint compatibility with GitHub issue form YAML**

   - What we know: The existing pre-commit config runs yamllint on all `.yml` files
   - What's unclear: Whether yamllint passes on GitHub issue form YAML (non-standard fields like `body[].type: checkboxes`)
   - Recommendation: Planner should include a verification step: `pre-commit run yamllint --all-files` after creating issue forms. If it fails, add `.yamllint.yml` with `ignore: .github/ISSUE_TEMPLATE/` as a hotfix task.

3. **CODEOWNERS enforcement vs. solo maintainer bypass**
   - What we know: Branch protection requires code owner review; `@Ezcareaga` is the global owner
   - What's unclear: Whether the current branch protection allows `@Ezcareaga` to self-approve a PR (owner bypass setting)
   - Recommendation: This is existing behavior from Phase 2 branch protection setup; the planner should note it as a known constraint, not a new issue.

---

## Sources

### Primary (HIGH confidence)

- `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms` — issue form YAML schema (all element types + validations)
- `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/configuring-issue-templates-for-your-repository` — config.yml schema (blank_issues_enabled, contact_links URL requirements)
- `https://docs.github.com/en/repositories/releasing-projects-on-github/automatically-generated-release-notes` — release.yml schema (categories, exclude, \* catch-all, main-branch-only constraint)
- `https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners` — CODEOWNERS syntax (placement, last-match-wins, solo maintainer behavior)
- `https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository` — PR template placement + auto-population behavior
- `https://cli.github.com/manual/gh_repo_edit` — `--enable-discussions` flag confirmed
- `https://cli.github.com/manual/gh_release_create` — `--notes-file`, `--generate-notes`, `--latest`, `--prerelease`, `--draft` flags
- `gh label list --repo Ezcareaga/l10n-paraguay` — live repo label state (9 defaults, no custom labels)
- `gh repo view Ezcareaga/l10n-paraguay --json hasDiscussionsEnabled` — Discussions status confirmed: false

### Secondary (MEDIUM confidence)

- `https://docs.github.com/en/issues/using-labels-and-milestones-to-track-work/managing-labels` — default labels list (bug, documentation, duplicate, enhancement, good first issue, help wanted, invalid, question, wontfix)
- `https://github.com/orgs/community/discussions/36757` — confirms `gh api --method PATCH ... -F has_discussions=true` works; `gh repo edit --enable-discussions` preferred
- WebSearch cross-reference: `--generate-notes` reads `release.yml` categories confirmed from multiple sources

### Tertiary (LOW confidence)

- Category ordering behavior (first-match vs last-match) — inferred from docs examples, not explicitly stated

---

## Metadata

**Confidence breakdown:**

- GitHub schemas (issue forms, release.yml, CODEOWNERS, config.yml): HIGH — verified against current official docs
- `gh` CLI flags (--enable-discussions, gh release create): HIGH — verified against current cli.github.com/manual
- Label inventory (what exists): HIGH — verified via live `gh label list`
- Discussions status: HIGH — verified via `gh repo view`
- Category ordering in release.yml: LOW — inferred, not explicitly documented
- Discussions Q&A URL slug: LOW — assumed from typical GitHub default, not verified post-enablement

**Research date:** 2026-06-09
**Valid until:** 2026-09-09 (90 days — GitHub config schemas are stable; `gh` CLI flags may change with major versions)
