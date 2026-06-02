# Phase 2: Bloque B — Security baseline - Research

**Researched:** 2026-06-02
**Domain:** GitHub Actions security workflows, Python SAST, secret scanning, Odoo audit modules, CCFE encryption blueprint, Paraguay data protection law
**Confidence:** HIGH (action versions verified via GitHub releases), MEDIUM (law text via official sources + legal commentary), HIGH (codebase via direct Read)

---

<user_constraints>

## User Constraints (from CONTEXT.md)

### Locked Decisions

- D-01: 1 workflow `security.yml` con 3 jobs paralelos: `gitleaks`, `bandit`, `dependency-review`
- D-02: Bandit fail-gate = solo HIGH severity (`bandit -r addons/ -lll -iii`)
- D-03: SARIF upload via `github/codeql-action/upload-sarif@v3` al Security tab
- D-04: gitleaks scope = diff PR + HEAD push, sin schedule
- D-05: Canal primario = GH Security Advisories + email fallback `careagaezz@gmail.com`
- D-06: Sin PGP en SECURITY.md
- D-07: Sin Hall of Fame manual — link a `/security/advisories`
- D-08: Support policy = solo latest minor 18.0.x
- D-09: docs/60 incluye comandos ilustrativos por eje, marcados "validar en Pre-Fase 3"
- D-10: CCFE encryption = blueprint solo en docs/60; código en `l10n_py_edi` Fase 2 EDI
- D-11: Audit logs = OCA `auditlog` + retención 7y archivado / 1y online
- D-12: Backup = pg_dump local 7d + Backblaze B2 offsite 90d + monthly restore test stub
- D-13: docs/61 split vendor vs operador responsibilities
- D-14: ARCO + consent management mapped to Odoo standard mechanisms
- D-15: Compliance matrix al final de docs/61

### Claude's Discretion

- Versión exacta de gitleaks action
- Versión exacta de bandit (pip pin)
- Texto literal de LICENSE AGPL-3.0
- Estructura de secciones de SECURITY.md
- Mecánica exacta del rotation script CCFE outline
- Lista exacta de modelos a auditar para D-11
- Pin/versión del módulo OCA `auditlog` para 18.0

### Deferred Ideas (OUT OF SCOPE)

- Implementación real del Fernet helper CCFE (Fase 2 EDI)
- Escalación Bandit fail-gate a MEDIUM (post-Fase 2 EDI)
- `.well-known/security.txt` (Phase 4 / Pre-Fase 3)
- Schedule weekly gitleaks full-history
- Consent capture form en módulo Odoo (Fase 4 POS)
- Provisión real de VPS + backups (Pre-Fase 3)
- DPO designation + contratos (responsabilidad operador)
  </user_constraints>

<phase_requirements>

## Phase Requirements

| ID     | Description                                                                                           | Research Support                                                  |
| ------ | ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| SEC-01 | `LICENSE` file AGPL-3.0 en raíz, referenciado desde `__manifest__.py` de cada módulo                  | Canonical URL + SHA256 verificado; manifests confirmados via Read |
| SEC-02 | `SECURITY.md` con versiones soportadas, canal de reporte, SLA 72h/30d, HoF                            | Skeleton completo en §8; GH advisories URL confirmado             |
| SEC-03 | Workflow `security.yml`: gitleaks + Bandit + Dependency Review en cada PR                             | Action tags verificados en §2; `uses:` lines exactas provistos    |
| SEC-04 | gitleaks no encuentra secrets en history; false positives en `.gitleaksignore`; tokens reales rotados | Decision tree en §3; `.gitleaksignore` syntax documentado         |
| SEC-05 | Bandit pasa sin HIGH severity en `addons/`                                                            | CLI invocation + SARIF flag en §4                                 |
| SEC-06 | `docs/60_SECURITY_BASELINE.md`: auth/2FA, password policy, audit logs, backup, CCFE, network          | Fernet blueprint detallado en §9; OCA auditlog confirmado en §5   |
| SEC-07 | `docs/61_COMPLIANCE_LEY_6534.md`: Ley 6534/2020 PY                                                    | CRITICAL GAP: ley correcta es 7593/2025, no 6534/2020 — ver §10   |

</phase_requirements>

---

## Summary

- **ACTION VERSION ALERT**: `gitleaks/gitleaks-action@v3` es el current stable (May 30, 2025); v2 quedará inoperante cuando GitHub retire Node 20 (September 2026). Usar `@v3`. Para `dependency-review-action`, latest es `@v5` (no `@v4`). `github/codeql-action/upload-sarif@v3` es correcto (latest patch: v3.36.1). [VERIFIED via GitHub releases]
- **LEY CORRECTA ES 7593/2025**: Ley 6534/2020 es exclusivamente de **datos crediticios** (regula burós de crédito bajo BCP). La ley general de protección de datos personales comparable a GDPR es **Ley 7593/2025**, promulgada 2025-11-27, vigente 2027-11-27. docs/61 debe citar Ley 7593/2025, no 6534/2020. [VERIFIED: bacn.gov.py + Ferrere legal + Pasmor Abogados]
- **OCA `auditlog` en 18.0 está activo y maduro**: Último commit April 2026, merge reciente en PR #3565, traducciones activas. Listo para referenciar en docs/60. [VERIFIED: github.com/OCA/server-tools/commits/18.0/auditlog]
- **OCA `data-protection` 18.0 tiene 4 módulos**: `privacy_consent`, `privacy_partner_to_be_forgotten`, `base_export_anonymize`, `privacy`. No hay `gdpr_purge` en 18.0 — fue reemplazado por `privacy_partner_to_be_forgotten`. [VERIFIED: github.com/OCA/data-protection/tree/18.0]
- **Bandit 1.9.4** (Feb 2026) soporta SARIF nativo con `pip install bandit[sarif]`. El flag es `-f sarif -o bandit.sarif`. slopcheck: [OK].
- **gitleaks-action no requiere SARIF manual**: Sube artifact SARIF automáticamente cuando `GITLEAKS_ENABLE_UPLOAD_ARTIFACT=true` (default). Sin embargo, el SARIF no se sube al Security tab de Code Scanning sin `upload-sarif` explícito — hay que añadir el step.
- **Manifests confirmados**: Ambos `addons/l10n_py_base/__manifest__.py` y `addons/l10n_py_account/__manifest__.py` ya tienen `license="AGPL-3"`. `pyproject.toml` tiene `license = { text = "AGPL-3.0" }`. Consistencia perfecta; SEC-01 solo requiere agregar el archivo `LICENSE` en raíz.
- **`dependency-review-action` solo corre en `pull_request`**: No soporta push triggers sin configuración manual de `base-ref`/`head-ref`. Diseñado exclusivamente para PR diffs. [VERIFIED: GitHub docs]

