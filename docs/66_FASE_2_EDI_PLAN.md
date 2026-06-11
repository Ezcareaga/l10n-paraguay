---
source: Generado por Claude Code (plan maestro Fase 2 — auditoría 2026-06-10 de addons/, account_edi Odoo 18, patrón l10n_ec_account_edi OCA 17.0 y brief SIFEN docs/01-02)
fetched_at: 2026-06-10
summary: Plan maestro ejecutable de la Fase 2 (l10n_py_edi MVP) — 9 paquetes de trabajo (1 paquete = 1 PR mergeable), decisiones de arquitectura corregidas contra Odoo 18 real, research pendiente por paquete y gates de validación.
priority: critical
---

# Fase 2 — `l10n_py_edi` MVP: Plan maestro

> **Para workers agénticos:** cada paquete PR-N se ejecuta con su propio plan
> detallado TDD (skill `superpowers:writing-plans` + subagent especializado)
> escrito inmediatamente antes de ejecutarlo, alimentado por la sección
> _Research pendiente_ del paquete. Este documento es el mapa, no el plan
> paso-a-paso de cada PR.

**Goal:** una FE creada en Odoo PY se postea, genera CDC + XML firmado XAdES,
se envía a SIFEN (test), recibe `0260`, y produce un KuDE con QR escaneable.
NC, cancelación e inutilización funcionan vía wizard.

**Arquitectura:** módulo OCA-style sobre el framework `account_edi` de Odoo 18
con el patrón **vigente** `_get_move_applicability()` → dict de callables
(NO `_post_invoice_edi`/`_cancel_invoice_edi`, obsoletos desde 17.0 — el
roadmap original docs/50 queda corregido por este plan). Servicios puros en
`services/` (testables sin Odoo, siguiendo el precedente de `modulo11.py` en
`l10n_py_base`). Blueprint de referencia: `l10n_ec_account_edi` (OCA Ecuador
17.0) — consultar siempre vía `bin/codegraph`, nunca Read directo.

