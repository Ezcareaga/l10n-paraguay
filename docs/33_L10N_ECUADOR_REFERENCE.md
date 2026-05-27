---
source: https://www.odoo.com/documentation/18.0/applications/finance/fiscal_localizations/ecuador.html + análisis local references/odoo-18.0/addons/l10n_ec + OCA/l10n-ecuador (17.0 branch tiene material real)
fetched_at: 2026-05-19
summary: Localización Ecuador — el patrón más cercano a Paraguay/SIFEN. Clave de acceso 49 dígitos (análogo a CDC), firma .p12 propia, conexión directa a SRI, sistema de retenciones.
priority: critical
---

# Ecuador — patrón EDI más cercano a Paraguay

> **Por qué Ecuador es la mejor referencia para Paraguay:**
>
> 1. **Clave de acceso de 49 dígitos** — concepto análogo al CDC paraguayo de 44 dígitos
> 2. **Certificado .p12 propio** del contribuyente → conexión directa al SRI
>    (Paraguay: CCFE propio → conexión directa a SIFEN). Sin intermediarios IAP/OSE.
> 3. **Sistema de retenciones IVA + Renta** — Paraguay también tiene retenciones IVA/IRE
> 4. **Receipt-acknowledgement flow** con SRI — Paraguay tiene el mismo patrón con SIFEN
> 5. **OCA tiene addons para EC en 17.0** (`l10n_ec_base`, `l10n_ec_account_edi`,
>    `l10n_ec_credit_note`, `l10n_ec_withhold`) — disponibles localmente para
>    referencia
> 6. **Tema de comprobantes con secuencia por punto de emisión** — Paraguay igual

## 1. Módulos del paquete Ecuador

| Módulo                        | Técnico               | Disp. en Comm?                       |
| ----------------------------- | --------------------- | ------------------------------------ |
| Ecuadorian Accounting         | `l10n_ec`             | ✓ (Odoo 18 community sparse-checked) |
| Ecuadorian Accounting EDI     | `l10n_ec_edi`         | ✗ (Enterprise)                       |
| Ecuadorian Accounting Reports | `l10n_ec_reports`     | ✗ Enterprise                         |
| ATS Report                    | `l10n_ec_reports_ats` | ✗ Enterprise                         |
| OCA Ecuador EDI base          | `l10n_ec_base`        | ✓ (`references/l10n-ecuador-17.0/`)  |
| OCA Ecuador Account EDI       | `l10n_ec_account_edi` | ✓ (idem)                             |
| OCA Ecuador Credit Note       | `l10n_ec_credit_note` | ✓ (idem)                             |
| OCA Ecuador Withhold          | `l10n_ec_withhold`    | ✓ (idem)                             |

**Implicación:** Para community EDI usar el OCA — está en 17.0, próximo a port
a 18.0.

## 2. Setup empresa

### Datos clave (mapea a `l10n_py_base` análogamente)

- **Country**: Ecuador
- **Identification Type**: RUC (13 dígitos)
- **VAT field**: RUC
- **SRI Taxpayer Type**: Regular | RIMPE | Special (régimen tributario)
- **Forced to Keep Accounting Books**: Boolean (algunos contribuyentes están exentos)

### Equivalente Paraguay

- **Country**: Paraguay
- **Identification Type**: RUC
- **VAT field**: RUC (8-9 dígitos + DV)
- **Tipo Contribuyente**: PF | PJ
- **Tipo Régimen**: catálogo SIFEN (8=Turismo, etc.)

## 3. Document types

Ecuador maneja:

- Factura
- Nota de Crédito
- Nota de Débito
- **Liquidación de Compras** (para compras a no-contribuyentes)
- **Retención** (documentación de tax withheld)
- **Guía de Remisión** (electronic shipping)

Cada uno con código SRI y sequence.

### Equivalente Paraguay

- Factura Electrónica (01)
- Autofactura (04) — análogo a Liquidación de Compras
- Nota de Crédito (05)
- Nota de Débito (06)
- Nota de Remisión (07) — análogo a Guía de Remisión
- **Comprobante de Retención** — NO es un DE separado en Paraguay (las
  retenciones se integran al flujo IVA/IRE/IRP de forma distinta)

## 4. Configuración tax (lo que va a `l10n_py_account`)

