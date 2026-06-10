# Architecture Decision Records

Este directorio contiene los ADRs (Architecture Decision Records) del proyecto
`l10n-paraguay`.

---

## Formato híbrido

Este proyecto usa dos formatos de ADR según la naturaleza de la decisión:

| ADRs                     | Formato           | Criterio                                                    |
| ------------------------ | ----------------- | ----------------------------------------------------------- |
| 0001–0003 (retroactivos) | Nygard liviano    | Sin opciones consideradas honestas a posteriori             |
| 0004–0005 (prospectivos) | MADR con opciones | Opciones reales abiertas que un lector futuro debe entender |

**Por qué el híbrido (D-12):** Los ADRs 0001–0003 registran decisiones tomadas al
inicio del proyecto donde las alternativas no fueron comparadas formalmente — fabricar
una sección "Opciones consideradas" sería deshonesto y reduciría la credibilidad del
registro entero. Los ADRs 0004–0005 cubren decisiones prospectivas con alternativas
reales que aún no están cerradas; el formato MADR con su sección de opciones y
conductores de decisión es el apropiado.

---

## Índice

| ADR                                           | Título                                     | Formato        | Estado   | Decisor    |
| --------------------------------------------- | ------------------------------------------ | -------------- | -------- | ---------- |
| [0001](0001-odoo-community.md)                | Odoo Community Edition (no Enterprise)     | Nygard liviano | Accepted | @Ezcareaga |
| [0002](0002-oca-style-from-day-one.md)        | Convenciones OCA desde el día uno          | Nygard liviano | Accepted | @Ezcareaga |
| [0003](0003-dnit-catalogs-source-of-truth.md) | Catálogos DNIT/SIFEN como fuente de verdad | Nygard liviano | Accepted | @Ezcareaga |
| [0004](0004-multi-rubro-strategy.md)          | Estrategia multi-rubro                     | MADR           | Accepted | @Ezcareaga |
| [0005](0005-hosting-strategy.md)              | Estrategia de hosting                      | MADR           | Proposed | @Ezcareaga |

---

## Cómo agregar un ADR

Cualquier cambio a la estructura de módulos, diseño del modelo de datos o estrategia
de integración requiere un nuevo ADR en este directorio **en el mismo PR** (ver
`CONTRIBUTING.md` §Architectural changes).

1. Elegir el número siguiente (`0006-...`)
2. Si la decisión ya fue tomada y las alternativas no se pueden reconstruir honestamente
   → usar el template Nygard liviano (secciones: Context / Decision / Consequences)
3. Si hay alternativas reales abiertas → usar el template MADR (YAML frontmatter +
   Context and Problem Statement / Decision Drivers / Considered Options /
   Decision Outcome / Consequences)
4. Estado inicial: `Proposed` al abrir el PR; el maintainer lo cambia a `Accepted`
   al aprobar

---

## Cross-references

- Regla DOC-09: [`../CONTRIBUTING.md`](../../CONTRIBUTING.md) §Architectural changes
- Roadmap de módulos: [`../50_MODULES_ROADMAP.md`](../50_MODULES_ROADMAP.md)
- Spec multi-rubro (Phase 5): [`../55_PRE_FASE_2_FOUNDATION.md`](../55_PRE_FASE_2_FOUNDATION.md)
