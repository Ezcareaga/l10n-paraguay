# Phase 3: Bloque C — Documentación operacional - Context

**Gathered:** 2026-06-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Producir la documentación operacional que permite a un dev externo (sin
contexto previo) levantar el proyecto local, entender la arquitectura, saber
cómo se despliega y qué hacer ante los ~10 incidentes más probables, leyendo
solo raíz + `docs/`. Cubre 10 REQs (DOC-01..10): `README.md` real,
`CHANGELOG.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
`docs/70_ARCHITECTURE.md`, `docs/71_DEPLOYMENT.md`, `docs/72_RUNBOOK.md`,
`docs/adr/` con ADRs 0001-0005, regla ADR-en-mismo-PR en CONTRIBUTING, y
smoke test humano de los docs.

Esta phase **NO** crea issue/PR templates ni CODEOWNERS ni release.yml
(Phase 4), **NO** escribe el contenido final del ADR-0004 multi-rubro
(Phase 5 IND-01 — acá solo el stub), **NO** provisiona VPS ni deploy real
(Pre-Fase 3), **NO** implementa el restore-smoke ejecutable (stub ya existe
de Phase 2). Cualquier idea sobre esos bloques va a Deferred.

</domain>

<decisions>
## Implementation Decisions

### Idioma y estructura del README (DOC-01, DOC-04)

- **D-01: Idioma split — inglés en raíz, español en docs/.** README,
  CONTRIBUTING, CODE*OF_CONDUCT y CHANGELOG se escriben en **inglés** (son
  los archivos que el reviewer OCA mira primero — cero retrabajo en Fase 6).
  `docs/70-72` + ADRs 0001-0005 en **español**, consistentes con los ~25
  docs existentes (audiencia operacional local). \_Razón:* OCA exige inglés
  en meta files; docs/ ya tiene convención española establecida.

- **D-02: README estructura OCA-style, evaluador primero.** Orden: qué es →
  tabla de módulos con estado REAL (versiones `18.0.1.1.0`/`18.0.1.0.0`,
  97 tests, sin "TODO" en módulos shipped) → installation (addons-path) →
  quick start docker-compose → links a docs/ → sección dev que delega a
  CONTRIBUTING.md. El detalle de codegraph/references/venv del README actual
  **se muda a CONTRIBUTING.md** (es tooling de contribuidor, no de evaluador).

- **D-03: Quick start reusa el `docker-compose.yml` existente.** Un solo
  compose en el repo: clone → `docker compose up` → instalar
  `l10n_py_base` + `l10n_py_account` → login. Es exactamente el camino que
  DOC-10 smoke-testea. El compose prod vive como code block dentro de
  docs/71 (ver D-14), no como segundo archivo.

- **D-04: CODE_OF_CONDUCT = Contributor Covenant 2.1** (base del CoC de
  OCA, estándar GitHub). Contacto de enforcement: el email del maintainer
  (`careagaezz@gmail.com`, mismo canal fallback que SECURITY.md).

- **D-05: Resolver colisión de numeración docs/60.** Renombrar
  `docs/60_FASE_1_RETROSPECTIVA.md` → `docs/65_FASE_1_RETROSPECTIVA.md`
  (o número libre equivalente), liberando el prefijo `60` para
  `60_SECURITY_BASELINE.md`. Actualizar TODOS los links que lo referencian
  (CLAUDE.md, PROJECT.md, docs internos — verificar con grep).

### Estrategia changelog (DOC-02)

- **D-06: `CHANGELOG.md` reemplaza `CHANGES.rst`.** Migrar el contenido del
  skeleton a CHANGELOG.md formato Keep a Changelog (en inglés, per D-01) y
  **eliminar** `CHANGES.rst`. Un solo changelog repo-level. Per-addon: los
  cambios por módulo van en `readme/HISTORY.rst` de cada addon según
  convención OCA, sin duplicar el repo-level.

- **D-07: Activar hook `oca-gen-addon-readme` en esta phase.** Los
  `readme/` fragment trees ya existen en ambos addons (la condición que
  Phase 1 dejó escrita se cumplió). Sumar el hook a
  `.pre-commit-config.yaml`; regenera `README.rst` per-addon desde
  fragments. El diff cosmético inicial se absorbe en un commit propio
  (patrón baseline de Phase 1 D-05).

- **D-08: Entry `[0.1.0]` = todo hasta el tag de Phase 4.** Documenta
  módulos Fase 1 (l10n_py_base 18.0.1.1.0 + l10n_py_account 18.0.1.0.0,
  97 tests) + foundation Pre-Fase 2 (CI, security baseline, docs
  operacionales), organizado en categorías Added/Changed/Fixed. La fecha
  del entry se completa cuando Phase 4 (REL-05) taggea. Hasta entonces el
  heading puede ser `[0.1.0] - Unreleased` o equivalente.

- **D-09: Mantenimiento del CHANGELOG = compilar al release.** Sin
  obligación per-PR. CHANGELOG.md se actualiza como paso del release
  process (que Phase 4 REL-06 documentará en CONTRIBUTING), compilando
  desde los Conventional Commits acumulados. Alineado con "cero ceremonia
  1 maintainer" y con release.yml de Phase 4.

### ARCHITECTURE + ADRs (DOC-05, DOC-08, DOC-09)

- **D-10: Diagramas en Mermaid.** Renderiza nativo en GitHub, texto
  versionable dentro del mismo .md. `C4Context`/`C4Container` (sintaxis
  experimental Mermaid, aceptada), `sequenceDiagram` para emisión FE,
  `stateDiagram-v2` para ciclo DTE. Sin PlantUML, sin PNGs commiteados.

- **D-11: docs/70 = doc completo con estados explícitos.** C4 Context +
  Container muestran los 6 módulos (`l10n_py_base/account/edi/reports/pos/
