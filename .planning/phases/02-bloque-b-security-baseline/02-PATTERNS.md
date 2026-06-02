# Phase 2: Bloque B — Security baseline - Pattern Map

**Mapped:** 2026-06-02
**Files analyzed:** 9 (7 new, 2 modified)
**Analogs found:** 8 / 9 (1 no analog — `LICENSE` is canonical download)

---

## File Classification

| New/Modified File                | Role      | Data Flow                                            | Closest Analog                                         | Match Quality                                  |
| -------------------------------- | --------- | ---------------------------------------------------- | ------------------------------------------------------ | ---------------------------------------------- |
| `LICENSE`                        | root-meta | static-asset                                         | `pyproject.toml` (license declaration)                 | partial (same license field, different format) |
| `SECURITY.md`                    | root-meta | request-response (reporter → maintainer)             | `README.md` (root doc with external links + tables)    | partial (same markdown style)                  |
| `.github/workflows/security.yml` | workflow  | event-driven (PR/push → SARIF → Security tab)        | `.github/workflows/pre-commit.yml`                     | role-match                                     |
| `.gitleaksignore`                | config    | static-asset (conditional)                           | `.gitignore` (gitconfig exclusion file)                | partial                                        |
| `docs/60_SECURITY_BASELINE.md`   | doc       | static-asset (strategy blueprint)                    | `docs/60_FASE_1_RETROSPECTIVA.md`                      | role-match (same series, same section depth)   |
| `docs/61_COMPLIANCE_LEY_7593.md` | doc       | static-asset (compliance matrix)                     | `docs/03_DOMAIN_MODEL.md` (table-heavy structured doc) | role-match                                     |
| `scripts/restore-smoke.sh`       | script    | batch (stub)                                         | `scripts/setup_references.sh`                          | role-match                                     |
| `README.md`                      | root-meta | MODIFY (add badge + section link)                    | `README.md` itself (existing badge block)              | exact (self-modification)                      |
| `.planning/REQUIREMENTS.md`      | config    | MODIFY (already amended for SEC-07 Ley 7593 wording) | N/A — no further changes needed in Phase 2             | —                                              |

---

## Pattern Assignments

---

### `LICENSE` (root-meta, static-asset)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\LICENSE`

**Role:** root-meta

**Closest analog:** `pyproject.toml` — both are authoritative license declarations for the project. `pyproject.toml` line 6 already reads `license = { text = "AGPL-3.0" }` and both `__manifest__.py` files have `"license": "AGPL-3"`. `LICENSE` is the full text that those fields reference.

**No template excerpt needed** — this is a verbatim canonical file. Fetch with:

```bash
# Verificar SHA256 tras descargar:
curl -sSL https://www.gnu.org/licenses/agpl-3.0.txt -o LICENSE
sha256sum LICENSE
# Esperado: 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0
```

**Manifests already consistent** (confirmed in RESEARCH.md §LICENSE Canonical Reference):

```python
# addons/l10n_py_base/__manifest__.py — línea 7 — NO tocar
"license": "AGPL-3",

# addons/l10n_py_account/__manifest__.py — línea 7 — NO tocar
"license": "AGPL-3",

# pyproject.toml — línea 6 — NO tocar
license = { text = "AGPL-3.0" }
```

**Adaptations needed:**

- None. Download verbatim from canonical URL. No edits.

**Pitfalls flagged:**

- Do NOT use the HTML version (`agpl-3.0.en.html`) — it has different formatting. Use the `.txt` endpoint.
- Do NOT edit the file after download. Verify SHA256 before committing.
- Do NOT modify any `__manifest__.py` — they are already correct.

---

### `SECURITY.md` (root-meta, request-response)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\SECURITY.md`

**Role:** root-meta

**Closest analog:** `README.md` — same project root, same markdown style (tables with `|`, H2 sections, badge-link syntax). RESEARCH.md §SECURITY.md Skeleton provides the exact skeleton to use directly.

**Style pattern from `README.md`** (lines 1-7):

```markdown
# l10n-paraguay

[![CI](https://github.com/...)](...)
[![License: AGPL-3.0](https://img.shields.io/badge/...)](...)

## Módulos planificados

| Version | Supported |
```

