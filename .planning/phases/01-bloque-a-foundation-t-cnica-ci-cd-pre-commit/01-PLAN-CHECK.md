# Phase 1 — PLAN CHECK (goal-backward audit)

**Audited:** 2026-05-27
**Auditor:** gsd-plan-checker
**Target:** `.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/01-PLAN.md`
**Inputs verified against:** ROADMAP.md Phase 1 Success Criteria + REQUIREMENTS.md CI-01..08 + CONTEXT.md (D-01..D-16 + Addendum A-01..A-04) + RESEARCH.md (R-01..R-11) + `infra/docker-compose.yml` + `pyproject.toml`

---

## Verdict

**Overall: FLAG-MINOR**

PLAN.md is well-structured, exhaustively cross-references RESEARCH, and traces every ROADMAP success criterion to specific tasks. Literal artifacts in Appendix A match RESEARCH Deliverables verbatim. Test gate (Appendix B) matches `infra/docker-compose.yml` reality (container `l10n_py_odoo`, DB `l10n_py_dev`, mount `/mnt/extra-addons/l10n-paraguay`). Sequencing matches ROADMAP locked order.

3 MEDIUM and 5 LOW flags identified — none block execution; all are easy fixes that the planner can resolve in a quick respin or the executor can absorb without losing the goal.

---

## Goal-backward coverage table

| # | ROADMAP Success Criterion (literal) | Plan IDs | Verification path | Verdict |
|---|---|---|---|---|
| 1 | `pre-commit run --all-files` corre limpio sobre todo el repo (hooks OCA listed) | P1-A → P1-B → P1-C | P1-C step 5: `pre-commit run --all-files` exits 0 after semantic baseline commit. Hook set matches REQ amendment (RESEARCH R-01 + A-03 swap of non-existent `oca-fix-manifest-version` for `oca-fix-manifest-website` + pylint-odoo C8106). | **PASS** |
| 2 | Push directo a `main` (incluso owner `@Ezcareaga`) es rechazado por GitHub | P1-H + P1-I step 6 | P1-H Appendix A.9 `gh api PUT` with `enforce_admins: true`. P1-I step 6 explicit negative test (`git push origin main` expected REJECT). | **PASS** |
| 3 | PR de prueba dispara workflows verdes antes de poder mergearse | P1-D + P1-E + P1-G → P1-I step 4 | P1-I PR #1 triggers `pre-commit`, `test (test with Odoo)`, `commitlint`. Branch protection from P1-H enforces "all 3 green before merge". | **PASS** |
| 4 | Dependabot abre PRs automáticas semanales | P1-F | `.github/dependabot.yml` Appendix A.5 with 2 ecosystems × weekly Monday schedule. Async verification within 7 days, tracked in DoD. | **FLAG** (async-by-nature; acknowledged in DoD) |
| 5 | Commit message no-conventional rechazado por commitlint | P1-G + P1-I step 5 (P-03) | `commitlint.config.js` Appendix A.4b `type-enum` severity 2. P1-I PR #2 with title `fixed bug` opened to confirm REJECT. | **PASS** |

---

## Sequencing integrity

ROADMAP locked sequencing: **CI-01 → CI-02 → CI-04 → {CI-03 ∥ CI-05 ∥ CI-06} → CI-07 → CI-08**

PLAN waves:
- Wave 1 → P1-A (CI-01) ✓
- Wave 2 → P1-B (CI-02 part 1) ✓
- Wave 3 → P1-C (CI-02 part 2) ✓
- Wave 4 → P1-D (CI-04) ✓
- Wave 5 → P1-E (CI-03) ∥ P1-F (CI-05) ∥ P1-G (CI-06) ✓
- Wave 6 → P1-H (CI-07) ✓
- Wave 7 → P1-I (CI-08) ✓

**Verdict: PASS.** Sequencing matches ROADMAP exactly. D-05 split of CI-02 into B+C is the only refinement (locked decision, additive).

---

## Atomic commits + Conventional Commits

| Plan | Expected commit count | Actual | Conventional? |
|---|---|---|---|
| P1-A | 1 | `chore(pre-commit): add OCA hand-rolled config` | ✓ |
| P1-B | 1 (D-05 part 1) | `chore(pre-commit): apply cosmetic baseline (black+isort+prettier)` | ✓ |
| P1-C | 1 (D-05 part 2) | `chore(pre-commit): apply semantic baseline (...)` | ✓ |
| P1-D | 1 | `ci(lint): add pre-commit workflow` | ✓ |
| P1-E | 1 | `ci(test): add test workflow with codecov` | ✓ |
| P1-F | 1 | `ci(deps): add dependabot config` | ✓ |
| P1-G | 1 | `ci(commitlint): add conventional commits validation` | ✓ |
| P1-H | 0 | (none — gh api state change) | N/A ✓ |
| P1-I | 1 | `chore: ci sanity check` | ✓ |

CI-02 = 2 commits per D-05 ✓. CI-07 (P1-H) = 0 commits ✓. Total = 8 commits planned. All Conventional Commits compliant. **Verdict: PASS.**

---

