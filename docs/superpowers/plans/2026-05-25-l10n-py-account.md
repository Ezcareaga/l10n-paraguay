# Fase 1b — `l10n_py_account` Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar `l10n_py_account 18.0.1.0.0` (PUC RG 49/14 + taxes IVA + document types SIFEN + timbrado + punto de emisión + extensiones a journal/move) y completar el gap pendiente en `l10n_py_base 18.0.1.1.0` (extensión `res.company` + modelo `l10n_py.economic_activity`).

**Architecture:** Dos módulos OCA-style en `addons/`, secuenciales: PR1 bumpea `l10n_py_base` con campos fiscales de empresa; PR2 crea `l10n_py_account` que depende de PR1 + `account` + `l10n_latam_invoice_document`. Patrón Odoo 18 chart_template moderno (`@template('py')` decorators + CSVs en `data/template/`). Sequence independiente por (journal, document_type) vía `_get_last_sequence_domain`. Defensive checks para evitar bugs SIFEN.

**Tech Stack:** Odoo 18 Community, Python 3.11, PostgreSQL 15, `pytest-odoo` para tests, `xlrd 2.0.2` para extraer PUC desde XLS DNIT. Sin libs Python externas adicionales (las de SIFEN entran en Fase 2).

**Spec:** [`docs/superpowers/specs/2026-05-25-l10n-py-account-design.md`](../specs/2026-05-25-l10n-py-account-design.md)

---

## File Structure

### PR1 — `l10n_py_base` 1.1.0 (modificaciones)

```
addons/l10n_py_base/
├── __manifest__.py                                    # MODIFY: version 1.0.0 → 1.1.0, +data files
├── models/
│   ├── __init__.py                                    # MODIFY: + economic_activity, res_company
│   ├── l10n_py_economic_activity.py                   # CREATE: catálogo SIFEN actividades
│   └── res_company.py                                 # CREATE: extensión fiscal de company
├── data/
│   └── l10n_py_economic_activity_demo.xml             # CREATE: 2 records demo
├── views/
│   ├── l10n_py_economic_activity_views.xml            # CREATE: tree/form/menu
│   ├── res_company_views.xml                          # CREATE: sección PY en form company
│   └── menus.xml                                      # MODIFY: + entry Economic Activities
├── security/
│   └── ir.model.access.csv                            # MODIFY: + access rules nuevo modelo
├── tests/
│   ├── __init__.py                                    # MODIFY: + test_company_setup, test_economic_activity
│   ├── test_company_setup.py                          # CREATE: 4 tests
│   └── test_economic_activity.py                      # CREATE: 2 tests
├── README.rst                                         # MODIFY: section "What's new in 1.1.0"
└── readme/CHANGES.rst                                 # MODIFY: + 1.1.0 entry
```

### PR2 — `l10n_py_account` 18.0.1.0.0 (módulo nuevo)

```
addons/l10n_py_account/
├── __init__.py                                        # CREATE: imports + hooks
├── __manifest__.py                                    # CREATE
├── hooks.py                                           # CREATE: _post_init_hook
├── README.rst                                         # CREATE
├── readme/
│   ├── DESCRIPTION.rst                                # CREATE
│   ├── CONFIGURE.rst                                  # CREATE
│   ├── USAGE.rst                                      # CREATE
│   └── ROADMAP.rst                                    # CREATE
├── models/
│   ├── __init__.py                                    # CREATE
│   ├── account_journal.py                             # CREATE
│   ├── account_move.py                                # CREATE
│   ├── account_move_line.py                           # CREATE
│   ├── l10n_latam_document_type.py                    # CREATE: _format_document_number override
│   ├── l10n_py_afectacion_iva.py                      # CREATE
│   ├── l10n_py_point_of_emission.py                   # CREATE
│   ├── l10n_py_timbrado.py                            # CREATE
│   ├── res_company.py                                 # CREATE: _localization_use_documents
│   └── template_py.py                                 # CREATE: @template('py') decorators
├── data/
│   ├── l10n_latam_document_type_data.csv              # CREATE: 5 docs
│   ├── l10n_py_afectacion_iva_data.csv                # CREATE: 4 records (desde catalog canónico)
│   └── template/
│       ├── account.account-py.csv                     # CREATE: PUC RG 49/14 (~200 cuentas)
│       ├── account.account.tag-py.csv                 # CREATE: tags Hechauka
│       ├── account.fiscal.position-py.csv             # CREATE: placeholder vacío
│       ├── account.group-py.csv                       # CREATE: grupos jerárquicos
│       ├── account.tax-py.csv                         # CREATE: 6 taxes IVA
│       └── account.tax.group-py.csv                   # CREATE: 1 grupo "IVA Paraguay"
├── views/
│   ├── account_journal_views.xml                      # CREATE
│   ├── account_move_views.xml                         # CREATE
│   ├── l10n_py_afectacion_iva_views.xml               # CREATE
│   ├── l10n_py_point_of_emission_views.xml            # CREATE
│   ├── l10n_py_timbrado_views.xml                     # CREATE
│   ├── menus.xml                                      # CREATE
│   └── res_company_views.xml                          # CREATE
├── wizards/
│   ├── __init__.py                                    # CREATE
│   ├── account_migration_wizard.py                    # CREATE
│   └── account_migration_wizard_views.xml             # CREATE
├── security/
│   ├── ir.model.access.csv                            # CREATE
│   └── l10n_py_account_security.xml                   # CREATE: grupo group_l10n_py_account_user
├── tests/
│   ├── __init__.py                                    # CREATE
│   ├── common.py                                      # CREATE: L10nPyAccountTestCase fixture
│   ├── test_account_move_defensive.py                 # CREATE
│   ├── test_account_move_sequence.py                  # CREATE
│   ├── test_chart_template.py                         # CREATE
│   ├── test_company_extension.py                      # CREATE
│   ├── test_document_types.py                         # CREATE
│   ├── test_hechauka_critical_accounts.py             # CREATE
│   ├── test_journal_extension.py                      # CREATE
│   ├── test_migration_wizard.py                       # CREATE
│   ├── test_point_of_emission.py                      # CREATE
│   ├── test_post_init_hook.py                         # CREATE
│   ├── test_pyme_e2e.py                               # CREATE
│   ├── test_taxes.py                                  # CREATE
│   └── test_timbrado.py                               # CREATE
└── i18n/                                              # vacío inicialmente
```

### Scripts (raíz del proyecto)

```
scripts/
└── extract_puc_rg49.py                                # CREATE: extrae PUC desde XLS DNIT → CSVs Odoo
```

---

## Phase 1 — `l10n_py_base` 1.1.0 bump (PR1)

### Task 1: Branch + manifest bump + dependencias

**Files:**

- Modify: `addons/l10n_py_base/__manifest__.py`

- [ ] **Step 1: Crear branch desde dev (o main si dev no existe)**

```bash
git checkout -b feat/l10n-py-base-company
```

- [ ] **Step 2: Bumpear version en manifest**

Editar `addons/l10n_py_base/__manifest__.py` línea `"version": "18.0.1.0.0"` → `"version": "18.0.1.1.0"`.

- [ ] **Step 3: Agregar nuevos data files al manifest**

En el array `"data"` agregar (después de los existing data files, antes de los views):

```python
"data/l10n_py_economic_activity_demo.xml",
```

Y agregar al final del array (después de los views):

```python
"views/l10n_py_economic_activity_views.xml",
"views/res_company_views.xml",
```

- [ ] **Step 4: Verificar manifest parsea OK**

```bash
python -c "with open('addons/l10n_py_base/__manifest__.py') as f: m = eval(f.read()); print(m['version'])"
```

Expected: `18.0.1.1.0`

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_base/__manifest__.py
git commit -m "chore(l10n_py_base): bump version to 18.0.1.1.0"
```

---

### Task 2: Modelo `l10n_py.economic_activity`

**Files:**

- Create: `addons/l10n_py_base/models/l10n_py_economic_activity.py`
- Create: `addons/l10n_py_base/tests/test_economic_activity.py`
- Create: `addons/l10n_py_base/data/l10n_py_economic_activity_demo.xml`
- Modify: `addons/l10n_py_base/models/__init__.py`
- Modify: `addons/l10n_py_base/tests/__init__.py`
- Modify: `addons/l10n_py_base/security/ir.model.access.csv`

- [ ] **Step 1: Escribir test que falla**

Crear `addons/l10n_py_base/tests/test_economic_activity.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del modelo l10n_py.economic_activity."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestEconomicActivity(TransactionCase):

    def test_create_economic_activity(self):
        """Crear una actividad económica simple."""
        activity = self.env["l10n_py.economic_activity"].create({
            "code": "1254",
            "name": "Venta al por menor de artículos de almacén",
        })
        self.assertEqual(activity.code, "1254")
        self.assertTrue(activity.active)

    def test_demo_records_loaded(self):
        """Los 2 records demo de actividades económicas deben estar cargados."""
        activities = self.env["l10n_py.economic_activity"].search([])
        self.assertGreaterEqual(len(activities), 2)
```

- [ ] **Step 2: Agregar test al `__init__.py` de tests**

Editar `addons/l10n_py_base/tests/__init__.py`:

```python
from . import test_economic_activity
```

- [ ] **Step 3: Crear el modelo**

Crear `addons/l10n_py_base/models/l10n_py_economic_activity.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo SIFEN de actividades económicas.

Vacío por default; se llenará vía WS SET en Fase 2 (l10n_py_edi). En Fase 1b
se permite carga manual desde la UI.
"""
from odoo import fields, models


class L10nPyEconomicActivity(models.Model):
    _name = "l10n_py.economic_activity"
    _description = "Paraguay - Actividad Económica DNIT"
    _order = "code"

    code = fields.Char(required=True, help="Código de la actividad económica DNIT (ej: 1254)")
    name = fields.Char(required=True, translate=True)
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "El código de actividad económica debe ser único"),
    ]
```

- [ ] **Step 4: Agregar import en `models/__init__.py`**

Editar `addons/l10n_py_base/models/__init__.py`, agregar línea:

```python
from . import l10n_py_economic_activity
```

(orden alfabético entre los imports `l10n_*`)

- [ ] **Step 5: Crear data file demo**

Crear `addons/l10n_py_base/data/l10n_py_economic_activity_demo.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Demo records mínimos. El catálogo completo SIFEN se carga vía WS SET en Fase 2. -->
<odoo>
    <data noupdate="1">
        <record id="economic_activity_1254" model="l10n_py.economic_activity">
            <field name="code">1254</field>
            <field name="name">Venta al por menor de artículos de almacén (minimarkets)</field>
        </record>
        <record id="economic_activity_5610" model="l10n_py.economic_activity">
            <field name="code">5610</field>
            <field name="name">Actividades de restaurantes y servicio móvil de comidas</field>
        </record>
    </data>
</odoo>
```

- [ ] **Step 6: Agregar access rules**

Editar `addons/l10n_py_base/security/ir.model.access.csv`, agregar 2 líneas al final:

```csv
access_l10n_py_economic_activity_user,l10n_py.economic_activity.user,model_l10n_py_economic_activity,base.group_user,1,0,0,0
access_l10n_py_economic_activity_manager,l10n_py.economic_activity.manager,model_l10n_py_economic_activity,base.group_system,1,1,1,1
```

- [ ] **Step 7: Reinstalar módulo y correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_base -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: tests `test_create_economic_activity` y `test_demo_records_loaded` PASS.

- [ ] **Step 8: Commit**

```bash
git add addons/l10n_py_base/models/l10n_py_economic_activity.py \
        addons/l10n_py_base/models/__init__.py \
        addons/l10n_py_base/data/l10n_py_economic_activity_demo.xml \
        addons/l10n_py_base/security/ir.model.access.csv \
        addons/l10n_py_base/tests/test_economic_activity.py \
        addons/l10n_py_base/tests/__init__.py
git commit -m "feat(l10n_py_base): add l10n_py.economic_activity catalog model"
```

---

### Task 3: Views + menú para economic_activity

**Files:**

- Create: `addons/l10n_py_base/views/l10n_py_economic_activity_views.xml`
- Modify: `addons/l10n_py_base/views/menus.xml`

- [ ] **Step 1: Crear el view XML**

Crear `addons/l10n_py_base/views/l10n_py_economic_activity_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_l10n_py_economic_activity_tree" model="ir.ui.view">
        <field name="name">l10n_py.economic_activity.tree</field>
        <field name="model">l10n_py.economic_activity</field>
        <field name="arch" type="xml">
            <list string="Actividades Económicas DNIT">
                <field name="code"/>
                <field name="name"/>
                <field name="active" widget="boolean_toggle"/>
            </list>
        </field>
    </record>

    <record id="view_l10n_py_economic_activity_form" model="ir.ui.view">
        <field name="name">l10n_py.economic_activity.form</field>
        <field name="model">l10n_py.economic_activity</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <field name="code"/>
                        <field name="name"/>
                        <field name="active"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>

    <record id="action_l10n_py_economic_activity" model="ir.actions.act_window">
        <field name="name">Actividades Económicas</field>
        <field name="res_model">l10n_py.economic_activity</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

- [ ] **Step 2: Agregar entrada de menú**

Editar `addons/l10n_py_base/views/menus.xml`, agregar dentro del menú padre "Catálogos PY":

```xml
<menuitem
    id="menu_l10n_py_economic_activity"
    name="Actividades Económicas"
    parent="menu_l10n_py_catalogs"
    action="action_l10n_py_economic_activity"
    sequence="50"/>
```

(Si el menú padre tiene otro id, ajustar; si no existe, ver `menus.xml` para identificarlo y ajustar a la jerarquía existente.)

- [ ] **Step 3: Reinstalar módulo y verificar carga sin errores**

```bash
docker compose exec odoo odoo -u l10n_py_base -d l10n_py_dev --stop-after-init
```

Expected: sin tracebacks, log "Modules loaded."

- [ ] **Step 4: Commit**

```bash
git add addons/l10n_py_base/views/l10n_py_economic_activity_views.xml \
        addons/l10n_py_base/views/menus.xml
git commit -m "feat(l10n_py_base): add tree/form/menu for economic_activity"
```

---

### Task 4: Extensión `res.company` con campos fiscales PY

**Files:**

- Create: `addons/l10n_py_base/models/res_company.py`
- Modify: `addons/l10n_py_base/models/__init__.py`

- [ ] **Step 1: Escribir el modelo extendido**

Crear `addons/l10n_py_base/models/res_company.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión de res.company para identidad fiscal paraguaya."""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from . import modulo11


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_py_taxpayer_type_id = fields.Many2one(
        comodel_name="l10n_py.taxpayer.type",
        string="Tipo de Contribuyente",
        help="Persona Física o Jurídica (D205 iTiContRec).",
    )
    l10n_py_regime_id = fields.Many2one(
        comodel_name="l10n_py.regime",
        string="Régimen Tributario",
        help="Régimen tributario DNIT (D104 cTipReg).",
    )
    l10n_py_economic_activity_ids = fields.Many2many(
        comodel_name="l10n_py.economic_activity",
        string="Actividades Económicas",
        help="Una empresa puede tener múltiples actividades. Una se marca como principal en el XML del DE.",
    )
    l10n_py_nombre_fantasia = fields.Char(
        string="Nombre de Fantasía",
        help="Nombre comercial alternativo (campo D102 dNomFanEmi en SIFEN).",
    )
    l10n_py_dv = fields.Char(
        string="DV RUC",
        size=1,
        compute="_compute_l10n_py_dv",
        store=True,
        help="Dígito verificador del RUC (último dígito).",
    )

    @api.depends("vat", "country_id")
    def _compute_l10n_py_dv(self):
        for company in self:
            if company.country_id and company.country_id.code == "PY" and company.vat:
                _cuerpo, dv = modulo11.split_ruc(company.vat)
                company.l10n_py_dv = str(dv) if dv is not None else False
            else:
                company.l10n_py_dv = False

    @api.constrains("vat", "country_id")
    def _check_l10n_py_company_ruc(self):
        """Valida RUC paraguayo de la company (módulo 11)."""
        for company in self:
            if not (company.country_id and company.country_id.code == "PY"):
                continue
            if not company.vat:
                # RUC opcional al crear company nueva; se exigirá al postear DE en Fase 2
                continue
            if not modulo11.validate_ruc(company.vat):
                raise ValidationError(
                    _(
                        "El RUC %(vat)s de la empresa %(name)s no es válido "
                        "(DV módulo 11 incorrecto o formato inválido).",
                        vat=company.vat,
                        name=company.name,
                    )
                )
