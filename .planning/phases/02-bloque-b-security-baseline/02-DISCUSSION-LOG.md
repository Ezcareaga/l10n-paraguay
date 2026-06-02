# Phase 2: Bloque B — Security baseline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-02 (resumed from 2026-05-28 checkpoint)
**Phase:** 02-bloque-b-security-baseline
**Areas discussed:** Workflow security.yml shape, SECURITY.md mecánica de reporte, docs/60 alcance + CCFE encryption, docs/61 alcance Ley 6534

---

## Workflow `security.yml` shape

| Option                                | Description                                                                                                                  | Selected |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- | -------- |
| 1 workflow, 3 jobs                    | Un `.github/workflows/security.yml` con gitleaks + bandit + dep-review como jobs paralelos. Visibilidad única en Actions UI. | ✓        |
| 3 workflows separados                 | Un archivo por tool. Logs aislados; más ruido en Actions tab.                                                                |          |
| 1 workflow, 1 job, steps secuenciales | Steps en serie en un job. Más lento; sin paralelismo.                                                                        |          |

**User's choice:** 1 workflow, 3 jobs (Recommended)
**Notes:** Encaja con triggers idénticos y status check único para branch protection.

---

| Option                                       | Description                                                | Selected |
| -------------------------------------------- | ---------------------------------------------------------- | -------- |
| Solo HIGH                                    | Solo Bandit HIGH falla la PR. MEDIUM/LOW se loguean.       | ✓        |
| HIGH + MEDIUM                                | Ambos fallan.                                              |          |
| HIGH falla; MEDIUM como comment en PR        | HIGH bloquea, MEDIUM se postea como PR comment.            |          |
| Solo HIGH ahora + reescalar post-l10n_py_edi | Empezar HIGH, escalar a MEDIUM cuando entre código crypto. |          |

**User's choice:** Solo HIGH (Recommended)
**Notes:** Baseline realista para estado actual del repo. Diferido escalación a Fase 2 EDI.

---

| Option                           | Description                                                        | Selected |
| -------------------------------- | ------------------------------------------------------------------ | -------- |
| SARIF al Security tab + logs     | Reports SARIF al Code scanning tab vía codeql-action/upload-sarif. | ✓        |
| Solo logs en Actions             | Output crudo, sin SARIF.                                           |          |
| SARIF + comment automático en PR | SARIF + bot comment. Ruido extra en PR.                            |          |

**User's choice:** SARIF al Security tab + logs (Recommended)
**Notes:** Consolida security state en GH; evita ruido de PR comments.

---

| Option                                | Description                                                | Selected |
| ------------------------------------- | ---------------------------------------------------------- | -------- |
| Diff PR + HEAD push, sin schedule     | Scan en cada PR contra origin/main y en push. Sin nightly. | ✓        |
| Diff PR + HEAD push + schedule weekly | + cron weekly.                                             |          |
| Solo scan completo en push a main     | Sin scan en PR.                                            |          |

**User's choice:** Diff PR + HEAD push, sin schedule (Recommended)
**Notes:** Overkill el nightly con 1 maintainer; el push detecta lo nuevo.

---

## SECURITY.md mecánica de reporte

| Option                                     | Description                                                           | Selected |
| ------------------------------------------ | --------------------------------------------------------------------- | -------- |
| GitHub Security Advisories + email         | Botón "Report a vulnerability" + email fallback careagaezz@gmail.com. | ✓        |
| Solo email + PGP opcional                  | Sin GH advisories, solo email.                                        |          |
| Email + tuta/protonmail dedicado security@ | Email separado con PGP.                                               |          |

**User's choice:** GitHub Security Advisories + email (Recommended)
**Notes:** Integrado con CVE issuance y Hall of Fame nativo.

---

| Option                                 | Description                                                                           | Selected |
| -------------------------------------- | ------------------------------------------------------------------------------------- | -------- |
| Generar PGP key + publicar fingerprint | GPG par (ed25519 o RSA 4096), public en keys.openpgp.org, fingerprint en SECURITY.md. | ✓        |
| Available on request                   | Mencionar PGP sin publicar fingerprint.                                               |          |
| Skip PGP                               | Sin PGP, TLS de GH suficiente.                                                        |          |

**User's choice:** Generar PGP key + publicar fingerprint (Recommended)
**Notes:** Compatible con futuro security.txt RFC 9116.

---

| Option                                                  | Description                               | Selected |
| ------------------------------------------------------- | ----------------------------------------- | -------- |
| Tabla inline en SECURITY.md                             | Sección ## Hall of Fame en mismo archivo. | ✓        |
| Archivo separado docs/SECURITY_HALL_OF_FAME.md          | Listado dedicado.                         |          |
| GH Security Advisories nativo (sin Hall of Fame propio) | Remitir a advisories publicados.          |          |

**User's choice:** Tabla inline en SECURITY.md (Recommended)
**Notes:** Cero entries hoy; migrar a archivo separado si crece >10.

---

| Option                          | Description                   | Selected |
| ------------------------------- | ----------------------------- | -------- |
| Latest minor de la serie 18.0.x | Solo última minor 18.0.x.     | ✓        |
| N + N-1 minor                   | Última + anterior con gracia. |          |
| Solo HEAD de main               | Bleeding edge.                |          |

**User's choice:** Latest minor de la serie 18.0.x (Recommended)
**Notes:** Alineado con Odoo 18.0 LTS y política OCA.

---

## docs/60 alcance + CCFE encryption

