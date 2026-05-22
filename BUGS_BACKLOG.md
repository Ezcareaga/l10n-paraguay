# Bugs / mejoras pendientes (no bloqueantes)

Bugs colaterales detectados durante el trabajo en otras tareas. Cada entrada
incluye: descripción, dónde se detectó, impacto, y solución sugerida.

## #1 — `infra/docker-compose.yml` monta todo el repo (incluyendo `references/`)

**Detectado:** 2026-05-22, sesión de verificación Docker post-reinstalación WSL.

**Síntoma:** Odoo 18 tarda ~2 minutos desde "Watching addons folder" hasta
arrancar el HTTP server. Causa: el compose monta `..:/mnt/extra-addons/l10n-paraguay`
(el repo entero), por lo que Odoo escanea recursivamente `references/odoo-18.0/`
(151 MB), `references/l10n-brazil/` (32 MB) y otros buscando `__manifest__.py`.

**Riesgo adicional:** si algún manifest dentro de `references/` se llegara a
cargar como módulo de cliente, podría romper el setup o cargar modelos de otra
localización.

**Solución propuesta:**

Opción A (recomendada): crear `addons/` en el root y montar solo esa carpeta:

```yaml
volumes:
  - ../addons:/mnt/extra-addons/l10n-paraguay
```

Mover los futuros `l10n_py_base/`, `l10n_py_account/`, etc. dentro de `addons/`.

Opción B: dejar el monte amplio pero agregar `--load-language=es_PY` y mantener
disciplinadamente `references/` fuera de cualquier carpeta nombrada como módulo.
Más frágil.

**Status:** anotado, no bloqueante para Fase 1 (todavía no creamos ningún
módulo `l10n_py_*`).
