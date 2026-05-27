# Fase 1 — Retrospectiva consolidada

**Período:** 2026-05-19 → 2026-05-25 (1 semana)
**Resultado:** 2 módulos Odoo 18 instalables, 97 tests verdes, 2 PRs mergeados.

---

## Entregables

| Módulo                        | Versión      | Tests        | Estado                                    |
| ----------------------------- | ------------ | ------------ | ----------------------------------------- |
| `l10n_py_base`                | `18.0.1.1.0` | 23           | ✅ mergeado en `main`                     |
| `l10n_py_account`             | `18.0.1.0.0` | 74           | ✅ mergeado en `main`                     |
| `scripts/extract_puc_rg49.py` | —            | —            | ✅ genera CSVs PUC desde XLS oficial DNIT |
| **Total Fase 1**              | —            | **97 tests** | **100% verde**                            |

## Sub-fases

### Fase 1a (2026-05-19 → 2026-05-22)

Bootstrap del repo + primer módulo OCA-style.

**Commits relevantes** (`git log` antes de Fase 1b):

- `e3c2bcb` — feat(l10n_py_base): bootstrap módulo OCA con catálogos SIFEN + validación CI/RUC
- `d64bf58` — docs(claude): enforce skill+subagent defaults, mark Fase 1a complete
- `72c9904` — fix(infra): silenciar FATAL de Postgres logs en docker-compose

**Deliverables Fase 1a:**

- `l10n_py_base 18.0.1.0.0` con catálogos SIFEN (regímenes, tipos de
  contribuyente, naturaleza receptor, distritos, ciudades, identification types)
- Validación módulo 11 RUC + CI
- Docker Compose Odoo 18 + Postgres 16, healthcheck, mount `addons/` only
- 17 tests (10 TestDataLoaded + 7 TestRucValidation)

### Fase 1b (2026-05-25)

20 commits atómicos. PR1 (bump base 1.1.0) + PR2 (account from scratch).

#### PR1 — `l10n_py_base 18.0.1.1.0` (7 commits)

