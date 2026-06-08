# Deployment — l10n-paraguay

**Estado:** blueprint pre-deploy (Pre-Fase 3)
**Vigencia:** Pre-Fase 3 — cuando exista deploy real, validar comandos contra entorno
**Cross-ref:** ver [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4 Backup y §6 Red
para estrategia de backup y seguridad de red (no se duplica aquí)

---

## Alcance del documento

Este documento es un **blueprint operacional** para desplegar `l10n-paraguay`
en producción. Cubre los ejes de infraestructura que un operador necesita para
levantar Odoo Community 18 con los módulos `l10n_py_*` en un VPS Linux.

Todos los snippets llevan el marker `> Note: validar en Pre-Fase 3 cuando exista
deploy real` — ninguno se ejecuta en un entorno productivo hoy. El compose de
producción se documenta como código de referencia inline; **no existe como archivo
commiteado en el repo**.

Para seguridad de red (ufw, fail2ban, SSH hardening) y estrategia de backup
completa (pg_dump + Backblaze B2 + restore mensual), ver
[`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4 y §6 — no se
duplica aquí.

---

## 1. VPS y sistema operativo

### Qué hacemos

- **VPS mínimo recomendado:** 2 vCPU, 4 GB RAM, 40 GB SSD (Hetzner CX21 ~EUR 5/mes
  o equivalente). Para producción con volumen medio: 4 vCPU / 8 GB RAM / 80 GB.
- **OS:** Ubuntu 22.04 LTS (Jammy) o Debian 12 (Bookworm) — base soportada por
  el stack Odoo 18 + Docker Engine.
- **Puertos expuestos:** 80 (HTTP → redirect HTTPS), 443 (HTTPS via Caddy),
  22 (SSH restringido por IP). Postgres (5432) NO se expone al exterior.
- **Docker Engine 24+** y Docker Compose v2 instalados en el host.

### Por qué

Odoo 18 Community requiere Python 3.10+ y PostgreSQL 12+ (la imagen oficial
usa PostgreSQL 15 internamente). Docker simplifica el setup y los upgrades.
El VPS mínimo de 4 GB RAM evita OOM killer en instancias con 10-50 usuarios
concurrentes (audiencia PyME objetivo).

### Comandos ilustrativos

```bash
# Instalar Docker Engine en Ubuntu 22.04:
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Verificar versiones:
docker --version        # >= 24.x
docker compose version  # >= 2.x
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

---

## 2. docker-compose de producción (referencia)

El siguiente bloque es **ilustrativo**. No existe como archivo commiteado en el
repo — se configura directamente en el VPS al provisionar. El compose de
desarrollo (`infra/docker-compose.yml`) es para uso local únicamente.

```yaml
# docker-compose.prod.yml (código de referencia — no commiteado)
# Ajustar $VAR a valores reales en el VPS antes de ejecutar.

services:
  postgres:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_USER: $ODOO_DB_USER
      POSTGRES_PASSWORD: $ODOO_DB_PASSWORD
      POSTGRES_DB: $ODOO_DB_NAME
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - /var/backups/odoo:/var/backups/odoo
    # NO exponer port 5432 al host — solo acceso interno

  odoo:
    image: odoo:18.0
    restart: unless-stopped
    depends_on:
      - postgres
    environment:
      HOST: postgres
      USER: $ODOO_DB_USER
      PASSWORD: $ODOO_DB_PASSWORD
    volumes:
      - odoo_data:/var/lib/odoo
      - /opt/l10n-paraguay/addons:/mnt/extra-addons:ro
    command: >
      odoo
      --addons-path=/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons
      --db_host=postgres
      --db_user=$ODOO_DB_USER
      --db_password=$ODOO_DB_PASSWORD
      --workers=2
      --max-cron-threads=1
      --proxy-mode
    ports:
      - "127.0.0.1:8069:8069"
    # Escuchar solo en loopback — Caddy hace el proxy externo

volumes:
  postgres_data:
  odoo_data:
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

**Variables de entorno requeridas** (definir en `.env` del VPS, nunca commitear):

| Variable            | Descripción                                              |
| ------------------- | -------------------------------------------------------- |
| `$ODOO_DB_USER`     | Usuario PostgreSQL de Odoo                               |
| `$ODOO_DB_PASSWORD` | Password PostgreSQL (generar con `openssl rand -hex 32`) |
| `$ODOO_DB_NAME`     | Nombre de la base de datos productiva                    |

---

## 3. Caddy reverse proxy con SSL automático

### Qué hacemos

- **Caddy** como reverse proxy frente a Odoo en `127.0.0.1:8069`.
- **SSL automático** vía Let's Encrypt (HTTP-01 challenge) — sin gestionar
  certificados manualmente.
- **Headers de seguridad:** HSTS, `X-Frame-Options`, `X-Content-Type-Options`,
  `Referrer-Policy`.
- Dominio configurado con placeholder `tu-dominio.com.py` — reemplazar con el
  dominio real al provisionar.

### Por qué

Caddy elimina la complejidad de renovación manual de certificados (nginx requiere
certbot + cron). El flag `--proxy-mode` en Odoo es obligatorio cuando hay un
reverse proxy (Odoo necesita el IP real del cliente desde `X-Forwarded-For`).

### Caddyfile ilustrativo

```caddyfile
# /etc/caddy/Caddyfile
# Reemplazar tu-dominio.com.py con el dominio real en Pre-Fase 3.

tu-dominio.com.py {
    reverse_proxy 127.0.0.1:8069 {
        header_up X-Forwarded-Proto {scheme}
        header_up X-Real-IP {remote_host}
    }

    header {
        Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
        X-Frame-Options "SAMEORIGIN"
        X-Content-Type-Options "nosniff"
        Referrer-Policy "strict-origin-when-cross-origin"
        -Server
    }

    log {
        output file /var/log/caddy/odoo-access.log
    }
}

# Redirect www a apex (opcional):
www.tu-dominio.com.py {
    redir https://tu-dominio.com.py{uri} permanent
}
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

---

## 4. Backup automatizado

### Qué hacemos

`pg_dump` diario + sync a Backblaze B2 offsite + test de restauración mensual.
El detalle completo de la estrategia (opciones de cifrado, retención, endpoints
alternativos, trade-offs) está documentado en
[`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4 Backup — no se
duplica aquí.

### Comandos ilustrativos (resumen)

```bash
# Backup diario (cron 02:00 AM):
pg_dump -U $ODOO_DB_USER $ODOO_DB_NAME | xz -T0 \
  > /var/backups/odoo/odoo-$(date +%F).sql.xz

# Sync offsite a Backblaze B2:
rclone sync /var/backups/odoo/ b2:$B2_BUCKET_NAME/odoo/ --transfers 4

# Retención local: 7 días
find /var/backups/odoo/ -name 'odoo-*.sql.xz' -mtime +7 -delete
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

Ver estrategia completa → [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4 Backup.

Script de restore test mensual → [`scripts/restore-smoke.sh`](../scripts/restore-smoke.sh).

---

## 5. Health checks

### Qué hacemos

- **Odoo health endpoint:** `GET http://127.0.0.1:8069/web/health` devuelve
  `{"status": "pass"}` cuando la instancia está lista.
- **Postgres liveness:** `pg_isready -U $ODOO_DB_USER -d $ODOO_DB_NAME`.
- **Cron de monitoreo:** verificar que el cron interno de Odoo esté corriendo
  (consulta `ir.cron` activos) — relevante para la cola EDI en Fase 2.

### Comandos ilustrativos

```bash
# Health check HTTP de Odoo (desde el VPS):
curl -sf http://127.0.0.1:8069/web/health | python3 -m json.tool
# Esperado: {"status": "pass"}

# Liveness de Postgres:
pg_isready -h localhost -U $ODOO_DB_USER -d $ODOO_DB_NAME
# Esperado: "accepting connections"

# Verificar workers Odoo (long-polling + cron):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml \
  exec odoo ps aux | grep odoo
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

---

## 6. Procedimiento de actualización (module upgrade)

### Qué hacemos

Actualizar un módulo `l10n_py_*` en producción requiere:

1. Hacer backup previo (§4).
2. Pull de la nueva versión del código en `/opt/l10n-paraguay/addons/`.
3. Reiniciar Odoo con flag `-u <module>` para correr migraciones ORM.
4. Verificar logs + health check (§5).
5. Si algo falla: rollback (ver runbook [`docs/72_RUNBOOK.md`](72_RUNBOOK.md) Incidente 9).

### Comandos ilustrativos

```bash
# 1. Backup previo (OBLIGATORIO antes de todo upgrade):
pg_dump -U $ODOO_DB_USER $ODOO_DB_NAME | xz -T0 \
  > /var/backups/odoo/pre-upgrade-$(date +%F-%H%M).sql.xz

# 2. Actualizar código:
cd /opt/l10n-paraguay
git pull origin main

# 3. Upgrade del módulo (ejemplo: l10n_py_account):
docker compose -f docker-compose.prod.yml run --rm odoo \
  odoo --stop-after-init -d $ODOO_DB_NAME -u l10n_py_account

# 4. Reiniciar servicio:
docker compose -f docker-compose.prod.yml restart odoo

# 5. Verificar:
curl -sf http://127.0.0.1:8069/web/health
docker compose -f docker-compose.prod.yml logs odoo | tail -50
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

---

## Cross-references

- Seguridad de red y backup completo: [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md)
- Compliance datos personales (Ley 7593/2025): [`docs/61_COMPLIANCE_LEY_7593.md`](61_COMPLIANCE_LEY_7593.md)
- Runbook de incidentes (incluyendo rollback): [`docs/72_RUNBOOK.md`](72_RUNBOOK.md)
- Script restore test mensual: [`scripts/restore-smoke.sh`](../scripts/restore-smoke.sh)

---

_Documento creado en Phase 3 Pre-Fase 2 (Bloque C Documentación operacional).
Próxima revisión: Pre-Fase 3 cuando se provisione el VPS real — validar cada
snippet contra el entorno y reemplazar todos los placeholders (`tu-dominio.com.py`,
`$VAR`) con valores reales._
