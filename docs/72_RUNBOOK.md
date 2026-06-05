# Runbook operacional — l10n-paraguay

**Estado:** baseline operacional (Pre-Fase 3)
**Vigencia:** incidentes SIFEN-dependientes se validan en Fase 2 EDI / homologación
**Cross-ref:** [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md),
[`docs/71_DEPLOYMENT.md`](71_DEPLOYMENT.md)

---

## Alcance del documento

Este runbook cubre los 10 incidentes más probables en la operación de
`l10n-paraguay` en producción. Cada incidente sigue el template fijo:
**Síntoma / Severidad / Diagnóstico / Resolución / Prevención**.

Los incidentes 1, 4, 5, 7 y 10 dependen de `l10n_py_edi` (Fase 2 EDI) y
llevan el marker correspondiente. Los comandos de diagnóstico en esos casos
son genéricos — **no se inventan códigos de error SIFEN específicos** que no
han sido verificados contra el entorno de homologación.

Los incidentes 6, 7 y 10 incorporan conocimiento operacional heredado del
sistema ÑandeFact (operación real con vendedoras de mercado en Paraguay).

---

## Incidentes

### Incidente 1: SIFEN timeout

**Síntoma:** Los DTEs quedan en estado `to_send` indefinidamente; los logs
de Odoo muestran errores de conexión o timeout al intentar enviar a SIFEN.

**Severidad:** Alta — la facturación electrónica está interrumpida. El plazo
legal de 72h para transmitir un DTE aprobado empieza a correr.

**Diagnóstico:**

```bash
# Verificar conectividad con el endpoint SIFEN (genérico — URL real en Fase 2):
curl -sv --max-time 10 https://sifen.set.gov.py/ 2>&1 | grep -E "Connected|timeout|SSL"

# Revisar logs de Odoo por errores de conexión:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml logs odoo \
  | grep -i "sifen\|timeout\|connection refused\|SOAP" | tail -30

# Verificar DNS desde el VPS:
nslookup sifen.set.gov.py

# Verificar estado de DTEs pendientes (Odoo shell — Fase 2):
# SELECT id, name, edi_state FROM account_move WHERE edi_state = 'to_send';
```

> Note: procedimiento se valida en Fase 2 EDI / homologación.

**Resolución:**

1. Verificar que el VPS tiene conectividad a internet: `curl -sf https://ifconfig.me`.
2. Verificar que el puerto 443 saliente no está bloqueado por ufw: `sudo ufw status`.
3. Consultar el panel de estado de SIFEN/DNIT (si existe) o el canal de avisos SET.
4. Si el timeout es transitorio (mantenimiento SIFEN): esperar y reencolar desde
   la UI de Odoo (Fase 2 — botón "Reintentar").
5. Si persiste: escalar a N2 (ver §Escalation path).

**Prevención:** Configurar alertas de monitoreo para el health check de Odoo
(`/web/health`) y para DTEs en `to_send` por más de 1 hora.

---

### Incidente 2: Postgres disk full

**Síntoma:** Odoo devuelve errores 500 o "could not write to file" en los
logs. `df -h` muestra disco al 100% en el volumen de datos.

**Severidad:** Alta — la instancia puede quedar en modo solo lectura o caerse
completamente.

**Diagnóstico:**

```bash
# Ver uso de disco:
df -h

# Ver los directorios más grandes:
du -sh /var/lib/docker/volumes/* 2>/dev/null | sort -rh | head -10

# Ver tamaño de la base de datos Odoo en Postgres:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT pg_size_pretty(pg_database_size('$ODOO_DB_NAME'));"

# Ver tablas más grandes:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
      FROM pg_catalog.pg_statio_user_tables
      ORDER BY pg_total_relation_size(relid) DESC LIMIT 10;"
```

**Resolución:**

1. **Liberar espacio inmediato:** borrar backups locales antiguos:
   `find /var/backups/odoo/ -name '*.sql.xz' -mtime +3 -delete`
2. Limpiar logs de Docker: `docker system prune -f` (sin `-v` para no borrar volúmenes).
3. Si el problema es la DB: identificar tabla grande (ver diagnóstico) y analizar
   con el operador — posiblemente `mail.message` o `ir.logging`.