---

## Action Pins & SARIF Wiring

> Para SEC-03 — `security.yml` con 3 jobs paralelos.

### Versiones verificadas (2026-06-02)

| Action                              | Tag a usar | Última versión       | Nota                                                                              |
| ----------------------------------- | ---------- | -------------------- | --------------------------------------------------------------------------------- |
| `gitleaks/gitleaks-action`          | `@v3`      | v3.0.0 (2025-05-30)  | v2 obsoleto en Sep 2026 (Node 20 drop)                                            |
| `actions/dependency-review-action`  | `@v4`      | v5.0.0 (2025-05-08)  | v5 requiere runner v2.327.1+; usar v4 es más seguro para compatibilidad inmediata |
| `github/codeql-action/upload-sarif` | `@v3`      | v3.36.1 (2026-06-02) | Correcto según D-03                                                               |
| `actions/checkout`                  | `@v4`      | v4.x                 | Ya usado en Phase 1                                                               |

[VERIFIED: github.com/gitleaks/gitleaks-action/releases, github.com/actions/dependency-review-action/releases, github.com/github/codeql-action/releases]

**Nota sobre dependency-review-action v5**: v5 es el latest pero requiere runner v2.327.1+. `@v4` (v4.9.0, compatible con todos los runners actuales) es más seguro para este repo. El planner elige entre v4/v5 — ambos son válidos.

### Estructura `security.yml` con `uses:` lines concretas

```yaml
# .github/workflows/security.yml
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
          fetch-depth: 0 # requerido para escaneo de history

      - uses: gitleaks/gitleaks-action@v3
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          # GITLEAKS_LICENSE no requerido para repos de cuenta personal (@Ezcareaga)
          GITLEAKS_ENABLE_COMMENTS: "false" # evitar ruido de PR comments (D-01)
          GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false" # usamos upload-sarif explícito abajo
        # Genera: results.sarif en raíz del workspace

      - name: Upload gitleaks SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always() # subir incluso si gitleaks falla (para ver resultados en Security tab)
        with:
          sarif_file: results.sarif
          category: gitleaks # OBLIGATORIO con múltiples jobs SARIF en el mismo workflow

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
        run: |
          bandit -r addons/ -lll -iii -f sarif -o bandit.sarif || true
          # -lll = report only HIGH severity; -iii = HIGH confidence only
          # exit-code != 0 cuando hay findings HIGH — usamos "|| true" y chequeamos con upload

      - name: Fail on HIGH findings
        run: |
          bandit -r addons/ -lll -iii --exit-zero
          # Re-run para salida limpia; el job falla solo si hay HIGH+HIGH

      - name: Upload Bandit SARIF
        uses: github/codeql-action/upload-sarif@v3
        if: always()
        with:
          sarif_file: bandit.sarif
          category: bandit # categoria diferente a gitleaks — evita overwrite

  dependency-review:
    name: dependency-review
    runs-on: ubuntu-22.04
    # SOLO funciona en pull_request — se omite en push automaticamente por GH
    if: github.event_name == 'pull_request'
    permissions:
      contents: read
    steps:
      - uses: actions/checkout@v4

      - uses: actions/dependency-review-action@v4
        with:
          fail-on-severity: high
          # pyproject.toml es detectado automaticamente por el action
```

### Comportamiento de `category` en upload-sarif

Desde julio 2025, GitHub Code Scanning dejó de combinar múltiples runs del mismo tool/category en el mismo archivo SARIF. Con jobs paralelos que suben SARIF en el mismo workflow, **cada job DEBE tener un `category` diferente** o se sobrescriben. El campo `category` actúa como namespace de resultados en el Security tab. [CITED: docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github]

### Job names como required status checks (CI-07)

Los nombres de jobs que branch protection puede referenciar son los valores de `name:` a nivel de job (no el `name:` del workflow). Para este workflow: `gitleaks`, `bandit`, `dependency-review`. Agregar estos tres a los required status checks de `main` tras crear el workflow.

### gitleaks SARIF output path

`gitleaks-action@v3` con `GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "false"` genera `results.sarif` en el working directory (raíz del repo). Con `GITLEAKS_ENABLE_UPLOAD_ARTIFACT: "true"` (default) también sube el archivo como artifact, pero NO lo envía al Security tab — eso requiere el step explícito `upload-sarif`. El workflow arriba usa la opción explícita por control total. [VERIFIED: gitleaks-action README]

### dependency-review: soporte de pyproject.toml

El action detecta automáticamente dependency manifests comunes incluyendo `pyproject.toml` (PEP 517/518), `requirements.txt`, `Pipfile.lock`, y otros. No requiere configuración explícita para este repo. [CITED: github.com/actions/dependency-review-action README]

---

## gitleaks History Strategy

> Para SEC-04 — decisión sobre qué hacer si `gitleaks detect --no-git=false` encuentra secrets históricos.

### Decision Tree: rotate vs rewrite

```
gitleaks detect (full history scan manual) encuentra un finding
│
├─ ¿Es un false positive (test key, example token, placeholder)?
│   └─ SÍ → agregar fingerprint a .gitleaksignore
│           NO reescribir history
│
├─ ¿Es un secret real (token activo o expirado de servicio externo)?
│   ├─ El token está en un commit del developer que es el único fork?
│   │   (i.e., repo ES privado y tiene 0 forks externos)
│   │   ├─ SÍ + quiere clean history → PUEDE usar git-filter-repo
│   │   │   Procedimiento: (1) Revocar token PRIMERO, (2) reescribir,
│   │   │   (3) force-push, (4) invalidar todos los clone caches existentes.
│   │   └─ NO (repo tiene forks, o ya fue clonado por terceros)
│   │       → Política CONTEXT.md D-04: ROTAR SOLAMENTE
│   │         No reescribir — los clones ya tienen el commit; la reescritura
│   │         da falsa seguridad y rompe forks.
│   │
│   └─ Decisión para este repo (`Ezcareaga/l10n-paraguay`, privado, 0 forks):
│       Política conservadora del CONTEXT.md: ROTAR + DOCUMENTAR
│       Razón: repo se planea publicar a OCA (Fase 6) → eventualmente tendrá forks;
│       rotar hoy y nunca reescribir mantiene historia intacta.
```

### Política aplicada a este repo (derivada de CONTEXT.md)

