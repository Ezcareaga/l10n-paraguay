# Bugs / mejoras pendientes (no bloqueantes)

Bugs colaterales detectados durante el trabajo en otras tareas. Cada entrada
incluye: descripción, dónde se detectó, impacto, y solución sugerida.

## #1 — `infra/docker-compose.yml` montaba todo el repo (RESUELTO 2026-05-22)

**Detectado:** 2026-05-22, sesión de verificación Docker post-reinstalación WSL.
**Resuelto:** 2026-05-22, mismo día.

**Síntoma original:** Odoo 18 tardaba ~140s desde "Watching addons folder"
hasta arrancar el HTTP server. Causa: el compose montaba `..:/mnt/extra-addons/l10n-paraguay`
(el repo entero), por lo que Odoo escaneaba recursivamente `references/odoo-18.0/`
(151 MB), `references/l10n-brazil/` (32 MB) y otros buscando `__manifest__.py`.

**Riesgo adicional:** si algún manifest dentro de `references/` se llegara a
cargar como módulo de cliente, podría haber roto el setup o cargado modelos
de otra localización.

**Solución aplicada (opción A):** se creó `addons/` en el root del repo y
el compose ahora monta solo esa carpeta:

```yaml
volumes:
  - ../addons:/mnt/extra-addons/l10n-paraguay
```

Los futuros `l10n_py_base/`, `l10n_py_account/`, etc. van dentro de `addons/`.

**Verificación:** boot pasó de ~140s a **4s** (35× más rápido). Odoo ahora
loggea correctamente "Registry loaded in 1.4s" — antes ni alcanzaba esa fase.

## #2 — `docker exec` para correr tests salta el entrypoint de Odoo (RESUELTO 2026-05-25)

**Detectado:** 2026-05-25 durante Fase 1b Task 2 al intentar correr tests
desde un subagente con `docker compose exec odoo odoo -u l10n_py_base ...`.

**Síntoma:** `psycopg2.OperationalError: connection to server on socket
"/var/run/postgresql/.s.PGSQL.5432" failed: No such file or directory`.
También se ve `Address already in use Port 8069`.

**Causa:** el `entrypoint.sh` de la imagen `odoo:18.0` lee las env vars
`HOST=postgres`, `USER=odoo`, `PASSWORD=odoo` (declaradas en
`docker-compose.yml`) e inyecta `--db_host`/`--db_user`/`--db_password` al
proceso Odoo que arranca como PID 1. Cuando uno hace `docker exec ... odoo`
para correr otra instancia (tests, scripts), **el entrypoint NO corre
otra vez** — solo se ejecuta el binario `odoo` directo, sin las flags de
conexión a DB. Además, el daemon principal ya tiene tomado el puerto 8069.

**Comando correcto para correr tests** (con flags explícitos):

```bash
docker exec l10n_py_odoo bash -c "odoo -u <modulo> -d l10n_py_dev \
  --db_host=postgres --db_user=odoo --db_password=odoo \
  --stop-after-init --test-tags l10n_py --test-enable \
  --http-port=8088 \
  --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/var/lib/odoo/addons/18.0,/mnt/extra-addons,/mnt/extra-addons/l10n-paraguay"
```

Las flags clave son `--db_host=postgres --db_user=odoo --db_password=odoo`
(suplen el entrypoint) y `--http-port=8088` (libera el 8069 del daemon
principal). `--addons-path` también hay que pasarlo explícito porque el
`odoo.conf` interno solo declara `/mnt/extra-addons`, no
`/mnt/extra-addons/l10n-paraguay`.

**TODO opcional:** crear wrapper `bin/odoo-test.ps1`/`bin/odoo-test.sh`
que encapsule este comando con un módulo como argumento. No es bloqueante;
documentar acá basta para que futuros subagentes lo conozcan.

## TD-004 — XML data files use deprecated `<data noupdate="1">` wrapper (RESUELTO)

