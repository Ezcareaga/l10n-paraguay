# Phase 3: Bloque C — Documentación operacional - Research

**Researched:** 2026-06-05
**Domain:** Technical documentation — OCA-style repo meta files + architecture docs + ADRs + RUNBOOK
**Confidence:** HIGH

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Idioma split — inglés en raíz (README, CONTRIBUTING, CODE_OF_CONDUCT, CHANGELOG), español en docs/ (docs/70-72, ADRs 0001-0005). Consistente con ~25 docs existentes en docs/.
- **D-02:** README estructura OCA-style, evaluador primero: qué es → tabla de módulos con estado REAL (versiones 18.0.1.1.0/18.0.1.0.0, 97 tests, sin "TODO" en módulos shipped) → installation → quick start docker-compose → links a docs/ → sección dev que delega a CONTRIBUTING.md. Tooling de contribuidor (codegraph, references, venv) se muda a CONTRIBUTING.md.
- **D-03:** Quick start reusa `infra/docker-compose.yml` existente. Secuencia: clone → `docker compose -f infra/docker-compose.yml up -d` → crear DB → instalar módulos → login. Es el camino que DOC-10 smoke-testea.
- **D-04:** CODE_OF_CONDUCT = Contributor Covenant 2.1. Contacto enforcement: `careagaezz@gmail.com`.
- **D-05:** Renombrar `docs/60_FASE_1_RETROSPECTIVA.md` → `docs/65_FASE_1_RETROSPECTIVA.md` (liberar prefijo 60 para SECURITY_BASELINE). Actualizar todos los links (CLAUDE.md, PROJECT.md, docs internos). Número exacto es discreción del planner.
- **D-06:** `CHANGELOG.md` reemplaza `CHANGES.rst`. Formato Keep a Changelog 1.1.0 en inglés. Eliminar `CHANGES.rst`.
- **D-07:** Activar hook `oca-gen-addon-readme` en `.pre-commit-config.yaml`. Usar el mismo pin `b89f767503be6ab2b11e4f50a7557cb20066e667` de maintainer-tools ya presente. El diff de regeneración de `README.rst` va en commit propio.
- **D-08:** Entry `[0.1.0] - Unreleased` documenta Fase 1 (l10n_py_base 18.0.1.1.0 + l10n_py_account 18.0.1.0.0, 97 tests) + foundation Pre-Fase 2 (CI, security baseline, docs operacionales). Fecha se completa cuando Phase 4 taggea.
- **D-09:** CHANGELOG se actualiza al release (compilado desde Conventional Commits). Sin obligación per-PR.
- **D-10:** Diagramas en Mermaid (C4Context, C4Container experimental, sequenceDiagram, stateDiagram-v2). Sin PlantUML, sin PNGs commiteados. Renderiza nativo en GitHub.
- **D-11:** docs/70 = doc completo con estados explícitos. C4 muestra los 6 módulos con marker shipped/planned. Sequence diagram FE y state machine DTE etiquetados "diseño objetivo — Fase 2 EDI".
- **D-12:** ADR template híbrido: ADRs 0001-0003 en Nygard liviano (retroactivos); ADRs 0004-0005 en MADR (con opciones abiertas reales). docs/adr/README.md explica el criterio.
- **D-13:** ADR-0004 = stub Proposed en Phase 3. Phase 5 (IND-01) lo completa.
- **D-14:** docs/71 = blueprint estilo docs/60. Compose prod + Caddyfile van como code blocks dentro del doc. Marker `> Note: validar en Pre-Fase 3 cuando exista deploy real` en snippets.
- **D-15:** RUNBOOK = 10 incidentes locked (lista exacta en CONTEXT.md). Template fijo por incidente: Síntoma / Severidad / Diagnóstico / Resolución / Prevención. Escalation N1→N2→N3 al final del doc. Incidentes SIFEN-dependientes llevan marker "procedimiento se valida en Fase 2 EDI".
- **D-16:** Smoke test DOC-10 = dev externo real + checklist en GitHub issue. Phase 3 queda "implemented" al mergear docs; DOC-10 es UAT asíncrono, no bloquea avance a Phase 4.

### Claude's Discretion

- Número exacto del rename de la retrospectiva (D-05) — `65_` u otro prefijo libre coherente.
- Wording y secciones exactas de CONTRIBUTING.md más allá de los 6 ejes obligatorios + regla DOC-09 + contenido migrado del README. Documentar divergencia CI (py3.10+PG12 OCA image) vs runtime local (py3.11+/PG15+) — A-01 Phase 1.
- Estructura del checklist del issue DOC-10 (D-16).
- Contenido de ADR-0005 hosting: opciones MADR a comparar (Hetzner vs Contabo vs proveedor local PY).
- Versión/pin exacto del hook `oca-gen-addon-readme` — researcher confirma que el pin existente `b89f767` lo incluye.
- Orden de PRs/waves de la phase.
- Badges adicionales del README solo si aportan — mantener los 6 existentes salvo razón.

### Deferred Ideas (OUT OF SCOPE)

- Contenido completo del ADR-0004 multi-rubro — Phase 5 (IND-01).
- Issue/PR templates, CODEOWNERS, release.yml, tag v0.1.0 — Phase 4.
- Release process en CONTRIBUTING (semantic-release vs manual) — Phase 4 REL-06 agrega la sección; Phase 3 deja placeholder.
- Deploy real (VPS + Caddy + Postgres prod) + validación de docs/71 — Pre-Fase 3.
- `scripts/restore-smoke.sh` ejecutable — Pre-Fase 3.
- Validación de procedimientos SIFEN del runbook (incidentes 1, 4, 5, 7, 10) — Fase 2 EDI.
- Migración de docs/ españoles a inglés — Fase 6 OCA.
  </user_constraints>

---

<phase_requirements>

## Phase Requirements

