# Security Baseline — l10n-paraguay

**Estado:** baseline pre-deploy (Pre-Fase 2 Bloque B)
**Vigencia:** Pre-Fase 3 — cuando exista deploy real, validar comandos contra entorno
**Cross-ref:** ver [`docs/61_COMPLIANCE_LEY_7593.md`](61_COMPLIANCE_LEY_7593.md) para alcance legal (Ley 7593/2025 — Protección de Datos Personales PY)

---

## Alcance del documento

Este documento es un **blueprint operacional**, no una implementación. Cubre los
6 ejes de la baseline de seguridad que el operador debe activar cuando exista
deploy real (Pre-Fase 3) y, crucialmente, sirve como **especificación
implementable** para el helper Fernet de CCFE que se codeará en Fase 2 EDI
(`l10n_py_edi.tools.crypto`).

Cada eje sigue el patrón **qué hacemos / por qué / comandos ilustrativos**.
Todos los snippets de comandos llevan el marker
`> Note: validar en Pre-Fase 3 cuando exista deploy real` — no se ejecuta nada
en Phase 2 contra infraestructura real.

| #   | Eje                       | Componente / Módulo                   | Implementación      |
| --- | ------------------------- | ------------------------------------- | ------------------- |
| 1   | Autenticación y 2FA       | OCA `auth_totp_mail_enforce` / `web`  | Pre-Fase 3 deploy   |
| 2   | Política de contraseñas   | Odoo `auth_password_policy` (si 18.0) | Pre-Fase 3 deploy   |
| 3   | Audit logs                | OCA `auditlog` (server-tools 18.0)    | Fase 2 EDI manifest |
| 4   | Backup strategy           | `pg_dump` + Backblaze B2 + monthly RT | Pre-Fase 3 deploy   |
| 5   | CCFE encryption blueprint | `cryptography.fernet` + systemd-creds | Fase 2 EDI código   |
| 6   | Seguridad de red          | ufw + fail2ban + Caddy reverse proxy  | Pre-Fase 3 deploy   |

---

## 1. Autenticación y 2FA

### Qué hacemos

- **Forzar 2FA TOTP para todos los usuarios `admin` y `internal user`** de Odoo
  productivo. Mecanismo: OCA `auth_totp_mail_enforce` (server-auth 18.0) que
  combina el módulo `auth_totp` estándar de Odoo Community con un enforcement
  por grupo. Si en el momento del deploy `auth_totp_mail_enforce` aún no está
  porteado a 18.0, usar `auth_totp` (core) + política manual + revisión
  mensual.
- **Password de admin:** longitud mínima 14 caracteres, sin diccionario,
  rotación cada 90 días.
- **Session timeout:** 8 horas para usuarios internos, 1 hora para portal
  (cliente final).
- **Login throttling:** 5 intentos fallidos → bloqueo IP 15 minutos (vía
  fail2ban — ver §6).

### Por qué

El admin de Odoo tiene acceso completo a la base de datos, incluyendo el
campo `vat`/`l10n_py_dv` de todos los partners. Compromiso de la cuenta
admin = **pérdida total de PII en reposo**.

Para la **emisión de DTE falsos**, el modelo de threat depende del estado
de implementación de §5 (CCFE encryption blueprint):

- **Sin el blueprint §5 implementado** (estado actual / Phase 2): el CCFE
  vive como Binary en la DB o filesystem en plaintext. Compromiso de admin
  permite extraer el CCFE y firmar DTE en nombre del contribuyente —
  **impacto fiscal directo**.
- **Con el blueprint §5 implementado** (target Fase 2 EDI + Pre-Fase 3
  deploy): el CCFE está cifrado con data key, que a su vez está cifrada
  con master key custodiada por systemd-creds fuera de PostgreSQL.
  Compromiso de admin expone PII pero el CCFE descifrado requiere
  **además** compromise del sistema operativo del VPS (acceso root o
  escalación). El blast radius se reduce a PII en reposo; la capacidad
  de firmar DTE queda detrás de una segunda barrera.

La defensa en profundidad (2FA + password policy + audit logs + CCFE
encryption + network security) es la suma de los 6 ejes de este documento.

### Comandos ilustrativos