**Detectado:** 2026-05-27 durante Fase 1 P1-C (semantic baseline pre-commit run).
**Resuelto:** 2026-05-28, PR fix/td-004-xml-regen.
**Severidad:** baja (sin impacto en runtime — Odoo 18 sigue cargando el XML; es
solo deprecation warning del hook `oca-checks-odoo-module`).

**Síntoma:** 7 archivos XML del set `addons/l10n_py_*/` usan el wrapper legacy
`<odoo><data noupdate="1">...</data></odoo>`. Odoo 18 prefiere el formato
moderno `<odoo noupdate="1">...</odoo>` (colapsar `<data>` en el elemento
raíz). `oca-checks-odoo-module` v0.0.33 marca `xml-deprecated-data-node` en cada
uno.

Archivos afectados:

- `addons/l10n_py_account/security/l10n_py_account_security.xml`
- `addons/l10n_py_base/data/l10n_latam_identification_type_data.xml`
- `addons/l10n_py_base/data/l10n_py_economic_activity_demo.xml`
- `addons/l10n_py_base/data/l10n_py_recipient_nature_data.xml`
- `addons/l10n_py_base/data/l10n_py_regime_data.xml`
- `addons/l10n_py_base/data/l10n_py_taxpayer_type_data.xml`
- `addons/l10n_py_base/data/res_country_state_data.xml`

**Estado actual:** los 7 archivos están excluidos del hook
`oca-checks-odoo-module` en `.pre-commit-config.yaml` (bloque `exclude:` con
comentario apuntando acá). `pre-commit run --all-files` exit 0 sobre `main`
con esta exclusión documentada.

**Solución:** 6 de los 7 son auto-generados por
`scripts/generate_module_data.py` — cambiar el template Jinja (cerca de
la línea 44, `<odoo><data noupdate="1">` → `<odoo noupdate="1">`) y
regenerar.
El 7° (`l10n_py_account_security.xml`) es hand-edited, requiere un edit
manual. Después de regenerar: correr D-07 (97 tests) para confirmar que el
parser de Odoo sigue contento con el formato nuevo, y remover el bloque
`exclude:` del hook.

**Owner:** Phase 2 (`l10n_py_edi`) prep o un mini-plan dedicado dentro del
milestone Pre-Fase 2 — lo primero que llegue.

**Refs:**

- `.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/p1c-review.md`
- `.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/01-RESEARCH.md` (R-01)
- `.pre-commit-config.yaml` (bloque `oca-checks-odoo-module: args:`)

## TD-005 — Flake8/bugbear opinionated checks suprimidos (RESUELTO)

**Detectado:** 2026-05-27 durante Fase 1 P1-C cuando se bumpeó flake8
3.9.2 → 7.1.1 y flake8-bugbear 21.9.2 → 24.10.31.
**Resuelto:** 2026-05-28, PR fix/td-005-bugbear (B017/B907/B950 reparados;
`.flake8` con `B9` restaurado en `select` y `B017`/`B907` removidos de
`ignore`).
**Severidad:** baja (refactor cosmético, sin impacto runtime).

**Síntoma:** flake8-bugbear v24 introduce checks opinionados que el código
existente no satisface. Tres checks suprimidos en `.flake8` (`ignore =
...B017,B907` + remoción de `B9` del `select`):

- **B017** — `assertRaises(Exception)` muy genérico en
  `addons/l10n_py_account/tests/test_point_of_emission.py:31` y
  `test_timbrado.py:54`. Fix: usar la excepción concreta
  (`UserError`/`ValidationError` de `odoo.exceptions`) según el caso.
- **B907** — comillas manuales reemplazables por `!r`:
  `scripts/codegraph_cli.py:59`, `scripts/extract_pdf.py:34`,
  `scripts/generate_module_data.py:67-75` (7 hits). Fix: convertir
  `f'"{x}"'` → `f'{x!r}'`.