| ID     | Description                                                                                                               | Research Support                                                                                           |
| ------ | ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| DOC-01 | `README.md` raíz refleja estado real, badges, quick start funcional con docker-compose, links a docs/                     | D-02/D-03 locked; infra/docker-compose.yml verificado operacional; 6 badges existentes confirmados         |
| DOC-02 | `CHANGELOG.md` formato Keep a Changelog con `v0.1.0` inicial                                                              | D-06/D-08 locked; Keep a Changelog 1.1.0 format verified; CHANGES.rst content identified for migration     |
| DOC-03 | `CONTRIBUTING.md` cubre 6 ejes: setup dev env, branch naming, Conventional Commits, code review, testing ≥80%, pre-commit | D-02/D-07 supply content; quick start sequence from docker-compose verified                                |
| DOC-04 | `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1)                                                                           | D-04 locked; CC 2.1 verified; single placeholder = enforcement email                                       |
| DOC-05 | `docs/70_ARCHITECTURE.md`: C4 Context, C4 Container, sequence FE, state machine DTE                                       | D-10/D-11 locked; Mermaid C4 experimental but GitHub-native confirmed; state machine from docs/03 verified |
| DOC-06 | `docs/71_DEPLOYMENT.md`: VPS, Docker Compose prod, Caddy, Postgres backup, health checks, update procedure                | D-14 locked; references Phase 2 docs/60 for backup/network (no duplication); blueprint pattern confirmed   |
| DOC-07 | `docs/72_RUNBOOK.md` ≥10 incidentes with template and escalation path                                                     | D-15 locked; 10 incidents confirmed; SIFEN domain knowledge from docs/01                                   |
| DOC-08 | `docs/adr/` with ADRs 0001-0005                                                                                           | D-12/D-13 locked; MADR format verified; Nygard format verified; hybrid rationale documented                |
| DOC-09 | Regla en `CONTRIBUTING.md` — cambio arquitectónico = nuevo ADR en el mismo PR                                             | Content item in CONTRIBUTING.md; no tooling required                                                       |
| DOC-10 | Smoke test: dev externo levanta el proyecto siguiendo solo `CONTRIBUTING.md`                                              | D-16 = GitHub issue checklist; async UAT; does not block Phase 4                                           |

</phase_requirements>

---

## Summary

Phase 3 is a documentation-production phase with zero new code. All 10 requirements map to creating or rewriting files in the repo root and `docs/`. The decisions are tightly locked (16 D-xx in CONTEXT.md), so the research task is primarily to verify the technical specifics that underpins those decisions rather than to explore alternatives.

The primary risk is **content correctness** (the docs reflect actual current state) rather than technical uncertainty. The second risk is **sequencing** — the rename of `docs/60_FASE_1_RETROSPECTIVA.md` (D-05) touches links in four locations and must happen early so the rest of the wave doesn't create links to the old name. The third risk is the `oca-gen-addon-readme` hook activation (D-07): the hook is confirmed present at the pinned maintainer-tools commit, but its first run will regenerate both `addons/l10n_py_base/README.rst` and `addons/l10n_py_account/README.rst` — these diffs must go in a dedicated commit so `git blame` stays clean.

The Mermaid C4 diagrams (D-10) render natively in GitHub but remain experimental — the syntax is stable enough for production use in 2025, but layout is manual and CSS themes are not customizable. The sequence diagram and state machine types (`sequenceDiagram`, `stateDiagram-v2`) are fully stable in Mermaid.

**Primary recommendation:** Execute in 4 waves. Wave 1: rename D-05 + meta files (README, CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT). Wave 2: `oca-gen-addon-readme` hook + baseline commit. Wave 3: docs/70-72 (ARCHITECTURE, DEPLOYMENT, RUNBOOK). Wave 4: docs/adr/ (ADRs 0001-0005 + README.md) + GitHub issue for DOC-10.

---

## Architectural Responsibility Map

| Capability                                          | Primary Tier               | Secondary Tier                    | Rationale                                               |
| --------------------------------------------------- | -------------------------- | --------------------------------- | ------------------------------------------------------- |
| README / CONTRIBUTING / CHANGELOG / CODE_OF_CONDUCT | Repo root / Static         | —                                 | Standard GitHub meta files; no runtime tier             |
| docs/70 ARCHITECTURE diagrams                       | Docs (static, versionable) | —                                 | Mermaid in .md files, rendered by GitHub; no build step |
| docs/71 DEPLOYMENT blueprint                        | Docs (static)              | —                                 | Blueprint-style; no live infra provisioned in Phase 3   |
| docs/72 RUNBOOK                                     | Docs (static)              | —                                 | Operational reference; snippets are illustrative        |
| docs/adr/ ADRs                                      | Docs (static)              | —                                 | Decision records; MADR/Nygard formats in plain Markdown |
| oca-gen-addon-readme hook                           | Pre-commit / CI            | repo root .pre-commit-config.yaml | Generates addons/\*/README.rst from readme/ fragments   |
| docs/60_FASE_1_RETROSPECTIVA.md rename              | Repo filesystem            | All linking files                 | D-05: rename + grep links in 4 locations                |

---

## Standard Stack

### Core (confirmed from existing codebase)

| Library/Tool             | Version        | Purpose                                                               | Why Standard                                                                                                             |
| ------------------------ | -------------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Mermaid (GitHub-native)  | Current (11.x) | C4Context, C4Container, sequenceDiagram, stateDiagram-v2 in .md files | [VERIFIED: mermaid.js.org/syntax/c4.html] Renders natively in GitHub; no build step; text-versionable                    |
| Keep a Changelog 1.1.0   | —              | CHANGELOG.md format                                                   | [VERIFIED: keepachangelog.com/en/1.1.0/] Industry standard; human-readable; clear Unreleased→versioned flow              |
| Contributor Covenant 2.1 | —              | CODE_OF_CONDUCT.md                                                    | [VERIFIED: contributor-covenant.org/version/2/1/code_of_conduct/] OCA standard CoC base; single enforcement placeholder  |
| MADR                     | Current        | ADRs 0004-0005                                                        | [VERIFIED: adr.github.io/madr/] Lightweight, YAML front matter for status, decision-drivers + considered-options pattern |
| Nygard liviano           | —              | ADRs 0001-0003 (retroactive)                                          | [ASSUMED] Industry standard for retroactive ADRs where "considered options" cannot be reconstructed honestly             |

### Supporting (confirmed from existing codebase)

| Library/Tool                | Version                      | Purpose                                              | When to Use                                                                                                                   |
| --------------------------- | ---------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `oca-gen-addon-readme` hook | maintainer-tools @ `b89f767` | Generate addons/\*/README.rst from readme/ fragments | [VERIFIED: codebase] Hook id confirmed present in pinned maintainer-tools commit; always_run=true, pass_filenames=false       |
| infra/docker-compose.yml    | Odoo 18.0 + PG16             | Quick start for CONTRIBUTING.md DOC-10               | [VERIFIED: codebase] Operacional — bind-mounted `addons/` only; command is `docker compose -f infra/docker-compose.yml up -d` |

### Alternatives Considered

| Instead of                | Could Use                       | Tradeoff                                                                              |
| ------------------------- | ------------------------------- | ------------------------------------------------------------------------------------- |
| Mermaid C4 (experimental) | PlantUML C4                     | PlantUML requires external renderer; Mermaid renders in GitHub natively — D-10 locked |
| Keep a Changelog          | Conventional Changelog auto-gen | Auto-gen is Phase 4 REL-06; Phase 3 writes the initial entry manually — D-09 locked   |
| MADR for all ADRs         | Nygard for all ADRs             | Retroactive ADRs 0001-0003 have no honest "options considered" — hybrid D-12 locked   |

---

## Package Legitimacy Audit

This phase installs **no new packages**. The `oca-gen-addon-readme` hook is added to an existing pre-commit repo entry (`oca/maintainer-tools`) already pinned in the repo — no new package install occurs.

**No package legitimacy audit required for this phase.**

---

## Architecture Patterns

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    Phase 3 Document Flow                        │
│                                                                 │
│  Existing Sources                 New/Rewritten Files           │
│  ─────────────────                ─────────────────────────     │
│  infra/docker-compose.yml ──────► README.md (D-02/D-03)         │
│  docs/60_FASE_1_RETROSPECTIVA ──► CHANGELOG.md [0.1.0] (D-06)  │
│  CHANGES.rst ───────────────────► (deleted after migration)     │
│  CONTRIBUTING fragments (README) ► CONTRIBUTING.md (D-03)       │
│  Contributor Covenant 2.1 ──────► CODE_OF_CONDUCT.md (D-04)    │
│                                                                 │
│  docs/03_DOMAIN_MODEL.md ───────► docs/70_ARCHITECTURE.md       │
│  docs/50_MODULES_ROADMAP.md ────►   (C4 + sequence + state)     │
│  docs/60_SECURITY_BASELINE.md ─►  docs/71_DEPLOYMENT.md         │
│  docs/01_SIFEN_KNOWLEDGE_BASE ──►   (blueprint + markers)       │
│  SIFEN operational experience ──► docs/72_RUNBOOK.md (10 inc.)  │
│                                                                 │
│  CONTEXT.md D-12/D-13 ─────────► docs/adr/0001-0005-*.md       │
│                                   docs/adr/README.md            │
│                                                                 │
│  addons/*/readme/*.rst ─────────► addons/*/README.rst (D-07)    │
│  (via oca-gen-addon-readme hook)                                │
└─────────────────────────────────────────────────────────────────┘
```