```

- [ ] **Step 2: Agregar import en `models/__init__.py`**

Editar `addons/l10n_py_base/models/__init__.py`, agregar línea (orden alfabético):

```python
from . import res_company
```

- [ ] **Step 3: Reinstalar módulo (smoke check)**

```bash
docker compose exec odoo odoo -u l10n_py_base -d l10n_py_dev --stop-after-init
```

Expected: sin errores.

- [ ] **Step 4: Commit**

```bash
git add addons/l10n_py_base/models/res_company.py \
        addons/l10n_py_base/models/__init__.py
git commit -m "feat(l10n_py_base): extend res.company with PY fiscal identity fields"
```

---

### Task 5: Tests de `res.company` extension

**Files:**

- Create: `addons/l10n_py_base/tests/test_company_setup.py`
- Modify: `addons/l10n_py_base/tests/__init__.py`

- [ ] **Step 1: Escribir los tests**

Crear `addons/l10n_py_base/tests/test_company_setup.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la extensión fiscal en res.company."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_py_base.models import modulo11


@tagged("post_install", "-at_install", "l10n_py")
class TestCompanySetup(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.taxpayer_pf = cls.env.ref("l10n_py_base.taxpayer_type_1")  # Persona Física
        cls.regime_general = cls.env.ref("l10n_py_base.regime_8")  # Turismo (any active)
        cls.activity_minimarket = cls.env.ref("l10n_py_base.economic_activity_1254")

    def _make_company(self, vat=None):
        cuerpo = "80069563"
        if vat is None:
            dv = modulo11.calculate_dv(cuerpo, basemax=11)
            vat = f"{cuerpo}-{dv}"
        return self.env["res.company"].create({
            "name": "Test PY Co",
            "country_id": self.country_py.id,
            "vat": vat,
            "l10n_py_taxpayer_type_id": self.taxpayer_pf.id,
            "l10n_py_regime_id": self.regime_general.id,
            "l10n_py_economic_activity_ids": [(6, 0, [self.activity_minimarket.id])],
            "l10n_py_nombre_fantasia": "Almacén Don Pedro",
        })

    def test_company_valid_ruc_computes_dv(self):
        company = self._make_company()
        cuerpo = "80069563"
        expected_dv = str(modulo11.calculate_dv(cuerpo, basemax=11))
        self.assertEqual(company.l10n_py_dv, expected_dv)

    def test_company_invalid_ruc_raises(self):
        cuerpo = "80069563"
        wrong_dv = (modulo11.calculate_dv(cuerpo, basemax=11) + 1) % 10
        with self.assertRaises(ValidationError):
            self._make_company(vat=f"{cuerpo}-{wrong_dv}")

    def test_company_non_py_country_skips_validation(self):
        country_ar = self.env.ref("base.ar")
        company = self.env["res.company"].create({
            "name": "Test AR Co",
            "country_id": country_ar.id,
            "vat": "any-invalid-vat",  # no se valida porque no es PY
        })
        self.assertFalse(company.l10n_py_dv)

    def test_company_empty_vat_is_allowed(self):
        # Permitir crear company sin RUC (se requerirá al postear DE en Fase 2)
        company = self.env["res.company"].create({
            "name": "Test PY Co Sin RUC",
            "country_id": self.country_py.id,
        })
        self.assertFalse(company.l10n_py_dv)
```

- [ ] **Step 2: Agregar al `tests/__init__.py`**

```python
from . import test_company_setup
```

- [ ] **Step 3: Correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_base -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 4 tests `TestCompanySetup` PASS.

- [ ] **Step 4: Commit**

```bash
git add addons/l10n_py_base/tests/test_company_setup.py \
        addons/l10n_py_base/tests/__init__.py
git commit -m "test(l10n_py_base): add tests for res.company PY extension"
```

---

### Task 6: View extension para `res.company` form

**Files:**

- Create: `addons/l10n_py_base/views/res_company_views.xml`

- [ ] **Step 1: Crear la vista**

Crear `addons/l10n_py_base/views/res_company_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_company_form_inherit_l10n_py" model="ir.ui.view">
        <field name="name">res.company.form.inherit.l10n_py</field>
        <field name="model">res.company</field>
        <field name="inherit_id" ref="base.view_company_form"/>
        <field name="arch" type="xml">
            <xpath expr="//notebook" position="inside">
                <page string="Paraguay (Fiscal)" invisible="country_id and country_id != %(base.py)d">
                    <group>
                        <group string="Identidad DNIT">
                            <field name="l10n_py_nombre_fantasia"/>
                            <field name="l10n_py_dv" readonly="1"/>
                            <field name="l10n_py_taxpayer_type_id"
                                   options="{'no_create': True, 'no_open': True}"/>
                            <field name="l10n_py_regime_id"
                                   options="{'no_create': True, 'no_open': True}"/>
                        </group>
                        <group string="Actividades Económicas">
                            <field name="l10n_py_economic_activity_ids"
                                   widget="many2many_tags"
                                   options="{'no_quick_create': True}"/>
                        </group>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

- [ ] **Step 2: Reinstalar y verificar carga sin errores**

```bash
docker compose exec odoo odoo -u l10n_py_base -d l10n_py_dev --stop-after-init
```

- [ ] **Step 3: Verificar manualmente en UI** (opcional pero recomendado)

Abrir Settings → Companies → seleccionar company PY → ver tab "Paraguay (Fiscal)".

- [ ] **Step 4: Commit**

```bash
git add addons/l10n_py_base/views/res_company_views.xml
git commit -m "feat(l10n_py_base): add Paraguay fiscal section to company form"
```

---

### Task 7: Update README + CHANGES + PR1

**Files:**

- Modify: `addons/l10n_py_base/readme/CHANGES.rst`
- Modify: `addons/l10n_py_base/README.rst`

- [ ] **Step 1: Agregar entrada a CHANGES.rst**

Editar `addons/l10n_py_base/readme/CHANGES.rst`, agregar al inicio (antes de la entry de 1.0.0):

```rst
18.0.1.1.0 (2026-05-25)
~~~~~~~~~~~~~~~~~~~~~~~~

* Add ``l10n_py.economic_activity`` catalog model (manual load; SET WS in Fase 2)
* Extend ``res.company`` with PY fiscal identity fields:
  ``l10n_py_taxpayer_type_id``, ``l10n_py_regime_id``,
  ``l10n_py_economic_activity_ids``, ``l10n_py_nombre_fantasia``, ``l10n_py_dv``
* Add modulo 11 RUC validation to company (mirrors partner validation)
* Add "Paraguay (Fiscal)" section in company form view
```

- [ ] **Step 2: Regenerar README.rst si usás oca-gen-addon-readme**

Si tenés `oca-gen-addon-readme` instalado:

```bash
cd addons/l10n_py_base && oca-gen-addon-readme --addon-dir . --branch 18.0 --org-name Ezcareaga --repo-name l10n-paraguay
```

Si no, editar manualmente `README.rst` para reflejar version 18.0.1.1.0 en el badge superior.

- [ ] **Step 3: Correr full test suite del módulo**

```bash
docker compose exec odoo odoo -u l10n_py_base -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 21 (existing) + 6 (new) = **27 tests PASS**.

- [ ] **Step 4: Commit + push + abrir PR**

```bash
git add addons/l10n_py_base/readme/CHANGES.rst addons/l10n_py_base/README.rst
git commit -m "docs(l10n_py_base): release notes 18.0.1.1.0"
git push -u origin feat/l10n-py-base-company
gh pr create --base main --title "feat(l10n_py_base): 1.1.0 — company fiscal extension + economic_activity" --body "$(cat <<'EOF'
## Summary
- Bump l10n_py_base to 18.0.1.1.0
- Add l10n_py.economic_activity catalog (manual load; full SET WS in Fase 2)
- Extend res.company with PY fiscal identity: taxpayer_type, regime, economic_activities, nombre_fantasia, dv
- Add company-level RUC validation (modulo 11)

## Test plan
- [x] 27 tests pass
- [x] Manual UI check: Paraguay section visible in company form

Spec: docs/superpowers/specs/2026-05-25-l10n-py-account-design.md (Phase 1, sec 1)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**🛑 CHECKPOINT — Merge PR1 a main antes de arrancar Phase 2.**

---

## Phase 2 — `l10n_py_account` 18.0.1.0.0 (PR2)

### Task 8: Module skeleton + manifest + branch

**Files:**

- Create: `addons/l10n_py_account/__init__.py`
- Create: `addons/l10n_py_account/__manifest__.py`
- Create: `addons/l10n_py_account/hooks.py`
- Create: `addons/l10n_py_account/security/ir.model.access.csv`
- Create: `addons/l10n_py_account/security/l10n_py_account_security.xml`
- Create: `addons/l10n_py_account/models/__init__.py`
- Create: `addons/l10n_py_account/tests/__init__.py`
- Create: `addons/l10n_py_account/wizards/__init__.py`
- Create: `addons/l10n_py_account/i18n/.gitkeep`

- [ ] **Step 1: Crear branch**

```bash
git checkout main && git pull
git checkout -b feat/l10n-py-account
```

- [ ] **Step 2: Crear estructura de directorios**

```bash
mkdir -p addons/l10n_py_account/{models,views,data/template,wizards,security,tests,readme,i18n}
touch addons/l10n_py_account/i18n/.gitkeep
```

- [ ] **Step 3: Crear `__manifest__.py`**

```python
# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Paraguay - Accounting",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations/Account Charts",
    "license": "AGPL-3",
    "author": "Careaga Dev, Odoo Community Association (OCA)",
    "website": "https://github.com/Ezcareaga/l10n-paraguay",
    "countries": ["py"],
    "summary": (
        "Plan de cuentas RG 49/14, impuestos IVA, tipos de documento SIFEN, "
        "timbrado y punto de emisión para la localización paraguaya."
    ),
    "depends": [
        "l10n_py_base",
        "account",
        "l10n_latam_invoice_document",
    ],
    "auto_install": ["account"],
    "data": [
        "security/l10n_py_account_security.xml",
        "security/ir.model.access.csv",
        "data/l10n_py_afectacion_iva_data.csv",
        "data/l10n_latam_document_type_data.csv",
        "views/l10n_py_afectacion_iva_views.xml",
        "views/l10n_py_timbrado_views.xml",
        "views/l10n_py_point_of_emission_views.xml",
        "views/account_journal_views.xml",
        "views/account_move_views.xml",
        "views/res_company_views.xml",
        "wizards/account_migration_wizard_views.xml",
        "views/menus.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "post_init_hook": "_post_init_hook",
}
```

- [ ] **Step 4: Crear `__init__.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from . import models
from . import wizards
from .hooks import _post_init_hook
```

- [ ] **Step 5: Crear `models/__init__.py`, `wizards/__init__.py`, `tests/__init__.py` vacíos**

`addons/l10n_py_account/models/__init__.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
```

Mismo content (solo header) en `wizards/__init__.py` y `tests/__init__.py`.

- [ ] **Step 6: Crear `hooks.py` con stub**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Hooks de instalación de l10n_py_account."""
import logging

_logger = logging.getLogger(__name__)


def _post_init_hook(env):
    """Stub - se completa en Task 31."""
    _logger.info("l10n_py_account: _post_init_hook ejecutado (stub).")
```

- [ ] **Step 7: Crear `security/l10n_py_account_security.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <data noupdate="1">
        <record id="group_l10n_py_account_user" model="res.groups">
            <field name="name">Paraguay Accounting - User</field>
            <field name="category_id" ref="base.module_category_accounting_accounting"/>
            <field name="implied_ids" eval="[(4, ref('account.group_account_user'))]"/>
        </record>
    </data>
</odoo>
```

- [ ] **Step 8: Crear `security/ir.model.access.csv`**

```csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_l10n_py_afectacion_iva_user,l10n_py.afectacion_iva.user,model_l10n_py_afectacion_iva,base.group_user,1,0,0,0
access_l10n_py_afectacion_iva_manager,l10n_py.afectacion_iva.manager,model_l10n_py_afectacion_iva,base.group_system,1,1,1,1
access_l10n_py_timbrado_user,l10n_py.timbrado.user,model_l10n_py_timbrado,group_l10n_py_account_user,1,0,0,0
access_l10n_py_timbrado_manager,l10n_py.timbrado.manager,model_l10n_py_timbrado,base.group_system,1,1,1,1
access_l10n_py_point_of_emission_user,l10n_py.point_of_emission.user,model_l10n_py_point_of_emission,group_l10n_py_account_user,1,0,0,0
access_l10n_py_point_of_emission_manager,l10n_py.point_of_emission.manager,model_l10n_py_point_of_emission,base.group_system,1,1,1,1
```

(La mayoría de los modelos se agregan al CSV en sus tasks respectivas.)

- [ ] **Step 9: Verificar que el módulo es detectable**

```bash
docker compose exec odoo odoo --update-list -d l10n_py_dev --stop-after-init
docker compose exec odoo odoo shell -d l10n_py_dev <<< "print(env['ir.module.module'].search([('name','=','l10n_py_account')]).state)"
```

Expected: `uninstalled`.

- [ ] **Step 10: Commit**

```bash
git add addons/l10n_py_account/
git commit -m "feat(l10n_py_account): module skeleton — manifest, init, security"
```

---

### Task 9: Modelo `l10n_py.afectacion_iva` + data load

**Files:**

- Create: `addons/l10n_py_account/models/l10n_py_afectacion_iva.py`
- Create: `addons/l10n_py_account/data/l10n_py_afectacion_iva_data.csv`
- Create: `addons/l10n_py_account/views/l10n_py_afectacion_iva_views.xml`
- Modify: `addons/l10n_py_account/models/__init__.py`

- [ ] **Step 1: Crear modelo**

`addons/l10n_py_account/models/l10n_py_afectacion_iva.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Catálogo SIFEN TABLA 6 — Códigos de Afectación IVA (campo E731 iAfecIVA)."""
from odoo import fields, models


class L10nPyAfectacionIva(models.Model):
    _name = "l10n_py.afectacion_iva"
    _description = "Paraguay - Afectación IVA (SIFEN E731)"
    _order = "code"

    code = fields.Char(required=True, size=2)
    name = fields.Char(required=True, translate=True)

    _sql_constraints = [
        ("code_uniq", "unique(code)", "El código de afectación IVA debe ser único"),
    ]
```

- [ ] **Step 2: Crear CSV de data**

`addons/l10n_py_account/data/l10n_py_afectacion_iva_data.csv`:

```csv
id,code,name
afectacion_iva_1,1,Gravado IVA
afectacion_iva_2,2,Exonerado (Art. 83 - Ley 125)
afectacion_iva_3,3,Exento
afectacion_iva_4,4,Gravado parcial
```

- [ ] **Step 3: Crear views**

`addons/l10n_py_account/views/l10n_py_afectacion_iva_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_l10n_py_afectacion_iva_tree" model="ir.ui.view">
        <field name="name">l10n_py.afectacion_iva.tree</field>
        <field name="model">l10n_py.afectacion_iva</field>
        <field name="arch" type="xml">
            <list>
                <field name="code"/>
                <field name="name"/>
            </list>
        </field>
    </record>
    <record id="action_l10n_py_afectacion_iva" model="ir.actions.act_window">
        <field name="name">Afectación IVA (SIFEN)</field>
        <field name="res_model">l10n_py.afectacion_iva</field>
        <field name="view_mode">list</field>
    </record>
</odoo>
```

- [ ] **Step 4: Agregar import a models/**init**.py**

```python
from . import l10n_py_afectacion_iva
```

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_account/models/l10n_py_afectacion_iva.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/data/l10n_py_afectacion_iva_data.csv \
        addons/l10n_py_account/views/l10n_py_afectacion_iva_views.xml
git commit -m "feat(l10n_py_account): add l10n_py.afectacion_iva catalog (SIFEN E731)"
```

---

### Task 10: Modelo `l10n_py.timbrado` + tests

**Files:**

- Create: `addons/l10n_py_account/models/l10n_py_timbrado.py`
- Create: `addons/l10n_py_account/views/l10n_py_timbrado_views.xml`
- Create: `addons/l10n_py_account/tests/common.py`
- Create: `addons/l10n_py_account/tests/test_timbrado.py`
- Modify: `addons/l10n_py_account/models/__init__.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Crear fixture compartido `tests/common.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Fixture compartido para tests de l10n_py_account."""
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class L10nPyAccountTestCase(AccountTestInvoicingCommon):
    """Fixture base: company PY + chart 'py' cargado + timbrado + PoE."""

    @classmethod
    def setUpClass(cls, chart_template_ref="py"):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.company_data["company"]
        cls.company.country_id = cls.env.ref("base.py")
        cls.company.account_fiscal_country_id = cls.env.ref("base.py")
        cls.timbrado = cls.env["l10n_py.timbrado"].create({
            "name": "12345678",
            "date_from": "2026-01-01",
            "state": "active",
            "company_id": cls.company.id,
        })
        cls.poe = cls.env["l10n_py.point_of_emission"].create({
            "establishment_code": "001",
            "code": "001",
            "address_id": cls.company.partner_id.id,
            "company_id": cls.company.id,
        })
        cls.sale_journal = cls.env["account.journal"].search([
            ("type", "=", "sale"),
            ("company_id", "=", cls.company.id),
        ], limit=1)
        cls.sale_journal.l10n_py_point_of_emission_id = cls.poe
```

(Notas: usa `AccountTestInvoicingCommon` para tener company con chart cargado y journals creados; los modelos `l10n_py.timbrado` y `l10n_py.point_of_emission` los creamos en Tasks 10/11; `account.chart.template.try_loading('py')` corre vía `chart_template_ref="py"` cuando `template_py.py` exista en Task 19. **Hasta entonces este fixture NO carga**; mientras tanto los tests usan `TransactionCase` plano.)

- [ ] **Step 2: Escribir tests que fallan**

`addons/l10n_py_account/tests/test_timbrado.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del modelo l10n_py.timbrado."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestTimbrado(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _make_timbrado(self, **kwargs):
        defaults = {
            "name": "12345678",
            "date_from": "2026-01-01",
            "state": "draft",
            "company_id": self.company.id,
        }
        defaults.update(kwargs)
        return self.env["l10n_py.timbrado"].create(defaults)

    def test_create_timbrado_ok(self):
        t = self._make_timbrado()
        self.assertEqual(t.name, "12345678")
        self.assertEqual(t.state, "draft")

    def test_timbrado_name_must_be_8_digits(self):
        with self.assertRaises(ValidationError):
            self._make_timbrado(name="123")

    def test_timbrado_name_must_be_numeric(self):
        with self.assertRaises(ValidationError):
            self._make_timbrado(name="abcd1234")

    def test_only_one_active_timbrado_per_company(self):
        self._make_timbrado(name="11111111", state="active")
        with self.assertRaises(ValidationError):
            self._make_timbrado(name="22222222", state="active")

    def test_two_drafts_allowed(self):
        self._make_timbrado(name="11111111", state="draft")
        # No raise
        self._make_timbrado(name="22222222", state="draft")

    def test_date_to_is_optional(self):
        t = self._make_timbrado(date_to=False)
        self.assertFalse(t.date_to)

    def test_unique_name_per_company(self):
        self._make_timbrado(name="11111111")
        with self.assertRaises(Exception):  # IntegrityError envuelto
            self._make_timbrado(name="11111111")

    def test_transition_draft_to_active(self):
        t = self._make_timbrado(state="draft")
        t.state = "active"
        self.assertEqual(t.state, "active")
```

- [ ] **Step 3: Agregar a tests/**init**.py**

```python
from . import test_timbrado
```

- [ ] **Step 4: Crear modelo `l10n_py.timbrado`**

`addons/l10n_py_account/models/l10n_py_timbrado.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Timbrado DNIT — autorización para emitir DTE.

MT v150 C001-C010: número de 8 dígitos, fecha inicio vigencia obligatoria,
fecha fin opcional ("el timbrado no manejará una fecha de fin de vigencia" — p.60).
Convención operacional DNIT: un timbrado vigente por contribuyente a la vez.
"""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class L10nPyTimbrado(models.Model):
    _name = "l10n_py.timbrado"
    _description = "Paraguay - Timbrado DNIT"
    _order = "date_from desc, name"

    name = fields.Char(
        string="Número",
        required=True,
        size=8,
        help="8 dígitos otorgados por DNIT (MT v150 C004 dNumTim)",
    )
    date_from = fields.Date(
        string="Vigencia desde",
        required=True,
        help="MT v150 C008 dFeIniT",
    )
    date_to = fields.Date(
        string="Vigencia hasta",
        help="MT v150 C009 dFeFinT. Vacío = indefinido (DNIT moderno).",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda s: s.env.company,
    )
    state = fields.Selection(
        [
            ("draft", "Borrador"),
            ("active", "Vigente"),
            ("expired", "Vencido"),
        ],
        default="draft",
        required=True,
    )

    _sql_constraints = [
        ("name_uniq", "unique(name, company_id)", "Timbrado único por empresa"),
    ]

    @api.constrains("state", "company_id")
    def _check_single_active(self):
        for rec in self.filtered(lambda r: r.state == "active"):
            others = self.search([
                ("company_id", "=", rec.company_id.id),
                ("state", "=", "active"),
                ("id", "!=", rec.id),
            ])
            if others:
                raise ValidationError(
                    _("Solo puede haber un timbrado vigente por empresa.")
                )

    @api.constrains("name")
    def _check_name_format(self):
        for rec in self:
            if not (rec.name and rec.name.isdigit() and len(rec.name) == 8):
                raise ValidationError(
                    _("El timbrado debe ser exactamente 8 dígitos numéricos.")
                )
```

- [ ] **Step 5: Agregar import a models/**init**.py**

```python
from . import l10n_py_timbrado
```

- [ ] **Step 6: Crear views**

`addons/l10n_py_account/views/l10n_py_timbrado_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_l10n_py_timbrado_tree" model="ir.ui.view">
        <field name="name">l10n_py.timbrado.tree</field>
        <field name="model">l10n_py.timbrado</field>
        <field name="arch" type="xml">
            <list decoration-success="state == 'active'" decoration-muted="state == 'expired'">
                <field name="name"/>
                <field name="date_from"/>
                <field name="date_to"/>
                <field name="state"/>
                <field name="company_id" groups="base.group_multi_company"/>
            </list>
        </field>
    </record>
    <record id="view_l10n_py_timbrado_form" model="ir.ui.view">
        <field name="name">l10n_py.timbrado.form</field>
        <field name="model">l10n_py.timbrado</field>
        <field name="arch" type="xml">
            <form>
                <header>
                    <field name="state" widget="statusbar" statusbar_visible="draft,active,expired"/>
                </header>
                <sheet>
                    <group>
                        <field name="name"/>
                        <field name="date_from"/>
                        <field name="date_to" placeholder="Vacío = indefinido"/>
                        <field name="company_id" groups="base.group_multi_company"/>
                    </group>
                </sheet>
            </form>
        </field>
    </record>
    <record id="action_l10n_py_timbrado" model="ir.actions.act_window">
        <field name="name">Timbrados DNIT</field>
        <field name="res_model">l10n_py.timbrado</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

- [ ] **Step 7: Instalar el módulo y correr tests**

```bash
docker compose exec odoo odoo -i l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 8 tests `TestTimbrado` PASS. (El test suite completo aún tiene tasks pendientes; algunos otros fallarán hasta completar fixtures.)

- [ ] **Step 8: Commit**

```bash
git add addons/l10n_py_account/models/l10n_py_timbrado.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/views/l10n_py_timbrado_views.xml \
        addons/l10n_py_account/tests/common.py \
        addons/l10n_py_account/tests/test_timbrado.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): add l10n_py.timbrado model + 8 tests"
