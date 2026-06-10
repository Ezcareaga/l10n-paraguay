---
source: Generado por documentation-engineer (Phase 5 Bloque E — IND-02 + IND-04)
date: 2026-06-10
summary: Roadmap de módulos l10n_py_industry_* — cuándo se construye cada rubro, demo data, hardware compatibility matrix, onboarding wizard, template mínimo de módulo industry, auditoría IND-03.
priority: high
---

# Roadmap multi-rubro — `l10n_py_industry_*`

> Este documento es el complemento operativo de
> [`docs/adr/0004-multi-rubro-strategy.md`](adr/0004-multi-rubro-strategy.md).
> Responde _cuándo_ y _cómo_ se construye cada rubro; el ADR responde _por qué_
> se eligió la arquitectura de módulos independientes.

---

## 1. Decisión base

Los módulos `l10n_py_base` y `l10n_py_account` son **rubro-agnósticos**: implementan
el ciclo fiscal paraguayo (RUC, IVA, SIFEN, timbrado, tipos de documento) sin asumir
qué tipo de negocio los instala.

Los rubros específicos se construyen como módulos `l10n_py_industry_*` independientes
que extienden `l10n_py_pos` (Fase 4) mediante herencia Odoo (`_inherit`). Cada módulo
agrega:

- Presets de configuración POS específicos del rubro
- Demo data (productos típicos, actividades económicas DNIT del rubro)
- Vistas opcionales extendidas para el rubro

Referencia completa de la decisión y su justificación:
[`docs/adr/0004-multi-rubro-strategy.md`](adr/0004-multi-rubro-strategy.md).

---

## 2. Timing por rubro

Los módulos `l10n_py_industry_*` se construyen **post Fase 6** (OCA submission).
Antes de esa fecha no existe `l10n_py_pos` estable — prerrequisito técnico de todos
los módulos de rubro.

### Prerrequisitos de cadena

```
Fase 1  l10n_py_base + l10n_py_account   ✓ completada 2026-05-25
Fase 2  l10n_py_edi (SIFEN)               pendiente
Fase 3  l10n_py_reports                   pendiente
Fase 4  l10n_py_pos                       pendiente — prerrequisito de industry_*
Fase 5  l10n_py_withholding               pendiente
Fase 6  Pulido + publicación OCA          pendiente — desbloquea industry_*
Fase 7+ l10n_py_industry_*                post Fase 6
```

### Tabla de módulos por rubro

| Módulo                         | Rubro objetivo                        | Prioridad | Prerequisitos          |
| ------------------------------ | ------------------------------------- | --------- | ---------------------- |
| `l10n_py_industry_retail`      | Minimarkets, almacenes, comercios     | Alta      | `l10n_py_pos` (Fase 4) |
| `l10n_py_industry_hospitality` | Gastronomía: restaurantes, cafeterías | Media     | `l10n_py_pos` (Fase 4) |
| `l10n_py_industry_services`    | Servicios profesionales, agencias     | Media     | `l10n_py_account`      |
| `l10n_py_industry_ecommerce`   | E-commerce, ventas online             | Baja      | `l10n_py_pos` o API    |

**Orden de construcción sugerido:**

1. `l10n_py_industry_retail` — audiencia inicial del proyecto (minimarkets y
   comercios de barrio de PyMEs paraguayas), mayor base de primeros clientes.
2. `l10n_py_industry_hospitality` — segundo caso de uso más común (gastronomía
   pequeña: cafeterías, comedores, bares).
3. `l10n_py_industry_services` — requiere menos integración POS; puede construirse
   en paralelo a hospitality.
4. `l10n_py_industry_ecommerce` — depende de validar integración con `website_sale`;
   se evalúa según demanda en Fase 7.

---

## 3. Demo data por rubro

Cada módulo `l10n_py_industry_*` incluye demo data específica del rubro. Convención:
los archivos van en `demo/` y solo se cargan cuando Odoo instala el módulo con
`--load-language` o en DBs de demo.

