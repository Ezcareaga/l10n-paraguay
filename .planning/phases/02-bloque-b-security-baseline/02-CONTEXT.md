# Phase 2: Bloque B — Security baseline - Context

**Gathered:** 2026-06-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Activar el baseline de seguridad del repo: archivos visibles obligatorios
(`LICENSE`, `SECURITY.md`), workflow CI que escanea secrets + SAST + deps en
cada PR, y documentación escrita de cómo se manejará información sensible
(CCFE, datos personales) cuando exista deploy real. Cubre 7 REQs (SEC-01..07).

Esta phase **NO** implementa código de crypto (Fernet helper para CCFE se
escribe en Fase 2 EDI cuando exista `l10n_py_edi`), **NO** provisiona VPS ni
backups reales (eso es Pre-Fase 3), **NO** crea CHANGELOG/CONTRIBUTING/docs/70
(Phase 3), **NO** crea templates `.github/ISSUE_TEMPLATE/` (Phase 4). Cualquier
idea sobre esos bloques va a Deferred.

Sequencing interno sugerido (no locked — el planner termina de definir):

1. SEC-01 `LICENSE` (AGPL-3.0 full text) + sync `__manifest__.py` license=AGPL-3
2. SEC-02 `SECURITY.md` (canal + PGP + Hall of Fame + support policy)
3. SEC-03 `.github/workflows/security.yml` (3 jobs: gitleaks + Bandit + Dep Review)
4. SEC-04/05 ejecutar y limpiar findings (gitleaks history + Bandit HIGH)
5. SEC-06 `docs/60_SECURITY_BASELINE.md` (6 ejes + matriz)
6. SEC-07 `docs/61_COMPLIANCE_LEY_6534.md` + cross-link a docs/60

</domain>

<decisions>
## Implementation Decisions

### Workflow `security.yml` shape

- **D-01: 1 workflow con 3 jobs.** `security.yml` con jobs paralelos:
  `gitleaks`, `bandit`, `dependency-review`. _Razón:_ visibilidad única en
  Actions UI; los 3 jobs comparten triggers idénticos (PR + push to main);
  cancel-in-progress vale para los 3 a la vez. Workflows separados serían
  ceremonia sin ventaja.

- **D-02: Bandit fail-gate = solo HIGH severity.** Configuración:
  `bandit -r addons/ -lll -iii` (only HIGH severity reported as errors).
  MEDIUM y LOW se loguean en SARIF pero NO bloquean PR. Escalación a MEDIUM
  se reevalúa post-`l10n_py_edi` (Fase 2) cuando el código de crypto/firma
  esté en el repo. **Razón:** baseline realista para repo en stage actual;
  evitar fatiga de warnings en primera iteración.

- **D-03: SARIF upload al Security tab + logs en Actions.** Tanto gitleaks
  como Bandit generan reports SARIF que se suben con
  `github/codeql-action/upload-sarif@v3`. Aparecen en pestaña Security >
  Code scanning del repo. Comments automáticos en PR descartados (ruido).

- **D-04: gitleaks scope = diff PR + HEAD push, sin schedule.** En PR:
  `gitleaks detect --source=. --log-opts=^origin/main..HEAD`. En push a main:
  scan completo del último commit. NO scheduled weekly (overkill para repo
  con 1 maintainer; si hay un push con secret, el push lo detecta). NO scan
  histórico completo en CI (eso fue manual en SEC-04 cleanup).

### SECURITY.md mecánica de reporte

- **D-05: Canal primario = GitHub Security Advisories.** Botón "Report a
  vulnerability" del Security tab (privado, integrado con CVE issuance + draft
  advisory workflow). Fallback: `careagaezz@gmail.com` para reportantes sin
  cuenta GH. _Razón:_ encaja con SARIF de D-03 (todo el security state en GH),
  no requiere infra email extra, integrado con Hall of Fame nativo si se
  activa después.

- **D-06: PGP key generada + fingerprint publicado.** Generar par GPG
  (ed25519 preferido por simplicidad y tamaño; RSA 4096 si tooling de
  destinatario lo requiere) durante Phase 2 implementación. Public key sube a
  `keys.openpgp.org` + fingerprint en SECURITY.md. Privada queda en gestor de
  passwords del owner. Permite reportes cifrados via email fallback.
  Compatible con futuro `.well-known/security.txt` RFC 9116 si se agrega
  durante Phase 4.