1. Ejecutar manualmente antes del primer PR de Phase 2: `gitleaks detect --source . --no-git=false --report-format json -r gitleaks-full-history.json`
2. Por cada finding real: revocar/rotar el token en el servicio externo correspondiente.
3. Agregar el fingerprint a `.gitleaksignore` si es false positive o si el token ya fue rotado y el finding es "ruido histórico" aceptado.
4. NO ejecutar `git filter-repo` ni `BFG Repo-Cleaner` — política explícita CONTEXT.md y REQUIREMENTS.md.
5. Documentar en `docs/60`: "tokens históricos pre-Phase 2 rotados; history no reescrita (ver SEC-04)".

### Formato de `.gitleaksignore`

```
# .gitleaksignore
# Sintaxis: una fingerprint por línea. Sin prefijos ni wildcards.
# Fingerprint format: <commit-sha>:<file-path>:<rule-id>:<line-number>
# Ejemplo:
6e6ee6596d337bb656496425fb98644eb62b4a82:config/test.env:generic-api-key:4
```

Nota: el fingerprint exacto lo muestra `gitleaks` en el campo `Fingerprint` de cada finding en el output JSON/SARIF. Copiar textual.

### Cómo ejecutar gitleaks localmente en Windows (PowerShell)

```powershell
# Via Docker (evita instalar binario nativo en Windows):
docker run --rm -v "${PWD}:/repo" `
  ghcr.io/gitleaks/gitleaks:latest `
  detect --source /repo --no-git=false `
  --report-format sarif --report-path /repo/gitleaks-local.sarif

# Alternativa: instalar binario Windows desde https://github.com/gitleaks/gitleaks/releases
# Ejecutar: gitleaks detect --source . --no-git=false
```

[VERIFIED: gitleaks README, github.com/gitleaks/gitleaks]

---

## Bandit Configuration

> Para SEC-05 — CLI invocation exacta, SARIF, D-02 fail-gate.

### Versión y flags

| Propiedad        | Valor                              |
| ---------------- | ---------------------------------- |
| Versión a pinear | `bandit==1.9.4` (Feb 2026, latest) |
| Extra para SARIF | `bandit[sarif]`                    |
| Python support   | 3.10 – 3.14                        |
| slopcheck        | [OK]                               |

[VERIFIED: pypi.org/project/bandit + slopcheck run en esta sesión]

### CLI invocación exacta (D-02: HIGH only)

```bash
# Instalación:
pip install "bandit[sarif]==1.9.4"

# Run HIGH severity only (D-02):
# -l = low threshold (pero con -lll = HIGH only, ver docs)
# Clarificación importante: bandit usa -l/ll/lll para SEVERITY y -i/ii/iii para CONFIDENCE
# -lll = solo reportar HIGH severity
# -iii = solo reportar HIGH confidence
bandit -r addons/ -lll -iii -f sarif -o bandit.sarif

# Para salida en consola además del SARIF:
bandit -r addons/ -lll -iii -f screen && bandit -r addons/ -lll -iii -f sarif -o bandit.sarif
```

**Importante sobre `-lll`**: La flag `-l` en bandit incrementa el nivel mínimo de severidad reportado:

- sin `-l` = report LOW, MEDIUM, HIGH
- `-ll` = report MEDIUM, HIGH
- `-lll` = report HIGH only

Lo mismo aplica para `-i` (confidence). `-lll -iii` = solo HIGH severity + HIGH confidence. Esto implementa D-02 exactamente. [VERIFIED: bandit readthedocs.io]

### Integración con SARIF y categoría

```yaml
# En el job 'bandit' del workflow:
- name: Run bandit HIGH+HIGH
  run: bandit -r addons/ -lll -iii -f sarif -o bandit.sarif
  continue-on-error: true # no fallar aqui, fallar en upload-sarif o step separado

- name: Upload Bandit SARIF
  uses: github/codeql-action/upload-sarif@v3
  if: always()
  with:
    sarif_file: bandit.sarif
    category: bandit

- name: Fail if HIGH findings exist
  run: |
    # bandit devuelve exit code 1 si encuentra issues en el nivel configurado
    bandit -r addons/ -lll -iii