withholding`) con marker visual shipped/planned. El sequence diagram FE
  end-to-end y el state machine DTE se etiquetan **"diseño objetivo —
  Fase 2 EDI"** y sirven como spec de entrada para esa fase. Un solo doc
  vivo que evoluciona planned→shipped.

- **D-12: ADR template híbrido.** ADRs 0001-0003 (retroactivos — Odoo
  Community, OCA-style day one, DNIT catalogs source of truth) en **Nygard
  liviano** (Status/Context/Decision/Consequences + fecha + refs) — sin
  inventar "opciones consideradas" a posteriori. ADRs 0004 (multi-rubro) y
  0005 (hosting) en **MADR** con Decision Drivers + Considered Options +
  Pros/Cons, porque sí tienen opciones reales abiertas. Dos formatos
  conviven deliberadamente; un README.md en docs/adr/ explica el criterio.
  _Nota: el usuario eligió el híbrido sobre la recomendación Nygard-only —
  decisión deliberada, no default._

- **D-13: ADR-0004 = stub Proposed en Phase 3; Phase 5 lo completa.**
  Phase 3 crea `docs/adr/0004-multi-rubro-strategy.md` con status
  **Proposed**, el statement central (base/account rubro-agnósticos;
  rubros = módulos `l10n_py_industry_*` que extienden `l10n_py_pos`) y
  skeleton MADR. Phase 5 (IND-01) completa el análisis de opciones y lo
  pasa a Accepted tras la auditoría grep. DOC-08 se cumple (los 5 archivos
  existen), IND-01 mantiene ownership del contenido.

### DEPLOYMENT + RUNBOOK (DOC-06, DOC-07, DOC-10)

- **D-14: docs/71 = blueprint estilo docs/60, compose inline.** Mismo
  patrón que Phase 2 D-09: qué hacemos / por qué / snippets ilustrativos
  con marker `> Note: validar en Pre-Fase 3 cuando exista deploy real`.
  El docker-compose prod + Caddyfile van como **code blocks dentro del
  doc**, no como archivos commiteados (evita artefactos huérfanos que
  driftean). Contenido alineado con Phase 2: backup pg_dump + Backblaze B2
  offsite (D-12 Ph2), restore-smoke checklist, network security de docs/60.

- **D-15: RUNBOOK = 10 incidentes con template fijo + escalation 3
  niveles.** Lista locked:

  1. SIFEN timeout (del REQ)
  2. Postgres disk full (del REQ)
  3. SSL cert expira (del REQ)
  4. CCFE expira (del REQ)
  5. Migración catálogos DNIT (del REQ)
  6. Timbrado vencido/agotado — bloquea facturación
  7. DTE rechazado por SIFEN (errores de validación masivos post-deploy)
  8. Restore de backup falla en el test mensual
  9. Update de módulo rompe la DB (migration error — rollback procedure)
  10. Cron/queue de envío EDI atascado (DTEs sin transmitir >72h — plazo legal)

  Template fijo por incidente: Síntoma / Severidad / Diagnóstico (comandos
  copy-paste) / Resolución (pasos numerados) / Prevención. Escalation path
  único al final del doc: **N1** operador del deploy → **N2** Careaga Dev
  (canal + SLA orientativo) → **N3** externo (mesa de ayuda SIFEN/DNIT,
  soporte VPS provider, comunidad OCA). Los incidentes 1, 4, 5, 7 y 10
  (SIFEN-dependientes) llevan marker "procedimiento se valida en Fase 2
  EDI / homologación" donde aplique.

- **D-16: Smoke test DOC-10 = dev externo real + checklist en issue.**
  Reclutar un colega dev sin contexto del repo que siga CONTRIBUTING.md en
  su máquina. Resultado registrado en un GitHub issue con checklist
  (clone → setup → docker up → módulos instalados → tests corren) +
  fricciones encontradas. El REQ cierra cuando el issue documenta el pase.
  Para el flujo GSD: Phase 3 queda "implemented" al mergear los docs;
  DOC-10 es el UAT item de la phase (verificación humana asíncrona, no
  bloquea el avance a Phase 4 — se trackea como item abierto).

### Claude's Discretion

Áreas donde researcher/planner tienen libertad sin reabrir discuss:

- Número exacto del rename de la retrospectiva (D-05) — `65_` u otro
  prefijo libre coherente con la serie de docs/.
- Wording/secciones exactas de CONTRIBUTING.md más allá de los 6 ejes del
  REQ (setup, branch naming, Conventional Commits, code review, testing
  ≥80%, pre-commit) + regla DOC-09 ADR-en-mismo-PR + lo migrado del README
  (codegraph, references, venv). Documentar la divergencia CI (OCA image
  py3.10+PG12) vs runtime local (py3.11+/PG15+) — A-01 Phase 1.
- Estructura del checklist del issue DOC-10 (D-16).
- Contenido de ADR-0005 hosting: opciones MADR a comparar (Hetzner vs
  Contabo vs proveedor local PY, etc.) — preliminar sin commit a vendor,
  consistente con D-12 Phase 2 (B2 default, vendor-neutral).
- Versión/pin exacto del hook `oca-gen-addon-readme` (D-07) — researcher
  confirma invocación como pre-commit hook y compatibilidad con el ref de
  `OCA/maintainer-tools` pinneado en Phase 1 D-02.
- Orden de PRs / waves de la phase (planner decide; sugerencia natural:
  meta files raíz → docs/70-72 → ADRs, con el rename D-05 temprano para
  no romper links dos veces).
- Badges adicionales del README solo si aportan — mantener los 6
  existentes salvo razón.

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source spec del milestone

- `docs/55_PRE_FASE_2_FOUNDATION.md` §"Bloque C — Documentación operacional"
  — output esperado, DoD, riesgo over-engineering ("minimum viable docs")
- `.planning/REQUIREMENTS.md` §"DOC — Bloque C" — los 10 REQs DOC-01..10
  literales (locked)
- `.planning/ROADMAP.md` §"Phase 3" — goal, dependencies (Phase 2),
  success criteria, complexity=large 4-5 días, paralelizable con Phase 5
- `.planning/PROJECT.md` §"Active" + §"Constraints" — milestone activo,
  constraint idioma (código inglés / comentarios español / UI español)

### Decisiones heredadas de phases previas (carry-forward)

- `.planning/phases/02-bloque-b-security-baseline/02-CONTEXT.md` — D-09
  (estilo blueprint + markers Pre-Fase 3), D-12 (backup pg_dump + B2),
  D-05/D-06 (canales SECURITY.md que CoC/README referencian), Deferred
  (restore-smoke ejecutable es Pre-Fase 3)
- `.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/01-CONTEXT.md`
  — D-02 (pins OCA maintainer-tools/odoo-pre-commit-hooks que D-07 debe
  respetar), A-01 (divergencia CI py3.10/PG12 vs runtime 3.11+/PG15+ que
  CONTRIBUTING documenta), Deferred (`oca-gen-addon-readme` reactivable en
  Phase 3 — ahora activado por D-07)
- `docs/60_SECURITY_BASELINE.md` — los 6 ejes que docs/71 referencia
  (backup, network security); NO duplicar contenido, linkear
- `docs/61_COMPLIANCE_LEY_7593.md` — referenciado desde docs/71/72 donde
  toque datos personales

### Materia prima para los docs a escribir

- `docs/50_MODULES_ROADMAP.md` — fases macro + módulos planned para el C4
  Container con estados (D-11)
- `docs/03_DOMAIN_MODEL.md` + `docs/05_DATA_MODEL.md` — fuente para el
  sequence diagram FE y state machine DTE de docs/70 (no duplicar — docs/70
  es overview, estos son el detalle)
- `docs/01_SIFEN_KNOWLEDGE_BASE.md` — ciclo DTE, eventos, plazos (72h)
  para runbook incidentes 7 y 10
- `docs/60_FASE_1_RETROSPECTIVA.md` (a renombrar a `65_` per D-05) —
  material para CHANGELOG [0.1.0] y ADRs retroactivos
- `docs/20_OCA_GUIDELINES.md` + `docs/21_OCA_DEVELOPMENT_BOOK.md` —
  convenciones para README OCA-style y readme/ fragments
- `CHANGES.rst` (raíz) — skeleton a migrar y eliminar (D-06)
- `README.md` (raíz) — badges existentes a conservar; estructura a
  reemplazar per D-02
- `docker-compose.yml` (raíz) — base del quick start D-03
- `addons/l10n_py_base/readme/` + `addons/l10n_py_account/readme/` —
  fragment trees existentes para D-07
- `SECURITY.md` — canal de reporte que README/CoC linkean

### Referencias externas (formato)

- Keep a Changelog 1.1 — `https://keepachangelog.com/en/1.1.0/` (D-06/D-08)
- Contributor Covenant 2.1 —
  `https://www.contributor-covenant.org/version/2/1/code_of_conduct/` (D-04)