- **B950** — líneas > 88+10% (= 97 chars):
  `addons/l10n_py_account/models/account_journal.py:46,58`,
  `account_move.py:36`, `template_py.py:22`,
  `addons/l10n_py_base/models/res_company.py:26`. Fix: split en multilínea
  o usar paréntesis implícitos. Ya cumplen el cap soft de 88 char vía
  black (que no rompe esas líneas porque son strings o comentarios).

**Estado actual:** `.flake8` suprime los tres checks con comentario que
apunta acá. flake8 corre clean sobre `main`.

**Owner:** plan de refactor cosmético al final de Pre-Fase 2 (cuando todo
el código del milestone esté congelado) o como parte del code review pre-PR
OCA, lo primero que llegue.

**Refs:** `.flake8` (`ignore =`/`select =`),
`.planning/phases/01-bloque-a-foundation-t-cnica-ci-cd-pre-commit/p1c-precommit-final-run.log`

## TD-006 — Negative-path constraint tests dejan `ERROR odoo.sql_db` en log (RESUELTO)

**Detectado:** 2026-05-28 durante Fase 1 P1-E PR #4 cuando `oca_checklog_odoo`
falló el job a pesar de que los 97 tests pasaron verdes.
**Resuelto:** 2026-05-28, PR #XX (TD-006 + TD-007 combinado).
**Severidad:** baja (no afecta producción; solo CI noise).

**Síntoma:** Dos tests negativos disparan SQL unique-constraint violations
que Postgres loggea en `odoo.sql_db` a nivel ERROR ANTES de que
`assertRaises` los capture en el test:

- `addons/l10n_py_account/tests/test_point_of_emission.py` — constraint
  `l10n_py_point_of_emission_estab_point_uniq`.
- `addons/l10n_py_account/tests/test_timbrado.py` — constraint
  `l10n_py_timbrado_name_uniq`.

`checklog-odoo` (consumido por `oca_checklog_odoo` con
`OCA_ENABLE_CHECKLOG_ODOO=1`) interpreta las líneas ERROR como falla
de CI aunque los tests pasaron.

**Mitigación actual:** `checklog-odoo.cfg` (raíz del repo) ignora la
regex `ERROR.*odoo\.sql_db.*duplicate key value violates unique constraint`.
CI verde con tests verdes.

**Fix proper:** envolver los dos test methods en
`with tools.mute_logger('odoo.sql_db'):` para que el ERROR no llegue al
appender raíz. Patrón estándar Odoo para `assertRaises` con SQL constraints.

**Owner:** mini-plan dentro de Pre-Fase 2 cuando haya bandwidth, o
parte del code review pre-PR OCA. Estimado: 10 min.

**Refs:** `checklog-odoo.cfg`, PR #4 commit `409d284`,
GitHub Actions run `26575788271`.

## TD-007 — `_post_init_hook` translate warnings con traceback (RESUELTO)

**Detectado:** 2026-05-28 durante Fase 1 P1-E PR #4, misma corrida que TD-006.
**Resuelto:** 2026-05-28, PR #XX (TD-006 + TD-007 combinado).
**Severidad:** baja (warnings, no errores; solo CI noise).

**Síntoma:** `addons/l10n_py_account/hooks.py:39-40` llama `_("...")` dentro
del `_post_init_hook` sin request context activo. Odoo emite WARNING con
traceback multilínea que `checklog-odoo` interpreta como noise.

**Mitigación actual:** `checklog-odoo.cfg` ignora `WARNING.*_post_init_hook`
y `WARNING.*translation.*context`.

**Fix proper:** una de dos opciones:

1. Reemplazar `_("...")` por `lazy_gettext("...")` (mantiene traducción
   diferida hasta que haya context).
2. Skip la traducción cuando `request` no esté disponible:
   ```python
   from odoo.http import request
   message = _("...") if request else "..."
   ```

**Owner:** mini-plan dentro de Pre-Fase 2, junto con TD-006.

