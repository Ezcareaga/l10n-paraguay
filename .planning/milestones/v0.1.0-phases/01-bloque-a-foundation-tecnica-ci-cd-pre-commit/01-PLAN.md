---
phase: 01-bloque-a-foundation-t-cnica-ci-cd-pre-commit
type: execute
planned: 2026-05-27
planner: gsd-planner
requirements: [CI-01, CI-02, CI-03, CI-04, CI-05, CI-06, CI-07, CI-08]
subagents:
  [
    voltagent-dev-exp:git-workflow-manager,
    python-pro,
    voltagent-qa-sec:code-reviewer,
  ]
autonomous: false # CI-07 + CI-08 require human-in-the-loop (gh auth + manual GitHub state verification)
---

# Phase 1 — PLAN: Bloque A — Foundation técnica (CI/CD + pre-commit)

**Planned:** 2026-05-27
**Planner:** gsd-planner
**Inputs read:**

- `.planning/PROJECT.md`
- `.planning/REQUIREMENTS.md` §"CI — Bloque A" (CI-01..08, including 2026-05-27 amendment to CI-01)
- `.planning/ROADMAP.md` §"Phase 1" (goal, internal sequencing locked, success criteria)
- `.planning/phases/01-.../01-CONTEXT.md` (D-01..D-16 + Addendum A-01..A-04)
- `.planning/phases/01-.../01-RESEARCH.md` (R-01..R-11, Deliverables)
- `docs/55_PRE_FASE_2_FOUNDATION.md` §"Bloque A"
- `CLAUDE.md` (repo) + `~/.claude/CLAUDE.md` (global)
- `infra/docker-compose.yml` (verified: container `l10n_py_odoo`, DB `l10n_py_dev`, mount `../addons → /mnt/extra-addons/l10n-paraguay`)
- `pyproject.toml` (`[tool.black]` `line-length=88, py311`; `[tool.isort]` `profile=black, sections=OCA`)
- `README.md` (current state: 3 placeholder badges — swap planned in P1-E)
- `references/l10n-brazil/.pylintrc` + `.pylintrc-mandatory` (Glob-verified present — source for P1-A)

**Subagents required:**

- `voltagent-dev-exp:git-workflow-manager` — pre-commit config, GitHub Actions workflow YAMLs, dependabot
- `python-pro` — `.coveragerc`, `commitlint.config.js`, `.yamllint`, pylint companion files
- `voltagent-qa-sec:code-reviewer` — review before each commit
- Orchestrator inline (no subagent) — CI-07 `gh api` branch protection call, CI-08 PR sanity workflow

**Override of global CLAUDE.md REGLA #1 ("nunca commit directo a `main`"):** Authorized by D-06 for P1-A, P1-B, P1-C only. After P1-D, all changes go through feature branches + PR (even before P1-H enables branch protection — building the pattern). P1-H + P1-I formalize the protection.

---

## Goal

Cualquier push o PR a este repo dispara automáticamente lint + tests y `main` está protegido contra merges sin checks verdes. End-state: `pre-commit run --all-files` corre limpio, branch protection en `main` rechaza push directo, commitlint rechaza mensajes no-conventional, dependabot abre PRs semanales.

## Success Criteria (literal from ROADMAP.md Phase 1)

1. `pre-commit run --all-files` corre limpio sobre todo el repo (hooks OCA: black, isort, flake8, pylint-odoo, oca-checks-odoo-module, oca-fix-manifest-version, codespell, yamllint).
2. Push directo a `main` (incluso desde la cuenta owner `@Ezcareaga`) es rechazado por GitHub con mensaje de branch protection.
3. Una PR de prueba (`chore: ci sanity check`) dispara workflows `lint.yml` + `test.yml` y ambos terminan verdes antes de poder mergearse.
4. Dependabot abre PRs automáticas semanales cuando hay updates de Python deps o GitHub Actions versions.
5. Commit message que viola Conventional Commits (ej. `fixed bug`) es rechazado por el GitHub Action de commitlint.

**Verification note for criterion 1:** REQ text lists `oca-fix-manifest-version` which does NOT exist in OCA tooling (RESEARCH R-01 + Addendum A-02/A-03). The plan implements the documented replacement: `oca-fix-manifest-website` + `pylint-odoo manifest-version-format` (C8106). Goal-backward audit (below) maps to this replacement.

---

## Manual steps before execution

These are user-required prerequisites — Claude cannot perform them:

1. **Codecov account + token** (required for P1-E test workflow).
   1. Visit `https://app.codecov.io/gh/Ezcareaga/l10n-paraguay` and sign in with GitHub OAuth.
   2. Copy "Repository Upload Token".
   3. GitHub: Settings → Secrets and variables → Actions → New repository secret → Name `CODECOV_TOKEN`, value from step 2.
2. **Verify `gh` CLI authenticated as `@Ezcareaga`** (required for P1-H branch protection).
   ```powershell
   gh auth status
   ```
   Expect: `Logged in to github.com as Ezcareaga`. If not: `gh auth login`.
3. **Free GitHub Actions minutes available** (private repo budget). Quick check: GitHub → Settings → Billing → Actions. Pre-Fase 2 estimated cost <100 min/mo (well within free tier 2000 min).

Mark each item `[done]` in PLAN execution log before starting the plan that depends on it.

---

## Plan Manifest

| Plan ID  | REQs                | Wave | Depends on         | Subagent                             | Files                                                                      | Commit msg                                                                                    |
| -------- | ------------------- | ---- | ------------------ | ------------------------------------ | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **P1-A** | CI-01               | 1    | —                  | git-workflow-manager + python-pro    | `.pre-commit-config.yaml`, `.pylintrc`, `.pylintrc-mandatory`, `.yamllint` | `chore(pre-commit): add OCA hand-rolled config`                                               |
| **P1-B** | CI-02.a             | 2    | P1-A               | git-workflow-manager + code-reviewer | (auto-fixes across repo from black+isort+prettier)                         | `chore(pre-commit): apply cosmetic baseline (black+isort+prettier)`                           |
| **P1-C** | CI-02.b             | 3    | P1-B               | git-workflow-manager + code-reviewer | (auto-fixes from codespell+oca-checks+yamllint+manifest-website)           | `chore(pre-commit): apply semantic baseline (codespell+oca-checks+yamllint+manifest-website)` |
| **P1-D** | CI-04               | 4    | P1-C               | git-workflow-manager                 | `.github/workflows/pre-commit.yml`                                         | `ci(lint): add pre-commit workflow` (via PR `ci/pre-commit-workflow`)                         |
| **P1-E** | CI-03 + P-01 + P-04 | 5    | P1-D               | git-workflow-manager + python-pro    | `.github/workflows/test.yml`, `.coveragerc`, `README.md` (badges only)     | `ci(test): add test workflow with codecov` (via PR `ci/test-workflow`)                        |
| **P1-F** | CI-05               | 5    | P1-D               | git-workflow-manager                 | `.github/dependabot.yml`                                                   | `ci(deps): add dependabot config` (via PR `ci/dependabot`)                                    |
| **P1-G** | CI-06               | 5    | P1-D               | git-workflow-manager + python-pro    | `.github/workflows/commitlint.yml`, `commitlint.config.js`                 | `ci(commitlint): add conventional commits validation` (via PR `ci/commitlint`)                |
| **P1-H** | CI-07               | 6    | P1-E ∧ P1-F ∧ P1-G | orchestrator inline                  | (no files — GitHub API state change)                                       | N/A (no commit)                                                                               |
| **P1-I** | CI-08 + P-03        | 7    | P1-H               | orchestrator inline                  | `CHANGES.rst` (new file at repo root)                                      | `chore: ci sanity check` (via PR `chore/ci-sanity-check`)                                     |

**Total commits planned:** 8 (P1-A, P1-B, P1-C, P1-D, P1-E, P1-F, P1-G, P1-I). P1-H produces no commit.

**Wave structure (locked by ROADMAP.md Phase 1 internal sequencing — NOT parallelizable):**

- Waves 1→3: P1-A → P1-B → P1-C (baseline trilogy, sequential, direct push to `main` per D-06)
- Wave 4: P1-D (lint workflow; enables CI to start running)
- Wave 5: P1-E ∥ P1-F ∥ P1-G (3 independent workflows/configs; can be opened as parallel PRs)
- Wave 6: P1-H (branch protection; needs all 3 status checks to have appeared at least once)
- Wave 7: P1-I (end-to-end sanity check; tests P1-H rules and P-03 commitlint behavior)

**Cross-cutting verification:** Hard test gate D-07 (97 tests verdes) runs BEFORE P1-B start, AFTER P1-B commit, AFTER P1-C commit. Command in Appendix B.

---

## Plans

### P1-A — Pre-commit config (CI-01)

**REQs:** CI-01 (amended 2026-05-27 — see RESEARCH R-01 + A-03)
**Wave:** 1
**Depends on:** —
**Subagent:** `voltagent-dev-exp:git-workflow-manager` (creates `.pre-commit-config.yaml`, `.yamllint`); `python-pro` (verifies pylint companion files alignment with `pyproject.toml`)
**Goal:** Create `.pre-commit-config.yaml` + 3 companion files (`.pylintrc`, `.pylintrc-mandatory`, `.yamllint`) such that `pre-commit run --all-files` runs and reports formatting/lint findings. Expected: non-zero exit (auto-fixes pending) but NO "hook not found" or "rev not found" errors.

**Files to create:**

- `.pre-commit-config.yaml` — literal content from Appendix A.1 (NO paraphrasing, NO improvisation).
- `.pylintrc` — copy from `references/l10n-brazil/.pylintrc` (Glob-verified present).
- `.pylintrc-mandatory` — copy from `references/l10n-brazil/.pylintrc-mandatory` (Glob-verified present).
- `.yamllint` — literal content from Appendix A.7.

**Tasks (atomic, sequential within the plan):**

1. **Verify pylint companion sources.**
   Subagent: `python-pro`.

   - Action: confirm `references/l10n-brazil/.pylintrc` and `.pylintrc-mandatory` exist and are non-empty. Read the first 5 and last 5 lines of each to sanity-check structure (must declare `[MESSAGES CONTROL]` or `[MASTER]` sections).
   - Verify: file size > 0, contains pylint config sections.
   - Done: both source files confirmed readable; if absent (regression vs Glob output), fallback is to render from `references/oca-addons-repo-template/src/.pylintrc.jinja` substituting `odoo_version=18.0` and `repo_slug=l10n-paraguay`.