- **D-07: Hall of Fame = tabla inline en SECURITY.md.** Sección
  `## Hall of Fame` con columnas: `Reporter`, `Date`, `Advisory ID`,
  `Severity`. Inicialmente vacía con nota _"No vulnerabilities have been
  reported yet."_. Si crece >10 entries, se evalúa migrar a archivo separado
  (deferred).

- **D-08: Support policy = solo latest minor 18.0.x.** Tabla:
  `18.0.x — :white_check_mark:` / `other — :x:`. Alineado con Odoo Community
  18.0 LTS upstream + política OCA estándar. Mantenible con 1 maintainer.
  Reevaluar en Pre-Fase 3 cuando haya primer cliente real downstream.

### docs/60 alcance + CCFE encryption

- **D-09: Strategy doc con commands ilustrativos.** Por cada eje (auth/2FA,
  password policy, audit logs, backup, CCFE encryption, network security)
  docs/60 incluye: **qué hacemos**, **por qué**, y **comandos/snippets
  ilustrativos**. Cada snippet lleva el marker
  `> Note: validar en Pre-Fase 3 cuando exista deploy real`. Sirve como
  blueprint reusable. Snippets cubren: cron de `pg_dump`, fail2ban rule,
  ufw config, fernet rotation script outline. **Razón:** sin commands esto
  queda como handwaving; con commands hay punto de partida concreto.

- **D-10: CCFE encryption implementación = Fase 2 EDI.** docs/60 documenta
  el patrón: helper `l10n_py_edi.tools.crypto` con `cryptography.fernet`,
  key envelope (data-key cifrada con master key), rotation script
  `scripts/ccfe-rotate-key.py` cada 90d, storage = `systemd-creds` en VPS
  para master key + `ir_config_parameter` para wrap key id. PERO **el código
  no se escribe en Phase 2 Pre-Fase 2** — solo la estrategia documentada. El
  helper real vive en `l10n_py_edi` cuando Fase 2 EDI lo cree. _Razón:_ Phase
  2 Pre-Fase 2 es bloque de docs+CI security, no de implementación crypto;
  escribir el helper ahora sin un consumidor es scope creep.

- **D-11: Audit logs = OCA `auditlog` module + retention escrita.** docs/60
  documenta: usar OCA `auditlog` (existe en 18.0). Modelos a auditar (lista
  literal en doc): `l10n_py.timbrado`, `l10n_py.document.type`, `res.partner`
  campos `vat`/`l10n_py_dv`/`l10n_py_doc_type`, `account.move` (post-Fase 2).
  Retention: **7 años archivado + 1 año online**, alineado con Ley 125/91
  tributaria PY (período de prescripción 5 años + margen). Documentar que el
  módulo `auditlog` se sumará al `__manifest__.py` del addon que lo necesite
  en su phase correspondiente (probable Fase 2 EDI).

- **D-12: Backup backend = S3-compatible (Backblaze B2 default) + filesystem
  local.** Doble target:
  - Filesystem local: `pg_dump | xz` diario, retención 7d, path `/var/backups/odoo/`
  - Offsite: sync nocturno a Backblaze B2 (default por costo; AWS S3 si
    cliente paga; documentamos ambos endpoints). Retention offsite: 90d.
  - Monthly restore test: checklist en docs/60 + script
    `scripts/restore-smoke.sh` (a escribir cuando exista deploy real en
    Pre-Fase 3). El script restaura el último dump a un container Postgres
    efímero y verifica `SELECT count(*) FROM ir_module_module WHERE state='installed'`.
    _Razón:_ vendor-neutral pero accionable; alineado con docs/55 hosting
    preliminar y con la ADR-0005 (Phase 3) sin comprometer vendor específico.

### docs/61 alcance Ley 6534