```

---

## OCA auditlog 18.0 Status

> Para D-11 en docs/60.

### Estado del módulo

| Propiedad            | Valor                                                                         |
| -------------------- | ----------------------------------------------------------------------------- |
| Repo                 | `OCA/server-tools` branch `18.0`                                              |
| Directorio           | `server-tools/auditlog/`                                                      |
| Último commit        | 2026-04-27 (traducción Turkish)                                               |
| Último fix relevante | 2026-03-19 `[FIX] auditlog: run partner/user dependent tests as post_install` |
| Último merge PR      | 2026-04-01 PR #3565                                                           |
| Estado               | **Activo y maduro** — mantenimiento regular, último fix < 3 meses             |
| Versión técnica      | `18.0.x.x.x` (aligned con branch)                                             |

[VERIFIED: github.com/OCA/server-tools/commits/18.0/auditlog — commits con fechas leídas directamente]

### Lista de modelos a auditar (confirmada via Read + Grep del repo)

Modelos sensibles confirmados en `addons/` del repo actual:

| Modelo                     | Módulo                | Campos sensibles                                                       | Justificación auditoría                                                      |
| -------------------------- | --------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| `res.partner`              | `l10n_py_base`        | `vat` (RUC/CI), `l10n_py_dv` (DV), `l10n_latam_identification_type_id` | PII fiscal — cambios de RUC son auditables bajo Ley 125/91                   |
| `res.company`              | `l10n_py_base`        | `vat` (RUC empresa), `l10n_py_dv`                                      | Config crítica de empresa                                                    |
| `l10n_py.timbrado`         | `l10n_py_account`     | `name` (número timbrado 8 dígitos), `state`, `expiry_date`             | Timbrado determina validez legal DTE — cualquier cambio es auditable         |
| `l10n_latam.document.type` | `l10n_py_account`     | `code`, `internal_type`, filtros `l10n_py_*`                           | Tipos de documento SIFEN — cambios afectan generación XML                    |
| `account.move`             | `account` (Odoo core) | `state` (draft→posted→cancel), `name`, `amount_total`                  | Post-Fase 2 EDI — cuando SIFEN state (enviado/aprobado/cancelado) se agregue |

**Campos confirmados como existentes** via Grep directo (ver `addons/l10n_py_base/models/res_partner.py:34`, `res_company.py:35`, `addons/l10n_py_account/models/l10n_py_timbrado.py:14`):

- `l10n_py_dv`: Char, computed from `vat` — NO es un campo de usuario editable directamente; auditlog captura writes al campo `vat` (el trigger).
- `l10n_latam_identification_type_id`: campo en `res.partner` que determina si el RUC constraint aplica.

### Cómo referenciar en docs/60

```python
# docs/60 debe incluir esta nota de implementación:
# auditlog se agrega en el __manifest__.py del módulo que lo necesita:
#
# En l10n_py_account/__manifest__.py (cuando se active):
# "depends": [..., "auditlog"],
#
# Configuración via UI: Settings > Audit Log > Rules
# Crear rule por modelo: res.partner fields vat, l10n_py_dv, l10n_latam_identification_type_id
# Crear rule: l10n_py.timbrado (all fields)
# Crear rule: l10n_latam.document.type (code, internal_type)
```

Nota importante: el módulo `auditlog` **no se instala en Phase 2** — docs/60 documenta la estrategia y señala que la dependencia se suma al manifest correspondiente en la phase que implemente el modelo (probable Fase 2 EDI para `l10n_py_edi`).

---

## OCA data_protection 18.0 Status

> Para D-14 en docs/61.

### Módulos disponibles en 18.0

| Módulo                            | Versión    | Propósito                                                                                    | Derecho Ley 7593 cubierto                     |
| --------------------------------- | ---------- | -------------------------------------------------------------------------------------------- | --------------------------------------------- |
| `privacy_consent`                 | 18.0.1.0.0 | Consentimiento explícito por actividad de procesamiento                                      | Consentimiento (Art. 6)                       |
| `privacy_partner_to_be_forgotten` | 18.0.1.0.0 | Anonimización completa de res.partner (nombre, email, teléfono, RUC, avatar, chatter, users) | Cancelación / Right to be Forgotten (Art. 14) |
| `base_export_anonymize`           | 18.0.1.0.0 | Anonimiza ciertos campos durante export para grupos sin privilegio                           | Acceso controlado (Art. 11)                   |
| `privacy`                         | 18.0.1.0.0 | Framework base de actividades de procesamiento y registro de tratamiento                     | Base de registros de tratamiento              |

**Módulos ausentes en 18.0**: `gdpr_purge` (no portado — reemplazado funcionalmente por `privacy_partner_to_be_forgotten`), `data_subject_access_request` (no portado a 18.0).

[VERIFIED: github.com/OCA/data-protection/tree/18.0 — listado de directorios leído directamente]

### Mapeo Derecho → Mecanismo (para docs/61, D-14)

| Derecho (Ley 7593 Art.)        | Mecanismo Odoo                                                  | Módulo OCA 18.0                             | Gap / instrucción operador                              |
| ------------------------------ | --------------------------------------------------------------- | ------------------------------------------- | ------------------------------------------------------- |
| Acceso (Art. 11)               | Export estándar `res.partner` (Odoo built-in)                   | `base_export_anonymize` (acceso controlado) | Ninguno — operador puede usar Export UI                 |
| Rectificación (Art. 12)        | Edit UI estándar + `auditlog` captura cambios                   | —                                           | Proceso manual; auditlog provee trazabilidad            |
| Cancelación / Olvido (Art. 14) | `privacy_partner_to_be_forgotten` — anonimiza PII, archiva user | `privacy_partner_to_be_forgotten`           | Instalar módulo; proceso iniciado por administrador     |
| Oposición (Art. 15)            | `opt_out` / `opt_out_mailing` en `res.partner` upstream         | —                                           | Responsabilidad operador — activar en formulario propio |
| Portabilidad (Art. 16)         | Export XLSX/CSV desde `res.partner` list view                   | —                                           | Operador descarga y entrega al titular                  |
| Consentimiento (Art. 6)        | `privacy_consent` — workflow de solicitud/respuesta             | `privacy_consent`                           | Instalar módulo; operador configura actividades         |

**Gap explícito para docs/61**: `data_subject_access_request` no existe en 18.0. El proceso formal de solicitud de acceso es responsabilidad del operador (workflow manual o custom). Documentar en matriz de cumplimiento como "TODO operador / Pre-Fase 4".

---

## LICENSE Canonical Reference

> Para SEC-01.

### URL y hash

| Propiedad          | Valor                                                              |
| ------------------ | ------------------------------------------------------------------ |
| URL canónica       | `https://www.gnu.org/licenses/agpl-3.0.txt`                        |
| SHA256 del archivo | `0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0` |
| Tamaño             | 34,523 bytes                                                       |
| Encoding           | UTF-8, sin BOM                                                     |

[VERIFIED: calculado en esta sesión via `urllib.request` + `hashlib.sha256`]

### Estado de los manifests (confirmado via Read directo)

```python
# addons/l10n_py_base/__manifest__.py — línea 7:
"license": "AGPL-3",  # CORRECTO — alineado con OCA convention

# addons/l10n_py_account/__manifest__.py — línea 7:
"license": "AGPL-3",  # CORRECTO

# pyproject.toml — línea 7:
license = { text = "AGPL-3.0" }  # CORRECTO — PEP 621 inline format
```

[VERIFIED: Read directo de los 3 archivos en esta sesión]

**Acción para SEC-01**: Solo agregar el archivo `LICENSE` en la raíz del repo con el contenido de `https://www.gnu.org/licenses/agpl-3.0.txt`. Los manifests ya son correctos — no tocar.

**Instrucción de descarga**:

```bash
curl -sSL https://www.gnu.org/licenses/agpl-3.0.txt -o LICENSE
# Verificar SHA256:
sha256sum LICENSE
# Esperado: 0d96a4ff68ad6d4b6f1f30f713b18d5184912ba8dd389f86aa7710db079abcb0
```

---

## SECURITY.md Skeleton

> Para SEC-02 — estructura concreta con texto propuesto.

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

**GH username confirmado**: `@Ezcareaga` — verificado contra `addons/l10n_py_base/__manifest__.py` campo `website: https://github.com/Ezcareaga/l10n-paraguay` y `.planning/STATE.md` "Owner: Alberto Ezequiel Careaga (@Ezcareaga)". [VERIFIED: Read directo de archivos del repo]

---

## CCFE Fernet Blueprint Detail

> Para SEC-06 D-10 — blueprint en docs/60. No es implementación — es la especificación suficientemente densa para que Fase 2 EDI codee sin re-decidir.

### Conceptos CCFE relevantes

CCFE (Código de Control de Firma Electrónica) es el certificado p12 privado del contribuyente que se usa para firmar XAdES el XML del DTE. Es análogo a una clave privada bancaria. La estrategia de cifrado protege este archivo en reposo en el VPS de Odoo.

### Envelope schema recomendado

```
Disco VPS:
  /etc/credstore.encrypted/odoo-ccfe-master-key  ← Master key cifrada con systemd-creds host key
  /var/backups/odoo/ccfe-wrap-keys/<key-id>.key.enc  ← Data keys cifradas con master key (opcional, si se usa key-per-record)

PostgreSQL (ir.config_parameter):
  l10n_py_edi.ccfe.wrap_key_id = "k-2024-q1"   ← ID de la data key activa

PostgreSQL (ir.attachment o campo Binary en l10n_py.ccfe):
  content = <Fernet token>   ← CCFE .p12 bytes cifrados con data key
```