2. **Create `.pre-commit-config.yaml`** at repo root with the literal content from Appendix A.1.
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action: write file verbatim. Do not modify pins. Do not add hooks. Do not remove the `exclude:` block.
   - Verify: `python -c "import yaml; yaml.safe_load(open('.pre-commit-config.yaml'))"` parses without error. Hook count: 10 entries under `repos:` (1 local fail-fast + 9 third-party + 1 local prettier).

3. **Create `.pylintrc` and `.pylintrc-mandatory`** at repo root by copying from `references/l10n-brazil/`.
   Subagent: `python-pro`.

   - Action: copy verbatim. No edits.
   - Verify: both files exist at repo root, size > 0, contain `[MASTER]` and `[MESSAGES CONTROL]` sections.

4. **Create `.yamllint`** at repo root with the literal content from Appendix A.7.
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action: write verbatim.
   - Verify: `python -c "import yaml; yaml.safe_load(open('.yamllint'))"` parses; contains `truthy.check-keys: false` (else GH Actions YAML fails).

5. **Install pre-commit hooks locally and smoke-run.**
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action:
     ```powershell
     pip install pre-commit
     pre-commit install
     pre-commit run --all-files
     ```
   - Capture the output and the resulting `git diff` to `/tmp/precommit-first-run.diff` (do NOT commit any auto-fixes — those go to P1-B and P1-C).
   - Verify: NO output containing `"hook not found"`, `"rev not found"`, `"InvalidRev"`, or `"InvalidManifestError"`. Exit code MAY be non-zero (expected — auto-fixes pending). At least black, isort, prettier should have reported changes (signal that they ran).

6. **Reset auto-fixes before committing.**
   Subagent: orchestrator inline.

   - Action: `git restore .` to revert any auto-fixes pre-commit may have written. Only `.pre-commit-config.yaml`, `.pylintrc`, `.pylintrc-mandatory`, `.yamllint`, and `.git/hooks/pre-commit` (managed by pre-commit, not committed) remain staged.
   - Verify: `git status` shows only the 4 new config files as untracked / staged.

7. **Code review.**
   Subagent: `voltagent-qa-sec:code-reviewer`.
   - Action: review the 4 new files against Appendix A.1, A.7, and the Brazil sources. Flag any drift.
   - Done: reviewer signs off; orchestrator stages and commits.

**Verification (goal-backward):**

- `.pre-commit-config.yaml` exists at repo root with the 10 hook repos listed in Appendix A.1.
- `.yamllint` exists with `truthy.check-keys: false`.
- `.pylintrc` + `.pylintrc-mandatory` exist, non-empty, contain `[MASTER]`.
- `pre-commit run --all-files` exits non-zero (auto-fixes pending — absorbed by P1-B, P1-C) BUT zero "hook not found" / "rev not found" errors.
- Commit `chore(pre-commit): add OCA hand-rolled config` lands on `main` (direct push per D-06).

**Risks / fallbacks:**