The above shows the pattern: H1 title, optional badges, then H2 sections with tables. Apply same style to `SECURITY.md`.

**Canonical content from RESEARCH.md §SECURITY.md Skeleton** (use this directly):

```markdown
# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 18.0.x  | ✅        |
| < 18.0  | ❌        |

Only the latest minor release of the 18.0 series receives security fixes.

## Reporting a Vulnerability

**Preferred channel:** Use [GitHub Security Advisories](https://github.com/Ezcareaga/l10n-paraguay/security/advisories/new)
— this keeps the report private and triggers the native CVE workflow.

**Fallback (no GitHub account):** Email `careagaezz@gmail.com` with subject
`[SECURITY] <brief description>`. Note: email is plaintext; do not include
production secrets in the initial report.

**Response SLA:**

- Confirmation within **72 hours**.
- Fix or mitigation within **30 days** for critical/high severity.
- Best-effort for lower severity.

## Security Update Process

1. Vulnerability confirmed → private advisory created on GitHub.
2. Fix developed in a private fork or branch.
3. Fix merged and tagged as a patch release `18.0.x.y.z`.
4. Advisory published and CVE assigned (if applicable).
5. Upstream OCA notified if the issue affects OCA modules.

## Acknowledgements

Security researchers who responsibly disclose vulnerabilities are credited in the
published advisory. View acknowledged reports at:
<https://github.com/Ezcareaga/l10n-paraguay/security/advisories>
```

**Adaptations needed:**

- Use exact structure above; add nothing else (no PGP section — D-06, no HoF table — D-07).
- GH username is `@Ezcareaga` — verified against `__manifest__.py` `website` field and `.planning/STATE.md`.

**Pitfalls flagged:**

- Do NOT add a PGP section (D-06: explicitly rejected).
- Do NOT add a Hall of Fame table (D-07: remit to GH Advisories link instead).
- Do NOT use "SENAC" as notification authority — that is wrong. This file does not mention a regulatory authority (that detail belongs in docs/61).
- The GitHub Advisories URL ends in `/new` for the reporting form. The Acknowledgements link omits `/new` (public listing).

---

### `.github/workflows/security.yml` (workflow, event-driven)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\.github\workflows\security.yml`

**Role:** workflow

**Closest analog:** `.github/workflows/pre-commit.yml` — same trigger block (`on: pull_request: branches: [main]` + `push: branches: [main]`), same `concurrency` group naming pattern, same `runs-on: ubuntu-22.04`, same `actions/checkout@v4`. This is the direct structural template.

**Trigger + concurrency pattern** from `.github/workflows/pre-commit.yml` (lines 1-12):

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
```

**Permissions pattern** from `.github/workflows/commitlint.yml` (lines 7-10):

```yaml
permissions:
  contents: read
  pull-requests: read
