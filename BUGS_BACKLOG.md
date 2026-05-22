# Bugs / mejoras pendientes (no bloqueantes)

Bugs colaterales detectados durante el trabajo en otras tareas. Cada entrada
incluye: descripción, dónde se detectó, impacto, y solución sugerida.

## #1 — `infra/docker-compose.yml` montaba todo el repo (RESUELTO 2026-05-22)

**Detectado:** 2026-05-22, sesión de verificación Docker post-reinstalación WSL.
**Resuelto:** 2026-05-22, mismo día.

**Síntoma original:** Odoo 18 tardaba ~140s desde "Watching addons folder"
hasta arrancar el HTTP server. Causa: el compose montaba `..:/mnt/extra-addons/l10n-paraguay`
(el repo entero), por lo que Odoo escaneaba recursivamente `references/odoo-18.0/`
(151 MB), `references/l10n-brazil/` (32 MB) y otros buscando `__manifest__.py`.

**Riesgo adicional:** si algún manifest dentro de `references/` se llegara a
cargar como módulo de cliente, podría haber roto el setup o cargado modelos
de otra localización.

**Solución aplicada (opción A):** se creó `addons/` en el root del repo y
el compose ahora monta solo esa carpeta:

```yaml
volumes:
  - ../addons:/mnt/extra-addons/l10n-paraguay
```

Los futuros `l10n_py_base/`, `l10n_py_account/`, etc. van dentro de `addons/`.

**Verificación:** boot pasó de ~140s a **4s** (35× más rápido). Odoo ahora
loggea correctamente "Registry loaded in 1.4s" — antes ni alcanzaba esa fase.
