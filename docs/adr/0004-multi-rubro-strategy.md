---
status: accepted
date: 2026-06-10
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

### Análisis de Opción A — configuración por rubro en base

**Pros:**

- Menos módulos que mantener: toda la lógica en los módulos existentes `l10n_py_base`
  y `l10n_py_account`.
- Un solo punto de instalación para el instalador.

**Contras:**

- Viola el principio de aislamiento: `l10n_py_base` deja de ser instalable en
  cualquier rubro sin cargar asunciones específicas de industria.
- Lógica condicional creciente: `if company.industry_type == 'retail':` dispersa
  en modelos base introduce deuda técnica acumulativa.
- Anti-patrón OCA: los módulos de localización fiscal OCA (l10n-spain, l10n-brazil,
  l10n-ecuador) no incluyen asunciones de rubro en los módulos base — hacerlo
  dificultaría la eventual submission a `OCA/l10n-paraguay`.
- Tests acoplados: los tests del módulo base pasarían a depender de datos de rubro
  específicos, complicando el aislamiento del test runner.

### Análisis de Opción B — módulos `l10n_py_industry_*`

**Pros:**

- Extensibilidad por herencia `_inherit`: un módulo de rubro extiende `pos.config`,
  `product.template` y `res.config.settings` sin tocar el código base fiscal.
- Convención OCA `l10n_<country>_industry_<sector>`: naming establecido, facilita
  la búsqueda en el ecosistema OCA y la revisión por maintainers.
- Base testeable standalone: `l10n_py_base` y `l10n_py_account` pasan tests
  completos sin ningún módulo de rubro instalado.
- Terceros pueden agregar rubros nuevos publicando un módulo OCA independiente
  sin solicitar cambios al core.

**Contras:**

- Más módulos que mantener: cada rubro es un módulo con su propio manifest,
  README, tests y ciclo de release.
- Overhead de bootstrap por rubro: crear un módulo nuevo requiere setup inicial
  (estructura de directorios, manifest, hooks pre-commit).

## Decision Outcome

**Aceptado: Opción B.**

Los módulos `l10n_py_base` y `l10n_py_account` permanecen rubro-agnósticos. Los
rubros se implementan como módulos `l10n_py_industry_*` independientes que extienden
`l10n_py_pos`. El primer rubro concreto (`l10n_py_industry_retail`) se desarrolla
post Fase 6 OCA submission.

### Resultado de la auditoría de rubro-agnosticismo (IND-03, 2026-06-10)

Auditoría ejecutada el 2026-06-10 con el siguiente comando:

```bash
grep -ri "minimarket|gastronom|hospedaje|comercio|restaurante" addons/
```

Se encontraron **11 hits** (búsqueda case-insensitive `-i`, superset del comando
literal de IND-03 — el mismo comando case-sensitive arroja 9 de estos 11,
excluyendo «Gastronomía» con inicial mayúscula), clasificados en tres
categorías — todas aceptables, sin refactor necesario:

1. **Texto de documentación (descripción de cobertura por rubro):**

   - `addons/l10n_py_account/README.rst` líneas 50, 80, 81
   - `addons/l10n_py_account/readme/USAGE.rst` líneas 14, 15
   - `addons/l10n_py_account/readme/CONFIGURE.rst` línea 3
   - `addons/l10n_py_account/readme/CHANGES.rst` línea 6
     — Texto descriptivo que _describe_ el alcance por rubro ("Comercio minorista
     (minimarket, almacén): cobertura completa"). No es lógica condicional.

2. **Demo data con nombres canónicos del catálogo DNIT:**

   - `addons/l10n_py_base/data/l10n_py_economic_activity_demo.xml` líneas 6, 10
     — Nombres oficiales del catálogo DNIT de actividades económicas ("Venta al
     por menor de artículos de almacén (minimarkets)", "Actividades de restaurantes
     y servicio móvil de comidas"). Son datos del catálogo regulatorio, no
     asunciones del código.

3. **Fixture de test que referencia demo data:**
   - `addons/l10n_py_base/tests/test_company_setup.py` líneas 20, 35
     — Variable `activity_minimarket` referencia `l10n_py_base.economic_activity_1254`
     como dato de prueba arbitrario (el test no asume minimarket, usa esa actividad
     económica como un `res.partner` cualquiera para validar el modelo).

**Veredicto: rubro-agnosticismo confirmado.** Cero campos condicionales, cero
métodos con branching por rubro, cero dominios que filtren por tipo de industria
en los modelos base. Sin refactors necesarios, sin tech debt para `BUGS_BACKLOG.md`.

El roadmap operativo de los módulos `l10n_py_industry_*` está en
[`docs/80_MULTI_RUBRO_ROADMAP.md`](../80_MULTI_RUBRO_ROADMAP.md).

## Consequences

- `l10n_py_base` y `l10n_py_account` permanecen rubro-agnósticos — instalables en
  cualquier PyME sin dependencia de un rubro específico.
- Cada rubro es un módulo OCA independiente: `l10n_py_industry_retail`,
  `l10n_py_industry_hospitality`, `l10n_py_industry_services`, etc.
- Un rubro nuevo no requiere modificar el código base — solo crear un nuevo módulo
  `l10n_py_industry_*` con `_inherit` sobre `l10n_py_pos`.
- El primer rubro real (`l10n_py_industry_retail`) no se desarrolla hasta después
  de Fase 6 OCA submission — explícito en `docs/80_MULTI_RUBRO_ROADMAP.md` y
  `docs/55_PRE_FASE_2_FOUNDATION.md`.
