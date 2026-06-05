# Arquitectura — l10n-paraguay

**Estado:** diseño objetivo (Fase 2 EDI pending)
**Vigencia:** actualizar al mergear cada phase que cambie la arquitectura
**Cross-ref:** [`docs/50_MODULES_ROADMAP.md`](50_MODULES_ROADMAP.md) (módulos planned/shipped),
[`docs/03_DOMAIN_MODEL.md`](03_DOMAIN_MODEL.md) (modelo de dominio detallado)

---

## Alcance del documento

Este documento describe la arquitectura del sistema `l10n-paraguay` en dos
niveles: contexto (actores externos y sistemas) y contenedores (módulos y sus
dependencias). Los diagramas de emisión FE y ciclo de vida DTE están etiquetados
como **"diseño objetivo — Fase 2 EDI"** porque el módulo `l10n_py_edi` aún no
existe — sirven como especificación de entrada para esa fase.

Para el modelo de dominio detallado y los casos de uso, ver
[`docs/03_DOMAIN_MODEL.md`](03_DOMAIN_MODEL.md) y
[`docs/04_USE_CASES.md`](04_USE_CASES.md). Este documento es la vista de alto
nivel; no duplicar el detalle de esos docs.

---

## 1. Contexto del sistema (C4 Context)

```mermaid
C4Context
  title Sistema — l10n-paraguay (diseño objetivo Fase 2 EDI)

  Person(operator, "Operador PyME", "Cajero / contador / dueño que crea facturas y gestiona DTEs")
  System(odoo, "Odoo 18 Community + l10n_py_*", "ERP con facturación electrónica para Paraguay")
  System_Ext(sifen, "SIFEN / DNIT", "Plataforma de facturación electrónica nacional del Ministerio de Hacienda")
  System_Ext(set, "SET / Marangatú", "Gestión tributaria: timbrado, certificados CCFE, validación de contribuyentes")
  System_Ext(bank, "Bancos / Medios de pago", "Integración de cobro (futuro — Fase n)")

  Rel(operator, odoo, "Crea facturas, consulta estado DTEs, gestiona catálogos")
  Rel(odoo, sifen, "Envía XML firmado XAdES via SOAP / consulta estado DTE", "HTTPS/SOAP")
  Rel(odoo, set, "Obtiene timbrado vigente / valida CCFE / consulta RUC", "HTTPS")
  Rel(odoo, bank, "Integración de pagos (Fase futura)", "API")
```

---

## 2. Contenedores (C4 Container)

Los módulos `l10n_py_base` y `l10n_py_account` están **shipped** y en `main`.
Los cuatro módulos restantes son **planned** para Fase 2 y posteriores.

```mermaid
C4Container
  title Contenedores — l10n-paraguay

  Person(operator, "Operador PyME", "")

  Container_Boundary(odoo_sys, "Odoo 18 Community") {
    Container(base_mod, "l10n_py_base", "Python / Odoo addon", "Catálogos SIFEN/DNIT, validación RUC/CI (módulo 11), res.company PY fiscal. Versión: 18.0.1.1.0 [shipped]")
    Container(account_mod, "l10n_py_account", "Python / Odoo addon", "Plan de cuentas RG 49/14, IVA taxes, tipos de documento, timbrado, secuencias por tipo. Versión: 18.0.1.0.0 [shipped]")
    Container(edi_mod, "l10n_py_edi", "Python / Odoo addon", "XML SIFEN, firma XAdES, cliente SOAP DNIT, CDC, KuDE, eventos cancelación/inutilización. [planned — Fase 2]")
    Container(reports_mod, "l10n_py_reports", "Python / Odoo addon", "Libros IVA, Hechauka, RG90. [planned]")
    Container(pos_mod, "l10n_py_pos", "Python / Odoo addon", "POS integrado con SIFEN (factura en punto de venta). [planned]")
    Container(withholding_mod, "l10n_py_withholding", "Python / Odoo addon", "Retenciones IVA / IRE / IRP. [planned]")

    Container(latam_base, "l10n_latam_base", "OCA addon", "Tipos de identificación y modelos latam base (dependencia OCA)")
    Container(latam_invoice, "l10n_latam_invoice_document", "OCA addon", "l10n_latam.document.type, número de documento latam (dependencia OCA)")
  }

  Rel(operator, base_mod, "Configura empresa, carga catálogos")
  Rel(operator, account_mod, "Crea facturas, gestiona timbrado")
  Rel(operator, edi_mod, "Emite / consulta DTEs (Fase 2)")
  Rel(base_mod, latam_base, "depends_on")
  Rel(account_mod, latam_invoice, "depends_on")
  Rel(account_mod, base_mod, "depends_on")
  Rel(edi_mod, account_mod, "depends_on")
  Rel(reports_mod, edi_mod, "depends_on")
  Rel(pos_mod, edi_mod, "depends_on")
  Rel(withholding_mod, account_mod, "depends_on")
```