```

**Full canonical structure** (from RESEARCH.md §Action Pins, incorporating all decisions D-01..D-04 + amendments A-02):

```yaml
name: security

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  gitleaks:
    name: gitleaks
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: gitleaks/gitleaks-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITLEAKS_ENABLE_COMMENTS: "false"
          GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false"

      - name: Upload gitleaks SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: results.sarif
          category: gitleaks

  bandit:
    name: bandit
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Install bandit with SARIF support
        run: pip install "bandit[sarif]==1.9.4"

      - name: Run bandit (HIGH only)
        run: bandit -r addons/ -lll -iii -f sarif -o bandit.sarif
        continue-on-error: true

      - name: Upload Bandit SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: bandit.sarif
          category: bandit

      - name: Fail if HIGH findings exist
        run: bandit -r addons/ -lll -iii

  dependency-review:
    name: dependency-review
    runs-on: ubuntu-22.04
    if: github.event_name == 'pull_request'
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high
```

**Required status check names** (for GitHub branch protection after workflow creation):

- `gitleaks` (job `name:` value)
- `bandit` (job `name:` value)
- `dependency-review` (job `name:` value)

Add all three to the required status checks for `main` via `gh api` or GitHub Settings UI after the first successful workflow run.

**Adaptations needed:**

- Use `name: security` (workflow-level) — consistent with `name: pre-commit`, `name: tests`, `name: commitlint` naming pattern from Phase 1.
- `runs-on: ubuntu-22.04` — NOT `ubuntu-latest` (matches all Phase 1 workflows exactly).
- `actions/setup-python@v5` with `python-version: "3.11"` for bandit (no OCA container needed here).
- Each SARIF upload step MUST have a different `category:` value (`gitleaks` vs `bandit`) — required since July 2025 for multi-SARIF workflows.
- `dependency-review` job: add `if: github.event_name == 'pull_request'` — this action does not support push triggers.

**Pitfalls flagged:**

- Do NOT pin gitleaks to `@v2` (amendment A-02: use `@v3`; v2 reaches Node 20 EOL in Sep 2026).
- Do NOT use `dependency-review-action@v5` — v5 requires runner v2.327.1+; use `@v4` for compatibility (RESEARCH.md §Risk 3).
- Do NOT omit `category:` in upload-sarif steps — missing category causes the second SARIF upload to overwrite the first in the Security tab.
- Do NOT add `workflow_dispatch` or `schedule:` triggers (D-04: explicitly rejected).
- Do NOT add PR comments from gitleaks (set `GITLEAKS_ENABLE_COMMENTS: "false"` — D-01 rationale: reduce noise).
- Do NOT set `GITLEAKS_LICENSE` — not required for personal account repos (`@Ezcareaga`).
- `if: always()` on SARIF upload steps is mandatory — without it, a non-zero bandit exit suppresses SARIF upload and the Security tab never receives results.

---

### `.gitleaksignore` (config, static-asset, conditional)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\.gitleaksignore`

**Role:** config (create only if SEC-04 cleanup detects false positives)

**Closest analog:** `.gitignore` — same concept (per-line exclusion file at repo root), same comment syntax with `#`.

**Format pattern** (from RESEARCH.md §gitleaks History Strategy):

```
# .gitleaksignore
# Sintaxis: una fingerprint por línea. Sin prefijos ni wildcards.
# Fingerprint format: <commit-sha>:<file-path>:<rule-id>:<line-number>
# Ejemplo:
6e6ee6596d337bb656496425fb98644eb62b4a82:config/test.env:generic-api-key:4
```

**Adaptations needed:**

- Only create this file if `gitleaks detect --source . --no-git=false` (run manually before first PR) finds false positive findings.
- Copy the exact fingerprint from the `Fingerprint` field of gitleaks JSON/SARIF output — do not construct it manually.
- If there are real secrets found: rotate them first, THEN add to `.gitleaksignore` as "historical/rotated" noise.
- Header comment must explain why each entry was added (date + reason: "false positive" or "rotated YYYY-MM-DD").

**Pitfalls flagged:**

- Do NOT add wildcards or glob patterns — gitleaks fingerprints are exact strings.
- Do NOT use this to suppress active (unrotated) secrets — rotate first, then ignore.
- Do NOT rewrite git history (`git filter-repo`, BFG) — policy from CONTEXT.md and REQUIREMENTS.md: rotate-only, never rewrite.

---

### `docs/60_SECURITY_BASELINE.md` (doc, static-asset/strategy blueprint)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\docs\60_SECURITY_BASELINE.md`

**Role:** doc

**Closest analog:** `docs/60_FASE_1_RETROSPECTIVA.md` — direct sibling in same numeric series, same H1 → H2 section depth, same table + bullet + code-fence style. Also `docs/01_SIFEN_KNOWLEDGE_BASE.md` for the pattern of frontmatter-less docs with glosario tables.

**Section structure pattern** from `docs/60_FASE_1_RETROSPECTIVA.md` (lines 1-15):

```markdown
# Fase 1 — Retrospectiva consolidada

**Período:** 2026-05-19 → 2026-05-25 (1 semana)
**Resultado:** 2 módulos Odoo 18 instalables, 97 tests verdes, 2 PRs mergeados.

---

## Entregables

| Módulo | Versión | Tests | Estado |
| ------ | ------- | ----- | ------ |
```

The style: H1 title + bold metadata line(s) + `---` divider + H2 sections with tables/bullets/code. No YAML frontmatter (unlike `docs/01_*` which has a legacy frontmatter block — do NOT add frontmatter to new docs/60 and docs/61).