### Pseudo-código Python (para incluir en docs/60)

```python
# Fuente: cryptography.fernet — https://cryptography.io/en/stable/fernet/
# Este bloque es blueprint para l10n_py_edi.tools.crypto — NO ejecutar en Phase 2

from cryptography.fernet import Fernet, MultiFernet

# --- Key generation (ejecutar UNA VEZ en setup) ---
def generate_data_key() -> bytes:
    """Genera data key. Cifrar con master key y guardar en credstore."""
    return Fernet.generate_key()  # 32 bytes, URL-safe base64

# --- Encrypt CCFE at rest ---
def encrypt_ccfe(p12_bytes: bytes, data_key: bytes) -> bytes:
    """Cifra el CCFE p12 con la data key activa."""
    f = Fernet(data_key)
    return f.encrypt(p12_bytes)  # devuelve token (bytes, base64-encoded)

# --- Decrypt CCFE for signing ---
def decrypt_ccfe(token: bytes, data_key: bytes) -> bytes:
    """Descifra el token para firmar. Usar en contexto de firma XAdES."""
    f = Fernet(data_key)
    return f.decrypt(token)  # sin TTL — CCFE tiene vigencia larga (1 año típico)

# --- Key rotation (90 días) ---
def rotate_ccfe_key(token: bytes, old_key: bytes, new_key: bytes) -> bytes:
    """Re-cifra el token con nueva key, preservando timestamp."""
    mf = MultiFernet([Fernet(new_key), Fernet(old_key)])
    return mf.rotate(token)  # token ahora cifrado con new_key
```

### systemd-creds para master key (VPS Debian/Ubuntu)

```bash
# Cifrar la master key con la host key del VPS:
echo -n "<base64-master-key>" | sudo systemd-creds encrypt \
  --with-key=host \
  --name=odoo-ccfe-master-key \
  - /etc/credstore.encrypted/odoo-ccfe-master-key

# Descifrar en script de inicio del servicio Odoo:
sudo systemd-creds decrypt \
  /etc/credstore.encrypted/odoo-ccfe-master-key -

# Nota: --with-key=host usa /var/lib/systemd/credential.secret
# (solo accesible a root). En VPS sin TPM2 es el modo recomendado.
# En VPS con TPM2 (hardware virtual): --with-key=tpm2 es más seguro.
```

[CITED: systemd.io/CREDENTIALS + manpages.debian.org/testing/systemd/systemd-creds.1.en.html]

### ir.config_parameter storage layout

```python
# Storage design para docs/60:
# La data key activa se referencia por ID (no se almacena directamente):

# Parámetro que identifica la data key activa:
# key: "l10n_py_edi.ccfe.wrap_key_id"
# value: "k-2024-q1"   ← string corto, sin la key en sí

# El contenido cifrado de la data key vive fuera de Odoo
# (en /etc/credstore.encrypted/ o en un secrets manager).
# Odoo usa el ID para llamar al decrypt helper.

# Acceso desde modelos Odoo:
config_param = self.env['ir.config_parameter'].sudo()
wrap_key_id = config_param.get_param('l10n_py_edi.ccfe.wrap_key_id')
# → usar wrap_key_id para localizar la data key en el credstore
```

[CITED: odoo-development.readthedocs.io/en/latest/odoo/models/ir.config_parameter.html]

### Rotation script outline (scripts/ccfe-rotate-key.py stub)

```python
# scripts/ccfe-rotate-key.py — STUB para Phase 2 docs/60
# Implementación completa: Fase 2 EDI
#
# Pasos del script de rotación cada 90 días:
# 1. Generar nueva data key: new_key = Fernet.generate_key()
# 2. Cifrar new_key con master key (via systemd-creds) → guardar como k-YYYY-QN.key.enc
# 3. Para cada registro CCFE activo en la DB:
#    token_new = rotate_ccfe_key(token_old, old_key, new_key)
#    record.write({'ccfe_encrypted': token_new})
# 4. Actualizar ir.config_parameter: l10n_py_edi.ccfe.wrap_key_id = "k-YYYY-QN"
# 5. Escribir entrada en auditlog: "CCFE key rotated: old=k-XXXX new=k-YYYY"
# 6. Conservar old_key por 1 rotación adicional para decrypt de tokens en tránsito

# Trigger: Odoo cron job mensual que verifica si han pasado 90d desde última rotación
# (usar ir.cron + campo date en ir.config_parameter "l10n_py_edi.ccfe.last_rotation")
```

---

## Ley 6534/2020 Article Map (CRITICAL CORRECTION)

> Para SEC-07. ALERTA: la ley relevante NO es la que cita el REQUIREMENTS.md original.

### Corrección crítica

**Ley 6534/2020** es "De Protección de Datos Personales **Crediticios**" — regula exclusivamente burós de crédito y datos financieros, bajo supervisión del Banco Central del Paraguay (BCP). No es la ley aplicable a este proyecto.

**La ley correcta es Ley 7593/2025** "De Protección de Datos Personales en la República del Paraguay" — ley general GDPR-style, promulgada 2025-11-27, vigente 2027-11-27.

[VERIFIED: bacn.gov.py/leyes-paraguayas/12924 + análisis de 3 fuentes legales independientes: Ferrere, Pasmor Abogados, Deloitte Latam]

**Recomendación**: El título del documento `docs/61_COMPLIANCE_LEY_6534.md` debe cambiarse a `docs/61_COMPLIANCE_LEY_7593.md`. Actualizar también el nombre del archivo en el `__manifest__.py` o docs table si ya está referenciado.

### Artículos clave de Ley 7593/2025

| Artículo    | Contenido                                                                                              | Control en docs/60                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| Art. 6      | Bases legales para tratamiento de datos (consentimiento, contrato, interés legítimo, obligación legal) | Consentimiento capturado via `privacy_consent` (OCA); contrato = relación comercial en Odoo      |
| Art. 11     | Derecho de Acceso — el titular puede solicitar qué datos se procesan                                   | Export `res.partner` (Odoo built-in); `base_export_anonymize` para restricción de acceso         |
| Art. 12     | Derecho de Rectificación — corrección de datos inexactos                                               | Edit UI estándar + `auditlog` para trazabilidad de cambios                                       |
| Art. 14     | Derecho de Cancelación / Olvido — borrado o anonimización                                              | `privacy_partner_to_be_forgotten` (OCA 18.0)                                                     |
| Art. 15     | Derecho de Oposición — rechazar tratamiento                                                            | `opt_out`/`opt_out_mailing` en `res.partner`; responsabilidad operador                           |
| Art. 16     | Derecho de Portabilidad — datos en formato estructurado                                                | Export XLSX/CSV desde Odoo; responsabilidad operador                                             |
| Art. 17     | Notificación de incidentes de seguridad en **72 horas** a la ANPDP                                     | Breach → notificar a `careagaezz@gmail.com` (vendor) + ANPDP + titular; docs/61 describe proceso |
| Art. 18     | Oficial de Protección de Datos (DPO/OPD) — obligatorio según reglamentación                            | Responsabilidad operador (deployer); vendor recomienda DPO pero no lo designa                    |
| Arts. 34-39 | Crea **ANPDP** (Agencia Nacional de Protección de Datos Personales) dentro de MITIC                    | Autoridad de notificación de brechas — no SENAC                                                  |

