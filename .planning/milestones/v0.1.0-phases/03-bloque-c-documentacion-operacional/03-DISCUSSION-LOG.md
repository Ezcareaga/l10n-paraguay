# Phase 3: Bloque C — Documentación operacional - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-05
**Phase:** 3-bloque-c-documentaci-n-operacional
**Areas discussed:** README + idioma de docs raíz, Estrategia changelog, ARCHITECTURE + ADRs: formato, DEPLOYMENT + RUNBOOK: profundidad

---

## README + idioma de docs raíz

### Q1 — ¿En qué idioma escribimos los documentos de Phase 3?

| Option                                         | Description                                                                                                   | Selected |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------- | -------- |
| Inglés en raíz, español en docs/ (Recommended) | README/CONTRIBUTING/CoC/CHANGELOG en inglés (OCA-facing, cero retrabajo Fase 6); docs/70-72 + ADRs en español | ✓        |
| Todo español ahora                             | Consistencia total; migración a inglés como tarea explícita de Fase 6                                         |          |
| Todo inglés                                    | Máximo OCA-ready; rompe consistencia con ~25 docs en español                                                  |          |

**User's choice:** Inglés en raíz, español en docs/

### Q2 — ¿A quién le habla primero el README y cómo se estructura el quick start?

| Option                                                | Description                                                                                                                                     | Selected |
| ----------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| Estructura OCA-style: evaluador primero (Recommended) | qué es → tabla módulos estado real → installation → quick start compose → docs/ → delega dev a CONTRIBUTING (codegraph/references se mudan ahí) | ✓        |
| Contribuidor primero (evolución del actual)           | Mantener orientación dev + sumar compose y tabla actualizada                                                                                    |          |
| Dos tracks explícitos                                 | Secciones paralelas usar/contribuir con quick starts separados                                                                                  |          |

**User's choice:** Estructura OCA-style: evaluador primero

### Q3 — ¿El quick start del README usa qué docker-compose?

| Option                                               | Description                                                                                           | Selected |
| ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------- | -------- |
| Reusar el docker-compose.yml existente (Recommended) | clone → compose up → instalar módulos → login; es lo que DOC-10 smoke-testea; compose prod en docs/71 | ✓        |
| Compose de ejemplo separado para evaluadores         | examples/docker-compose.yml mínimo; duplica mantenimiento                                             |          |
| Solo link a DEPLOYMENT                               | README sin pasos inline; riesgo con criterio DOC-01                                                   |          |

**User's choice:** Reusar el docker-compose.yml existente

### Q4 — ¿Qué CODE_OF_CONDUCT adoptamos y arreglamos la colisión docs/60?

| Option                                                           | Description                                                                | Selected |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------- | -------- |
| Contributor Covenant 2.1 + renombrar retrospectiva (Recommended) | CC 2.1 + rename docs/60*FASE_1_RETROSPECTIVA.md → 65*\* actualizando links | ✓        |
| Contributor Covenant 2.1, numeración queda como está             | CC 2.1; colisión 60 como tech debt en BUGS_BACKLOG.md                      |          |
| OCA Code of Conduct boilerplate                                  | CoC oficial OCA; referencia canales OCA aún no integrados                  |          |

**User's choice:** Contributor Covenant 2.1 + renombrar retrospectiva

---

## Estrategia changelog

### Q1 — ¿Cómo conviven CHANGELOG.md, CHANGES.rst y los historiales per-addon?

| Option                                           | Description                                                                 | Selected |
| ------------------------------------------------ | --------------------------------------------------------------------------- | -------- |
| CHANGELOG.md reemplaza CHANGES.rst (Recommended) | Migrar skeleton, eliminar .rst; per-addon readme/HISTORY.rst convención OCA | ✓        |
| Convivir ambos en raíz                           | Dos archivos sincronizados a mano — más ceremonia                           |          |
| Solo per-addon, CHANGELOG.md mínimo              | Detalle en HISTORY.rst; raíz solo releases con links                        |          |

**User's choice:** CHANGELOG.md reemplaza CHANGES.rst

### Q2 — ¿Activamos el hook oca-gen-addon-readme en esta phase?

