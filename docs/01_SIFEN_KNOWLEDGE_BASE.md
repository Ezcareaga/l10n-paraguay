---
source: Extracted from ÑandeFact CLAUDE.md (github.com/Ezcareaga/nandefact)
fetched_at: 2026-05-19
summary: Base de conocimiento conceptual SIFEN/DNIT — glosario, tipos de documento, CDC, IVA, firma digital, KuDE, eventos. Lenguaje-agnóstico, válido para cualquier implementación (Odoo o no).
priority: critical
---

# SIFEN — Base de Conocimiento Conceptual

> Este documento extrae el conocimiento **conceptual** del proyecto ÑandeFact (sistema
> previo en Node.js+TypeScript) y lo presenta de forma agnóstica al stack.
> La referencia **técnica completa** (formato XML, web services, códigos) vive en
> [`02_SIFEN_REFERENCIA_COMPLETA.md`](02_SIFEN_REFERENCIA_COMPLETA.md).
>
> Cuando este documento dice "el sistema", reemplazá mentalmente por "los módulos
> `l10n_py_*` que vamos a construir".

## 1. Glosario esencial

| Término | Significado |
|---------|-------------|
| **SIFEN** | Sistema Integrado de Facturación Electrónica Nacional |
| **DNIT** | Dirección Nacional de Ingresos Tributarios (antes SET) |
| **DE** | Documento Electrónico (antes de ser aprobado por SIFEN) |
| **DTE** | Documento Tributario Electrónico (DE aprobado — tiene validez legal) |
| **CDC** | Código de Control — 44 dígitos numéricos, identifica únicamente un DE |
| **CSC** | Código de Seguridad del Contribuyente — otorgado por DNIT para QR |
| **KuDE** | Kuatia Documento Electrónico — representación gráfica del DE/DTE (PDF) |
| **CCFE** | Certificado Cualificado de Firma Electrónica (PKCS#12 .p12/.pfx) |
| **Timbrado** | Código numérico de autorización DNIT para emitir DTE |
| **Marangatú** | Sistema de gestión tributaria DNIT (donde se solicita timbrado) |
| **e-Kuatia** | Portal/plataforma SIFEN para consultas y gestión |

## 2. Tipos de Documento Electrónico

| Código | Tipo | Notas |
|--------|------|-------|
| 1 | Factura Electrónica (FE) | Core obligatorio |
| 4 | Autofactura Electrónica | Compras a no contribuyentes |
| 5 | Nota de Crédito Electrónica | Devoluciones, descuentos |
| 6 | Nota de Débito Electrónica | Ajustes monto hacia arriba |
| 7 | Nota de Remisión Electrónica | Traslado de mercadería |

**Otros (fuera de scope típico):** Factura de Exportación, Factura Cambiaria,
Comprobante de Retención, Recibo Electrónico de Dinero, Boleta Resimple,
Comprobante de Donación, Comprobante de Importación, Comprobante de Percepción.

## 3. CDC — Código de Control (44 dígitos)

El CDC identifica de manera **única** cada DE, aprobado o no.

```
Posición  Largo  Campo
01-02     2      Tipo de DE (01=Factura, 05=NC, 06=ND, 07=NR)
03-10     8      RUC emisor (sin DV)
11        1      Dígito Verificador del RUC
12-14     3      Código de Establecimiento (ej: 001)
15-17     3      Punto de Expedición (ej: 003)
18-24     7      Número del documento
25        1      Tipo Contribuyente (1=Persona Física, 2=Persona Jurídica)
26-33     8      Fecha de emisión (YYYYMMDD)
34        1      Tipo de Emisión (1=Normal, 2=Contingencia)
35-43     9      Código Seguridad Aleatorio (lo genera el sistema)
44        1      Dígito Verificador del CDC (módulo 11)
```

**Ejemplo:** `01800695631001003000013712022010619364760029`

### Algoritmo del DV del CDC

1. Tomar los primeros 43 dígitos.
2. Aplicar módulo 11 con factores 2-9 cíclicos de derecha a izquierda.
3. Sumar los productos parciales.
4. `resto = suma % 11`.
5. Si `resto == 0` → DV = 0. Si `resto == 1` → DV = 1. Sino → DV = 11 − resto.

### Reglas del CDC

- Se genera **ANTES** de enviar a SIFEN — lo construye el sistema emisor, no DNIT.
- Si un DE es **rechazado** y la corrección NO altera campos del CDC, se puede
  **reutilizar el mismo CDC** al reenviar.
- El **código seguridad aleatorio** (9 dígitos) lo genera el sistema; no hay un
  algoritmo prescripto, solo que sea numérico y único en práctica.
- **Numeración correlativa OBLIGATORIA** por establecimiento + punto de expedición.
  Saltarse números requiere envío de evento de **Inutilización**.

## 4. IVA Paraguay — Reglas conceptuales

### Tasas vigentes

| Tasa | Aplicación |
|------|-----------|
| 10% (general) | Mayoría bienes/servicios, manufactura, tecnología, ropa |
| 5% (reducida) | Canasta básica, medicamentos, agropecuarios natural, alquiler vivienda, gastronomía/turismo |
| 0% (exenta) | Exportaciones, educación, ciertos servicios financieros |

### Proporciones especiales

No siempre se grava el 100% del valor:

| Proporción | Caso |
|-----------|------|
| 100% | Caso normal |
| 85% | Régimen de turismo |
| 30% | Venta de inmuebles (30% gravado al 5%, 70% exento) |
| 50% | Casos especiales |

### Fórmulas (precios INCLUYEN IVA)

```
Tasa 10%: base = total / 1.10        iva = total - base
Tasa 5%:  base = total / 1.05        iva = total - base
Exenta:   base = 0                   iva = 0

Con proporción parcial (ej: 30% gravado al 5%):
  porcion_gravada = total * 0.30
  base = porcion_gravada / 1.05
  iva = porcion_gravada - base
  porcion_exenta = total * 0.70
```

### Regla de redondeo

- **PYG (Guaraníes): SIN decimales**. Todo entero.
- **USD u otra moneda**: decimales según la moneda destino.

### Liquidación obligatoria en la factura

Subtotales separados — el XML SIFEN los exige explícitamente:

- Total IVA 10% (suma de montoIVA de items al 10%)
- Total IVA 5% (suma de montoIVA de items al 5%)
- Total Exenta (suma de montos exentos)
- Total General (suma de todos los items)

## 5. Firma Digital del DE

- Algoritmo: **RSA 2048 bits**
- Hash: **SHA-256**
- Formato: **XMLDSig (Enveloped Signature)**
- URI del tag `<Reference>`: CDC precedido por `#`
- **Cada DE individual firmado ANTES** de incluirlo en lote
- Certificado **PKCS#12** (`.p12` / `.pfx`) emitido por **prestador autorizado por la
  Autoridad Certificadora Raíz del Paraguay** (tipo F110 jurídica, F211 física)
- El RUC del contribuyente debe estar en el **SerialNumber** (jurídica) o
  **SubjectAlternativeName** (física) del certificado
- El certificado firma **Y** autentica la conexión TLS (mutual TLS contra SIFEN)
- **NUNCA almacenar en texto plano** — encriptar en BD/disco

## 6. KuDE — Representación Gráfica

Representación gráfica del DE/DTE en formato físico o digital visible. Se entrega
al receptor cuando no es facturador electrónico (la mayoría de casos B2C).

### Formatos
1. Papel carta (formato completo)
2. Cinta de papel (formato ticket/POS) — relevante para `l10n_py_pos`
3. Cinta resumen (versión reducida)

### Campos obligatorios
- **Encabezado:** RUC, razón social, nombre fantasía, timbrado, establecimiento,
  punto de expedición, número, fecha emisión, CDC
- **Items:** código, descripción, cantidad, precio unitario, subtotal
- **Totales:** subtotal gravado 10%, subtotal gravado 5%, subtotal exento,
  total IVA 10%, total IVA 5%, total general
- **QR Code:** para verificación en e-Kuatia
- **Info consulta:** URL de verificación en e-Kuatia

### Regla cardinal

> NO puede existir información en el KuDE que NO forme parte del XML del DE
> firmado (excepto campos específicos del Manual Técnico como el QR).

## 7. Código QR

### Composición

El QR contiene una URL con parámetros para consulta automática del DE/DTE.

```
https://ekuatia.set.gov.py/consultas/qr?
  nVersion=150
  &Id={CDC}
  &dFeEmiDE={fechaEmision}
  &dRucRec={rucReceptor}
  &dTotGralOpe={totalGeneral}
  &dTotIVA={totalIVA}
  &cItems={cantidadItems}
  &DigestValue={digestValue}
  &IdCSC={idCSC}
  &cHashQR={hashQR}
```

### Generación

1. Tomar el CDC del DE.
2. Concatenar con el CSC (Código de Seguridad del Contribuyente, 32 caracteres
   alfanuméricos otorgado por DNIT).
3. Generar hash (según metodología del Manual Técnico).
4. Construir URL con parámetros.
5. Generar imagen QR.

## 8. Eventos SIFEN

### Eventos del emisor (implementar en core)

| Evento | Descripción | Cuándo usar |
|--------|-------------|------------|
| **Cancelación** | Cancelar un DTE aprobado | Operación no se concretó |
| **Inutilización** | Inutilizar rango de numeración | Se saltearon números |
| **Anulación / Ajuste** | Anular o ajustar un DTE | Vía Nota de Crédito/Débito |

### Eventos del receptor (NO implementar)

Conformidad, Disconformidad, Desconocimiento, Acuse de Recibo — fuera de scope
de la mayoría de implementaciones.

### Estructura mínima de evento de cancelación

```xml
<rEnvioEvento>
  <dId>{identificador}</dId>
  <dEvReg>
    <Id>{CDC del DTE a cancelar}</Id>
    <mOtEve>{motivo de cancelación}</mOtEve>
  </dEvReg>
</rEnvioEvento>
```

## 9. Web Services SIFEN (SOAP 1.2)

### Ambientes

| Ambiente | URL base |
|----------|----------|
| Test (homologación) | `https://sifen-test.set.gov.py/de/ws/` |
| Producción | `https://sifen.set.gov.py/de/ws/` |

### Servicios MVP

| WS | Tipo | Descripción |
|----|------|-------------|
| `siRecepDE` | Síncrono | Recepción de UN DE individual |
| `siRecepLoteDE` | Asíncrono | Recepción de lote (hasta 50 DE) |
| `siResultLoteDE` | Síncrono | Consulta resultado de lote |
| `siConsDE` | Síncrono | Consulta DE por CDC |
| `siRecepEvento` | Síncrono | Recepción de eventos (cancelación, inutilización) |
| `siConsRUC` | Síncrono | Consulta datos de RUC |

### Códigos de respuesta clave

| Código | Significado |
|--------|-------------|
| `0260` | DE aprobado |
| `0261` | DE aprobado con observación |
| `0300-0399` | Rechazo (ver mensaje específico) |
| `0360` | Lote recibido (asíncrono) |
| `0361` | Lote en procesamiento (consultar de nuevo en ≥10 min) |
| `0362` | Procesamiento de lote concluido |
| `0364` | Consulta extemporánea (>48h) — consultar CDC individual |

### Reglas de conexión

- **SOAP 1.2 Document/Literal**
- **Mutual TLS** con CCFE del contribuyente
- Lote: contenido XML **comprimido + Base64**
- Plazo consulta resultado de lote: **48 horas** post-envío
- Intervalo mínimo entre consultas: **10 minutos**

## 10. Plazos críticos

| Plazo | Descripción |
|-------|-------------|
| 72 horas | Tiempo máximo para transmitir DE a SIFEN post-firma |
| 48 horas | Plazo de consulta de resultado de lote post-envío |
| 10 minutos | Intervalo mínimo entre consultas de resultado de lote |
| 5 años | Conservación obligatoria de DTE (emisor y receptor) |
| 24 horas | Tiempo máximo de procesamiento de lote en alta carga |

## 11. Homologación

### Pasos
1. RUC activo y al día con obligaciones tributarias.
2. Solicitar **acceso a ambiente de pruebas** en Marangatú.
3. Obtener **timbrado de prueba** (sin valor fiscal) + **CSC de prueba**.
4. Ejecutar pruebas: emitir DE, firmar, enviar, consultar, eventos.
5. **Declarar cumplimiento** (DDJJ).
6. Solicitar **habilitación de producción** en Marangatú.
7. Obtener **timbrado producción** + **CSC producción**.

### Ambiente de pruebas
- Disponible 24/7 (salvo mantenimientos comunicados)
- DE emitidos en test **NO** tienen valor jurídico
- Mismo flujo completo: TLS, firma, XML, envío, consulta, eventos

## 12. Codificaciones DNIT/SIFEN

### Tipos de documento del receptor
```
1 = Cédula de Identidad paraguaya
2 = Pasaporte
3 = Cédula de Identidad extranjera
4 = Carnet de residencia
5 = Innominado (sin documento, hasta cierto monto)
6 = Tarjeta Diplomática
9 = Otro
```

### Tipos de contribuyente
```
1 = Persona Física
2 = Persona Jurídica
```

### Tipos de condición de venta
```
1 = Contado
2 = Crédito
```

### Tipos de pago (entregas)
```
1 = Efectivo                      6 = Giro
2 = Cheque                        7 = Billetera electrónica
3 = Tarjeta de crédito            8 = Tarjeta no crédito/débito
4 = Tarjeta de débito             9 = Otro
5 = Transferencia
```

### Presencia del comprador
```
1 = Presencial          2 = Electrónica          3 = Telemarketing
4 = A domicilio         5 = Bancaria             6 = Cíclica          9 = Otro
```

### Monedas
```
PYG = Guaraní Paraguayo
USD = Dólar Americano
BRL = Real Brasileño
ARS = Peso Argentino
EUR = Euro
(tabla completa en Manual Técnico DNIT)
```

### Unidades de medida comunes
```
77 = Unidad (UNI)
83 = Kilogramo (KG)
87 = Litro (LT)
(tabla completa en Manual Técnico DNIT)
```

## 13. Validaciones de negocio que SIFEN ejecuta

### Certificado y conexión
- Certificado vencido o revocado
- RUC del certificado ≠ RUC del emisor
- TLS handshake fallido

### Formato XML
- Schema inválido (no cumple XSD oficial)
- Campos obligatorios faltantes
- Tipos de datos incorrectos
- Valores fuera de rango

### Negocio
- Timbrado vencido o no vigente
- Número de DE duplicado (CDC ya existe en SIFEN)
- RUC del emisor cancelado
- RUC del receptor cancelado (B2B)
- Fecha de emisión fuera de rango permitido
- Total no cuadra con suma de items
- IVA no cuadra con base gravada
- CDC malformado o DV incorrecto

## 14. Mapeo conceptual a Odoo

> Esta sección NO es prescriptiva — es para orientar el diseño en Odoo. Decisiones
> finales viven en [`50_MODULES_ROADMAP.md`](50_MODULES_ROADMAP.md).

| Concepto SIFEN | Modelo Odoo destino | Módulo |
|----------------|---------------------|--------|
| Emisor (Comercio + RUC + Timbrado) | `res.company` (extendido) | `l10n_py_base` |
| Punto de Expedición | Probablemente nuevo modelo `l10n_py.point_of_emission` o campo en `account.journal` | `l10n_py_account` |
| Establecimiento | Campo extendido en `res.company` o `res.partner` (sucursales) | `l10n_py_base` |
| RUC | Campo en `res.partner` siguiendo patrón `l10n_latam_base` (`l10n_latam_identification_type`) | `l10n_py_base` |
| Tipos de Documento (FE, NC, ND, NR) | Records de `l10n_latam.document.type` | `l10n_py_account` |
| Receptor (Cliente) | `res.partner` | core |
| DE / DTE | `account.move` (extendido) | `l10n_py_edi` |
| Detalles (items) | `account.move.line` (líneas de factura) | core + `l10n_py_edi` |
| CDC | Campo computed en `account.move` (`l10n_py_edi_cdc`) | `l10n_py_edi` |
| XML DE | Generado por `account.edi.format` → almacenado en `ir.attachment` ligado al move | `l10n_py_edi` |
| Firma digital | Servicio Python (signxml) llamado desde el `account.edi.format` | `l10n_py_edi` |
| Estado SIFEN | Campo `edi_state` del framework `account.edi.document` | `l10n_py_edi` |
| Eventos (Cancelación, Inutilización) | Wizards + métodos del move + envío SOAP | `l10n_py_edi` |
| KuDE | Reporte QWeb generado al postear el move | `l10n_py_edi` |
| Libros IVA / Hechauka | Reportes contables | `l10n_py_reports` |

Ver detalles en [`50_MODULES_ROADMAP.md`](50_MODULES_ROADMAP.md) y los análisis de
[`32_L10N_PERU_REFERENCE.md`](32_L10N_PERU_REFERENCE.md),
[`33_L10N_ECUADOR_REFERENCE.md`](33_L10N_ECUADOR_REFERENCE.md),
[`34_L10N_ARGENTINA_REFERENCE.md`](34_L10N_ARGENTINA_REFERENCE.md).

## 15. Diferencias clave Paraguay vs vecinos

| Tema | Paraguay (SIFEN) | Perú (SUNAT) | Ecuador (SRI) | Argentina (AFIP) |
|------|------------------|--------------|---------------|------------------|
| Identificador documento | CDC 44 dígitos | UBL 2.1 ID | Clave de acceso 49 dígitos | CAE post-aprobación |
| Generación del ID | En sistema emisor | En sistema emisor | En sistema emisor | Devuelto por AFIP |
| Formato XML | Propio (xsd SIFEN) | UBL 2.1 | Propio (xsd SRI) | Propio (wsfev1) |
| Firma | XMLDSig RSA-2048+SHA-256 | XMLDSig | XMLDSig | TLS + token |
| Numeración | Correlativa estricta, inutilización | Por serie | Por punto de emisión | CAE consume número |
| Tasas IVA | 10% y 5% | 18% (IGV) | 12% | 21%, 10.5%, 2.5% |
| Decimales moneda local | **NO** (PYG entero) | Sí (2 dec) | Sí (2 dec) | Sí (2 dec) |
| Token vs cert | Certificado propio | Cert propio + opcional IAP | Cert propio | Cert propio |

**Implicación de diseño:** Ecuador (clave de acceso 49 dígitos + flujo similar) es
la referencia más cercana al modelo SIFEN. Perú aporta el patrón maestro de
`account.edi.format` en localización LATAM. Argentina aporta el patrón maduro de
`l10n_latam_invoice_document` para clasificación de tipos de documento.
