---
source: https://www.odoo.com/documentation/18.0/developer/reference/backend/views.html
fetched_at: 2026-05-19
summary: Vistas Odoo 18 — todos los tipos (form, list, kanban, search, calendar, pivot, graph, activity, qweb), herencia XPath, widgets, modifiers, menuitems y actions.
priority: important
---

# Odoo 18 — Views Guide

> Referencia de los tipos de vista, herencia XPath, widgets y modifiers. Documentación
> oficial: https://www.odoo.com/documentation/18.0/developer/reference/backend/views.html

## 1. `ir.ui.view` — record de vista

```xml
<record id="account_move_view_form" model="ir.ui.view">
    <field name="name">account.move.form</field>           <!-- convención: <model>.<type> -->
    <field name="model">account.move</field>
    <field name="type">form</field>                         <!-- form|list|kanban|search|calendar|pivot|graph|activity|qweb|settings -->
    <field name="arch" type="xml">
        <form>
            <!-- estructura -->
        </form>
    </field>
</record>
```

Atributos clave:

- `name` — display identifier (convención `<model>.<type>` o `.inherit.<purpose>`)
- `model` — modelo target
- `type` — categoría (puede omitirse; Odoo lo infiere del root element)
- `inherit_id` — referencia a vista padre (para herencia)
- `mode` — `'primary'` (default) o `'extension'`
- `priority` — int (default 16); más bajo = se aplica primero

## 2. Herencia via XPath

```xml
<record id="account_move_view_form_l10n_py" model="ir.ui.view">
    <field name="name">account.move.form.l10n_py</field>
    <field name="model">account.move</field>
    <field name="inherit_id" ref="account.view_move_form"/>
    <field name="arch" type="xml">

        <!-- Agregar campo después de partner_id -->
        <xpath expr="//field[@name='partner_id']" position="after">
            <field name="l10n_py_cdc" invisible="country_code != 'PY'"/>
        </xpath>

        <!-- Modificar atributos de un field existente -->
        <xpath expr="//field[@name='ref']" position="attributes">
            <attribute name="readonly">l10n_py_cdc</attribute>
        </xpath>

        <!-- Reemplazar (USAR CON CUIDADO — rompe otras herencias) -->
        <xpath expr="//button[@name='action_post']" position="replace">
            <button name="action_post_with_sifen" string="Confirm" type="object"/>
        </xpath>

    </field>
</record>
```

**Position options:**

- `before` — insertar antes
- `after` — insertar después
- `inside` — insertar como hijo (default)
- `replace` — reemplazar completo (último recurso)
- `attributes` — solo modificar atributos del elemento

**Convenciones OCA (ver `20_OCA_GUIDELINES.md`):**

- Evitar `position="replace"` salvo justificación
- Un módulo solo debería heredar una vista una vez (consolidar todos los cambios)
- Para "esconder" un campo: `invisible="1"` en `position="attributes"` en lugar de `replace`

### Shortcut sin xpath (cuando matchea por field name)

```xml
<field name="partner_id" position="after">
    <field name="l10n_py_cdc"/>
</field>
```

Es equivalente a `<xpath expr="//field[@name='partner_id']" position="after">`.

## 3. Form view

```xml
<form>
    <header>
        <!-- Buttons (acciones), statusbar -->
        <button name="action_post" string="Confirm" type="object" class="oe_highlight"
                invisible="state != 'draft'"/>
        <field name="state" widget="statusbar" statusbar_visible="draft,posted"/>
    </header>
    <sheet>
        <!-- Botones superiores (smart buttons) -->
        <div class="oe_button_box">
            <button class="oe_stat_button" type="action" name="%(action_related)d" icon="fa-list">
                <field string="Lines" name="line_count" widget="statinfo"/>
            </button>
        </div>

        <!-- Title -->
        <div class="oe_title">
            <h1><field name="name" placeholder="Document #"/></h1>
        </div>

        <!-- Fields agrupados -->
        <group>
            <group>
                <field name="partner_id"/>
                <field name="invoice_date"/>
            </group>
            <group>
                <field name="amount_total"/>
                <field name="currency_id"/>
            </group>
        </group>

        <!-- Notebook con tabs -->
        <notebook>
            <page string="Lines" name="lines">
                <field name="invoice_line_ids">
                    <list editable="bottom">
                        <field name="product_id"/>
                        <field name="quantity"/>
                        <field name="price_unit"/>
                        <field name="price_subtotal"/>
                    </list>
                </field>
            </page>
            <page string="Other Info" name="other">
                <group>
                    <field name="ref"/>
                </group>
            </page>
        </notebook>
    </sheet>

    <!-- Chatter (si el modelo hereda mail.thread) -->
    <div class="oe_chatter">
        <field name="message_follower_ids"/>
        <field name="message_ids"/>
    </div>
</form>
```

