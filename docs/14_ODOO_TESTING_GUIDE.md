---
source: https://www.odoo.com/documentation/18.0/developer/reference/backend/testing.html + OCA practice
fetched_at: 2026-05-19
summary: Testing en Odoo 18 — TransactionCase, HttpCase, @tagged, fixtures, AccountTestInvoicingCommon, ejecución de tests, patrones OCA.
priority: important
---

# Odoo 18 — Testing Guide

> Tests obligatorios en OCA: unit para lógica de dominio, integration para
> adaptadores externos (SIFEN), HTTP/tour para flujos UI cuando aplique.

## 1. Clases base de tests

| Clase | Aislamiento | Cuándo usar |
|-------|-------------|-------------|
| `TransactionCase` | Sub-transacción por test (rollback automático) | 95% — default |
| `SingleTransactionCase` | Una sola transacción para toda la clase | Cuando setup es muy caro y tests son independientes |
| `HttpCase` | Como TransactionCase + browser_js + URL routes | Tests de UI, controllers, tours |
| `ChromeBrowserException` | (exception) | Errores en JS tours |

```python
from odoo.tests import TransactionCase, tagged

@tagged('post_install', '-at_install', 'l10n_py')
class TestL10nPyCdc(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env['res.company'].create({
            'name': 'Test Paraguay Co',
            'country_id': cls.env.ref('base.py').id,
            'l10n_py_ruc': '80069563',
            'l10n_py_dv_ruc': '1',
            'l10n_py_tipo_contribuyente': 'persona_juridica',
        })

    def test_compute_cdc_valid(self):
        invoice = self._create_test_invoice()
        invoice.action_post()
        self.assertEqual(len(invoice.l10n_py_cdc), 44)
        self.assertTrue(self._validate_cdc_dv(invoice.l10n_py_cdc))

    def _create_test_invoice(self):
        return self.env['account.move'].create({
            'company_id': self.company.id,
            'move_type': 'out_invoice',
            # ...
        })
```

## 2. Tags y ejecución selectiva

### Tags estándar en Odoo

| Tag | Significado |
|-----|-------------|
| `standard` | Default — corre en `--test-enable` sin filtros |
| `at_install` | Corre al instalar el módulo (antes de cargar otros módulos dependientes) |
| `post_install` | Corre después que todos los modules están instalados |
| `-standard` | EXCLUYE del default (solo si lo invocás explícitamente) |
| `external` | Requiere servicios externos (en OCA: SIFEN test, AFIP test, etc.) |

### Convención de tags útil

```python
@tagged('post_install', '-at_install', 'l10n_py')      # default + tag módulo
@tagged('-standard', 'external', 'l10n_py')            # solo cuando explícito
@tagged('-standard', 'external_l10n', 'l10n_py_sifen') # tests contra SIFEN real
```

`@tagged('-at_install')` es importante para tests que dependen de **múltiples
módulos cargados** (típico en localizaciones que tocan account, point_of_sale,
etc.). Si no lo ponés, Odoo intenta correrlo durante el load del módulo y los
deps aún no están listos.

### Comandos de ejecución

```bash
# Correr tests del módulo al instalarlo
odoo-bin -d test_db -i l10n_py_edi --test-enable --stop-after-init

# Correr tests al actualizar
odoo-bin -d test_db -u l10n_py_edi --test-enable --stop-after-init

# Solo tests con tag específico
odoo-bin -d test_db -u l10n_py_edi --test-enable --test-tags l10n_py --stop-after-init

# Múltiples filtros
--test-tags '/l10n_py_edi:TestSomething.test_one'

# Excluir
--test-tags '-external'
```

Sintaxis full: `[-][tag][/module][:class][.method]`.

## 3. Patrones de setup

### `setUpClass` vs `setUp`

```python
class TestSomething(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ejecuta UNA vez antes de TODOS los tests de la clase
        # Cualquier record creado aquí persiste entre tests (dentro del rollback general)
        cls.partner = cls.env['res.partner'].create({'name': 'Common'})

    def setUp(self):
        super().setUp()
        # Ejecuta antes de CADA test
        # Útil para resetear contexto, mocks, etc.
        self.invoice = self._create_invoice()
```