| Option                               | Description                                                                          | Selected |
| ------------------------------------ | ------------------------------------------------------------------------------------ | -------- |
| Sí, activar en Phase 3 (Recommended) | readme/ trees ya existen (condición Phase 1 cumplida); diff inicial en commit propio | ✓        |
| Diferir a Fase 6 OCA                 | No tocar pre-commit en phase de docs; riesgo drift fragments vs .rst                 |          |
| Regenerar manual una vez, sin hook   | Sincroniza hoy, no previene drift futuro                                             |          |

**User's choice:** Sí, activar en Phase 3

### Q3 — ¿Qué contiene la entry [0.1.0] del CHANGELOG?

| Option                                     | Description                                                                     | Selected |
| ------------------------------------------ | ------------------------------------------------------------------------------- | -------- |
| Todo hasta el tag de Phase 4 (Recommended) | Módulos Fase 1 + foundation Pre-Fase 2 en Added/Changed/Fixed; fecha al taggear | ✓        |
| Solo módulos; foundation queda Unreleased  | Literal al REQ pero el tag contendría cosas no documentadas                     |          |
| Subsecciones por módulo                    | Por módulo en vez de categorías Keep a Changelog                                |          |

**User's choice:** Todo hasta el tag de Phase 4

### Q4 — ¿Cómo se mantiene CHANGELOG.md después de Phase 3?

| Option                                          | Description                                              | Selected |
| ----------------------------------------------- | -------------------------------------------------------- | -------- |
| Compilar al release desde commits (Recommended) | Paso del release process (REL-06); cero fricción per-PR  | ✓        |
| Cada PR actualiza [Unreleased]                  | Máxima fidelidad Keep a Changelog; fricción + conflictos |          |
| Híbrido                                         | Features a mano, resto al release; frontera subjetiva    |          |

**User's choice:** Compilar al release desde commits

---

## ARCHITECTURE + ADRs: formato

### Q1 — ¿Con qué se dibujan los diagramas de docs/70?

| Option                   | Description                                                                      | Selected |
| ------------------------ | -------------------------------------------------------------------------------- | -------- |
| Mermaid (Recommended)    | Render nativo GitHub, texto versionable; C4 experimental, sequence/state maduros | ✓        |
| PlantUML + C4 stdlib     | C4 primera clase pero no renderiza en GitHub (PNGs commiteados)                  |          |
| Mermaid + ASCII fallback | Mermaid para sequence/state, ASCII para C4                                       |          |

**User's choice:** Mermaid

### Q2 — ¿Cómo trata docs/70 los módulos futuros?

| Option                                            | Description                                                                                  | Selected |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------- |
| Doc completo con estados explícitos (Recommended) | 6 módulos con marker shipped/planned; sequence FE + state DTE = "diseño objetivo Fase 2 EDI" | ✓        |
| Solo shipped + sección Future separada            | Cuerpo solo base+account; fragmenta visión end-to-end                                        |          |
| Referenciar docs/03-05 existentes                 | docs/70 delgado con links; REQ pide los 4 artefactos explícitos                              |          |

**User's choice:** Doc completo con estados explícitos

### Q3 — ¿Qué template usamos para los ADRs?

| Option                                      | Description                                              | Selected |
| ------------------------------------------- | -------------------------------------------------------- | -------- |
| Nygard clásico liviano (Recommended)        | Status/Context/Decision/Consequences; ideal retroactivos |          |
| MADR 4.0                                    | Template completo con Considered Options para todos      |          |
| Híbrido: Nygard retro + MADR para 0004/0005 | 0001-0003 Nygard; 0004/0005 MADR con opciones reales     | ✓        |

**User's choice:** Híbrido — Nygard para retroactivos, MADR para 0004/0005 (eligió contra la recomendación — decisión deliberada)

### Q4 — ¿Cómo maneja Phase 3 el ADR-0004 que pertenece a Phase 5?

| Option                                                   | Description                                                          | Selected |
| -------------------------------------------------------- | -------------------------------------------------------------------- | -------- |
| Stub Proposed en Phase 3, Phase 5 completa (Recommended) | Statement central + skeleton MADR; IND-01 completa y pasa a Accepted | ✓        |
| Phase 3 escribe 0004 completo                            | Vacía de contenido a IND-01; decide sin auditoría hecha              |          |
| Ejecutar Phase 5 en paralelo                             | parallelization=true sincronizando merge del ADR                     |          |

