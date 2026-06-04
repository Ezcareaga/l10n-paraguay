# Compliance — Ley 7593/2025 (Protección de Datos Personales)

**Ley aplicable:** Ley 7593/2025 PY (general, GDPR-style)
**Vigencia:** 2027-11-27 (promulgada 2025-11-27)
**Autoridad supervisora:** ANPDP (Agencia Nacional de Protección de Datos Personales) dentro de MITIC
**Cross-ref:** ver [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) para controles técnicos
**Audiencia:** reviewers OCA, abogados del cliente, deployers / operadores

---

## 1. Alcance y ley aplicable

Este documento describe cómo el proyecto `l10n-paraguay` se posiciona frente a la
**Ley 7593/2025 — "De Protección de Datos Personales en la República del
Paraguay"**. Esta es la ley **general** de protección de datos personales en
Paraguay, equivalente conceptual al GDPR europeo: cubre cualquier dato personal
(nombre, RUC, CI, email, teléfono, dirección, datos comerciales) tratado por un
responsable o encargado en territorio paraguayo.

**Por qué aplica a este proyecto:**

- Los módulos `l10n_py_base`, `l10n_py_account` y futuros (`l10n_py_edi`,
  `l10n_py_pos`, etc.) procesan **PII de clientes** (`res.partner`) y de
  **empleados/usuarios** (`res.users`) — RUC, CI, dirección, teléfono, email.
- Las facturas electrónicas (DTE) emitidas por SIFEN contienen datos
  identificatorios del cliente (`vat`, `l10n_py_dv`, `name`, dirección) —
  todos son datos personales sujetos a la ley.
- El proyecto se distribuye bajo AGPL-3.0 a comercios paraguayos
  (deployers/operadores) — el operador es el **responsable de tratamiento**
  ante la ANPDP; este proyecto es **encargado de software / vendor**.

**Comparación rápida con GDPR (Reglamento (UE) 2016/679):**

| Concepto                     | GDPR                                 | Ley 7593/2025 PY                        |
| ---------------------------- | ------------------------------------ | --------------------------------------- |
| Base legal                   | Art. 6                               | Art. 5 (condiciones tratamiento lícito) |
| Derecho de acceso            | Art. 15                              | Art. 28                                 |
| Derecho de rectificación     | Art. 16                              | Art. 29                                 |
| Derecho de borrado           | Art. 17 ("right to be forgotten")    | Art. 31 (supresión / cancelación)       |
| Derecho de oposición         | Art. 21                              | Art. 30                                 |
| Derecho de portabilidad      | Art. 20                              | Art. 32                                 |
| Plazo notificación brecha    | 72h                                  | 72h (Art. 17)                           |
| Figura del DPO               | Art. 37                              | Art. 18                                 |
| Transferencia internacional  | Art. 44-49                           | Art. 19                                 |
| Evaluación de impacto (DPIA) | Art. 35                              | Arts. 14-15                             |
| Autoridad supervisora        | DPA nacional (e.g., AEPD en España)  | **ANPDP** dentro de **MITIC**           |
| Sanciones                    | Hasta 4% facturación anual / 20M EUR | Régimen escalonado (Arts. 43-47)        |

**ANPDP en formación — caveat temporal:** la Ley 7593/2025 fue promulgada el
27 de noviembre de 2025 con **vigencia diferida al 27 de noviembre de 2027**
(período de adecuación de 2 años). La ANPDP, creada por la propia ley (Arts.
34-39), está **en proceso de constitución dentro de MITIC** durante 2026 y se
espera operativa antes de la entrada en vigor. Hasta 2027 el enforcement es
limitado — las referencias en este documento son **forward-looking**: el
operador debe re-verificar el estado regulatorio antes del despliegue
productivo y al actualizar versiones de este proyecto post-2027.