### Referencias a data por XML ID

```python
class TestX(TransactionCase):
    def test_foo(self):
        admin = self.env.ref('base.user_admin')          # recordset
        partner_id = self.ref('base.partner_admin')      # int (id)
        partner = self.browse_ref('base.partner_admin')  # recordset (alias de env.ref)
```

### `AccountTestInvoicingCommon`

Base perfecta para tests de localizaciones que tocan facturación:

```python
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged

@tagged('post_install', '-at_install', 'l10n_py')
class TestL10nPyInvoice(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls, chart_template_ref='l10n_py.l10n_py_coa'):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.company_data['company'].write({
            'l10n_py_ruc': '80069563',
            'l10n_py_dv_ruc': '1',
        })
        cls.partner_b.write({
            'l10n_latam_identification_type_id': cls.env.ref(
                'l10n_py_base.it_ruc'
            ).id,
            'vat': '1234567-8',
        })

    def test_post_invoice_generates_cdc(self):
        invoice = self.init_invoice('out_invoice', amounts=[100.0], post=False)
        invoice.action_post()
        self.assertTrue(invoice.l10n_py_cdc)
```

Provee: companies, partners (a, b, c), products, taxes, journals — todo
pre-configurado. Ahorra cientos de líneas de boilerplate.

## 4. Aserciones comunes

```python
# Igualdad
self.assertEqual(invoice.amount_total, 1100.0)

# Truth/falsy
self.assertTrue(invoice.l10n_py_cdc)
self.assertFalse(invoice.exists())

# Membresía
self.assertIn('PY', invoice.country_id.code)

# Excepciones
with self.assertRaises(ValidationError):
    invoice.write({'l10n_py_cdc': 'invalid'})

# Recordset values en bulk
self.assertRecordValues(invoices, [
    {'name': 'INV/2026/0001', 'amount_total': 1100.0},
    {'name': 'INV/2026/0002', 'amount_total': 550.0},
])

# Approximadamente igual (floats)
self.assertAlmostEqual(invoice.amount_total, 1100.0, places=2)
```

## 5. Mocking y patching

### Mockear servicios externos (SIFEN)

```python
from unittest.mock import patch, MagicMock

@patch('odoo.addons.l10n_py_edi.services.sifen_client.SifenClient.send_de')
def test_send_invoice_calls_sifen(self, mock_send):
    mock_send.return_value = {'codigo': '0260', 'mensaje': 'Aprobado'}

    invoice = self._create_test_invoice()
    invoice.action_post()
    invoice.edi_document_ids._process_documents_web_services()

    mock_send.assert_called_once()
    self.assertEqual(invoice.edi_state, 'sent')
```

### Patch via context manager

```python
def test_with_mock(self):
    with patch('odoo.addons.l10n_py_edi.services.cdc.gen_random') as m:
        m.return_value = '123456789'
        cdc = build_cdc({...})
        self.assertIn('123456789', cdc)
```

### Mock al nivel de método ORM

```python
def test_action_post(self):
    with patch.object(type(self.env['account.move']), '_post') as mock_post:
        mock_post.return_value = self.env['account.move']
        self.invoice.action_post()
        mock_post.assert_called()
```

## 6. Tests HTTP / tours

### HttpCase básico

```python
from odoo.tests import HttpCase, tagged

@tagged('post_install', '-at_install')
class TestL10nPyController(HttpCase):

    def test_qr_redirect(self):
        response = self.url_open('/l10n_py/qr/01800695631001003000013712022010619364760029')
        self.assertEqual(response.status_code, 302)
        self.assertIn('ekuatia.set.gov.py', response.headers['Location'])
```

### Tours (UI flow tests)

JavaScript define los pasos, Python los dispara:

```python
def test_create_invoice_tour(self):
    self.start_tour('/web', 'l10n_py_edi.tour_create_invoice', login='admin')
```

