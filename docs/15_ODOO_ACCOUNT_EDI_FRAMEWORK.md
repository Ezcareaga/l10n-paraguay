---
source: Synthesis from Odoo 18 source (addons/account_edi/) + LATAM localization patterns (l10n_ar_edi, l10n_pe_edi @ enterprise, l10n_ec_edi @ OCA); GitHub README fetch returned 404
fetched_at: 2026-05-19
summary: Framework account_edi de Odoo — modelos account.edi.format y account.edi.document, ciclo de vida, hooks que cada localización debe implementar, integración con account.move.
priority: critical
---

# `account_edi` Framework — referencia para `l10n_py_edi`

> Este es el framework canónico que TODA localización con factura electrónica
> debe extender en Odoo 18. Diseñado por Odoo SA para Bélgica, Italia, México,
> Chile, Perú, etc. — `l10n_py_edi` lo usa para Paraguay/SIFEN.
>
> **Fuente del addon:** `references/odoo-18.0/addons/account_edi/` (sparse-checked
> en este repo — consultable vía codegraph).

## 1. Modelos principales

### `account.edi.format`

Cada formato EDI soportado se modela como un **record de datos** de este modelo.
La lógica vive en métodos de subclase Python:

```python
# l10n_py_edi/models/account_edi_format.py
from odoo import api, models, _

class AccountEdiFormat(models.Model):
    _inherit = 'account.edi.format'

    def _needs_web_services(self):
        self.ensure_one()
        return self.code == 'py_dnit_sifen' or super()._needs_web_services()

    def _is_compatible_with_journal(self, journal):
        self.ensure_one()
        if self.code != 'py_dnit_sifen':
            return super()._is_compatible_with_journal(journal)
        return (
            journal.type == 'sale'
            and journal.company_id.country_id.code == 'PY'
        )

    def _get_move_applicability(self, move):
        self.ensure_one()
        if self.code != 'py_dnit_sifen':
            return super()._get_move_applicability(move)
        if move.country_code != 'PY':
            return None
        return {
            'post': self._l10n_py_post_invoice_edi,
            'cancel': self._l10n_py_cancel_invoice_edi,
            'edi_content': self._l10n_py_export_invoice_xml,
        }

    def _l10n_py_post_invoice_edi(self, invoices):
        """Para cada invoice: construir XML, firmar, enviar a SIFEN."""
        result = {}
        for invoice in invoices:
            try:
                xml = self._l10n_py_generate_xml(invoice)
                signed = self._l10n_py_sign(xml, invoice.company_id)
                response = self._l10n_py_send_to_sifen(signed, invoice.company_id)
                if response['codigo'] in ('0260', '0261'):
                    attachment = self.env['ir.attachment'].create({
                        'name': f"DE_{invoice.l10n_py_cdc}.xml",
                        'res_model': 'account.move',
                        'res_id': invoice.id,
                        'datas': base64.b64encode(signed),
                        'mimetype': 'application/xml',
                    })
                    result[invoice] = {'success': True, 'attachment': attachment}
                else:
                    result[invoice] = {
                        'success': False,
                        'error': f"SIFEN {response['codigo']}: {response['mensaje']}",
                        'blocking_level': 'error' if response['codigo'].startswith('03') else 'warning',
                    }
            except Exception as e:
                result[invoice] = {
                    'success': False,
                    'error': str(e),
                    'blocking_level': 'error',
                }
        return result
```

### Record del format (en data XML)

```xml
<!-- l10n_py_edi/data/account_edi_format_data.xml -->
<odoo>
    <data noupdate="1">
        <record id="edi_format_py_dnit_sifen" model="account.edi.format">
            <field name="name">SIFEN (DNIT Paraguay)</field>
            <field name="code">py_dnit_sifen</field>
        </record>
    </data>
</odoo>
```

### `account.edi.document`

Records auto-creados por el framework cuando una `account.move` con un
`account.edi.format` aplicable se postea. Estado de cada documento EDI:

```python
class AccountEdiDocument(models.Model):
    _name = 'account.edi.document'

    move_id = fields.Many2one('account.move', required=True, ondelete='cascade')
    edi_format_id = fields.Many2one('account.edi.format', required=True)
    state = fields.Selection([
        ('to_send', 'To Send'),       # esperando envío
        ('sent', 'Sent'),              # enviado y aprobado
        ('to_cancel', 'To Cancel'),    # esperando cancelación
        ('cancelled', 'Cancelled'),    # cancelado en autoridad fiscal
    ])
    blocking_level = fields.Selection([
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ])
    error = fields.Html()
    attachment_id = fields.Many2one('ir.attachment')   # XML firmado
```

## 2. Hooks que `account.edi.format` expone

| Método                                  | Cuándo lo llama el framework                               | Qué debe devolver/hacer                                                                        |
| --------------------------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| `_get_move_applicability(move)`         | Antes de postear o pedir EDI                               | dict con `{'post': fn, 'cancel': fn, 'edi_content': fn}` o `None` si no aplica                 |
| `_needs_web_services()`                 | Para decidir si crear `edi.document` con `state='to_send'` | bool                                                                                           |
| `_is_compatible_with_journal(journal)`  | Filtro en UI de journal config                             | bool                                                                                           |
| `_check_move_configuration(move)`       | Antes de postear                                           | list[str] de errores; vacía si OK                                                              |
| `_post_invoice_edi(invoices)`           | Cron / botón "Send Now"                                    | dict `{invoice: {'success': bool, 'error': str, 'attachment': record, 'blocking_level': str}}` |
| `_cancel_invoice_edi(invoices)`         | Al cancelar move con `edi_state='sent'`                    | mismo formato que post                                                                         |
| `_export_invoice_xml(invoice)` (legacy) | Generar XML sin enviar (debug)                             | bytes XML                                                                                      |

**Cambio en Odoo 17/18:** se introdujo `_get_move_applicability` para reemplazar
varios métodos sueltos. La preferencia ahora es **un solo método** que devuelve
un dict de callables, en lugar de override de cada hook.

## 3. Flujo end-to-end

```
[USER]
  └─ Click "Confirm" en account.move (state: draft)
      │
[ORM]
  └─ account.move._post()
      │
      ├─ Valida (constraints, _check_move_configuration de los EDI formats aplicables)
      ├─ Move state: draft → posted
      └─ Por cada edi_format aplicable (via _get_move_applicability)
          └─ Crea account.edi.document(state='to_send', move_id=move, edi_format_id=format)
                │
                │  (asincrónico — el user ya recibió confirmación inmediata)
                │
[CRON: account.edi.document._cron_process_documents]
  └─ Cada 1h busca documents con state='to_send' + blocking_level != 'error'
      └─ Llama edi_format._post_invoice_edi(invoices)
          │
          ├─ Genera XML (l10n_py)
          ├─ Firma con CCFE (lxml + signxml)
          ├─ Envía a SIFEN (zeep + mutual TLS)
          ├─ Procesa respuesta
          └─ Devuelve dict result
                │
                ▼
[FRAMEWORK]
  └─ Procesa dict result:
      ├─ Si {'success': True} → state='sent', guarda attachment
      └─ Si {'success': False} → guarda error + blocking_level
                                  (si 'error' → próximo cron NO reintenta;
                                   si 'warning' → SÍ reintenta)
```

## 4. Campos computados en `account.move`

El framework agrega estos campos al `account.move`:

```python
edi_format_ids = fields.Many2many('account.edi.format', compute='_compute_edi_format_ids')
edi_document_ids = fields.One2many('account.edi.document', 'move_id')
edi_state = fields.Selection([...], compute='_compute_edi_state', store=True)
# edi_state agrega: 'to_send', 'sent', 'to_cancel', 'cancelled'
edi_error_count = fields.Integer(compute='_compute_edi_error_count')
edi_blocking_level = fields.Selection([...])
edi_web_services_to_process = fields.Char(compute=...)
edi_show_force_cancel = fields.Boolean(compute=...)
```

## 5. Configuración del journal

Los `account.edi.format` se asignan al `account.journal`:

```python
class AccountJournal(models.Model):
    _inherit = 'account.journal'

    edi_format_ids = fields.Many2many('account.edi.format')
    compatible_edi_ids = fields.Many2many(
        'account.edi.format', compute='_compute_compatible_edi_ids',
    )
```

