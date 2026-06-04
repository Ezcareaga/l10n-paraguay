#!/usr/bin/env bash
# scripts/restore-smoke.sh — Smoke test de restauración de backup mensual.
#
# STUB — Phase 2 Pre-Fase 2 security baseline (D-12).
# Implementación completa: Pre-Fase 3 cuando exista deploy real en VPS.
#
# Propósito (referencia: docs/60_SECURITY_BASELINE.md §4 Backup strategy):
#   Restaurar el último dump a un container Postgres efímero y verificar:
#       SELECT count(*) FROM ir_module_module WHERE state='installed'
#   El script falla si el count es 0 (dump corrupto o vacío) o si difiere
#   significativamente del baseline registrado en la última restauración OK.
#
# Uso (cuando esté implementado en Pre-Fase 3):
#   ./scripts/restore-smoke.sh [--dump-path /var/backups/odoo/latest.sql.xz]
#
# Pasos del test de restauración real (a implementar):
#   1. Descomprimir el dump:
#        xz -d < <dump_path> > /tmp/restore-smoke.sql
#   2. Levantar container Postgres efímero (mismo major que prod):
#        docker run -d --name odoo-restore-smoke -e POSTGRES_PASSWORD=tmp postgres:16
#   3. Restaurar:
#        psql -h localhost -U postgres -d odoo < /tmp/restore-smoke.sql
#   4. Verificar módulos instalados:
#        psql -h localhost -U postgres -d odoo -c \
#          "SELECT count(*) FROM ir_module_module WHERE state='installed'"
#   5. Limpiar:
#        docker rm -f odoo-restore-smoke
#        rm -f /tmp/restore-smoke.sql
#
# Trigger en Pre-Fase 3: cron mensual el primer domingo de cada mes a las 04:00.
# Salida esperada: log a syslog con tag "restore-smoke" + exit code 0/1.

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Las variables se usarán en la implementación completa de Pre-Fase 3.
# Por ahora se marcan como unused para evitar warnings de shellcheck SC2034.
: "${SCRIPT_DIR}"
: "${REPO_ROOT}"

echo "[restore-smoke] STUB — implementación pendiente para Pre-Fase 3."
echo "[restore-smoke] Ver docs/60_SECURITY_BASELINE.md §4 Backup strategy para el diseño."
echo "[restore-smoke] Sin acción en este entorno; exit 0 para no romper pre-commit/CI."
exit 0