```bash
# Activar 2FA TOTP en la instancia (load_modules):
odoo-bin --addons-path=/odoo/addons,/opt/oca,/opt/l10n-paraguay/addons \
         --load=base,web,auth_totp \
         --database=odoo_prod
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

```bash
# Forzar TOTP por grupo (UI):
# Settings > Users & Companies > Groups > Internal User > Inherited > "Two-factor authentication required"
# Verificar que el grupo "settings" (admins) tenga la regla activa.
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

### Gap conocido

Si `auth_totp_mail_enforce` no está disponible en 18.0 al momento del deploy,
documentar como **gap aceptado** en el ADR de deploy y aplicar la política
manualmente (review mensual de usuarios sin 2FA activa).

---

## 2. Política de contraseñas

### Qué hacemos

- **Longitud mínima ≥ 10** para usuarios estándar, ≥ 14 para admins.
- **Sin palabras de diccionario** — usar password manager generado.
- **Lockout tras 5 intentos fallidos** en 5 minutos (capa fail2ban — §6).
- Apuntar al módulo `auth_password_policy` (Odoo standard) si está disponible
  en 18.0; si no, política documentada + revisión periódica de hashes débiles.
- **NO** usar SHA-1 ni MD5 para password storage (Odoo usa PBKDF2 desde 13.0
  por default — no tocar).

### Por qué

El attack vector más común contra instancias Odoo expuestas a internet es
credential stuffing (passwords reutilizadas filtradas de otros sitios). La
combinación 2FA (§1) + password policy + lockout (§6) reduce el riesgo a
phishing dirigido o compromiso del endpoint del usuario.

### Comandos ilustrativos

```bash
# Verificar disponibilidad de auth_password_policy en 18.0:
pip show odoo-addon-auth-password-policy 2>/dev/null \
  || echo "[gap] auth_password_policy no instalado — usar política manual"
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

```bash
# Auditar usuarios sin password fuerte (script de revisión periódica):
# psql -U odoo -d odoo_prod -c "SELECT login, length(password) FROM res_users WHERE active = true;"
# (length aquí mide el hash PBKDF2; no revela password real)
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

### Gap conocido

Odoo no expone configuración granular de password policy en Community sin
módulo adicional. Si `auth_password_policy` no se porta a 18.0, queda como
**TODO operador** documentado en el handover.

---

## 3. Audit logs (OCA `auditlog`)

### Qué hacemos