**Refs:** `addons/l10n_py_account/hooks.py:39-40`, `checklog-odoo.cfg`,
PR #4 commit `409d284`, GitHub Actions run `26575788271`.

## test_modulo11.py sin @tagged("l10n_py") — probablemente excluido del CI (RESUELTO)

- **Detectado:** 2026-06-10, planning PR-1 l10n_py_edi.
- **Resuelto:** 2026-06-11 en PR #30 — BaseCase + tagged("standard", "l10n_py").
- **Síntoma:** `addons/l10n_py_base/tests/test_modulo11.py` define
  `TestModulo11(unittest.TestCase)` sin decorator `@tagged`. Con
  `ODOO_TEST_TAGS="l10n_py"` en CI, el filtro selecciona solo tests con tag
  `l10n_py`, así que esta suite no corre en CI (sí corre localmente sin filtro).
- **Fix aplicado:** herencia cambiada de `unittest.TestCase` a `odoo.tests.BaseCase`
  (el runner Odoo 18 requiere la metaclase de BaseCase para inyectar `test_module`);
  decorator `@tagged("standard", "l10n_py")` agregado; imports actualizados a
  `from odoo.tests import BaseCase, tagged` (eliminado `import unittest`).
- **Prioridad:** media — el algoritmo está cubierto indirectamente por
  test_ruc_validation, pero la suite directa quedó invisible.

## TD-008 — Hardening del generador CDC (diferido de PR-2)

**Detectado:** 2026-06-15 en code review de PR-2 (generador CDC, `l10n_py_edi`).
**Severidad:** baja (ninguno bloquea el MVP; el CDC se genera correcto y
validado contra el ejemplo oficial del Manual v150).

Ítems acordados como backlog para PRs posteriores de la Fase 2 (sobre todo el
PR del XML builder del DE, que comparte la fecha de emisión con el CDC):

1. **Helper compartido de fecha de emisión.** `account_move.py`
   `_l10n_py_edi_cdc_components()` usa `issue_date = self.invoice_date or
self.date` para la posición 26-33 del CDC. Esa fecha **debe** ser
   byte-idéntica al campo `dFeEmiDE` del XML del DE. Cuando se escriba el XML
   builder, extraer un único `_l10n_py_edi_issue_date()` (devolviendo `date`)
   que consuman tanto el CDC como el XML, para que no puedan divergir. Por
   ahora hay un comentario en el modelo señalando el acoplamiento.
2. **Retry/mensaje amigable ante colisión de security code.** Dos posteos
   concurrentes que saquen el mismo código de 9 dígitos (`secrets`, ~1e-9) y
   compartan el resto de componentes disparan un `psycopg2 UniqueViolation`
   crudo en vez de un `UserError` traducible. Agregar un regenerate-and-retry
   single-shot o envolver el error.
3. **Validación de largo de RUC con mensaje accionable.** Un cuerpo de RUC > 8
   dígitos cae en el `CdcError` genérico (`_digits(ruc, 8, ...)`). Validar el
   largo en `_l10n_py_edi_cdc_components()` con un mensaje específico de
   configuración, como los otros prerequisitos.
4. **DRY del doble parse de RUC.** `_l10n_py_edi_cdc_components()` llama
   `split_ruc(vat)` y después `validate_ruc(vat)` (que vuelve a hacer
   `split_ruc` + recomputa el DV). Validar una sola vez con los valores ya
   separados (`calculate_dv(ruc, basemax=11) == ruc_dv`).
5. **Tests faltantes:** camino de contingencia end-to-end
   (`l10n_py_emission_type == "2"` → posición 34 del CDC en un move posteado)
   y rechazo por largo de RUC > 8 en el modelo.