- **R-A-1:** `oca/maintainer-tools @ b89f767` rev fetch fails (rare — pinned commit, no garbage-collection on OCA repos). Fallback: try unpinned `master` (last resort, NOT recommended; record in BUGS_BACKLOG.md if used).
- **R-A-2:** Node 22.9.0 not available in the developer's local env. Mitigation: pre-commit will install Node into its own env. If that also fails: temporarily drop `default_language_version.node` to whatever is available (`node`); workflow CI step uses `actions/setup-node@v4 with node-version: "22.9.0"` regardless.
- **R-A-3:** `.pylintrc` content from Brazil includes Brazil-specific paths or module names. Mitigation: copy verbatim first (Brazil's pylintrc is generic OCA — no per-repo paths). If pylint errors during P1-C semantic baseline cite Brazil-specific patterns, surface to code-reviewer subagent and adjust.

**Commit:** `chore(pre-commit): add OCA hand-rolled config` (direct push to `main` per D-06).

---

### P1-B — Baseline cosmetic (CI-02 part 1)

**REQs:** CI-02 (part 1 of the 2-commit baseline per D-05)
**Wave:** 2
**Depends on:** P1-A
**Subagent:** `voltagent-dev-exp:git-workflow-manager` (drives hook execution); `voltagent-qa-sec:code-reviewer` (verifies diff is purely cosmetic, no logic change)
**Goal:** Apply auto-fixes from purely-cosmetic hooks (black + isort + prettier+plugin-xml) in a single commit. 97 tests verdes BEFORE the commit and AFTER the commit (D-07 hard gate).

**Tasks (atomic, sequential):**

1. **Pre-commit test gate (D-07 BEFORE).**
   Subagent: orchestrator inline (Docker exec).

   - Action: run Appendix B test command. Capture output.
   - Verify: `97 tests` reported, `0 failed, 0 errored`. If any rojo: `git reset --hard HEAD` and abort the plan, escalate to debugger.
   - Done: green; proceed.

2. **Run cosmetic hooks selectively.**
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action:
     ```powershell
     pre-commit run black --all-files
     pre-commit run isort --all-files
     pre-commit run prettier --all-files
     ```
   - These 3 hooks auto-write. Other hooks (codespell, oca-fix-manifest-website, yamllint, pylint, oca-checks, manifest-version-format, pre-commit-hooks/end-of-file-fixer/trailing-whitespace) are EXCLUDED from this commit — they belong to P1-C.
   - Verify: `git diff --stat` shows files touched ONLY by black/isort/prettier. Expected scope: `addons/l10n_py_base/**/*.py`, `addons/l10n_py_account/**/*.py`, `scripts/**/*.py`, possibly some XML view files (prettier+plugin-xml).
   - Caveat: `pre-commit run trailing-whitespace --all-files` and `end-of-file-fixer` will also auto-write if invoked; SKIP them here.

3. **Code review of cosmetic diff.**
   Subagent: `voltagent-qa-sec:code-reviewer`.

   - Action: review `git diff` against expectation: purely whitespace, line-length wrapping, import reordering, XML attribute formatting. ANY semantic change → escalate (likely a hook misconfiguration, not a real refactor).
   - Verify: reviewer sign-off.

4. **Stage and commit.**
   Subagent: orchestrator inline.

   - Action:
     ```powershell
     git add -A
     git commit -m "chore(pre-commit): apply cosmetic baseline (black+isort+prettier)"
     ```

5. **Post-commit test gate (D-07 AFTER).**
   Subagent: orchestrator inline.

   - Action: run Appendix B test command again. Same 97 tests verdes expected.
   - Verify: 97 tests verdes. If rojo: `git reset --hard HEAD~1` (drops the commit), debug, retry.

6. **Push to `main`.**
   Subagent: orchestrator inline.
   - Action: `git push origin main` (direct per D-06; CI-07 branch protection not yet active).
   - Verify: GitHub UI shows commit on `main`.

**Verification (goal-backward):**

- D-07 gate green BEFORE (97 tests verdes on `main` HEAD).
- Auto-fixes touched only `.py` and `.xml` files (cosmetic only).
- D-07 gate green AFTER (97 tests verdes on new HEAD).
- Commit `chore(pre-commit): apply cosmetic baseline (black+isort+prettier)` exists on `origin/main`.

**Risks / fallbacks:**

- **R-B-1:** Black/isort touches a file that breaks a test (rare, but unicode encoding edge cases exist). Mitigation: D-07 AFTER catches it; `git reset --hard HEAD~1` + diagnose with debugger subagent.
- **R-B-2:** Prettier reformats `__manifest__.py` in a way pylint-odoo rejects later. Mitigation: `__manifest__.py` is `.py`, prettier handles `.py` only if extension matches `files:` regex in Appendix A.1 — verify regex does NOT match `.py` (it doesn't; line 358 of A.1: `\.(css|htm|html|js|json|jsx|less|md|scss|toml|ts|xml|yaml|yml)$`). Confirmed safe.
- **R-B-3:** 100+ cosmetic changes overwhelm `git blame`. Accepted (per D-05 split rationale; that's why we have 2 commits, not 1).

**Commit:** `chore(pre-commit): apply cosmetic baseline (black+isort+prettier)` (direct push to `main` per D-06).

---

### P1-C — Baseline semantic (CI-02 part 2)

**REQs:** CI-02 (part 2 of the 2-commit baseline per D-05)
**Wave:** 3
**Depends on:** P1-B
**Subagent:** `voltagent-dev-exp:git-workflow-manager` + `voltagent-qa-sec:code-reviewer`
**Goal:** Apply auto-fixes from semantic/structural hooks (codespell + oca-fix-manifest-website + yamllint + oca-checks-odoo-module + manifest-version-format via pylint-odoo + pre-commit-hooks/end-of-file-fixer/trailing-whitespace). 97 tests verdes BEFORE and AFTER.

**Tasks (atomic, sequential):**

1. **Pre-commit test gate (D-07 BEFORE).** Same as P1-B step 1. 97 tests verdes required.

2. **Run semantic hooks.**
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action:
     ```powershell
     pre-commit run codespell --all-files
     pre-commit run oca-fix-manifest-website --all-files
     pre-commit run yamllint --all-files
     pre-commit run oca-checks-odoo-module --all-files
     pre-commit run oca-checks-po --all-files
     pre-commit run trailing-whitespace --all-files
     pre-commit run end-of-file-fixer --all-files
     pre-commit run pylint_odoo --all-files   # both invocations (informational + mandatory)
     ```
   - Auto-fix hooks (codespell, oca-fix-manifest-website, trailing-whitespace, end-of-file-fixer): write changes directly.
   - Read-only hooks (yamllint, oca-checks-\*, pylint_odoo mandatory): report findings. These should NOT need manual fixes in well-maintained Odoo modules. If they DO flag issues:
     - **Manifest-version-format (C8106):** current manifests `18.0.1.1.0` and `18.0.1.0.0` match the regex (RESEARCH R-01 confirmed). No fix needed.
     - **OCA module structural checks:** read each finding, fix or document as tech debt in `BUGS_BACKLOG.md` (do NOT silence with `# noqa` blindly).
     - **Yamllint warnings:** likely line-length > 120; either reflow or document the line in `.yamllint` ignore.
     - **Pylint optional (informational):** `--exit-zero` flag means it doesn't fail; review output for actionable hints but don't fix unless trivial.

3. **Code review of semantic diff.**
   Subagent: `voltagent-qa-sec:code-reviewer`.

   - Action: review every file changed. Distinguish:
     - Pure auto-fixes (whitespace/EOL/typos/website URL) → accept.
     - Manifest changes (oca-fix-manifest-website added/updated `"website"` key) → verify URL = `https://github.com/Ezcareaga/l10n-paraguay`.
     - Any code change beyond whitespace/strings → escalate (suggests a hook misbehavior; abort).

4. **Stage and commit.**
   Subagent: orchestrator inline.

   - Action:
     ```powershell
     git add -A
     git commit -m "chore(pre-commit): apply semantic baseline (codespell+oca-checks+yamllint+manifest-website)"
     ```

5. **Final pre-commit run — must be CLEAN.**
   Subagent: orchestrator inline.

   - Action: `pre-commit run --all-files`. After P1-B + P1-C, this MUST exit 0.
   - Verify: exit code 0; no auto-fixes applied; no errors reported.
   - This is the moment ROADMAP Success Criterion #1 becomes TRUE on `main`.

6. **Post-commit test gate (D-07 AFTER).** Run Appendix B. 97 tests verdes required.

7. **Push to `main`.**
   Subagent: orchestrator inline.
   - Action: `git push origin main`.
   - Verify: GitHub UI shows commit on `main`.

**Verification (goal-backward):**

- After P1-C commit, `pre-commit run --all-files` exits 0 with NO changes (the repo is in steady state — Success Criterion #1).
- 97 tests verdes maintained.
- `addons/l10n_py_base/__manifest__.py` and `l10n_py_account/__manifest__.py` have `"website": "https://github.com/Ezcareaga/l10n-paraguay"` (auto-added by oca-fix-manifest-website if missing/wrong).
- Commit `chore(pre-commit): apply semantic baseline (codespell+oca-checks+yamllint+manifest-website)` on `origin/main`.

**Risks / fallbacks:**

- **R-C-1:** `oca-checks-odoo-module` flags a structural issue (missing `__init__.py`, wrong manifest key, missing `readme/` folder). Mitigation: each finding handled case-by-case during step 2. If non-trivial, escalate (do not silence).
- **R-C-2:** Codespell flags Spanish-language tokens as typos (`afectacion`, `consumidor`, `timbrado`). Mitigation: add a `.codespellrc` companion file with `ignore-words-list = afectacion,exonerado,...` OR add `# codespell-ignore` inline comments. Document chosen approach in `BUGS_BACKLOG.md`.
- **R-C-3:** Pylint mandatory fails on a real issue (not a hook misconfiguration). Mitigation: actually fix the issue (do NOT bypass `pylint_odoo` mandatory; it's the floor).

**Commit:** `chore(pre-commit): apply semantic baseline (codespell+oca-checks+yamllint+manifest-website)` (direct push to `main` per D-06).

---

### P1-D — Lint workflow (CI-04)

**REQs:** CI-04
**Wave:** 4
**Depends on:** P1-C
**Subagent:** `voltagent-dev-exp:git-workflow-manager`
**Goal:** Activate GitHub Actions to run pre-commit on every PR + push to `main`. First workflow file; sets the pattern for P1-E/F/G.

**Branch model from this plan onwards:** Feature branch + PR. Branch protection not yet active, but discipline starts here.

**Files to create:**

- `.github/workflows/pre-commit.yml` — literal content from Appendix A.2.

**Tasks (atomic, sequential):**

1. **Create branch and file.**
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action:
     ```powershell
     git checkout main
     git pull origin main
     git checkout -b ci/pre-commit-workflow
     # Create .github/workflows/ directory if it doesn't exist
     # Write .github/workflows/pre-commit.yml verbatim from Appendix A.2
     ```
   - Verify: file exists, parses as valid YAML.

2. **Local pre-commit verify** (before pushing).
   Subagent: orchestrator inline.

   - Action: `pre-commit run --all-files`. MUST be clean (we just achieved this in P1-C; anything other than green is regression in this plan).

3. **Code review.**
   Subagent: `voltagent-qa-sec:code-reviewer`.

   - Action: verify Appendix A.2 content match exactly; confirm `jobs.pre-commit.name = pre-commit` (Wave 6 P1-H references this name).

4. **Commit + push + open PR.**
   Subagent: orchestrator inline.

   - Action:
     ```powershell
     git add .github/workflows/pre-commit.yml
     git commit -m "ci(lint): add pre-commit workflow"
     git push -u origin ci/pre-commit-workflow
     gh pr create --base main --title "ci(lint): add pre-commit workflow" --body "Adds the pre-commit GitHub Action that will validate every PR going forward. Implements CI-04."
     ```

5. **Wait for the workflow to run (first time) and self-verify.**
   Subagent: orchestrator inline.

   - Action: `gh pr checks <PR-number> --watch` or open PR in browser.
   - Verify: `pre-commit` job runs and exits green (since `main` already passed `pre-commit run --all-files` after P1-C).
   - Done: PR shows green `pre-commit` check.

6. **Merge PR.**
   Subagent: orchestrator inline.
   - Action: `gh pr merge --squash --delete-branch <PR-number>` (squash so the commit landing on `main` carries the conventional commit message `ci(lint): add pre-commit workflow`).
   - Verify: `main` now contains `.github/workflows/pre-commit.yml`; `ci/pre-commit-workflow` branch deleted.

**Verification (goal-backward):**

- `.github/workflows/pre-commit.yml` exists on `main`.
- PR ran the `pre-commit` job successfully (green check appears in GitHub Actions UI).
- Status check `pre-commit` now exists in GitHub's check registry → unlocks P1-H eligibility for this check.

**Risks / fallbacks:**

- **R-D-1:** First CI run is slow or times out (cold runner, pip cache miss). Mitigation: re-run job; the YAML caches `~/.cache/pre-commit` keyed by `.pre-commit-config.yaml` hash so subsequent runs are fast.
- **R-D-2:** `pre-commit run` in CI fails for a reason that didn't trigger locally (line-ending differences Windows→Linux). Mitigation: hook `mixed-line-ending --fix=lf` in A.1 enforces LF; this should not happen post-P1-C. If it does: re-run P1-C with `git config core.autocrlf input` set locally; debug subagent.

**Commit:** `ci(lint): add pre-commit workflow` (via squash-merge of PR `ci/pre-commit-workflow`).

---

### P1-E — Test workflow + coverage (CI-03) + P-01 + P-04

**REQs:** CI-03 (implements OCA-CI container + Codecov + tags); P-01 (smoke-verify `ODOO_TEST_TAGS`); P-04 (README badges)
**Wave:** 5 (parallel with P1-F + P1-G)
**Depends on:** P1-D
**Subagent:** `voltagent-dev-exp:git-workflow-manager` (workflow YAML); `python-pro` (`.coveragerc`)
**Goal:** Activate test workflow inside `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest` + PG12 service (per A-01). Codecov informational only (D-13). Append CI badges to README (per P-04).

**Files to create / modify:**

- `.github/workflows/test.yml` — literal content from Appendix A.3.
- `.coveragerc` — literal content from Appendix A.6.
- `README.md` — replace the "Status: Bootstrap" badge with CI + pre-commit + Coverage badges (Appendix A.8). The license badge stays. The Odoo version badge stays. The "Module status" table stays — Phase 3 DOC-01 owns the real rewrite.

**Manual prerequisite (re-check before starting):** `CODECOV_TOKEN` repo secret set (see Manual steps before execution #1).

**Tasks (atomic, sequential):**

1. **Verify `CODECOV_TOKEN` is set.**
   Subagent: orchestrator inline.

   - Action: `gh secret list | Select-String CODECOV_TOKEN`.
   - Verify: secret name appears. If missing → STOP, ask user to complete Manual Step #1.

2. **Create branch + write files.**
   Subagent: `voltagent-dev-exp:git-workflow-manager` (workflow + README badges); `python-pro` (`.coveragerc`).

   - Action:
     ```powershell
     git checkout main
     git pull
     git checkout -b ci/test-workflow
     ```
     Then create:
     - `.github/workflows/test.yml` — Appendix A.3 verbatim. **Verify the ENV var `ODOO_TEST_TAGS` line is present** (P-01 dependency).
     - `.coveragerc` — Appendix A.6 verbatim.
     - Edit `README.md`: replace lines 5 (`Status: Bootstrap` badge) with the 3-badge block from Appendix A.8 (CI + pre-commit + Coverage). License badge on line 3 unchanged.

3. **Add P-01 smoke-verification step inline to `test.yml`.**
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action: insert (immediately AFTER `oca_init_test_database`, BEFORE `oca_run_tests`) a step that echoes the env vars and lists installed addons. Already included in Appendix A.3 as the "Smoke-verify test tag env (P-01)" step — verify it's present in the file written.
   - Rationale: if `oca_run_tests` ignores `ODOO_TEST_TAGS`, we'll see it in the CI log of this PR and can fix BEFORE CI-07 enforces this check. RESEARCH R-03 flagged this as MEDIUM uncertainty.
   - Fallback path documented inline as a comment in Appendix A.3.

4. **Local pre-commit verify.**
   Subagent: orchestrator inline.

   - Action: `pre-commit run --all-files`. Must be clean (else fix and re-run; do not commit pre-commit failures).

5. **Code review.**
   Subagent: `voltagent-qa-sec:code-reviewer`.

   - Action: verify `.github/workflows/test.yml` matches Appendix A.3 (container, services, env vars, all 7 steps); `.coveragerc` matches Appendix A.6 (scope = `addons/l10n_py_base` + `l10n_py_account`); README badges match Appendix A.8 (3 new badges; license + Odoo unchanged).

6. **Commit + push + open PR.**
   Subagent: orchestrator inline.

   - Action:
     ```powershell
     git add .github/workflows/test.yml .coveragerc README.md
     git commit -m "ci(test): add test workflow with codecov"
     git push -u origin ci/test-workflow
     gh pr create --base main --title "ci(test): add test workflow with codecov" --body "..."
     ```
   - PR body: include the P-01 smoke-verification note ("This PR contains the first CI run of the test workflow. We expect `ODOO_TEST_TAGS` to be honored by `oca_run_tests`; if the smoke-verify step shows it's ignored, follow-up PR replaces `oca_run_tests` with explicit `odoo --test-enable` invocation").

7. **Watch first run + analyze smoke-verify output.**
   Subagent: orchestrator inline.

   - Action: `gh pr checks <PR-number> --watch`. Wait for `test (test with Odoo)` job.
   - Verify:
     - Job exits green.
     - `oca_install_addons` resolves `l10n_latam_base` and `l10n_latam_invoice_document` (or fails clearly with a missing-dep message).
     - **P-01 verification:** the "Smoke-verify test tag env" step output shows `ODOO_TEST_TAGS=/l10n_py,-l10n_py_external,-standard`.
     - `oca_run_tests` actually executes ≥97 tests (NOT all Odoo standard tests; if the count is much higher, the `-standard` tag is being ignored).
     - Codecov upload succeeds (or `fail_ci_if_error: false` masks a failure; verify the Codecov bot posts a comment OR the PR shows a Codecov status).
   - Done: green check. If smoke-verify reveals `ODOO_TEST_TAGS` ignored → open a follow-up PR with the fallback (explicit `odoo --test-enable --test-tags=...` invocation).

8. **Merge PR.**
   Subagent: orchestrator inline.
   - Action: `gh pr merge --squash --delete-branch <PR-number>`.

**Verification (goal-backward):**

- `.github/workflows/test.yml` exists on `main` with the OCA-CI container image and `ODOO_TEST_TAGS` env.
- `.coveragerc` exists on `main` with `source = addons/l10n_py_base, addons/l10n_py_account`.
- `README.md` has 3 new badges (CI, pre-commit, Coverage) replacing the placeholder "Status: Bootstrap".
- First CI run on `main` is green; subsequent push or PR also green.
- Status check name `test (test with Odoo)` registered in GitHub → eligible for P1-H.
- Codecov bot posts coverage % on the PR (informational; no gate).
- **P-04 satisfied:** 4 badges total (License + Odoo + CI + pre-commit + Coverage — actually 5 if Odoo stays; that's fine, README rewrite is Phase 3).

**Risks / fallbacks:**

- **R-E-1:** OCA-CI container fails to install our addons (missing `l10n_latam_base` from a sibling repo). Mitigation: add `requirements.txt` at repo root listing `git+https://github.com/OCA/l10n-latam.git@18.0#subdirectory=l10n_latam_base&egg=odoo-addon-l10n-latam-base` if the container's default resolution misses it. Document in a follow-up PR.
- **R-E-2:** `ODOO_TEST_TAGS` ignored by `oca_run_tests`. Fallback documented in Appendix A.3 as a code comment: replace step 6 of the workflow with `odoo --test-enable --stop-after-init -d ${PGDATABASE:-odoo} --test-tags=l10n_py,-l10n_py_external,-standard -i l10n_py_base,l10n_py_account --addons-path=...`. P-01 smoke-verify step exists precisely to detect this.
- **R-E-3:** Codecov upload fails (token wrong, network glitch). Mitigation: `fail_ci_if_error: false` means CI still passes; Codecov badge may show "unknown" until next push. Re-run job typically resolves.
- **R-E-4:** README badge URLs 404 because no workflow run yet on `main`. Mitigation: badges auto-resolve after the first workflow run. Accept the transient "no status" image until merge.

**Commit:** `ci(test): add test workflow with codecov` (via squash-merge of PR `ci/test-workflow`).

---

### P1-F — Dependabot (CI-05)

**REQs:** CI-05
**Wave:** 5 (parallel with P1-E + P1-G — no file conflicts)
**Depends on:** P1-D
**Subagent:** `voltagent-dev-exp:git-workflow-manager`
**Goal:** Activate Dependabot weekly grouped PRs for pip + github-actions ecosystems.

**Files to create:**

- `.github/dependabot.yml` — literal content from Appendix A.5.

**Tasks (atomic, sequential):**

1. **Create branch + file.**
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action:
     ```powershell
     git checkout main
     git pull
     git checkout -b ci/dependabot
     ```
     Write `.github/dependabot.yml` verbatim from Appendix A.5.
   - Verify: parses as valid YAML; contains 2 `updates` entries (pip + github-actions); both have `groups:` with one group each.

2. **Local pre-commit verify.** `pre-commit run --all-files` clean.

3. **Code review.** Subagent: `voltagent-qa-sec:code-reviewer`. Verify Appendix A.5 match.

4. **Commit + push + open PR.**

   ```powershell
   git add .github/dependabot.yml
   git commit -m "ci(deps): add dependabot config"
   git push -u origin ci/dependabot
   gh pr create --base main --title "ci(deps): add dependabot config" --body "Adds Dependabot for pip (pyproject.toml) and github-actions, weekly grouped PRs."
   ```

5. **Watch checks.** `pre-commit` + `test (test with Odoo)` + `commitlint` (once P1-G lands) must run green. Note: P1-F and P1-G can race; either one merging first means the other's PR will be re-evaluated against the updated `main`.

6. **Merge.** `gh pr merge --squash --delete-branch`.

**Verification (goal-backward):**

- `.github/dependabot.yml` on `main`.
- GitHub Settings → Insights → Dependency graph → Dependabot tab shows the 2 ecosystem configurations.
- **Deferred verification:** Dependabot opens its first weekly PR within 7 days (ROADMAP Success Criterion #4). Track in execution log; if absent at day 7, debug. Cannot block phase closure on this single async signal — the config presence + parser acceptance is the immediate criterion.

**Risks / fallbacks:**

- **R-F-1:** Dependabot rejects the YAML (rare; schema validated by GitHub). Mitigation: GitHub's Insights tab will show "Dependabot encountered a configuration error" with specifics. Fix in a follow-up PR.
- **R-F-2:** Weekly schedule timezone wrong. Mitigation: `America/Asuncion` per the literal in Appendix A.5 — verify this is a valid IANA tz (yes — it is).

**Commit:** `ci(deps): add dependabot config` (via squash-merge of PR `ci/dependabot`).

---

### P1-G — Commitlint (CI-06)

**REQs:** CI-06
**Wave:** 5 (parallel with P1-E + P1-F)
**Depends on:** P1-D
**Subagent:** `voltagent-dev-exp:git-workflow-manager` (workflow); `python-pro` (`commitlint.config.js` — JS but Python subagent picks up linting/style conventions)
**Goal:** Activate `wagoid/commitlint-github-action@v6` to validate PR commits + PR title against Conventional Commits config.

**Files to create:**

- `.github/workflows/commitlint.yml` — literal content from Appendix A.4.
- `commitlint.config.js` — literal content from Appendix A.5b (renumbered: A.5 is dependabot; commitlint config is A.4b — see Appendices).

**Tasks (atomic, sequential):**

1. **Create branch + files.**
   Subagent: `voltagent-dev-exp:git-workflow-manager`.

   - Action:
     ```powershell
     git checkout main
     git pull
     git checkout -b ci/commitlint
     ```
     Write `.github/workflows/commitlint.yml` (Appendix A.4) and `commitlint.config.js` (Appendix A.4b) verbatim.
   - Verify: both parse (YAML + JS).

2. **Local pre-commit verify.** `pre-commit run --all-files` clean (yamllint will validate the workflow; prettier may reformat the JS — re-run until stable).

3. **Code review.** Subagent: `voltagent-qa-sec:code-reviewer`.

   - Verify `commitlint.config.js`: `type-enum` includes 11 types per CONTEXT (feat, fix, refactor, test, docs, chore, style, perf, build, ci, revert); `scope-enum` is severity 1 (warning, not error — allows new scopes to land as warnings without blocking PRs).
   - Verify `.github/workflows/commitlint.yml`: 2 invocations of `wagoid/commitlint-github-action@v6` — one for commits, one for PR title (R-06 explicit).

4. **Commit + push + open PR.**

   ```powershell
   git add .github/workflows/commitlint.yml commitlint.config.js
   git commit -m "ci(commitlint): add conventional commits validation"
   git push -u origin ci/commitlint
   gh pr create --base main --title "ci(commitlint): add conventional commits validation" --body "..."
   ```

   - PR title MUST be conventional — the new commitlint will gate this very PR.

5. **Watch checks.** Expect: `pre-commit`, `test (test with Odoo)`, `commitlint` all green. **The `commitlint` job validates the commits IN this PR**, so the conventional commit message we just wrote must pass.

6. **Merge.** `gh pr merge --squash --delete-branch`.

**Verification (goal-backward):**

- `.github/workflows/commitlint.yml` on `main`.
- `commitlint.config.js` on `main`.
- The PR's own `commitlint` check ran green (proves the new workflow validates as expected on a well-formed commit).
- Status check name `commitlint` registered → eligible for P1-H.

**Risks / fallbacks:**

- **R-G-1:** `wagoid/commitlint-github-action@v6` does NOT validate PR title by default at v6 (RESEARCH R-06 flagged this as needing smoke-test). Mitigation: P-03 in P1-I explicitly tests with a non-conventional PR title; if it doesn't reject, replace the second action invocation with an explicit title-checker. Appendix A.4 documents the v6 behavior as confirmed-by-smoke-test only.
- **R-G-2:** `@commitlint/config-conventional` not auto-installed by wagoid action. Mitigation: wagoid action ships with `@commitlint/cli` and standard config; verify by reading the action's README at v6. Per RESEARCH it does.

**Commit:** `ci(commitlint): add conventional commits validation` (via squash-merge of PR `ci/commitlint`).

---

### P1-H — Branch protection (CI-07)

**REQs:** CI-07
**Wave:** 6
**Depends on:** P1-D ∧ P1-E ∧ P1-F ∧ P1-G (all 3 workflows must have run at least once on `main` to register status check names)
**Subagent:** **None — orchestrator inline.** Single `gh api` call requires owner credentials (`@Ezcareaga`); not a code task.
**Goal:** Lock `main`: PR required (even owner), 3 status checks must pass, conversation resolution required, no force push.

**Manual prerequisite (re-check before starting):**

- Verify all 3 status check names exist in GitHub Actions UI (Settings → Branches → Branch protection rules → Status check search). Names: `pre-commit`, `test (test with Odoo)`, `commitlint`. If any is missing → check that the corresponding plan (P1-D/E/G) actually ran and produced a successful workflow on `main`.

**Tasks (atomic, sequential):**

1. **Verify status check names registered.**
   Subagent: orchestrator inline.

   - Action:
     ```powershell
     gh api repos/Ezcareaga/l10n-paraguay/actions/runs --jq '.workflow_runs[].name' | Sort-Object -Unique
     ```
   - Verify: output contains `pre-commit`, `tests`, `commitlint` (workflow names). Then the matrix-expanded check name `test (test with Odoo)` will exist; spot-check by viewing the latest `tests` run in GitHub UI.

2. **Apply branch protection via `gh api`.**
   Subagent: orchestrator inline.

   - Action: Appendix A.9 (`gh api PUT repos/Ezcareaga/l10n-paraguay/branches/main/protection`). Paste the JSON via stdin heredoc.
   - Verify: command exits 0 (or returns JSON body of the protection rule).

3. **Verify protection state.**
   Subagent: orchestrator inline.

   - Action:
     ```powershell
     gh api repos/Ezcareaga/l10n-paraguay/branches/main/protection | ConvertFrom-Json | Select-Object -ExpandProperty required_status_checks | Select-Object -ExpandProperty checks
     ```
   - Verify: returns 3 entries with `context` values `pre-commit`, `test (test with Odoo)`, `commitlint`.

4. **Attempt direct push to `main` (negative test).**
   Subagent: orchestrator inline.
   - Action: create a trivial local edit, attempt `git push origin main`.
     ```powershell
     git checkout main
     git pull
     "# scratch" | Add-Content -Path .scratch
     git add .scratch
     git commit -m "test: trying to bypass protection"
     git push origin main
     # Expect: remote rejected with "protected branch hook declined"
     git reset --hard HEAD~1
     Remove-Item .scratch
     ```
   - Verify: push REJECTED. If accepted → protection misconfigured; re-apply Appendix A.9.

**Verification (goal-backward):**

- `gh api ... /branches/main/protection` returns the 3 required checks.
- `git push origin main` from a local clone is rejected.
- **ROADMAP Success Criterion #2 satisfied:** push directo a `main` rechazado por GitHub.

**Risks / fallbacks:**

- **R-H-1:** `gh api` returns `Check 'test (test with Odoo)' is not registered yet`. Mitigation: this means the workflow hasn't completed a run on `main` yet. Wait/re-trigger by pushing an empty commit on a branch + merging.
- **R-H-2:** `gh` not authenticated as owner (orgs-level perms missing for branch protection). Mitigation: re-auth with `gh auth login --scopes repo,admin:org` (admin:org required for protection rules).
- **R-H-3:** Force-push policy needs to remain disabled but contributors may complain. Accepted per CI-07 — no force-push to `main`, period.

**Commit:** **N/A** — no file change. Record outcome in `PLAN.md` execution log:

```
P1-H complete 2026-MM-DD: branch protection applied. 3 required checks: pre-commit, test (test with Odoo), commitlint. enforce_admins=true. Direct push rejected (verified).
```

---

### P1-I — Sanity PR (CI-08) + P-03 smoke test

**REQs:** CI-08; P-03 (smoke-verify commitlint rejects non-conventional PR title)
**Wave:** 7
**Depends on:** P1-H
**Subagent:** **None — orchestrator inline.** End-to-end verification, not a code task.
**Goal:** Verify the entire CI/CD edifice end-to-end via a deliberately trivial PR + a deliberately bad PR.

**Files to create:**

- `CHANGES.rst` at repo root — content per Appendix A.10 (1 line + 2-line header).

**Tasks (atomic, sequential):**

1. **Create branch + file.**
   Subagent: orchestrator inline.

   - Action:
     ```powershell
     git checkout main
     git pull
     git checkout -b chore/ci-sanity-check
     ```
     Write `CHANGES.rst` per Appendix A.10.

2. **Local pre-commit verify.** `pre-commit run --all-files` clean.

3. **Commit on branch.**

   - Action:
     ```powershell
     git add CHANGES.rst
     git commit -m "chore: ci sanity check"
     git push -u origin chore/ci-sanity-check
     ```

4. **Open PR #1 (the green path).**

   - Action:
     ```powershell
     gh pr create --base main --title "chore: ci sanity check" --body "End-to-end CI verification — see PLAN.md P1-I. Adds CHANGES.rst with a single line entry."
     ```
   - Verify: 3 status checks (`pre-commit`, `test (test with Odoo)`, `commitlint`) all run and turn GREEN. This is ROADMAP Success Criterion #3.

5. **Open PR #2 (the red path — P-03 smoke test).**

   - Action: from the same branch (or a parallel branch), open a SECOND PR with a deliberately non-conventional title:
     ```powershell
     git checkout -b chore/ci-sanity-bad-title
     "# scratch bad-title test" | Add-Content -Path CHANGES.rst
     git add CHANGES.rst
     git commit -m "fixed bug"   # non-conventional, but the commit will pass commitlint at the commit level only if commitlint is also checking commits, not just titles. wagoid v6 by default checks commits — so this MUST fail.
     git push -u origin chore/ci-sanity-bad-title
     gh pr create --base main --title "fixed bug" --body "P-03 smoke test — expect commitlint REJECT"
     ```
   - Verify: `commitlint` check RED.
   - **P-03 outcome:**
     - If RED → P-03 PASSES, R-G-1 / R-06 resolved positively. Close PR #2 with comment `closed: smoke test passed, commitlint correctly rejected non-conventional title/commit`.
     - If GREEN → P-03 FAILS, R-G-1 / R-06 was real. Follow up: update `.github/workflows/commitlint.yml` to explicitly check the PR title via the `wagoid` action's title-mode (or use `amannn/action-semantic-pull-request@v5`). Open a fix PR; re-test.

6. **Negative test: direct push to main rejected.**

   - Action (from yet another local branch):
     ```powershell
     git checkout main
     "# direct push attempt" | Add-Content -Path .scratch
     git add .scratch
     git commit -m "chore: trying direct push (expected REJECT)"
     git push origin main
     # Expect: remote rejected with "protected branch hook declined"
     git reset --hard HEAD~1
     Remove-Item .scratch
     ```
   - Verify: push REJECTED with branch protection message. This re-verifies P1-H from a fresh terminal context.

7. **Merge PR #1 (green path).**

   - Action: `gh pr merge --squash --delete-branch <PR1-number>`.
   - Verify: PR can ONLY merge once all 3 checks are green (P1-H enforces this).
   - Done: `main` contains `CHANGES.rst`.

8. **Record results.**
   Subagent: orchestrator inline.
   - Action: write outcome to `.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/01-EXECUTION_LOG.md`:
     ```
     P1-I executed 2026-MM-DD:
     - PR #1 (green path): merged. 3 checks green. CHANGES.rst on main.
     - PR #2 (red path, P-03): commitlint rejected as expected → P-03 PASS.
       (or: P-03 FAIL → fix workflow in follow-up PR #N, re-verified DATE.)
     - Direct push to main: REJECTED (branch protection working).
     - ROADMAP Success Criteria 1-5: ALL SATISFIED.
     ```

**Verification (goal-backward):**

- `CHANGES.rst` on `main` via squash-merged PR.
- 3 status checks ran green on the green-path PR.
- Non-conventional PR (`fixed bug`) was rejected → P-03 satisfied (ROADMAP Success Criterion #5).
- Direct push to `main` rejected (re-verifies ROADMAP Success Criterion #2).
- ROADMAP Success Criterion #3 satisfied (PR de prueba triggers lint+test, both green).

**Risks / fallbacks:**

- **R-I-1:** PR #2 (red path) commitlint passes despite bad title. Document, escalate, fix workflow. P-03 is a smoke-test gate — failure is informative, not blocking.
- **R-I-2:** PR #1 (green path) test job times out (~15-20 min for OCA-CI Odoo full install + tests). Mitigation: re-run; if persistent, increase `timeout-minutes` in `.github/workflows/test.yml` (default 360 should be ample).
- **R-I-3:** Branch protection blocks orchestrator from squash-merging because `enforce_admins: true`. Mitigation: that's by design. Use `gh pr merge --squash` (which respects protection rules and waits for checks); if Codecov bot leaves a "needs review" comment, resolve it ("conversation resolution required" per CI-07).

**Commit:** `chore: ci sanity check` (via squash-merge of PR `chore/ci-sanity-check` onto `main`).

---

## Threat Model (security_enforcement: enabled by default)

| Threat ID | Category               | Component                                                                                                                  | Disposition | Mitigation Plan                                                                                                                                                                                                                                                                                    |
| --------- | ---------------------- | -------------------------------------------------------------------------------------------------------------------------- | ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| T-01-01   | Tampering              | Pre-commit hook pins (`oca/maintainer-tools @ b89f767`, `OCA/odoo-pre-commit-hooks @ v0.0.33`, `OCA/pylint-odoo @ v9.1.3`) | mitigate    | Pin to full SHA / immutable tag; OCA repos do not force-push tags. Re-verify SHA at install (pre-commit caches by SHA).                                                                                                                                                                            |
| T-01-02   | Tampering              | `wagoid/commitlint-github-action @ v6` and `codecov/codecov-action @ v5` (3rd-party Actions)                               | accept      | Both are widely-used GHA marketplace actions (codecov is the canonical Codecov runner; wagoid is recommended by GitHub for commitlint). Major-version pin reduces but does not eliminate risk. Higher fidelity (commit SHA pin) is deferred to Pre-Fase 3 with the security baseline.              |
| T-01-03   | Disclosure             | `CODECOV_TOKEN` exposure                                                                                                   | mitigate    | Token stored as repo secret (encrypted at rest). Codecov action v5 reads `secrets.CODECOV_TOKEN` and does not echo to logs. Free Codecov token has limited scope (upload to one repo).                                                                                                             |
| T-01-04   | Repudiation            | Direct push to `main` bypassing checks                                                                                     | mitigate    | P1-H sets `enforce_admins: true` — even owner cannot bypass. CI-08 verifies via negative test.                                                                                                                                                                                                     |
| T-01-05   | Elevation of Privilege | `gh api` PUT call requires admin token                                                                                     | accept      | Owner of the repo runs the call once, then control devolves to branch protection rules. Token not stored anywhere; orchestrator runs interactively with the user's `gh auth`.                                                                                                                      |
| T-01-SC   | Tampering              | npm package installs from `wagoid/commitlint-github-action` (transitive `@commitlint/*` deps)                              | mitigate    | All installs happen inside the wagoid action container, ephemeral per run, never written to repo. **Package Legitimacy Gate:** wagoid and `@commitlint/config-conventional` are both VERIFIED — see Appendix C audit table. No `[ASSUMED]` / `[SUS]` / `[SLOP]` packages introduced by this phase. |

**Package Legitimacy Audit:** Appendix C below. No blocking checkpoints required — all packages are `[VERIFIED]` against canonical sources.

---

## Goal-backward audit

For each ROADMAP Success Criterion, the chain of plans/artifacts that achieves it:

| ROADMAP Success Criterion                        | Plans satisfying it                     | Specific artifact / event                                                                                                                                                                          |
| ------------------------------------------------ | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **#1** — `pre-commit run --all-files` runs clean | P1-A + P1-B + P1-C                      | After P1-C commit, `pre-commit run --all-files` exits 0 on `main` (step 5 of P1-C). REQ-amendment: `oca-fix-manifest-version` → `oca-fix-manifest-website` + `manifest-version-format`.            |
| **#2** — Push directo a `main` rechazado         | P1-H + P1-I step 6                      | `gh api PUT .../branches/main/protection` with `enforce_admins: true` + 3 required checks (P1-H). Negative test in P1-I step 6 reproduces the rejection.                                           |
| **#3** — PR de prueba dispara workflows verdes   | P1-D + P1-E + P1-F + P1-G → P1-I step 4 | PR #1 of P1-I triggers `pre-commit` + `test (test with Odoo)` + `commitlint`, all green. P1-D/E/G provide the workflows; P1-F adds the dependabot config which has no check (its impact is async). |
| **#4** — Dependabot weekly PRs                   | P1-F                                    | `.github/dependabot.yml` with 2 ecosystems × weekly schedule. First-PR-appears within 7 days verified async, post-phase.                                                                           |
| **#5** — Commit no-conventional rechazado        | P1-G + P1-I step 5 (P-03)               | `commitlint.config.js` enforces `type-enum` (error severity 2) + `wagoid/commitlint-github-action@v6` runs on PR. P-03 smoke test in P1-I PR #2 verifies.                                          |

**Pending registry (P-01..P-04) mapped to plans:**

| Pending                                                | Plan                      | Status path                                                                                             |
| ------------------------------------------------------ | ------------------------- | ------------------------------------------------------------------------------------------------------- |
| P-01 — smoke-verify `ODOO_TEST_TAGS` honored           | P1-E step 7               | Smoke step in `test.yml`; CI output reveals; fallback documented in Appendix A.3 comment.               |
| P-02 — `.pylintrc` / `.pylintrc-mandatory` not in repo | P1-A step 1 + 3           | Glob-verified Brazil sources; copy verbatim. Fallback: render from jinja.                               |
| P-03 — commitlint rejects bad PR title                 | P1-I step 5               | PR #2 with title `fixed bug` opened deliberately; expect `commitlint` RED. If GREEN → follow-up fix PR. |
| P-04 — Codecov badge in README                         | P1-E step 2 (README edit) | 3 new badges replace "Status: Bootstrap" stub. Real README rewrite deferred to Phase 3 DOC-01.          |

**No ROADMAP success criterion is unmapped.** No deferred item is silently re-introduced.

---

## Definition of Done — Phase 1

The phase is COMPLETE when ALL of the following are TRUE on `main`:

- [ ] `.pre-commit-config.yaml`, `.pylintrc`, `.pylintrc-mandatory`, `.yamllint` present at repo root.
- [ ] `.github/workflows/pre-commit.yml`, `test.yml`, `commitlint.yml` present.
- [ ] `.github/dependabot.yml` present.
- [ ] `commitlint.config.js` present at repo root.
- [ ] `.coveragerc` present at repo root.
- [ ] `CHANGES.rst` present at repo root (P1-I).
- [ ] README.md has CI + pre-commit + Coverage badges (P-04, not full rewrite).
- [ ] `pre-commit run --all-files` exits 0 (Success Criterion #1).
- [ ] `gh api repos/Ezcareaga/l10n-paraguay/branches/main/protection` returns the 3 required checks (Success Criterion #2 setup).
- [ ] Negative test: `git push origin main` REJECTED (Success Criterion #2 verified).
- [ ] PR #1 of P1-I: 3 checks GREEN, merged via squash (Success Criterion #3).
- [ ] PR #2 of P1-I (`fixed bug`): commitlint RED, closed (Success Criterion #5 verified via P-03).
- [ ] 97 tests verdes maintained throughout (D-07 gate respected at P1-B BEFORE/AFTER and P1-C BEFORE/AFTER).
- [ ] CODECOV_TOKEN set + first test workflow run posted coverage to Codecov.
- [ ] Async verification: Dependabot opens first PR within 7 days (Success Criterion #4, tracked in execution log post-phase).

---

## Appendices

### Appendix A — Literal artifact content

#### A.1 — `.pre-commit-config.yaml`

```yaml
# Pre-commit configuration for l10n-paraguay (Odoo 18.0 Community)
# Hand-rolled from references/l10n-brazil/.pre-commit-config.yaml (OCA 18.0)
# Pins sourced from OCA copier template @ v1.41 (odoo_version < 19 block).
# CI-01 hook set: black, isort, flake8, pylint-odoo, oca-checks-odoo-module,
# (oca-fix-manifest-version replaced with oca-fix-manifest-website +
#  manifest-version-format via pylint-odoo — see RESEARCH R-01), codespell,
# yamllint, prettier+plugin-xml (D-03 addition).

exclude: |
  (?x)
  # Vendored references — prohibido tocar (CLAUDE.md del repo)
  ^references/|
  # Catálogos DNIT canónicos generados por scripts/
  ^addons/[^/]+/data/.*\.csv$|
  # Formato custom GSD para PROJECT.md
  ^\.planning/PROJECT\.md$|
  # Files we don't want pre-commit to mess with
  \.svg$|
  ^README\.rst$|
  (LICENSE.*|COPYING.*)

default_language_version:
  python: python3.12
  node: "22.9.0"

repos:
  # -- Local fail-fast hooks ----------------------------------------------
  - repo: local
    hooks:
      - id: forbidden-files
        name: forbidden files
        entry: found forbidden files; remove them
        language: fail
        files: "\\.rej$"

  # -- OCA maintainer-tools (manifest website + utility) ------------------
  - repo: https://github.com/oca/maintainer-tools
    rev: b89f767503be6ab2b11e4f50a7557cb20066e667
    hooks:
      - id: oca-fix-manifest-website
        args: ["https://github.com/Ezcareaga/l10n-paraguay"]

  # -- OCA module structural checks (read-only) ---------------------------
  - repo: https://github.com/OCA/odoo-pre-commit-hooks
    rev: v0.0.33
    hooks:
      - id: oca-checks-odoo-module
      - id: oca-checks-po
        args: ["--disable=po-pretty-format"]

  # -- Black (reads [tool.black] from pyproject.toml) ---------------------
  - repo: https://github.com/psf/black
    rev: 22.8.0
    hooks:
      - id: black

  # -- isort (reads [tool.isort] from pyproject.toml) ---------------------
  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort
        name: isort except __init__.py
        args: ["--settings=."]
        exclude: /__init__\.py$

  # -- flake8 -------------------------------------------------------------
  - repo: https://github.com/PyCQA/flake8
    rev: 3.9.2
    hooks:
      - id: flake8
        additional_dependencies: ["flake8-bugbear==21.9.2"]

  # -- pylint-odoo (also enforces manifest-version-format C8106) ---------
  - repo: https://github.com/OCA/pylint-odoo
    rev: v9.1.3
    hooks:
      - id: pylint_odoo
        name: pylint with optional checks (informational)
        args:
          - --rcfile=.pylintrc
          - --exit-zero
        verbose: true
      - id: pylint_odoo
        name: pylint mandatory checks
        args: ["--rcfile=.pylintrc-mandatory"]

  # -- codespell (typos) --------------------------------------------------
  - repo: https://github.com/codespell-project/codespell
    rev: v2.4.2
    hooks:
      - id: codespell
        additional_dependencies: ["tomli"]

  # -- yamllint -----------------------------------------------------------
  - repo: https://github.com/adrienverge/yamllint
    rev: v1.38.0
    hooks:
      - id: yamllint
        args: ["-c=.yamllint"]

  # -- prettier (with plugin-xml) — D-03 addition -------------------------
  - repo: local
    hooks:
      - id: prettier
        name: prettier (with plugin-xml)
        entry: prettier
        args:
          - --write
          - --list-different
          - --ignore-unknown
        types: [text]
        files: \.(css|htm|html|js|json|jsx|less|md|scss|toml|ts|xml|yaml|yml)$
        language: node
        additional_dependencies:
          - "prettier@3.3.3"
          - "@prettier/plugin-xml@3.4.1"

  # -- Standard pre-commit-hooks (whitespace, EOL, syntax) ----------------
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
        exclude: /README\.rst$|\.pot?$
      - id: end-of-file-fixer
        exclude: /README\.rst$|\.pot?$
      - id: debug-statements
      - id: check-case-conflict
      - id: check-docstring-first
      - id: check-merge-conflict
        exclude: /README\.rst$|^docs/.*\.rst$
      - id: check-symlinks
      - id: check-xml
      - id: mixed-line-ending
        args: ["--fix=lf"]
```

#### A.2 — `.github/workflows/pre-commit.yml`

```yaml
name: pre-commit

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  pre-commit:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"
          cache-dependency-path: ".pre-commit-config.yaml"

      - name: Setup Node.js (for prettier)
        uses: actions/setup-node@v4
        with:
          node-version: "22.9.0"

      - name: Get python version hash
        run: echo "PY=$(python -VV | sha256sum | cut -d' ' -f1)" >> $GITHUB_ENV

      - uses: actions/cache@v4
        with:
          path: ~/.cache/pre-commit
          key: pre-commit|${{ env.PY }}|${{ hashFiles('.pre-commit-config.yaml') }}

      - name: Install pre-commit
        run: pip install pre-commit

      - name: Run pre-commit
        run: pre-commit run --all-files --show-diff-on-failure --color=always

      - name: Check that all files generated by pre-commit are in git
        run: |
          newfiles="$(git ls-files --others --exclude-from=.gitignore)"
          if [ "$newfiles" != "" ] ; then
            echo "Please check-in the following files:"
            echo "$newfiles"
            exit 1
          fi
```

#### A.3 — `.github/workflows/test.yml`

```yaml
name: tests

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-22.04
    container: ${{ matrix.container }}
    name: ${{ matrix.name }}
    strategy:
      fail-fast: false
      matrix:
        include:
          - container: ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest
            name: test with Odoo
    services:
      postgres:
        image: postgres:12
        env:
          POSTGRES_USER: odoo
          POSTGRES_PASSWORD: odoo
          POSTGRES_DB: odoo
        ports:
          - 5432:5432
    env:
      OCA_ENABLE_CHECKLOG_ODOO: "1"
      # Restrict test selection to l10n_py tests, skip externals + Odoo core.
      # P-01: smoke-verify in the dedicated step below that oca_run_tests honors this.
      # Fallback (if oca_run_tests ignores ODOO_TEST_TAGS): replace the
      # "Run tests" step with:
      #   odoo --test-enable --stop-after-init -d $PGDATABASE \
      #        --test-tags=l10n_py,-l10n_py_external,-standard \
      #        -i l10n_py_base,l10n_py_account \
      #        --addons-path=$ADDONS_PATH
      ODOO_TEST_TAGS: "/l10n_py,-l10n_py_external,-standard"
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - name: Install addons and dependencies
        run: oca_install_addons

      - name: Check licenses
        run: manifestoo -d . check-licenses

      - name: Check development status
        run: manifestoo -d . check-dev-status --default-dev-status=Beta
        continue-on-error: true # Beta is fine; do not block during Pre-Fase 2

      - name: Initialize test database
        run: oca_init_test_database

      - name: Smoke-verify test tag env (P-01)
        run: |
          echo "ODOO_TEST_TAGS=$ODOO_TEST_TAGS"
          echo "OCA_ENABLE_CHECKLOG_ODOO=$OCA_ENABLE_CHECKLOG_ODOO"
          echo "PGDATABASE=$PGDATABASE"
          echo "ADDONS_PATH=$ADDONS_PATH"
          which oca_run_tests
          # If oca_run_tests is a shell script, dump its first 50 lines for grep
          head -50 "$(which oca_run_tests)" || true

      - name: Run tests
        run: oca_run_tests

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v5
        if: ${{ always() }}
        with:
          token: ${{ secrets.CODECOV_TOKEN }}
          files: ./coverage.xml
          flags: unittests
          fail_ci_if_error: false
          verbose: true

      - name: Upload screenshots from JS tests (on failure)
        if: ${{ failure() }}
        uses: actions/upload-artifact@v4
        with:
          name: screenshots-${{ matrix.name }}
          path: /tmp/odoo_tests/${{ env.PGDATABASE }}
          if-no-files-found: ignore
```

#### A.4 — `.github/workflows/commitlint.yml`

```yaml
name: commitlint

on:
  pull_request:
    branches: [main]

permissions:
  contents: read
  pull-requests: read

jobs:
  commitlint:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0 # commitlint needs full history to diff PR commits

      - name: Validate PR commits
        uses: wagoid/commitlint-github-action@v6
        with:
          configFile: commitlint.config.js
          firstParent: false
          failOnWarnings: false
          helpURL: https://www.conventionalcommits.org

      - name: Validate PR title (Conventional Commits)
        uses: wagoid/commitlint-github-action@v6
        with:
          configFile: commitlint.config.js
          # wagoid at v6 validates PR title when github.event_name == 'pull_request'
          # P-03 will smoke-test this in P1-I PR #2 (title="fixed bug").
```

#### A.4b — `commitlint.config.js`

```javascript
// Conventional Commits config for l10n-paraguay.
// Consumed by .github/workflows/commitlint.yml (wagoid/commitlint-github-action@v6).
// Locally usable with `npx commitlint --from=origin/main`.

module.exports = {
  extends: ["@commitlint/config-conventional"],
  rules: {
    "type-enum": [
      2,
      "always",
      [
        "feat", // new feature
        "fix", // bug fix
        "refactor", // code change neither feat nor fix
        "test", // adding / fixing tests
        "docs", // documentation only
        "chore", // tooling, infra, no code change
        "style", // formatting, no semantic change
        "perf", // performance improvement
        "build", // build system / dependencies
        "ci", // CI/CD config
        "revert", // revert previous commit
      ],
    ],
    "scope-enum": [
      1, // 1 = warning (not error) — scope is optional
      "always",
      [
        "l10n_py_base",
        "l10n_py_account",
        "pre-commit",
        "ci",
        "docs",
        "", // allow empty scope
      ],
    ],
    "subject-case": [2, "never", ["upper-case", "pascal-case", "start-case"]],
    "header-max-length": [2, "always", 100],
    "body-leading-blank": [2, "always"],
    "footer-leading-blank": [2, "always"],
  },
};
```

#### A.5 — `.github/dependabot.yml`

```yaml
# Dependabot config for l10n-paraguay.
# Two ecosystems: pip (pyproject.toml dev deps) + github-actions (workflows).
# Weekly schedule, grouped PRs per ecosystem, no auto-merge (deferred to Pre-Fase 3).

version: 2

updates:
  # Python dev dependencies declared in pyproject.toml
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "06:00"
      timezone: "America/Asuncion"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "build"
      include: "scope"
    labels:
      - "dependencies"
      - "python"
    groups:
      python-deps:
        patterns:
          - "*"
        update-types:
          - "minor"
          - "patch"

  # GitHub Actions versions in .github/workflows/*.yml
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
      day: "monday"
      time: "06:00"
      timezone: "America/Asuncion"
    open-pull-requests-limit: 5
    commit-message:
      prefix: "ci"
      include: "scope"
    labels:
      - "dependencies"
      - "github-actions"
    groups:
      actions-deps:
        patterns:
          - "*"
```

#### A.6 — `.coveragerc`

```ini
# Coverage scope (D-16): addons/l10n_py_* only.
# Excludes tests, data files, manifest/init boilerplate, scripts and bin/.

[run]
branch = True
source =
    addons/l10n_py_base
    addons/l10n_py_account
    # Future addons (un-comment as added):
    # addons/l10n_py_edi
    # addons/l10n_py_reports
    # addons/l10n_py_pos
    # addons/l10n_py_withholding
omit =
    addons/*/tests/*
    addons/*/data/*
    addons/*/demo/*
    addons/*/__manifest__.py
    addons/*/__init__.py
    addons/*/migrations/*
    addons/*/wizards/*_views.xml
    scripts/*
    bin/*
parallel = True
relative_files = True

[report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    \.\.\.

[html]
directory = htmlcov
title = l10n-paraguay coverage report

[xml]
output = coverage.xml
```

#### A.7 — `.yamllint`

```yaml
extends: default
rules:
  line-length:
    max: 120
    level: warning
  truthy:
    check-keys: false # GitHub Actions uses `on:` key which yamllint flags as truthy
  document-start: disable
```

#### A.8 — README.md badge block (replaces line 5 `Status: Bootstrap` badge)

Edit `README.md` lines 3-5. The line 3 license badge stays. Replace line 4 (Odoo) + line 5 (Status: Bootstrap) with the 4-badge block below. Keep license + Odoo, add CI + pre-commit + Coverage. Final result lines 3-7:

```markdown
[![License: AGPL-3](https://img.shields.io/badge/license-AGPL--3-blue.svg)](http://www.gnu.org/licenses/agpl-3.0-standalone.html)
[![Odoo](https://img.shields.io/badge/Odoo-18.0%20Community-714B67.svg)](https://www.odoo.com/)
[![CI](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/test.yml)
[![pre-commit](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/pre-commit.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/pre-commit.yml)
[![Coverage](https://codecov.io/gh/Ezcareaga/l10n-paraguay/branch/main/graph/badge.svg)](https://codecov.io/gh/Ezcareaga/l10n-paraguay)
```

Do NOT touch any other line in README.md. Phase 3 DOC-01 owns the real rewrite.

#### A.9 — `gh api` snippet for CI-07 branch protection

```bash
gh api -X PUT repos/Ezcareaga/l10n-paraguay/branches/main/protection \
  -H "Accept: application/vnd.github+json" \
  --input - <<'JSON'
{
  "required_status_checks": {
    "strict": true,
    "checks": [
      {"context": "pre-commit"},
      {"context": "test (test with Odoo)"},
      {"context": "commitlint"}
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 0,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false
  },
  "restrictions": null,
  "required_linear_history": false,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": true
}
JSON
```

CI-07 explicit knobs translated:

- "PR required (incluso owner)" → `enforce_admins: true` + `required_approving_review_count: 0`.
- "status checks (lint + tests) must pass" → 3 `checks` listed.
- "conversation resolution required" → `required_conversation_resolution: true`.
- "no force push" → `allow_force_pushes: false`.

**Windows note:** PowerShell does not support `<<'JSON'` heredoc directly. Use a temp file:

```powershell
@'
{ ...JSON content... }
'@ | Set-Content -Encoding UTF8 -Path branch-protection.json
gh api -X PUT repos/Ezcareaga/l10n-paraguay/branches/main/protection `
  -H "Accept: application/vnd.github+json" `
  --input branch-protection.json
Remove-Item branch-protection.json
```

#### A.10 — `CHANGES.rst` (P1-I)

```rst
Changelog
=========

Unreleased
----------

- Initial CI sanity check (Phase 1 / chore: ci sanity check).
```

### Appendix B — Verification gate D-07 (test command)

**Container name (verified `infra/docker-compose.yml`):** `l10n_py_odoo`
**Dev DB:** `l10n_py_dev`
**Addons mount:** `/mnt/extra-addons/l10n-paraguay` (host `../addons` from `infra/`)

D-07 hard gate command (run from repo root):

```powershell
# 1. Ensure dev stack is up
docker compose -f infra/docker-compose.yml up -d

# 2. Wait for postgres healthy
docker compose -f infra/docker-compose.yml ps   # both services should be 'healthy' / 'running'

# 3. Drop + recreate a dedicated test DB so the 97-test suite runs from scratch
docker compose -f infra/docker-compose.yml exec -T postgres `
  psql -U odoo -d postgres -c "DROP DATABASE IF EXISTS l10n_py_test; CREATE DATABASE l10n_py_test OWNER odoo;"

# 4. Run the suite. -i installs the modules; --test-enable + --test-tags filter.
docker compose -f infra/docker-compose.yml exec -T odoo `
  odoo --stop-after-init `
       -d l10n_py_test `
       --addons-path=/mnt/extra-addons,/mnt/extra-addons/l10n-paraguay `
       --test-enable `
       --test-tags=l10n_py,-l10n_py_external,-standard `
       -i l10n_py_base,l10n_py_account `
       --without-demo=False
```

**Expected output line near the end:**

```
... Tests run: 97 ... 0 failed, 0 errored
```

(Exact format depends on Odoo's test reporter; alternative format: `INFO ... odoo.tests.runner: 97 tests run, 0 failures, 0 errors`.)

**If non-97 result count:** RESEARCH evidence (R-03) confirms 97 is the total at HEAD (l10n_py_base 23 + l10n_py_account 74). A different count means either:

- A test was added/removed since RESEARCH (re-baseline; update D-07 expected count in this PLAN).
- The `--test-tags` filter is missing tests (audit the `@tagged` decorators across `addons/*/tests/`).

**Exit code:** 0 on success. Non-zero on test failure or install error.

### Appendix C — Package Legitimacy Audit

Phase 1 introduces 3 third-party action references in GitHub Actions YAMLs + 1 npm-via-action transitive (commitlint via wagoid). No direct `pip install` of new packages and no `npm install` to repo root — wagoid + codecov actions handle their own deps inside ephemeral runners. Pre-commit hooks pull from canonical OCA & community repos at pinned SHAs / tags.

| Package                                     | Version pin                                           | Source URL                                          | Legitimacy     | Evidence                                                                                                                               |
| ------------------------------------------- | ----------------------------------------------------- | --------------------------------------------------- | -------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `oca/maintainer-tools`                      | `b89f767503be6ab2b11e4f50a7557cb20066e667` (full SHA) | `github.com/oca/maintainer-tools`                   | **[VERIFIED]** | OCA-owned org. Used by `references/l10n-brazil/.pre-commit-config.yaml:51`. RESEARCH R-01 + R-05 cite this exact SHA.                  |
| `OCA/odoo-pre-commit-hooks`                 | `v0.0.33`                                             | `github.com/OCA/odoo-pre-commit-hooks`              | **[VERIFIED]** | OCA-owned org. Canonical OCA pre-commit hooks repo. RESEARCH R-01 verified via WebFetch.                                               |
| `OCA/pylint-odoo`                           | `v9.1.3`                                              | `github.com/OCA/pylint-odoo`                        | **[VERIFIED]** | OCA-owned org. The de facto OCA Python linter for Odoo. RESEARCH R-01 verified.                                                        |
| `psf/black`                                 | `22.8.0`                                              | `github.com/psf/black`                              | **[VERIFIED]** | Python Software Foundation.                                                                                                            |
| `PyCQA/isort`                               | `5.12.0`                                              | `github.com/PyCQA/isort`                            | **[VERIFIED]** | PyCQA (Python Code Quality Authority).                                                                                                 |
| `PyCQA/flake8`                              | `3.9.2`                                               | `github.com/PyCQA/flake8`                           | **[VERIFIED]** | PyCQA.                                                                                                                                 |
| `pre-commit/pre-commit-hooks`               | `v4.6.0`                                              | `github.com/pre-commit/pre-commit-hooks`            | **[VERIFIED]** | Official pre-commit project.                                                                                                           |
| `codespell-project/codespell`               | `v2.4.2`                                              | `github.com/codespell-project/codespell`            | **[VERIFIED]** | Long-running typo-checker.                                                                                                             |
| `adrienverge/yamllint`                      | `v1.38.0`                                             | `github.com/adrienverge/yamllint`                   | **[VERIFIED]** | Canonical YAML linter.                                                                                                                 |
| `prettier`                                  | `3.3.3`                                               | `npmjs.com/package/prettier`                        | **[VERIFIED]** | Canonical JS/CSS/MD formatter.                                                                                                         |
| `@prettier/plugin-xml`                      | `3.4.1`                                               | `npmjs.com/package/@prettier/plugin-xml`            | **[VERIFIED]** | Official prettier plugin org `@prettier`.                                                                                              |
| `actions/checkout`                          | `v4`                                                  | `github.com/actions/checkout`                       | **[VERIFIED]** | GitHub-owned.                                                                                                                          |
| `actions/setup-python`                      | `v5`                                                  | `github.com/actions/setup-python`                   | **[VERIFIED]** | GitHub-owned.                                                                                                                          |
| `actions/setup-node`                        | `v4`                                                  | `github.com/actions/setup-node`                     | **[VERIFIED]** | GitHub-owned.                                                                                                                          |
| `actions/cache`                             | `v4`                                                  | `github.com/actions/cache`                          | **[VERIFIED]** | GitHub-owned.                                                                                                                          |
| `actions/upload-artifact`                   | `v4`                                                  | `github.com/actions/upload-artifact`                | **[VERIFIED]** | GitHub-owned.                                                                                                                          |
| `codecov/codecov-action`                    | `v5`                                                  | `github.com/codecov/codecov-action`                 | **[VERIFIED]** | Codecov-owned.                                                                                                                         |
| `wagoid/commitlint-github-action`           | `v6`                                                  | `github.com/wagoid/commitlint-github-action`        | **[VERIFIED]** | Long-running (since 2019), maintained, used by thousands of repos per GitHub network graph.                                            |
| `@commitlint/config-conventional`           | (transitive via wagoid)                               | `npmjs.com/package/@commitlint/config-conventional` | **[VERIFIED]** | Official commitlint org.                                                                                                               |
| `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest` | (latest tag)                                          | `github.com/OCA/oca-ci`                             | **[VERIFIED]** | OCA-owned. Used by all OCA 18.0 repos. Note: `:latest` is unpinned — accepted risk; defer SHA pinning to Pre-Fase 3 security baseline. |

**Result:** 0 `[ASSUMED]`, 0 `[SUS]`, 0 `[SLOP]`. No blocking checkpoints required. T-01-02 (Tampering on 3rd-party Actions) carries `accept` disposition documented in the threat model.

### Appendix D — Pendings registry (P-01..P-04 recap)

| Pending  | Description                                                                                    | Plan handling                                                                                                                                                                  | Smoke-test trigger                                   |
| -------- | ---------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------- |
| **P-01** | `oca_run_tests` may ignore `ODOO_TEST_TAGS` (RESEARCH R-03 medium uncertainty).                | P1-E step 7: dedicated "Smoke-verify test tag env" step in `test.yml` echoes the env vars and lists installed addons. Fallback YAML documented in Appendix A.3 inline comment. | First CI run of `test.yml` on PR `ci/test-workflow`. |
| **P-02** | `.pylintrc` / `.pylintrc-mandatory` not present in repo (RESEARCH R-05 dependency).            | P1-A step 1: verify Brazil sources exist (Glob-confirmed). Step 3: copy verbatim. Fallback: render jinja templates.                                                            | Pre-commit run during P1-A step 5.                   |
| **P-03** | `wagoid/commitlint-github-action@v6` PR-title validation behavior unconfirmed (RESEARCH R-06). | P1-I step 5: deliberate PR #2 with non-conventional title `fixed bug`. Expect REJECT.                                                                                          | P1-I step 5 PR opening.                              |
| **P-04** | Codecov badge + 3 other CI badges in README (RESEARCH R-11; CONTEXT § Decisions D-13/D-14).    | P1-E step 2: edit `README.md` lines 3-7 per Appendix A.8. NOT a full README rewrite — Phase 3 DOC-01 owns that.                                                                | Visual inspection of `README.md` post-P1-E merge.    |

### Appendix E — Branch model for this phase

| Plan | Branch                                                                               | Push policy                                                                                                                    |
| ---- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------ |
| P1-A | (work on `main` directly)                                                            | Direct push per D-06 (branch protection not yet active).                                                                       |
| P1-B | (work on `main` directly)                                                            | Direct push per D-06.                                                                                                          |
| P1-C | (work on `main` directly)                                                            | Direct push per D-06. After this point: `pre-commit run --all-files` is clean on `main`; ROADMAP Success Criterion #1 is TRUE. |
| P1-D | `ci/pre-commit-workflow` → PR → squash-merge                                         | First PR-based plan. Branch protection not yet enforced but discipline starts.                                                 |
| P1-E | `ci/test-workflow` → PR → squash-merge                                               | PR-based.                                                                                                                      |
| P1-F | `ci/dependabot` → PR → squash-merge                                                  | PR-based. Can race with P1-E/G; no file conflicts.                                                                             |
| P1-G | `ci/commitlint` → PR → squash-merge                                                  | PR-based. The first PR to validate commits against the new workflow is this PR itself.                                         |
| P1-H | (no commit)                                                                          | Single `gh api` PUT call.                                                                                                      |
| P1-I | `chore/ci-sanity-check` (+ `chore/ci-sanity-bad-title` for P-03) → PR → squash-merge | PR-based. Tests P1-H rules.                                                                                                    |

All non-merge commits follow Conventional Commits per global CLAUDE.md and per CI-06 enforcement (starting at P1-G).

---

_PLAN created 2026-05-27. Confidence: HIGH (RESEARCH provided literal artifacts; all decisions locked or addended; only known uncertainty is `ODOO_TEST_TAGS` honored by `oca_run_tests`, mitigated by P-01 smoke-verify step)._