[GitHub PR #1](https://github.com/Ezcareaga/l10n-paraguay/pull/1) — mergeado vía rebase.

- `b6bc1f1` chore: bump version 18.0.1.1.0
- `550348c` feat: l10n_py.economic_activity catalog model
- `2a6c27f` docs(bugs): docker exec entrypoint gotcha (BUGS #2)
- `bfd8f21` feat: tree/form/menu economic_activity
- `ee17599` feat: extend res.company with PY fiscal identity fields
- `bcdf464` test: res.company PY extension (4 tests)
- `1c6c907` feat: Paraguay (Fiscal) section in company form
- `391cad4` docs: release notes 18.0.1.1.0

**Modelos nuevos:**

- `l10n_py.economic_activity` — catálogo SIFEN actividades (manual load por
  ahora; WS SET en Fase 2)

**Extensiones a `res.company`:**

- `l10n_py_taxpayer_type_id` (Many2one)
- `l10n_py_regime_id` (Many2one)
- `l10n_py_economic_activity_ids` (Many2many)
- `l10n_py_nombre_fantasia` (Char)
- `l10n_py_dv` (Char computed) — DV módulo 11 calculado desde `vat`
- `@api.constrains` valida RUC módulo 11 si `country_id == PY`

**Vistas:**

- Nuevo tab "Paraguay (Fiscal)" en form view de `res.company`, visible solo si country == PY

#### PR2 — `l10n_py_account 18.0.1.0.0` (20 commits)

[GitHub PR #2](https://github.com/Ezcareaga/l10n-paraguay/pull/2) — mergeado vía rebase.

**Modelos nuevos:**

- `l10n_py.afectacion_iva` — catálogo SIFEN TABLA 6 (4 records: Gravado /
  Exonerado / Exento / Parcial)
- `l10n_py.timbrado` — autorización DNIT con validaciones (8 dígitos numéricos,
  single active per company, \_sql_constraints uniqueness)
- `l10n_py.point_of_emission` — establecimiento + punto de expedición SIFEN
  (3 dígitos zero-pad en `name`, `_sql_constraints` unique por
  `(company, est, code)`)
- `l10n.py.account.migration.wizard` — wizard 3 modos
  (clean/assisted/coexist) para companies con chart preexistente

**Extensiones:**

| Modelo                     | Cambios                                                                                                                                                                                                                                                                                                             |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `res.company`              | `_localization_use_documents` retorna True si `account_fiscal_country_id == PY`; `l10n_py_active_timbrado_id` computed; `l10n_py_timbrado_ids` O2M                                                                                                                                                                  |
| `account.journal`          | `l10n_py_point_of_emission_id` (M2O); constraint requiere PoE en journals sale + PY + use_documents; constraint inverso (PoE → use_documents debe estar on); ambos constraints skip en `install_mode` para no romper chart_template load                                                                            |
| `account.move`             | `_get_starting_sequence` retorna `EST-POE-0000000`; `_get_last_sequence_domain` filtra por doc_type; `_post` defensivo (solo sale journals) raise si falta PoE; `_get_sequence_cache` scoped por doc_type; `_auto_init` re-crea índice unique `account_move_unique_name` para incluir `l10n_latam_document_type_id` |
| `account.move.line`        | `l10n_py_iva_proporcion` (Integer 1-100) para "gravado parcial" SIFEN                                                                                                                                                                                                                                               |
| `account.tax`              | `l10n_py_afectacion_iva_id` (M2O) para campo E731 del XML SIFEN                                                                                                                                                                                                                                                     |
| `l10n_latam.document.type` | `_format_document_number` override valida y normaliza a `EEE-PPP-NNNNNNN` (3-3-7 dígitos zero-pad)                                                                                                                                                                                                                  |

**Data (CSVs):**

- `data/l10n_py.afectacion_iva.csv` — 4 records (Tabla 6 SIFEN)
- `data/l10n_latam.document.type.csv` — 5 records (FE=1, AF=4, NC=5, ND=6, NR=7)
- `data/template/account.account-py.csv` — 139 cuentas (80 activas default)
- `data/template/account.group-py.csv` — 164 grupos jerárquicos
- `data/template/account.tax-py.csv` — 6 taxes IVA + repartition lines
- `data/template/account.tax.group-py.csv` — 1 tax group "IVA Paraguay"
- `data/template/account.fiscal.position-py.csv` — placeholder vacío (Fase 2)

**Chart template:**

- `models/template_py.py` — Odoo 18 API moderna con `@template("py")` decorators
- 3 decorators: base template data, `res.company` defaults, `account.journal` defaults
- **No `code_digits`** — PUC RG 49/14 tiene códigos de 2-11 dígitos; padding
  uniforme distorsionaría códigos canónicos DNIT

**Hooks + UX:**

- `_post_init_hook` defensivo (Fase 2 lo extiende):
  - Detecta journals sale PY con `use_documents=True` pero sin PoE → desactiva
    - crea mail activity para que el usuario los configure
  - Warning si hay chart custom con >20 cuentas preexistentes (sugiere wizard)
- 4 menús bajo `Contabilidad → Configuración → Paraguay`:
  Timbrados / Puntos de Emisión / Afectación IVA / Migración Chart

**Tests (74):**

| Test file                            | Cuenta                 |
| ------------------------------------ | ---------------------- |
| `test_account_move_defensive.py`     | 3                      |
| `test_account_move_sequence.py`      | 8                      |
| `test_chart_template.py`             | 8                      |
| `test_company_extension.py`          | 4                      |
| `test_document_types.py`             | 12                     |
| `test_hechauka_critical_accounts.py` | 2 (leaf + groups)      |
| `test_journal_extension.py`          | 7                      |
| `test_migration_wizard.py`           | 3                      |
| `test_point_of_emission.py`          | 6                      |
| `test_post_init_hook.py`             | 2                      |
| `test_pyme_e2e.py`                   | 1 (smoke E2E completo) |
| `test_taxes.py`                      | 10                     |
| `test_timbrado.py`                   | 8                      |

## Decisiones técnicas relevantes

### Sequence per-doc-type — requirió 2 fixes no triviales

**Problema:** SIFEN exige que cada tipo de documento (FE/NC/ND) en el mismo
journal tenga su propia secuencia correlativa empezando en `0000001`. l10n_ar
y l10n_ec no tienen este problema porque sus formatos prefijan el `name` con
`doc_code_prefix` (ej. `"FA-A 00001-00000001"` vs `"NC-A 00001-00000001"`),
dándole a cada doc_type un nombre distinto en el unique index. Paraguay no
puede por requisito SIFEN — el formato debe ser raw `EEE-PPP-NNNNNNN` sin
prefijo de tipo.

**Solución (en `addons/l10n_py_account/models/account_move.py`):**

1. **`_auto_init`**: re-crea el índice `account_move_unique_name` UNIQUE para
   incluir `l10n_latam_document_type_id`. Sin esto, la inserción de un NC con
   mismo prefix `001-001-` que un FE existente colisiona en el unique index,
   y Odoo hace save-point retry incrementando el seq a 2 en vez de 1.
2. **`_get_sequence_cache`**: scopes el bucket `precommit.data['sequence.mixin']`
   por doc_type para PY+use_documents. El cache base usa key
   `(format_string.format(seq=0), journal_id)`; como FE/NC/ND comparten formato
   `EEE-PPP-{seq:07d}`, colisionaban dentro de la misma transacción.
3. **`_get_last_sequence_domain`**: filtra por `l10n_latam_document_type_id`
   para que la búsqueda de "última secuencia usada" se limite al tipo actual.

Diagnóstico final por `voltagent-qa-sec:debugger` — el override
`_get_last_sequence_domain` solo (fix 3) era insuficiente; los 2 mechanisms
upstream (1 y 2) lo enmascaraban.

### Chart_template constraint skip en install_mode

**Problema:** El constraint `_check_py_point_of_emission` en `account.journal`
fire durante el chart template load porque Odoo crea el sale journal con
`l10n_latam_use_documents=True` antes de que el usuario configure el PoE.

**Solución:** Skip ambos constraints (`_check_py_point_of_emission`,
`_check_py_poe_requires_use_documents`) cuando `env.context.get('install_mode')`
es True. El check defensivo real está en `account.move._post` (no permite
postear sin PoE), que es donde realmente importa.

### PUC heurística receivable/payable

El script `extract_puc_rg49.py` infiere `account_type` desde nombre + prefix:

```python
if "DEUDORES" in n or "CUENTAS POR COBRAR" in n:
    return "asset_receivable"
if "PROVEEDORES" in n and code.startswith("201"):
    return "liability_payable"
```

La heurística original solo matcheaba codigos `1010103*` para receivable —
fallaba para el código real `1010301` (Deudores por Ventas).

### Tests Odoo 18 → `account.account` usa `company_ids` (M2M), no `company_id`

Discovery durante test fix. Toda búsqueda `("company_id", "=", company.id)`
sobre `account.account` debe ser `("company_ids", "in", company.id)`.

### Fixture `AccountTestInvoicingCommon` Odoo 18

El idiom correcto NO es pasar `chart_template_ref` como kwarg a `setUpClass`
(eso era Odoo 16/17). Es:

```python
class L10nPyAccountTestCase(AccountTestInvoicingCommon):
    @classmethod
    @AccountTestInvoicingCommon.setup_chart_template("py")
    def setUpClass(cls):
        super().setUpClass()
```

El decorator setea `cls.chart_template = "py"` antes de que corra
`super().setUpClass()`, donde el chart se carga sobre `cls.env.company` vía
`setup_independent_company → _create_company → _use_chart_template`.

### Bugs descubiertos durante el plan (todos fixados antes de mergear)

| #   | Lugar                     | Bug                                                | Fix                                                   |
| --- | ------------------------- | -------------------------------------------------- | ----------------------------------------------------- |
| 1   | Plan Task 21              | `raise models.UserError(...)` (typo)               | `from odoo.exceptions import UserError`               |
| 2   | Plan Task 17              | Códigos Hechauka 11-dígitos (`10103050102/3`)      | Son 9-dígitos (`101030502/3`) en RG 49/14             |
| 3   | Plan Task 10              | `chart_template_ref` kwarg a setUpClass            | No existe en Odoo 18, usar decorator                  |
| 4   | Múltiples tests           | `company_id` en `account.account`                  | Es `company_ids` Many2many                            |
| 5   | `extract_puc_rg49.py`     | Heurística receivable solo `1010103*`              | Detectar "DEUDORES" por nombre                        |
| 6   | `template_py.py`          | `code_digits=9` (paddeaba `1010101` → `001010101`) | Removido — PUC tiene longitud variable                |
| 7   | `account_move.py` `_post` | Verificaba PoE en TODOS los journals PY            | Solo sale journals (purchase tiene PoE del proveedor) |
| 8   | Infra docker              | `docker exec` no re-corre entrypoint               | Documentado en BUGS_BACKLOG #2 con comando correcto   |

## Cobertura por industria PyME

| Industria                                | Cobertura         | Notas                                                                     |
| ---------------------------------------- | ----------------- | ------------------------------------------------------------------------- |
| Comercio minorista (minimarket, almacén) | ✅ completa       | —                                                                         |
| Gastronomía                              | ✅ completa       | —                                                                         |
| Servicios profesionales                  | ✅ completa       | —                                                                         |
| Importador / distribuidor                | ⚠ activar manual | Cuentas exterior `4.06-4.08`, `1.01.04.11` Importaciones en curso         |
| Agro / ganadería                         | ⚠ activar manual | Grupos `4.02-4.05` ventas + `5.02-5.05` costos + activos biológicos       |
| Régimen Turismo / Zona Franca / Maquila  | ⚠ activar manual | Grupos `4.10`, `5.10`, cuenta `1.01.03.05.04` IVA Crédito Régimen Turismo |

## Pendientes para Fase 2 (`l10n_py_edi`)

Listados en `addons/l10n_py_account/readme/ROADMAP.rst`:

- **CDC** (Código de Control de Documento, 44 chars)
- **Firma XAdES-BES** sobre el XML del DTE
- **Cliente SOAP SIFEN** (consulta timbrado, envío DTE, eventos)
- **KuDE** (representación gráfica PDF)
- **Eventos** (inutilización, cancelación, conformidad/disconformidad,
  notificación, ajuste)
- **Auto-numbering Autofactura** con PoE propio
- **WS SET para catálogos** (actualmente carga manual de `economic_activity`)
- **Serie alfabética del timbrado** cuando se agotan 9.999.999 facturas
- **Constraint EEE-PPP coincide con PoE del journal** en `l10n_latam_document_number`
- **Comprobante de Retención** (código 8 SIFEN, "Futuro") cuando DNIT lo active

## Métricas de proceso

| Métrica                             | Valor                                                     |
| ----------------------------------- | --------------------------------------------------------- |
| Duración Fase 1b                    | 1 día (2026-05-25)                                        |
| Commits Fase 1b                     | 20 atómicos (Conventional Commits)                        |
| Líneas neto Fase 1b                 | +2 460 / −1                                               |
| Tests pre-Fase 1b → post            | 17 → 97 (+471%)                                           |
| Subagent dispatches durante Fase 1b | ≈ 18 (mayoría sonnet; opus solo para debug arquitectural) |
| Plan original (líneas)              | 3 778                                                     |
| Diff plan vs realidad               | 24 tasks intactas, 8 plan-bugs descubiertos y fixados     |

## Referencias cruzadas

- Spec original Fase 1b: [`docs/superpowers/specs/2026-05-25-l10n-py-account-design.md`](superpowers/specs/2026-05-25-l10n-py-account-design.md)
- Plan ejecutable Fase 1b: [`docs/superpowers/plans/2026-05-25-l10n-py-account.md`](superpowers/plans/2026-05-25-l10n-py-account.md)
- Roadmap general de módulos: [`docs/50_MODULES_ROADMAP.md`](50_MODULES_ROADMAP.md)
- CHANGES.rst l10n_py_base: [`addons/l10n_py_base/readme/CHANGES.rst`](../addons/l10n_py_base/readme/CHANGES.rst)
- CHANGES.rst l10n_py_account: [`addons/l10n_py_account/readme/CHANGES.rst`](../addons/l10n_py_account/readme/CHANGES.rst)
- Bugs colaterales: [`BUGS_BACKLOG.md`](../BUGS_BACKLOG.md)
- PR1: https://github.com/Ezcareaga/l10n-paraguay/pull/1
- PR2: https://github.com/Ezcareaga/l10n-paraguay/pull/2
