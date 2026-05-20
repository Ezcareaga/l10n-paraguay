# `infra/` — Stack local de desarrollo

Contenedores Docker para correr Odoo 18 Community + PostgreSQL 16 contra los
módulos `l10n_py_*` de este repo.

## Pre-requisitos (Windows)

1. **Docker Desktop** con backend WSL2
   ```bash
   winget install Docker.DockerDesktop
   ```
   Después de instalar, abrir Docker Desktop y dejar que termine la inicialización.

2. **Compartir la unidad C:** con Docker (Settings → Resources → File Sharing).
   Necesario para que el mount `..:/mnt/extra-addons/l10n-paraguay` funcione.

3. **WSL2** habilitado (Docker Desktop suele instalarlo solo).

## Comandos típicos

Desde el **repo root** (no desde `infra/`):

```bash
# Levantar stack en background
docker compose -f infra/docker-compose.yml up -d

# Ver logs Odoo en vivo
docker compose -f infra/docker-compose.yml logs -f odoo

# Shell dentro del contenedor Odoo (para debug)
docker compose -f infra/docker-compose.yml exec odoo bash

# Re-instalar un módulo después de cambios en data/views
docker compose -f infra/docker-compose.yml exec odoo \
  odoo -d l10n_py_dev -u l10n_py_base --stop-after-init

# Bajar stack pero PRESERVAR volúmenes (DB intacta)
docker compose -f infra/docker-compose.yml down

# RESET TOTAL (borra DB y filestore)
docker compose -f infra/docker-compose.yml down -v
```

## Primera vez

1. `docker compose -f infra/docker-compose.yml up -d`
2. Esperar ~30s a que Odoo termine de inicializar (`docker compose ... logs odoo`)
3. Abrir http://localhost:8069 en el navegador
4. Crear database:
   - **Master Password:** `admin` (cambiar después en producción)
   - **Database Name:** `l10n_py_dev`
   - **Email:** `admin@example.com`
   - **Password:** `admin`
   - **Phone:** —
   - **Language:** Spanish / Español (Paraguay)
   - **Country:** Paraguay
   - **Demo data:** **NO** (queremos base limpia para testing)
5. Una vez creada, Apps → buscar `l10n_py_base` (cuando exista) → Install

## Puertos

| Servicio | Container | Host | Notas |
|---|---|---|---|
| Postgres | 5432 | 5433 | Cambiado del default para no chocar con postgres del host |
| Odoo HTTP | 8069 | 8069 | UI principal |
| Odoo longpolling | 8072 | 8072 | Para chatter, notificaciones |

## Conectarse a la DB desde el host

```bash
# psql via Docker (recomendado — no requiere postgres-client local)
docker compose -f infra/docker-compose.yml exec postgres psql -U odoo -d l10n_py_dev

# psql desde host (si tenés psql instalado) — usar puerto 5433
psql -h localhost -p 5433 -U odoo -d l10n_py_dev
```

## Troubleshooting

- **"Cannot connect to the Docker daemon"** → Abrir Docker Desktop, esperar a que
  termine el splash y reintentar.
- **"port is already allocated"** → Alguien ya está usando 8069 o 5433. Cambiar
  en `docker-compose.yml` o detener el otro proceso.
- **"Mounts denied"** → Compartir unidad C: en Docker Desktop Settings.
- **Cambios en código no se reflejan** → `--dev=all` debería autorecargar Python.
  Para XML/views, reiniciar el contenedor o re-instalar el módulo con `-u`.
