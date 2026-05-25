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