## Literal artifact verbatim quote check

Compared Appendix A.1-A.7 in PLAN.md vs. RESEARCH.md Deliverables. Spot-check of hook pins:

| Hook | RESEARCH pin (R-05) | PLAN Appendix A.1 | Match |
|---|---|---|---|
| `oca/maintainer-tools` | `b89f767503be6ab2b11e4f50a7557cb20066e667` | `b89f767503be6ab2b11e4f50a7557cb20066e667` (line 866) | ✓ |
| `OCA/odoo-pre-commit-hooks` | `v0.0.33` | `v0.0.33` (line 873) | ✓ |
| `OCA/pylint-odoo` | `v9.1.3` | `v9.1.3` (line 903) | ✓ |
| `psf/black` | `22.8.0` | `22.8.0` (line 881) | ✓ |
| `prettier+plugin-xml` | `3.3.3 / 3.4.1` | `3.3.3 / 3.4.1` (lines 943-944) | ✓ |

Workflows A.2, A.3, A.4 also verified verbatim against RESEARCH sections. `commitlint.config.js` A.4b matches RESEARCH. Dependabot A.5 matches RESEARCH. `.coveragerc` A.6 matches RESEARCH. Zero TODO placeholders. Zero paraphrasing.

**Verdict: PASS.**

---

## Manual prerequisites listed

PLAN.md section "Manual steps before execution" explicitly enumerates:

1. **CODECOV_TOKEN setup BEFORE P1-E** — step-by-step (visit codecov.io → copy token → GitHub Settings → secret `CODECOV_TOKEN`). Re-check enforced inside P1-E step 1 (`gh secret list | Select-String CODECOV_TOKEN`). ✓
2. **`gh auth status` check BEFORE P1-H** — listed; expected output documented. ✓
3. GitHub Actions free-tier minutes available — listed (bonus, not in requested checks). ✓

**Verdict: PASS.**

---

## Pendings P-01..P-04 scheduled