**Table style** from `docs/03_DOMAIN_MODEL.md` (lines 19-22):

```markdown
| Actor       | Descripción                   | Mapeo Odoo                            |
| ----------- | ----------------------------- | ------------------------------------- |
| Comerciante | Usa el sistema para facturar. | `res.users` con grupos de `l10n_py_*` |
```

**Code block pattern** — always labeled with language tag:

```markdown
\`\`\`bash

# Comentario en español

comando aqui
\`\`\`

\`\`\`python

# Este bloque es blueprint — NO ejecutar en Phase 2

from cryptography.fernet import Fernet
\`\`\`
```

**Required sections for docs/60** (D-09, D-10, D-11, D-12):

The doc must cover 6 ejes with the structure: `## N. <Eje>` → qué hacemos → por qué → comandos ilustrativos con marker `> Note: validar en Pre-Fase 3 cuando exista deploy real`.

```
## 1. Autenticación y 2FA
## 2. Política de contraseñas
## 3. Audit logs (OCA auditlog)
## 4. Backup strategy (D-12)
## 5. CCFE encryption blueprint (D-10)
## 6. Seguridad de red
```

**Audit log models table** (from RESEARCH.md §OCA auditlog 18.0 Status — use this verbatim in the section):

| Modelo                     | Módulo            | Campos sensibles                                         |
| -------------------------- | ----------------- | -------------------------------------------------------- |
| `res.partner`              | `l10n_py_base`    | `vat`, `l10n_py_dv`, `l10n_latam_identification_type_id` |
| `res.company`              | `l10n_py_base`    | `vat`, `l10n_py_dv`                                      |
| `l10n_py.timbrado`         | `l10n_py_account` | `name`, `state`, `expiry_date`                           |
| `l10n_latam.document.type` | `l10n_py_account` | `code`, `internal_type`                                  |
| `account.move`             | Odoo core         | `state`, `name`, `amount_total` (post-Fase 2 EDI)        |

**Fernet blueprint** — include the pseudo-code block from RESEARCH.md §CCFE Fernet Blueprint Detail with the exact comment `# Este bloque es blueprint para l10n_py_edi.tools.crypto — NO ejecutar en Phase 2`.

**Adaptations needed:**

- Style: operacional, no académico (D-09 instruction: "snippets > prosa larga; tablas + bullets + code blocks").
- Every command snippet carries the note: `> Note: validar en Pre-Fase 3 cuando exista deploy real`.
- Retention wording for audit logs: "7 años archivado + 1 año online" — Ley 125/91 PY base.
- Cross-reference to docs/61 at the start of the "audit logs" and "CCFE/PII handling" sections.
- `auditlog` module NOT installed in Phase 2 — doc states it clearly: "se agrega al `__manifest__.py` correspondiente en Fase 2 EDI".

**Pitfalls flagged:**

- Do NOT add YAML frontmatter (only the old docs/01-02 have that legacy block).
- Do NOT write the Fernet helper code as implementation — mark it clearly as blueprint stub.
- Do NOT cite SENAC as any authority — Ley 7593/2025 authority is ANPDP under MITIC.
- Do NOT document `gdpr_purge` (not in OCA 18.0) — use `privacy_partner_to_be_forgotten` instead.

---

### `docs/61_COMPLIANCE_LEY_7593.md` (doc, static-asset/compliance matrix)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\docs\61_COMPLIANCE_LEY_7593.md`

**Role:** doc

**CRITICAL NOTE:** File name is `_LEY_7593.md` NOT `_LEY_6534.md` (amendment A-01). Ley 6534/2020 covers only credit data (BCP/burós) and is NOT applicable to this project.

**Closest analog:** `docs/03_DOMAIN_MODEL.md` — heavily table-driven structured doc with split-responsibility framing. Also `docs/60_FASE_1_RETROSPECTIVA.md` for series style.

**Table-heavy style pattern** from `docs/03_DOMAIN_MODEL.md` (lines 18-22):

```markdown
## 1. Actores

| Actor       | Descripción                   | Mapeo Odoo                            |
| ----------- | ----------------------------- | ------------------------------------- |
| Comerciante | Usa el sistema para facturar. | `res.users` con grupos de `l10n_py_*` |
```