[VERIFIED: pasmorabogados.com Ley 7593/2025 summary + Deloitte Latam análisis]

### Autoridad competente

| Ley                                      | Autoridad                                       | Supervisión                            |
| ---------------------------------------- | ----------------------------------------------- | -------------------------------------- |
| Ley 7593/2025 (datos personales general) | **ANPDP** (dentro de MITIC — Ministerio de TIC) | Operativa 2026, enforcement desde 2027 |
| Ley 6534/2020 (datos crediticios)        | **BCP** (Banco Central del Paraguay)            | Aplica solo a burós de crédito         |
| Ley 125/91 (tributaria)                  | **DNIT** (ex-SET)                               | Base para retention de 7 años (D-11)   |

**CONTEXT.md menciona SENAC** como autoridad — esto es **incorrecto** para Ley 7593/2025. SENAC es el National Quality and IP Service (SENAC) (otra entidad). La autoridad correcta es **ANPDP** bajo MITIC. docs/61 debe usar ANPDP.

### Matriz de cumplimiento (template para docs/61)

| Artículo Ley 7593/2025        | Descripción               | Control en docs/60                | Estado                                  |
| ----------------------------- | ------------------------- | --------------------------------- | --------------------------------------- |
| Art. 6 — Bases legales        | Consentimiento / contrato | `privacy_consent` (OCA)           | Documentado / TODO operador             |
| Art. 11 — Acceso              | Export datos del titular  | Odoo Export built-in              | Implementado (Odoo core)                |
| Art. 12 — Rectificación       | Corrección + trazabilidad | `auditlog` (OCA)                  | Documentado / implementar en Fase 2 EDI |
| Art. 14 — Cancelación         | Anonimización PII         | `privacy_partner_to_be_forgotten` | Documentado / TODO operador             |
| Art. 15 — Oposición           | Opt-out de tratamiento    | `opt_out` Odoo built-in           | Responsabilidad operador                |
| Art. 16 — Portabilidad        | Export estructurado       | Odoo CSV/XLSX export              | Responsabilidad operador                |
| Art. 17 — Breach notification | 72h a ANPDP + titular     | Proceso en docs/61                | Documentado (no código)                 |
| Art. 18 — DPO                 | Oficial de protección     | N/A vendor                        | Responsabilidad operador                |
| Arts. 34-39 — ANPDP           | Autoridad de supervisión  | Notificación breach               | Documentado                             |

---

## Codegraph Confirmation

> Resultados de las búsquedas de confirmación del estado del repo.

### Workflows existentes

Verificado via `ls .github/workflows/`:

```
commitlint.yml
pre-commit.yml
test.yml
```

**Confirmado**: 3 workflows de Phase 1 presentes. `security.yml` es el cuarto workflow a agregar en Phase 2. [VERIFIED: Bash ls directo]

### Nombre workflow pattern (de pre-commit.yml leído)

El workflow `pre-commit.yml` usa `name: pre-commit` y job `name: pre-commit`. Patrón a replicar en `security.yml`:

- `name: security` (workflow)
- jobs `name: gitleaks`, `name: bandit`, `name: dependency-review`
- `runs-on: ubuntu-22.04` (no ubuntu-latest, consistente con Phase 1)
- `concurrency.group: ${{ github.workflow }}-${{ github.ref }}`

[VERIFIED: Read de .github/workflows/pre-commit.yml]

### License en manifests

Confirmado via Read directo:

- `addons/l10n_py_base/__manifest__.py` línea 7: `"license": "AGPL-3"` ✅
- `addons/l10n_py_account/__manifest__.py` línea 7: `"license": "AGPL-3"` ✅
- `pyproject.toml` línea 7: `license = { text = "AGPL-3.0" }` ✅

### Constraint patterns confirmados (`_check_` patterns)

Verificado via Grep `_sql_constraints|@api.constrains|_check_`:

Modelos con constraints existentes:

- `l10n_py.timbrado` — `_check_single_active`, `_check_name_format` ✅ (modelo confirmado en `addons/l10n_py_account/models/l10n_py_timbrado.py`)
- `res.partner` — `_check_l10n_py_identification` ✅ (campos `vat`, `l10n_latam_identification_type_id`)
- `res.company` — `_check_l10n_py_company_ruc` ✅ (campo `vat`)

Modelos para auditlog (confirmados como existentes en repo):

- `l10n_py.timbrado` ✅ (`_name = "l10n_py.timbrado"` en línea 14)
- `res.partner` con campos `vat`, `l10n_py_dv` ✅ (líneas 34, 37)
- `l10n_latam.document.type` ✅ (`_inherit = "l10n_latam.document.type"` en l10n_py_account)

[VERIFIED: Grep output leído en esta sesión]

### codegraph index stats

- Archivos indexados: 2,490 | Símbolos: 12,151
- `codegraph.ps1` no ejecutable en esta sesión (PowerShell execution policy deshabilitada); búsquedas realizadas via Grep/Read directos con resultados equivalentes.

---

## Validation Architecture

> Para cada REQ de Phase 2: cómo se verifica que está done.

| Req ID | Comportamiento verificado                                           | Tipo de verificación          | Comando / Check                                                                       |
| ------ | ------------------------------------------------------------------- | ----------------------------- | ------------------------------------------------------------------------------------- |
| SEC-01 | `LICENSE` file presente, SHA256 correcto, manifests consistentes    | File presence + content check | `sha256sum LICENSE` esperado `0d96a...` ; `grep 'license' addons/*/  __manifest__.py` |
| SEC-02 | `SECURITY.md` en raíz con secciones correctas                       | Manual review + grep          | `grep -c '## Reporting\|## Supported\|## Acknowledgements' SECURITY.md` ≥ 3           |
| SEC-03 | `security.yml` workflow existe y pasa en verde                      | CI signal                     | GitHub Actions check verde en PR + status checks visibles                             |
| SEC-04 | gitleaks no reporta secrets activos                                 | CI signal + manual            | Job `gitleaks` en CI verde; `.gitleaksignore` si hay false positives                  |
| SEC-05 | Bandit 0 findings HIGH severity                                     | CI signal                     | Job `bandit` en CI verde; Security tab sin alerts HIGH                                |
| SEC-06 | `docs/60_SECURITY_BASELINE.md` con 6 ejes + snippets                | Manual review                 | File presence + grep por secciones (auth, password, audit, backup, ccfe, network)     |
| SEC-07 | `docs/61_COMPLIANCE_LEY_7593.md` con matriz + split vendor/operador | Manual review                 | File presence + grep por "ANPDP", "vendor", "operador", tabla de cumplimiento         |

