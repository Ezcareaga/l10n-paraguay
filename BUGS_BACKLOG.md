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

## TD-005 — Flake8/bugbear opinionated checks suprimidos (ABIERTO)

**Detectado:** 2026-05-27 durante Fase 1 P1-C cuando se bumpeó flake8
3.9.2 → 7.1.1 y flake8-bugbear 21.9.2 → 24.10.31.
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
