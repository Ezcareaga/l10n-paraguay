---
source: Analysis of references/odoo-18.0/addons/l10n_latam_invoice_document/ (Odoo 18 Community)
fetched_at: 2026-05-19
summary: Document type framework for government-mandated fiscal invoice classification (FA, ND, NC, etc.)
priority: critical
---

# l10n_latam_invoice_document: Fiscal Document Types & Numbering

## Core Purpose

Manages country-specific invoice document types defined by fiscal authorities (DGI in Paraguay, AFIP in Argentina, SII in Chile). Each document type has its own sequence number, internal classification, and legal requirements. Essential for countries where invoices must be tagged with official document codes.

Why it matters for Paraguay: SET (Subsistema de Traspaso Electrónico) requires invoices classified as:

- FA (Factura): regular invoice
- ND (Nota de Débito): debit note
- NC (Nota de Crédito): credit note

Each type must have unique sequential numbering per journal.

---

## Core Models

### l10n_latam.document.type

The central registry model:

| Field           | Type                  | Purpose                                                                      |
| --------------- | --------------------- | ---------------------------------------------------------------------------- |
| country_id      | Many2one(res.country) | Required; country where document type is valid                               |
| code            | Char                  | Government code (e.g., 'FA', '01' for Argentina)                             |
| name            | Char                  | Human-readable name (translatable)                                           |
| doc_code_prefix | Char                  | Prefix prepended to sequential number (e.g., 'FA ' builds 'FA 0001-0000001') |
| report_name     | Char                  | Text printed on reports, e.g., "CREDIT NOTE" (translatable)                  |
| internal_type   | Selection             | Classification: invoice, debit_note, credit_note, all                        |
| sequence        | Integer               | Sort order in UI (lower = first)                                             |
| active          | Boolean               | Enable/disable without deleting                                              |

internal_type values:

- invoice – matches account.move.move_type in [out_invoice, in_invoice]
- debit_note – matches out_invoice moved to debit note status
- credit_note – matches out_refund, in_refund (refund moves)
- all – applies to any document type (rare; fallback)

Key Method:

`python
def _format_document_number(self, document_number):
    """Override in localizations to validate/format numbers.
    Raises UserError if invalid. Returns formatted string."""
    return document_number
`

### account.move Extensions

Five new fields and extensive compute logic:

`python
l10n_latam_available_document_type_ids = fields.Many2many(
'l10n_latam.document.type',
compute='\_compute_l10n_latam_available_document_types'
)

l10n_latam_document_type_id = fields.Many2one(
'l10n_latam.document.type',
compute='\_compute_l10n_latam_document_type',
store=True
)

l10n_latam_document_number = fields.Char(
compute='\_compute_l10n_latam_document_number',
inverse='\_inverse_l10n_latam_document_number'
)

l10n_latam_use_documents = fields.Boolean(
related='journal_id.l10n_latam_use_documents'
)

l10n_latam_manual_document_number = fields.Boolean(
compute='\_compute_l10n_latam_manual_document_number'
)
`

Constraints enforced:

1. Posted invoice with l10n_latam_use_documents=True MUST have document_type
2. Posted invoice with manual numbering MUST have document_number
3. document_type.internal_type must match move_type (credit_note only for refunds)
4. Unique constraints on (name, journal_id) or (name, partner_id, document_type_id, company_id)

### account.journal Extensions

`python
l10n_latam_use_documents = fields.Boolean(
'Use Documents?',
help='If True, invoices require document type classification'
)

l10n_latam_company_use_documents = fields.Boolean(
compute='\_compute_l10n_latam_company_use_documents'
)
`

Behavior:

- On company change: auto-enable l10n_latam_use_documents if journal type (sale/purchase) AND company uses documents
- Constraint: can't toggle if journal has posted invoices

### res.company Extension

`python
def _localization_use_documents(self):
    """Override in l10n_py to return True."""
    return False
`

---

## Document Numbering & Sequences

### Name Computation (move.name)

For documents-enabled journals:

`
name = "[DOC_CODE_PREFIX] [SEQUENTIAL_NUMBER]"

# Example: "FA 0001-0000001"

`

Rules:

1. If draft & unposted_before & auto-numbering: sequence generated from journal.sequence_id
2. If manual_document_number: user enters number in l10n_latam_document_number field
3. On document_type change (draft): name reset to recompute with new prefix
4. Posted moves: name locked

Sequence Handling:

- One sequence per document_type (not debit/refund sequences)
- journal.debit_sequence & refund_sequence = False when using documents
- Sequence never resets (never='never') for document moves

### Document Number Inverse

When user edits l10n_latam_document_number:

`python
def _inverse_l10n_latam_document_number(self):
    for rec in self.filtered(lambda x: x.l10n_latam_document_type_id):
        formatted = rec.l10n_latam_document_type_id._format_document_number(
            rec.l10n_latam_document_number
        )
        rec.name = "%s %s" % (
            rec.l10n_latam_document_type_id.doc_code_prefix,
            formatted
        )
`

---

## Compute Methods (Critical)

### \_compute_l10n_latam_available_document_types()

Filters document types by move context:

`python
def \_get_l10n_latam_documents_domain(self):
internal_types = []
if self.move_type in ['out_refund', 'in_refund']:
internal_types = ['credit_note']
elif self.move_type in ['out_invoice', 'in_invoice']:
internal_types = ['invoice', 'debit_note']

    if self.debit_origin_id:
        internal_types = ['debit_note']

    internal_types += ['all']

    return [
        ('internal_type', 'in', internal_types),
        ('country_id', '=', self.company_id.account_fiscal_country_id.id)
    ]

`

Only computes when: journal has l10n_latam_use_documents=True, partner_id set, company has fiscal country.

### \_compute_l10n_latam_document_type()

Auto-selects first available type for draft unposted invoices.

### \_compute_l10n_latam_document_number()

Extracts sequential part from move.name: "FA 0001-0000001" -> "0001-0000001"

---

## Extension Hooks for Localizations

### Partner-Based Document Filtering

`python
class AccountMove(models.Model):
\_inherit = 'account.move'

    def _get_l10n_latam_documents_domain(self):
        domain = super()._get_l10n_latam_documents_domain()

        # Restrict based on partner ID type
        if self.partner_id.l10n_latam_identification_type_id.name == 'CI':
            domain = [
                ('code', '=', 'FA_SIMPLE'),
                ('country_id', '=', self.company_id.account_fiscal_country_id.id)
            ]

        return domain

`

### Manual Numbering Logic

`python
def \_is_manual_document_number(self):
"""Determine if move requires manual number entry."""
if self.country_code != 'PY':
return super().\_is_manual_document_number()

    return self.l10n_latam_use_documents and self.journal_id.type == 'purchase'

`

### Number Format Validation

`python
class L10nLatamDocumentType(models.Model):
\_inherit = 'l10n_latam.document.type'

    def _format_document_number(self, document_number):
        if self.country_id.code != "PY":
            return super()._format_document_number(document_number)

        if self.code == 'FA':
            parts = document_number.split('-')
            if len(parts) != 2 or len(parts[0]) > 4 or len(parts[1]) > 8:
                raise UserError("FA format: XXXX-XXXXXXXX")
            return f"{parts[0]:>04s}-{parts[1]:>08s}"

        return document_number

`

---

## Example Patterns from Other Countries

### Argentina (l10n_ar)

Manual numbering for non-POS sales/purchase journals. Validates "00001-00000001" format (point_of_sale-invoice_number). Extends document_type with l10n_ar_letter field (A-X).

### Chile (l10n_cl)

Extends internal_type with invoice_in, invoice, receipt_invoice, stock_picking. Has l10n_cl_active boolean. Pads document numbers to 6 digits: "123" -> "000123".

---

## Data Setup for Paraguay

`xml

<!-- l10n_py/data/l10n_latam.document.type.xml -->
<record model='l10n_latam.document.type' id='dt_fa'>
    <field name='country_id' ref='base.py'/>
    <field name='code'>FA</field>
    <field name='name'>Factura</field>
    <field name='doc_code_prefix'>FA </field>
    <field name='report_name'>FACTURA</field>
    <field name='internal_type'>invoice</field>
    <field name='sequence'>10</field>
</record>

<record model='l10n_latam.document.type' id='dt_nd'>
    <field name='country_id' ref='base.py'/>
    <field name='code'>ND</field>
    <field name='name'>Nota de Débito</field>
    <field name='doc_code_prefix'>ND </field>
    <field name='report_name'>NOTA DE DÉBITO</field>
    <field name='internal_type'>debit_note</field>
    <field name='sequence'>20</field>
</record>

<record model='l10n_latam.document.type' id='dt_nc'>
    <field name='country_id' ref='base.py'/>
    <field name='code'>NC</field>
    <field name='name'>Nota de Crédito</field>
    <field name='doc_code_prefix'>NC </field>
    <field name='report_name'>NOTA DE CRÉDITO</field>
    <field name='internal_type'>credit_note</field>
    <field name='sequence'>30</field>
</record>
`

---

## UI Form Integration

### Invoice Form (account.move view)

`xml
<field name="l10n_latam_document_type_id"
    invisible="not l10n_latam_use_documents"
    readonly="posted_before"
    required="partner_id and l10n_latam_use_documents"
    domain="[('id', 'in', l10n_latam_available_document_type_ids)]"
    options="{'no_open': True, 'no_create': True}"/>

<field name="l10n_latam_document_number"
    invisible="(not l10n_latam_use_documents or not l10n_latam_manual_document_number)"
    readonly="posted_before and state != 'draft'"
    required="partner_id and l10n_latam_use_documents and l10n_latam_manual_document_number"/>
`

Logic:

- document_type hidden unless journal uses documents & partner exists
- document_number shown only if manual (vs auto-sequenced) AND draft
- Both fields locked after posting

---

## Key Takeaways for Paraguay

1. Define 3+ document types (FA, ND, NC) with correct internal_type & country_id
2. Document types auto-filter by move_type and partner via \_get_l10n_latam_documents_domain()
3. Override \_format_document_number() to validate DGI number formats (e.g., "0001-0000001")
4. Override \_is_manual_document_number() if purchase journals need manual entry
5. Implement res.company.\_localization_use_documents() returning True
6. Don't allow l10n_latam_use_documents toggle on journals with posted invoices
7. Use l10n_latam_document_number field in forms (auto builds move.name with prefix)
8. Test auto-selection and format validation thoroughly