**User's choice:** Stub Proposed en Phase 3, Phase 5 completa

---

## DEPLOYMENT + RUNBOOK: profundidad

### Q1 — ¿Qué nivel de prescripción tiene docs/71_DEPLOYMENT.md?

| Option                                                 | Description                                                                                  | Selected |
| ------------------------------------------------------ | -------------------------------------------------------------------------------------------- | -------- |
| Blueprint estilo docs/60, compose inline (Recommended) | Patrón Phase 2 D-09: snippets + marker "validar en Pre-Fase 3"; compose prod como code block | ✓        |
| Compose prod commiteado (deploy/)                      | Archivos reales verificables pero sin consumidor hasta Pre-Fase 3                            |          |
| Paso-a-paso reproducible ya                            | Testeable en VM local; infla scope hacia deploy real                                         |          |

**User's choice:** Blueprint estilo docs/60, compose inline

### Q2 — ¿Cómo completamos la lista de incidentes del RUNBOOK?

| Option                                     | Description                                                                      | Selected |
| ------------------------------------------ | -------------------------------------------------------------------------------- | -------- |
| Los 5 del REQ + 5 propuestos (Recommended) | + timbrado vencido, DTE rechazado, restore falla, migration error, cola EDI >72h | ✓        |
| Researcher compila la lista                | Derivar de docs/01-02 + ÑandeFact; agrega un ciclo                               |          |
| Prefiero dictar la lista yo                | Incidentes específicos de la experiencia ÑandeFact                               |          |

**User's choice:** Los 5 del REQ + 5 propuestos

### Q3 — ¿Estructura de cada incidente y escalation path?

| Option                                             | Description                                                                                    | Selected |
| -------------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------- |
| Template fijo + escalation 3 niveles (Recommended) | Síntoma/Severidad/Diagnóstico/Resolución/Prevención; N1 operador → N2 Careaga Dev → N3 externo | ✓        |
| Formato libre por incidente                        | Estructura ad-hoc; menos uniforme bajo presión                                                 |          |
| Tabla compacta + detalle top 3                     | Resumen una línea + 3 procedimientos completos                                                 |          |

**User's choice:** Template fijo + escalation 3 niveles

### Q4 — ¿Cómo se ejecuta y registra el smoke test DOC-10?

| Option                                              | Description                                                                                  | Selected |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------- | -------- |
| Dev externo real + checklist en issue (Recommended) | Colega sin contexto sigue CONTRIBUTING; issue con checklist + fricciones; UAT item asíncrono | ✓        |
| Vos mismo en entorno limpio                         | VM limpia; sesgo del autor es lo que se quiere detectar                                      |          |
| Diferir al cierre del milestone                     | Smoke como parte del UAT del milestone completo                                              |          |

**User's choice:** Dev externo real + checklist en issue

---

## Claude's Discretion

- Número exacto del rename de la retrospectiva (65\_ u otro libre)
- Wording/secciones de CONTRIBUTING más allá de los 6 ejes + DOC-09 + migración README
- Estructura del checklist del issue DOC-10
- Opciones MADR del ADR-0005 hosting (vendor-neutral)
- Pin del hook oca-gen-addon-readme
- Orden de PRs/waves de la phase
- Badges adicionales del README (default: mantener los 6)

## Deferred Ideas

- Contenido completo ADR-0004 → Phase 5 (IND-01)
- Issue/PR templates, CODEOWNERS, release.yml, tag v0.1.0 → Phase 4
- Release process en CONTRIBUTING (semantic-release vs manual) → Phase 4 REL-06
- Deploy real + validación docs/71 → Pre-Fase 3
- restore-smoke.sh ejecutable → Pre-Fase 3
- Validación procedimientos SIFEN del runbook → Fase 2 EDI / homologación
- Migración docs/ españoles a inglés → Fase 6 OCA (si exigido)
- README.es.md traducción → post-OCA si la comunidad lo pide