4. Expandir el volumen del VPS si la causa es crecimiento orgánico (contactar
   al proveedor VPS).
5. Una vez con espacio disponible: reiniciar Odoo si quedó en estado degradado.

**Prevención:** Configurar alerta en el VPS cuando el disco supere el 80% de
uso. Revisar política de retención de backups locales (7 días, ver
[`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4).

---

### Incidente 3: SSL cert expira

**Síntoma:** El navegador muestra `ERR_CERT_DATE_INVALID` o similar. Caddy
logs muestran errores de renovación Let's Encrypt.

**Severidad:** Alta — los usuarios no pueden acceder a Odoo via HTTPS.

**Diagnóstico:**

```bash
# Ver fecha de vencimiento del certificado actual:
echo | openssl s_client -connect tu-dominio.com.py:443 -servername tu-dominio.com.py 2>/dev/null \
  | openssl x509 -noout -dates

# Ver logs de Caddy por errores de renovación:
journalctl -u caddy --since "7 days ago" | grep -i "error\|renew\|acme\|challenge"

# Estado de Caddy:
systemctl status caddy
```

**Resolución:**

1. Verificar que el puerto 80 está accesible desde internet (HTTP-01 challenge):
   `curl -sf http://tu-dominio.com.py/` desde una máquina externa.
2. Forzar renovación manual: `sudo caddy reload` o `sudo systemctl restart caddy`.
3. Caddy intentará renovar automáticamente 30 días antes del vencimiento — si
   falló, verificar que el DNS del dominio apunta al VPS: `nslookup tu-dominio.com.py`.
4. Si el dominio caducó o el DNS está mal: corregir DNS y reiniciar Caddy.

**Prevención:** Caddy renueva automáticamente. Monitorear la fecha de
vencimiento mensualmente con el comando de diagnóstico.

---

### Incidente 4: CCFE expira

**Síntoma:** Los DTEs fallan al firmar — error en el proceso de firma XAdES.
El CCFE (certificado digital del contribuyente para firmar ante SIFEN) venció.

**Severidad:** Alta — la emisión de facturas electrónicas queda bloqueada.

**Diagnóstico:**

```bash
# Verificar fecha de vencimiento del CCFE (cuando exista l10n_py_edi):
# En Odoo: Configuración > Empresa > CCFE → ver campo 'Fecha de vencimiento'

# Desde línea de comandos (si el .p12 está accesible):
openssl pkcs12 -in /ruta/al/ccfe.p12 -nokeys -clcerts 2>/dev/null \
  | openssl x509 -noout -dates

# Logs de error de firma (Fase 2):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml logs odoo \
  | grep -i "ccfe\|firma\|sign\|certificate" | tail -20
```

> Note: procedimiento se valida en Fase 2 EDI / homologación.

**Resolución:**

1. Contactar al SET / Marangatú para renovar el CCFE antes del vencimiento.
2. Una vez obtenido el nuevo CCFE (.p12): subirlo en Odoo
   (Configuración > Empresa > CCFE — interfaz Fase 2).
3. Verificar que la firma funciona emitiendo un DTE de prueba en homologación.

**Prevención:** Configurar alerta 30 días antes del vencimiento del CCFE.
El CCFE típicamente tiene vigencia de 1 año — agendar la renovación con
antelación. El sistema debe mostrar un aviso en la UI cuando queden <30 días.

---

### Incidente 5: Migración catálogos DNIT

**Síntoma:** SIFEN rechaza DTEs con errores de validación de catálogos
(códigos de régimen, tipo de contribuyente, departamentos, etc.). DNIT publicó
una nueva versión del Manual Técnico SIFEN con cambios en tablas de referencia.

**Severidad:** Media — los DTEs nuevos pueden fallar; los ya emitidos son válidos.

**Diagnóstico:**

```bash
# Verificar versión del Manual Técnico en uso (comentado en código o ADR):
grep -r "Manual.*SIFEN\|v150\|version" addons/l10n_py_base/data/ | head -10

# Ver los catálogos actuales cargados:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT code, name FROM l10n_py_taxpayer_type ORDER BY code;" 2>/dev/null || true

# Respuestas de rechazo de SIFEN (Fase 2):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml logs odoo \
  | grep -i "rechazo\|invalid.*codigo\|catalog" | tail -20
```

> Note: procedimiento se valida en Fase 2 EDI / homologación.

**Resolución:**

1. Descargar la nueva versión del Manual Técnico SIFEN desde el sitio de DNIT.
2. Identificar los catálogos modificados comparando con la versión anterior.
3. Actualizar los CSVs canónicos en `addons/l10n_py_base/data/` con los nuevos
   valores y crear un PR con los cambios.
4. Generar los archivos de datos con `scripts/generate_module_data.py` si aplica.
5. Hacer upgrade del módulo en producción: `-u l10n_py_base` (ver
   [`docs/71_DEPLOYMENT.md`](71_DEPLOYMENT.md) §6).

**Prevención:** Suscribirse a notificaciones de actualización del portal DNIT.
Revisar el Manual Técnico SIFEN al inicio de cada trimestre.

---

### Incidente 6: Timbrado vencido o agotado

**Síntoma:** Odoo bloquea la confirmación de facturas con error "Timbrado
vencido" o "Número de documento agotado". No se pueden emitir nuevos DTEs.

**Severidad:** Alta — la facturación está bloqueada hasta resolver el timbrado.

**Diagnóstico:**

```bash
# Ver timbrados activos (Odoo shell o UI):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT name, expiry_date, state, company_id
      FROM l10n_py_timbrado
      WHERE state = 'active'
      ORDER BY expiry_date;"

# Ver últimas facturas confirmadas y su número de secuencia:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT name, invoice_date, state FROM account_move
      WHERE move_type IN ('out_invoice','out_refund')
        AND state = 'posted'
      ORDER BY id DESC LIMIT 10;"
```

**Resolución:**

1. **Timbrado vencido:** Gestionar un nuevo timbrado ante el SET / Marangatú.
   Una vez obtenido: Odoo > Contabilidad > Timbrado > Nuevo > activar.
2. **Secuencia agotada:** Verificar si el rango del timbrado se agotó (raro en
   PyMEs — el rango típico es de 9.999.999 documentos). Si es necesario, obtener
   un nuevo timbrado con el mismo o distinto PoE.
3. Desactivar el timbrado vencido/agotado para evitar confusión.
4. Emitir una factura de prueba para confirmar que el nuevo timbrado funciona.

**Prevención:** Configurar alerta 60 días antes del vencimiento del timbrado.
El timbrado tiene vigencia de 1 año — agendar la renovación con anticipación.
Los timbrados típicamente cubren millones de documentos; el agotamiento no es
común en PyMEs pero monitorear cuando el saldo sea < 10.000.

---

### Incidente 7: DTE rechazado por SIFEN (errores de validación masivos post-deploy)

**Síntoma:** Después de un upgrade de `l10n_py_edi` o cambio de catálogos,
múltiples DTEs son rechazados por SIFEN al enviarlos.

**Severidad:** Alta — los DTEs rechazados deben corregirse y reenviarse. Existe
un plazo legal de 72h.

**Diagnóstico:**

```bash
# Ver DTEs en estado error (Fase 2 — cuando exista edi_state):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT id, name, edi_state, edi_error_message
      FROM account_move
      WHERE edi_state = 'error'
      ORDER BY id DESC LIMIT 20;" 2>/dev/null || \
  echo "Columna edi_state no existe aun (pre-Fase 2)"

# Ver logs de respuesta SIFEN:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml logs odoo \
  | grep -i "sifen\|rechazado\|error.*edi\|SOAP.*Fault" | tail -50

# Verificar estructura del XML generado (muestra un caso):
# Odoo > Factura > Chatter > adjunto XML (Fase 2)
```

> Note: procedimiento se valida en Fase 2 EDI / homologación.

**Resolución:**

1. Identificar el patrón del error en los mensajes de rechazo (todos comparten
   la misma causa, o son individuales).
2. Si el error es un campo de catálogo: verificar si hay un cambio de versión
   de Manual Técnico pendiente (ver Incidente 5).
3. Si el error es de estructura XML: revisar el último commit de `l10n_py_edi`
   que tocó el builder.
4. Corregir la causa raíz y hacer upgrade del módulo.
5. Reencolar los DTEs rechazados desde la UI (botón "Reintentar" — Fase 2).
6. Verificar que el reenvío se aprueba antes de 72h desde la fecha de la factura.

**Prevención:** Ejecutar pruebas en el entorno de homologación SIFEN antes de
cada deploy a producción de `l10n_py_edi`.

---

### Incidente 8: Restore de backup falla en el test mensual

**Síntoma:** El script `scripts/restore-smoke.sh` ejecutado el primer domingo
del mes devuelve error o el check de módulos instalados falla.

**Severidad:** Media — la facturación productiva no está afectada, pero se
pierde la garantía de recuperabilidad del backup.

**Diagnóstico:**

```bash
# Ver el log del último run de restore-smoke:
journalctl -t restore-smoke --since "7 days ago"

# Ejecutar manualmente con output verbose:
bash -x /opt/l10n-paraguay/scripts/restore-smoke.sh \
  --dump-path "$(ls -t /var/backups/odoo/*.sql.xz | head -1)"

# Verificar integridad del dump más reciente:
xz -tv "$(ls -t /var/backups/odoo/*.sql.xz | head -1)"
```

Ver procedimiento completo de backup →
[`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4 Backup.

Ver script de restore → [`scripts/restore-smoke.sh`](../scripts/restore-smoke.sh).

**Resolución:**

1. **Dump corrupto:** verificar si el cron de backup está corriendo
   correctamente. Restaurar desde el dump anterior y reactivar el cron.
2. **Container efímero no levanta:** verificar disponibilidad de Docker y espacio
   en disco.
3. **Módulos instalados < esperados:** puede indicar que el dump es de una DB
   con menos módulos. Verificar que el dump es del ambiente correcto.
4. Una vez resuelto: ejecutar el smoke test nuevamente para confirmar OK.

**Prevención:** El cron mensual (primer domingo, 04:00 AM) está definido en
[`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4. Asegurarse de
que el log llega a `journald` con el tag `restore-smoke`.

---

### Incidente 9: Update de módulo rompe la DB (migration error — rollback)

**Síntoma:** Al hacer upgrade con `-u l10n_py_account` o similar, Odoo termina
con traceback en los logs, la DB queda en estado inconsistente y la instancia no
levanta correctamente.

**Severidad:** Alta — la instancia productiva está caída.

**Diagnóstico:**

```bash
# Ver el error exacto del upgrade:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml logs odoo \
  | grep -E "ERROR|Traceback|migration|upgrade" | tail -50

# Ver si Odoo levanta tras el fallo:
curl -sf http://127.0.0.1:8069/web/health || echo "Odoo no responde"

# Ver estado de módulos en la DB (si Postgres está OK):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT name, state, latest_version FROM ir_module_module
      WHERE state IN ('to upgrade','uninstallable');"
```

**Resolución:**

1. **STOP Odoo inmediatamente** (no reintentar el upgrade en caliente):
   `docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml stop odoo`
2. Restaurar desde el backup pre-upgrade (tomado antes del upgrade — ver
   [`docs/71_DEPLOYMENT.md`](71_DEPLOYMENT.md) §6 paso 1):
   ```bash
   # Restaurar dump pre-upgrade:
   docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
     psql -U $ODOO_DB_USER -c "DROP DATABASE $ODOO_DB_NAME;"
   docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
     psql -U $ODOO_DB_USER -c "CREATE DATABASE $ODOO_DB_NAME;"
   xz -dc /var/backups/odoo/pre-upgrade-FECHA.sql.xz \
     | docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec -T postgres \
         psql -U $ODOO_DB_USER -d $ODOO_DB_NAME
   ```
3. Reiniciar Odoo con la versión anterior del código:
   `cd /opt/l10n-paraguay && git checkout <commit-anterior>`
4. Verificar que la instancia levanta y la DB está OK.
5. Reportar el error al canal de desarrollo para corregir la migración.

**Prevención:** SIEMPRE tomar backup antes de cualquier upgrade (obligatorio,
ver [`docs/71_DEPLOYMENT.md`](71_DEPLOYMENT.md) §6). Probar el upgrade en
un entorno de staging antes de aplicar a producción.

---

### Incidente 10: Cron/queue de envío EDI atascado (DTEs sin transmitir >72h)

**Síntoma:** Hay DTEs en estado `to_send` que llevan más de 72 horas sin
transmitirse a SIFEN. El plazo legal de 72h establecido en la normativa DNIT
está próximo a vencer o ya venció.

**Severidad:** Alta — riesgo de incumplimiento legal. Los DTEs no transmitidos
a tiempo pueden generar multas o invalidación.

**Diagnóstico:**

```bash
# Ver DTEs en to_send con más de 1 hora de antigüedad (Fase 2):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT id, name, invoice_date, create_date, edi_state
      FROM account_move
      WHERE edi_state = 'to_send'
        AND create_date < NOW() - INTERVAL '1 hour'
      ORDER BY create_date;" 2>/dev/null || \
  echo "Columna edi_state no existe aun (pre-Fase 2)"

# Ver si el cron de Odoo está corriendo:
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec postgres \
  psql -U $ODOO_DB_USER -d $ODOO_DB_NAME \
  -c "SELECT name, active, nextcall, lastcall
      FROM ir_cron
      WHERE active = true
      ORDER BY nextcall LIMIT 10;"

# Ver workers de Odoo (cron thread):
docker compose -f /opt/l10n-paraguay/docker-compose.prod.yml exec odoo \
  ps aux | grep odoo
```

> Note: procedimiento se valida en Fase 2 EDI / homologación.

**Resolución:**

1. Verificar conectividad con SIFEN (ver Incidente 1 diagnóstico).
2. Verificar que el cron worker de Odoo está activo (el compose prod usa
   `--max-cron-threads=1` — si el proceso murió, reiniciar Odoo).
3. Si el cron está bloqueado por una excepción no manejada: revisar logs de
   Odoo por el traceback específico.
4. Reintentar manualmente los DTEs atascados desde la UI (Fase 2 — botón
   "Reintentar" o función de reenvío masivo).
5. Si el plazo de 72h está próximo a vencer: priorizar el reenvío de los DTEs
   más antiguos primero.

**Prevención:** Configurar alerta para DTEs en `to_send` por más de 30
minutos. El cron de envío debe ejecutarse cada 5 minutos en producción.
El plazo legal de 72h es el máximo absoluto — el objetivo operacional es
transmitir en < 5 minutos.

---

## Escalation path

| Nivel | Rol                  | Canal                                                                       | SLA orientativo        |
| ----- | -------------------- | --------------------------------------------------------------------------- | ---------------------- |
| N1    | Operador del deploy  | Panel Odoo / logs VPS / acceso directo VPS                                  | Inmediato              |
| N2    | Careaga Dev          | careagaezz@gmail.com                                                        | Respuesta < 4h hábiles |
| N3    | Externo (según caso) | Mesa ayuda SIFEN/DNIT, soporte VPS provider, comunidad OCA (#odoo-paraguay) | Variable               |

**Cuándo escalar a N2:** cuando el N1 no puede resolver en 30 minutos, cuando
el incidente involucra pérdida de datos o riesgo legal (plazo 72h DTEs), o
cuando el error requiere un fix en el código del módulo.

**Cuándo escalar a N3:** cuando el problema es externo (SIFEN down, proveedor
VPS con outage, certificado CCFE requiere trámite con SET) o cuando N2 no
puede resolver en 4h.

---

## Cross-references

- Estrategia de backup completa: [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4
- Seguridad de red y acceso: [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §6
- Deploy y procedimiento de upgrade: [`docs/71_DEPLOYMENT.md`](71_DEPLOYMENT.md)
- Script de restore test mensual: [`scripts/restore-smoke.sh`](../scripts/restore-smoke.sh)
- Ciclo de vida DTE (arquitectura): [`docs/70_ARCHITECTURE.md`](70_ARCHITECTURE.md)

---

_Documento creado en Phase 3 Pre-Fase 2 (Bloque C Documentación operacional).
Los incidentes SIFEN-dependientes (1, 4, 5, 7, 10) se validan en Fase 2 EDI
durante la homologación con CCFE de prueba._