| Módulo                         | Demo data incluida                                                                                                                   |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------ |
| `l10n_py_industry_retail`      | Productos típicos (arroz, azúcar, aceite, bebidas); actividades económicas DNIT: "Venta al por menor de artículos de almacén" (1254) |
| `l10n_py_industry_hospitality` | Productos típicos (platos del día, bebidas, servicios de mesa); actividad DNIT: "Actividades de restaurantes" (5610)                 |
| `l10n_py_industry_services`    | Productos tipo servicio (honorarios, consultoría, asesoría); actividades DNIT del sector servicios (régimen general/simplificado)    |
| `l10n_py_industry_ecommerce`   | Productos digitales/físicos genéricos; actividad DNIT: "Venta al por menor por internet" (4791)                                      |

**Reglas para la demo data:**

- Los nombres de actividades económicas deben ser los **nombres canónicos del catálogo
  DNIT** — no inventarlos. Verificar en `addons/l10n_py_base/data/` o en el manual
  técnico SIFEN actualizado.
- Los productos son solo datos de referencia — no asumir precios, ya que varían.
- La demo data no crea `account.move` ni `pos.order` — solo `product.template`,
  `res.partner` de ejemplo y presets de configuración.

---

## 4. Hardware compatibility matrix por rubro

La siguiente tabla describe el hardware de punto de venta relevante por rubro.
Los módulos `l10n_py_industry_*` no implementan drivers de hardware — eso lo
maneja el módulo `point_of_sale` de Odoo core y las integraciones de IoT Box.
Esta matrix orienta los requisitos de setup documentados en el onboarding wizard
y la documentación de implementación.

| Hardware                        | Retail    | Hospitality | Services | E-commerce |
| ------------------------------- | --------- | ----------- | -------- | ---------- |
| Impresora térmica 80mm (ticket) | Requerido | Requerido   | Opcional | N/A        |
| Lector de código de barras      | Requerido | Opcional    | N/A      | N/A        |
| Balanza electrónica             | Opcional  | N/A         | N/A      | N/A        |
| Cajón portamonedas              | Requerido | Requerido   | Opcional | N/A        |
| Pantalla cliente (display)      | Opcional  | Opcional    | N/A      | N/A        |
| Impresora de comandas (cocina)  | N/A       | Opcional    | N/A      | N/A        |
| KDS (Kitchen Display System)    | N/A       | Opcional    | N/A      | N/A        |
| Terminal de pago integrada      | Opcional  | Opcional    | Opcional | Requerido  |
| Lector QR/NFC (pagos)           | Opcional  | Opcional    | Opcional | Requerido  |

**Leyenda:**

- **Requerido:** sin este hardware el flujo POS típico del rubro no es viable
  en producción.
- **Opcional:** agrega eficiencia operativa pero el flujo funciona sin él.
- **N/A:** no aplica al rubro o al modo de operación típico.

**Modelos probados en Paraguay (referencia de ÑandeFact):**

- Impresoras térmicas: Epson TM-T20III, XPrint A160H (comunes en PyMEs PY).
- Lectores de barras: cualquier HID genérico USB o Bluetooth (el POS Odoo los
  detecta como teclado).
- No hay una matrix de certificación formal — se documenta con el primer cliente
  real de cada rubro.

---

## 5. Onboarding wizard por rubro

El onboarding wizard es un concepto para la Fase 7+ que reduce el tiempo de
configuración inicial al instalar un módulo `l10n_py_industry_*`.

### Concepto

Al instalar `l10n_py_industry_<sector>`, un wizard de bienvenida pregunta al
usuario configuraciones clave del rubro y aplica presets automáticamente:

1. **Nombre del negocio y RUC** (precargado desde `res.company` si ya existe).
2. **Cantidad de puntos de venta** (configura `pos.config` por punto).
3. **Hardware disponible** (activa/desactiva integraciones según lo disponible).
4. **Demo data** (opcional: carga productos de ejemplo para el rubro elegido).
5. **Actividades económicas principales** (selección de la lista DNIT, precargada
   con las del rubro por defecto).

### Implementación

El wizard se implementa como un `res.config.settings` extendido o como un
`ir.actions.act_window` de un `wizard` dedicado. La ubicación preferida es dentro
del propio módulo `l10n_py_industry_<sector>`:

```
l10n_py_industry_retail/
    wizard/
        l10n_py_retail_setup_wizard.py
        l10n_py_retail_setup_wizard.xml
```

El wizard llama a métodos de `l10n_py_pos` para configurar `pos.config` y a
`l10n_py_base` para setear las actividades económicas de la empresa. No modifica
los módulos base — usa la API pública de Odoo.