| Pending | Scheduled in | Specific task | Verdict |
|---|---|---|---|
| **P-01** — smoke-verify `ODOO_TEST_TAGS` env var | P1-E step 3 + Appendix A.3 lines 1085-1093 inline step | Confirmed | ✓ PASS |
| **P-02** — `.pylintrc` / `.pylintrc-mandatory` sourcing | P1-A steps 1 + 3 (copy from Brazil, fallback render from jinja) | Documented in Appendix D | ✓ PASS |
| **P-03** — commitlint PR-title smoke-test | P1-I step 5 (PR #2 with title `fixed bug`, expect commitlint RED) | Branch `chore/ci-sanity-bad-title` + outcome documented | ✓ PASS |
| **P-04** — 4 README badges | P1-E step 2 + Appendix A.8 (CI + pre-commit + Coverage; license + Odoo retained) | README rewrite full deferred to Phase 3 DOC-01 | ✓ PASS |

**Verdict: PASS.** All 4 pendings have concrete scheduling with verification commands.

---

## Test gate D-07 command matches `infra/docker-compose.yml`

| Item | docker-compose.yml | PLAN Appendix B | Match |
|---|---|---|---|
| Container name | `l10n_py_odoo` (line 40) | `l10n_py_odoo` (cited in header) | ✓ |
| Postgres service | `postgres` (line 18) | `postgres` (exec target) | ✓ |
| Test DB | (creates `l10n_py_test` fresh) | `DROP DATABASE IF EXISTS l10n_py_test; CREATE...` | ✓ better hygiene than reusing `l10n_py_dev` |
| Addons path | `/mnt/extra-addons,/mnt/extra-addons/l10n-paraguay` (line 60) | identical (Appendix B step 4) | ✓ |
| User | container default `odoo` | uses container default (no explicit `-u`) | ✓ acceptable |

**Compose exec invocation:** PLAN uses `docker compose -f infra/docker-compose.yml exec -T odoo ...` — more correct than `docker exec l10n_py_odoo ...` because it honors compose context/network.

**Subtle issue:** PLAN uses `--without-demo=False` in Appendix B (loads demo data). Phase 1 retrospectiva showed 97 tests green — worth confirming the original run used the same flag (see L-04).

**Verdict: PASS.**

---

## Branch model consistency

D-06 says baseline (P1-A, B, C) goes direct to main. PLAN Appendix E confirms:

| Plan | Branch model | Matches D-06? |
|---|---|---|
| P1-A, B, C | Direct push to `main` | ✓ |
| P1-D onwards | Feature branch + PR | ✓ |
| P1-H | `gh api` state change (no commit) | ✓ |

**P1-H sequencing:** depends on P1-D ∧ P1-E ∧ P1-F ∧ P1-G — workflows must have run at least once on `main` to register status check names. PLAN explicitly states this and verifies via `gh api repos/.../actions/runs`. R-H-1 fallback documented. Workflows re-trigger on `push: branches: [main]` after squash-merge, registering the check context for branch protection. ✓

**Verdict: PASS.**

---

## Subagent routing per plan

Project CLAUDE.md REGLA REFORZADA requires subagent for any code task.

| Plan | Subagent assigned | Code task? | Compliant? |
|---|---|---|---|
| P1-A | git-workflow-manager + python-pro + code-reviewer | Yes (4 config files) | ✓ |
| P1-B | git-workflow-manager + code-reviewer | Yes (auto-fixes) | ✓ |
| P1-C | git-workflow-manager + code-reviewer | Yes (auto-fixes + review) | ✓ |
| P1-D | git-workflow-manager + code-reviewer | Yes (workflow YAML) | ✓ |
| P1-E | git-workflow-manager + python-pro + code-reviewer | Yes (YAML + .coveragerc + README) | ✓ |
| P1-F | git-workflow-manager + code-reviewer | Yes (dependabot YAML) | ✓ |
| P1-G | git-workflow-manager + python-pro + code-reviewer | Yes (YAML + JS config) | ✓ |
| P1-H | Orchestrator inline | No (gh api state change) | ✓ acceptable |
| P1-I | Orchestrator inline | Minimal (1 file `CHANGES.rst` + verifications) | ⚠ Borderline (F-02) |

**Verdict: PASS with one MINOR flag (F-02).**

---

## HIGH-severity concerns (BLOCK)

**None.**

---

## MEDIUM-severity concerns (FLAG)

**F-01 — Success Criterion #4 (Dependabot weekly PRs) is async-verified by nature.**
- Dimension: verification_derivation.
- Issue: cannot be synchronously verified at phase close. PLAN acknowledges in DoD line 818 as "tracked in execution log post-phase".
- Severity: MEDIUM (already mitigated).
- Recommendation: add synchronous proxy check in P1-F step 6 (e.g., fetch GitHub Insights dependency-graph endpoint to confirm config parsed without error). Currently only file presence + YAML parse verified.

**F-02 — `CHANGES.rst` created without subagent in P1-I.**
- Dimension: claude_md_compliance.
- Issue: Project CLAUDE.md REGLA REFORZADA: "Edits inline solo para correcciones triviales de typos en docs o configuración, nunca para código de modelos/tests/views/scripts". A new 5-line RST file is debatably trivial config/docs — borderline.
- Severity: MEDIUM (compliance interpretation).
- Recommendation: assign documentation-engineer or python-pro subagent for `CHANGES.rst` creation, OR explicitly document the inline-edit exemption with rationale in the plan.

**F-03 — Workflow filename drift from ROADMAP literal "lint.yml".**
- Dimension: requirement_coverage.
- Issue: ROADMAP Success Criterion #3 says "workflows `lint.yml` + `test.yml`". PLAN creates `.github/workflows/pre-commit.yml` (not `lint.yml`). The workflow `name:` field is `pre-commit`.
- Impact: None on behavior — GitHub branch protection uses job-display names, and PLAN's required check `pre-commit` matches the job name. OCA convention names this file `pre-commit.yml` (Brazil does exactly this).
- Severity: MEDIUM (semantic drift; resolved by documentation).
- Recommendation: add a one-line note in PLAN "Success Criteria" section mapping ROADMAP's "lint.yml" → `pre-commit.yml` (OCA-standard filename). PLAN already has a similar note for the `oca-fix-manifest-version` rename — add equivalent for the workflow filename.

---

## LOW-severity concerns (informational)

**L-01 — Addendum A-04 says "4 README badges", Appendix A.8 produces 5 total** (License + Odoo + CI + pre-commit + Coverage). Wording mismatch only.

**L-02 — `pyproject.toml` requires-python `>=3.11` and black `target-version = ["py311"]`** but CI runs inside `py3.10-odoo18.0` container. Black 22.8.0 under py3.10 still emits py311-targeted output (compatible).

**L-03 — Container `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`** is unpinned. T-01-02 documents this as `accept` disposition deferred to Pre-Fase 3.

**L-04 — Appendix B includes `--without-demo=False`** which loads demo data. Worth confirming the 2026-05-25 retrospectiva run used the same flag (97 tests green baseline).

**L-05 — PLAN line 783 lists `P1-D + P1-E + P1-F + P1-G → P1-I step 4`** for Success Criterion #3. P1-F (dependabot) does not contribute a status check — same row clarifies this. Could be tightened. Non-blocking.

---

## Recommendation

**Proceed to execution.**

- Overall: **FLAG-MINOR**.
- HIGH: **0**.
- MEDIUM: **3** (all already mitigated or single-line fixes).
- LOW: **5**.

Recommended quick fixes (optional respin, otherwise absorb during execution):

1. (F-03) Add one-line note mapping ROADMAP "lint.yml" → `pre-commit.yml`.
2. (F-02) Either add subagent for `CHANGES.rst` creation in P1-I, or document the inline exemption.
3. (F-01) Add synchronous proxy check in P1-F to reduce async-only verification on Dependabot.
4. Validate `--without-demo=False` against 97-test baseline before P1-B step 1.

Run `/gsd:execute-phase 1` to proceed. The 3 MEDIUM flags can be polished mid-flight without changing plan structure.

---

*PLAN CHECK created 2026-05-27 by gsd-plan-checker.*