6. **Fixture `L10nPyEdiTestCase` propia.** En PR-2 se agregó `vat` +
   `taxpayer_type` a la fixture base `L10nPyAccountTestCase`
   (`addons/l10n_py_account/tests/common.py`) porque los tests de CDC heredan
   directamente de ella y `_post()` exige RUC válido. Cuando aparezca una
   fixture `L10nPyEdiTestCase` (probablemente en el PR del XML builder), mover
   ahí esos datos para no acoplar la fixture de account al comportamiento de
   edi.
7. **Nota de migración del cambio de comportamiento de `modulo11`.** El fix
   18.0.1.1.1 (resto==1 → DV 0) rechaza RUCs con DV=1 sobre cuerpos de
   resto==1 que antes se aceptaban. No hay script de migración porque el
   módulo aún no tiene despliegues en producción; si llega a haber clientes
   antes de estabilizar, agregar un `migrations/` `end-` que re-valide los
   `res.partner.vat` existentes y avise de los que queden inválidos.

**Owner:** PR del XML builder del DE (ítems 1 y 6 son co-requisitos de ese PR)

- mini-hardening cuando haya bandwidth (ítems 2-5, 7).

**Refs:** code review PR-2 (commit `1c02923`),
`addons/l10n_py_edi/models/account_move.py`,
`addons/l10n_py_edi/services/cdc.py`.

## TD-009 — `dDesAfecIVA` no matchea el enum del XSD SIFEN (4 de 5 valores)

**Detectado:** 2026-06-17 durante PR-4a (spike XAdES), al re-habilitar la
validación XSD del DE tras corregir `_xsd_dir()` (ver TD-011).
**Severidad:** **alta** — SIFEN rechazaría toda FE con ítem gravado (el caso común).

**Síntoma:** validando el `<DE>` generado contra `DE_Types_v150.xsd` (vía
wrapper-schema por tipo), `dDesAfecIVA="Gravado IVA 10%"` falla el facet
`enumeration`. El enum oficial (`DE_Types_v150.xsd` líneas 1328-1335) es:
`{"Gravado IVA", "Exonerado (Art. 83- Ley 125/91)", "Exento", "Gravado parcial (Grav- Exento)"}`.

**Origen:** `addons/l10n_py_edi/services/xml_constants.py:146-152`
(`IVA_AFEC_DESC`). 4 de 5 valores son incorrectos:

- `IVA_GRAVADO_10: "Gravado IVA 10%"` → debe ser `"Gravado IVA"` (la tasa va en `dTasaIVA`)
- `IVA_GRAVADO_5: "Gravado IVA 5%"` → debe ser `"Gravado IVA"`
- `IVA_EXONERADO: "Exonerado"` → debe ser `"Exonerado (Art. 83- Ley 125/91)"`
- `IVA_GRAVADO_PARCIAL: "Gravado parcial"` → debe ser `"Gravado parcial (Grav- Exento)"`
- `IVA_EXENTO: "Exento"` → ✓ correcto

**Fix:** alinear `IVA_AFEC_DESC` al enum del XSD. Verificar también la
correspondencia código `iAfecIVA` ↔ descripción contra el Manual Técnico v150
(el módulo usa 5 códigos; el XSD `tiAfecIVA` arranca en "1").

**Owner:** PR dedicado "xml_builder XSD compliance + validator rewrite"
(junto con TD-010 y TD-011).

**Refs:** `xml_constants.py:146-152`, `DE_Types_v150.xsd:1305-1335`,
`docs/research/xades_sifen.md` §"Hallazgo de spike".

## TD-010 — `dDesDepEmi` case mismatch ("Central" → "CENTRAL")

**Detectado:** 2026-06-17 durante PR-4a, misma corrida que TD-009.
**Severidad:** media — SIFEN rechaza departamentos cuyo nombre no matchee el
enum exacto (MAYÚSCULAS).

**Síntoma:** `dDesDepEmi="Central"` falla el facet `enumeration` del XSD; el
set oficial está en MAYÚSCULAS (`..., "CENTRAL", ...`).

