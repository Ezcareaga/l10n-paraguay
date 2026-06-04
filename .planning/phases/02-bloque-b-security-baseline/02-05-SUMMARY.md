---
phase: 02-bloque-b-security-baseline
plan: 05
subsystem: docs / compliance
tags: [compliance, ley-7593-2025, anpdp, gdpr, oca-data-protection, sec-07]
dependency_graph:
  requires: [02-02]
  provides: [docs/61_COMPLIANCE_LEY_7593.md]
  affects: [docs/60_SECURITY_BASELINE.md cross-refs]
tech_stack:
  added: []
  patterns:
    [
      vendor-vs-operador-split,
      compliance-matrix,
      ARCO-map,
      OCA-18.0-data-protection-modules,
    ]
key_files:
  created:
    - docs/61_COMPLIANCE_LEY_7593.md
  modified:
    - .codespellrc
decisions:
  - "Use Ley 7593/2025 (general GDPR-style) as governing law per amendment A-01; Ley 6534/2020 (credit data, BCP) explicitly out of scope in closing footnote"
  - "Name supervisory authority as ANPDP/MITIC throughout; zero SENAC references (verified)"
  - "Use OCA 18.0 modules verified in research: privacy_consent, privacy_partner_to_be_forgotten, base_export_anonymize, privacy; document data_subject_access_request as gap"
  - "Document module of cancellation/olvido vigente exclusively as privacy_partner_to_be_forgotten; never as gdpr_purge (verified zero gdpr_purge mentions)"
  - "Cross-reference docs/60_SECURITY_BASELINE.md (parallel artifact from Plan 02-04) in 9 places; markdown link target validated post-merge by orchestrator"
metrics:
  duration_seconds: 1320
  completed: 2026-06-03
  tasks: 1
  files_created: 1
  files_modified: 1
  commits: 2
requirements:
  - SEC-07
---

# Phase 02 Plan 05: Bloque B Security Baseline — SEC-07 Ley 7593/2025 Compliance Doc Summary

Documento de compliance que cierra SEC-07 con `docs/61_COMPLIANCE_LEY_7593.md` (176 líneas), citando la ley correcta (Ley 7593/2025 PY) tras amendment A-01 — Ley 6534/2020 queda explícitamente fuera de scope.

## One-liner

Compliance doc Ley 7593/2025 (general GDPR-style PY) con split vendor/operador, mapeo ARCO a módulos OCA 18.0 verificados, matriz de cumplimiento de 10 filas y cross-refs a docs/60_SECURITY_BASELINE.md.

## Tasks Completed

| Task ID  | Description                                                                                  | Files                          | Commit    |
| -------- | -------------------------------------------------------------------------------------------- | ------------------------------ | --------- |
| 02-05-01 | Author docs/61_COMPLIANCE_LEY_7593.md (vendor/operador split + ARCO map + compliance matrix) | docs/61_COMPLIANCE_LEY_7593.md | `0a553fd` |

## Output Spec

### File created — `docs/61_COMPLIANCE_LEY_7593.md` (176 lines)

**H2 sections (5 required + 1 bonus):**

