---
status: proposed
date: 2026-06-05
decision-makers: ["@Ezcareaga"]
---

# ADR-0005: Estrategia de hosting

## Context and Problem Statement

Los módulos `l10n_py_*` son software self-hosted. Las PyMEs paraguayas que los
adopten necesitan un entorno de producción con acceso confiable a SIFEN/DNIT (latencia
baja hacia servidores paraguayos), cumplimiento de Ley 7593/2025 (datos personales de
contribuyentes) y costo acorde a una PyME. ¿En qué infraestructura se despliega
Odoo Community + `l10n_py_*` para un cliente real?

## Decision Drivers

- **Costo:** presupuesto típico de una PyME paraguaya es bajo — VPS < EUR 10/mo es
  el techo razonable para el servidor Odoo.
- **Latencia hacia SIFEN/DNIT:** el servidor SOAP de DNIT está en Paraguay; latencia
  alta desde Europa puede provocar timeouts en la firma y envío de DTEs.
- **Soberanía de datos (Ley 7593/2025):** los datos de RUC, facturación y clientes
  son datos personales bajo la ley paraguaya — ver
  [`docs/61_COMPLIANCE_LEY_7593.md`](../61_COMPLIANCE_LEY_7593.md). Un datacenter
  en Paraguay o con acuerdo de adecuación es preferible.
- **Facilidad de backup offsite:** backup diario a almacenamiento S3-compatible
  (Backblaze B2 default per `docs/60_SECURITY_BASELINE.md` §Backup).
- **Simplicidad operacional:** el operador de una PyME no es sysadmin — el deploy
  debe ser reproducible con un `docker compose up`.

## Considered Options

### Opción A: Hetzner CX21 (Europa)

- **Precio:** ~EUR 3.79/mo (2 vCPU, 4 GB RAM, 40 GB NVMe, Frankfurt o Nürnberg)
- **Pros:** precio muy bajo, SLA 99.9%, snapshots automatizados disponibles, soporte
  IPv6, datacenter bien conocido en comunidad OCA/Odoo
- **Contras:** datacenter en Alemania — latencia hacia SIFEN ~180-220ms (aceptable
  para SOAP síncrono, pero introduce riesgo de timeout en picos DNIT); datos fuera
  de Paraguay requiere análisis Ley 7593/2025 con el cliente

### Opción B: Contabo VPS S (Europa)

- **Precio:** ~EUR 4.50/mo (4 vCPU, 8 GB RAM, 100 GB SSD, múltiples DCs europeos)
- **Pros:** más RAM y CPU por precio similar, plan generoso para Odoo con múltiples
  módulos
- **Contras:** mismas consideraciones de latencia y soberanía que Hetzner; menos
  transparencia en uptime histórico que Hetzner

### Opción C: Telecel Cloud (Paraguay)

- **Precio:** variable — consultar cotización (estimado USD 15-30/mo para VPS básico)
- **Pros:** datacenter en Paraguay — latencia < 10ms hacia DNIT/SIFEN; datos en
  territorio paraguayo (Ley 7593/2025 sin complejidad adicional); soporte local en
  español
- **Contras:** precio más alto; ecosistema de herramientas (backups, snapshots, API)
  menos maduro que Hetzner/Contabo; evaluación real pendiente Pre-Fase 3

## Decision Outcome

**Propuesto: sin proveedor comprometido.** La decisión final se toma en Pre-Fase 3
cuando exista un deploy real para un cliente concreto. El factor determinante será la
evaluación de Ley 7593/2025 con el cliente (proveedor local vs cláusulas de
transferencia internacional) y la latencia medida hacia DNIT desde cada opción.

Como referencia por defecto para documentación y scripts: Hetzner CX21 (Opción A)
por su relación precio/calidad y familiaridad en la comunidad Odoo — sin compromiso
de proveedor.

## Consequences

- No se commitea ningún archivo de configuración con dominio, IP o credenciales
  reales — todos los snippets en `docs/71_DEPLOYMENT.md` usan placeholders.
- La soberanía de datos bajo Ley 7593/2025 debe evaluarse caso a caso con cada
  cliente antes de elegir proveedor — ver
  [`docs/61_COMPLIANCE_LEY_7593.md`](../61_COMPLIANCE_LEY_7593.md).
- El backup offsite a Backblaze B2 (default en `docs/60_SECURITY_BASELINE.md`)
  no depende del proveedor VPS — funciona con cualquiera de las tres opciones.
- Si Pre-Fase 3 elige un proveedor, este ADR se actualiza a `Accepted` con la
  opción seleccionada y el razonamiento de la elección final.

## Cross-references

- Compliance datos personales: [`docs/61_COMPLIANCE_LEY_7593.md`](../61_COMPLIANCE_LEY_7593.md)
- Seguridad y backup: [`docs/60_SECURITY_BASELINE.md`](../60_SECURITY_BASELINE.md)
- Deployment blueprint: [`docs/71_DEPLOYMENT.md`](../71_DEPLOYMENT.md)