**Origen:** `addons/l10n_py_edi/services/xml_builder.py:324` — pass-through
directo de `issuer["department_desc"]`. El builder confía en que el caller
provea el nombre canónico en vez de derivarlo del código `cDepEmi`.

**Fix:** derivar `dDesDepEmi` del código `cDepEmi` vía una tabla canónica de
departamentos (SIFEN los enumera en `Departamentos_v141.xsd`), haciendo el
campo a prueba del caller. Alternativa mínima: corregir el fixture y validar
el contrato.

**Owner:** PR dedicado "xml_builder XSD compliance + validator rewrite".

**Refs:** `xml_builder.py:323-324`, `Departamentos_v141.xsd`.

## TD-011 — `validate_against_xsd` necesita wrapper-schema (XSDs declaran tipos, no globals)

**Detectado:** 2026-06-17 durante PR-4a, al corregir `_xsd_dir()`
(`parents[4]→parents[3]`) y re-habilitar la validación.
**Severidad:** media — la validación XSD del DE no funciona como está escrita;
el test la enmascaraba con un skip silencioso.

**Síntoma:** `lxml.etree.XMLSchema.validate(<DE>)` contra `DE_v150.xsd` falla
con `SCHEMAV_CVC_ELT_1: ... 'DE': No matching global declaration available for
the validation root`. Inspección de los 9 XSD: **ninguno declara elementos
globales** — son bibliotecas de tipos (`tDE`, `tiAfecIVA`, …) + includes. Solo
`xmldsig-core-schema.xsd` (W3C) tiene globals. lxml exige que la raíz a validar
matchee una declaración de elemento global; no existe `DE` ni `rDE` global.

**Causa de raíz del skip silencioso:** `_xsd_dir()` usaba `parents[4]`
(sobrepasaba la raíz del repo) → `FileNotFoundError` → `test_fe_simple_xsd_valid`
lo capturaba como `SkipTest("XSD files are unavailable")`. El skip era engañoso:
los XSD SÍ están en el repo. `parents[4]→parents[3]` ya está corregido en PR-4a;
el test quedó con `@unittest.skip` honesto apuntando a este TD.

**Fix:** reescribir `validate_against_xsd` con la técnica wrapper-schema:
generar un schema que `include` el XSD de tipos y declare un elemento global
del tipo a validar (`<xs:element name="DE" type="sifen:tDE"/>`), luego validar.
Probado funcionando en el spike (ancla y valida el subárbol DE completo — fue
así que se detectaron TD-009 y TD-010).

**Owner:** PR dedicado "xml_builder XSD compliance + validator rewrite".
Re-habilita `test_fe_simple_xsd_valid` (sin skip) y resuelve TD-009/TD-010.

**Refs:** `addons/l10n_py_edi/services/xsd_validator.py`,
`addons/l10n_py_edi/tests/test_xml_builder.py:257`,
`docs/research/xades_sifen.md` §"Hallazgo de spike".

## TD-012 — `test_fe_simple_golden_file` skipea silenciosamente (auto-crea golden y salta)

**Detectado:** 2026-06-17 durante PR-4a, al correr la suite con la validación
XSD activa.
**Severidad:** baja — el test no asegura nada en CI.

**Síntoma:** `test_fe_simple_golden_file` escribe el golden
`tests/xml_fixtures/fe_simple.xml` la primera vez que corre y hace
`skipped: Golden file creado: ...`. El fixture no está commiteado, así que en
CI (checkout limpio) **siempre** crea-y-skipea — nunca compara contra un golden.

**Fix:** commitear un golden válido y que el test compare (falle ante drift),
o convertir el patrón a aserción directa. Co-requisito: el golden debe
generarse desde un DE válido (post TD-009/TD-010), por eso va en el mismo PR
dedicado.

**Owner:** PR dedicado "xml_builder XSD compliance + validator rewrite".

**Refs:** `addons/l10n_py_edi/tests/test_xml_builder.py`
(`test_fe_simple_golden_file`).