## 4. List view (tree)

```xml
<list editable="bottom" default_order="date desc"
      decoration-info="state == 'draft'"
      decoration-success="state == 'posted'"
      decoration-danger="state == 'cancel'"
      decoration-muted="active == False">
    <field name="name"/>
    <field name="partner_id"/>
    <field name="invoice_date" optional="show"/>
    <field name="amount_total" sum="Total"/>
    <field name="state" widget="badge"/>
</list>
```

Atributos:

- `editable` — `'top'` | `'bottom'` | omitido (read-only)
- `default_order` — ej: `'date desc, id'`
- `decoration-<class>` — `info`, `success`, `warning`, `danger`, `muted` con expresión Python
- `sum` / `avg` — agregación en footer
- `optional="show"` / `"hide"` — usuario puede toggle visibility
- `multi_edit="1"` — permitir edit masivo
- `expand="1"` — auto-expandir grupos (hierarchical)

## 5. Kanban view

```xml
<kanban default_group_by="state" class="o_kanban_dashboard">
    <field name="name"/>
    <field name="amount_total"/>
    <field name="partner_id"/>
    <templates>
        <t t-name="card">
            <div class="oe_kanban_card">
                <strong><field name="name"/></strong>
                <div><field name="partner_id"/></div>
                <div class="text-end"><field name="amount_total" widget="monetary"/></div>
            </div>
        </t>
    </templates>
</kanban>
```

QWeb dentro de Kanban — common expressions:

- `<field name="x"/>` — render del field
- `<t t-esc="record.x.value"/>` — texto plano
- `<t t-if="...">...</t>` — condicional
- `<t t-foreach="..." t-as="...">...</t>` — loop
- `<t t-attf-class="bg-{{record.state.raw_value}}"/>` — atributo dinámico

## 6. Search view

```xml
<search string="Invoices">
    <!-- Campos buscables -->
    <field name="name" string="Number"/>
    <field name="partner_id"/>
    <field name="l10n_py_cdc" string="CDC"/>

    <separator/>

    <!-- Filtros predefinidos -->
    <filter string="Draft" name="filter_draft" domain="[('state','=','draft')]"/>
    <filter string="Posted" name="filter_posted" domain="[('state','=','posted')]"/>
    <separator/>
    <filter string="SIFEN Pending" name="filter_sifen_pending"
            domain="[('edi_state','=','to_send')]"/>

    <!-- Group By -->
    <group string="Group By" expand="0">
        <filter string="Partner" name="group_partner" context="{'group_by':'partner_id'}"/>
        <filter string="Month" name="group_month" context="{'group_by':'invoice_date:month'}"/>
        <filter string="State" name="group_state" context="{'group_by':'state'}"/>
    </group>

    <!-- Panel lateral -->
    <searchpanel>
        <field name="company_id" enable_counters="1"/>
        <field name="state" select="multi"/>
    </searchpanel>
</search>
```

## 7. Otras vistas

### Calendar

```xml
<calendar date_start="invoice_date" color="partner_id" mode="month">
    <field name="name"/>
    <field name="amount_total"/>
</calendar>
```

### Pivot

```xml
<pivot string="Analysis">
    <field name="partner_id" type="row"/>
    <field name="invoice_date" type="col" interval="month"/>
    <field name="amount_total" type="measure"/>
</pivot>
```

### Graph

```xml
<graph string="Monthly" type="line">
    <field name="invoice_date" type="row" interval="month"/>
    <field name="amount_total" type="measure"/>
</graph>
```

### Activity

```xml
<activity string="Activities">
    <field name="partner_id"/>
    <templates>
        <div t-name="activity-box">
            <img t-att-src="activity_image('res.partner', 'image_128', record.partner_id.raw_value)"/>
        </div>
    </templates>
</activity>
```

### Qweb (templates para reportes y mails)

```xml
<template id="report_kude_document">
    <t t-call="web.html_container">
        <t t-foreach="docs" t-as="doc">
            <t t-call="web.external_layout">
                <div class="page">
                    <h2>Factura Electrónica</h2>
                    <p>CDC: <span t-field="doc.l10n_py_cdc"/></p>
                    <!-- ... -->
                </div>
            </t>
        </t>
    </t>
</template>
```

## 8. Modifiers (Odoo 18 — solo Python expressions)

> **Odoo 18 cambió**: ya no se usa el atributo `attrs` con dict. Ahora `invisible`,
> `readonly`, `required` aceptan directamente una **expresión Python evaluada contra
> el record**.