### Recommended Project Structure (new files)

```
/ (repo root)
├── README.md                         # REWRITE — OCA-style evaluator-first (D-02)
├── CHANGELOG.md                      # NEW — Keep a Changelog 1.1.0 [0.1.0] (D-06)
├── CONTRIBUTING.md                   # NEW — 6 ejes + DOC-09 (D-03)
├── CODE_OF_CONDUCT.md                # NEW — Contributor Covenant 2.1 (D-04)
└── CHANGES.rst                       # DELETE after migration (D-06)

docs/
├── 65_FASE_1_RETROSPECTIVA.md        # RENAME from 60_* (D-05)
├── 70_ARCHITECTURE.md                # NEW — C4 + sequence + state machine (D-11)
├── 71_DEPLOYMENT.md                  # NEW — blueprint + markers (D-14)
├── 72_RUNBOOK.md                     # NEW — 10 incidents (D-15)
└── adr/
    ├── README.md                     # NEW — explains hybrid Nygard/MADR (D-12)
    ├── 0001-odoo-community.md        # NEW — Nygard liviano
    ├── 0002-oca-style-from-day-one.md  # NEW — Nygard liviano
    ├── 0003-dnit-catalogs-source-of-truth.md  # NEW — Nygard liviano
    ├── 0004-multi-rubro-strategy.md   # NEW — MADR stub Proposed (D-13)
    └── 0005-hosting-strategy.md      # NEW — MADR with options (D-12)

addons/l10n_py_base/README.rst        # REGENERATED by oca-gen-addon-readme (D-07)
addons/l10n_py_account/README.rst     # REGENERATED by oca-gen-addon-readme (D-07)
.pre-commit-config.yaml               # ADD oca-gen-addon-readme hook (D-07)
```

---

### Pattern 1: Nygard Lightweight ADR (ADRs 0001-0003)

**What:** Minimal retroactive ADR for a decision that was made without alternatives being formally compared.
**When to use:** When the "options considered" cannot be reconstructed honestly; for decisions that were obvious at the time.