- MADR template — `https://adr.github.io/madr/` (D-12, ADRs 0004/0005)
- Mermaid C4 syntax — `https://mermaid.js.org/syntax/c4.html` (D-10;
  researcher verifica estado actual de la sintaxis experimental)
- OCA `oca-gen-addon-readme` — `OCA/maintainer-tools` (D-07; researcher
  confirma invocación como pre-commit hook y pin)

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- **README.md badges (6)** — CI, pre-commit, security, codecov, license,
  Odoo ya están correctos (Phase 1+2). El refactor D-02 los conserva tal
  cual en el header.
- **`readme/` fragment trees** en ambos addons + `README.rst` — base para
  D-07; verificar que los fragments reflejen estado real antes de
  regenerar.
- **`docker-compose.yml` dev operacional** — quick start D-03 lo usa sin
  cambios; documentar la secuencia exacta de instalación de módulos que
  los 97 tests ya validan.
- **`docs/60_SECURITY_BASELINE.md` + `docs/61_COMPLIANCE_LEY_7593.md`**
  (Phase 2 Wave 4) — docs/71 linkea sus ejes backup/network; estilo
  blueprint a imitar (D-14).
- **`scripts/restore-smoke.sh` stub** (Phase 2) — runbook incidente 8 lo
  referencia; NO reimplementar.