- **D-13: Alcance split vendor vs operador.** docs/61 estructurado como tabla
  explícita de responsabilidades:

  - **Vendor (este proyecto):** cifrado de PII en reposo (cuando aplique),
    audit logs, mecanismos para export/borrado, default password policy.
  - **Operador (deployer/cliente final):** DPO designation, notificaciones a
    SENAC si aplica, contratos con encargados, consent capture en formularios
    propios, política de retención específica del negocio.
    _Razón:_ correcto desde lo legal — somos software vendor, no controlador;
    documentar como tal evita asumir riesgos ajenos y guía al deployer.

- **D-14: ARCO + consent management.** docs/61 mapea cada derecho a
  mecanismo Odoo disponible:

  - **Acceso:** export del registro `res.partner` (Odoo standard "Export").
  - **Rectificación:** edit UI estándar + audit log de cambios via D-11.
  - **Cancelación:** archive del partner + módulo OCA `data_protection` /
    `gdpr_purge` si aplica (TODO documentar disponibilidad en 18.0).
  - **Oposición / portabilidad:** export en formato XLSX/CSV + flags
    `opt_out_*` existentes en `res.partner` upstream.
  - **Consent capture:** **NO se implementa en Phase 2.** Documentar como
    TODO operador (formulario web del cliente, no del módulo). Si Fase 4
    POS necesita consent registrado al cliente, se agrega ahí.

- **D-15: Cross-references explícitas + matriz de cumplimiento.** Al final
  de docs/61: tabla `Artículo Ley 6534 → Control en docs/60 → Estado
(implementado / documentado / TODO Pre-Fase 3 / responsabilidad operador)`.
  docs/60 linkea a docs/61 al inicio de los ejes "audit logs" y "PII handling".
  _Razón:_ accionable para reviewers OCA, abogado del cliente, y auditoría
  futura; señala dónde están los gaps sin esconderlos.

### Claude's Discretion

Áreas donde el researcher / planner tiene libertad para terminar de
especificar sin reabrir discuss:

- Versión exacta de gitleaks action (`gitleaks/gitleaks-action@v2` parece
  default; researcher confirma pin estable).
- Versión exacta de `bandit` (vía pip pin en step Action o action upstream).
  Pin a versión current major.
- Texto literal de `LICENSE` AGPL-3.0 (copiar desde
  `https://www.gnu.org/licenses/agpl-3.0.txt` — versión canónica).
- Estructura de secciones de SECURITY.md siguiendo template GitHub propuesto
  (`Reporting a Vulnerability`, `Supported Versions`, `Hall of Fame`,
  `Security Update Process`).
- Mecánica exacta del rotation script CCFE outline (envelope schema, naming
  de wrap keys). Si requiere decisiones de arquitectura, planner crea entry
  en `<canonical_refs>` apuntando al ADR/spec que define el contrato.
- Lista exacta de modelos a auditar para D-11 — researcher revisa addons
  actuales con codegraph para confirmar campos sensibles.
- Pin/versión del módulo OCA `auditlog` para Odoo 18.0 (si todavía no está
  porteado a 18.0, researcher documenta el alternativo o flagea como gap).

### Folded Todos

Ninguno — `gsd-sdk query todo.match-phase 2` no produjo matches relevantes
para esta phase (verificar al ejecutar plan).

</decisions>

<canonical_refs>

## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Source spec del milestone

- `docs/55_PRE_FASE_2_FOUNDATION.md` §"Bloque B — Security baseline" — output
  esperado, DoD, riesgo gitleaks-history (no reescribir, rotar)
- `.planning/REQUIREMENTS.md` §"SEC — Bloque B" — los 7 REQs SEC-01..07
  literales (locked)
- `.planning/ROADMAP.md` §"Phase 2" — goal, dependencies, success criteria,
  complexity=medium 2-3 días
- `.planning/PROJECT.md` §"Active" — milestone activo + constraints
- `.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/01-CONTEXT.md`
  — Phase 1 CONTEXT (workflows pattern OCA Brazil, status check names,
  branch protection en main ya activa)

### Marco legal y de cumplimiento

- **Ley 6534/2020 PY** — Protección de Datos Personales (consultar texto
  oficial vía Gaceta Oficial cuando el doc se redacte; researcher confirma
  artículos relevantes y compila citas en docs/61)
- **Ley 125/91 PY** — Régimen Tributario (retention period 5 años → base
  para D-11 retention 7y)