**Tech stack:** Python 3.11, lxml, signxml, zeep, cryptography (Fernet +
PKCS#12), qrcode, requests-pkcs12.

---

## Decisiones de arquitectura (fijadas por la auditoría 2026-06-10)

| #   | Decisión                                                                                    | Razón                                                                                                                                                                                                                                      |
| --- | ------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| D1  | Usar `account.edi.format` + `account.edi.document` (framework core)                         | Sigue activo y mantenido en 18.0; aporta states (`to_send/sent/to_cancel/cancelled`), retry, batching y cron `ir_cron_edi_network` gratis. Ninguna community 18.0 lo usa, pero Ecuador OCA 17.0 (port a 18 en curso) es blueprint directo. |
| D2  | Patrón `_get_move_applicability(move)` → `{'post': ..., 'cancel': ..., 'edi_content': ...}` | Es el contrato real de Odoo 18 (`account_edi_format.py:71-81`). Los hooks del roadmap original están obsoletos.                                                                                                                            |
| D3  | XML con **lxml programático** (no templates QWeb como Ecuador)                              | El DE SIFEN tiene fuerte condicionalidad por grupo (iNatRec, moneda, NC vs FE); lxml puro es unit-testeable sin registry y valida XSD offline.                                                                                             |
| D4  | Firma con **signxml** (no `xades`+`xmlsig` como Ecuador)                                    | SIFEN exige XMLDSig enveloped RSA-SHA256 con Reference `#CDC`; signxml lo cubre y está mantenido. Ya decidido en docs/40.                                                                                                                  |
| D5  | mTLS con **requests-pkcs12** inyectado como transport de zeep                               | SIFEN exige TLS mutuo con el CCFE (Ecuador no lo necesita — es la diferencia principal con el blueprint). Fallback documentado: conversión .p12 → .pem temporal.                                                                           |
| D6  | CCFE en BD encriptado **Fernet**, key fuera de la BD                                        | Baseline docs/60. Campos en `res.company`, acceso solo vía service.                                                                                                                                                                        |
| D7  | Helpers puros en `l10n_py_edi/services/` importables sin registry Odoo                      | Precedente `modulo11.py`; permite tests unit rápidos + reuso futuro (POS, reports).                                                                                                                                                        |
| D8  | Envío MVP: `siRecepDE` síncrono primero; lote (`siRecepLoteDE`) detrás del mismo client     | El flujo síncrono simplifica homologación temprana; el cron de lotes entra en PR-6.                                                                                                                                                        |

## Estado de partida (qué ya existe y se consume tal cual)

- `company.l10n_py_active_timbrado_id` (timbrado 8 dígitos, single-active) y
  `journal.l10n_py_point_of_emission_id` (EEE-PPP + address).
- `move.name` con formato `EEE-PPP-NNNNNNN`, secuencia con scope por
  `l10n_latam_document_type_id` (códigos SIFEN 1/4/5/6/7 ya cargados).
- RUC + DV computed (`l10n_py_dv`, módulo 11) en company y partner;
  `l10n_latam.identification.type.l10n_py_sifen_code` (D208).
- `tax.l10n_py_afectacion_iva_id` (E731) y `move_line.l10n_py_iva_proporcion`.
- Base de tests `L10nPyAccountTestCase` (`addons/l10n_py_account/tests/common.py`)
  con company PY + chart + timbrado + PoE listos.
- CI: 4 workflows (test con tag `l10n_py`, pre-commit, security, commitlint).

## Paquetes de trabajo (1 paquete = 1 branch `feature/*` = 1 PR a `main`)

> Workflow por paquete: **research** (cerrar los gaps listados) → **plan
> detallado TDD** → **ejecutar** (subagent especializado, atomic commits) →
> **verificar** (tests + pre-commit + `verification-before-completion` +
> `code-reviewer`) → **PR + merge**. No se arranca un paquete con el anterior
> sin mergear, salvo que sean independientes (PR-2 y PR-3 pueden solaparse).

### PR-1 — Scaffold del módulo + certificado CCFE

**Files:** `addons/l10n_py_edi/{__manifest__.py,__init__.py}`,
`models/res_company.py`, `services/certificate.py`, `views/res_company_views.xml`,
`security/ir.model.access.csv`, `tests/{common.py,test_certificate.py,test_company_edi.py}`

- [ ] Manifest 18.0.1.0.0: depends `l10n_py_account`, `account_edi`;
      external_dependencies python: lxml, signxml, zeep, cryptography, qrcode, requests_pkcs12
- [ ] `res.company`: `l10n_py_edi_environment` (selection test/prod),
      `l10n_py_ccfe_certificate` (Binary encriptado), `l10n_py_ccfe_password`
      (encriptado), `l10n_py_csc`, `l10n_py_csc_id` — escritura solo vía
      método que encripta con Fernet (key desde `ir.config_parameter`/env var,
      según docs/60)
- [ ] `services/certificate.py`: load PKCS#12 (cryptography), validar vigencia,
      extraer RUC del subject (F110 SerialNumber / F211 SAN), exponer cert+key
      para firma y para mTLS
- [ ] `tests/common.py`: `L10nPyEdiTestCase(L10nPyAccountTestCase)` con
      certificado self-signed de fixture generado en setUp (nunca commitear .p12 real)
- [ ] Instalación limpia en `l10n_py_dev` sin warnings

**Research pendiente:** ninguno bloqueante. Verificar disponibilidad de
`requests-pkcs12` en la imagen OCA del CI (si no, agregar a requirements del workflow).

### PR-2 — Generador CDC

**Files:** `services/cdc.py`, `models/account_move.py`,
`tests/test_cdc.py`, `tests/test_account_move_cdc.py`

- [ ] `services/cdc.py` puro: `compose_cdc(...)` (43 dígitos desde tipo DE,
      RUC+DV, est, punto, número, tipo contribuyente, fecha YYYYMMDD, tipo
      emisión, código seguridad) + `cdc_check_digit()` = `modulo11.calculate_dv`
      con basemax=11 (pesos 2-11 — la mención "2-9" era un error de docs,
      corregido) + `generate_security_code()` (9 dígitos, `secrets`)
- [ ] Verificar contra el CDC ejemplo de docs/01 (`018006956310010030000137...9`)
- [ ] `account.move`: campos `l10n_py_cdc` (char 44, readonly, copy=False, indexed),
      `l10n_py_security_code`, `l10n_py_emission_type` (default normal);
      generación en `_post()` solo para doc types SIFEN; constraint de unicidad
- [ ] Regla de reutilización: si el DE fue rechazado y la corrección no toca
      campos del CDC → mismo CDC (no regenerar security code)

**Research cerrado 2026-06-11:** el DV del CDC usa basemax=11 (no 2-9 como
decían docs/01-02 — corregidos). Fix de mapping resto==1 aplicado a
`modulo11.calculate_dv` en l10n_py_base 18.0.1.1.1.

### PR-3 — XML builder del DE (FE + NC)

**Files:** `services/xml_builder.py`, `services/xml_constants.py` (códigos D/E),
`models/account_edi_xml.py` (mapper move→dict), `xsd/` (XSD oficiales),
`tests/test_xml_builder.py`, `tests/fixtures/*.xml` (golden files)

- [ ] Builder lxml: `<rDE>` ns `http://ekuatia.set.gov.py/sifen/xsd`, dVerFor 150,
      grupos: gOpeDE (AA), gTimb (A), gDatGralOpe (B/C/D: gEmis + gDatRec),
      gDtipDE (E: gCamFE + gCamItem repetible con gCamIVA), gTotSub (F)
- [ ] NC (tipo 5): grupo de referencia al CDC de la FE original
      (`move.reversed_entry_id.l10n_py_cdc`)
- [ ] Mapper Odoo separado del builder: el builder recibe dicts puros
      (unit-testeable), el mapper extrae de move/lines/taxes
      (afectación E731 + proporción)
- [ ] Validación XSD offline en tests (golden files FE simple, FE multi-item,
      FE exenta/mixta, NC)
- [ ] Casos condicionales: receptor contribuyente vs no contribuyente vs
      innominado; moneda PYG (sin tipo cambio) — moneda extranjera queda fuera del MVP si el XSD lo permite

**Research pendiente:** descargar XSD oficiales vigentes desde
`https://ekuatia.set.gov.py/sifen/xsd/` (docs/original/xsd está incompleto —
gap #4/#7); confirmar nombres exactos de grupos E contra el XSD real (el brief
salió de docs/02 que resume, no normativa).

### PR-4 — Firmador XAdES

**Files:** `services/xmldsig.py`, `tests/test_xmldsig.py`

- [ ] Firma enveloped con signxml: RSA-SHA256, digest SHA-256,
      Reference URI=`#<CDC>`, KeyInfo X509Certificate, posición del nodo
      Signature según XSD (dentro de `<rDE>`, después del DE)
- [ ] Canonicalization configurable (exclusive vs inclusive C14N) — default según research
- [ ] Tests: firma con cert fixture y verificación independiente
      (signxml.XMLVerifier + openssl CLI si disponible); firma estable tras
      serialización (no romper el digest al re-serializar)

**Research pendiente (BLOQUEANTE):** canonicalization exacta que acepta SIFEN
(gap #3) — buscar en Manual Técnico v150, WSDL de siRecepDE y proyectos open
source que ya homologaron (facturasend, librerías PHP/Node SIFEN en GitHub,
`references/nandefact`).

### PR-5 — Cliente SOAP SIFEN

**Files:** `services/sifen_client.py`, `services/sifen_endpoints.py`,
`tests/test_sifen_client.py`

- [ ] Client zeep con `Transport(session=requests_pkcs12 session)` para mTLS
- [ ] Operaciones: `send_de` (siRecepDE), `send_lote` (siRecepLoteDE: hasta 50
      DE mismo tipo, gzip + base64), `query_lote` (siResultLoteDE),
      `query_de` (siConsDE)
- [ ] Parser de respuestas → dataclass `SifenResponse(code, message, approved,
observations)`; mapping 0260/0261 aprobado, 03xx rechazo, 0361 en proceso,
      0362 concluido, 0364 extemporáneo
- [ ] Timeouts + manejo de errores de red (raise tipado, sin silenciar)
- [ ] Tests 100% mockeados (zeep client mock + respuestas reales de ejemplo
      tomadas de docs/02); cero red en suite estándar

**Research pendiente:** WSDLs reales (estructura exacta de request/response de
cada operación — descargar de sifen-test y versionar en `wsdl/` como Ecuador);
verificar si siRecepDE espera el XML como string o como nodo embebido.

### PR-6 — Integración `account_edi`

**Files:** `data/account_edi_data.xml`, `models/account_edi_format.py`,
`models/account_edi_document.py`, `data/ir_cron.xml`,
`tests/test_edi_flow.py`, `tests/test_edi_checks.py`

- [ ] Record `account.edi.format` code `py_dnit_sifen` + `_needs_web_services()
→ True` + `_is_compatible_with_journal()` (sale + PY + use_documents)
- [ ] `_check_move_configuration(move)`: RUC company, certificado cargado y
      vigente, timbrado activo y vigente a fecha de emisión, PoE en journal,
      partner con identificación válida, taxes con afectación E731
- [ ] `_get_move_applicability(move)` → `{'post': _l10n_py_post_de, 'cancel':
_l10n_py_cancel_de, 'edi_content': _l10n_py_render_xml}` solo para doc
      types 1 y 5 en sale
- [ ] `_l10n_py_post_de(invoices)`: CDC → XML → validar XSD → firmar → enviar
      (síncrono MVP) → attachment XML firmado + respuesta → chatter; respuesta
      del framework `{move: {'success': ..., 'attachment': ..., 'error': ...,
'blocking_level': ...}}`
- [ ] Modo lote: batching key por (company, doc type) + cron consulta lotes
      pendientes c/15 min (mínimo 10 entre consultas del mismo lote, deadline
      48h → fallback siConsDE)
- [ ] Tests: flujo post completo con SifenClient mockeado (aprobado, rechazado,
      timeout → retry), edi_state en move, attachments presentes

**Research pendiente:** ninguno nuevo (depende de PR-3/4/5 cerrados).

### PR-7 — Eventos: cancelación + inutilización

**Files:** `services/sifen_event_client.py`, `services/event_xml_builder.py`,
`wizards/{cancellation_wizard.py,inutilization_wizard.py}`, vistas de wizards,
`models/l10n_py_inutilization.py` (registro), `tests/test_events.py`,
`tests/test_wizards.py`

- [ ] XML de evento (`rEnvioEvento`/`rGesEve`) firmado con el mismo signer
- [ ] Wizard cancelación: solo DTE aprobado, motivo obligatorio, valida window;
      éxito → `edi_state` refleja cancelado + chatter
- [ ] Wizard inutilización: rango est/punto/desde/hasta + motivo; persiste en
      modelo `l10n_py.inutilization` para auditoría
- [ ] Tests con event client mockeado

**Research pendiente (BLOQUEANTE):** window oficial de cancelación (gap #2 —
48h vs ilimitado/según monto) y estructura exacta del XML de evento + su firma
(gap: Reference del evento ¿apunta a qué Id?).

### PR-8 — KuDE QWeb + QR

**Files:** `report/kude_report.xml`, `report/kude_templates.xml`,
`services/kude_qr.py`, `tests/test_kude_qr.py`, `tests/test_kude_render.py`

- [ ] `services/kude_qr.py`: URL e-Kuatia con nVersion/Id/dFeEmiDE/dRucRec/
      totales/cItems/DigestValue/IdCSC/cHashQR (hash con CSC concatenado)
- [ ] QWeb A4 con todos los elementos obligatorios (encabezado timbrado/CDC,
      items, totales por tasa, QR) — formato ticket queda para Fase 4 (POS)
      salvo que sea trivial compartir template
- [ ] Regla cardinal testeada: todo dato del KuDE existe en el XML firmado
- [ ] PDF adjunto al move al aprobarse; QR decodificable en test (qrcode +
      decode con zxing/pyzbar si disponible, sino assert de URL)

**Research pendiente (BLOQUEANTE):** algoritmo exacto de `cHashQR` (gap #1 —
Manual Técnico v150 sección QR; verificar contra implementación de referencia
nandefact/facturasend).

### PR-9 — Hardening + homologación-ready

- [ ] `ecc:security-review` + `security-auditor` (opus) sobre: Fernet/CCFE,
      logging (nunca loggear password/key), mTLS, inyección en XML (escaping lxml)
- [ ] Tests `@tagged('-standard', 'external', 'l10n_py')` contra sifen-test
      (skip limpio si no hay certificado configurado)
- [ ] Demo data + `readme/` fragments + oca-gen-addon-readme
- [ ] Docs: actualizar docs/50 (corrección patrón account_edi), nueva guía
      `docs/67_FASE_2_HOMOLOGACION.md` (pasos con DNIT), CHANGELOG
- [ ] Checklist de homologación del roadmap (docs/50:98-107) ejecutable

## Gates de validación (Definition of Done de la fase — de docs/50)

1. XML pasa validación XSD oficial offline ✅ (PR-3)
2. Firma verifica con OpenSSL externo ✅ (PR-4)
3. `sifen-test` devuelve 0260 para FE simple ✅ (PR-6, requiere CCFE de prueba)
4. Lote de 5 facturas aprobado vía consulta ✅ (PR-6)
5. Cancelación + inutilización aprobadas ✅ (PR-7)
6. KuDE con QR escaneable que resuelve en e-Kuatia ✅ (PR-8)
7. Tests con mocks 100% verdes sin red ✅ (todos)
8. Pre-commit + CI verdes en cada PR ✅ (todos)

> **Riesgo transversal:** los gates 3-6 dependen de conseguir el **CCFE de
> prueba** (trámite DNIT, fuera del control del código). Todo el desarrollo
> está diseñado para avanzar al 100% con mocks; los tests `external` se
> activan cuando el certificado exista.

## Orden y paralelismo

```
PR-1 ──► PR-2 ──┬──► PR-4 ──► PR-6 ──► PR-7 ──► PR-9
                │              ▲
                └──► PR-3 ─────┤
        PR-5 (independiente) ──┘        PR-8 (tras PR-6)
```

PR-2/PR-3 y PR-5 pueden desarrollarse en paralelo (worktrees) una vez mergeado PR-1.
