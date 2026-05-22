# `addons/` — Módulos Odoo de este repo

Esta carpeta es la **única** que Docker monta en `/mnt/extra-addons/l10n-paraguay/`
dentro del contenedor Odoo. Solo los módulos `l10n_py_*` viven acá.

## Por qué `addons/` y no el repo entero

Antes de 2026-05-22, el compose montaba `..` (el repo root) en
`/mnt/extra-addons/l10n-paraguay/`. Eso hacía que Odoo escaneara recursivamente
`references/` (151 MB de odoo-18.0/, 32 MB de l10n-brazil/, etc.) buscando
`__manifest__.py` — el boot del container tardaba ~2 minutos por eso, y existía
riesgo de que algún manifest dentro de `references/` se cargara como módulo de
cliente y rompiera el setup.

Aislando los módulos del proyecto en esta carpeta:

- Boot rápido (Odoo solo escanea lo nuestro)
- Imposible cargar accidentalmente un módulo de `references/`
- `references/` queda libre para consulta vía `bin/codegraph` sin afectar al
  runtime de Odoo

Ver `BUGS_BACKLOG.md` #1 para el historial completo del cambio.

## Estructura esperada (cuando estén creados)

```
addons/
├── README.md                     ← este archivo
├── l10n_py_base/                 ← Fase 1: plan de cuentas, RUC, regímenes
├── l10n_py_account/              ← Fase 2: doc types, timbrado, secuencias
├── l10n_py_edi/                  ← Fase 3: XML, firma, SOAP DNIT, CDC
├── l10n_py_reports/              ← Fase 4: Libro IVA, Hechauka, RG90
├── l10n_py_pos/                  ← Fase 5: POS con SIFEN
└── l10n_py_withholding/          ← Fase 6: retenciones IVA/IRE/IRP
```

El roadmap completo está en `docs/50_MODULES_ROADMAP.md`.

## Cómo agregar un módulo nuevo

1. Crear `addons/<nombre>/__manifest__.py` con metadata OCA standard.
2. Estructura mínima: `__init__.py`, `models/`, `views/`, `data/`, `security/`,
   `tests/`, `i18n/`, `README.rst`.
3. Reiniciar el contenedor Odoo para que detecte el manifest nuevo:
   ```powershell
   docker compose -f infra/docker-compose.yml restart odoo
   ```
4. Instalar desde Apps → Update Apps List → buscar el nombre.