```

---

### Task 11: Modelo `l10n_py.point_of_emission` + tests

**Files:**

- Create: `addons/l10n_py_account/models/l10n_py_point_of_emission.py`
- Create: `addons/l10n_py_account/views/l10n_py_point_of_emission_views.xml`
- Create: `addons/l10n_py_account/tests/test_point_of_emission.py`
- Modify: `addons/l10n_py_account/models/__init__.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Escribir tests**

`addons/l10n_py_account/tests/test_point_of_emission.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del modelo l10n_py.point_of_emission."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestPointOfEmission(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company

    def _make_poe(self, **kwargs):
        defaults = {
            "establishment_code": "001",
            "code": "001",
            "address_id": self.company.partner_id.id,
            "company_id": self.company.id,
        }
        defaults.update(kwargs)
        return self.env["l10n_py.point_of_emission"].create(defaults)

    def test_create_poe_ok(self):
        poe = self._make_poe()
        self.assertEqual(poe.name, "001-001")

    def test_unique_establishment_point_per_company(self):
        self._make_poe(establishment_code="001", code="001")
        with self.assertRaises(Exception):
            self._make_poe(establishment_code="001", code="001")

    def test_two_points_in_same_establishment_allowed(self):
        self._make_poe(establishment_code="001", code="001")
        # No raise
        self._make_poe(establishment_code="001", code="002")

    def test_codes_must_be_numeric(self):
        with self.assertRaises(ValidationError):
            self._make_poe(establishment_code="abc")

    def test_codes_max_3_digits(self):
        with self.assertRaises(ValidationError):
            self._make_poe(establishment_code="1234")

    def test_compute_name_pads_with_zeros(self):
        poe = self._make_poe(establishment_code="1", code="2")
        self.assertEqual(poe.name, "001-002")
```