```markdown
# ADR-0001: Odoo Community Edition (not Enterprise)

**Status:** Accepted
**Date:** 2026-05-19
**Refs:** docs/50_MODULES_ROADMAP.md, docs/00_OBJECTIVE.md

## Context

Este proyecto construye módulos AGPL-3 para OCA. OCA publica únicamente en Community.
Odoo Enterprise usa licencia propietaria incompatible con AGPL-3.

## Decision

Usar Odoo Community 18. Todo el código de este repo es AGPL-3.

## Consequences

- Compatible con OCA/l10n-paraguay cuando exista.
- Limita acceso a módulos Enterprise (contabilidad avanzada, etc.) — no relevante
  para el scope de localización fiscal.
- Sin costos de licencia para adopción por PyMEs.
```

### Pattern 2: MADR (ADRs 0004-0005)

**What:** Full MADR with Decision Drivers + Considered Options + Pros/Cons, for decisions where real alternatives were weighed.
**When to use:** When there are genuine competing options that a future reader should understand.

```markdown
---
status: proposed
date: 2026-06-05
decision-makers: ["@Ezcareaga"]
---

# ADR-0004: Estrategia multi-rubro

## Context and Problem Statement

Los módulos `l10n_py_base` y `l10n_py_account` deben funcionar para cualquier
industria paraguaya (minimarket, gastronomía, servicios). ¿Cómo separamos las
asunciones por rubro del código base?

## Decision Drivers

- Reutilización: no duplicar código base por rubro
- Extensibilidad: terceros pueden agregar rubros sin modificar base
- Compatibilidad OCA: seguir convención `l10n_py_industry_*`

## Considered Options

- Opción A: parámetros de configuración por rubro dentro de base/account
- Opción B: módulos `l10n_py_industry_*` independientes que extienden `l10n_py_pos`

## Decision Outcome

**Propuesto:** Opción B. [Phase 5 IND-01 completa este análisis → status: Accepted]

## Consequences

- base y account permanecen rubro-agnósticos
- Rubros = módulos `l10n_py_industry_retail`, `l10n_py_industry_hospitality`, etc.
- Phase 5 auditará el código actual con grep para verificar rubro-agnosticismo
```

### Pattern 3: Blueprint-style Documentation (docs/71, docs/72)

**What:** Docs with operational snippets and explicit validation-deferred markers.
**When to use:** When the implementation will exist in a future phase (Pre-Fase 3 deploy) and snippets are illustrative.

````markdown
## Backup automatizado

**Qué hacemos:** `pg_dump` diario a Backblaze B2 vía rclone. Retención 30d local + 90d offsite.

> Note: validar en Pre-Fase 3 cuando exista deploy real.

```bash
# Ejemplo ilustrativo — ajustar paths y credenciales al VPS real
pg_dump -U odoo l10n_py_prod | gzip > /backup/$(date +%Y%m%d).sql.gz
rclone copy /backup/ b2:l10n-paraguay-backups/
```
````