```xml
<field name="discount" invisible="state == 'done'"/>
<field name="amount" readonly="state != 'draft'"/>
<field name="reference" required="type == 'internal'"/>

<!-- Múltiples condiciones -->
<field name="x"
       invisible="parent.state != 'draft' or company_id != False"
       readonly="qty_delivered > 0"/>
```

**Variables disponibles en la expresión:**

- Todos los fields del record actual (por nombre)
- `parent.<field>` — campos del padre en One2many/embedded views
- `context.get('key')` — del contexto
- `uid` — id del usuario actual

## 9. Widgets comunes

```xml
<!-- Selección de tags M2M -->
<field name="tag_ids" widget="many2many_tags" options="{'color_field':'color'}"/>

<!-- Statusbar -->
<field name="state" widget="statusbar" statusbar_visible="draft,posted"/>

<!-- Badge con decoration -->
<field name="state" widget="badge"
       decoration-success="state=='posted'"
       decoration-danger="state=='cancel'"/>

<!-- Monetario (requiere currency_field en el model) -->
<field name="amount_total" widget="monetary" options="{'currency_field':'currency_id'}"/>

<!-- Image -->
<field name="image_128" widget="image" class="rounded-circle"/>

<!-- HTML editor -->
<field name="description" widget="html"/>

<!-- Percentage -->
<field name="completion" widget="percentage"/>

<!-- Drag handle (para ordering por sequence) -->
<field name="sequence" widget="handle"/>

<!-- Priority (estrellas) -->
<field name="priority" widget="priority"/>

<!-- Signature pad -->
<field name="signature" widget="signature"/>

<!-- Boolean toggle (slider) -->
<field name="active" widget="boolean_toggle"/>

<!-- Radio buttons -->
<field name="state" widget="radio" options="{'horizontal': True}"/>

<!-- Code editor (Ace) -->
<field name="code" widget="ace" options="{'mode': 'python'}"/>

<!-- Many2one con quick create -->
<field name="partner_id" options="{'no_create_edit': True, 'no_quick_create': True}"/>
```

## 10. Menuitems y actions

```xml
<!-- Top-level menu -->
<menuitem id="menu_l10n_py" name="Paraguay (SIFEN)"
          parent="account.menu_finance" sequence="200"/>

<!-- Submenu -->
<menuitem id="menu_l10n_py_timbrado" name="Timbrados"
          parent="menu_l10n_py" sequence="10"
          action="action_l10n_py_timbrado"/>

<!-- Action que el menu invoca -->
<record id="action_l10n_py_timbrado" model="ir.actions.act_window">
    <field name="name">Timbrados</field>
    <field name="res_model">l10n_py.timbrado</field>
    <field name="view_mode">list,form</field>
    <field name="context">{'search_default_filter_active': 1}</field>
    <field name="domain">[]</field>
    <field name="help" type="html">
        <p class="o_view_nocontent_smiling_face">
            Crea tu primer timbrado DNIT
        </p>
    </field>
</record>
```

### Server actions (ejecutar código)

```xml
<record id="action_server_sifen_resend" model="ir.actions.server">
    <field name="name">Resend to SIFEN</field>
    <field name="model_id" ref="account.model_account_move"/>
    <field name="binding_model_id" ref="account.model_account_move"/>
    <field name="binding_view_types">list,form</field>
    <field name="state">code</field>
    <field name="code">
for record in records:
    record.action_l10n_py_resend_sifen()
    </field>
</record>
```

## 11. Context propagation

```xml
<!-- Pasar default desde la action -->
<record id="action_invoices_py" model="ir.actions.act_window">
    <field name="res_model">account.move</field>
    <field name="context">{
        'default_move_type': 'out_invoice',
        'default_l10n_py_tipo_emision': 'normal',
        'search_default_filter_posted': 1,
    }</field>
</record>

<!-- Consumir en la view (el field se prellena automáticamente con default_X) -->
```

Cualquier key con prefijo `default_<field_name>` en el context pre-llena ese field
en el formulario al crear.

## 12. Tips operacionales

- **Developer mode** (`?debug=1` en URL) habilita: ver XML IDs, recargar vistas
  sin reiniciar Odoo, ir a la view desde la UI.
- Para debuggear vistas: `View → Edit Form View` en debug mode.
- `priority` define el orden de aplicación de herencia (no de prioridad de usuario).
- Si una herencia rompe, verificar `xpath expr=` matchea EXACTAMENTE un elemento
  (debug mode te dice si matchea 0 o >1).
- Las vistas también heredan via `<field name="inherit_id" ref="..."/>` sin xpath —
  Odoo intenta matchear por nombre de field automáticamente.