- **OWASP Top 10 (current)** — referencia genérica para D-02 Bandit policy

### Stack OCA / Odoo

- **OCA `auditlog`** — repo: `OCA/server-tools` (verificar branch 18.0;
  researcher confirma estado del port a 18.0)
- **OCA `data_protection` / `gdpr_purge`** — repo: `OCA/data-protection`
  (verificar disponibilidad en 18.0 para D-14)
- `references/l10n-brazil/.github/workflows/` — patrones OCA-style para
  security workflows (no hay `security.yml` propio en Brazil pero hay
  pre-commit + test que sirven como template estructural)
- `references/oca-addons-repo-template/.github/dependabot.yml` — Dependency
  Review action es complementaria a dependabot

### Estado actual del repo

- `addons/l10n_py_base/__manifest__.py` — campo `license="AGPL-3"` ya
  presente; SEC-01 verifica consistencia + linkea LICENSE raíz
- `addons/l10n_py_account/__manifest__.py` — idem
- `pyproject.toml` — license declarada en metadata; SEC-01 verifica
  consistencia con LICENSE raíz
- `.github/workflows/{pre-commit,test,commitlint}.yml` — creados en Phase 1;
  `security.yml` se suma como cuarto workflow

### Conocimiento interno del proyecto

- `docs/01_SIFEN_KNOWLEDGE_BASE.md` — contexto CCFE (qué es, ciclo de vida,
  por qué requiere encryption)
- `docs/02_SIFEN_REFERENCIA_COMPLETA.md` — detalle técnico CCFE para D-10
  (Fernet helper signature, key envelope)
- `docs/40_PYTHON_LIBRARIES.md` — librerías ya decididas (incluye
  `cryptography` que provee Fernet)
- `docs/60_FASE_1_RETROSPECTIVA.md` — lecciones cosméticas del baseline
  anterior; no aplicable a Phase 2 directamente pero útil para tono

### Tooling externo (researcher confirma versiones)

- `gitleaks/gitleaks-action@v2` — secrets scan
- `PyCQA/bandit` — SAST Python; CLI vía `pip install bandit[toml]`
- `actions/dependency-review-action@v4` — Dep Review de GitHub
- `github/codeql-action/upload-sarif@v3` — upload SARIF al Security tab
- `keys.openpgp.org` — public PGP keyserver para D-06

</canonical_refs>

<code_context>

## Existing Code Insights

### Reusable Assets

- **`__manifest__.py` license metadata.** Ambos addons ya declaran
  `license="AGPL-3"`. SEC-01 implica: agregar LICENSE raíz + linkear desde
  cada manifest vía el campo existente; verificar consistencia con `git grep
"license"`. No hace falta tocar manifests si ya están bien.
- **`pyproject.toml` license field.** Ya declara license="AGPL-3.0";
  SEC-01 verifica que coincida con archivo raíz.
- **GitHub Actions runner ubuntu-latest.** Phase 1 workflows ya lo usan;
  `security.yml` reusa el mismo runner — sin matrix necesaria para Phase 2.
- **`.gitignore` + `.gitattributes`.** Existen desde bootstrap; cualquier
  exclusión nueva por gitleaks (`.gitleaksignore`) va aparte.

### Established Patterns

- **No leer `references/` manualmente** (CLAUDE.md). Para inspeccionar
  patrones OCA usar `bin/codegraph.ps1 search/symbol/file`.
- **Subagent override de Phase 2** (project CLAUDE.md): `voltagent-qa-sec:security-auditor`
  (opus) es el subagent crítico para SEC-03..05. Para docs de policy
  (SEC-06/07) `voltagent-dev-exp:documentation-engineer` complementa.
- **Atomic commits + Conventional Commits.** Cada REQ se merge como PR
  separada con prefix `feat(sec):` o `docs(sec):`. La sequence sugerida
  (5-6 PRs en Phase 2) respeta el patrón Phase 1.
- **Branch protection ya activo en `main`** (post Phase 1). Todos los
  commits de Phase 2 van por PR — sin overrides ad-hoc como D-06 de Phase 1.
- **Status checks names para CI-07.** Sumar `security` (job único del workflow
  con jobs paralelos D-01) a los required status checks tras crear el
  workflow. Researcher confirma el job name exacto.