1. `## 1. Alcance y ley aplicable` — qué es Ley 7593/2025, por qué aplica al proyecto (PII de clientes/facturas), comparación rápida con GDPR (tabla 10 filas), caveat temporal sobre ANPDP en formación (operativa 2026, enforcement 2027), aclaración explícita de que la autoridad es ANPDP/MITIC y no otra entidad regulatoria.
2. `## 2. Responsabilidades: vendor vs operador (D-13)` — tabla 10 filas con responsabilidades partidas entre vendor (este proyecto) y operador (deployer), cubriendo cifrado PII, audit logs, export/borrado, password policy, DPO, breach notification a ANPDP, consent capture, contratos con encargados, retention policy y registro de tratamiento.
3. `## 3. Derechos ARCO + mecanismos Odoo (D-14)` — tabla 6 filas mapeando Acceso (Art. 11), Rectificación (Art. 12), Cancelación (Art. 14), Oposición (Art. 15), Portabilidad (Art. 16) y Consentimiento (Art. 6) a mecanismos Odoo + módulos OCA 18.0; cross-ref a docs/60 §3 Audit logs para trazabilidad de cambios; notas detalladas de `privacy_partner_to_be_forgotten` y `privacy_consent`; gap explícito sobre `data_subject_access_request` (no portado a 18.0).
4. `## 4. Módulos OCA disponibles en 18.0` — tabla 4 módulos OCA 18.0 verificados (`privacy_consent`, `privacy_partner_to_be_forgotten`, `base_export_anonymize`, `privacy` — todos `18.0.1.0.0`) + tabla 2 filas de módulos ausentes con plan de reemplazo / TODO operador.
5. `## 5. Matriz de cumplimiento — Ley 7593/2025 (D-15)` — tabla 10 filas cubriendo Arts. 6, 11, 12, 14, 15, 16, 17, 18, 34-39 + fila gap explícito para `data_subject_access_request`, cada fila referenciando el control en docs/60 y el estado (Implementado / Documentado / Responsabilidad operador / TODO operador / Pre-Fase 4).
6. `## 6. Próximos pasos para el operador` — checklist de 7 items para deploy productivo, alineado con docs/60.

**Closing footnote:** Ley 6534/2020 (Datos Personales Crediticios, BCP, burós de crédito) explícitamente declarada fuera de scope.

### File modified — `.codespellrc` (Rule 3 auto-fix)

Agregados `ue` (sigla Unión Europea en cita "Reglamento (UE) 2016/679") y `anual` (palabra española correcta) a `ignore-words-list`. Política del repo es agregar tokens cuando codespell flagea — exactamente este caso. Sin impacto en otros archivos.

## Acceptance Criteria Verification

| Criterion                                                                           | Result                                                               |
| ----------------------------------------------------------------------------------- | -------------------------------------------------------------------- |
| File name exact: `docs/61_COMPLIANCE_LEY_7593.md`                                   | ✅ True                                                              |
| Wrong filename `_LEY_6534.md` does NOT exist                                        | ✅ False (correctly absent)                                          |
| No YAML frontmatter (first line = `# `)                                             | ✅ True                                                              |
| 5 H2 sections present (`## 1.` through `## 5.`)                                     | ✅ 5 + bonus §6                                                      |
| Cites `Ley 7593/2025`                                                               | ✅ True                                                              |
| `ANPDP` count                                                                       | ✅ 15 (>= 2)                                                         |
| `MITIC` present                                                                     | ✅ True                                                              |
| `SENAC` count                                                                       | ✅ 0 (must be 0)                                                     |
| `gdpr_purge` count                                                                  | ✅ 0 (must be 0)                                                     |
| Vendor table keywords: Cifrado PII, Audit logs, password, DPO, Notificación a ANPDP | ✅ all present                                                       |
| `privacy_partner_to_be_forgotten` referenced                                        | ✅ True                                                              |
| Article matches for Arts. 6/11/12/14/15/16/17/18                                    | ✅ 33 (>= 8)                                                         |
| `Arts. 34` (ANPDP creation) present                                                 | ✅ True                                                              |
| Cross-refs to `60_SECURITY_BASELINE`                                                | ✅ 9 (>= 1)                                                          |
| Footnote with `Ley 6534/2020` + `no aplica` + burós de crédito                      | ✅ True                                                              |
| Line count                                                                          | ✅ 176 (>= 150)                                                      |
| `pre-commit run --files docs/61_COMPLIANCE_LEY_7593.md` exit 0                      | ✅ Passed                                                            |
| Conventional Commits message format                                                 | ✅ `docs(sec): add Ley 7593/2025 compliance doc ... (closes SEC-07)` |

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 — Blocking issue] codespell rejected `ue` and `anual` as typos**