En la UI del journal (Accounting → Configuration → Journals) aparece la sección
**Advanced Settings → Electronic Invoicing**, donde el admin marca qué formatos
aplica este journal.

Para Paraguay, en el `post_init_hook` autoasignamos:

```python
def post_init_hook(env):
    py_format = env.ref('l10n_py_edi.edi_format_py_dnit_sifen')
    py_sale_journals = env['account.journal'].search([
        ('type', '=', 'sale'),
        ('company_id.country_id.code', '=', 'PY'),
    ])
    py_sale_journals.write({'edi_format_ids': [(4, py_format.id)]})
```

## 6. Reintentos y manejo de errores

| Situación                                       | `blocking_level` | ¿Cron reintenta?                                 |
| ----------------------------------------------- | ---------------- | ------------------------------------------------ |
| Red caída, timeout                              | `'warning'`      | Sí (próximo cron)                                |
| SIFEN devuelve `0361` (lote en procesamiento)   | `'info'`         | Sí                                               |
| SIFEN devuelve `0300-0399` (rechazo de negocio) | `'error'`        | NO — user debe corregir y reintentar manualmente |
| Cert inválido / TLS handshake fail              | `'error'`        | NO — admin debe revisar config                   |
| Exception inesperada en el código nuestro       | `'error'`        | NO — bug del módulo                              |

El user puede **forzar reintento** desde la UI: botón "Send Now" en la factura,
o "Process Documents" en `account.edi.document`.

## 7. Buenas prácticas para `l10n_py_edi`

1. **NO bloquear `action_post()`** con llamadas síncronas a SIFEN. Solo validar
   localmente (CDC válido, RUC válido, timbrado vigente). El envío es asíncrono
   vía cron.
2. **Logguear todo** en `move.message_post()` — cualquier respuesta de SIFEN
   (aprobada, rechazada, errores) debe quedar en el chatter para auditoría.
3. **Attachment del XML firmado** con `res_model='account.move'` y `res_id`
   apropiado — así aparece en la lista de archivos adjuntos de la factura.
4. **Para batch**: si Odoo manda 50 invoices al hook, usar `siRecepLoteDE`
   (asíncrono SOAP) en lugar de llamar `siRecepDE` 50 veces.
5. **Tests con mocks** del cliente SOAP — los tests no deben hablar con
   `sifen-test.set.gov.py` salvo cuando se invoca explícitamente el tag
   `external`.
6. **`_check_move_configuration`** debe pillar TODOS los errores de configuración
   ANTES de postear, no después. Ejemplo: company sin CCFE, partner sin
   identification type, item sin tax SIFEN.

## 8. Comparación rápida con localizaciones existentes

| Localización  | Repo                       | Patrón clave                                                 |
| ------------- | -------------------------- | ------------------------------------------------------------ |
| `l10n_ar_edi` | odoo/odoo (community)      | WSAA + WSFEv1, CAE, document types vía `l10n_latam`          |
| `l10n_pe_edi` | odoo/odoo (**enterprise**) | UBL 2.1, OSE (Digiflow/SUNAT), IAP opcional                  |
| `l10n_ec_edi` | OCA/l10n-ecuador           | Clave de acceso 49 dígitos (similar a CDC), .p12, REST a SRI |
| `l10n_mx_edi` | odoo/odoo (community)      | CFDI 4.0, PAC providers                                      |
| `l10n_cl_edi` | odoo/odoo (community)      | Folios CAF, autorización SII                                 |

**Implicación para `l10n_py_edi`:**

- El patrón más cercano es **`l10n_ec_edi`** (OCA, clave de acceso, .p12 directo
  al SRI). Ver `references/l10n-ecuador-17.0/l10n_ec_edi/` (cuando disponible).
- Para la integración con `l10n_latam_invoice_document` (tipos de documento),
  el patrón maduro es **`l10n_ar`**. Ver `references/odoo-18.0/addons/l10n_ar/`.
- Para el framework `account.edi.format` puro, **`l10n_mx_edi`** y **`l10n_cl_edi`**
  en community son los ejemplos más completos.

Consultar via codegraph:

```
codegraph search "account.edi.format inheritance"
codegraph search "_post_invoice_edi implementation"
codegraph search "_get_move_applicability return dict"
```
