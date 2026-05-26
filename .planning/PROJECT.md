# l10n-paraguay

## What This Is

Suite de 6 módulos OCA-style (`l10n_py_*`) para la localización fiscal de
Paraguay sobre **Odoo Community 18**, cubriendo el ciclo completo de
facturación electrónica DNIT/SIFEN: plan de cuentas, impuestos, timbrado,
documentos electrónicos (FE/AF/NC/ND/NR), CDC, firma XAdES, SOAP SIFEN, KuDE,
eventos, libros IVA, Hechauka, POS y retenciones. Audiencia inicial: PyMEs
paraguayas con punto de venta físico (minimarkets, comercios de barrio,
gastronomía pequeña).

## Core Value

**Hacer cumplimiento SIFEN posible sin SaaS pago ni soluciones cerradas** —
módulos AGPL-3 reutilizables por toda la comunidad Odoo Paraguay, con conexión
directa a DNIT (sin IAP, sin proveedores intermedios), tests verdes y docs OCA-
compliant. Si todo lo demás falla, ESTO tiene que funcionar: una PyME monta
Odoo Community + estos módulos y factura legalmente en Paraguay.

## Requirements

### Validated

<!-- Shipped y confirmado en `main`. Versionado en CHANGES.rst de cada módulo. -->

**`l10n_py_base 18.0.1.1.0`** — Fase 1a + 1b (PR #1, mergeado 2026-05-25):

- ✓ **REQ-BASE-01**: Catálogos SIFEN cargados (regímenes, tipos de contribuyente,
  naturaleza receptor, departamentos, distritos, ciudades, identification types) — Fase 1a
- ✓ **REQ-BASE-02**: Validación módulo 11 RUC + CI con `@api.constrains` — Fase 1a
- ✓ **REQ-BASE-03**: Modelo `l10n_py.economic_activity` (catálogo SIFEN actividades) — Fase 1b
- ✓ **REQ-BASE-04**: Extensión `res.company` con campos PY (taxpayer type, regime,
  economic activities M2M, nombre fantasía, DV computed) — Fase 1b
- ✓ **REQ-BASE-05**: Tab "Paraguay (Fiscal)" en form view de `res.company` (visible solo si country==PY) — Fase 1b
- ✓ **REQ-BASE-06**: 23 tests verdes, módulo instalable sin warnings en DB limpia — Fase 1

**`l10n_py_account 18.0.1.0.0`** — Fase 1b (PR #2, mergeado 2026-05-25):

- ✓ **REQ-ACC-01**: Chart of accounts paraguayo (139 cuentas + 164 grupos jerárquicos, RG 49/14)
- ✓ **REQ-ACC-02**: Taxes IVA (10%, 5%, exenta, 0% exportación) con repartition lines
- ✓ **REQ-ACC-03**: `l10n_latam.document.type` records (FE=1, AF=4, NC=5, ND=6, NR=7) + `_format_document_number` override (3-3-7 zero-pad)
- ✓ **REQ-ACC-04**: Modelo `l10n_py.timbrado` (8 dígitos, single-active per company, sql uniqueness)
- ✓ **REQ-ACC-05**: Modelo `l10n_py.point_of_emission` (3 dígitos zero-pad, unique por est+code+company)
- ✓ **REQ-ACC-06**: Modelo `l10n_py.afectacion_iva` (Tabla 6 SIFEN: Gravado/Exonerado/Exento/Parcial)
- ✓ **REQ-ACC-07**: Sequence per doc_type en `account.move` (3 mecanismos: `_auto_init` index rebuild, `_get_sequence_cache` scoped, `_get_last_sequence_domain` filter)
- ✓ **REQ-ACC-08**: Wizard de migración chart (clean/assisted/coexist) para companies con CoA preexistente
- ✓ **REQ-ACC-09**: `_post_init_hook` defensivo (desactiva sale journals PY sin PoE, crea mail activity)
- ✓ **REQ-ACC-10**: 74 tests verdes incluyendo smoke E2E PyME (compra+venta+cuadre IVA)

### Active

<!-- Pendiente: el usuario va a pasar el archivo del milestone Fase 2
(`l10n_py_edi`). Esta sección se completa en /gsd:new-milestone o
al definir REQUIREMENTS.md del milestone. -->

- [ ] **Milestone Fase 2 — `l10n_py_edi`**: scope a definir cuando el usuario
  pase el archivo de contexto del milestone. Roadmap macro
  [`docs/50_MODULES_ROADMAP.md`](../docs/50_MODULES_ROADMAP.md#fase-2) propone:
  CDC + XML builder (grupos AA/A/B/C/D/E/F/H) + firma XAdES + cliente SOAP +
  eventos + KuDE + wizards cancelación/inutilización + homologación
  sifen-test.set.gov.py.

### Out of Scope

<!-- Boundaries explícitas con razonamiento para prevenir re-adición. -->

- **Odoo Enterprise** — proyecto target Community puro. Si Enterprise requiere
  algo, se documenta workaround community o se saltea. Compatibilidad
  Enterprise puede vivir aparte si surge demanda pagada.
- **Backports Odoo <18.0** — hasta que módulos estén estables y haya demanda.
  Sin recursos para mantener matrix 16/17/18 ahora.
- **SaaS / hosting** — software es self-hosted o gestionado por terceros.
  Careaga Dev cobra consultoría, no software.
- **IAP / proveedores intermedios** — conexión SIFEN directa contra DNIT.
  Sin TIPS-SA, sin OSE, sin Mendieta SDK.
- **Grandes empresas con flujos custom Enterprise** — audiencia es PyME.
  Implementaciones grandes pueden requerir customizaciones fuera del scope OCA.
- **Sectores regulados con régimen especial** (farmacias, importadores con ICE,
  combustibles) — pueden requerir módulos adicionales fuera de este repo.
- **Fork de Odoo** — siempre módulos addons, nunca tocar core upstream.
- **Modelos paralelos a Odoo core** — no crear `l10n_py.invoice` cuando
  `account.move` ya sirve. Rompe integración con sale/purchase/pos/stock.

## Context

**Brownfield rico.** Repo arrancado 2026-05-19. Fase 1 completa al 2026-05-25
con 97 tests verdes (l10n_py_base 23 + l10n_py_account 74), 2 PRs mergeados a
`main` vía rebase. Docker Compose Odoo 18 + Postgres 16 operacional con bind
mount `addons/`. Workflow GSD nunca ejecutado en este repo (`.planning/` se
crea ahora, esto es la primera invocación).

**Documentación previa robusta** (vive toda en
[`docs/`](../docs/)):
- Knowledge base SIFEN conceptual + referencia técnica completa
  (`01_SIFEN_KNOWLEDGE_BASE.md`, `02_SIFEN_REFERENCIA_COMPLETA.md`)
- Modelo de dominio, casos de uso, modelo de datos (`03-05`)
- Guías Odoo 18 (estructura módulo, ORM, vistas, seguridad, testing,
  `account_edi`) (`10-15`)
- OCA guidelines + development book (`20-21`)
- Referencias l10n latam (Perú, Ecuador, Argentina, Brasil) con análisis cross-
  pattern (`30-34`)
- Librerías Python runtime (`40`)
- Roadmap macro 6 fases (`50_MODULES_ROADMAP.md`)
- Retrospectiva Fase 1 consolidada (`60_FASE_1_RETROSPECTIVA.md`)

**Indexación de referencias.** Repos en `references/` indexados con
`bin/codegraph` (SQLite + FTS5 + AST symbol extraction). Lookups vía
`codegraph search/symbol/file` — leer archivos en `references/` manualmente
está prohibido en `CLAUDE.md` del repo.

**Prior project ÑandeFact.** Ez (lead dev) viene de un sistema previo SIFEN en
Node/TS (vertical para vendedoras de mercado, low-end Android). De ahí hereda:
conocimiento SIFEN profundo, patrones UX validados (3-tap facturación, KuDE
ticket, consumidor final default), modelo conceptual de invariantes. No
hereda: stack (Node→Python), arquitectura hexagonal estricta, offline-first.

**Workflow del repo (override de global CLAUDE.md REGLA #1):** cualquier task
de código va por subagent. Trigger explícito de escalación: 1 test que falla,
1 traceback que no entendés primero, 1 "esto debería funcionar pero...", o
>2 lecturas seguidas para entender un bug. Razón documentada: sesión 2026-05-25
perdió 1h debug inline que `voltagent-qa-sec:debugger` resolvió en una pasada.

## Constraints

- **Tech stack**: Odoo Community Edition 18.0 (NO Enterprise). Python 3.11+.
  PostgreSQL 15+. No dependencias propietarias. — Definición del proyecto.
- **Librerías SIFEN runtime fijas**: `lxml`, `signxml`, `zeep`, `cryptography`,
  `qrcode`, `requests`, `requests-pkcs12`. — Cubren todo SIFEN sin SDK
  propietarios.
- **OCA strict**: naming `l10n_py_*`, AGPL-3, manifest OCA-compliant
  (`author` termina en `, Odoo Community Association (OCA)`). — Target final
  es OCA/l10n-paraguay.
- **Cobertura tests ≥80%** en módulos nuevos, pre-commit OCA activo
  (black, isort, pylint-odoo, flake8, oca-checks-*). — Calidad publicable.
- **Idioma**: código en inglés, comentarios/docstrings en español, UI en
  español + i18n vía `.pot`. — Convención del repo.
- **TLS mutual con PKCS#12 en Python 3.11+**: usar `requests-pkcs12` con
  fallback plan `.p12 → .pem` por OpenSSL si hay edge cases. — Documentado en
  docs/50 como riesgo Fase 2.
- **Homologación SIFEN**: requiere CCFE de prueba (timbrado test de DNIT) —
  bloqueador externo para validación final Fase 2.
- **Modelos delgados + servicios puros**: lógica compleja (CDC, firma XAdES,
  XML building) en módulos Python bajo `services/`, testables sin levantar
  Odoo. — Lección estructural del proyecto, refuerza testabilidad.
- **No `code_digits` en chart_template** — PUC RG 49/14 tiene códigos de
  longitud variable (2-11 dígitos). Padding uniforme distorsionaría códigos
  canónicos DNIT. — Decisión técnica de Fase 1b ya validada.

## Key Decisions

| Decision | Rationale | Outcome |
|---|---|---|
| Odoo Community 18 (no Enterprise) | Foco OCA + costo bajo para PyME | ✓ Good |
| AGPL-3 + naming `l10n_py_*` | Compatibilidad OCA + reutilización por la comunidad | ✓ Good |
| Conexión SIFEN directa (no IAP, no OSE intermedio) | Costo bajo + autonomía técnica | ✓ Good |
| Modelos delgados + servicios Python puros bajo `services/` | Testabilidad sin levantar Odoo | ✓ Good (validado en Fase 1b) |
| Sequence per doc_type vía 3 mecanismos (`_auto_init` + cache scoped + domain filter) | Requisito SIFEN — FE/NC/ND distintos secuenciales no satisfacible con un solo override (debugger lo verificó) | ✓ Good (8 tests verdes) |
| No `code_digits` en chart_template | PUC RG 49/14 longitud variable; padding distorsiona | ✓ Good (validado en pyme E2E test) |
| Skip constraints sale-journal-PoE en `install_mode` | Chart load crea journals antes del PoE config; check defensivo real está en `_post` | ✓ Good |
| `account.account` usa `company_ids` (M2M) en Odoo 18 — no `company_id` | Discovery durante test fix Fase 1b | ✓ Good (documentado en retrospectiva) |
| Fixture chart vía `@AccountTestInvoicingCommon.setup_chart_template("py")` decorator | Patrón Odoo 18 — `chart_template_ref` kwarg fue removido | ✓ Good |
| ÑandeFact NO se port literalmente, se herda conocimiento dominio + UX patterns | Stack/arquitectura distintos; sólo el dominio SIFEN se reutiliza | ✓ Good |
| Mantener docs/ extensa fuera de CLAUDE.md (CLAUDE.md = TOC) | CLAUDE.md crece sin control si tiene documentación técnica; docs/ versiona mejor | ✓ Good |
| Indexar `references/` con `bin/codegraph` (no leer manualmente) | Repos referencia totalizan ~190MB; búsqueda directa sin saturar contexto | ✓ Good |
| Subagent override del global CLAUDE.md (cualquier código → subagent, no inline edits) | Sesión 2026-05-25 perdió 1h debug inline que debugger resolvió en una pasada | ✓ Good (formalizado en CLAUDE.md del repo) |
| Stack runtime para Fase 2: `lxml`+`signxml`+`zeep`+`cryptography`+`qrcode`+`requests-pkcs12` | Cubre todo SIFEN sin proveedores intermedios; documentado en docs/40 | — Pending (validar al implementar) |
| Homologación SIFEN bloqueada por CCFE de prueba | DNIT requiere certificado test; depende de conseguir uno (cliente real o solicitud personal) | — Pending (Fase 2) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition` o equivalente):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state (Fases completadas, tests acumulados,
   PRs mergeados, métricas del repo)

## Stakeholders

| Quién | Rol |
|---|---|
| **Ez (Alberto Ezequiel Careaga)** | Lead developer, owner del repo, dueño de Careaga Dev |
| Clientes PyME paraguayas | Beta testers iniciales, fuente de requirements reales (Fases 3-4 onward) |
| **OCA** | Eventual home del repo (`OCA/l10n-paraguay`), source of best practices |
| Comunidad Odoo Paraguay | Contribuidores potenciales (consultoras locales) — alcance Fase 6+ |
| **DNIT** | Reguladora — Manual Técnico SIFEN es el contrato implícito |

## References

- Objetivo extendido: [`docs/00_OBJECTIVE.md`](../docs/00_OBJECTIVE.md)
- Roadmap macro 6 fases: [`docs/50_MODULES_ROADMAP.md`](../docs/50_MODULES_ROADMAP.md)
- Retrospectiva Fase 1: [`docs/60_FASE_1_RETROSPECTIVA.md`](../docs/60_FASE_1_RETROSPECTIVA.md)
- Conocimiento SIFEN: [`docs/01_SIFEN_KNOWLEDGE_BASE.md`](../docs/01_SIFEN_KNOWLEDGE_BASE.md) + [`docs/02_SIFEN_REFERENCIA_COMPLETA.md`](../docs/02_SIFEN_REFERENCIA_COMPLETA.md)
- Framework `account_edi`: [`docs/15_ODOO_ACCOUNT_EDI_FRAMEWORK.md`](../docs/15_ODOO_ACCOUNT_EDI_FRAMEWORK.md)
- Librerías Python: [`docs/40_PYTHON_LIBRARIES.md`](../docs/40_PYTHON_LIBRARIES.md)
- PR #1 (l10n_py_base 1.1.0): https://github.com/Ezcareaga/l10n-paraguay/pull/1
- PR #2 (l10n_py_account 1.0.0): https://github.com/Ezcareaga/l10n-paraguay/pull/2

---
*Last updated: 2026-05-26 — initial GSD bootstrap (post Fase 1 completada).*
