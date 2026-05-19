---
source: Analysis of references/odoo-18.0/addons/l10n_latam_base/ (Odoo 18 Community)
fetched_at: 2026-05-19
summary: Framework for country-specific identification types beyond VAT (RUC, CI, Passport, etc.)
priority: critical
---

# l10n_latam_base: Identification Types Framework

## Core Purpose

Extends res.partner with a flexible identification type system to handle multiple government-issued document types beyond simple VAT numbers. Essential for countries like Paraguay, Argentina, Chile where fiscal operations require precise document classification.

Why it matters for Paraguay: The Dirección General de Ingresos (DGI) requires companies and individuals to be identified by RUC (Registración Única de Contribuyente) and individuals by CI (Cédula de Identidad). The generic VAT field is insufficient.

---

## Models & Fields

### l10n_latam.identification.type

The primary model you'll extend:

| Field | Type | Purpose |
|-------|------|---------|
| id | Char | XML ID (e.g., l10n_latam_base.it_vat) |
| name | Char | Short human-readable name (translatable) |
| description | Char | Long form / help text (translatable) |
| country_id | Many2one(res.country) | Country where valid; leave empty for generic types |
| is_vat | Boolean | Marks this as the country's primary VAT/tax ID (used for validation & as default) |
| sequence | Integer | Sort order; lower = shown first (default 10) |
| active | Boolean | Enable/disable without deleting (default True) |

Standard Generic Types (shipped in base):

| XML ID | Name | is_vat | Sequence |
|--------|------|--------|----------|
| l10n_latam_base.it_vat | VAT | True | 80 |
| l10n_latam_base.it_pass | Passport | False | 90 |
| l10n_latam_base.it_fid | Foreign ID | False | 100 |

These appear in partner forms regardless of country. Country-specific types are filtered by partner's country_id.

### res.partner Extensions

Two new fields injected:

`python
l10n_latam_identification_type_id = fields.Many2one(
    'l10n_latam.identification.type',
    string="Identification Type",
    index='btree_not_null',
    default=lambda self: self.env.ref('l10n_latam_base.it_vat', ...)
)
vat = fields.Char(
    string='Identification Number',
    help="Identification Number for selected type"
)
`

Key Behavior:

- vat is now semantic: its meaning depends on l10n_latam_identification_type_id.is_vat
- VAT validation (from base_vat) only applies to records where is_vat=True
- _commercial_fields() includes l10n_latam_identification_type_id so it propagates to child contacts

Automatic Defaults:

On onchange('country_id'):
1. Search for the country's is_vat identification type
2. If not found, fall back to generic it_vat
3. Only triggers if current type is missing or from a different country

---

## Data Files & XML IDs

### Base CSV: data/l10n_latam.identification.type.csv

Simple format:

`csv
id,name,sequence,is_vat
l10n_latam_base.it_vat,VAT,80,TRUE
l10n_latam_base.it_pass,Passport,90,
l10n_latam_base.it_fid,Foreign ID,100,
`

### How to Add Paraguay Types

Create data/l10n_latam.identification.type.xml in your l10n_py module:

`xml
<?xml version="1.0" encoding="UTF-8"?>
<odoo>
<data>
    <record model='l10n_latam.identification.type' id='it_ruc'>
        <field name='name'>RUC</field>
        <field name='description'>Registración Única de Contribuyente (Tax ID)</field>
        <field name='country_id' ref='base.py'/>
        <field name='is_vat' eval='True'/>
        <field name='sequence'>10</field>
    </record>

    <record model='l10n_latam.identification.type' id='it_ci'>
        <field name='name'>CI</field>
        <field name='description'>Cédula de Identidad (ID Card)</field>
        <field name='country_id' ref='base.py'/>
        <field name='sequence'>20</field>
    </record>

    <record model='l10n_latam.identification.type' id='it_pasaporte'>
        <field name='name'>Pasaporte</field>
        <field name='description'>Passport</field>
        <field name='country_id' ref='base.py'/>
        <field name='sequence'>30</field>
    </record>
</data>
</odoo>
`

Key Rules:
- Only is_vat=True for ONE type per country (typically RUC for Paraguay)
- XML IDs must be unique; prefix with module name (e.g., l10n_py.it_ruc)
- Reference base country ID: ref='base.py' for Paraguay
- Sequence determines display order in partner form dropdowns

---

## Extension Patterns

### Add Country-Specific Fields

Inherit the model in your localization:

`python
from odoo import models, fields

class L10nLatamIdentificationType(models.Model):
    _inherit = "l10n_latam.identification.type"

    l10n_py_dgi_code = fields.Char(
        "DGI Code",
        help="Code assigned by Dirección General de Ingresos"
    )
`

Example: Argentina does this with l10n_ar_afip_code to store AFIP's numeric codes.

### Add Validation Logic

Override check_vat() in res.partner:

`python
from odoo import models, api
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.constrains('vat', 'l10n_latam_identification_type_id')
    def check_vat(self):
        ruc_records = self.filtered(
            lambda x: x.l10n_latam_identification_type_id.is_vat
        )
        super(ResPartner, ruc_records).check_vat()
        
        ci_records = self.filtered(
            lambda x: x.l10n_latam_identification_type_id.name == 'CI'
        )
        for rec in ci_records:
            if not rec._validate_ci(rec.vat):
                raise ValidationError(f"Invalid CI: {rec.vat}")

    def _validate_ci(self, ci_number):
        return len(ci_number) == 8 and ci_number.isdigit()
`

---

## Form & UI

### Partner Form Integration

The module inherits base_vat.view_partner_base_vat_form and replaces:

`xml
<field name="l10n_latam_identification_type_id" 
    placeholder="Type" 
    domain="country_id and ['|', ('country_id', '=', False), ('country_id', '=', country_id)] or []"
    required="True" 
    readonly="parent_id"/>
<field name="vat" placeholder="Number" class="oe_inline" readonly="parent_id"/>
`

Domain Logic:
- If partner has country_id: show generic types + types for that country
- If no country: show generic types + types for company's fiscal country
- Partner's country changes -> identification type auto-updates if incompatible

---

## Manifest & Dependencies

`python
{
    'name': 'Paraguay Localization',
    'depends': [
        'l10n_latam_base',
        'account',
    ],
    'data': [
        'data/l10n_latam.identification.type.xml',
    ],
}
`

---

## Key Takeaways for Paraguay

1. Define 3+ identification types in XML: RUC (is_vat=True, seq 10), CI (seq 20), Pasaporte (seq 30)
2. Reference DGI codes if needed (see Argentina's l10n_ar_afip_code pattern)
3. Only RUC triggers VAT validation; CI & Pasaporte are for flexibility
4. Partner country auto-selects the right type; users just pick from dropdown
5. Don't override res.company.create() unless you need special logic; base handles it