### Estructura naming Ecuador

```
"IVA 12% (104, [form code] [tax support code] [tax support short name])"
```

Cada tax referencia:

- 104 form code (campo del reporte 104)
- Tax support classification (sustento tributario)

### Estructura naming Paraguay (propuesta)

```
"IVA 10% (Gravada)"
"IVA 5% (Reducida)"
"IVA Exenta"
```

Campos custom en `account.tax`:

- `l10n_py_tax_code`: código SIFEN del tax
- `l10n_py_iva_proporcion`: 100, 85, 30, 50

Sin "form code" porque los reportes paraguayos (Hechauka, libros IVA) tienen
otra estructura.

## 5. Configuración del journal de ventas

### Ecuador (lo que define el setup)

```
[Entity]-[Point] [Document Type]
Ej: "001-001 Sales Documents"
```

Campos:

- **Emission Entity**: número del establecimiento (3 dígitos)
- **Emission Point**: número del punto de emisión (3 dígitos)
- **Short Code**: prefijo de 5 dígitos para la sequence (ej: VT001)
- **Electronic invoicing**: checkbox para activar transmisión

### Equivalente Paraguay

```
[Establishment]-[Point] [Document]
Ej: "001-001 Facturación"
```

Campos custom en `account.journal`:

- `l10n_py_establishment` (Char 3)
- `l10n_py_point_of_emission` (Char 3)
- `l10n_py_timbrado_id` (Many2one a `l10n_py.timbrado`)

Y el field estándar:

- `edi_format_ids` con el record SIFEN seleccionado

## 6. Electronic signature

### Ecuador

- Formato: **PKCS#12 (.p12)**
- Issued by SRI
- Usado para firmar XML del documento

### Paraguay

- Formato: **PKCS#12 (.p12 / .pfx)**
- Issued by prestador autorizado por Autoridad Certificadora Raíz del Paraguay
- Tipos F110 (PJ) o F211 (PF)
- Usado para firmar XML **Y** autenticar mutual TLS con SIFEN

Esto último es una diferencia: en Ecuador el .p12 firma pero la conexión al SRI
puede ser HTTPS estándar; en Paraguay el .p12 también es el client cert para el
TLS handshake (esto cambia cómo se configura el cliente SOAP).

### Implicación en código Python

```python
# Ecuador (más simple)
from cryptography.hazmat.primitives.serialization.pkcs12 import load_pkcs12
p12 = load_pkcs12(cert_bytes, password)
xml_signed = sign_xml(xml, p12.cert, p12.key)
response = requests.post(SRI_URL, data=xml_signed.encode())

# Paraguay (mutual TLS)
import zeep
from requests import Session
from requests_pkcs12 import Pkcs12Adapter
session = Session()
session.mount('https://', Pkcs12Adapter(pkcs12_data=cert_bytes, pkcs12_password=password))
transport = zeep.transports.Transport(session=session)
client = zeep.Client(SIFEN_WSDL, transport=transport)
response = client.service.siRecepDE(xml_firmado)
```

Ver detalle en [`40_PYTHON_LIBRARIES.md`](40_PYTHON_LIBRARIES.md) librería `requests-pkcs12`.

## 7. Clave de acceso vs CDC

### Ecuador: clave de acceso (49 dígitos)

```
Posición  Largo  Campo
1-8       8      Fecha emisión (DDMMYYYY)
9-10      2      Código tipo comprobante
11-13     3      RUC contribuyente (parcial)
14-16     3      Emisión entity (establecimiento)
17-19     3      Emisión point (punto de emisión)
20-28     9      Secuencial (per tipo doc)
29-37     8 + 1  Código numérico + tipo emisión
38-48     11     Adicional
49        1      DV módulo 11
```

### Paraguay: CDC (44 dígitos)

```
Posición  Largo  Campo
01-02     2      Tipo Documento Electrónico
03-10     8      RUC emisor (sin DV)
11        1      DV RUC
12-14     3      Código Establecimiento
15-17     3      Punto Expedición
18-24     7      Número del documento
25        1      Tipo Contribuyente
26-33     8      Fecha emisión (YYYYMMDD)
34        1      Tipo Emisión
35-43     9      Código Seguridad Aleatorio
44        1      DV CDC
```

Diferencias:

- Largo: 44 vs 49
- Paraguay incluye `tipo_contribuyente`, Ecuador no
- Paraguay tiene un "código de seguridad aleatorio" de 9 dígitos generado por
  el sistema; Ecuador tiene "código numérico" + "tipo emisión" en un campo
  combinado
- Algoritmo DV: ambos módulo 11

**El algoritmo de generación es similar — el código de `l10n_ec_account_edi`
para clave de acceso es referencia directa para el CDC paraguayo.**

## 8. Withholdings (mapea a `l10n_py_withholding`)

### Ecuador

Dos tipos:

- **VAT Withholding (Retención IVA)**: % retenido sobre IVA en compras
- **Income Tax Withholding (Retención a la Renta)**: % retenido sobre base
  imponible de la compra

Configurado vía:

- **SRI Taxpayer Type** del partner: define % a aplicar (consumibles, servicios,
  tarjeta crédito)
- Account.tax con flag de withhold
- Generación automática de "Comprobante de Retención" cuando se valida una bill

### Paraguay

Estructura similar. Tipos:

- **Retención IVA** (% sobre IVA en compras)
- **Retención IRE** (Impuesto a la Renta Empresarial)
- **Retención IRP** (Impuesto a la Renta Personal)

Probable diseño:

- Campo `l10n_py_withhold_type` en `account.tax`
- Campo `l10n_py_taxpayer_type` en `res.partner`
- Generación de "Comprobante de Retención" como subtipo de `account.move`
  (move_type='entry' con flag custom, o move_type custom si Odoo lo permite)

Detalle en una futura iteración cuando se implemente `l10n_py_withholding`.

## 9. Reportes Ecuador

- **Form 103** — Income tax withholdings
- **Form 104** — VAT report
- **ATS Report** (Anexo Transaccional Simplificado) — XML export para DIMM

### Equivalente Paraguay

- **Libro IVA Ventas**
- **Libro IVA Compras**
- **Hechauka** — sistema declaración DNIT (formato específico)
- **DDJJ IVA mensual** — Form 120 (o equivalente)
- **DDJJ IRE / IRP**

## 10. Flujo de envío al SRI vs SIFEN

### Ecuador (SRI)

1. Documento creado en Odoo con datos completos
2. Sistema firma con .p12 (XMLDSig)
3. Genera clave de acceso (49 dígitos)
4. Envía XML al SRI (REST API)
5. SRI devuelve **autorización** con timestamp
6. Almacena XML original + recibo de autorización
7. Genera **RIDE** (representación impresa) para entregar al cliente

### Paraguay (SIFEN)

1. Documento creado en Odoo con datos completos
2. Sistema firma con CCFE (XMLDSig)
3. Genera CDC (44 dígitos)
4. Envía DE al SIFEN via **SOAP 1.2 con mutual TLS** (NO REST)
5. SIFEN devuelve código respuesta (0260=aprobado, 0261=observado, 03xx=rechazado)
6. Almacena XML firmado + respuesta SIFEN
7. Genera **KuDE** (representación impresa) para entregar al cliente

**Diferencias críticas:**

- REST (EC) vs SOAP (PY)
- Sin mutual TLS (EC) vs con mutual TLS (PY)
- Modelos de error distintos

## 11. Take-aways prácticos

1. **Estudiar `references/l10n-ecuador-17.0/l10n_ec_account_edi/`** (cuando se
   port a 18.0, sino del 17.0) para el patrón de:
   - Generación de XML
   - Firma con .p12
   - Envío al SRI
   - Manejo de respuestas
   - Almacenamiento de attachments
2. **Adaptar a SOAP**: cambiar `requests` por `zeep` en la capa de transporte
3. **Adaptar a mutual TLS**: agregar `requests-pkcs12` al transport del zeep client
4. **Replicar el modelo de retenciones** (ver `l10n_ec_withhold` en 17.0) para
   `l10n_py_withholding`
5. **Replicar el patrón de credit_note** (ver `l10n_ec_credit_note` en 17.0)
   para Paraguay — flujo de nota de crédito que referencia un DE original

## Queries útiles

```
codegraph search "clave_acceso generation"
codegraph search "l10n_ec_account_edi sign_xml"
codegraph file references/l10n-ecuador-17.0/l10n_ec_account_edi/__manifest__.py
```