**Required sections** (D-13, D-14, D-15):

```
## 1. Alcance y ley aplicable
## 2. Responsabilidades: vendor vs operador (D-13)
## 3. Derechos ARCO + mecanismos Odoo (D-14)
## 4. Módulos OCA disponibles en 18.0
## 5. Matriz de cumplimiento (D-15) — artículos Ley 7593 → control → estado
```

**Vendor vs operador split pattern** (D-13, for section 2):

```markdown
## 2. Responsabilidades: vendor vs operador

| Responsabilidad         | Vendor (este proyecto)           | Operador (deployer/cliente)         |
| ----------------------- | -------------------------------- | ----------------------------------- |
| Cifrado PII en reposo   | ✅ (blueprint docs/60 §5)        | Implementar en deploy real          |
| Audit logs              | ✅ (OCA auditlog, docs/60 §3)    | Activar reglas via UI               |
| Export/borrado          | ✅ (mecanismos en §3)            | Ejecutar a solicitud del titular    |
| Default password policy | ✅ (docs/60 §2)                  | Configurar en instancia             |
| DPO designation         | ❌ responsabilidad operador      | Designar según reglamentación ANPDP |
| Notificación a ANPDP    | Notificar breach al vendor email | Notificar a ANPDP en ≤72h (Art. 17) |
```

**Compliance matrix pattern** (D-15, use content from RESEARCH.md §Ley 7593/2025 Article Map):

```markdown
## 5. Matriz de cumplimiento — Ley 7593/2025

| Artículo                      | Descripción               | Control en docs/60                | Estado                               |
| ----------------------------- | ------------------------- | --------------------------------- | ------------------------------------ |
| Art. 6 — Bases legales        | Consentimiento / contrato | `privacy_consent` (OCA)           | Documentado / TODO operador          |
| Art. 11 — Acceso              | Export datos del titular  | Odoo Export built-in              | Implementado (Odoo core)             |
| Art. 12 — Rectificación       | Corrección + trazabilidad | `auditlog` (OCA)                  | Documentado / implementar Fase 2 EDI |
| Art. 14 — Cancelación         | Anonimización PII         | `privacy_partner_to_be_forgotten` | Documentado / TODO operador          |
| Art. 15 — Oposición           | Opt-out de tratamiento    | `opt_out` Odoo built-in           | Responsabilidad operador             |
| Art. 16 — Portabilidad        | Export estructurado       | Odoo CSV/XLSX export              | Responsabilidad operador             |
| Art. 17 — Breach notification | 72h a ANPDP + titular     | Proceso en §6                     | Documentado (no código)              |
| Art. 18 — DPO                 | Oficial de protección     | N/A vendor                        | Responsabilidad operador             |
| Arts. 34-39 — ANPDP           | Autoridad supervisora     | Notificación breach               | Documentado                          |
```

**Ley 6534/2020 footnote** — add at the bottom per amendment A-01:

```markdown
---

> **Nota:** Ley 6534/2020 ("De Protección de Datos Personales Crediticios") regula
> exclusivamente burós de crédito bajo supervisión del BCP. Su scope es datos
> financieros/crediticios — **no aplica** a los datos de clientes/facturas que
> maneja este proyecto. No confundir con Ley 7593/2025.
```

**Adaptations needed:**

- Title: `# Compliance — Ley 7593/2025 (Protección de Datos Personales)`
- Authority: ANPDP (dentro de MITIC), NOT SENAC — SENAC is a different entity.
- ANPDP temporal caveat: "ANPDP en formación (ley vigente Nov 2027); enforcement limitado hasta esa fecha" — add to the breach notification section.
- OCA `data-protection` module names: use `privacy_partner_to_be_forgotten` not `gdpr_purge` (not in 18.0).
- `data_subject_access_request` module: NOT in OCA 18.0 — document as "gap / TODO operador / Pre-Fase 4".

**Pitfalls flagged:**

- Do NOT name the file `docs/61_COMPLIANCE_LEY_6534.md` (amendment A-01 — wrong law).
- Do NOT cite SENAC as the data protection authority — correct authority is ANPDP under MITIC.
- Do NOT treat `gdpr_purge` as available — it is not in OCA 18.0; use `privacy_partner_to_be_forgotten`.
- Do NOT imply the vendor (this project) carries DPO responsibility — that is explicitly operador's obligation.
- Do NOT omit the Ley 6534/2020 "out of scope" footnote — reviewers may check why it's absent.