Ver detalles de estrategia de backup → [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §Backup.

````

### Pattern 4: RUNBOOK Incident Template (docs/72)

**What:** Fixed-format incident template for operational runbook.
**When to use:** For each of the 10 locked incidents.

```markdown
### Incidente N: [Nombre corto]

**Síntoma:** [lo que el operador observa]
**Severidad:** Alta / Media / Baja — [criterio: impacto en facturación / datos]

**Diagnóstico:**
```bash
# Comandos copy-paste para confirmar causa
````

**Resolución:**

1. Paso 1
2. Paso 2

**Prevención:** [qué configura/monitorea para evitarlo]

> Note: [si aplica] procedimiento se valida en Fase 2 EDI / homologación.

````

### Pattern 5: Mermaid C4 (docs/70)

**What:** C4 Context and Container diagrams using Mermaid experimental C4 syntax, rendered natively in GitHub.
**When to use:** For architectural overview; do not go to C4 Code (Component) level per DOC out-of-scope.

```markdown
```mermaid
C4Context
  title System Context — l10n-paraguay (diseño objetivo Fase 2 EDI)

  Person(operator, "Operador PyME", "Factura, gestiona DTEs")
  System(odoo, "Odoo 18 Community + l10n_py_*", "Sistema ERP con facturación electrónica PY")
  System_Ext(sifen, "SIFEN / DNIT", "Plataforma facturación electrónica nacional")
  System_Ext(set, "SET / Marangatú", "Gestión tributaria (timbrado, certificados)")
  System_Ext(bank, "Bancos / Pagos", "Medios de cobro integrados (futuro)")

  Rel(operator, odoo, "Crea facturas, consulta DTEs")
  Rel(odoo, sifen, "Envía XML firmado XAdES via SOAP", "HTTPS")
  Rel(odoo, set, "Obtiene timbrado / valida CCFE", "HTTPS")
  Rel(odoo, bank, "Integración pagos (Fase futura)", "API")
````

````

### Anti-Patterns to Avoid

- **Duplicar contenido de docs/60:** docs/71 LINKEA a docs/60 §Backup y §Network — no copia los comandos. Duplicación implica dos fuentes de verdad.
- **Commitear compose de producción como archivo:** El `docker-compose.prod.yml` va como code block dentro de docs/71, no commiteado. Archivos `.yml` sin un `docker compose up` funcional en el repo driftean silenciosamente.
- **Inventar opciones consideradas en ADRs retroactivos:** ADRs 0001-0003 usan Nygard; fabricar "opciones consideradas" para eventos pasados reduce la credibilidad del ADR file entero.
- **Dejar `[0.1.0] - Unreleased` sin fecha permanentemente:** El heading debe aclarar que la fecha se completa en Phase 4. Ej: `[0.1.0] - Unreleased (see Phase 4 REL-05)`.
- **Smoke test DOC-10 como checklist de agente:** DOC-10 requiere un dev humano real. Crear el issue con el checklist al final de la phase y comunicarlo al maintainer — no simularlo.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| CODE_OF_CONDUCT text | Custom CoC from scratch | Contributor Covenant 2.1 verbatim | [VERIFIED] OCA uses CC as base; GitHub recognizes it for "Community Standards" badge; only placeholder = email |
| CHANGELOG format | Free-form release notes | Keep a Changelog 1.1.0 structure | [VERIFIED] Tooling (auto-changelog, release-please, etc.) expects this format; Phase 4 REL-04 release.yml auto-populates from it |
| ADR template (with options) | Custom format | MADR YAML frontmatter template | [VERIFIED: adr.github.io/madr] Status machine (proposed→accepted), decision-makers, date — all in frontmatter |
| Architecture diagrams | PNG screenshots / draw.io exports | Mermaid inside .md | [VERIFIED: mermaid.js.org] Text-versionable, GitHub-native, diffs in PR |
| Addon README.rst generation | Hand-writing README.rst | `oca-gen-addon-readme` hook | [VERIFIED: codebase] Hook already in pinned maintainer-tools commit; fragments already exist in addons |

---

## Runtime State Inventory

Phase 3 is greenfield documentation (new files + edits to existing docs). No rename of application data, live services, or OS-registered state is involved.

The one "rename" is `docs/60_FASE_1_RETROSPECTIVA.md` → `docs/65_FASE_1_RETROSPECTIVA.md`, which is a file rename with link-update side effects. This is a pure filesystem + markdown links operation — no runtime state.

| Category | Items Found | Action Required |
|----------|-------------|-----------------|
| Stored data | None — no database records reference docs file paths | None |
| Live service config | None — no external service config references these doc paths | None |
| OS-registered state | None | None |
| Secrets/env vars | None | None |
| Build artifacts / links | `docs/60_FASE_1_RETROSPECTIVA.md` referenced in 4 locations: `CLAUDE.md` (line 122), `.planning/PROJECT.md`, `.planning/phases/01-*/01-CONTEXT.md`, `AGENTS.md`. The `.planning/phases/02-*/02-04-PLAN.md` and `02-05-PLAN.md` also reference it as a style anchor — these are historical planning files; update is optional (they are read-only artifacts). | grep + sed rename links in CLAUDE.md + PROJECT.md + AGENTS.md before or simultaneously with the file rename |

**Nothing found in category:** Stored data, live service config, OS-registered state, secrets/env vars — all verified None (docs phase, no infra changes).

---

## Common Pitfalls

### Pitfall 1: `oca-gen-addon-readme` global exclude collision

**What goes wrong:** The global `exclude` block in `.pre-commit-config.yaml` line 19 contains `^README\.rst$`. This anchored pattern matches only the bare path `README.rst` (not `addons/l10n_py_base/README.rst`). However the `trailing-whitespace` and `end-of-file-fixer` hooks use `/README\.rst$` which matches path-endings. The `oca-gen-addon-readme` hook writes `addons/*/README.rst` files. If these files get re-staged by another hook in the same pre-commit run that has a stricter `excluded` pattern, the commit can fail.
**Why it happens:** Hook ordering matters: `oca-gen-addon-readme` runs and generates files, then `trailing-whitespace` runs and would normally touch them — but `trailing-whitespace` already excludes `/README.rst$`, so no conflict.
**How to avoid:** Keep `trailing-whitespace` and `end-of-file-fixer` excludes on `README.rst` (already present in config). Add `oca-gen-addon-readme` to the `maintainer-tools` repo block with no `exclude` override. The `always_run: true` and `pass_filenames: false` flags in the hook definition mean it does not take a file list — it scans all addons.
**Warning signs:** `pre-commit run --all-files` reports `oca-gen-addon-readme` passes but no files were regenerated — means the hook ran but found no changes (expected after first run).

### Pitfall 2: Docs/60 prefix collision not resolved before writing links

**What goes wrong:** If the planner creates docs/70, docs/71, docs/72 before resolving the D-05 rename, those new docs may link to `docs/60_FASE_1_RETROSPECTIVA.md` (old name). After the rename, those links break.
**Why it happens:** Natural wave sequencing temptation to tackle docs/70-72 first (bigger content) while deferring cleanup.
**How to avoid:** D-05 rename must be in Wave 1, before any doc that references retrospective. Confirmed affected files: CLAUDE.md (line 122), AGENTS.md, .planning/PROJECT.md, .planning/phases/01-.../01-CONTEXT.md.

### Pitfall 3: Mermaid C4 syntax breaks on GitHub

**What goes wrong:** GitHub renders `C4Context` and `C4Container` blocks as Mermaid diagrams but the rendering can silently fail if the Mermaid version bundled in GitHub's markdown renderer does not support the C4 keyword. The result is a raw code block shown instead of a diagram.
**Why it happens:** Mermaid C4 support is labeled "experimental" in official docs — syntax may vary between Mermaid versions.
**How to avoid:** Use the `C4Context` / `C4Container` keywords (confirmed syntax as of Mermaid 11.x). Fallback: if C4 renders poorly on GitHub, switch `docs/70` to standard `graph TD` flowchart for the container overview. The `sequenceDiagram` and `stateDiagram-v2` types are fully stable and not at risk.
**Warning signs:** Push the PR for docs/70 and check the rendered preview on github.com — verify diagrams render before merging.

### Pitfall 4: RUNBOOK incidentes SIFEN validated against mock state

**What goes wrong:** Writer invents specific error codes or SOAP response bodies for SIFEN incidentes 1, 4, 5, 7, 10 without operational experience. Runbook looks complete but gives wrong commands in production.
**Why it happens:** Docs phase without live SIFEN access.
**How to avoid:** Per D-15, SIFEN-dependent incidentes carry the marker "procedimiento se valida en Fase 2 EDI / homologación". Diagnóstico commands for those incidents should use generic `curl` / `grep` patterns rather than SIFEN-specific API responses. The ÑandeFact knowledge (incidentes 6, 7, 10) can be documented concretely because it comes from real operational history.
**Warning signs:** Any SIFEN-specific error code (e.g., "code 250", "mensaje RECHAZADO_...") in RUNBOOK that hasn't been verified against docs/02_SIFEN_REFERENCIA_COMPLETA.md.

### Pitfall 5: CODE_OF_CONDUCT missing enforcement contact

**What goes wrong:** The Contributor Covenant 2.1 template has exactly one placeholder `[INSERT CONTACT METHOD]`. Committing without replacing it creates a technically broken CoC (GitHub Community Standards check will warn about it).
**Why it happens:** Template is copy-pasted without reading the fill-in sections.
**How to avoid:** Replace `[INSERT CONTACT METHOD]` with `careagaezz@gmail.com` per D-04. Verify with `grep "INSERT CONTACT" CODE_OF_CONDUCT.md` returning no output.

### Pitfall 6: CHANGELOG entry missing the Pre-Fase 2 Bloque A + B work

**What goes wrong:** `[0.1.0]` only documents Fase 1 (modules) and misses CI/CD (Bloque A Phase 1) and security baseline (Bloque B Phase 2).
**Why it happens:** D-08 says "Fase 1 + foundation Pre-Fase 2" but the author focuses on the module delivery.
**How to avoid:** The `[0.1.0]` Added section should include: `l10n_py_base 18.0.1.1.0`, `l10n_py_account 18.0.1.0.0`, CI/CD pipeline (lint + test + commitlint + dependabot), security workflow (gitleaks + Bandit + dependency-review), security docs (docs/60 + docs/61). Changed: README restructured. Source: `docs/65_FASE_1_RETROSPECTIVA.md` + `docs/60_SECURITY_BASELINE.md`.

---

## Code Examples

### Keep a Changelog [0.1.0] Entry Structure
```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] - Unreleased (see Phase 4 REL-05 for tag date)

### Added
- `l10n_py_base 18.0.1.1.0` — Paraguayan localization base module: SIFEN/DNIT
  catalogs (departments, districts, cities, economic regimes, taxpayer types),
  `l10n_py.timbrado` model, `res.company` PY fiscal extension, RUC/CI validation
  (módulo 11 algorithm), 23 tests
- `l10n_py_account 18.0.1.0.0` — Chart of accounts, IVA taxes (10%/5%/exenta),
  `l10n_latam.document.type` records for Paraguay (FE/NC/ND/NR),
  `account.journal` timbrado extension, 74 tests
- CI/CD pipeline: GitHub Actions lint + test (OCA py3.10/PG12 matrix) +
  commitlint + dependabot
- Security workflow: gitleaks (secret scanning) + Bandit (SAST) +
  Dependency Review
- `SECURITY.md` — vulnerability reporting channel (GitHub Advisories + email)
- `docs/60_SECURITY_BASELINE.md` — 6-axis security blueprint
- `docs/61_COMPLIANCE_LEY_7593.md` — Ley 7593/2025 compliance framework

### Changed
- Branch protection on `main` — PR required, 6 status checks enforced
````

### Mermaid State Machine (DTE lifecycle)

````markdown
```mermaid
stateDiagram-v2
    [*] --> draft : account.move created
    draft --> posted : action_post()
    posted --> to_send : action_send_and_print()
    to_send --> sent : SIFEN aprueba (edi_state=sent)
    to_send --> error : SIFEN rechaza (edi_state=error)
    error --> to_send : retry
    sent --> cancelled : evento de cancelación SIFEN
    posted --> cancelled : cancel_move_button() — sin EDI

    note right of sent
        Diseño objetivo — Fase 2 EDI
        (l10n_py_edi no existe aún)
    end note
```
````

````

### CONTRIBUTING.md Environment Divergence Note
```markdown
## CI Environment vs Local Runtime

> The GitHub Actions CI matrix uses `ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`
> (Python 3.10, PostgreSQL 12 — OCA standard). Local development typically runs
> Python 3.11+ with PostgreSQL 15+. Both are supported; see `infra/docker-compose.yml`
> which uses `postgres:16` and `odoo:18.0` (Python 3.12 upstream image).
>
> If a test passes locally but fails in CI, check for Python 3.10/3.12 syntax
> differences or PostgreSQL version-specific behavior (JSON operators, etc.).
````

### oca-gen-addon-readme pre-commit entry

```yaml
# In .pre-commit-config.yaml, under the existing maintainer-tools repo block:
- repo: https://github.com/oca/maintainer-tools
  rev: b89f767503be6ab2b11e4f50a7557cb20066e667
  hooks:
    - id: oca-fix-manifest-website
      args: ["https://github.com/Ezcareaga/l10n-paraguay"]
    - id: oca-gen-addon-readme # ADD THIS
```

---

## State of the Art

| Old Approach                                 | Current Approach                                             | When Changed | Impact                                                                                     |
| -------------------------------------------- | ------------------------------------------------------------ | ------------ | ------------------------------------------------------------------------------------------ |
| `CHANGES.rst` skeleton                       | `CHANGELOG.md` Keep a Changelog 1.1.0                        | Phase 3 D-06 | GitHub renders .md natively; release tooling (release.yml Phase 4) expects markdown format |
| README with tooling detail (codegraph, venv) | README evaluator-first, contributor detail → CONTRIBUTING.md | Phase 3 D-02 | OCA reviewer sees module status immediately; not buried under setup instructions           |
| No ADRs                                      | `docs/adr/` 0001-0005                                        | Phase 3 D-08 | Decision history prevents "why did we choose X?" questions; DOC-09 keeps it current        |

**Deprecated/outdated:**

- `CHANGES.rst`: replaced by CHANGELOG.md. Delete after migration (D-06).
- Current `README.md` "Estado" section ("Bootstrap inicial completado. Aún no hay código de módulos publicado"): factually incorrect — 2 modules shipped with 97 tests. D-02 fixes this.
- Current `README.md` "Módulos planificados" table with all statuses "TODO": l10n_py_base and l10n_py_account are shipped. Table must reflect real versions (18.0.1.1.0 / 18.0.1.0.0).

---

## Assumptions Log

| #   | Claim                                                                                                   | Section                              | Risk if Wrong                                                                                                     |
| --- | ------------------------------------------------------------------------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------------------------------------------------- |
| A1  | Nygard "lightweight" format (without "Options Considered") is acceptable for retroactive ADRs 0001-0003 | Standard Stack, Code Examples        | Low — D-12 explicitly chooses this; only risk is OCA reviewer expects MADR for all ADRs (easily changed)          |
| A2  | Mermaid C4 blocks (`C4Context`, `C4Container`) render correctly in GitHub's current Mermaid version     | Architecture Patterns, Code Examples | Medium — C4 is "experimental" per docs; fallback is standard `graph TD` flowchart, which is trivial to substitute |
| A3  | The `65_` prefix is free in docs/ and coherent with the numbering series                                | Recommended Project Structure        | Low — confirmed: only 60, 61 exist in docs/6x range; 62-69 are free                                               |

---

## Open Questions

1. **ADR-0005 hosting options (Claude's Discretion)**

   - What we know: D-12 specifies MADR format with Decision Drivers + Considered Options + Pros/Cons; D-14 Ph2 established Backblaze B2 as default for backup (vendor-neutral)
   - What's unclear: Which specific VPS providers to list in Considered Options (Hetzner, Contabo, proveedor local PY?)
   - Recommendation: Planner can populate with Hetzner CX21, Contabo VPS S, and 1 Paraguayan provider (Telecel Cloud or similar) as illustrative options. ADR-0005 stays "Proposed" — no commitment to vendor per D-12.

2. **DOC-10 smoke test issue checklist content**
   - What we know: D-16 = GitHub issue with checklist; steps are clone → setup → docker up → módulos instalados → tests corren
   - What's unclear: What exact friction points to instrument in the checklist
   - Recommendation: Planner writes a 6-7 item checklist covering: (1) clone succeeds, (2) docker compose up exits clean, (3) http://localhost:8069 reachable, (4) DB creation with Country=Paraguay, (5) l10n_py_base installs without error, (6) l10n_py_account installs, (7) `docker exec ... python -m pytest` or Odoo test runner reports 97 green.

---

## Environment Availability

| Dependency  | Required By                                   | Available | Version | Fallback                               |
| ----------- | --------------------------------------------- | --------- | ------- | -------------------------------------- |
| Docker      | D-03 quick start validation, docs/71 snippets | ✓         | 29.4.3  | —                                      |
| Node.js     | Mermaid diagrams render check in browser      | ✓         | 24.16.0 | Not needed (GitHub renders in browser) |
| Python      | pre-commit oca-gen-addon-readme hook          | ✓         | 3.13.13 | —                                      |
| git         | Rename operation D-05                         | ✓         | 2.47.1  | —                                      |
| GitHub (CI) | Branch protection, status checks              | ✓         | —       | —                                      |

**Missing dependencies with no fallback:** None.

**Missing dependencies with fallback:** None.

---

## Validation Architecture

`nyquist_validation: true` — section included.

### Test Framework

| Property           | Value                                                                                                                                                          |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Framework          | Odoo built-in test runner (TransactionCase) invoked via `oca_run_tests` in CI                                                                                  |
| Config file        | `.github/workflows/test.yml` (env `ODOO_TEST_TAGS: "l10n_py"`)                                                                                                 |
| Quick run command  | `docker compose -f infra/docker-compose.yml exec odoo odoo --test-enable --stop-after-init -d l10n_py_dev --test-tags=l10n_py -i l10n_py_base,l10n_py_account` |
| Full suite command | Same (all l10n_py tests = 97)                                                                                                                                  |

### Phase Requirements → Test Map

| Req ID | Behavior                                     | Test Type           | Automated Command                                                                                          | File Exists?                       |
| ------ | -------------------------------------------- | ------------------- | ---------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| DOC-01 | README has no "TODO" in shipped modules      | manual / grep       | `grep -c "TODO" README.md` (expect 0)                                                                      | ❌ manual check                    |
| DOC-02 | CHANGELOG.md exists with [0.1.0] entry       | manual              | `grep "\[0.1.0\]" CHANGELOG.md`                                                                            | ❌ Wave 0 — file doesn't exist yet |
| DOC-03 | CONTRIBUTING.md covers 6 ejes                | manual              | `grep -c "pre-commit\|Conventional Commits\|branch naming\|code review\|cobertura\|setup" CONTRIBUTING.md` | ❌ Wave 0                          |
| DOC-04 | CODE_OF_CONDUCT.md has no `[INSERT CONTACT]` | grep                | `grep "INSERT CONTACT" CODE_OF_CONDUCT.md \|\| echo "OK"`                                                  | ❌ Wave 0                          |
| DOC-05 | docs/70 contains C4 and state machine        | manual render check | Verify Mermaid blocks parse: `node -e "const m = require('@mermaid-js/mermaid-zenuml')"` (optional)        | ❌ Wave 0                          |
| DOC-06 | docs/71 contains VPS/backup/Caddy sections   | grep                | `grep -c "Caddy\|backup\|health check" docs/71_DEPLOYMENT.md`                                              | ❌ Wave 0                          |
| DOC-07 | docs/72 covers ≥10 incidents                 | grep                | `grep -c "^### Incidente" docs/72_RUNBOOK.md` (expect ≥10)                                                 | ❌ Wave 0                          |
| DOC-08 | docs/adr/ has 5 ADR files                    | ls                  | `ls docs/adr/000*.md \| wc -l` (expect 5)                                                                  | ❌ Wave 0                          |
| DOC-09 | CONTRIBUTING.md contains ADR rule            | grep                | `grep -c "ADR\|mismo PR\|same PR" CONTRIBUTING.md`                                                         | ❌ Wave 0                          |
| DOC-10 | Smoke test issue exists                      | manual              | GitHub issue created; async UAT                                                                            | ❌ Wave 4 — created as final step  |

### Sampling Rate

- **Per task commit:** `grep -c "TODO" README.md; grep "\[0.1.0\]" CHANGELOG.md; grep "INSERT CONTACT" CODE_OF_CONDUCT.md || echo OK`
- **Per wave merge:** Full grep audit across all new files per wave
- **Phase gate:** `ls docs/70_ARCHITECTURE.md docs/71_DEPLOYMENT.md docs/72_RUNBOOK.md docs/adr/000*.md` returns 8 files; `grep -c "TODO" README.md` returns 0; `pre-commit run --all-files` clean

### Wave 0 Gaps

All 10 target files are new (none exist yet). No test framework changes needed — validation is grep-based, not test-runner-based.

- [ ] `CHANGELOG.md` — covers DOC-02
- [ ] `CONTRIBUTING.md` — covers DOC-03, DOC-09
- [ ] `CODE_OF_CONDUCT.md` — covers DOC-04
- [ ] `docs/70_ARCHITECTURE.md` — covers DOC-05
- [ ] `docs/71_DEPLOYMENT.md` — covers DOC-06
- [ ] `docs/72_RUNBOOK.md` — covers DOC-07
- [ ] `docs/adr/README.md` + `docs/adr/0001-0005-*.md` — covers DOC-08

---

## Security Domain

`security_enforcement` not explicitly false — section included.

### Applicable ASVS Categories

| ASVS Category         | Applies | Standard Control              |
| --------------------- | ------- | ----------------------------- |
| V2 Authentication     | no      | Phase 3 is documentation-only |
| V3 Session Management | no      | Documentation-only            |
| V4 Access Control     | no      | Documentation-only            |
| V5 Input Validation   | no      | No user input in static docs  |
| V6 Cryptography       | no      | Documentation-only            |

**Security-relevant content in this phase (not ASVS-gated but important):**

- `CODE_OF_CONDUCT.md` exposes maintainer email (`careagaezz@gmail.com`) publicly in enforcement section. This is intentional per D-04 and consistent with the email already in `SECURITY.md`. No new exposure.
- `CONTRIBUTING.md` will document pre-commit hooks including security hooks (gitleaks, Bandit). No sensitive content exposed.
- `docs/72_RUNBOOK.md` will contain operational commands for diagnosis. Avoid hardcoding real credentials in snippets — use `$VAR` placeholders.
- `docs/71_DEPLOYMENT.md` contains Caddyfile snippet with domain placeholder — do not use real domain names until Pre-Fase 3.

---

## Project Constraints (from CLAUDE.md)

| Constraint                                                           | Source           | Impact on Phase 3                                                                                                                                 |
| -------------------------------------------------------------------- | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Código en inglés                                                     | CLAUDE.md / D-01 | README, CONTRIBUTING, CHANGELOG, CODE_OF_CONDUCT in English                                                                                       |
| Documentación en docs/, comentarios en español                       | CLAUDE.md / D-01 | docs/70-72 and ADRs in Spanish                                                                                                                    |
| OCA conventions estrictas                                            | CLAUDE.md        | README OCA-style; CC 2.1; CONTRIBUTING covers 6 required ejes                                                                                     |
| No leer references/ manualmente — usar codegraph                     | CLAUDE.md        | If pattern research needed from l10n-brazil README, use `bin/codegraph.ps1 search`                                                                |
| Subagent default Phase 3: `voltagent-dev-exp:documentation-engineer` | STATE.md         | Primary executor for all Wave work; `architect-reviewer` (opus) can review docs/70 + ADRs                                                         |
| Atomic commits + Conventional Commits                                | CLAUDE.md        | Commit type for doc files: `docs(scope): description`; D-07 readme regen = own commit `chore(pre-commit): activate oca-gen-addon-readme baseline` |
| GSD Workflow Enforcement — all code edits via plan                   | CLAUDE.md        | No inline edits; planner produces PLAN.md files consumed by `gsd-executor`                                                                        |

---

## Sources

### Primary (HIGH confidence)

- Codebase inspection — `.pre-commit-config.yaml`, `infra/docker-compose.yml`, `addons/*/readme/`, `docs/60_SECURITY_BASELINE.md`, `docs/01_SIFEN_KNOWLEDGE_BASE.md`, `docs/03_DOMAIN_MODEL.md`, `docs/60_FASE_1_RETROSPECTIVA.md`, `README.md`, `CHANGES.rst` — all read directly
- `gh api repos/oca/maintainer-tools/contents/.pre-commit-hooks.yaml?ref=b89f767...` — confirmed `oca-gen-addon-readme` hook id present at pinned commit
- [mermaid.js.org/syntax/c4.html](https://mermaid.js.org/syntax/c4.html) — C4 experimental status confirmed
- [keepachangelog.com/en/1.1.0/](https://keepachangelog.com/en/1.1.0/) — format and Unreleased section verified
- [contributor-covenant.org/version/2/1/code_of_conduct/](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) — CC 2.1 structure and single placeholder confirmed
- [adr.github.io/madr/](https://adr.github.io/madr/) — MADR template sections confirmed

### Secondary (MEDIUM confidence)

- WebSearch "Mermaid C4 diagram GitHub rendering native support 2025" — confirmed GitHub renders C4 natively; multiple sources agree. [CITED: mermandraw.com/blog/how-to-add-mermaid-to-github-readme/]

### Tertiary (LOW confidence)

- Nygard lightweight ADR format for retroactive ADRs — [ASSUMED] based on community convention; no single authoritative spec

---

## Metadata

**Confidence breakdown:**

- Standard stack: HIGH — all tools verified from codebase and official docs
- Architecture: HIGH — all decisions locked in CONTEXT.md; implementation is mechanical
- Pitfalls: HIGH for oca-gen-addon-readme and naming collision (D-05); MEDIUM for Mermaid C4 rendering on GitHub (experimental tag)

**Research date:** 2026-06-05
**Valid until:** 2026-07-05 (stable domain — docs format specs don't change fast; Mermaid C4 status could change sooner)