### Integration Points

- **`LICENSE`** (raíz, nuevo) — AGPL-3.0 full text.
- **`SECURITY.md`** (raíz, nuevo) — reporte + PGP + Hall of Fame + support.
- **`.github/workflows/security.yml`** (nuevo) — 3 jobs paralelos.
- **`.gitleaksignore`** (raíz, condicional) — solo si SEC-04 cleanup detecta
  false positives legítimos.
- **`docs/60_SECURITY_BASELINE.md`** (nuevo) — 6 ejes.
- **`docs/61_COMPLIANCE_LEY_6534.md`** (nuevo) — alcance Ley 6534 + matriz.
- **`scripts/restore-smoke.sh`** (nuevo, stub) — placeholder para D-12 monthly
  restore test, completado en Pre-Fase 3.
- **`README.md`** — sumar 1 badge security (workflow status) + link a
  SECURITY.md en sección "Security". NO refactor de README real (eso es
  Phase 3 DOC-01).
- **GitHub Settings → Code scanning alerts.** Habilitar Dependency graph +
  Dependabot alerts en repo settings (manual UI step, documentar en
  PLAN.md).

</code_context>

<specifics>
## Specific Ideas

- **Cero ceremonia que no se pueda mantener con 1 maintainer.** Cada
  decisión (D-01..D-15) está calibrada para que la operación recurrente sea
  baja: 1 workflow no 3, fail-gate solo HIGH, no schedule semanal, no
  archivos separados para Hall of Fame vacío. Optimización para repo
  pre-cliente.
- **CCFE encryption en docs/60 = blueprint, no implementación.** El usuario
  evitó scope creep al rechazar implementar Fernet helper ahora. El doc tiene
  que ser tan claro que cuando Fase 2 EDI lo lea, el código se escribe
  siguiendo el patrón sin re-decidir.
- **Matriz de cumplimiento Ley 6534 al final de docs/61.** Es la artefacto
  que más valor entrega al reviewer OCA / abogado: vista panorámica de
  gaps con estado explícito.
- **Estilo de docs/60-61: operacional, no académico.** Snippets de comandos,
  paths absolutos, nombres de módulos OCA reales. Evitar prosa larga; tablas
  - bullets + code blocks.

</specifics>

<deferred>
## Deferred Ideas

### Fuera de scope Phase 2 — capturar para milestones futuros

- **Implementación real del Fernet helper CCFE** — Fase 2 EDI
  (`l10n_py_edi.tools.crypto`). docs/60 deja el blueprint.
- **Escalación Bandit fail-gate a MEDIUM** — Reevaluar post-Fase 2 EDI
  cuando el código de crypto/firma esté en el repo y MEDIUM warnings tengan
  contexto.
- **`.well-known/security.txt` (RFC 9116)** — Phase 4 (REL-\* repo hygiene)
  o Pre-Fase 3 cuando exista dominio público. Hoy no hay sitio donde
  alojarlo.
- **Schedule weekly de gitleaks full-history** — Pre-Fase 3 si aparece señal
  de churn de secrets. Hoy no se justifica.
- **Migrar Hall of Fame a archivo separado** — cuando crezca a >10 entries.
  Hoy queda inline.
- **Consent capture form en módulo Odoo** — Fase 4 POS o Fase 5 si surge un
  flow de signup propio. Por defecto es responsabilidad operador.
- **Provisión real de VPS + Caddy + Postgres prod** — Pre-Fase 3.
- **Implementar `scripts/restore-smoke.sh` ejecutable** — Pre-Fase 3 cuando
  exista backend de backup real. Phase 2 deja el stub + el checklist.
- **Pre-FASE 3: revisar pricing Backblaze B2 vs AWS S3 con datos reales** —
  hoy es default neutral; cliente real puede pedir cambiar.
- **DPO designation + contratos con encargados** — responsabilidad
  operador / Pre-Fase 3 con primer cliente real. docs/61 lo documenta
  como TODO operador.

### Reviewed Todos (not folded)

No applicable — `gsd-sdk query todo.match-phase 2` no devolvió matches.

</deferred>

---

_Phase: 2-bloque-b-security-baseline_
_Context gathered: 2026-06-02_