---

## 3. Secuencia de emisión FE (diseño objetivo — Fase 2 EDI)

> **Nota:** Este esquema describe el flujo **cuando `l10n_py_edi` exista**.
> Hoy el módulo no existe. Es la especificación de entrada para Fase 2 EDI.

```mermaid
sequenceDiagram
    participant Op as Operador PyME
    participant Odoo as Odoo 18 + l10n_py_edi
    participant XML as XML Builder (services/)
    participant Signer as XAdES Signer (services/)
    participant SIFEN as SIFEN / DNIT

    Note over Op,SIFEN: Diseño objetivo — Fase 2 EDI (l10n_py_edi no existe aún)

    Op->>Odoo: Confirmar factura (action_post)
    Odoo->>Odoo: Validar timbrado vigente + PoE activo
    Odoo->>XML: Generar XML DTE (grupos AA/A/B/C/D/E/F/H)
    XML-->>Odoo: XML DTE generado
    Odoo->>Signer: Firmar XML con CCFE (XAdES-BES)
    Signer-->>Odoo: XML firmado + CDC calculado
    Odoo->>SIFEN: Enviar XML via SOAP (rDE)
    SIFEN-->>Odoo: Respuesta: aprobado / rechazado / en proceso
    alt Aprobado
        Odoo->>Odoo: edi_state = sent, guardar CDC
        Odoo-->>Op: DTE aprobado, KuDE disponible
    else Rechazado
        Odoo->>Odoo: edi_state = error, guardar mensaje
        Odoo-->>Op: Error SIFEN — ver diagnóstico
    else En proceso
        Odoo->>Odoo: edi_state = to_send, reencolar
        Odoo-->>Op: Pendiente — cron reintentará
    end
```

---

## 4. Ciclo de vida del DTE (stateDiagram — diseño objetivo — Fase 2 EDI)

> **Nota:** Los estados `to_send`, `sent`, `error` y la transición de cancelación
> dependen de `l10n_py_edi` que se implementa en Fase 2. Los estados `draft` y
> `posted` ya existen en `account.move` estándar de Odoo.

```mermaid
stateDiagram-v2
    [*] --> draft : account.move creado
    draft --> posted : action_post() — validación timbrado/PoE
    posted --> to_send : action_send_and_print() — genera XML + firma
    to_send --> sent : SIFEN aprueba (edi_state=sent)
    to_send --> error : SIFEN rechaza (edi_state=error)
    error --> to_send : Reintento manual o cron
    sent --> cancelled : Evento de cancelación enviado a SIFEN
    posted --> cancelled : cancel_move_button() — sin EDI aún transmitido

    note right of sent
        Diseño objetivo — Fase 2 EDI
        (l10n_py_edi no existe aún)
    end note

    note right of to_send
        Diseño objetivo — Fase 2 EDI
        Cron de envío — plazo legal 72h
    end note
```

---

## Cross-references

- Módulos planned/shipped: [`docs/50_MODULES_ROADMAP.md`](50_MODULES_ROADMAP.md)
- Modelo de dominio (detalle): [`docs/03_DOMAIN_MODEL.md`](03_DOMAIN_MODEL.md)
- Casos de uso: [`docs/04_USE_CASES.md`](04_USE_CASES.md)
- Modelo de datos: [`docs/05_DATA_MODEL.md`](05_DATA_MODEL.md)
- Deployment blueprint: [`docs/71_DEPLOYMENT.md`](71_DEPLOYMENT.md)
- Runbook operacional: [`docs/72_RUNBOOK.md`](72_RUNBOOK.md)

---

_Documento creado en Phase 3 Pre-Fase 2 (Bloque C Documentación operacional).
Próxima revisión: al comenzar Fase 2 EDI, actualizar estado de l10n_py_edi de
"planned" a "shipped" y validar los diagramas de secuencia y estado contra la
implementación real._