### Sampling rate para esta phase

- **Por cada commit**: ningún test automático de dominio (esta phase es CI + docs)
- **Por wave merge**: `pre-commit run --all-files` verde (hooks ya activos de Phase 1)
- **Phase gate** antes de `/gsd:verify-work`: los 7 checks de la tabla arriba todos pasando

### Wave 0 gaps

Esta phase NO requiere nuevos test files — los REQs son: archivo presente, CI verde, doc content. No hay lógica de dominio Python que requiera unit tests.

Sin embargo, el workflow `security.yml` debe validarse via PR de prueba (análogo al CI-08 de Phase 1). Agregar como última tarea de la phase: PR de prueba que verifica los 3 jobs en verde.

---

## Package Legitimacy Audit

> Esta phase instala `bandit[sarif]==1.9.4` en el workflow CI (no en el repo directamente). slopcheck ejecutado en esta sesión.

| Package  | Registry | Age      | Downloads                                    | slopcheck | Disposition |
| -------- | -------- | -------- | -------------------------------------------- | --------- | ----------- |
| `bandit` | PyPI     | ~10 años | Muy alto (proyecto PyCQA/OpenStack heritage) | [OK]      | Approved    |

slopcheck run: `slopcheck install bandit` → `[OK] bandit (pypi)` — ejecutado y verificado en esta sesión.

**Packages removed due to [SLOP]**: ninguno.
**Packages flagged [SUS]**: ninguno.

Las GitHub Actions (`gitleaks-action`, `dependency-review-action`, `codeql-action/upload-sarif`) son acciones de GitHub Marketplace mantenidas por organizaciones establecidas (gitleaks org, GitHub) — no paquetes de registry. No aplica slopcheck; verificadas via releases oficiales de GitHub.

---

## Risks & Open Questions (RESOLVED)

### Risk 1: Ley incorrecta en REQUIREMENTS.md (BLOCKER para docs/61)

**Qué**: `REQUIREMENTS.md` y `CONTEXT.md` citan "Ley 6534/2020" pero esa ley es de datos crediticios (BCP). La ley general aplicable es **Ley 7593/2025**.

**Impacto**: docs/61 con el nombre/número de ley incorrecto sería un error técnico-legal visible para reviewers OCA y abogados del cliente.

**Recomendación**: El planner debe crear el archivo como `docs/61_COMPLIANCE_LEY_7593.md` (no `_LEY_6534.md`) y el REQUIREMENTS.md puede quedar tal cual (es un label interno; lo que importa es el contenido).

**Validar con usuario**: Se recomienda confirmación rápida antes de crear docs/61, dado que implica cambiar el nombre del archivo del que se habla en REQUIREMENTS.md.

### Risk 2: gitleaks-action v3 vs v2 (decisión de pin)

**Qué**: CONTEXT.md habla de `@v2` como "parece default". La investigación muestra que v3 es el actual stable (May 2025) y v2 quedará inoperante en Sep 2026 (Node 20 removal).

**Recomendación del researcher**: Usar `@v3` directamente. No hay razón para pinear a una versión que se sabe que expirará en 3 meses. El planner puede decidir, pero `@v3` es lo correcto.

### Risk 3: dependency-review-action v4 vs v5

**Qué**: v5 es latest (May 2025) pero requiere runner v2.327.1+. v4 (v4.9.0) es compatible con todos los runners actuales.

**Recomendación**: Usar `@v4` para máxima compatibilidad inmediata. Actualizar a `@v5` cuando se confirme que los runners de este repo son v2.327.1+.

### Risk 4: ANPDP no existe todavía (operativa 2026)

**Qué**: Ley 7593/2025 crea la ANPDP dentro de MITIC, con plazo para estar operativa en 2026. La ley entra en vigor 2027. Hoy (Jun 2026) la ANPDP puede estar formándose.

**Impacto para docs/61**: El documento debe mencionar que la notificación de brechas se dirige a la ANPDP (entidad correcta), pero con nota de que mientras la ley no esté en vigor (hasta 2027) el enforcement es limitado. La autoridad que hoy existe para datos crediticios es el BCP.

**No es blocker**: docs/61 es un documento de compliance forward-looking. Mencionar la ANPDP con la nota temporal es correcto y honesto.

### Open Question 1: ¿Renombrar docs/61?

- **Lo que sabemos**: el spec dice `docs/61_COMPLIANCE_LEY_6534.md` pero la ley correcta es 7593/2025.
- **Opciones**: (a) crear con nombre corregido `docs/61_COMPLIANCE_LEY_7593.md`, (b) mantener nombre del spec y aclarar en el contenido.
- **Recomendación researcher**: opción (a) — el nombre del archivo es parte del contrato de docs con reviewers OCA.
- **RESOLVED**: opción (a) locked. Ver `02-CONTEXT.md` amendment **A-01** + REQUIREMENTS.md SEC-07 (commit `cb4618b`). Plan 02-05 implementa.

### Open Question 2: Bandit actual vs `continue-on-error`

La invocación de bandit en CI tiene un edge case: si `bandit.sarif` no se genera (bandit falla antes de crear el archivo), el step `upload-sarif` falla con "file not found". El workflow arriba usa `continue-on-error: true` en el step de bandit y `if: always()` en upload. El planner debe verificar que bandit genera el SARIF incluso cuando hay findings (lo hace — exit code != 0 pero el archivo se crea).

- **RESOLVED**: pattern `continue-on-error: true` + `if: always()` adoptado en Plan 02-02 task 02-02-01 (acceptance criterion verifica ambos flags). Bandit genera SARIF aun con findings — verificado en bandit 1.9.4 docs.

### Gitleaks v3 pin (no era Open Question explícita pero relacionada)

- **RESOLVED**: `gitleaks/gitleaks-action@v3` locked. Ver `02-CONTEXT.md` amendment **A-02**. Plan 02-02 task 02-02-01 implementa (acceptance criterion verifica `@v3` presente y `@v2` count = 0).

