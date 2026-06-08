---
status: proposed
date: 2026-06-05
decision-makers: ["@Ezcareaga"]
---

# ADR-0004: Estrategia multi-rubro

## Context and Problem Statement

Los módulos `l10n_py_base` y `l10n_py_account` deben funcionar para cualquier
industria paraguaya (minimarket, gastronomía, servicios, e-commerce). La audiencia
inicial son PyMEs con punto de venta físico, pero el diseño debe permitir extensiones
por rubro sin modificar el código base. ¿Cómo separamos las asunciones específicas de
cada rubro del código base de localización fiscal?

## Decision Drivers

- **Reutilización:** el código de localización fiscal (RUC, IVA, SIFEN) es idéntico
  para todos los rubros — no debe duplicarse.
- **Extensibilidad:** terceros deben poder agregar soporte para un rubro nuevo sin
  modificar `l10n_py_base` ni `l10n_py_account`.
- **Compatibilidad OCA:** la convención OCA para extensiones por industria es
  `l10n_<country>_industry_<sector>` — seguirla facilita la submission futura.
- **Aislamiento de complejidad:** los módulos base deben poder instalarse y pasar
  tests sin ningún módulo de rubro presente.

## Considered Options

- **Opción A:** Parámetros de configuración por rubro dentro de `l10n_py_base` /
  `l10n_py_account` (campos `industry_type` en `res.company`, lógica condicional
  en modelos base).
- **Opción B:** Módulos independientes `l10n_py_industry_*` que extienden
  `l10n_py_pos` mediante herencia Odoo (`_inherit`) y agregan la lógica específica
  del rubro (p. ej. `l10n_py_industry_retail`, `l10n_py_industry_hospitality`).

## Decision Outcome

**Propuesto: Opción B.** [Phase 5 IND-01 completa este análisis → status: Accepted]

Los módulos `l10n_py_base` y `l10n_py_account` permanecen rubro-agnósticos. Los
rubros se implementan como módulos `l10n_py_industry_*` independientes que extienden
`l10n_py_pos`. El primer rubro concreto (`l10n_py_industry_retail`) se desarrolla
post Fase 2 EDI.

Phase 5 (IND-01) auditará el código actual con `grep` para verificar que no existen
asunciones de rubro en base/account, y completará el análisis de pros/contras antes
de cambiar este ADR a `Accepted`.

## Consequences

- `l10n_py_base` y `l10n_py_account` permanecen rubro-agnósticos — instalables en
  cualquier PyME sin dependencia de un rubro específico.
- Cada rubro es un módulo OCA independiente: `l10n_py_industry_retail`,
  `l10n_py_industry_hospitality`, `l10n_py_industry_services`, etc.
- Un rubro nuevo no requiere modificar el código base — solo crear un nuevo módulo
  `l10n_py_industry_*` con `_inherit` sobre `l10n_py_pos`.
- La auditoría grep de Phase 5 puede revelar asunciones de rubro existentes que
  requieran refactoring antes de cerrar este ADR.
- El primer rubro real (`l10n_py_industry_retail`) no se desarrolla hasta después
  de Fase 2 EDI — explícito en `docs/55_PRE_FASE_2_FOUNDATION.md`.