---

### `scripts/restore-smoke.sh` (script, batch/stub)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\scripts\restore-smoke.sh`

**Role:** script (stub only in Phase 2 — full implementation in Pre-Fase 3)

**Closest analog:** `scripts/setup_references.sh` — same shebang, same bash boilerplate, same `set -euo pipefail`, same `SCRIPT_DIR`/`REPO_ROOT` pattern.

**Shell boilerplate pattern** from `scripts/setup_references.sh` (lines 1-12):

```bash
#!/usr/bin/env bash
# scripts/setup_references.sh — Clona los repos de referencia para codegraph.
#
# Tras correr este script, ejecutar:
#   python scripts/build_index.py
# para construir el índice consultable vía bin/codegraph.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
```

**Stub content for restore-smoke.sh** (Phase 2 delivers this stub; real implementation in Pre-Fase 3):

```bash
#!/usr/bin/env bash
# scripts/restore-smoke.sh — Smoke test de restauración de backup mensual.
#
# STUB — Phase 2 Pre-Fase 2 security baseline.
# Implementación completa: Pre-Fase 3 cuando exista deploy real en VPS.
#
# Propósito (D-12 docs/60):
#   Restaurar el último dump a un container Postgres efímero y verificar:
#   SELECT count(*) FROM ir_module_module WHERE state='installed'
#
# Uso (cuando esté implementado):
#   ./scripts/restore-smoke.sh [--dump-path /var/backups/odoo/latest.sql.xz]
#
# Pasos del test de restauración:
#   1. Descomprimir el dump: xz -d < <dump_path> > /tmp/restore-smoke.sql
#   2. Levantar container Postgres efímero:
#      docker run -d --name odoo-restore-smoke postgres:12
#   3. Restaurar: psql -h localhost -U postgres odoo < /tmp/restore-smoke.sql
#   4. Verificar módulos:
#      psql -h localhost -U postgres odoo -c \
#        "SELECT count(*) FROM ir_module_module WHERE state='installed'"
#   5. Limpiar: docker rm -f odoo-restore-smoke

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "[restore-smoke] STUB — implementación pendiente para Pre-Fase 3."
echo "[restore-smoke] Ver docs/60_SECURITY_BASELINE.md §4 Backup strategy para el diseño."
exit 0
```

**Adaptations needed:**

- Make executable: `chmod +x scripts/restore-smoke.sh` (add as a step in the commit that creates it).
- Use Spanish comments per project CLAUDE.md convention.
- `exit 0` stub so pre-commit and CI don't fail if the script is ever invoked.

**Pitfalls flagged:**

- Do NOT implement real backup logic in Phase 2 — explicitly deferred to Pre-Fase 3 (D-12, Deferred section).
- Do NOT reference `/var/backups/odoo/` as if it exists — it's a future path, mark as TODO.
- Script must still parse syntactically; test with `bash -n scripts/restore-smoke.sh` before committing.

---

### `README.md` (root-meta, MODIFY — minimal touch)

**Target:** `C:\Proyectos\odoo-l10n-paraguay\README.md`

**Role:** root-meta (MODIFY)

**Closest analog:** `README.md` itself — self-modification. The existing badge block (lines 1-7) is the exact pattern to extend.

**Existing badge block** from `README.md` (lines 1-7):

```markdown
# l10n-paraguay

[![CI](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/test.yml)
[![pre-commit](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/pre-commit.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/pre-commit.yml)
[![codecov](https://codecov.io/gh/Ezcareaga/l10n-paraguay/branch/main/graph/badge.svg)](https://codecov.io/gh/Ezcareaga/l10n-paraguay)
[![License: AGPL-3.0](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0.en.html)
[![Odoo](https://img.shields.io/badge/Odoo-18.0%20Community-714B67.svg)](https://www.odoo.com/)
```

**Add after existing badges** (1 new badge):

```markdown
[![Security](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/security.yml/badge.svg?branch=main)](https://github.com/Ezcareaga/l10n-paraguay/actions/workflows/security.yml)
```