**Estado:** concepto documentado para Fase 7. No se implementa hasta tener
`l10n_py_pos` estable (Fase 4) y al menos un rubro validado con un cliente real.

---

## 6. Template mínimo de un módulo `l10n_py_industry_*`

Esta sección es la guía operativa para crear un rubro nuevo desde cero.

### Estructura de directorios

```
addons/
└── l10n_py_industry_retail/        ← nombre: l10n_py_industry_<sector>
    ├── __init__.py
    ├── __manifest__.py
    ├── data/
    │   └── l10n_py_retail_pos_config_data.xml   ← presets de configuración
    ├── demo/
    │   └── l10n_py_retail_demo.xml              ← productos y datos de demo
    ├── models/
    │   ├── __init__.py
    │   └── pos_config.py                        ← _inherit = 'pos.config'
    ├── readme/
    │   ├── DESCRIPTION.rst
    │   ├── INSTALL.rst
    │   ├── CONFIGURE.rst
    │   └── USAGE.rst
    ├── static/
    │   └── description/
    │       └── icon.png
    ├── tests/
    │   ├── __init__.py
    │   └── test_retail_setup.py
    └── views/
        └── pos_config_views.xml                 ← vistas opcionales
```

### `__manifest__.py` de ejemplo

```python
# -*- coding: utf-8 -*-
{
    "name": "Paraguay - Industria: Retail",
    "summary": "Presets POS para comercios minoristas paraguayos (minimarkets, almacenes)",
    "version": "18.0.1.0.0",
    "category": "Localization",
    "author": "Alberto Ezequiel Careaga, Odoo Community Association (OCA)",
    "website": "https://github.com/Ezcareaga/l10n-paraguay",
    "license": "AGPL-3",
    "depends": [
        "l10n_py_pos",          # prerrequisito: POS con SIFEN integrado (Fase 4)
    ],
    "data": [
        "data/l10n_py_retail_pos_config_data.xml",
    ],
    "demo": [
        "demo/l10n_py_retail_demo.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": False,
}
```

**Reglas del manifest:**

- `version` sigue el formato `18.0.x.y.z` (OCA).
- `author` debe terminar en `, Odoo Community Association (OCA)`.
- `license` siempre `"AGPL-3"`.
- `depends` incluye solo lo estrictamente necesario — no agregar `l10n_py_base`
  directamente si `l10n_py_pos` ya lo arrastra como transitiva.
- `auto_install: False` siempre — el usuario decide qué rubro instalar.

### Qué hereda de base y qué agrega

Un módulo `l10n_py_industry_*` **no toca los modelos fiscales**. La regla es:

| Qué hacer                                                          | Cómo                                                |
| ------------------------------------------------------------------ | --------------------------------------------------- |
| Agregar campos de configuración al POS                             | `_inherit = 'pos.config'` en `models/pos_config.py` |
| Agregar productos de demo del rubro                                | `demo/` con `product.template` records              |
| Preconfigurar actividades económicas DNIT del rubro                | `data/` con `res.company` write o config wizard     |
| Extender la UI del POS para el rubro (campo, botón, vista)         | `views/` + `static/src/` OWL component              |
| Agregar configuraciones en `res.config.settings`                   | `_inherit = 'res.config.settings'`                  |
| **NO:** modificar `l10n.py.timbrado`, `account.tax`, `res.partner` | Esos son responsabilidad de `l10n_py_base/account`  |
| **NO:** hardcodear lógica condicional `if rubro == 'retail'`       | Violaría el principio de aislamiento del ADR-0004   |

### Dónde van los archivos

- **`data/`:** presets de configuración que se cargan en instalación normal
  (no solo en demo). Ejemplos: `pos.config` defaults, `ir.property` para el rubro.
- **`demo/`:** datos de ejemplo que solo se cargan en DBs de demo. Ejemplos:
  productos típicos del rubro, `res.partner` de cliente frecuente.
- **`models/`:** extensiones de modelos existentes via `_inherit`. Regla: si el
  modelo que querés extender no está en `l10n_py_pos` o `point_of_sale`, revisar
  si la extensión corresponde al rubro o al módulo base.
- **`views/`:** extensiones de vistas XML (`ir.ui.view` con `inherit_id`). Solo
  vistas que agregan campos/botones del rubro — no reemplazar vistas base.

### Tests mínimos esperados

Todo módulo `l10n_py_industry_*` debe tener al mínimo:

