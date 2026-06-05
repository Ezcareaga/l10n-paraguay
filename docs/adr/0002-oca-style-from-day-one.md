# ADR-0002: Convenciones OCA desde el día uno

**Status:** Accepted
**Date:** 2026-05-19
**Refs:** [`docs/20_OCA_GUIDELINES.md`](../20_OCA_GUIDELINES.md), [`docs/21_OCA_DEVELOPMENT_BOOK.md`](../21_OCA_DEVELOPMENT_BOOK.md)

## Context

El objetivo final del proyecto es publicar los módulos en `OCA/l10n-paraguay`.
OCA mantiene un conjunto de convenciones estrictas para todos sus repositorios:
naming `l10n_*` con prefijo de país, manifests con `author` terminando en
`, Odoo Community Association (OCA)`, licencia AGPL-3 obligatoria en el manifest,
estructura de `readme/` con fragmentos RST (`DESCRIPTION.rst`, `USAGE.rst`,
`CONTRIBUTORS.rst`, `CREDITS.rst`, `CHANGES.rst`) que el hook `oca-gen-addon-readme`
convierte en `README.rst`. Adoptar estas convenciones desde el primer commit evita
una refactorización costosa al momento de la submission, y permite usar las
herramientas OCA de CI (`oca/maintainer-tools`, `oca/pre-commit-hooks`) desde el
inicio.

## Decision

Adoptar las convenciones OCA desde el día uno: naming `l10n_py_*`, manifests
OCA-compliant (campo `author` terminando en `, Odoo Community Association (OCA)`,
`license: AGPL-3`), estructura `readme/` con fragmentos RST, hook
`oca-gen-addon-readme` activado en pre-commit. Todo el tooling de CI sigue el
stack OCA (`ghcr.io/oca/oca-ci/py3.10-odoo18.0:latest`).

## Consequences

- Submission futura a OCA requiere mínimo o nulo trabajo de reformateo.
- El hook `oca-gen-addon-readme` regenera `README.rst` automáticamente al modificar
  fragmentos — mantiene la documentación sincronizada sin esfuerzo manual.
- El CI usa la imagen OCA (Python 3.10, PostgreSQL 12), que puede diferir del
  entorno local de desarrollo (Python 3.11+, PostgreSQL 15+) — diferencias
  documentadas en `CONTRIBUTING.md`.
- El campo `author` con la firma OCA es un commitment implícito de calidad y
  proceso de revisión; no puede usarse en módulos propietarios derivados.
