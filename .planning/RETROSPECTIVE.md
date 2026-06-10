# RETROSPECTIVE — l10n-paraguay

---

## Milestone: v0.1.0 — Pre-Fase 2 Foundation

**Shipped:** 2026-06-10
**Phases:** 5 (Bloques A → E)
**Plans:** 16 (14 formales GSD + 2 ejecuciones directas)
**REQs:** 35/35 v1 completados
**Duración:** 2026-05-26 → 2026-06-10 (15 días calendario)

---

### What Was Built (una línea por phase)

| Phase              | Resultado                                                                                                                                                            |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Phase 1 — Bloque A | pre-commit OCA activo + GitHub Actions lint/test/commitlint/dependabot + branch protection en `main` (6 required status checks)                                      |
| Phase 2 — Bloque B | Security baseline: LICENSE AGPL-3 + SECURITY.md + `security.yml` (gitleaks 0 findings, Bandit 0 findings) + docs/60 (6 ejes) + docs/61 (compliance Ley 7593/2025 PY) |
| Phase 3 — Bloque C | Docs operacionales: README real + CHANGELOG + CONTRIBUTING + CODE_OF_CONDUCT + ARCHITECTURE C4 + DEPLOYMENT + RUNBOOK (10+ incidentes) + ADRs 0001-0005              |
| Phase 4 — Bloque D | Repo hygiene: issue templates + PR template + CODEOWNERS + release.yml (7 categorías) + GitHub Release v0.1.0 publicado (tag `v0.1.0` en `01fe470`)                  |
| Phase 5 — Bloque E | Multi-rubro foundation: ADR-0004 aceptado + docs/80 roadmap + auditoría grep limpia + template `l10n_py_industry_*` documentado                                      |

---

### What Worked

**Subagents especializados por dominio**: despachar `voltagent-qa-sec:security-auditor` para Phase 2 y `voltagent-dev-exp:documentation-engineer` para Phase 3 evitó tropiezos inline que ya costaron 1h en Fase 1b (debugging 6 tests que el debugger resolvió en una pasada). El costo de dispatch upfront (2-3 min) fue menor que el costo de iterar inline.

**Atomic commits + PRs con checks requeridos**: cada plan GSD cerró con un PR que pasaba todos los checks antes de mergear. El historial quedó limpio y cualquier regresión se habría detectado antes de llegar a `main`.

**Tracking docs vivos (STATE.md + ROADMAP.md + phase SUMMARY.md)**: mantener el estado actualizado en cada checkpoint permitió resumir sesiones sin perder contexto. Los SUMMARY.md de cada plan son la fuente de verdad de lo que se ejecutó realmente.

**Wave sequencing en Phase 2 y Phase 3**: dividir las phases en waves (Wave 1 → blocked → Wave 2 → ...) forzó el orden correcto de dependencias sin tener que coordinar manualmente qué plan corría primero.

**Worktrees para planes paralelos (Phase 2 Wave 4)**: los planes 02-04 y 02-05 corrieron en worktrees separados sin interferencia de archivos.

---

### What Was Inefficient

**Checkboxes de REQUIREMENTS.md quedaron desincronizados hasta el cierre**: los 35 REQs en PROJECT.md se marcaron `[ ]` (sin `x`) durante toda la ejecución del milestone. La sincronización ocurrió recién en PR #28 (commit de cierre). En el próximo milestone, marcar cada REQ como `[x]` en el mismo PR que lo cierra.

**Debugging inline en sesión 2026-05-25 (Fase 1b, pre-milestone)**: antes de establecer la regla de dispatch temprano, se perdió ~1h debuggeando inline 6 tests que el debugger resolvió en una pasada. Esta ineficiencia fue el origen de la regla formalizada en CLAUDE.md: cualquier test que falla después de un fix → dispatch a subagent, sin excepción.

**Phase 1 sin plans GSD**: la primera phase se ejecutó directamente antes de tener GSD configurado en el repo. Funcionó, pero sin SUMMARY.md ni tracking formal. Las fases siguientes con planes GSD tuvieron mejor trazabilidad.

---

### Key Lessons

1. **Regla de dispatch temprano es correcta**: el overhead de despachar un subagent (2-3 min) es menor que el costo de iterar inline en un bug. No negociar con la regla.

2. **Los tracking docs se pudren si no se actualizan en el mismo PR**: STATE.md y REQUIREMENTS.md deben actualizarse como parte del PR que cierra cada plan, no al final del milestone.

3. **Content filter en CoC**: generar Contributor Covenant vía subagent activa el content filter de la API. Solución: `curl` directo desde la URL canónica. Documentado en MEMORY.md.

4. **`oca-gen-addon-readme` y digest drift**: los digests son OS-dependientes (Windows backslash vs Linux). Solución: `--keep-source-digest` en `.pre-commit-config.yaml`. Cualquier futuro hook que genere archivos deterministas debe verificarse en ambos OS o usar el mismo flag.

5. **Ley 7593/2025 (no 6534/2020)**: la ley de protección de datos generales de Paraguay es 7593/2025 (GDPR-style, autoridad ANPDP/MITIC). Ley 6534/2020 aplica solo a datos crediticios (BCP). Verificar leyes vía Exa MCP antes de escribir docs de compliance — no confiar en training data.

6. **Manual releases > semantic-release para proyectos early-stage**: semantic-release requiere historial de commits perfectamente formateado. Para el primer release de un proyecto con historia imperfecta, el proceso manual (CHANGELOG → tag → `gh release create --notes-file`) es más predecible.

---

_Retrospective creada: 2026-06-10 — cierre milestone v0.1.0_