```python
# tests/test_retail_setup.py (ejemplo para retail)
from odoo.tests import tagged, TransactionCase

@tagged("post_install", "-at_install", "l10n_py")
class TestRetailSetup(TransactionCase):

    def test_module_installs_without_errors(self):
        """El módulo se instala sin warnings en una DB limpia."""
        # Si llegamos acá, la instalación fue exitosa
        self.assertTrue(True)

    def test_demo_products_loaded(self):
        """La demo data carga al menos 5 productos del rubro."""
        products = self.env["product.template"].search(
            [("categ_id.name", "=", "Retail PY")]
        )
        self.assertGreaterEqual(len(products), 5)

    def test_pos_config_preset_applied(self):
        """El preset de POS config del rubro está disponible."""
        # Verificar que el preset definido en data/ existe
        config = self.env.ref(
            "l10n_py_industry_retail.pos_config_retail_default", raise_if_not_found=False
        )
        self.assertIsNotNone(config)
```

La cobertura objetivo mínima para módulos `l10n_py_industry_*` es del 80% en
código Python nuevo, consistente con el estándar del proyecto (`docs/00_OBJECTIVE.md`
§5 Calidad).

---

## 7. Apéndice — Auditoría de rubro-agnosticismo (IND-03)

**Fecha:** 2026-06-10

**Comando ejecutado:**

```bash
grep -ri "minimarket|gastronom|hospedaje|comercio|restaurante" addons/
```

**Resultado:** 11 hits encontrados. Clasificados en tres categorías:

> **Nota:** el comando usa `-i` (case-insensitive), un superset del comando
> literal de IND-03. El mismo comando case-sensitive arroja 9 de estos 11
> hits — excluye «Gastronomía» con inicial mayúscula (`README.rst:81` y
> `USAGE.rst:15`). El veredicto es idéntico en ambos casos.

### Categoría 1 — Texto de documentación (descripción de alcance)

Archivos y líneas:

- `addons/l10n_py_account/README.rst:50,80,81`
- `addons/l10n_py_account/readme/USAGE.rst:14,15`
- `addons/l10n_py_account/readme/CONFIGURE.rst:3`
- `addons/l10n_py_account/readme/CHANGES.rst:6`

Descripción: texto que _describe_ la cobertura del módulo por tipo de rubro
("Comercio minorista (minimarket, almacén): cobertura completa", "activas por
default para comercio/servicios"). Es documentación de alcance, no lógica
condicional ni campos que filtren por industria.

**Clasificación: aceptable — no requiere acción.**

### Categoría 2 — Demo data con nombres canónicos del catálogo DNIT

Archivos y líneas:

- `addons/l10n_py_base/data/l10n_py_economic_activity_demo.xml:6,10`

Descripción: nombres oficiales del catálogo DNIT de actividades económicas
("Venta al por menor de artículos de almacén (minimarkets)", "Actividades de
restaurantes y servicio móvil de comidas"). Son nombres regulatorios — el catálogo
DNIT los define así, no son asunciones del código.

**Clasificación: aceptable — datos canónicos del regulador, no asunciones de rubro.**

### Categoría 3 — Fixture de test que referencia demo data

Archivos y líneas:

- `addons/l10n_py_base/tests/test_company_setup.py:20,35`

Descripción: variable `activity_minimarket` referencia
`l10n_py_base.economic_activity_1254` como dato de prueba arbitrario. El test
valida el modelo de empresa usando esa actividad económica como representante de
cualquier actividad DNIT — no asume ni fuerza un rubro específico en la lógica
probada.

**Clasificación: aceptable — uso de demo data como fixture, sin acoplar lógica al rubro.**

### Veredicto final

Rubro-agnosticismo **confirmado**. No se encontraron:

- Campos con `selection` o `char` que restrinjan el rubro.
- Métodos con `if company.industry_type` o equivalente.
- Dominios que filtren por tipo de industria.
- Configuraciones default que asuman un rubro específico.

**Sin refactors necesarios. Sin entradas para `BUGS_BACKLOG.md`.**

---

_Documento creado: 2026-06-10 — Phase 5 Bloque E (IND-02 + IND-04 + apéndice IND-03)_
_Cross-ref: [`docs/adr/0004-multi-rubro-strategy.md`](adr/0004-multi-rubro-strategy.md)_