**Existing "Licencia" section** (lines 81-84) — add a "Seguridad" section just before it:

```markdown
## Seguridad

Para reportar vulnerabilidades, ver [`SECURITY.md`](SECURITY.md).
El workflow de seguridad (gitleaks + Bandit + Dependency Review) corre en cada PR.
```

**Adaptations needed:**

- Add exactly 1 badge (security workflow) — matches existing badge format (shields.io style for consistency vs GH badge style for CI badges; use GH badge style like the CI and pre-commit badges).
- Add exactly 1 "Seguridad" section with 2 lines — no more (full README refactor is Phase 3 DOC-01, not Phase 2).
- Badge must reference `security.yml` workflow, not a shields.io endpoint.

**Pitfalls flagged:**

- Do NOT refactor or restructure the README (Phase 3 DOC-01 is the full README overhaul).
- Do NOT add the security badge before the security workflow exists and is green — create the PR for `security.yml` first, then the README badge PR.
- The existing "Licencia" section (line 81) already links to `LICENSE` — do NOT duplicate.

---

## Shared Patterns

### GitHub Actions: trigger + concurrency block

**Source:** `.github/workflows/pre-commit.yml` lines 1-12
**Apply to:** `security.yml`

```yaml
on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

### GitHub Actions: runner + checkout pin

**Source:** All three Phase 1 workflows
**Apply to:** `security.yml` (all jobs)

```yaml
runs-on: ubuntu-22.04 # NOT ubuntu-latest — project standard
steps:
  - uses: actions/checkout@v4 # Phase 1 pin
```

### GitHub Actions: least-privilege permissions

**Source:** `.github/workflows/commitlint.yml` lines 7-10
**Apply to:** `security.yml` jobs (especially `dependency-review` which only needs `contents: read`)

```yaml
permissions:
  contents: read
```

### Markdown doc style (new docs/6x series)

**Source:** `docs/60_FASE_1_RETROSPECTIVA.md` lines 1-5
**Apply to:** `docs/60_SECURITY_BASELINE.md`, `docs/61_COMPLIANCE_LEY_7593.md`

```markdown
# <Title>

**<Key metadata label>:** <value>
**<Key metadata label>:** <value>

---
```

No YAML frontmatter. H1 → H2 → tables + bullets + fenced code blocks. Spanish prose, Spanish comments in code. All code blocks labeled with language tag (`bash`, `python`, `yaml`).

### Shell script boilerplate

**Source:** `scripts/setup_references.sh` lines 1-10
**Apply to:** `scripts/restore-smoke.sh`

```bash
#!/usr/bin/env bash
# scripts/<name>.sh — <descripción en español>
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
```

---

## No Analog Found

| File                  | Role      | Data Flow    | Reason                                                                                                                                                                                |
| --------------------- | --------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `LICENSE` (full text) | root-meta | static-asset | No existing analog for full license text file; closest is `pyproject.toml` license field but those are metadata declarations, not the full text. Use canonical download from GNU.org. |

---

## Codegraph Queries Needed (for executor)

The CLAUDE.md rule "NEVER read `references/` manually — use codegraph" applies. The following queries were attempted but the codegraph CLI was unavailable in the research session (PowerShell execution policy). The research was done via direct Grep/Read with equivalent results. The executor should run these as sanity checks before creating the workflow:

```powershell
# Confirmar que no hay security.yml en referencias (no modelo exacto)
.\bin\codegraph.ps1 files "*security*yml*"

# Confirmar el pattern de concurrency en referencias OCA
.\bin\codegraph.ps1 search "concurrency"

# Confirmar dependabot config en oca-addons-repo-template
.\bin\codegraph.ps1 file "references/oca-addons-repo-template/.github/dependabot.yml"
```

---

## Metadata

**Analog search scope:** `.github/workflows/`, `docs/`, `scripts/`, `README.md`, `pyproject.toml`, `addons/l10n_py_base/__manifest__.py`
**Files scanned:** 10 (3 workflows + 3 docs + 1 script + README + pyproject.toml + 1 manifest)
**Pattern extraction date:** 2026-06-02

---

## PATTERN MAPPING COMPLETE