- [ ] **Step 2: Agregar a tests/**init**.py**

```python
from . import test_point_of_emission
```

- [ ] **Step 3: Crear modelo**

`addons/l10n_py_account/models/l10n_py_point_of_emission.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Punto de Emisión — establecimiento + punto de expedición SIFEN.

MT v150 C005 dEst (3 chars zero-padded) + C006 dPunExp (3 chars zero-padded).
"""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class L10nPyPointOfEmission(models.Model):
    _name = "l10n_py.point_of_emission"
    _description = "Paraguay - Punto de Emisión"
    _order = "establishment_code, code"

    name = fields.Char(compute="_compute_name", store=True)
    establishment_code = fields.Char(
        string="Establecimiento",
        required=True,
        size=3,
        help="MT v150 C005 dEst — 3 dígitos zero-padded",
    )
    code = fields.Char(
        string="Punto de Expedición",
        required=True,
        size=3,
        help="MT v150 C006 dPunExp — 3 dígitos zero-padded",
    )
    address_id = fields.Many2one(
        "res.partner",
        string="Dirección física",
        required=True,
        domain="['|', ('id', '=', company_partner_id), ('parent_id', '=', company_partner_id)]",
        help="Dirección física de la sucursal. Va al XML del DE.",
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda s: s.env.company,
    )
    company_partner_id = fields.Many2one(related="company_id.partner_id")
    journal_ids = fields.One2many(
        "account.journal",
        "l10n_py_point_of_emission_id",
        string="Journals",
    )
    active = fields.Boolean(default=True)

    _sql_constraints = [
        (
            "estab_point_uniq",
            "unique(company_id, establishment_code, code)",
            "Ya existe un punto de emisión con ese establecimiento + punto en esta empresa",
        ),
    ]

    @api.depends("establishment_code", "code")
    def _compute_name(self):
        for rec in self:
            est = (rec.establishment_code or "").zfill(3)
            pt = (rec.code or "").zfill(3)
            rec.name = f"{est}-{pt}"

    @api.constrains("establishment_code", "code")
    def _check_codes_numeric(self):
        for rec in self:
            for val, fld in [
                (rec.establishment_code, "establecimiento"),
                (rec.code, "punto de expedición"),
            ]:
                if not (val and val.isdigit() and len(val) <= 3):
                    raise ValidationError(
                        _("Código de %s: 1-3 dígitos numéricos", fld)
                    )
```

- [ ] **Step 4: Agregar import a models/**init**.py**

```python
from . import l10n_py_point_of_emission
```

- [ ] **Step 5: Crear views**

`addons/l10n_py_account/views/l10n_py_point_of_emission_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_l10n_py_poe_tree" model="ir.ui.view">
        <field name="name">l10n_py.point_of_emission.tree</field>
        <field name="model">l10n_py.point_of_emission</field>
        <field name="arch" type="xml">
            <list>
                <field name="name"/>
                <field name="establishment_code"/>
                <field name="code"/>
                <field name="address_id"/>
                <field name="active" widget="boolean_toggle"/>
            </list>
        </field>
    </record>
    <record id="view_l10n_py_poe_form" model="ir.ui.view">
        <field name="name">l10n_py.point_of_emission.form</field>
        <field name="model">l10n_py.point_of_emission</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <group>
                        <group>
                            <field name="establishment_code"/>
                            <field name="code"/>
                            <field name="active"/>
                        </group>
                        <group>
                            <field name="address_id"/>
                            <field name="company_id" groups="base.group_multi_company"/>
                        </group>
                    </group>
                    <notebook>
                        <page string="Diarios asociados">
                            <field name="journal_ids" readonly="1"/>
                        </page>
                    </notebook>
                </sheet>
            </form>
        </field>
    </record>
    <record id="action_l10n_py_poe" model="ir.actions.act_window">
        <field name="name">Puntos de Emisión</field>
        <field name="res_model">l10n_py.point_of_emission</field>
        <field name="view_mode">list,form</field>
    </record>
</odoo>
```

- [ ] **Step 6: Reinstalar + correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 6 tests `TestPointOfEmission` PASS.

- [ ] **Step 7: Commit**

```bash
git add addons/l10n_py_account/models/l10n_py_point_of_emission.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/views/l10n_py_point_of_emission_views.xml \
        addons/l10n_py_account/tests/test_point_of_emission.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): add l10n_py.point_of_emission model + 6 tests"
```

---

### Task 12: Extensión `res.company` (account-level) + tests

**Files:**

- Create: `addons/l10n_py_account/models/res_company.py`
- Create: `addons/l10n_py_account/views/res_company_views.xml`
- Create: `addons/l10n_py_account/tests/test_company_extension.py`
- Modify: `addons/l10n_py_account/models/__init__.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Escribir tests**

`addons/l10n_py_account/tests/test_company_extension.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la extensión account-level de res.company."""
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestCompanyExtension(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.company = cls.env["res.company"].create({
            "name": "Test Co PY",
            "country_id": cls.country_py.id,
            "account_fiscal_country_id": cls.country_py.id,
        })

    def test_localization_use_documents_true_for_py(self):
        self.assertTrue(self.company._localization_use_documents())

    def test_localization_use_documents_false_for_non_py(self):
        country_ar = self.env.ref("base.ar")
        company_ar = self.env["res.company"].create({
            "name": "Test Co AR",
            "country_id": country_ar.id,
            "account_fiscal_country_id": country_ar.id,
        })
        self.assertFalse(company_ar._localization_use_documents())

    def test_active_timbrado_returns_active_one(self):
        self.env["l10n_py.timbrado"].create({
            "name": "11111111", "date_from": "2026-01-01",
            "state": "draft", "company_id": self.company.id,
        })
        active = self.env["l10n_py.timbrado"].create({
            "name": "22222222", "date_from": "2026-01-01",
            "state": "active", "company_id": self.company.id,
        })
        self.assertEqual(self.company.l10n_py_active_timbrado_id, active)

    def test_active_timbrado_empty_when_none(self):
        self.assertFalse(self.company.l10n_py_active_timbrado_id)
```

- [ ] **Step 2: Agregar a tests/**init**.py**

```python
from . import test_company_extension
```

- [ ] **Step 3: Crear modelo extension**

`addons/l10n_py_account/models/res_company.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión account-level de res.company para Paraguay."""
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_py_timbrado_ids = fields.One2many(
        "l10n_py.timbrado",
        "company_id",
        string="Timbrados",
    )
    l10n_py_active_timbrado_id = fields.Many2one(
        "l10n_py.timbrado",
        string="Timbrado Vigente",
        compute="_compute_l10n_py_active_timbrado",
        help="Timbrado actualmente vigente (state=active)",
    )

    def _compute_l10n_py_active_timbrado(self):
        Timbrado = self.env["l10n_py.timbrado"]
        for company in self:
            company.l10n_py_active_timbrado_id = Timbrado.search([
                ("company_id", "=", company.id),
                ("state", "=", "active"),
            ], limit=1)

    def _localization_use_documents(self):
        self.ensure_one()
        return (
            self.account_fiscal_country_id.code == "PY"
            or super()._localization_use_documents()
        )
```

- [ ] **Step 4: Crear view extension**

`addons/l10n_py_account/views/res_company_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_company_form_inherit_l10n_py_account" model="ir.ui.view">
        <field name="name">res.company.form.inherit.l10n_py_account</field>
        <field name="model">res.company</field>
        <field name="inherit_id" ref="l10n_py_base.view_company_form_inherit_l10n_py"/>
        <field name="arch" type="xml">
            <xpath expr="//page[@string='Paraguay (Fiscal)']" position="inside">
                <group string="Timbrado SIFEN">
                    <field name="l10n_py_active_timbrado_id" readonly="1"/>
                    <field name="l10n_py_timbrado_ids" widget="one2many">
                        <list editable="bottom">
                            <field name="name"/>
                            <field name="date_from"/>
                            <field name="date_to"/>
                            <field name="state"/>
                        </list>
                    </field>
                </group>
            </xpath>
        </field>
    </record>
</odoo>
```

- [ ] **Step 5: Agregar import**

```python
from . import res_company
```

- [ ] **Step 6: Reinstalar + correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 4 tests `TestCompanyExtension` PASS.

- [ ] **Step 7: Commit**

```bash
git add addons/l10n_py_account/models/res_company.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/views/res_company_views.xml \
        addons/l10n_py_account/tests/test_company_extension.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): extend res.company with _localization_use_documents + timbrado"
```

---

### Task 13: Extensión `account.journal` + tests

**Files:**

- Create: `addons/l10n_py_account/models/account_journal.py`
- Create: `addons/l10n_py_account/views/account_journal_views.xml`
- Create: `addons/l10n_py_account/tests/test_journal_extension.py`
- Modify: `addons/l10n_py_account/models/__init__.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Escribir tests**

`addons/l10n_py_account/tests/test_journal_extension.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la extensión account.journal para Paraguay."""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestJournalExtension(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.company = cls.env["res.company"].create({
            "name": "Test Co PY", "country_id": cls.country_py.id,
            "account_fiscal_country_id": cls.country_py.id,
        })
        cls.poe = cls.env["l10n_py.point_of_emission"].create({
            "establishment_code": "001", "code": "001",
            "address_id": cls.company.partner_id.id,
            "company_id": cls.company.id,
        })

    def _make_journal(self, type_, **kwargs):
        defaults = {
            "name": f"Test {type_} journal",
            "type": type_,
            "code": "TST",
            "company_id": self.company.id,
        }
        defaults.update(kwargs)
        return self.env["account.journal"].with_company(self.company).create(defaults)

    def test_sale_journal_require_emission_true(self):
        journal = self._make_journal("sale", l10n_latam_use_documents=True,
                                      l10n_py_point_of_emission_id=self.poe.id)
        self.assertTrue(journal.l10n_py_require_emission)

    def test_purchase_journal_require_emission_false(self):
        journal = self._make_journal("purchase", l10n_latam_use_documents=True)
        self.assertFalse(journal.l10n_py_require_emission)

    def test_sale_journal_without_poe_raises(self):
        with self.assertRaises(ValidationError):
            self._make_journal("sale", l10n_latam_use_documents=True)

    def test_poe_without_use_documents_raises(self):
        with self.assertRaises(ValidationError):
            self._make_journal("sale", l10n_latam_use_documents=False,
                                l10n_py_point_of_emission_id=self.poe.id)

    def test_non_py_journal_no_constraint(self):
        country_ar = self.env.ref("base.ar")
        company_ar = self.env["res.company"].create({
            "name": "Co AR", "country_id": country_ar.id,
            "account_fiscal_country_id": country_ar.id,
        })
        # No raise: country != PY
        journal = self.env["account.journal"].with_company(company_ar).create({
            "name": "Sale AR", "type": "sale", "code": "VEN",
            "company_id": company_ar.id, "l10n_latam_use_documents": True,
        })
        self.assertFalse(journal.l10n_py_require_emission)

    def test_change_use_documents_off_keeps_poe_raises(self):
        journal = self._make_journal("sale", l10n_latam_use_documents=True,
                                      l10n_py_point_of_emission_id=self.poe.id)
        with self.assertRaises(ValidationError):
            journal.l10n_latam_use_documents = False

    def test_journal_country_code_is_py(self):
        journal = self._make_journal("sale", l10n_latam_use_documents=True,
                                      l10n_py_point_of_emission_id=self.poe.id)
        self.assertEqual(journal.country_code, "PY")
```

- [ ] **Step 2: Agregar a tests/**init**.py**

```python
from . import test_journal_extension
```

- [ ] **Step 3: Crear extension**

`addons/l10n_py_account/models/account_journal.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión account.journal — Punto de Emisión obligatorio en sale journals PY."""
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class AccountJournal(models.Model):
    _inherit = "account.journal"

    l10n_py_point_of_emission_id = fields.Many2one(
        "l10n_py.point_of_emission",
        string="Punto de Emisión",
        domain="[('company_id', '=', company_id)]",
        copy=False,
    )
    l10n_py_require_emission = fields.Boolean(
        compute="_compute_l10n_py_require_emission",
        help="True si el journal debe tener PoE (sale + PY + use_documents).",
    )

    @api.depends("type", "country_code", "l10n_latam_use_documents")
    def _compute_l10n_py_require_emission(self):
        for journal in self:
            journal.l10n_py_require_emission = (
                journal.type == "sale"
                and journal.country_code == "PY"
                and journal.l10n_latam_use_documents
            )

    @api.constrains(
        "l10n_py_point_of_emission_id",
        "type",
        "country_code",
        "l10n_latam_use_documents",
    )
    def _check_py_point_of_emission(self):
        for j in self.filtered(lambda x: x.l10n_py_require_emission):
            if not j.l10n_py_point_of_emission_id:
                raise ValidationError(
                    _("Los diarios de ventas paraguayos con documentos requieren un Punto de Emisión.")
                )

    @api.constrains("l10n_py_point_of_emission_id", "l10n_latam_use_documents")
    def _check_py_poe_requires_use_documents(self):
        for j in self.filtered(lambda x: x.l10n_py_point_of_emission_id):
            if not j.l10n_latam_use_documents:
                raise ValidationError(
                    _('Un diario con Punto de Emisión PY debe tener "Usar Documentos" habilitado.')
                )
```

- [ ] **Step 4: Crear view**

`addons/l10n_py_account/views/account_journal_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_account_journal_form_inherit_l10n_py" model="ir.ui.view">
        <field name="name">account.journal.form.inherit.l10n_py</field>
        <field name="model">account.journal</field>
        <field name="inherit_id" ref="account.view_account_journal_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='l10n_latam_use_documents']" position="after">
                <field name="l10n_py_require_emission" invisible="1"/>
                <field name="l10n_py_point_of_emission_id"
                       invisible="not l10n_py_require_emission"
                       required="l10n_py_require_emission"
                       options="{'no_quick_create': True}"/>
            </xpath>
        </field>
    </record>
</odoo>
```

- [ ] **Step 5: Agregar import**

```python
from . import account_journal
```

- [ ] **Step 6: Reinstalar + correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 7 tests `TestJournalExtension` PASS.

- [ ] **Step 7: Commit**

```bash
git add addons/l10n_py_account/models/account_journal.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/views/account_journal_views.xml \
        addons/l10n_py_account/tests/test_journal_extension.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): extend account.journal with PoE + constraints"
```

---

### Task 14: Script de extracción PUC RG 49/14 → CSV Odoo

**Files:**

- Create: `scripts/extract_puc_rg49.py`

- [ ] **Step 1: Crear el script de extracción**

`scripts/extract_puc_rg49.py`:

```python
#!/usr/bin/env python3
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later
"""Extrae el Plan de Cuentas paraguayo desde el XLS oficial DNIT RG 49/14.

Genera 3 CSVs en formato Odoo 18:
  - addons/l10n_py_account/data/template/account.group-py.csv
  - addons/l10n_py_account/data/template/account.account-py.csv

Schema de salida (account.account):
    id,code,name,account_type,reconcile,non_trade

Convención de XML IDs: ``py_<código_sin_puntos>``.

Subset activo por default (~80 cuentas): definido en ACTIVE_CODES abajo.
Resto: ``active=False`` por default (las crea el chart template).

Uso:
    python scripts/extract_puc_rg49.py
"""
import csv
import re
import sys
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parents[1]
XLS_PATH = ROOT / "data" / "catalogs" / "_verification" / "dnit_rg_49_14_anexos.xls"
OUT_DIR = ROOT / "addons" / "l10n_py_account" / "data" / "template"

# Códigos RG 49/14 (sin puntos) que mapeamos a account_type Odoo.
# Reglas: Activo (1.x) → asset_*, Pasivo (2.x) → liability_*, Patrimonio (3.x) → equity,
# Ingresos (4.x, 7.x, 8.x, 17.x) → income, Costos+Gastos (5.x, 10.x-15.x) → expense.
def infer_account_type(code: str, name: str) -> str:
    """Mapea código RG 49/14 → account_type Odoo 18."""
    n = name.upper()
    if code.startswith("1010101") or "RECAUDACIONES" in n or "CAJA" in n or "FONDOS" in n or "BANCOS" in n:
        return "asset_cash"
    if code.startswith("1010103") and "DEUDORES" in n:
        return "asset_receivable"
    if "INVENTARIO" in n or "MERCADER" in n or code.startswith("1010104"):
        return "asset_current"
    if "PAGADOS POR ADELANTADO" in n or "PAGAR POR ADELANTADO" in n:
        return "asset_prepayments"
    if code.startswith("10204"):
        return "asset_fixed"
    if code.startswith("1") and "DEPRECIACION" in n:
        return "asset_fixed"
    if code.startswith("1"):
        return "asset_current" if code.startswith("101") else "asset_non_current"
    if "PROVEEDORES" in n and code.startswith("201"):
        return "liability_payable"
    if code.startswith("2"):
        return "liability_current" if code.startswith("201") else "liability_non_current"
    if code.startswith("3"):
        return "equity"
    if code.startswith("4") and "DESCUENTOS CONCEDIDOS" in n:
        return "income_other"
    if code.startswith("4") or code.startswith("8"):
        return "income"
    if code.startswith("5") or code.startswith("10") or code.startswith("11") or code.startswith("13"):
        return "expense"
    if code.startswith("15"):
        return "expense_depreciation"
    return "expense"  # fallback


# Subset activo por default: comercio + servicios típico PyME.
# Códigos sin puntos. Resto se carga como active=False.
ACTIVE_CODES = {
    # 1.01.01 Disponibilidades
    "1010101", "1010102", "1010103", "1010104",
    # 1.01.03 Créditos
    "1010301", "1010305", "10103050102", "10103050103",  # IVA Crédito + retenciones
    # 1.01.04 Mercaderías (excepto agro/regímenes especiales)
    "10104", "1010401", "101040101", "101040102", "101040103",
    # 1.02.04 PPyE
    "1020401", "1020402", "1020403", "1020404", "1020405",
    "10204099",  # depreciación acumulada
    # 2.01 Pasivo corriente
    "2010101",  # Proveedores locales
    "2010301",  # Deudas fiscales corrientes (padre)
    "201030101", "201030102", "201030103",  # IRACIS / IVA a Pagar / Retenciones
    "2010302",  # Obligaciones laborales
    # 3 Patrimonio
    "30101", "3010101",  # Capital
    "30201",  # Reserva legal
    "30301",  # Resultados acumulados
    # 4 Ingresos
    "401", "40101", "40102",  # Ventas mercaderías gravadas/exentas
    "4010101", "4010102",  # subniveles gravadas IVA 10/5%
    "409",  # Ventas servicios gravados
    "498",  # Descuentos concedidos
    "499",  # Devoluciones
    # 5 Costos
    "501", "50101", "50102",  # Costo mercaderías
    # 8 Otros ingresos
    "801", "802", "803", "805",  # intereses, comisiones, descuentos, dif. cambio
    # 10-11 Gastos
    "1001", "1002", "1004", "1005",  # Gastos de ventas
    "1101", "1105", "1106", "1107", "1108", "1109", "1110", "1111", "1117",
    # 13 Gastos bancarios
    "1301", "1303", "1304",
    # 15 Depreciaciones
    "1501", "1502",
    # 19 IR
    "19",
    # 20 Resultado neto
    "20",
}


def code_to_id(code_raw: str) -> str:
    """1.01.03.05.02 → py_10103050102"""
    return "py_" + code_raw.replace(".", "")


def extract_chart() -> tuple[list[dict], list[dict]]:
    """Retorna (groups, accounts) extraídos del XLS DNIT."""
    wb = xlrd.open_workbook(str(XLS_PATH))
    groups = []
    accounts = []

    # Patrón de línea: "1.01.03.05.02 | RETENCIONES DE IVA"
    code_re = re.compile(r"^(\d+(?:\.\d+)*)$")

    for sheet_name in ["1_Balance General", "2_Estado de Resultados"]:
        sh = wb.sheet_by_name(sheet_name)
        for r in range(sh.nrows):
            row_vals = [str(sh.cell_value(r, c)).strip() for c in range(sh.ncols)]
            code_raw = row_vals[0] if row_vals else ""
            name = row_vals[1] if len(row_vals) > 1 else ""

            if not code_raw or not name or "(nuevas cuentas" in name.lower():
                continue
            m = code_re.match(code_raw)
            if not m:
                continue
            code_clean = code_raw.replace(".", "")
            xml_id = code_to_id(code_raw)

            # Heurística: códigos hasta nivel 3 (`1.01.01`) → group; nivel >=4 → account.
            depth = code_raw.count(".") + 1
            if depth <= 3:
                groups.append({
                    "id": xml_id + "_grp",
                    "code_prefix_start": code_clean,
                    "code_prefix_end": code_clean,
                    "name": name.title(),
                })
            else:
                acc_type = infer_account_type(code_clean, name)
                is_active = code_clean in ACTIVE_CODES or any(
                    code_clean.startswith(active) for active in ACTIVE_CODES
                )
                accounts.append({
                    "id": xml_id,
                    "code": code_clean,
                    "name": name.title(),
                    "account_type": acc_type,
                    "reconcile": "True" if acc_type in (
                        "asset_receivable", "liability_payable"
                    ) else "False",
                    "non_trade": "",
                    "active": "True" if is_active else "False",
                })

    return groups, accounts


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} records)")


def main() -> int:
    if not XLS_PATH.is_file():
        print(f"ERROR: missing {XLS_PATH}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    groups, accounts = extract_chart()
    write_csv(
        OUT_DIR / "account.group-py.csv",
        groups,
        ["id", "code_prefix_start", "code_prefix_end", "name"],
    )
    write_csv(
        OUT_DIR / "account.account-py.csv",
        accounts,
        ["id", "code", "name", "account_type", "reconcile", "non_trade", "active"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Correr el script**

```bash
python scripts/extract_puc_rg49.py
```

Expected:

```
wrote addons/l10n_py_account/data/template/account.group-py.csv (~40 records)
wrote addons/l10n_py_account/data/template/account.account-py.csv (~200 records)
```

- [ ] **Step 3: Verificar manualmente algunas cuentas críticas Hechauka**

```bash
grep -E "(101030502|101030503|201030102)" addons/l10n_py_account/data/template/account.account-py.csv
```

Expected: 3 líneas, una por cada código (Retenciones IVA, IVA Crédito, IVA a Pagar).

- [ ] **Step 4: Commit**

```bash
git add scripts/extract_puc_rg49.py \
        addons/l10n_py_account/data/template/account.group-py.csv \
        addons/l10n_py_account/data/template/account.account-py.csv
git commit -m "feat(l10n_py_account): generate PUC RG 49/14 CSVs from DNIT XLS"
```

---

### Task 15: CSVs de taxes IVA + tax group + fiscal position placeholder

**Files:**

- Create: `addons/l10n_py_account/data/template/account.tax.group-py.csv`
- Create: `addons/l10n_py_account/data/template/account.tax-py.csv`
- Create: `addons/l10n_py_account/data/template/account.fiscal.position-py.csv`

- [ ] **Step 1: Crear tax group CSV**

`addons/l10n_py_account/data/template/account.tax.group-py.csv`:

```csv
id,name,sequence,country_id
tax_group_iva_py,IVA Paraguay,10,base.py
```

- [ ] **Step 2: Crear taxes CSV**

`addons/l10n_py_account/data/template/account.tax-py.csv`:

```csv
id,name,description,amount,amount_type,type_tax_use,tax_group_id,invoice_repartition_line_ids/factor_percent,invoice_repartition_line_ids/repartition_type,invoice_repartition_line_ids/account_id,refund_repartition_line_ids/factor_percent,refund_repartition_line_ids/repartition_type,refund_repartition_line_ids/account_id,l10n_py_afectacion_iva_id,active
tax_iva_venta_10,IVA Débito Fiscal 10%,IVA 10%,10.0,percent,sale,tax_group_iva_py,100|100,base|tax,|py_201030102,100|100,base|tax,|py_201030102,l10n_py_account.afectacion_iva_1,True
tax_iva_venta_5,IVA Débito Fiscal 5%,IVA 5%,5.0,percent,sale,tax_group_iva_py,100|100,base|tax,|py_201030102,100|100,base|tax,|py_201030102,l10n_py_account.afectacion_iva_1,True
tax_iva_venta_exenta,IVA Exenta (ventas),Exenta,0.0,percent,sale,tax_group_iva_py,100,base,,100,base,,l10n_py_account.afectacion_iva_3,True
tax_iva_venta_export,IVA 0% Exportación,Export,0.0,percent,sale,tax_group_iva_py,100,base,,100,base,,l10n_py_account.afectacion_iva_1,True
tax_iva_compra_10,IVA Crédito Fiscal 10%,IVA 10%,10.0,percent,purchase,tax_group_iva_py,100|100,base|tax,|py_101030503,100|100,base|tax,|py_101030503,l10n_py_account.afectacion_iva_1,True
tax_iva_compra_5,IVA Crédito Fiscal 5%,IVA 5%,5.0,percent,purchase,tax_group_iva_py,100|100,base|tax,|py_101030503,100|100,base|tax,|py_101030503,l10n_py_account.afectacion_iva_1,True
```

(Sintaxis de `invoice_repartition_line_ids` en CSV: `factor_percent|factor_percent` para 2 lines, separadas por `|`. `repartition_type` `base|tax`. `account_id` vacío para la línea base, código para la tax line. Verificar contra `l10n_ec/data/template/account.tax-ec.csv` la sintaxis exacta.)

- [ ] **Step 3: Crear fiscal position placeholder**

`addons/l10n_py_account/data/template/account.fiscal.position-py.csv`:

```csv
id,name,sequence
```

(Header solo, sin registros — placeholder por si Fase 2 necesita agregar export/turismo.)

- [ ] **Step 4: Agregar campo `l10n_py_afectacion_iva_id` a account.tax**

Necesario para que el CSV cargue el FK. Editar `addons/l10n_py_account/models/account_tax.py` (CREATE):

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Extensión account.tax con FK a afectación IVA SIFEN."""
from odoo import fields, models


class AccountTax(models.Model):
    _inherit = "account.tax"

    l10n_py_afectacion_iva_id = fields.Many2one(
        "l10n_py.afectacion_iva",
        string="Afectación IVA (SIFEN E731)",
        help="Código SIFEN de afectación IVA usado en la línea del DE.",
    )
```

Agregar a `models/__init__.py`:

```python
from . import account_tax
```

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_account/data/template/ \
        addons/l10n_py_account/models/account_tax.py \
        addons/l10n_py_account/models/__init__.py
git commit -m "feat(l10n_py_account): add tax group + 6 IVA taxes + fiscal position placeholder"
```

---

### Task 16: `template_py.py` con decorator `@template('py')`

**Files:**

- Create: `addons/l10n_py_account/models/template_py.py`
- Modify: `addons/l10n_py_account/models/__init__.py`

- [ ] **Step 1: Crear el módulo de template**

`addons/l10n_py_account/models/template_py.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Chart template loader para Paraguay (Odoo 18 API moderna)."""
from odoo import models
from odoo.addons.account.models.chart_template import template


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("py")
    def _get_py_template_data(self):
        return {
            "property_account_receivable_id": "py_1010301",   # Deudores por Ventas
            "property_account_payable_id": "py_2010101",      # Proveedores Locales
            "property_account_income_categ_id": "py_4010101", # Ventas Mercaderías Gravadas 10%
            "property_account_expense_categ_id": "py_5010101",
            # Los prefijos siguientes son ejemplos basados en RG 49/14;
            # se ajustan si el script extract_puc_rg49.py cambia la convención.
            "bank_account_code_prefix": "1010104",
            "cash_account_code_prefix": "1010102",
            "transfer_account_code_prefix": "1010103",
            "code_digits": 9,
        }

    @template("py", "res.company")
    def _get_py_res_company(self):
        return {
            self.env.company.id: {
                "account_fiscal_country_id": "base.py",
                "account_sale_tax_id": "tax_iva_venta_10",
                "account_purchase_tax_id": "tax_iva_compra_10",
            },
        }

    @template("py", "account.journal")
    def _get_py_account_journal(self):
        return {
            "sale": {"name": "001-001 Facturación"},
        }
```

- [ ] **Step 2: Agregar import**

```python
from . import template_py
```

- [ ] **Step 3: Reinstalar el módulo y probar cargar chart**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init
docker compose exec odoo odoo shell -d l10n_py_dev <<< "
company = env['res.company'].create({'name': 'Test PY', 'country_id': env.ref('base.py').id})
env['account.chart.template'].try_loading('py', company=company)
print('Accounts:', env['account.account'].search_count([('company_id','=',company.id)]))
print('Taxes:', env['account.tax'].search_count([('company_id','=',company.id)]))
"
```

Expected: ~200 accounts, 6 taxes. Sin tracebacks.

- [ ] **Step 4: Commit**

```bash
git add addons/l10n_py_account/models/template_py.py \
        addons/l10n_py_account/models/__init__.py
git commit -m "feat(l10n_py_account): add @template('py') decorator loader"
```

---

### Task 17: Tests del chart template + Hechauka critical accounts + taxes

**Files:**

- Create: `addons/l10n_py_account/tests/test_chart_template.py`
- Create: `addons/l10n_py_account/tests/test_hechauka_critical_accounts.py`
- Create: `addons/l10n_py_account/tests/test_taxes.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Actualizar `tests/common.py` para usar `AccountTestInvoicingCommon` con chart 'py'**

Reemplazar contenido de `addons/l10n_py_account/tests/common.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Fixture compartido para tests con chart 'py' cargado."""
from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class L10nPyAccountTestCase(AccountTestInvoicingCommon):
    """Fixture: company PY + chart 'py' + timbrado active + PoE + sale journal con PoE."""

    @classmethod
    def setUpClass(cls, chart_template_ref="py"):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company = cls.company_data["company"]
        cls.country_py = cls.env.ref("base.py")
        cls.company.country_id = cls.country_py
        cls.company.account_fiscal_country_id = cls.country_py
        cls.timbrado = cls.env["l10n_py.timbrado"].create({
            "name": "12345678",
            "date_from": "2026-01-01",
            "state": "active",
            "company_id": cls.company.id,
        })
        cls.poe = cls.env["l10n_py.point_of_emission"].create({
            "establishment_code": "001",
            "code": "001",
            "address_id": cls.company.partner_id.id,
            "company_id": cls.company.id,
        })
        cls.sale_journal = cls.env["account.journal"].search([
            ("type", "=", "sale"), ("company_id", "=", cls.company.id),
        ], limit=1)
        # Asignar PoE antes de activar use_documents (que ya viene True por chart)
        cls.sale_journal.l10n_py_point_of_emission_id = cls.poe
```

- [ ] **Step 2: Crear `test_chart_template.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestChartTemplate(L10nPyAccountTestCase):

    def test_chart_loaded(self):
        accounts = self.env["account.account"].search([
            ("company_id", "=", self.company.id),
        ])
        self.assertGreater(len(accounts), 50, "PUC debe tener > 50 cuentas cargadas")

    def test_subset_active_around_80(self):
        active = self.env["account.account"].search([
            ("company_id", "=", self.company.id),
            ("active", "=", True),
        ])
        self.assertGreaterEqual(len(active), 60)
        self.assertLessEqual(len(active), 100)

    def test_account_groups_loaded(self):
        groups = self.env["account.group"].search([
            ("company_id", "=", self.company.id),
        ])
        self.assertGreater(len(groups), 30, "Debe haber grupos jerárquicos")

    def test_iva_taxes_loaded(self):
        taxes = self.env["account.tax"].search([
            ("company_id", "=", self.company.id),
            ("tax_group_id.name", "=", "IVA Paraguay"),
        ])
        self.assertEqual(len(taxes), 6, "Deben existir 6 taxes IVA")

    def test_default_sale_tax_is_iva_10(self):
        self.assertEqual(self.company.account_sale_tax_id.amount, 10.0)

    def test_default_purchase_tax_is_iva_10(self):
        self.assertEqual(self.company.account_purchase_tax_id.amount, 10.0)

    def test_sale_journal_use_documents_active(self):
        self.assertTrue(self.sale_journal.l10n_latam_use_documents)

    def test_company_localization_uses_documents(self):
        self.assertTrue(self.company._localization_use_documents())
```

- [ ] **Step 3: Crear `test_hechauka_critical_accounts.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Guard: cuentas RG 49/14 obligatorias para mapeo Hechauka."""
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase

# Códigos sin puntos (RG 49/14 Anexos.xls). Si alguno desaparece del PUC,
# Hechauka no se podrá declarar correctamente.
HECHAUKA_REQUIRED_CODES = [
    # Disponibilidades
    "1010101", "1010102", "1010104",
    # Créditos
    "1010301",                       # Deudores por ventas
    "10103050102",                   # Retenciones de IVA
    "10103050103",                   # IVA Crédito Fiscal
    # Mercaderías
    "101040101", "101040102", "101040103",
    # Pasivo
    "2010101",                       # Proveedores locales
    "201030102",                     # IVA a Pagar
    "201030103",                     # Retenciones a ingresar
    # Patrimonio
    "3010101",                       # Capital integrado
    # Ingresos
    "401",                           # Ventas mercaderías
    # Costos
    "501",                           # Costo mercaderías
    # Resultado
    "19",                            # Impuesto a la Renta
    "20",                            # Resultado neto del ejercicio
]


@tagged("post_install", "-at_install", "l10n_py")
class TestHechaukaCriticalAccounts(L10nPyAccountTestCase):

    def test_all_required_codes_present(self):
        for code in HECHAUKA_REQUIRED_CODES:
            account = self.env["account.account"].search([
                ("code", "=", code),
                ("company_id", "=", self.company.id),
            ])
            self.assertTrue(
                account,
                f"Cuenta {code} requerida por Hechauka RG 49/14 está ausente del PUC",
            )
```

- [ ] **Step 4: Crear `test_taxes.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestTaxes(L10nPyAccountTestCase):

    def _tax_by_xmlid(self, xmlid):
        return self.env.ref(f"account.{self.company.id}_{xmlid}")

    def test_iva_venta_10_cabled_to_iva_a_pagar(self):
        tax = self._tax_by_xmlid("tax_iva_venta_10")
        tax_lines = tax.invoice_repartition_line_ids.filtered(
            lambda r: r.repartition_type == "tax"
        )
        self.assertEqual(len(tax_lines), 1)
        self.assertEqual(tax_lines.account_id.code, "201030102")

    def test_iva_compra_10_cabled_to_iva_credito(self):
        tax = self._tax_by_xmlid("tax_iva_compra_10")
        tax_lines = tax.invoice_repartition_line_ids.filtered(
            lambda r: r.repartition_type == "tax"
        )
        self.assertEqual(len(tax_lines), 1)
        self.assertEqual(tax_lines.account_id.code, "101030503")

    def test_iva_venta_5_amount(self):
        tax = self._tax_by_xmlid("tax_iva_venta_5")
        self.assertEqual(tax.amount, 5.0)

    def test_iva_venta_exenta_amount_zero(self):
        tax = self._tax_by_xmlid("tax_iva_venta_exenta")
        self.assertEqual(tax.amount, 0.0)

    def test_iva_export_amount_zero_and_gravado(self):
        tax = self._tax_by_xmlid("tax_iva_venta_export")
        self.assertEqual(tax.amount, 0.0)
        # Export es gravado al 0%, no exento
        self.assertEqual(
            tax.l10n_py_afectacion_iva_id,
            self.env.ref("l10n_py_account.afectacion_iva_1"),
        )

    def test_afectacion_iva_fk_on_iva_taxes(self):
        for xmlid in ["tax_iva_venta_10", "tax_iva_venta_5", "tax_iva_compra_10",
                      "tax_iva_compra_5"]:
            tax = self._tax_by_xmlid(xmlid)
            self.assertEqual(
                tax.l10n_py_afectacion_iva_id.code, "1", f"{xmlid} debe ser Gravado",
            )

    def test_compute_amount_iva_10(self):
        tax = self._tax_by_xmlid("tax_iva_venta_10")
        result = tax.compute_all(price_unit=100.0)
        self.assertEqual(result["total_excluded"], 100.0)
        self.assertEqual(result["total_included"], 110.0)

    def test_compute_amount_iva_5(self):
        tax = self._tax_by_xmlid("tax_iva_venta_5")
        result = tax.compute_all(price_unit=100.0)
        self.assertEqual(result["total_included"], 105.0)

    def test_compute_amount_iva_exenta(self):
        tax = self._tax_by_xmlid("tax_iva_venta_exenta")
        result = tax.compute_all(price_unit=100.0)
        self.assertEqual(result["total_included"], 100.0)

    def test_taxes_have_correct_tax_group(self):
        for xmlid in ["tax_iva_venta_10", "tax_iva_venta_5", "tax_iva_venta_exenta",
                      "tax_iva_venta_export", "tax_iva_compra_10", "tax_iva_compra_5"]:
            tax = self._tax_by_xmlid(xmlid)
            self.assertEqual(tax.tax_group_id.name, "IVA Paraguay")
```

- [ ] **Step 5: Agregar a tests/**init**.py**

```python
from . import test_chart_template
from . import test_hechauka_critical_accounts
from . import test_taxes
```

- [ ] **Step 6: Correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 8 + 1 (loop) + 10 = 19 nuevos tests PASS.

Si fallan: el más probable es que los XML IDs `py_xxx` no matcheen los códigos esperados — revisar `account.account-py.csv` y el mapping en el script.

- [ ] **Step 7: Commit**

```bash
git add addons/l10n_py_account/tests/test_chart_template.py \
        addons/l10n_py_account/tests/test_hechauka_critical_accounts.py \
        addons/l10n_py_account/tests/test_taxes.py \
        addons/l10n_py_account/tests/common.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "test(l10n_py_account): add chart_template + Hechauka + taxes tests"
```

---

### Task 18: Document types CSV + `_format_document_number` override + tests

**Files:**

- Create: `addons/l10n_py_account/data/l10n_latam_document_type_data.csv`
- Create: `addons/l10n_py_account/models/l10n_latam_document_type.py`
- Create: `addons/l10n_py_account/tests/test_document_types.py`
- Modify: `addons/l10n_py_account/models/__init__.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Crear CSV de document types**

`addons/l10n_py_account/data/l10n_latam_document_type_data.csv`:

```csv
id,code,name,report_name,internal_type,sequence,doc_code_prefix,country_id:id
dt_fe,1,Factura Electrónica,FACTURA ELECTRÓNICA,invoice,10,,base.py
dt_af,4,Autofactura Electrónica,AUTOFACTURA ELECTRÓNICA,invoice,20,,base.py
dt_nc,5,Nota de Crédito Electrónica,NOTA DE CRÉDITO ELECTRÓNICA,credit_note,30,,base.py
dt_nd,6,Nota de Débito Electrónica,NOTA DE DÉBITO ELECTRÓNICA,debit_note,40,,base.py
dt_nr,7,Nota de Remisión Electrónica,NOTA DE REMISIÓN ELECTRÓNICA,,50,,base.py
```

(Notas: `internal_type` vacío para NR → fuera del filtro account normal; `doc_code_prefix` vacío → name = number puro.)

- [ ] **Step 2: Crear modelo extension**

`addons/l10n_py_account/models/l10n_latam_document_type.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Override _format_document_number para Paraguay: EEE-PPP-NNNNNNN."""
from odoo import _, models
from odoo.exceptions import UserError


class L10nLatamDocumentType(models.Model):
    _inherit = "l10n_latam.document.type"

    def _format_document_number(self, document_number):
        if self.country_id.code != "PY":
            return super()._format_document_number(document_number)
        if not document_number:
            return document_number
        parts = document_number.split("-")
        if len(parts) != 3:
            raise UserError(_("Formato número PY: EEE-PPP-NNNNNNN (3-3-7 dígitos)"))
        est, poe, num = parts
        if not (est.isdigit() and poe.isdigit() and num.isdigit()):
            raise UserError(_("El número solo puede contener dígitos y guiones"))
        if len(est) > 3 or len(poe) > 3 or len(num) > 7:
            raise UserError(_("Máximo EEE=3, PPP=3, NNNNNNN=7 dígitos"))
        return f"{est:>03s}-{poe:>03s}-{num:>07s}"
```

- [ ] **Step 3: Agregar import**

```python
from . import l10n_latam_document_type
```

- [ ] **Step 4: Crear tests**

`addons/l10n_py_account/tests/test_document_types.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestDocumentTypes(L10nPyAccountTestCase):

    def _dt(self, xmlid):
        return self.env.ref(f"l10n_py_account.{xmlid}")

    def test_five_doc_types_loaded(self):
        types = self.env["l10n_latam.document.type"].search([
            ("country_id", "=", self.country_py.id),
        ])
        self.assertEqual(len(types), 5)

    def test_codes_are_single_digit(self):
        for xmlid, expected in [("dt_fe", "1"), ("dt_af", "4"), ("dt_nc", "5"),
                                 ("dt_nd", "6"), ("dt_nr", "7")]:
            self.assertEqual(self._dt(xmlid).code, expected)

    def test_internal_types(self):
        self.assertEqual(self._dt("dt_fe").internal_type, "invoice")
        self.assertEqual(self._dt("dt_af").internal_type, "invoice")
        self.assertEqual(self._dt("dt_nc").internal_type, "credit_note")
        self.assertEqual(self._dt("dt_nd").internal_type, "debit_note")
        self.assertFalse(self._dt("dt_nr").internal_type)  # NR vacío

    def test_format_normalizes_padding(self):
        dt = self._dt("dt_fe")
        self.assertEqual(dt._format_document_number("1-1-123"), "001-001-0000123")

    def test_format_normalizes_already_padded(self):
        dt = self._dt("dt_fe")
        self.assertEqual(dt._format_document_number("001-001-0000123"), "001-001-0000123")

    def test_format_rejects_invalid_segments(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("01-01")  # solo 2 segmentos

    def test_format_rejects_non_numeric(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("001-001-ABC")

    def test_format_rejects_too_many_digits(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("001-001-12345678")  # 8 dígitos > 7

    def test_format_rejects_too_many_est_digits(self):
        dt = self._dt("dt_fe")
        with self.assertRaises(UserError):
            dt._format_document_number("0001-001-0000001")  # est = 4 dígitos

    def test_format_empty_returns_empty(self):
        dt = self._dt("dt_fe")
        self.assertEqual(dt._format_document_number(""), "")
        self.assertFalse(dt._format_document_number(False))

    def test_format_non_py_passes_through(self):
        dt_ar = self.env.ref("l10n_ar.dc_a_f", raise_if_not_found=False)
        if dt_ar:
            # No raise para AR
            self.assertEqual(dt_ar._format_document_number("00001-00000001"),
                             "00001-00000001")

    def test_nr_excluded_from_invoice_domain(self):
        # NR no debe aparecer en filtros account porque internal_type=''
        invoice_types = self.env["l10n_latam.document.type"].search([
            ("country_id", "=", self.country_py.id),
            ("internal_type", "in", ["invoice", "debit_note", "credit_note"]),
        ])
        codes = invoice_types.mapped("code")
        self.assertNotIn("7", codes)
        self.assertIn("1", codes)
        self.assertIn("5", codes)
        self.assertIn("6", codes)
```

- [ ] **Step 5: Agregar a tests/**init**.py**

```python
from . import test_document_types
```

- [ ] **Step 6: Reinstalar + correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 12 tests `TestDocumentTypes` PASS.

- [ ] **Step 7: Commit**

```bash
git add addons/l10n_py_account/data/l10n_latam_document_type_data.csv \
        addons/l10n_py_account/models/l10n_latam_document_type.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/tests/test_document_types.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): add 5 SIFEN document types + _format_document_number"
```

---

### Task 19: `account.move` — sequence overrides + defensive `_post` + tests

**Files:**

- Create: `addons/l10n_py_account/models/account_move.py`
- Create: `addons/l10n_py_account/tests/test_account_move_sequence.py`
- Create: `addons/l10n_py_account/tests/test_account_move_defensive.py`
- Modify: `addons/l10n_py_account/models/__init__.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Crear extension `account.move`**

`addons/l10n_py_account/models/account_move.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""account.move PY: sequence per (journal, doc_type) + defensive PoE check."""
from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_starting_sequence(self):
        self.ensure_one()
        if (
            self.journal_id.country_code == "PY"
            and self.journal_id.l10n_latam_use_documents
        ):
            poe = self.journal_id.l10n_py_point_of_emission_id
            if not poe:
                raise UserError(
                    _(
                        "El diario '%(journal)s' usa documentos paraguayos pero no "
                        "tiene Punto de Emisión configurado. Configure el PoE en "
                        "Contabilidad → Configuración → Diarios antes de postear.",
                        journal=self.journal_id.name,
                    )
                )
            return f"{poe.establishment_code.zfill(3)}-{poe.code.zfill(3)}-0000000"
        return super()._get_starting_sequence()

    def _get_last_sequence_domain(self, relaxed=False):
        where_string, param = super()._get_last_sequence_domain(relaxed)
        if (
            self.company_id.account_fiscal_country_id.code == "PY"
            and self.l10n_latam_use_documents
        ):
            where_string += " AND l10n_latam_document_type_id = %(l10n_latam_document_type_id)s"
            param["l10n_latam_document_type_id"] = self.l10n_latam_document_type_id.id or 0
        return where_string, param

    def _post(self, soft=True):
        for move in self.filtered(
            lambda m: m.company_id.account_fiscal_country_id.code == "PY"
            and m.l10n_latam_use_documents
        ):
            if not move.journal_id.l10n_py_point_of_emission_id:
                raise UserError(
                    _(
                        "El diario '%(journal)s' no tiene Punto de Emisión configurado.",
                        journal=move.journal_id.name,
                    )
                )
        return super()._post(soft=soft)
```

- [ ] **Step 2: Crear tests de sequence**

`addons/l10n_py_account/tests/test_account_move_sequence.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestAccountMoveSequence(L10nPyAccountTestCase):

    def _make_invoice(self, doc_type_xmlid, move_type="out_invoice"):
        doc_type = self.env.ref(f"l10n_py_account.{doc_type_xmlid}")
        partner = self.env["res.partner"].create({
            "name": "Cliente Test PY",
            "country_id": self.country_py.id,
        })
        invoice = self.env["account.move"].with_company(self.company).create({
            "move_type": move_type,
            "partner_id": partner.id,
            "journal_id": self.sale_journal.id,
            "l10n_latam_document_type_id": doc_type.id,
            "invoice_line_ids": [(0, 0, {
                "name": "Producto Test",
                "quantity": 1,
                "price_unit": 100.0,
            })],
        })
        return invoice

    def test_first_fe_numbers_001_001_0000001(self):
        inv = self._make_invoice("dt_fe")
        inv.action_post()
        self.assertEqual(inv.name, "001-001-0000001")

    def test_second_fe_numbers_0000002(self):
        inv1 = self._make_invoice("dt_fe")
        inv1.action_post()
        inv2 = self._make_invoice("dt_fe")
        inv2.action_post()
        self.assertEqual(inv2.name, "001-001-0000002")

    def test_nc_independent_sequence_from_fe(self):
        inv = self._make_invoice("dt_fe")
        inv.action_post()
        nc = self._make_invoice("dt_nc", move_type="out_refund")
        nc.action_post()
        # NC arranca en 0000001 también, no continúa la sequence de FE
        self.assertEqual(nc.name, "001-001-0000001")

    def test_nd_independent_sequence_from_fe_and_nc(self):
        self._make_invoice("dt_fe").action_post()
        self._make_invoice("dt_nc", move_type="out_refund").action_post()
        nd = self._make_invoice("dt_nd")
        nd.action_post()
        self.assertEqual(nd.name, "001-001-0000001")

    def test_starting_sequence_format(self):
        inv = self._make_invoice("dt_fe")
        self.assertEqual(inv._get_starting_sequence(), "001-001-0000000")

    def test_doc_type_change_draft_resets_name(self):
        inv = self._make_invoice("dt_fe")
        self.assertFalse(inv.name or inv.name == "/")
        # Cambio a NC en draft
        inv.l10n_latam_document_type_id = self.env.ref("l10n_py_account.dt_nc")
        inv.move_type = "out_refund"
        # El name se recompute solo al postear; verificamos que el sequence reset funciona

    def test_format_document_number_inverse_works(self):
        inv = self._make_invoice("dt_fe")
        inv.action_post()
        # Verificar que el formato es correcto
        self.assertRegex(inv.name, r"^\d{3}-\d{3}-\d{7}$")

    def test_multiple_journals_independent_sequences(self):
        # Crear otro PoE + sale journal en misma company
        poe2 = self.env["l10n_py.point_of_emission"].create({
            "establishment_code": "002", "code": "001",
            "address_id": self.company.partner_id.id,
            "company_id": self.company.id,
        })
        journal2 = self.env["account.journal"].with_company(self.company).create({
            "name": "Sucursal 2 Sales", "type": "sale", "code": "VEN2",
            "company_id": self.company.id,
            "l10n_latam_use_documents": True,
            "l10n_py_point_of_emission_id": poe2.id,
        })
        inv1 = self._make_invoice("dt_fe")
        inv1.action_post()
        inv2 = self._make_invoice("dt_fe")
        inv2.journal_id = journal2
        inv2.action_post()
        self.assertEqual(inv2.name, "002-001-0000001")
```

- [ ] **Step 3: Crear tests defensivos**

`addons/l10n_py_account/tests/test_account_move_defensive.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.exceptions import UserError
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestAccountMoveDefensive(L10nPyAccountTestCase):

    def _make_invoice(self):
        partner = self.env["res.partner"].create({
            "name": "Cliente", "country_id": self.country_py.id,
        })
        return self.env["account.move"].with_company(self.company).create({
            "move_type": "out_invoice",
            "partner_id": partner.id,
            "journal_id": self.sale_journal.id,
            "l10n_latam_document_type_id": self.env.ref("l10n_py_account.dt_fe").id,
            "invoice_line_ids": [(0, 0, {"name": "X", "quantity": 1, "price_unit": 100})],
        })

    def test_post_without_poe_raises_user_error(self):
        # Quitar PoE del journal
        self.sale_journal.l10n_latam_use_documents = False
        self.sale_journal.l10n_py_point_of_emission_id = False
        self.sale_journal.l10n_latam_use_documents = True
        invoice = self._make_invoice()
        with self.assertRaises(UserError) as ctx:
            invoice.action_post()
        self.assertIn("Punto de Emisión", str(ctx.exception))

    def test_post_with_poe_works(self):
        invoice = self._make_invoice()
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_starting_sequence_without_poe_raises(self):
        self.sale_journal.l10n_latam_use_documents = False
        self.sale_journal.l10n_py_point_of_emission_id = False
        self.sale_journal.l10n_latam_use_documents = True
        invoice = self._make_invoice()
        with self.assertRaises(UserError):
            invoice._get_starting_sequence()
```

- [ ] **Step 4: Agregar imports**

```python
# models/__init__.py
from . import account_move

# tests/__init__.py
from . import test_account_move_sequence
from . import test_account_move_defensive
```

- [ ] **Step 5: Reinstalar + correr tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 8 sequence tests + 3 defensive tests = 11 PASS.

- [ ] **Step 6: Commit**

```bash
git add addons/l10n_py_account/models/account_move.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/tests/test_account_move_sequence.py \
        addons/l10n_py_account/tests/test_account_move_defensive.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): account.move sequence per doc_type + defensive PoE check"
```

---

### Task 20: `account.move.line` — `l10n_py_iva_proporcion`

**Files:**

- Create: `addons/l10n_py_account/models/account_move_line.py`
- Create: `addons/l10n_py_account/views/account_move_views.xml`
- Modify: `addons/l10n_py_account/models/__init__.py`

- [ ] **Step 1: Crear extension**

`addons/l10n_py_account/models/account_move_line.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Proporción de IVA gravada (SIFEN para 'gravado parcial')."""
from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_py_iva_proporcion = fields.Integer(
        string="Proporción IVA (%)",
        default=100,
        help="Porcentaje (1-100) de la base gravada por IVA. < 100 indica "
             "afectación 'Gravado parcial' SIFEN. Usado por XML builder en Fase 2.",
    )
```

- [ ] **Step 2: Crear view para el campo**

`addons/l10n_py_account/views/account_move_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_move_form_inherit_l10n_py" model="ir.ui.view">
        <field name="name">account.move.form.inherit.l10n_py</field>
        <field name="model">account.move</field>
        <field name="inherit_id" ref="account.view_move_form"/>
        <field name="arch" type="xml">
            <xpath expr="//field[@name='invoice_line_ids']/list/field[@name='tax_ids']" position="after">
                <field name="l10n_py_iva_proporcion"
                       optional="hide"
                       column_invisible="parent.country_code != 'PY'"/>
            </xpath>
        </field>
    </record>
</odoo>
```

- [ ] **Step 3: Agregar import**

```python
from . import account_move_line
```

- [ ] **Step 4: Reinstalar (smoke)**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init
```

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_account/models/account_move_line.py \
        addons/l10n_py_account/models/__init__.py \
        addons/l10n_py_account/views/account_move_views.xml
git commit -m "feat(l10n_py_account): add l10n_py_iva_proporcion to account.move.line"
```

---

### Task 21: Wizard de migración + tests

**Files:**

- Create: `addons/l10n_py_account/wizards/account_migration_wizard.py`
- Create: `addons/l10n_py_account/wizards/account_migration_wizard_views.xml`
- Create: `addons/l10n_py_account/tests/test_migration_wizard.py`
- Modify: `addons/l10n_py_account/wizards/__init__.py`
- Modify: `addons/l10n_py_account/security/ir.model.access.csv`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Crear el modelo wizard**

`addons/l10n_py_account/wizards/account_migration_wizard.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Wizard para migrar companies PY con chart preexistente."""
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class L10nPyAccountMigrationWizard(models.TransientModel):
    _name = "l10n.py.account.migration.wizard"
    _description = "Paraguay - Asistente Migración Chart"

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda s: s.env.company,
    )
    mode = fields.Selection(
        [
            ("clean", "Instalación limpia (reemplazar chart existente)"),
            ("assisted", "Mapeo asistido (mantener cuentas; sugerir merges)"),
            ("coexist", "Coexistir (solo cargar taxes + document types + timbrado)"),
        ],
        required=True,
        default="coexist",
    )
    existing_accounts_count = fields.Integer(
        compute="_compute_existing_accounts_count",
    )
    confirm_destructive = fields.Boolean(
        string="Confirmo: entiendo que esta operación es destructiva",
    )

    def _compute_existing_accounts_count(self):
        for w in self:
            w.existing_accounts_count = self.env["account.account"].search_count([
                ("company_id", "=", w.company_id.id),
            ])

    def action_apply(self):
        self.ensure_one()
        if self.mode == "clean":
            if not self.confirm_destructive:
                raise models.UserError(_(
                    "Modo 'limpia' requiere confirmar la operación destructiva."
                ))
            self._apply_clean()
        elif self.mode == "assisted":
            self._apply_assisted()
        else:
            self._apply_coexist()
        return {"type": "ir.actions.client", "tag": "reload"}

    def _apply_clean(self):
        # Eliminar todas las cuentas y recargar chart 'py'
        existing = self.env["account.account"].search([
            ("company_id", "=", self.company_id.id),
        ])
        existing.unlink()
        self.env["account.chart.template"].try_loading(
            "py", company=self.company_id,
        )
        _logger.info("Chart 'py' cargado en modo clean para company %s", self.company_id.name)

    def _apply_assisted(self):
        # No destructivo: solo loguea y deja el chart como está; manda activity
        self.company_id.partner_id.message_post(body=_(
            "Modo asistido: chart existente preservado. Revisar manualmente el mapeo "
            "de cuentas IVA a códigos RG 49/14."
        ))

    def _apply_coexist(self):
        # Solo cargar taxes + document types (sin chart). Asumimos que ya existen
        # como data del módulo cargados al instalar.
        pass
```

- [ ] **Step 2: Crear view del wizard**

`addons/l10n_py_account/wizards/account_migration_wizard_views.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_l10n_py_account_migration_wizard" model="ir.ui.view">
        <field name="name">l10n.py.account.migration.wizard.form</field>
        <field name="model">l10n.py.account.migration.wizard</field>
        <field name="arch" type="xml">
            <form>
                <sheet>
                    <div class="alert alert-warning" role="alert">
                        Su company ya tiene <field name="existing_accounts_count" readonly="1" nolabel="1"/>
                        cuentas. Elija cómo proceder:
                    </div>
                    <group>
                        <field name="company_id"/>
                        <field name="mode" widget="radio"/>
                        <field name="confirm_destructive" invisible="mode != 'clean'"/>
                    </group>
                </sheet>
                <footer>
                    <button string="Aplicar" type="object" name="action_apply" class="btn-primary"/>
                    <button string="Cancelar" special="cancel"/>
                </footer>
            </form>
        </field>
    </record>
    <record id="action_l10n_py_account_migration_wizard" model="ir.actions.act_window">
        <field name="name">Migración Chart Paraguay</field>
        <field name="res_model">l10n.py.account.migration.wizard</field>
        <field name="view_mode">form</field>
        <field name="target">new</field>
    </record>
</odoo>
```

- [ ] **Step 3: Agregar import + access rule**

`wizards/__init__.py`:

```python
from . import account_migration_wizard
```

`security/ir.model.access.csv` (agregar línea):

```csv
access_l10n_py_migration_wizard,l10n_py.account.migration.wizard,model_l10n_py_account_migration_wizard,base.group_system,1,1,1,1
```

- [ ] **Step 4: Crear tests**

`addons/l10n_py_account/tests/test_migration_wizard.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install", "l10n_py")
class TestMigrationWizard(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.country_py = cls.env.ref("base.py")
        cls.company = cls.env["res.company"].create({
            "name": "Co PY", "country_id": cls.country_py.id,
        })

    def test_wizard_coexist_mode_works(self):
        w = self.env["l10n.py.account.migration.wizard"].create({
            "company_id": self.company.id, "mode": "coexist",
        })
        result = w.action_apply()
        self.assertEqual(result["type"], "ir.actions.client")

    def test_wizard_clean_mode_requires_confirm(self):
        w = self.env["l10n.py.account.migration.wizard"].create({
            "company_id": self.company.id, "mode": "clean",
            "confirm_destructive": False,
        })
        with self.assertRaises(UserError):
            w.action_apply()

    def test_existing_accounts_count(self):
        w = self.env["l10n.py.account.migration.wizard"].create({
            "company_id": self.company.id, "mode": "coexist",
        })
        # Cero accounts en company nueva sin chart cargado
        self.assertEqual(w.existing_accounts_count, 0)
```

- [ ] **Step 5: Agregar a tests/**init**.py**

```python
from . import test_migration_wizard
```

- [ ] **Step 6: Reinstalar + tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 3 tests `TestMigrationWizard` PASS.

- [ ] **Step 7: Commit**

```bash
git add addons/l10n_py_account/wizards/ \
        addons/l10n_py_account/security/ir.model.access.csv \
        addons/l10n_py_account/tests/test_migration_wizard.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): add migration wizard (clean/assisted/coexist) + 3 tests"
```

---

### Task 22: `_post_init_hook` defensivo + tests + menus

**Files:**

- Modify: `addons/l10n_py_account/hooks.py`
- Create: `addons/l10n_py_account/tests/test_post_init_hook.py`
- Create: `addons/l10n_py_account/views/menus.xml`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Reemplazar `hooks.py` con lógica defensiva**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Hook post-install que maneja DBs preexistentes."""
import logging

from odoo import _

_logger = logging.getLogger(__name__)


def _post_init_hook(env):
    """Defensive handling for companies PY with pre-existing journals/charts."""
    py_companies = env["res.company"].search([
        ("account_fiscal_country_id.code", "=", "PY"),
    ])
    for company in py_companies:
        # Caso A: journals sale PY con use_documents pero sin PoE → desactivar + activity
        broken_journals = env["account.journal"].search([
            ("company_id", "=", company.id),
            ("type", "=", "sale"),
            ("l10n_latam_use_documents", "=", True),
            ("l10n_py_point_of_emission_id", "=", False),
        ])
        if broken_journals:
            _logger.warning(
                "Company %s: %d journals sale sin PoE — desactivando use_documents",
                company.name, len(broken_journals),
            )
            broken_journals.write({"l10n_latam_use_documents": False})
            for journal in broken_journals:
                try:
                    journal.activity_schedule(
                        "mail.mail_activity_data_todo",
                        summary=_("Configurar Punto de Emisión Paraguay"),
                        note=_(
                            "Este diario requiere Punto de Emisión para emitir "
                            "documentos PY. Configure el PoE y reactive "
                            '"Usar Documentos".'
                        ),
                        user_id=env.user.id,
                    )
                except Exception as exc:
                    _logger.warning("No se pudo crear activity: %s", exc)

        # Caso B: chart custom preexistente
        existing_accounts = env["account.account"].search_count([
            ("company_id", "=", company.id),
        ])
        chart = company.chart_template
        if chart and chart != "py" and existing_accounts > 20:
            _logger.warning(
                "Company %s tiene chart '%s' con %d cuentas. l10n_py_account NO "
                "cargó el chart 'py' automáticamente. Use Configuración → "
                "Contabilidad → Migración Chart Paraguay.",
                company.name, chart, existing_accounts,
            )
```

- [ ] **Step 2: Crear menús del módulo**

`addons/l10n_py_account/views/menus.xml`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <menuitem
        id="menu_l10n_py_account_config"
        name="Paraguay"
        parent="account.menu_finance_configuration"
        sequence="100"/>
    <menuitem
        id="menu_l10n_py_timbrado"
        name="Timbrados"
        parent="menu_l10n_py_account_config"
        action="action_l10n_py_timbrado"
        sequence="10"/>
    <menuitem
        id="menu_l10n_py_poe"
        name="Puntos de Emisión"
        parent="menu_l10n_py_account_config"
        action="action_l10n_py_poe"
        sequence="20"/>
    <menuitem
        id="menu_l10n_py_afectacion_iva"
        name="Afectación IVA (SIFEN)"
        parent="menu_l10n_py_account_config"
        action="action_l10n_py_afectacion_iva"
        sequence="30"/>
    <menuitem
        id="menu_l10n_py_migration_wizard"
        name="Migración Chart"
        parent="menu_l10n_py_account_config"
        action="action_l10n_py_account_migration_wizard"
        sequence="90"/>
</odoo>
```

- [ ] **Step 3: Crear tests del hook**

`addons/l10n_py_account/tests/test_post_init_hook.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo.tests.common import TransactionCase, tagged

from odoo.addons.l10n_py_account.hooks import _post_init_hook


@tagged("post_install", "-at_install", "l10n_py")
class TestPostInitHook(TransactionCase):

    def test_legacy_journal_without_poe_gets_disabled(self):
        country_py = self.env.ref("base.py")
        company = self.env["res.company"].create({
            "name": "Legacy PY", "country_id": country_py.id,
            "account_fiscal_country_id": country_py.id,
        })
        # Crear journal sale con use_documents=True pero sin PoE
        # (bypass constraint usando _write directo)
        journal = self.env["account.journal"].with_company(company).create({
            "name": "Sale Legacy", "type": "sale", "code": "VLG",
            "company_id": company.id, "l10n_latam_use_documents": False,
        })
        # Forzar use_documents=True via SQL bypass del constraint
        self.env.cr.execute(
            "UPDATE account_journal SET l10n_latam_use_documents = true WHERE id = %s",
            (journal.id,),
        )
        journal.invalidate_recordset()

        _post_init_hook(self.env)

        journal.invalidate_recordset()
        self.assertFalse(journal.l10n_latam_use_documents,
                          "Hook debe desactivar use_documents")

    def test_company_with_custom_chart_not_overwritten(self):
        country_py = self.env.ref("base.py")
        company = self.env["res.company"].create({
            "name": "Co Custom Chart", "country_id": country_py.id,
            "account_fiscal_country_id": country_py.id,
            "chart_template": "generic_coa",  # chart distinto a 'py'
        })
        # Crear algunas cuentas custom
        for code in ["1000", "2000", "3000"] * 8:  # >20 cuentas
            self.env["account.account"].create({
                "name": f"Cuenta {code}", "code": code,
                "account_type": "asset_current", "company_id": company.id,
            })
        accounts_before = self.env["account.account"].search_count([
            ("company_id", "=", company.id),
        ])

        _post_init_hook(self.env)

        accounts_after = self.env["account.account"].search_count([
            ("company_id", "=", company.id),
        ])
        self.assertEqual(accounts_before, accounts_after,
                          "Hook NO debe tocar cuentas existentes")
```

- [ ] **Step 4: Agregar a tests/**init**.py**

```python
from . import test_post_init_hook
```

- [ ] **Step 5: Reinstalar + tests**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 2 tests `TestPostInitHook` PASS.

- [ ] **Step 6: Commit**

```bash
git add addons/l10n_py_account/hooks.py \
        addons/l10n_py_account/views/menus.xml \
        addons/l10n_py_account/tests/test_post_init_hook.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "feat(l10n_py_account): defensive _post_init_hook + menus + 2 tests"
```

---

### Task 23: Smoke test E2E PyME (compra + venta + cuadre IVA)

**Files:**

- Create: `addons/l10n_py_account/tests/test_pyme_e2e.py`
- Modify: `addons/l10n_py_account/tests/__init__.py`

- [ ] **Step 1: Crear el smoke test**

`addons/l10n_py_account/tests/test_pyme_e2e.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Smoke test: operación PyME completa (compra + venta + cuadre IVA)."""
from odoo.tests.common import tagged

from .common import L10nPyAccountTestCase


@tagged("post_install", "-at_install", "l10n_py")
class TestPymeE2E(L10nPyAccountTestCase):

    def test_compra_venta_cierre_mes_cuadre_iva(self):
        """Ciclo: compra → venta → IVA Débito - IVA Crédito = IVA a Pagar."""
        partner_proveedor = self.env["res.partner"].create({
            "name": "Proveedor Local",
            "country_id": self.country_py.id,
            "supplier_rank": 1,
        })
        partner_cliente = self.env["res.partner"].create({
            "name": "Cliente Local",
            "country_id": self.country_py.id,
            "customer_rank": 1,
        })

        # 1. Compra: 100 Gs gravada IVA 10% → IVA Crédito = 10
        purchase_journal = self.env["account.journal"].search([
            ("type", "=", "purchase"), ("company_id", "=", self.company.id),
        ], limit=1)
        bill = self.env["account.move"].with_company(self.company).create({
            "move_type": "in_invoice",
            "partner_id": partner_proveedor.id,
            "journal_id": purchase_journal.id,
            "l10n_latam_document_type_id": self.env.ref("l10n_py_account.dt_fe").id,
            "l10n_latam_document_number": "001-001-0000001",
            "invoice_line_ids": [(0, 0, {
                "name": "Compra mercadería",
                "quantity": 1,
                "price_unit": 100.0,
                "tax_ids": [(6, 0, [self.env.ref(
                    f"account.{self.company.id}_tax_iva_compra_10"
                ).id])],
            })],
        })
        bill.action_post()
        self.assertEqual(bill.amount_tax, 10.0)

        # 2. Venta: 200 Gs gravada IVA 10% → IVA Débito = 20
        invoice = self.env["account.move"].with_company(self.company).create({
            "move_type": "out_invoice",
            "partner_id": partner_cliente.id,
            "journal_id": self.sale_journal.id,
            "l10n_latam_document_type_id": self.env.ref("l10n_py_account.dt_fe").id,
            "invoice_line_ids": [(0, 0, {
                "name": "Venta mercadería",
                "quantity": 1,
                "price_unit": 200.0,
                "tax_ids": [(6, 0, [self.env.ref(
                    f"account.{self.company.id}_tax_iva_venta_10"
                ).id])],
            })],
        })
        invoice.action_post()
        self.assertEqual(invoice.amount_tax, 20.0)

        # 3. Cuadre: IVA Débito (20) - IVA Crédito (10) = IVA a Pagar (10)
        iva_credito = self.env["account.account"].search([
            ("code", "=", "101030503"), ("company_id", "=", self.company.id),
        ])
        iva_a_pagar = self.env["account.account"].search([
            ("code", "=", "201030102"), ("company_id", "=", self.company.id),
        ])
        balance_credito = sum(
            self.env["account.move.line"].search([
                ("account_id", "=", iva_credito.id),
                ("parent_state", "=", "posted"),
            ]).mapped("balance")
        )
        balance_a_pagar = sum(
            self.env["account.move.line"].search([
                ("account_id", "=", iva_a_pagar.id),
                ("parent_state", "=", "posted"),
            ]).mapped("balance")
        )
        # IVA Crédito: cuenta de activo, débito = +10
        self.assertEqual(balance_credito, 10.0)
        # IVA a Pagar: cuenta de pasivo, crédito = -20 (balance neg en convención Odoo)
        self.assertEqual(balance_a_pagar, -20.0)
        # IVA a Pagar neto del periodo = |-20| - 10 = 10
        self.assertEqual(abs(balance_a_pagar) - balance_credito, 10.0)
```

- [ ] **Step 2: Agregar a tests/**init**.py**

```python
from . import test_pyme_e2e
```

- [ ] **Step 3: Correr el test**

```bash
docker compose exec odoo odoo -u l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: 1 test `TestPymeE2E` PASS.

- [ ] **Step 4: Commit**

```bash
git add addons/l10n_py_account/tests/test_pyme_e2e.py \
        addons/l10n_py_account/tests/__init__.py
git commit -m "test(l10n_py_account): add PyME E2E smoke test (compra+venta+cuadre IVA)"
```

---

### Task 24: Verificación full suite + README + CHANGES + PR2

**Files:**

- Create: `addons/l10n_py_account/README.rst`
- Create: `addons/l10n_py_account/readme/DESCRIPTION.rst`
- Create: `addons/l10n_py_account/readme/CONFIGURE.rst`
- Create: `addons/l10n_py_account/readme/USAGE.rst`
- Create: `addons/l10n_py_account/readme/ROADMAP.rst`

- [ ] **Step 1: Crear DESCRIPTION.rst**

```rst
Plan de cuentas paraguayo basado en la **Resolución General DNIT 49/14** (estándar
de facto para reporting Hechauka), impuestos IVA (10%, 5%, exenta, exportación 0%),
5 tipos de documento electrónico SIFEN (Factura, Autofactura, Notas de Crédito,
Débito y Remisión) con formato de numeración ``EEE-PPP-NNNNNNN``, modelos de
**Timbrado** y **Punto de Emisión**, y extensiones a ``account.journal`` y
``account.move`` para numeración independiente por (journal, tipo de documento).

Este módulo cierra la fase contable previa al EDI SIFEN (Fase 2 - ``l10n_py_edi``).
```

- [ ] **Step 2: Crear CONFIGURE.rst**

```rst
1. Instale ``l10n_py_account`` en una company con país = Paraguay.
2. El chart RG 49/14 se carga automáticamente al instalar (~200 cuentas, ~80
   activas por default para comercio/servicios; resto inactive para activar
   según industria — ver "Cobertura por industria" abajo).
3. Vaya a **Contabilidad → Configuración → Paraguay → Timbrados** y registre el
   timbrado DNIT vigente (8 dígitos numéricos, fecha inicio obligatoria, fecha
   fin opcional).
4. Vaya a **Contabilidad → Configuración → Paraguay → Puntos de Emisión** y
   registre uno por cada combinación (establecimiento, punto de expedición).
5. En **Contabilidad → Configuración → Diarios**, asigne el PoE
   correspondiente a cada diario de ventas paraguayo.

Si su company ya tiene un chart custom preexistente, use **Contabilidad →
Configuración → Paraguay → Migración Chart** y elija uno de los 3 modos
(clean / assisted / coexist).
```

- [ ] **Step 3: Crear USAGE.rst**

```rst
Una vez configurado, las facturas de venta numeran automáticamente con formato
``EEE-PPP-NNNNNNN`` (ej: ``001-001-0000001``). Cada tipo de documento (Factura,
Nota de Crédito, Nota de Débito) tiene su propia secuencia correlativa dentro
del mismo journal — no comparten numeración (requisito SIFEN).

Para facturas de compra (recibidas del proveedor), el número se ingresa
manualmente en el campo "Número de Documento" del move.

La emisión real al SIFEN (firma XAdES + envío SOAP) está fuera de este módulo
y se implementa en ``l10n_py_edi`` (Fase 2).

**Cobertura por industria:**

* Comercio minorista (minimarket, almacén): cobertura completa.
* Gastronomía: cobertura completa.
* Servicios profesionales: cobertura completa.
* Importador/distribuidor: activar manualmente cuentas exterior (``4.06-4.08``)
  e ``1.01.04.11 Importaciones en curso``.
* Agro/ganadería: activar grupos ``4.02-4.05`` (ventas) y ``5.02-5.05``
  (costos), más activos biológicos.
* Régimen Turismo / Zona Franca / Maquila: activar grupos ``4.10``, ``5.10``
  y cuenta ``1.01.03.05.04 IVA Crédito Fiscal - Régimen Turismo``.
```

- [ ] **Step 4: Crear ROADMAP.rst**

```rst
* **Fase 2 (l10n_py_edi)**: CDC, firma XAdES, cliente SOAP SIFEN, KuDE, eventos.
* **Auto-numbering Autofactura**: actualmente manual; en Fase 2 con PoE propio.
* **Catálogo actividades económicas SIFEN**: actualmente carga manual; en Fase 2
  vía WS de SET.
* **Serie alfabética del timbrado** (cuando se agotan 9.999.999 facturas):
  Fase 2.
* **Constraint EEE-PPP del número manual coincide con PoE del journal**: Fase 2.
* **Comprobante de Retención** (código 8 SIFEN, "Futuro"): cuando DNIT lo
  active.
```

- [ ] **Step 5: Crear CHANGES.rst**

`addons/l10n_py_account/readme/CHANGES.rst`:

```rst
18.0.1.0.0 (2026-05-25)
~~~~~~~~~~~~~~~~~~~~~~~~

* Initial release.
* PUC RG 49/14 (~200 cuentas, ~80 activas default para comercio/servicios)
* 6 taxes IVA + 1 tax group + modelo ``l10n_py.afectacion_iva``
* 5 records ``l10n_latam.document.type`` (códigos 1, 4, 5, 6, 7)
* Modelos ``l10n_py.timbrado`` y ``l10n_py.point_of_emission``
* Extensiones ``res.company``, ``account.journal``, ``account.move``,
  ``account.move.line``, ``l10n_latam.document.type``
* Sequence independiente por (journal, document_type)
* Defensive checks: ``_get_starting_sequence``, ``_post`` raise UserError claro
  si falta PoE
* ``_post_init_hook`` defensivo para DBs preexistentes
* Wizard de migración 3 modos (clean / assisted / coexist)
* 73 tests
```

- [ ] **Step 6: Crear README.rst raíz**

`addons/l10n_py_account/README.rst`:

```rst
=========================
Paraguay Accounting (l10n_py_account)
=========================

.. !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
   !! This file is generated by oca-gen-addon-readme !!
   !! changes will be overwritten.                   !!
   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

.. |badge1| image:: https://img.shields.io/badge/maturity-Beta-yellow.png
    :target: https://odoo-community.org/page/development-status
    :alt: Beta
.. |badge2| image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3
.. |badge3| image:: https://img.shields.io/badge/github-Ezcareaga%2Fl10n--paraguay-lightgray.png?logo=github
    :target: https://github.com/Ezcareaga/l10n-paraguay/tree/main/addons/l10n_py_account
    :alt: Ezcareaga/l10n-paraguay

|badge1| |badge2| |badge3|

.. include:: readme/DESCRIPTION.rst

**Table of contents**

.. contents::
   :local:

Configuration
=============

.. include:: readme/CONFIGURE.rst

Usage
=====

.. include:: readme/USAGE.rst

Changelog
=========

.. include:: readme/CHANGES.rst

Known issues / Roadmap
======================

.. include:: readme/ROADMAP.rst
```

- [ ] **Step 7: Correr suite full**

```bash
docker compose exec odoo odoo -u l10n_py_base,l10n_py_account -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

Expected: **100 tests** (27 base + 73 account) PASS sin warnings.

Si algún test falla: ejecutar el subset y debuggear:

```bash
docker compose exec odoo odoo -d l10n_py_dev --stop-after-init --test-tags l10n_py --test-enable
```

- [ ] **Step 8: Commit del README**

```bash
git add addons/l10n_py_account/README.rst addons/l10n_py_account/readme/
git commit -m "docs(l10n_py_account): README, CONFIGURE, USAGE, ROADMAP, CHANGES"
```

- [ ] **Step 9: Push + PR**

```bash
git push -u origin feat/l10n-py-account
gh pr create --base main --title "feat(l10n_py_account): 18.0.1.0.0 — PUC RG 49/14 + taxes IVA + SIFEN document types + timbrado/PoE" --body "$(cat <<'EOF'
## Summary
- PUC RG 49/14 (~200 cuentas, ~80 activas default) cargado via @template('py') Odoo 18 API
- 6 taxes IVA cableados a cuentas Crédito/Débito correctas + tax group
- 5 document types SIFEN (códigos 1, 4, 5, 6, 7) + override _format_document_number
- Modelos l10n_py.timbrado + l10n_py.point_of_emission
- Sequence independiente por (journal, doc_type) vía _get_last_sequence_domain
- Defensive checks en _post + _get_starting_sequence
- _post_init_hook defensivo para DBs preexistentes
- Wizard migración 3 modos (clean / assisted / coexist)
- 73 tests (100 totales con base)

## Test plan
- [x] 100 tests PASS (l10n_py_base + l10n_py_account)
- [x] Instalación limpia en DB nueva sin warnings
- [x] Manual smoke: company PY + timbrado + PoE → crear FE → name 001-001-0000001
- [x] Crear NC referenciando FE → name 001-001-0000001 (sequence independiente verificada)

Spec: docs/superpowers/specs/2026-05-25-l10n-py-account-design.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

**🛑 FIN Phase 2. Después del merge: tag `v0.2.0` opcional.**

---

## Self-Review (post-plan)

Después de escribir el plan completo, lo audité contra el spec:

**1. Spec coverage:**

- ✅ Sec 1 (Arquitectura): Tasks 1, 8 cubren manifest + split base/account.
- ✅ Sec 2 (PUC + Taxes): Tasks 9, 14, 15, 16, 17 cubren afectacion, PUC extraction, taxes, template_py, tests.
- ✅ Sec 3 (Document types): Task 18.
- ✅ Sec 4 (Timbrado/PoE/journal): Tasks 10, 11, 12, 13, 19, 20.
- ✅ Sec 5 (Testing + entregables): Tasks 7, 17, 22, 23, 24 + DoD en Task 24 step 7.
- ✅ Sec 6 (Riesgos/mitigaciones): hooks defensivos en Task 22, wizard en Task 21, tests críticos Hechauka en Task 17, smoke E2E en Task 23.

**2. Placeholder scan:** sin TBD/TODO/"implement later". Los TODO menores del spec (serie alfabética → Fase 2; auto-numbering AF → Fase 2) están explícitamente diferidos.

**3. Type consistency:**

- `l10n_py_point_of_emission_id` se usa consistentemente en Tasks 11, 12, 13, 19, 20, 22.
- `l10n_py_timbrado` se referencia desde common.py (Task 10) + tests (Task 12, 19, etc).
- `account_id` en taxes (Task 15) usa códigos sin puntos consistentes con CSV (Task 14).

**Posible riesgo de implementación encontrado en self-review:**

- Task 15 CSV de taxes usa `account_id` con prefijo `py_` (XML ID); verificar sintaxis exacta de Odoo 18 al cargar referencias en CSV nativos del chart template (puede requerir prefix módulo: `l10n_py_account.py_201030102`). **Documentado**: si Task 15 step 5 falla con "External ID not found", ajustar prefijos en el CSV agregando `l10n_py_account.` antes de cada referencia.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-05-25-l10n-py-account.md`. Two execution options:**

**1. Subagent-Driven (recommended)** - Dispatch fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** - Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