### Established Patterns

- **Estilo docs operacional, no académico** (Phase 2 specifics): tablas +
  bullets + code blocks + paths absolutos; evitar prosa larga.
- **Markers de validación diferida**: `> Note: validar en Pre-Fase 3
cuando exista deploy real` (Phase 2 D-09) — aplicar en docs/71-72.
- **No leer `references/` manualmente** — usar `bin/codegraph` si hace
  falta inspeccionar patrones OCA (ej. READMEs de l10n-brazil).
- **Atomic commits + Conventional Commits** — commits `docs(...)`/`chore(...)`;
  el diff de regeneración README.rst (D-07) va en commit propio.
- **Branch protection activa** — todo va por PR contra `main` con los 6
  status checks verdes.
- **Subagent default Phase 3** (STATE.md): `voltagent-dev-exp:documentation-engineer`
  como subagent primario; `architect-reviewer` (opus) puede revisar
  docs/70 + ADRs.

### Integration Points

- **`README.md`** — reescritura completa (estructura D-02, inglés D-01).
- **`CHANGELOG.md`** (nuevo) / **`CHANGES.rst`** (eliminar) — D-06.
- **`CONTRIBUTING.md`** (nuevo) — 6 ejes + DOC-09 + contenido migrado del
  README + divergencia CI/runtime.