Usar el módulo OCA [`auditlog`](https://github.com/OCA/server-tools/tree/18.0/auditlog)
(server-tools 18.0, último commit ~Abril 2026, mantenimiento activo) para
registrar create/write/unlink en los modelos fiscalmente sensibles. **NO se
instala en Phase 2** — la dependencia se suma al `__manifest__.py` del addon
correspondiente en su phase (probable Fase 2 EDI para `l10n_py_edi`).

### Modelos a auditar

| Modelo                     | Módulo                                 | Campos sensibles                                               | Justificación                                                                                                                  |
| -------------------------- | -------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| `res.partner`              | `l10n_py_base`                         | `vat`, `l10n_py_dv`, `l10n_latam_identification_type_id`       | PII fiscal — cambios de RUC son auditables bajo Ley 125/91                                                                     |
| `res.company`              | `l10n_py_base`                         | `vat`, `l10n_py_dv`                                            | Configuración crítica de empresa contribuyente                                                                                 |
| `l10n_py.timbrado`         | `l10n_py_account`                      | `name`, `state`, `expiry_date`                                 | Timbrado determina validez legal del DTE — cualquier cambio es auditable                                                       |
| `l10n_latam.document.type` | `l10n_py_account`                      | `code`, `internal_type`                                        | Tipos de documento SIFEN — cambios afectan generación XML                                                                      |
| `account.move`             | Odoo core + `l10n_py_account` (Fase 1) | `state`, `name`, `amount_total`, `l10n_latam_document_type_id` | Trazabilidad de cambios post-emisión (Ley 125/91); en Fase 2 EDI se sumarán campos SIFEN (`sifen_state`, `cdc`, `fecha_envio`) |

> Cross-ref: ver [`docs/61_COMPLIANCE_LEY_7593.md`](61_COMPLIANCE_LEY_7593.md) §3
> "Derechos ARCO + mecanismos Odoo" — el audit log es el control que respalda
> el derecho de rectificación (Art. 12 Ley 7593/2025).

### Retención

**7 años archivado + 1 año online.** Fundamento: Ley 125/91 PY (Régimen
Tributario) define un período de prescripción de 5 años para deuda fiscal; se
agregan 2 años de margen para cubrir reapertura de fiscalizaciones, demandas y
auditorías externas. El primer año queda en tablas Odoo (`auditlog.log`)
accesible vía UI; los 6 años restantes se exportan a almacenamiento frío
(S3-compatible, ver §4) en formato Parquet o JSONL comprimido.

### Por qué

Trazabilidad obligatoria para fiscalización DNIT (cambios de RUC,
manipulación de timbrados, edición post-emisión de DTE) y para responder
solicitudes de rectificación bajo Ley 7593/2025.

### Comandos ilustrativos

```python
# En l10n_py_account/__manifest__.py o l10n_py_edi/__manifest__.py (Fase 2 EDI):
# "depends": [..., "auditlog"],
#
# Configuración via UI: Settings > Audit Log > Rules
# Crear rule por modelo:
#   - res.partner — fields: vat, l10n_py_dv, l10n_latam_identification_type_id
#   - res.company — fields: vat, l10n_py_dv
#   - l10n_py.timbrado — all fields
#   - l10n_latam.document.type — fields: code, internal_type
```

```bash
# Export anual a almacenamiento frío (cron):
psql -U odoo -d odoo_prod -c "\
COPY (SELECT * FROM auditlog_log WHERE create_date < now() - interval '1 year') \
TO PROGRAM 'gzip > /var/backups/odoo/audit-$(date +%Y).jsonl.gz' \
WITH (FORMAT csv, HEADER true);"
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

### Gap conocido

`auditlog` no captura cambios fuera del ORM (raw SQL via psql, `cr.execute()`
en código custom). El operador debe restringir acceso shell a la base de
datos para mantener la cadena de custodia.

---

## 4. Backup strategy

### Qué hacemos (D-12)

Doble target — local + offsite — con test de restauración mensual:

- **Filesystem local:** `pg_dump | xz` diario a las 02:00 AM, retención 7 días,
  path `/var/backups/odoo/`.
- **Offsite (S3-compatible):** sync nocturno a **Backblaze B2** (default por
  costo, ~USD 6/TB/mes). Alternativa: AWS S3 (~USD 23/TB/mes) si el cliente
  paga la diferencia. Retención offsite: **90 días** rolling.
- **Monthly restore test:** primer domingo de cada mes corre
  [`scripts/restore-smoke.sh`](../scripts/restore-smoke.sh) — restaura el
  último dump a un container Postgres efímero y verifica
  `SELECT count(*) FROM ir_module_module WHERE state='installed'` (módulos
  instalados > 0 y consistente con el deploy de referencia).

### Por qué

- **Local:** RPO < 24h para recovery rápido (perdiendo máximo 1 día de
  emisiones DTE — recuperable desde SIFEN ya que el envío al servidor DNIT es
  la fuente de verdad fiscal).
- **Offsite:** protección contra ransomware del VPS, fallo de hardware, o
  compromiso del operador.
- **Monthly restore test:** un backup que no se restaura no es un backup.
  Validación periódica detecta corrupción silenciosa antes de que se necesite.

### Comandos ilustrativos

```bash
# /etc/cron.d/odoo-backup — diario 02:00 AM:
# Opción A — compresión sin cifrar (DEFAULT — Backblaze B2 cifra en
# tránsito + reposo del lado del proveedor, pero el archivo local
# queda en plaintext):
0 2 * * * postgres pg_dump -Fc odoo_prod | xz -T0 > /var/backups/odoo/odoo-$(date +\%F).sql.xz

# Opción B — compresión + cifrado GPG (RECOMENDADO para compliance
# estricto Ley 7593/2025 — protege el dump local contra exfiltración):
# Pre-requisito: importar la GPG pubkey del operador como user `postgres`:
#   sudo -u postgres gpg --import /path/to/operator-backup-pub.key
0 2 * * * postgres pg_dump -Fc odoo_prod \
    | gpg --encrypt --recipient backup@operador.com.py \
    | xz -T0 > /var/backups/odoo/odoo-$(date +\%F).sql.gpg.xz

# Rotación: keep 7 days
30 2 * * * root find /var/backups/odoo/ -name 'odoo-*.sql*.xz' -mtime +7 -delete
```

**Trade-off encryption local:**

| Opción       | Compliance                         | Complejidad             | Latencia restore |
| ------------ | ---------------------------------- | ----------------------- | ---------------- |
| A — solo xz  | Riesgo: PII plaintext en disco VPS | Baja                    | Inmediato        |
| B — gpg + xz | Cumple Ley 7593/2025 más estricto  | Media (gestión GPG key) | +30s (decrypt)   |

**Para PyMEs**: opción A es aceptable si el VPS tiene controles de acceso
fuertes (SSH key-only §6 + ufw + fail2ban + sin shell users no-admin) y el
riesgo de compromise filesystem es bajo.

**Para clientes con SLA estricto o auditoría externa**: opción B obligatoria.
La gestión de la GPG private key del operador (custodia, rotación, backup
separado) se documenta en `docs/72_RUNBOOK.md` (Pre-Fase 3).

> Note: validar en Pre-Fase 3 cuando exista deploy real

```bash
# Sync offsite a Backblaze B2 (rclone):
# Configurar rclone una vez: rclone config → nuevo remote tipo "b2" → keyID/applicationKey
0 3 * * * postgres rclone sync /var/backups/odoo/ b2:l10n-paraguay-backups/odoo/ \
                              --transfers 4 --b2-hard-delete
# Retención offsite — lifecycle rule en B2: delete after 90 days
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

```bash
# Monthly restore test (primer domingo cada mes):
0 4 1-7 * 0 root /opt/l10n-paraguay/scripts/restore-smoke.sh \
                 --dump-path "$(ls -t /var/backups/odoo/*.sql.xz | head -1)" \
                 2>&1 | logger -t restore-smoke
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

### Endpoints alternativos

| Backend           | Costo (USD/TB/mes) | Latencia restore | Recomendado para      |
| ----------------- | ------------------ | ---------------- | --------------------- |
| Backblaze B2      | ~6                 | Minutos          | Default (PyME budget) |
| AWS S3 Standard   | ~23                | Segundos         | Cliente premium / SLA |
| AWS S3 Glacier IR | ~4                 | ~10 min          | Archivo > 90 días     |
| Cloudflare R2     | ~15                | Segundos         | Sin egress fees       |

> Note: pricing 2026-06 — revalidar antes de provisionar.

---

## 5. CCFE encryption blueprint (D-10)

### Conceptos CCFE relevantes

**CCFE** (Código de Control de Firma Electrónica) es el certificado p12
privado del contribuyente que se usa para firmar XAdES el XML del DTE antes
de enviar al servidor SIFEN. Es análogo a una clave privada bancaria. La
estrategia de cifrado en reposo (data at rest) protege este archivo contra
exfiltración de la base de datos o el disco del VPS.

### Envelope schema recomendado

```
Disco VPS:
  /etc/credstore.encrypted/odoo-ccfe-master-key
    └─ Master key cifrada con systemd-creds host key (TPM2 si disponible)

  /var/backups/odoo/ccfe-wrap-keys/<key-id>.key.enc
    └─ Data keys cifradas con master key (1 data key por trimestre / rotación 90d)

PostgreSQL (ir.config_parameter):
  l10n_py_edi.ccfe.wrap_key_id = "k-2026-q2"
    └─ ID de la data key activa (referencia, no contenido)

PostgreSQL (ir.attachment o campo Binary en l10n_py.ccfe):
  content = <Fernet token>
    └─ CCFE .p12 bytes cifrados con data key activa
```

### Pseudo-código Python (blueprint para `l10n_py_edi.tools.crypto`)

```python
# Fuente: cryptography.fernet — https://cryptography.io/en/stable/fernet/
# Este bloque es blueprint para l10n_py_edi.tools.crypto — NO ejecutar en Phase 2
# Implementación real: Fase 2 EDI (módulo l10n_py_edi)

from cryptography.fernet import Fernet, MultiFernet


def generate_data_key() -> bytes:
    """Genera una nueva data key (32 bytes URL-safe base64).

    Cifrar con la master key (vía systemd-creds) y guardar como
    /var/backups/odoo/ccfe-wrap-keys/k-YYYY-QN.key.enc antes de usar.
    """
    return Fernet.generate_key()


def encrypt_ccfe(p12_bytes: bytes, data_key: bytes) -> bytes:
    """Cifra el CCFE .p12 con la data key activa.

    Devuelve un token Fernet (bytes, base64-encoded) que se almacena en
    PostgreSQL como Binary o como ir.attachment.content.
    """
    f = Fernet(data_key)
    return f.encrypt(p12_bytes)


def decrypt_ccfe(token: bytes, data_key: bytes) -> bytes:
    """Descifra el token para firmar XAdES.

    Usar en el contexto de firma (TransactionCase corto). Sin TTL — el CCFE
    tiene vigencia larga (1 año típico) y los tokens deben sobrevivir todo
    el período del certificado.
    """
    f = Fernet(data_key)
    return f.decrypt(token)


def rotate_ccfe_key(token: bytes, old_key: bytes, new_key: bytes) -> bytes:
    """Re-cifra el token con una key nueva, preservando timestamp.

    MultiFernet.rotate() descifra con old_key y re-cifra con new_key en una
    sola operación atómica. Llamar para cada record CCFE durante la rotación
    trimestral (ver scripts/ccfe-rotate-key.py outline más abajo).
    """
    mf = MultiFernet([Fernet(new_key), Fernet(old_key)])
    return mf.rotate(token)
```

[Cita: <https://cryptography.io/en/stable/fernet/> — `Fernet` y `MultiFernet`
API estable.]

### systemd-creds para master key (VPS Debian/Ubuntu)

```bash
# Cifrar la master key con la host key del VPS (modo --with-key=host):
echo -n "<base64-master-key>" | sudo systemd-creds encrypt \
    --with-key=host \
    --name=odoo-ccfe-master-key \
    - /etc/credstore.encrypted/odoo-ccfe-master-key

# Permisos restrictivos:
sudo chmod 0600 /etc/credstore.encrypted/odoo-ccfe-master-key
sudo chown root:root /etc/credstore.encrypted/odoo-ccfe-master-key
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

```bash
# Descifrar en script de inicio del servicio Odoo:
sudo systemd-creds decrypt \
    /etc/credstore.encrypted/odoo-ccfe-master-key -

# Nota: --with-key=host usa /var/lib/systemd/credential.secret (solo root).
# En VPS con TPM2 (KVM con vTPM o hardware dedicado):
#   --with-key=tpm2  → más seguro, key bound al hardware
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

[Cita: <https://systemd.io/CREDENTIALS> + manpages de `systemd-creds(1)`.]

### Caveat de Disaster Recovery con `--with-key=host`

El modo `--with-key=host` (línea 357 del bloque anterior) ata la master key
al archivo `/var/lib/systemd/credential.secret` del VPS donde se ejecuta el
encrypt. Esto tiene una consecuencia importante:

**Si el VPS se rebuilea (provisioning nuevo, fallo de hardware, migración a
otro provider, reinstall del OS), se pierde la capacidad de descifrar la
master key cifrada.**

Esto implica que el contenido cifrado por la master key (las data keys
trimestrales) tampoco puede recuperarse desde un backup. Los CCFE cifrados
con esa data key se vuelven inutilizables.

**Mitigaciones:**

1. **Procedimiento de rebuild planificado:**

   - ANTES del rebuild: descifrar la master key a un archivo temporal seguro
     (`systemd-creds decrypt ... > /tmp/master-key.tmp`).
   - Hacer rebuild del VPS.
   - Re-cifrar con la NUEVA host key del nuevo VPS:
     `systemd-creds encrypt --with-key=host - /etc/credstore.encrypted/...`
   - Eliminar archivo temporal: `shred -u /tmp/master-key.tmp`.

2. **Para deploys con DR estricto** (cliente paga por alta disponibilidad):
   considerar **HashiCorp Vault** o **AWS KMS** desde el inicio del deploy.
   El blueprint general (envelope de master/data keys) sigue siendo el mismo
   — solo cambia el storage de la master key.

3. **Backup planeado de la master key:**
   - Exportar a un secrets manager separado (1Password, Bitwarden Business,
     etc.) con MFA obligatorio.
   - Documentar el procedimiento de restore en `docs/72_RUNBOOK.md`
     (Pre-Fase 3) con responsabilidad operador.

> **Trade-off explícito:** `--with-key=host` es más simple pero acopla la
> seguridad al hardware/host actual. Vault/KMS desacopla pero suma
> dependencia operacional. Para el primer cliente PyME, el riesgo de
> rebuild planificado es bajo y el procedimiento de mitigación 1 es
> suficiente.

### `ir.config_parameter` storage layout

```python
# Storage design — la data key activa se referencia por ID (no se almacena):
#
# Parámetro que identifica la data key activa:
#   key:   "l10n_py_edi.ccfe.wrap_key_id"
#   value: "k-2026-q2"   (string corto, sin la key en sí)
#
# El contenido cifrado de la data key vive fuera de Odoo
# (en /etc/credstore.encrypted/ o un secrets manager externo).
# Odoo usa el ID para localizar y descifrar la data key en runtime.

# Acceso desde modelos Odoo (blueprint — NO ejecutar en Phase 2):
config_param = self.env['ir.config_parameter'].sudo()
wrap_key_id = config_param.get_param('l10n_py_edi.ccfe.wrap_key_id')
# → usar wrap_key_id para localizar la data key en /etc/credstore.encrypted/
```

[Cita: `odoo-development.readthedocs.io` → `ir.config_parameter`.]

### Rotation script outline (`scripts/ccfe-rotate-key.py` stub)

```python
# scripts/ccfe-rotate-key.py — outline para Fase 2 EDI (NO existe en Phase 2)
# Trigger: ir.cron mensual que verifica si pasaron 90 días desde última rotación

# Pasos del script de rotación trimestral:
# 1. Generar nueva data key:
#       new_key = Fernet.generate_key()
# 2. Cifrar new_key con master key (vía systemd-creds) y guardar como
#       /var/backups/odoo/ccfe-wrap-keys/k-YYYY-QN.key.enc
# 3. Para cada registro CCFE activo en la DB:
#       token_new = rotate_ccfe_key(token_old, old_key, new_key)
#       record.write({'ccfe_encrypted': token_new})
# 4. Actualizar ir.config_parameter:
#       l10n_py_edi.ccfe.wrap_key_id = "k-YYYY-QN"
# 5. Escribir entrada en auditlog:
#       "CCFE key rotated: old=k-XXXX new=k-YYYY"  (§3)
# 6. Conservar old_key por 1 rotación adicional (180 días total)
#    para decrypt de tokens en tránsito o backups recientes.
```

### Por qué este diseño

- **Envelope cifrado:** la master key nunca toca la base de datos. Un dump
  filtrado de PostgreSQL solo expone tokens Fernet (inútiles sin la data key).
- **Data key rotativa:** comprometer una data key compromete máximo 90 días de
  CCFEs cifrados — limita el blast radius.
- **systemd-creds:** evita gestionar un secrets manager externo (HashiCorp
  Vault, AWS KMS) en la primera iteración. Si el cliente lo requiere, el
  blueprint sigue siendo el mismo cambiando solo el storage de la master key.
- **`MultiFernet.rotate()`:** API explícita de la stdlib `cryptography` que
  preserva el timestamp del token original, evitando regenerar ciphertext
  desde cero.

> Cross-ref: ver [`docs/61_COMPLIANCE_LEY_7593.md`](61_COMPLIANCE_LEY_7593.md) §2
> "Responsabilidades: vendor vs operador" — el vendor (este proyecto) provee
> el helper de cifrado; el operador provee y custodia la master key.

### Gap conocido

El código real **no existe en Phase 2**. Se escribe en Fase 2 EDI cuando
exista el módulo `l10n_py_edi` y un consumidor concreto (el flujo de firma
XAdES). Este blueprint es suficientemente denso para que la implementación se
escriba siguiendo el patrón sin re-decidir envelope schema, rotation cadence,
ni storage layout.

---

## 6. Seguridad de red

### Qué hacemos

- **Firewall (ufw):** permitir solo 22 (SSH, restringido por IP del operador),
  80 (HTTP → redirect HTTPS), 443 (HTTPS). Bloquear todo lo demás. Postgres
  (5432) **NO** se expone — solo accesible localmente o vía SSH tunnel.
- **fail2ban:** monitorear `/var/log/auth.log` (SSH brute force) y
  `/var/log/odoo/odoo.log` (login fail Odoo). Ban 15 min tras 5 fallos en
  5 min.
- **Reverse proxy Caddy:** SSL automático vía Let's Encrypt (HTTP-01
  challenge), HSTS, headers de seguridad (`X-Frame-Options`, `X-Content-Type-Options`,
  `Referrer-Policy`). Caddy proxy a Odoo en `127.0.0.1:8069`.
- **SSH:** solo public key, sin password, port 22 abierto solo al CIDR del
  operador (o IPs whitelisted).

### Por qué

El VPS de Odoo es internet-facing. Sin firewall + fail2ban, en horas hay
intentos de brute force SSH y de login Odoo (`admin/admin`, `admin/123456`).
Sin Caddy + HSTS, hay riesgo de downgrade attack (MITM forzando HTTP) que
filtra session cookies de Odoo y credenciales de login.

### Comandos ilustrativos

```bash
# ufw rules (Ubuntu/Debian):
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow from <operator-cidr> to any port 22 proto tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status verbose
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

```ini
# /etc/fail2ban/jail.d/odoo.conf:
[odoo-auth]
enabled = true
port = http,https
filter = odoo-auth
logpath = /var/log/odoo/odoo.log
maxretry = 5
findtime = 300
bantime = 900

# /etc/fail2ban/filter.d/odoo-auth.conf:
# [Definition]
# failregex = ^.*Login failed for db:.*login:.*from <HOST>.*$
#
# GAP CONOCIDO: Odoo Community 18.0 NO emite logs estructurados de
# login failure con el formato anterior por default. La regex es ilustrativa;
# en deploy real hay que:
#
# 1. Instrumentar logs via:
#    a) Monkey-patch de res.users.authenticate() para emitir formato custom
#    b) Modulo OCA auth_brute_force si esta portado a 18.0 (verificar)
#    c) Hook en login form template para loguear desde JS
#
# 2. Ajustar el failregex al formato emitido por la opcion elegida en (1).
#
# 3. Validar con fail2ban-regex contra logs reales antes de activar el jail.
#
# Documentar el approach final en docs/72_RUNBOOK.md (Pre-Fase 3).
```

> Note: validar en Pre-Fase 3 cuando exista deploy real

```caddyfile
# /etc/caddy/Caddyfile — reverse proxy + SSL automático:
odoo.example.com {
    reverse_proxy 127.0.0.1:8069 {
        header_up X-Forwarded-Proto {scheme}
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
```

> Note: validar en Pre-Fase 3 cuando exista deploy real — cross-ref futuro `docs/71_DEPLOY_PRODUCTION.md` (Phase 3 DOC-02)

### Gap conocido

- **DDoS:** ufw + fail2ban protegen contra ataques de baja sofisticación; un
  DDoS volumétrico requiere Cloudflare o proveedor anti-DDoS. Documentar como
  TODO operador / Pre-Fase 4 si el cliente lo amerita.
- **SSH 22 público:** si el operador no tiene IP fija, considerar Tailscale o
  un bastion host en lugar de whitelisting CIDR.
- **fail2ban + Odoo:** el approach genérico (monitorear `odoo.log`) no
  funciona out-of-the-box en 18.0 por falta de logs estructurados de
  login failure. Resolver en Pre-Fase 3 con instrumentación específica
  (ver comentarios en el bloque `odoo-auth.conf` arriba). Mientras tanto,
  el control de §1 (2FA) + §2 (password policy) + rate-limiting via Caddy
  provee defensa razonable.

---

## Cross-references

- Compliance legal: [`docs/61_COMPLIANCE_LEY_7593.md`](61_COMPLIANCE_LEY_7593.md)
- Restore test stub: [`scripts/restore-smoke.sh`](../scripts/restore-smoke.sh)
- Workflow CI de seguridad: [`.github/workflows/security.yml`](../.github/workflows/security.yml)
- Reporte de vulnerabilidades: [`SECURITY.md`](../SECURITY.md)
- Librerías Python (incluye `cryptography`): [`docs/40_PYTHON_LIBRARIES.md`](40_PYTHON_LIBRARIES.md)

---

_Documento creado en Phase 2 Pre-Fase 2 (Bloque B Security Baseline). Próxima
revisión: Pre-Fase 3 cuando se provisione el VPS real y se valide cada snippet
contra el entorno._
