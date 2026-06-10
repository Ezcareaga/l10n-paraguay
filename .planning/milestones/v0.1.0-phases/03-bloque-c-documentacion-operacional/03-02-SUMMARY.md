---
phase: 03-bloque-c-documentaci-n-operacional
plan: 02
subsystem: docs/adr
tags: [documentation, adr, architecture-decisions, doc-08]
dependency_graph:
  requires: ["03-01"]
  provides: ["docs/adr/README.md", "docs/adr/0001-0005-*.md"]
  affects: ["README.md", "CONTRIBUTING.md"]
tech_stack:
  added: []
  patterns: ["Nygard lightweight ADR", "MADR with YAML frontmatter"]
key_files:
  created:
    - docs/adr/README.md
    - docs/adr/0001-odoo-community.md
    - docs/adr/0002-oca-style-from-day-one.md
    - docs/adr/0003-dnit-catalogs-source-of-truth.md
    - docs/adr/0004-multi-rubro-strategy.md
    - docs/adr/0005-hosting-strategy.md
  modified: []
decisions:
  - "ADR hybrid format: Nygard liviano for retroactive 0001-0003 (no fabricated options), MADR for prospective 0004-0005 (D-12)"
  - "ADR-0004 stays status:proposed — Phase 5 IND-01 owns the grep audit and Accepted flip (D-13)"
  - "ADR-0005 hosting options: Hetzner CX21 / Contabo VPS S / Telecel Cloud PY — no vendor committed; sovereignty driver refs docs/61"
metrics:
  duration_minutes: 15
  completed_date: "2026-06-05"
  tasks_completed: 2
  tasks_total: 2
  files_created: 6
  files_modified: 0
---

# Phase 03 Plan 02: ADRs 0001-0005 Summary

**One-liner:** Five ADRs in hybrid Nygard/MADR format — retroactive decisions
0001-0003 in Nygard liviano (no fabricated options), prospective 0004-0005 in MADR
with real options; DOC-08 satisfied.

---

## Tasks Completed

| Task | Name                                 | Commit  | Files                                |
| ---- | ------------------------------------ | ------- | ------------------------------------ |
| 1    | Nygard ADRs 0001-0003 + index README | cffa0fe | docs/adr/README.md, 0001, 0002, 0003 |
| 2    | MADR stub 0004 + hosting MADR 0005   | 349ae21 | docs/adr/0004, docs/adr/0005         |

---

## Verification Results

```
ls docs/adr/000*.md | wc -l  → 5  (DOC-08 gate PASSED)
grep "status: proposed" 0004  → PASSED (stub not prematurely Accepted)
grep "Nygard" README.md       → PASSED
grep "MADR" README.md         → PASSED
grep "Considered Options" 0001/0002/0003  → NOT FOUND (Nygard liviano correct)
```

All success criteria met.

---

## Deviations from Plan

None — plan executed exactly as written. Prettier hook reformatted `docs/adr/README.md`
table alignment on first commit attempt; re-staged and re-committed cleanly on second
attempt (standard pre-commit hook behavior, not a deviation).

---

## Known Stubs

**ADR-0004** (`docs/adr/0004-multi-rubro-strategy.md`) is an intentional stub per
D-13. `status: proposed`. Phase 5 IND-01 owns the full grep-audit analysis and will
flip it to `Accepted`. The stub satisfies DOC-08 (file must exist) while correctly
marking the decision as not yet fully analyzed.

---

## Threat Flags

No new network endpoints, auth paths, file access patterns, or schema changes
introduced. T-03-03 (hosting options public) mitigated: only illustrative provider
names and public pricing used in ADR-0005, no account IDs or real domain names.
T-03-04 (repudiation on ADR-0004 ownership) mitigated: explicit `status: proposed`
and `Phase 5 IND-01` marker in Decision Outcome.

---

## Self-Check: PASSED

- docs/adr/README.md: FOUND
- docs/adr/0001-odoo-community.md: FOUND
- docs/adr/0002-oca-style-from-day-one.md: FOUND
- docs/adr/0003-dnit-catalogs-source-of-truth.md: FOUND
- docs/adr/0004-multi-rubro-strategy.md: FOUND
- docs/adr/0005-hosting-strategy.md: FOUND
- Commit cffa0fe: FOUND (docs(adr): add 0001-0003 Nygard ADRs + index)
- Commit 349ae21: FOUND (docs(adr): add 0004 multi-rubro stub + 0005 hosting MADRs)
