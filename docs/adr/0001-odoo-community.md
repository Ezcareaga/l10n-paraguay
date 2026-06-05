# ADR-0001: Odoo Community Edition (no Enterprise)

**Status:** Accepted
**Date:** 2026-05-19
**Refs:** [`docs/00_OBJECTIVE.md`](../00_OBJECTIVE.md), [`docs/50_MODULES_ROADMAP.md`](../50_MODULES_ROADMAP.md)

## Context

Este proyecto construye módulos OCA-style (`l10n_py_*`) para la localización fiscal
de Paraguay sobre Odoo. El objetivo es publicar los módulos bajo AGPL-3 en OCA
(`OCA/l10n-paraguay`) para que cualquier PyME paraguaya pueda adoptarlos sin costo
de licencia. OCA publica exclusivamente módulos para Odoo Community Edition — los
módulos de la organización OCA deben ser compatibles con Community y licenciarse
bajo AGPL-3. La licencia propietaria de Odoo Enterprise es incompatible con AGPL-3:
distribuir un módulo AGPL-3 que dependa de módulos Enterprise viola la AGPL.

## Decision

Usar Odoo Community 18.0 como plataforma base. Todo el código de este repositorio
es AGPL-3. No se introducen dependencias de módulos Enterprise en ningún módulo
`l10n_py_*`.

## Consequences

- Compatible con la submission futura a `OCA/l10n-paraguay` (requirement de OCA).
- Sin costos de licencia para adopción por PyMEs paraguayas — alineado con el core
  value del proyecto.
- Los módulos Enterprise de contabilidad avanzada (p. ej. `account_reports` Enterprise)
  no están disponibles — no relevante para el scope de localización fiscal SIFEN.
- Las implementaciones Enterprise que requieran estos módulos deberán mantenerse como
  forks externos al repositorio OCA.