- **`CODE_OF_CONDUCT.md`** (nuevo) — CC 2.1, D-04.
- **`docs/70_ARCHITECTURE.md`**, **`docs/71_DEPLOYMENT.md`**,
  **`docs/72_RUNBOOK.md`** (nuevos) — D-10/11/14/15.
- **`docs/adr/0001..0005-*.md`** + **`docs/adr/README.md`** (nuevos) —
  D-12/13.
- **`docs/60_FASE_1_RETROSPECTIVA.md`** → rename a `65_` (D-05) + grep de
  links rotos (CLAUDE.md, .planning/, docs/).
- **`.pre-commit-config.yaml`** — sumar `oca-gen-addon-readme` (D-07).
- **`addons/*/README.rst`** — regenerados por el hook (commit propio).
- **GitHub issue DOC-10** — creado al final de la phase con el checklist
  del smoke test (D-16).

</code_context>

<specifics>
## Specific Ideas

- **El reviewer OCA es el lector que ordena las prioridades.** Idioma
  inglés en raíz, README OCA-style, CC 2.1: todas las decisiones del
  área 1 optimizan para que Fase 6 (migración a OCA/l10n-paraguay) no
  requiera retrabajo de meta files.
- **docs/70 como spec de entrada para Fase 2 EDI.** Los diagramas de
  emisión FE y ciclo DTE etiquetados "diseño objetivo" no son decorativos:
  el milestone siguiente los consume como contrato visual (D-11).
- **Cero ceremonia 1-maintainer se mantiene** (heredado Phase 2):
  changelog compilado al release (no per-PR), blueprint con markers en vez
  de artefactos prod commiteados, escalation path realista (N2 = Careaga
  Dev, no un SOC inventado).
- **El RUNBOOK hereda conocimiento ÑandeFact**: los incidentes 6, 7 y 10
  (timbrado agotado, DTE rechazado, cola >72h) vienen de la experiencia
  operando SIFEN real con vendedoras de mercado.

</specifics>

<deferred>
## Deferred Ideas

### Fuera de scope Phase 3 — capturar para phases/milestones futuros

- **Contenido completo del ADR-0004 multi-rubro** — Phase 5 (IND-01)
  completa el stub Proposed → Accepted con análisis MADR + auditoría grep.
- **Issue/PR templates, CODEOWNERS, release.yml, tag v0.1.0** — Phase 4
  (REL-01..05). La fecha del CHANGELOG [0.1.0] se completa ahí.
- **Release process en CONTRIBUTING (semantic-release vs manual)** —
  Phase 4 REL-06 agrega la sección; Phase 3 deja el placeholder/heading.
- **Deploy real (VPS + Caddy + Postgres prod) + validación de docs/71** —
  Pre-Fase 3. Los snippets llevan marker.
- **`scripts/restore-smoke.sh` ejecutable** — Pre-Fase 3 (ya diferido en
  Phase 2).
- **Validación de procedimientos SIFEN del runbook (incidentes 1, 4, 5,
  7, 10)** — Fase 2 EDI / homologación con CCFE de prueba.
- **Migración de docs/ españoles a inglés** — Fase 6 OCA si OCA lo exige
  para docs no-meta (probable que docs/ técnicos puedan quedar locales).
- **Traducción español del README (README.es.md)** — post-OCA si la
  comunidad local lo pide; hoy el split D-01 cubre ambas audiencias.

### Reviewed Todos (not folded)

No aplica — `gsd-sdk query todo.match-phase 3` devolvió `todo_count: 0`.

</deferred>

---

_Phase: 3-bloque-c-documentaci-n-operacional_
_Context gathered: 2026-06-05_
