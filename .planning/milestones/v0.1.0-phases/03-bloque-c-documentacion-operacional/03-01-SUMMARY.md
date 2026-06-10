---
phase: 03-bloque-c-documentaci-n-operacional
plan: "01"
subsystem: docs-prep
tags: [docs, pre-commit, rename, hook, readme-regeneration]
dependency_graph:
  requires: []
  provides: [docs/65_FASE_1_RETROSPECTIVA.md, oca-gen-addon-readme-active]
  affects:
    [
      AGENTS.md,
      .planning/PROJECT.md,
      .pre-commit-config.yaml,
      addons/l10n_py_base/README.rst,
      addons/l10n_py_account/README.rst,
    ]
tech_stack:
  added: []
  patterns:
    [
      oca-gen-addon-readme with --no-gen-html on Windows,
      mixed-line-ending exclude for generated RST,
    ]
key_files:
  created: []
  modified:
    - docs/65_FASE_1_RETROSPECTIVA.md
    - AGENTS.md
    - .planning/PROJECT.md
    - .pre-commit-config.yaml
    - addons/l10n_py_base/README.rst
    - addons/l10n_py_account/README.rst
decisions:
  - "--no-gen-html added to oca-gen-addon-readme args to avoid cp1252 UnicodeDecodeError on Windows"
  - "mixed-line-ending hook now excludes /README.rst$ (matches existing trailing-whitespace/end-of-file-fixer pattern; prevents CRLF cycle on Windows)"
metrics:
  duration: "~10 min"
  completed: "2026-06-05"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 6
---

# Phase 03 Plan 01: Foundation prep (rename 60→65 + oca-gen-addon-readme) Summary

**One-liner:** Freed docs/60 prefix by renaming retrospectiva to docs/65 and activated oca-gen-addon-readme hook with Windows-compatible args, regenerating both addon README.rst files from fragments.

## Tasks Completed

| Task | Name                                                         | Commit  | Files                                                                                      |
| ---- | ------------------------------------------------------------ | ------- | ------------------------------------------------------------------------------------------ |
| 1    | Rename docs/60*FASE_1_RETROSPECTIVA → docs/65* (D-05)        | cc17da7 | docs/65_FASE_1_RETROSPECTIVA.md, AGENTS.md, .planning/PROJECT.md                           |
| 2    | Activate oca-gen-addon-readme + regenerate README.rst (D-07) | 15d2937 | .pre-commit-config.yaml, addons/l10n_py_base/README.rst, addons/l10n_py_account/README.rst |

## Verification

- `docs/65_FASE_1_RETROSPECTIVA.md` exists; `docs/60_FASE_1_RETROSPECTIVA.md` does not
- `git log --diff-filter=R --summary` shows rename at 100% similarity
- Zero occurrences of `60_FASE_1_RETROSPECTIVA` in AGENTS.md / .planning/PROJECT.md
- `docs/60_SECURITY_BASELINE.md` untouched (prefix 60 now unambiguous)
- `.pre-commit-config.yaml` contains `oca-gen-addon-readme` exactly once, in maintainer-tools block (pin b89f767 unchanged)
- No new `- repo:` block added
- `pre-commit run oca-gen-addon-readme --all-files` exits 0 (Passed)
- Both addon README.rst regenerated from readme/ fragments and tracked

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] oca-gen-addon-readme requires --repo-name and --branch args**

- **Found during:** Task 2
- **Issue:** Plan said "no `exclude` override needed" and implied bare `- id: oca-gen-addon-readme` would work. The hook CLI requires `--repo-name` (required option) and `--branch` (required option) that must be passed as args.
- **Fix:** Added `args: [--addons-dir=addons, --repo-name=l10n-paraguay, --branch=18.0, --no-gen-html]` to the hook entry.
- **Files modified:** `.pre-commit-config.yaml`
- **Commit:** 15d2937

**2. [Rule 1 - Bug] Windows cp1252 UnicodeDecodeError in index.html generation**

- **Found during:** Task 2
- **Issue:** `oca-gen-addon-readme` generates `static/description/index.html` by default. On Windows, reading the generated HTML with the system cp1252 codec hit byte 0x9d (undefined in cp1252), causing a traceback on the second run.
- **Fix:** Added `--no-gen-html` arg. HTML index is optional; README.rst is the required output. This suppresses the `static/` directory creation entirely.
- **Files modified:** `.pre-commit-config.yaml`
- **Commit:** 15d2937

**3. [Rule 1 - Bug] CRLF cycle: oca-gen-addon-readme writes CRLF on Windows, mixed-line-ending kept re-fixing**

- **Found during:** Task 2 (commit loop)
- **Issue:** `oca-gen-addon-readme` generates README.rst with CRLF line endings on Windows. The `mixed-line-ending` hook (--fix=lf) then modified the files on every pre-commit run, creating an infinite cycle preventing commit.
- **Fix:** Added `exclude: /README\.rst$` to the `mixed-line-ending` hook entry, matching the same pattern already used by `trailing-whitespace` and `end-of-file-fixer`. The README.rst files are committed in LF form (normalized by the first hook pass).
- **Files modified:** `.pre-commit-config.yaml`
- **Commit:** 15d2937

## Known Stubs

None.

## Threat Flags

None. No new network endpoints, auth paths, file access patterns, or schema changes introduced. The hook reuses an already-pinned maintainer-tools source (T-03-01 mitigated: pin b89f767 unchanged).

## Self-Check: PASSED

- `docs/65_FASE_1_RETROSPECTIVA.md` exists: FOUND
- `docs/60_FASE_1_RETROSPECTIVA.md` absent: CONFIRMED
- Commit cc17da7 exists: FOUND
- Commit 15d2937 exists: FOUND
- `oca-gen-addon-readme` in .pre-commit-config.yaml: 1 occurrence (FOUND)
- `addons/l10n_py_base/README.rst` tracked: FOUND
- `addons/l10n_py_account/README.rst` tracked: FOUND