**Aclaración sobre la autoridad:** la autoridad supervisora correcta es
**ANPDP / MITIC**. Otras entidades regulatorias paraguayas (servicios
nacionales con acrónimo parecido vinculados a calidad o acreditación) **no**
tienen competencia en protección de datos personales y no deben citarse como
autoridad de notificación bajo Ley 7593/2025.

---

## 2. Responsabilidades: vendor vs operador (D-13)

Este proyecto es **software vendor / encargado**, no **responsable de
tratamiento**. La distinción es jurídica y técnica: el **operador (deployer
del módulo en su VPS)** decide los fines y medios del tratamiento; este
proyecto proporciona las **herramientas técnicas** para que ese tratamiento
cumpla con Ley 7593/2025.

| Responsabilidad          | Vendor (este proyecto)                                                                               | Operador (deployer/cliente)                                     |
| ------------------------ | ---------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| Cifrado PII en reposo    | ✅ Blueprint en [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §5 (CCFE / Fernet)         | Implementar en deploy real (VPS + systemd-creds)                |
| Audit logs               | ✅ Estrategia en [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §3 (OCA `auditlog`)       | Activar reglas vía UI; configurar retención 7y / 1y             |
| Export / borrado         | ✅ Mecanismos documentados en §3 de este doc (Odoo built-in + OCA)                                   | Ejecutar a solicitud del titular dentro del plazo legal         |
| Default password policy  | ✅ Documentado en [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §2 (Odoo built-in + 2FA) | Configurar en instancia + forzar 2FA para admins                |
| DPO designation          | ❌ No corresponde al vendor                                                                          | Designar DPO según reglamentación ANPDP (Art. 18)               |
| Notificación a ANPDP     | ❌ No corresponde al vendor (notifica al operador, no a ANPDP)                                       | Notificar a ANPDP + titulares en **≤72h** (Art. 17)             |
| Consent capture          | ❌ No incluido en módulos Odoo del proyecto                                                          | Implementar en formulario web propio o POS (Fase 4)             |
| Contratos con encargados | ❌ No corresponde al vendor                                                                          | Firmar contratos de tratamiento con terceros (hosting, mailing) |
| Política de retención    | ❌ Vendor no define retention business-specific                                                      | Definir retention por categoría de dato y tipo de negocio       |
| Registro de tratamiento  | ❌ Plantilla mínima en blueprint                                                                     | Mantener registro vía OCA `privacy` (ver §4)                    |

**Comunicación vendor → operador en caso de vulnerabilidad descubierta por el
vendor:** si el vendor descubre una vulnerabilidad en los módulos que pueda
afectar a deployers (vía `SECURITY.md` reporting o disclosure interno),
notifica a operadores conocidos vía email `careagaezz@gmail.com` con prioridad
alta. Esta comunicación **NO sustituye** la obligación del operador de
notificar a la ANPDP en ≤72h (Art. 17 Ley 7593/2025); es un canal técnico
complementario para que el operador pueda iniciar su propio proceso de
notificación a tiempo.

**Lectura clave:** el vendor proporciona **mecanismos**, el operador **los
configura y los ejecuta** ante la ANPDP. La responsabilidad legal del
tratamiento es **siempre** del operador frente al titular y frente a la
autoridad. El vendor responde por defectos técnicos en los mecanismos
provistos, no por cómo el operador los usa.

---

## 3. Derechos ARCO + mecanismos Odoo (D-14)

La Ley 7593/2025 establece los derechos **ARCO** del titular (Acceso,
Rectificación, Cancelación, Oposición) más Portabilidad y Consentimiento.
Cada derecho se mapea a un mecanismo Odoo concreto — built-in o módulo OCA
disponible en 18.0. Cuando no hay módulo OCA, se documenta el gap y el
proceso manual que el operador debe seguir.

| Derecho (Ley 7593)                | Mecanismo Odoo                                                                                                                                                                                     | Módulo OCA 18.0                                                                                      | Instrucción al operador                                                                                    |
| --------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Acceso (Art. 28)                  | Export estándar `res.partner` desde UI lista o Developer Mode (XLSX/CSV)                                                                                                                           | `base_export_anonymize` (control de acceso al export)                                                | Operador entrega export al titular en plazo legal (≤30 días, Art. 26); usar módulo OCA si necesita filtrar |
| Rectificación (Art. 29)           | Edit UI estándar — cualquier usuario con permiso `Contacts/Edit` puede corregir; `auditlog` registra el cambio (cross-ref [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §3 Audit logs) | — (se usa Odoo core + `auditlog`)                                                                    | Confirmar trazabilidad activa antes de aceptar el cambio; conservar log 7 años                             |
| Supresión / Cancelación (Art. 31) | Anonimización completa del `res.partner`: nombre, email, teléfono, RUC, avatar, chatter, users vinculados                                                                                          | **`privacy_partner_to_be_forgotten`** (módulo OCA 18.0 — ver §4 para módulos no disponibles en 18.0) | Instalar el módulo OCA; proceso iniciado por administrador con permiso explícito                           |
| Oposición (Art. 30)               | Campos `opt_out` / `opt_out_mailing` ya presentes en `res.partner` upstream (módulo `mass_mailing` de Odoo)                                                                                        | — (Odoo core)                                                                                        | Activar opt-out desde el portal del cliente o vía solicitud manual                                         |
| Portabilidad (Art. 32)            | Export XLSX/CSV de `res.partner` + facturas relacionadas vía Odoo Export                                                                                                                           | — (Odoo core)                                                                                        | Entregar paquete estructurado al titular (CSV legible por máquina, sin formato propietario)                |
| Consentimiento (Art. 6)           | Workflow de solicitud/respuesta de consentimiento por actividad de procesamiento (Art. 6 = condiciones de consentimiento válido)                                                                   | **`privacy_consent`**                                                                                | Instalar el módulo; configurar actividades; el vendor no captura consent en formularios                    |

**Notas sobre `privacy_partner_to_be_forgotten`** (módulo OCA 18.0.1.0.0,
repo `OCA/data-protection`):

- Anonimiza el `res.partner` reemplazando PII por valores genéricos
  (`name = "Anonymized"`, `email = NULL`, `phone = NULL`, `vat = NULL`, etc.).
- Desactiva (`active = False`) los `res.users` vinculados.
- Elimina avatar y mensajes del chatter asociado.
- Es **acción no reversible** — el operador debe confirmar la solicitud del
  titular por escrito y conservar la solicitud (no los datos borrados).
- **Es el módulo de cancelación/olvido vigente en OCA `data-protection` 18.0.**
  Módulos análogos de releases previas (con nombres tipo `*_purge`) **no están
  portados a la branch 18.0** y no deben documentarse como disponibles — usar
  exclusivamente `privacy_partner_to_be_forgotten`.

**Notas sobre `privacy_consent`** (módulo OCA 18.0.1.0.0):

- Define **actividades de procesamiento** (`data.processing.activity`) con
  base legal, finalidad y categorías de datos.
- Permite registrar consentimiento explícito del titular por actividad +
  versión del aviso de privacidad firmado.
- No captura el consentimiento desde un formulario web por sí mismo — el
  operador debe integrarlo con su propio frontend o portal de cliente.

**Gap explícito — `data_subject_access_request`:** este módulo OCA (presente
en versiones previas de Odoo) **NO está portado a 18.0**. El proceso formal
de solicitud de acceso del titular es responsabilidad del operador — workflow
manual (email → ticket → export → entrega) o desarrollo custom. Se rastrea
como TODO operador / Pre-Fase 4 en la matriz §5.

---

## 4. Módulos OCA disponibles en 18.0

Verificado contra `github.com/OCA/data-protection/tree/18.0` (auditado en
investigación de Phase 2, 2026-06-02). Solo **4 módulos** están portados a
Odoo 18.0:

| Módulo                            | Versión      | Propósito                                                                                          | Derecho cubierto                              | Estado deploy                  |
| --------------------------------- | ------------ | -------------------------------------------------------------------------------------------------- | --------------------------------------------- | ------------------------------ |
| `privacy_consent`                 | `18.0.1.0.0` | Consentimiento explícito por actividad de procesamiento; versionado de avisos                      | Consentimiento (Art. 6)                       | TODO operador                  |
| `privacy_partner_to_be_forgotten` | `18.0.1.0.0` | Anonimización completa de `res.partner` (nombre, email, teléfono, RUC, avatar, chatter, users)     | Cancelación / Right to be Forgotten (Art. 14) | TODO operador                  |
| `base_export_anonymize`           | `18.0.1.0.0` | Anonimiza ciertos campos durante export para grupos sin privilegio                                 | Acceso controlado (Art. 11)                   | TODO operador (si corresponde) |
| `privacy`                         | `18.0.1.0.0` | Framework base de actividades de procesamiento y registro de tratamiento (Art. 30 GDPR / Ley 7593) | Base de registros de tratamiento              | TODO operador                  |

**Módulos AUSENTES en OCA 18.0** (documentar como gap o usar alternativa):

| Módulo ausente                         | Reemplazo en 18.0                                              | Plan                                                     |
| -------------------------------------- | -------------------------------------------------------------- | -------------------------------------------------------- |
| Módulo de purga GDPR pre-17.0 (legacy) | `privacy_partner_to_be_forgotten` (funcionalmente equivalente) | Usar exclusivamente el módulo vigente en branch 18.0     |
| `data_subject_access_request`          | Sin reemplazo OCA — manual / custom                            | TODO operador / Pre-Fase 4 — workflow manual documentado |

**Instrucción de despliegue:** el operador agrega los módulos OCA que
necesite al `addons_path` de su instancia y los instala desde Apps. Este
proyecto **no declara dependencia hard** a estos módulos en `__manifest__.py`
porque (a) son responsabilidad del operador en deploy productivo, (b) no
todos los deployers necesitarán todos los módulos según el negocio.

---

## 5. Matriz de cumplimiento — Ley 7593/2025 (D-15)

Tabla final con el detalle artículo → control técnico → estado de
implementación. Esta es la vista panorámica para reviewers OCA y abogados
del cliente.

| Artículo Ley 7593/2025                   | Descripción                                                              | Control en docs/60                                                                                                                                    | Estado                                 |
| ---------------------------------------- | ------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------- |
| Art. 5 — Bases legales                   | Consentimiento / contrato / int. legítimo / obligación legal             | `privacy_consent` (OCA) — ver §3, §4                                                                                                                  | Documentado / TODO operador            |
| Art. 6 — Condiciones del consentimiento  | Consentimiento previo, libre, informado, inequívoco                      | `privacy_consent` (OCA) versiona aviso de privacidad firmado                                                                                          | Documentado / TODO operador            |
| Art. 28 — Acceso                         | Export datos del titular (plazo ≤30 días por Art. 26)                    | Odoo Export built-in + `base_export_anonymize` (OCA) — ver §3                                                                                         | Implementado (Odoo core)               |
| Art. 29 — Rectificación                  | Corrección + trazabilidad                                                | `auditlog` (OCA) — [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §3 Audit logs                                                            | Documentado / implementar Fase 2 EDI   |
| Art. 31 — Supresión / Cancelación        | Anonimización PII (right to be forgotten)                                | `privacy_partner_to_be_forgotten` (OCA) — ver §3, §4                                                                                                  | Documentado / TODO operador            |
| Art. 30 — Oposición                      | Opt-out de tratamiento                                                   | `opt_out` / `opt_out_mailing` (Odoo core)                                                                                                             | Responsabilidad operador               |
| Art. 32 — Portabilidad                   | Export estructurado (CSV/XLSX legible)                                   | Odoo CSV/XLSX export                                                                                                                                  | Responsabilidad operador               |
| Art. 17 — Breach notification            | 72h a ANPDP + titular                                                    | Proceso documentado en §2 (vendor → operador → ANPDP); cifrado en reposo [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §5 CCFE encryption | Documentado (no código)                |
| Art. 18 — DPO                            | Oficial de protección de datos                                           | N/A vendor — operador designa según reglamentación                                                                                                    | Responsabilidad operador               |
| Art. 19 — Transferencias internacionales | Adecuación de destino, cláusulas contractuales, consentimiento explícito | Documentado en §7 (ver lista de servicios externos típicos)                                                                                           | Documentado / responsabilidad operador |
| Arts. 14-15 — DPIA + consulta previa     | Evaluación de impacto + consulta a ANPDP si hay riesgo                   | N/A vendor — operador evalúa según reglamentación ANPDP                                                                                               | Responsabilidad operador               |
| Arts. 34-39 — ANPDP                      | Autoridad supervisora (creación + competencias + director)               | Notificación de brechas + canal oficial                                                                                                               | Documentado                            |
| **Gap — `data_subject_access_request`**  | Workflow formal de solicitud de acceso                                   | Sin módulo OCA en 18.0; usar Odoo Export manual                                                                                                       | **TODO operador / Pre-Fase 4**         |

**Leyenda de estados:**

- **Implementado:** el control existe en Odoo 18.0 community sin esfuerzo adicional.
- **Documentado:** este proyecto documenta el patrón / blueprint pero el código vive en otro módulo (Fase 2 EDI) o en el deploy real (Pre-Fase 3).
- **TODO operador:** el operador instala/configura el módulo OCA o ejecuta el proceso manual; el vendor no lo provee como dependencia hard.
- **Responsabilidad operador:** el deployer asume la obligación legal directa frente al titular o la ANPDP.
- **Pre-Fase 3 / Pre-Fase 4:** se difiere a una phase posterior cuando exista deploy real o el módulo OCA esté disponible.

---

## 6. Próximos pasos para el operador

Checklist mínimo antes del despliegue productivo en cliente real (alineado
con [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §1-§6):

1. **Designar DPO** según Art. 18 — registrar nombre y contacto ante la ANPDP cuando esté operativa.
2. **Instalar `privacy_consent` + `privacy_partner_to_be_forgotten`** en `addons_path` antes del primer cliente real (Pre-Fase 3).
3. **Configurar `auditlog`** sobre los modelos sensibles ([`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §3 lista de modelos): `res.partner`, `res.company`, `l10n_py.timbrado`, `l10n_latam.document.type`, `account.move`.
4. **Definir retention policy** específica por categoría de dato — base mínima 7 años para datos fiscales (Ley 125/91).
5. **Firmar contratos** con encargados (hosting VPS, proveedor de email) que procesen PII por cuenta del operador.
6. **Configurar canal de breach notification** interno: detección → vendor → ANPDP en ≤72h (Art. 17).
7. **Re-verificar el estado regulatorio** en 2027 cuando la Ley 7593/2025 entre en vigor — la ANPDP puede emitir reglamentación adicional entre 2026 y 2027 que ajuste detalles operativos.

---

## 7. Transferencias internacionales de datos

Cuando el operador deployea l10n-paraguay con servicios externos para backup,
monitoring, email, CI/CD u otros, los datos personales del titular pueden
salir del territorio paraguayo. Esto constituye **transferencia internacional
de datos personales** y está regulada por la **Ley 7593/2025 Art. 19**
(adecuación del destino, cláusulas contractuales modelo, consentimiento
explícito como base alternativa).

**Servicios externos típicos usados en deploys del proyecto:**

| Servicio                                      | Datos transferidos                                 | Jurisdicción típica       | Responsabilidad |
| --------------------------------------------- | -------------------------------------------------- | ------------------------- | --------------- |
| Backblaze B2 (backup offsite default §60.4)   | PII completa de la DB Odoo                         | US (East/West)            | Operador        |
| AWS S3 (alternativa premium §60.4)            | PII completa                                       | US/EU/global según región | Operador        |
| Gmail / Google Workspace (email del operador) | Direcciones de clientes en correos transaccionales | US                        | Operador        |
| GitHub (código + planning artifacts)          | Sin PII de clientes — solo código y docs           | US                        | Vendor          |
| Codecov (cobertura)                           | Sin PII — solo métricas                            | US                        | Vendor          |

**Obligaciones del operador (Art. 19):**

1. **Evaluar adecuación del destino:** verificar si el país donde reside el
   servicio es considerado "adecuado" por la ANPDP cuando publique su lista de
   países con nivel adecuado de protección.

2. **Implementar salvaguardas si el país NO es adecuado:**

   - Firmar **cláusulas contractuales modelo** equivalentes a las SCC del GDPR
     cuando la ANPDP las publique.
   - O obtener **consentimiento explícito e informado** del titular para la
     transferencia específica.
   - O recurrir a las excepciones del Art. 19 (cooperación judicial,
     operaciones bancarias, finalidad médica, etc.).

3. **Documentar las transferencias** en el registro de tratamiento del
   operador (mantenido vía OCA `privacy` — ver §4).

4. **Considerar alternativas con localización en PY** si el cliente exige
   residencia local de datos:
   - Hosting VPS en Paraguay (proveedores locales con datacenter en Asunción).
   - Backup S3-compatible en proveedor latinoamericano si está disponible.
   - Trade-off: costos típicamente más altos vs servicios internacionales.

**Estado de este proyecto:**

El vendor (este proyecto) **no realiza transferencias de PII de clientes
finales** — solo procesa código y docs en GitHub (US) y métricas en Codecov
(US). Las transferencias internacionales en deploys productivos son
**enteramente responsabilidad del operador** según la configuración que elija
(backup target, email provider, hosting).

> Cross-ref: [`docs/60_SECURITY_BASELINE.md`](60_SECURITY_BASELINE.md) §4
> documenta los backends de backup disponibles con sus pricings y
> jurisdicciones.

---

> **Nota:** Ley 6534/2020 ("De Protección de Datos Personales Crediticios") regula
> exclusivamente burós de crédito bajo supervisión del BCP. Su scope es datos
> financieros/crediticios — **no aplica** a los datos de clientes/facturas que
> maneja este proyecto. No confundir con Ley 7593/2025.

---

**Numbering verificado contra Ley 7593/2025 texto oficial publicado** en
[bacn.gov.py — Ley Nº 7593/2025](https://www.bacn.gov.py/leyes-paraguayas/12924/ley-n-7593-2025-de-proteccion-de-datos-personales-en-la-republica-del-paraguay)
y cross-validado contra el texto en baselegal.com.py (consulta: 2026-06-04).

**Cambios de numeración aplicados respecto a versión 1.0:** Derecho de acceso
Art. 11 → **Art. 28**; rectificación Art. 12 → **Art. 29**; cancelación/
supresión Art. 14 → **Art. 31**; oposición Art. 15 → **Art. 30**;
portabilidad Art. 16 → **Art. 32**; bases legales Art. 6 → **Art. 5**
(Art. 6 queda específico de condiciones del consentimiento). Art. 17
(notificación brecha 72h), Art. 18 (DPO) y Arts. 34-39 (ANPDP) ya estaban
correctos. Se agregaron: **Art. 19** (transferencias internacionales) y
**Arts. 14-15** (DPIA + consulta previa).

---

_Última revisión: 2026-06-04 (Phase 2 Bloque B — SEC-07, post-review)_
_Versión: 1.1_