```js
// static/tests/tours/create_invoice_tour.js
import { registry } from "@web/core/registry";

registry.category("web_tour.tours").add("l10n_py_edi.tour_create_invoice", {
    test: true,
    steps: () => [
        { trigger: 'a[data-menu-xmlid="account.menu_finance_receivables"]' },
        { trigger: '.o_list_button_add' },
        { trigger: 'input[name="partner_id"]', run: 'text Acme PY' },
        // ...
    ],
});
```

Y registrar el asset en `__manifest__.py`:
```python
'assets': {
    'web.assets_tests': [
        'l10n_py_edi/static/tests/tours/*.js',
    ],
},
```

## 7. Anti-flaky patterns

| Anti-pattern | Reemplazo |
|--------------|-----------|
| `datetime.now()` | `@freeze_time('2026-05-19')` (requiere `pip install freezegun`) |
| `time.sleep(...)` | Mock del cron / call directo del método |
| Hardcodear `id=1` | Usar `self.env.ref('module.xml_id').id` o crear el record |
| Compartir state entre tests | `setUpClass` solo para data, no para counters mutables |
| Llamar `self.cr.commit()` | NUNCA (rompe el rollback) |

## 8. Layout de tests en un módulo OCA

```
l10n_py_edi/tests/
├── __init__.py                     # from . import test_X, test_Y
├── common.py                       # AccountTestInvoicingCommon o helpers
├── test_cdc_generation.py
├── test_xml_builder.py
├── test_xmldsig_signing.py
├── test_sifen_send.py              # Mocked
├── test_sifen_send_external.py     # Real (tagged 'external')
├── test_account_move_workflow.py
├── test_cancellation_wizard.py
├── test_kude_report.py
└── tours/
    └── tour_create_invoice.py
```

### `tests/__init__.py`

```python
from . import test_cdc_generation
from . import test_xml_builder
from . import test_xmldsig_signing
from . import test_sifen_send
from . import test_account_move_workflow
from . import test_cancellation_wizard
from . import test_kude_report
# NO importar test_sifen_send_external — se carga solo por tag explícito
```

Actually, **siempre importar todos** — los tags filtran qué se ejecuta. Si no
importás, ni siquiera podés invocarlos por tag.

## 9. Cobertura

```bash
pip install coverage

coverage run --source=odoo/addons/l10n_py_edi /path/to/odoo-bin \
  -d test_db -u l10n_py_edi --test-enable --stop-after-init
coverage report
coverage html  # genera htmlcov/
```

OCA usa Coveralls en CI — el target informal es 80%+ para módulos nuevos.

## 10. Patrón: tests de integration SIFEN

Dos archivos separados:

**`test_sifen_send.py`** — mocked, corre siempre:

```python
@tagged('post_install', '-at_install', 'l10n_py')
class TestSifenSendMocked(AccountTestInvoicingCommon):
    @patch('odoo.addons.l10n_py_edi.services.sifen_client.SifenClient')
    def test_workflow(self, MockClient):
        MockClient.return_value.send_de.return_value = {'codigo': '0260'}
        # ...
```

**`test_sifen_send_external.py`** — real, solo con `--test-tags external`:

```python
@tagged('-standard', 'external', 'l10n_py_sifen_real')
class TestSifenSendReal(AccountTestInvoicingCommon):
    def setUp(self):
        super().setUp()
        ccfe = self._get_test_ccfe_or_skip()
        self.company.write({'l10n_py_ccfe_certificate': ccfe, ...})

    def _get_test_ccfe_or_skip(self):
        import os
        ccfe_path = os.environ.get('SIFEN_TEST_CCFE_PATH')
        if not ccfe_path:
            self.skipTest('SIFEN_TEST_CCFE_PATH no configurado')
        with open(ccfe_path, 'rb') as f:
            return base64.b64encode(f.read())

    def test_real_send(self):
        # Hace HTTP real a sifen-test.set.gov.py
        ...
```