| Option                               | Description                                                          | Selected |
| ------------------------------------ | -------------------------------------------------------------------- | -------- |
| Strategy doc + commands ilustrativos | Eje por eje, qué + por qué + snippets marcados "validar Pre-Fase 3". | ✓        |
| Strategy doc solo (sin comandos)     | Decisiones high-level, sin snippets.                                 |          |
| Strategy doc + Odoo Mantra only      | Foco en config Odoo, sin infra.                                      |          |

**User's choice:** Strategy doc + commands ilustrativos (Recommended)
**Notes:** Blueprint reusable cuando llegue deploy real.

---

| Option                                          | Description                                  | Selected |
| ----------------------------------------------- | -------------------------------------------- | -------- |
| docs/60 describe; implementación es Fase 2 EDI  | Patrón documentado, código en `l10n_py_edi`. | ✓        |
| Implementar helper crypto ahora en l10n_py_base | Adelantar helper a base.                     |          |
| Skip CCFE encryption hasta Fase 2               | Mencionar sin describir.                     |          |

**User's choice:** docs/60 describe; implementación es Fase 2 EDI (Recommended)
**Notes:** Sin consumidor real, implementar crypto ahora sería scope creep.

---

| Option                                  | Description                                                     | Selected |
| --------------------------------------- | --------------------------------------------------------------- | -------- |
| OCA auditlog module + retention escrita | Usar OCA `auditlog` 18.0 + retention 7y/1y online (Ley 125/91). | ✓        |
| PostgreSQL audit (pgaudit / triggers)   | Audit a nivel DB.                                               |          |
| Decisión diferida a Pre-Fase 3          | Solo requirement, no el cómo.                                   |          |

**User's choice:** OCA auditlog module + retention escrita (Recommended)
**Notes:** Alineado con stack Odoo; retention basada en Ley 125/91 PY.

---

| Option                                                    | Description                                        | Selected |
| --------------------------------------------------------- | -------------------------------------------------- | -------- |
| S3-compatible (Backblaze B2 o similar) + filesystem local | Doble target con monthly restore test scripteable. | ✓        |
| Solo filesystem + rsync a VPS secundario                  | Sin cloud, mejor data residency.                   |          |
| Borg/restic genérico, vendor a definir en deploy          | Tool sin backend.                                  |          |

**User's choice:** S3-compatible + filesystem local (Recommended)
**Notes:** Vendor-neutral pero accionable; Backblaze B2 default por costo, AWS S3 si paga cliente.

---

## docs/61 alcance Ley 6534

| Option                                               | Description                      | Selected |
| ---------------------------------------------------- | -------------------------------- | -------- |
| Doc de responsabilidades split: vendor vs operador   | Tabla explícita vendor/operador. | ✓        |
| Doc completo asumiendo somos operador                | Sobre-asume rol.                 |          |
| Doc mínimo: solo qué datos personales toca el módulo | Listado PII + remitir a abogado. |          |

**User's choice:** Doc de responsabilidades split: vendor vs operador (Recommended)
**Notes:** Correcto legalmente: somos software vendor, no controlador.

---

| Option                                                | Description                          | Selected |
| ----------------------------------------------------- | ------------------------------------ | -------- |
| Documentar mecanismos disponibles en Odoo + qué falta | Mapeo ARCO → mecanismo Odoo + TODOs. | ✓        |
| Implementar consent capture ahora en l10n_py_base     | Campo nuevo en partner.              |          |
| Solo listado de derechos sin mapeo a Odoo             | Sin accionabilidad.                  |          |

**User's choice:** Documentar mecanismos disponibles en Odoo + qué falta (Recommended)
**Notes:** Consent capture es responsabilidad operador (formulario web propio); diferido.

---

| Option                                            | Description                                                      | Selected |
| ------------------------------------------------- | ---------------------------------------------------------------- | -------- |
| Linking explícito + matriz de cumplimiento        | Matriz "art Ley → control docs/60 → estado" al final de docs/61. | ✓        |
| Linking mínimo, sin matriz                        | Solo links inline.                                               |          |
| Linking diferido a docs/70 ARCHITECTURE (Phase 3) | Sin cross-refs hoy.                                              |          |

**User's choice:** Linking explícito + matriz de cumplimiento (Recommended)
**Notes:** Vista panorámica de gaps; útil para reviewers OCA y abogado del cliente.

---

## Claude's Discretion

Items que el researcher/planner resuelve sin reabrir discuss:

- Versión exacta de gitleaks-action / bandit / dependency-review-action pins.
- Texto literal de LICENSE AGPL-3.0 (canonical de gnu.org).
- Estructura de secciones SECURITY.md (template GitHub).
- Mecánica exacta del rotation script CCFE outline.
- Lista exacta de modelos a auditar para D-11 (review con codegraph).
- Disponibilidad del módulo OCA `auditlog` / `data_protection` / `gdpr_purge` en 18.0.
- Confirmar disponibilidad del módulo `gdpr_purge` para D-14 cancelación.

## Deferred Ideas

- Implementación real del Fernet helper CCFE → Fase 2 EDI.
- Escalación Bandit a MEDIUM → post-Fase 2 EDI.
- `.well-known/security.txt` RFC 9116 → Phase 4 o Pre-Fase 3.
- Schedule weekly de gitleaks → Pre-Fase 3 si hay señal.
- Migrar Hall of Fame a archivo separado → cuando >10 entries.
- Consent capture form en Odoo → Fase 4 POS o Fase 5.
- VPS / Caddy / Postgres prod provisioning → Pre-Fase 3.
- Implementar `scripts/restore-smoke.sh` ejecutable → Pre-Fase 3.
- Revisar pricing Backblaze B2 vs AWS S3 con datos reales → Pre-Fase 3.
- DPO designation + contratos encargados → responsabilidad operador / Pre-Fase 3.
