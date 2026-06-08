# ADR-0003: Catálogos DNIT/SIFEN como fuente de verdad

**Status:** Accepted
**Date:** 2026-05-19
**Refs:** [`docs/01_SIFEN_KNOWLEDGE_BASE.md`](../01_SIFEN_KNOWLEDGE_BASE.md)

## Context

Los módulos `l10n_py_base` y `l10n_py_account` requieren datos canónicos de la
DNIT: departamentos, distritos, ciudades, regímenes tributarios, tipos de
contribuyente, naturaleza del receptor, actividades económicas, tipos de documento,
y otros catálogos del Manual Técnico SIFEN v150. Estos datos son definidos y
versionados por la DNIT — no son de libre interpretación. La alternativa de
mantener los CSVs como datos hand-edited introduce riesgo de drift respecto al
Manual Técnico y dificulta auditar la fuente de cada valor.

## Decision

Los CSVs de datos maestros (`ir.model.data` / data XML) se generan programáticamente
desde el Manual Técnico SIFEN como fuente canónica. Los archivos CSV en
`addons/*/data/` no se editan a mano — se regeneran ejecutando los scripts en
`scripts/` cuando la DNIT actualiza el Manual Técnico. El script y su proceso están
documentados en `docs/01_SIFEN_KNOWLEDGE_BASE.md`.

## Consequences

- Un cambio en los catálogos DNIT requiere actualizar el Manual Técnico de referencia
  y regenerar los CSVs vía script — trazabilidad garantizada.
- Los CSVs commiteados en el repo son el output del script, no la fuente de verdad;
  modificarlos directamente sin regenerar introduce inconsistencias silenciosas.
- La auditoría de conformidad con el Manual Técnico es trivial: diff entre output
  del script y CSV commiteado debe ser vacío.
- Cuando la DNIT publique una nueva versión del Manual Técnico, el proceso de
  actualización es: actualizar fuente → ejecutar script → commitear CSVs regenerados.