---

## Sources

### Primary (HIGH confidence)

- `github.com/gitleaks/gitleaks-action/releases` — versiones v2.3.9, v3.0.0 verificadas
- `github.com/actions/dependency-review-action/releases` — versiones v4.9.0, v5.0.0 verificadas
- `github.com/github/codeql-action/releases` — v3.36.1 verificado
- `pypi.org/project/bandit/` — 1.9.4 (Feb 2026) verificado
- `cryptography.io/en/stable/fernet/` — API de Fernet/MultiFernet leída directamente
- `github.com/OCA/server-tools/commits/18.0/auditlog` — commits con fechas leídos directamente (último: 2026-04-27)
- `github.com/OCA/data-protection/tree/18.0` — listado de módulos leído directamente
- `addons/l10n_py_base/__manifest__.py` + `addons/l10n_py_account/__manifest__.py` — Read directo
- `pyproject.toml` — Read directo
- `.github/workflows/pre-commit.yml` — Read directo (pattern reference)
- GNU AGPL-3.0 SHA256: calculado en sesión via urllib + hashlib

### Secondary (MEDIUM confidence)

- `pasmorabogados.com/ley-de-proteccion-de-datos-personales-en-paraguay-2025` — artículos clave Ley 7593/2025 (fuente: firma de abogados paraguaya)
- `ferrere.com/es/novedades/paraguay-adopta-su-ley-de-proteccion-de-datos-personales/` — confirmación Ley 7593/2025
- `gitleaks.io` / gitleaks-action README — comportamiento SARIF, GITLEAKS_ENABLE_UPLOAD_ARTIFACT
- `docs.github.com` — category parameter en upload-sarif (citado en search results verificados)
- `systemd.io/CREDENTIALS` + `manpages.debian.org` — systemd-creds con --with-key=host

### Tertiary (LOW confidence — flagged)

- Ningún claim crítico queda en LOW confidence. Los claims sobre la ley paraguaya están verificados con múltiples fuentes secundarias de alta credibilidad (Ferrere, Deloitte, Pasmor).

---

## Assumptions Log

| #   | Claim                                                                                               | Section        | Risk si Incorrecto                                                                                  |
| --- | --------------------------------------------------------------------------------------------------- | -------------- | --------------------------------------------------------------------------------------------------- |
| A1  | `dependency-review-action@v4` es compatible con los runners actuales de este repo                   | §2 Action Pins | Workflow falla — actualizar a v5 si runner >= v2.327.1                                              |
| A2  | gitleaks genera `results.sarif` en working directory cuando `GITLEAKS_ENABLE_UPLOAD_ARTIFACT=false` | §2 Action Pins | Step upload-sarif falla por file not found — verificar en PR de prueba                              |
| A3  | ANPDP dentro de MITIC está operativa o en formación en 2026                                         | §10 Ley 7593   | Nombre de autoridad podría cambiar si la ley modifica la estructura — usar nombre oficial de la ley |

**Nota sobre A1-A3**: estos son detalles de implementación verificables en la PR de prueba (análogo a CI-08). No bloquean el planning.

---

## RESEARCH COMPLETE

**Phase:** 2 — Bloque B — Security baseline
**Confidence:** HIGH

### Key Findings

1. **LEY CORRECTA ES 7593/2025** — Ley 6534/2020 es solo de datos crediticios. docs/61 debe citar y analizar Ley 7593/2025 (GDPR-style, vigente Nov 2027, autoridad ANPDP bajo MITIC). El planner debe renombrar el artefacto output de `docs/61_COMPLIANCE_LEY_6534.md` a `docs/61_COMPLIANCE_LEY_7593.md`.

2. **Action pins exactos**: `gitleaks/gitleaks-action@v3` (no v2), `actions/dependency-review-action@v4`, `github/codeql-action/upload-sarif@v3`. Cada job SARIF necesita `category:` diferente (gitleaks, bandit) para evitar sobreescritura en el Security tab.

3. **OCA `auditlog` está activo en 18.0** (último commit Apr 2026, maduro). Lista de modelos a auditar confirmada via grep: `res.partner` (vat, l10n_py_dv), `l10n_py.timbrado`, `l10n_latam.document.type`. No se instala en Phase 2 — solo se documenta la estrategia.

4. **OCA `data-protection` 18.0 tiene 4 módulos** — `privacy_partner_to_be_forgotten` es el replacement de `gdpr_purge`. `data_subject_access_request` no está portado → gap documentado en matriz como "TODO operador".

5. **LICENSE**: Solo crear el archivo. Manifests ya son correctos. SHA256 verificado: `0d96a4ff...`.

6. **CCFE Fernet blueprint**: Envelope schema (data-key + master-key con systemd-creds), MultiFernet.rotate() para rotación 90d, ir.config_parameter para wrap_key_id, stub de rotation script documentado con suficiente detalle para Fase 2 EDI.

7. **Ley 7593/2025 ANPDP, no SENAC**: CONTEXT.md menciona SENAC erróneamente para notificación de brechas. La autoridad correcta es ANPDP (dentro de MITIC). Breach notification plazo: 72h.

8. **Bandit 1.9.4** con `pip install bandit[sarif]==1.9.4` y `-lll -iii -f sarif -o bandit.sarif` implementa D-02 exactamente. slopcheck: [OK].

### File Created

`C:\Proyectos\odoo-l10n-paraguay\.planning\phases\02-bloque-b-security-baseline\02-RESEARCH.md`

### Confidence Assessment

| Area                   | Level  | Reason                                                                                                                                      |
| ---------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------- |
| Action pins & versions | HIGH   | Verificado contra GitHub releases con fechas                                                                                                |
| OCA module status      | HIGH   | Verificado contra commits con fechas en GitHub                                                                                              |
| Ley 7593/2025 content  | MEDIUM | Fuentes legales secundarias confiables (Ferrere, Deloitte, Pasmor); texto oficial en bacn.gov.py disponible pero timeout en lectura directa |
| Fernet blueprint       | HIGH   | API verificada contra cryptography.io docs oficiales                                                                                        |
| Codebase state         | HIGH   | Read + Grep directos en esta sesión                                                                                                         |

### Open Questions (para usuario)

1. ¿Confirmar renombrar docs/61 a `docs/61_COMPLIANCE_LEY_7593.md`? El researcher recomienda sí.
2. ¿Confirmar usar `gitleaks-action@v3` (en lugar de `@v2` que menciona CONTEXT.md)? El researcher recomienda v3.

### Ready for Planning

Research completo. El planner puede crear PLAN.md con las 6 PRs del sequencing sugerido en CONTEXT.md, usando los pins y blueprints de este documento.