- **Found during:** Task 02-05-01 (pre-commit run)
- **Issue:** `codespell` hook reported `UE ==> USE, DUE` (línea 32) y `anual ==> annual` (línea 45). Ambos son falsos positivos: `UE` es la sigla "Unión Europea" en la cita normativa "Reglamento (UE) 2016/679" y `anual` es palabra española correcta para "annual" en la oración sobre sanciones GDPR.
- **Fix:** Agregué `ue,anual` al final de `ignore-words-list` en `.codespellrc`. La política del repo (en el header del `.codespellrc`) es explícita: "If codespell starts flagging new tokens later, add them" — exactamente este caso.
- **Files modified:** `.codespellrc`
- **Commit:** `33f8e23`
- **Why Rule 3 (not 4):** No es decisión arquitectural — es un ajuste de whitelist documentado como práctica recurrente del repo. Sin este fix, el commit del task principal no pasaría pre-commit.

### Plan adjustments (within Claude's Discretion)

**2. Vendor/operador table grew from 6 → 10 rows**

Plan exigía ≥5 filas (must_haves). Decidí agregar 4 filas extra (Consent capture, Contratos con encargados, Política de retención, Registro de tratamiento) porque están explícitamente listadas en D-13 (CONTEXT.md) como responsabilidades operador y son necesarias para que el split sea accionable para el reviewer / abogado del cliente. Sin overhead — completa el contrato D-13 sin scope creep.

**3. Matriz §5 incluye fila de gap explícita**

Plan sugería agregar 1 fila final marcando `data_subject_access_request` como gap. Lo hice como fila separada al final de la tabla con `**Gap — ...**` en bold y estado `TODO operador / Pre-Fase 4`. Cumple la instrucción literal del plan.

**4. Bonus §6 "Próximos pasos para el operador"**

Agregué una sexta sección (no exigida por el plan) con un checklist de 7 items para el operador. Razón: cierra el ciclo "compliance doc accionable" al darle al deployer un punto de partida concreto sin que tenga que sintetizar el doc completo. Mantiene el doc en estilo operacional (D-09: "snippets > prosa larga"). Sin conflicto con must_haves (5 secciones siguen presentes en `## 1.` a `## 5.`).

## Known Stubs

Ninguno. El doc es 100% prosa + tablas; no hay placeholder code, no hay "TODO" en el sentido de gancho técnico no implementado — los TODOs documentados son **responsabilidad operador** (parte del contrato del doc).

## Threat Flags

Ninguno. Este plan no introduce nueva surface técnica — es un documento de compliance que **reduce** riesgo de repudiation (T-SEC-07-doc, T-SEC-07-wronglaw del threat model del plan).

## Self-Check

- [x] `docs/61_COMPLIANCE_LEY_7593.md` exists (176 lines, verified)
- [x] Commit `0a553fd` exists in `git log` (verified)
- [x] Commit `33f8e23` exists in `git log` (verified)
- [x] No accidental deletions in `git diff HEAD~2 HEAD --diff-filter=D` (verified empty output)
- [x] Pre-commit passes for `docs/61_COMPLIANCE_LEY_7593.md` + `.codespellrc`
- [x] HEAD on `worktree-agent-a70dcdd146ca001b1` (worktree-agent-\* namespace, never on protected ref)
- [x] No modifications to `.planning/STATE.md` or `.planning/ROADMAP.md` (orchestrator owns those)

## Self-Check: PASSED

## Wave 4 parallel artifact note

Plan 02-05 ejecutó en paralelo con Plan 02-04 (Wave 4, no file overlap). Este worktree contiene únicamente `docs/61_COMPLIANCE_LEY_7593.md` + `.codespellrc`; el archivo `docs/60_SECURITY_BASELINE.md` no existe en este worktree pero estará presente tras el merge del worktree de Plan 02-04 al main branch. Los 9 cross-refs a `60_SECURITY_BASELINE.md` se resolverán post-merge.
