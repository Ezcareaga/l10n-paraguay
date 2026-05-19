---
source: ÑandeFact/SIFEN_REFERENCIA_COMPLETA.md (github.com/Ezcareaga/nandefact)
fetched_at: 2026-05-19
summary: Referencia técnica SIFEN — Manual Técnico v150, web services SOAP, XML schemas, firma digital, eventos, codificaciones. Lenguaje-agnóstico.
priority: critical
---

# SIFEN — Referencia Técnica Completa

> Investigación basada en: Manual Técnico SIFEN v150 (DNIT), Guía de Mejores Prácticas
> DNIT, librerías TIPS-SA (npm), Decreto 872/2023, portal e-Kuatia, y documentación oficial.
>
> Documento heredado del proyecto ÑandeFact (Node.js+TypeScript) — el contenido es
> **agnóstico al stack** y aplica idénticamente a la implementación en Python/Odoo.

## 1. Glosario esencial

- **SIFEN**: Sistema Integrado de Facturación Electrónica Nacional
- **DNIT**: Dirección Nacional de Ingresos Tributarios (antes SET)
- **DE**: Documento Electrónico (antes de ser aprobado por SIFEN)
- **DTE**: Documento Tributario Electrónico (DE aprobado por SIFEN, tiene validez legal)
- **CDC**: Código de Control — 44 dígitos numéricos que identifican únicamente un DE
- **CSC**: Código de Seguridad del Contribuyente — otorgado por DNIT para generar QR
- **KuDE**: Kuatia Documento Electrónico — representación gráfica/impresa del DE/DTE
- **CCFE**: Certificado Cualificado de Firma Electrónica (tipo F110 persona jurídica o F211 persona física)
- **Timbrado**: código numérico de autorización que la DNIT otorga para emitir DTE
- **Marangatú**: sistema de gestión tributaria de la DNIT (donde se solicita timbrado)
- **e-Kuatia**: portal/plataforma de SIFEN para consultas y gestión

## 2. Tipos de Documentos Electrónicos

### Prioridad MVP (Factura Electrónica + Nota de Crédito):
| Código | Tipo | Descripción |
|--------|------|-------------|
| 1 | Factura Electrónica (FE) | Venta directa de bienes/servicios |
| 5 | Nota de Crédito Electrónica | Devoluciones, descuentos, ajustes (referencia CDC de FE) |

### Fase 2:
| Código | Tipo | Descripción |
|--------|------|-------------|
| 6 | Nota de Débito Electrónica | Ajuste de precio hacia arriba |
| 7 | Nota de Remisión Electrónica | Traslado de mercadería |

### Fuera de scope típico:
Factura de Exportación, Autofactura, Factura Cambiaria, Comprobante de Retención,
Recibo Electrónico de Dinero, Boleta Resimple, Comprobante de Donación,
Comprobante de Importación, Comprobante de Percepción.

## 3. Estructura del CDC (44 dígitos)

```
Posición  | Largo | Campo                        | Ejemplo
----------|-------|------------------------------|--------
01-02     | 2     | Tipo de Documento Electrónico| 01 (Factura)
03-10     | 8     | RUC del emisor (sin DV)      | 80069563
11        | 1     | Dígito Verificador del RUC   | 1
12-14     | 3     | Código de Establecimiento    | 001
15-17     | 3     | Punto de Expedición          | 003
18-24     | 7     | Número del documento         | 0000137
25        | 1     | Tipo de Contribuyente        | 1 (PF) / 2 (PJ)
26-33     | 8     | Fecha de emisión (YYYYMMDD)  | 20220106
34        | 1     | Tipo de Emisión              | 1 (Normal) / 2 (Contingencia)
35-43     | 9     | Código de Seguridad Aleatorio| 936476002
44        | 1     | Dígito Verificador del CDC   | 9
```

**Ejemplo real:** `01800695631001003000013712022010619364760029`

### Algoritmo del DV del CDC
1. Tomar los primeros 43 dígitos del CDC.
2. Aplicar módulo 11 con factores multiplicadores del 2 al 9 (derecha a izquierda, cíclico).
3. Sumar todos los productos parciales.
4. Calcular `resto = suma % 11`.
5. Si `resto == 0` → DV = 0; si `resto == 1` → DV = 1; sino → DV = 11 - resto.

### Reglas del CDC
- Se genera ANTES de enviar a SIFEN (lo genera el sistema emisor).
- Si un DE es rechazado y la corrección NO altera campos del CDC, se puede REUTILIZAR el mismo CDC.
- El código seguridad aleatorio (9 dígitos) debe ser generado por el sistema del contribuyente.
- Numeración correlativa obligatoria por establecimiento y punto de expedición.

## 4. IVA Paraguay — Reglas de cálculo

### Tasas vigentes:
| Tasa | Aplicación |
|------|-----------|
| 10% (general) | Mayoría bienes y servicios, manufactura, tecnología, ropa |
| 5% (reducida) | Canasta básica, medicamentos, agropecuarios natural, alquiler vivienda, gastronomía/turismo |
| 0% (exenta) | Exportaciones, servicios educativos, ciertos servicios financieros |

### Proporción gravada del IVA:
| Proporción | Caso |
|-----------|------|
| 100% | Caso normal |
| 85% | Régimen de turismo |
| 30% | Venta de inmuebles (30% gravado al 5%, 70% exento) |
| 50% | Algunos casos especiales |

### Campos IVA en el item del DE:
```json
{
  "ivaTipo": 1,         // 1=Gravado, 2=Parcialmente exento, 3=Exento
  "ivaProporcion": 100, // 100, 85, 30, 50, etc.
  "iva": 10             // Tasa: 10, 5, o 0
}
```

### Fórmulas (precios INCLUYEN IVA — caso normal en Paraguay):
```
// Tasa 10%:
baseGravada = precioTotal / 1.10
montoIVA = precioTotal - baseGravada

// Tasa 5%:
baseGravada = precioTotal / 1.05
montoIVA = precioTotal - baseGravada

// Con proporción parcial (ej: 30% gravado al 5%):
porcionGravada = precioTotal * 0.30
baseGravada = porcionGravada / 1.05
montoIVA = porcionGravada - baseGravada
porcionExenta = precioTotal * 0.70
```

### Liquidación en la factura
Subtotales separados obligatorios:
- Total IVA 10%
- Total IVA 5%
- Total Exenta
- Total General

### Redondeo
- PYG: NO tiene decimales — todo entero.
- Otras monedas: decimales según moneda.

## 5. Estructura XML del Documento Electrónico

```
<DE>
  ├── Grupo AA: Campos que identifican el formato electrónico (versión XML, CDC)
  ├── Grupo A: Campos del DE (timbrado, fecha emisión, tipo DE)
  ├── Grupo B: Campos del emisor (RUC, razón social, establecimiento, actividades económicas)
  ├── Grupo C: Campos del usuario que firma el DE
  ├── Grupo D: Campos del receptor (RUC/CI, razón social, dirección)
  │   ├── D1: Datos generales receptor
  │   ├── D2: Datos del receptor contribuyente
  │   └── D3: Datos del receptor no contribuyente
  ├── Grupo E: Campos específicos por tipo de DE
  │   ├── E1: Campos de Factura Electrónica
  │   ├── E4: Campos de Autofactura
  │   ├── E5: Campos de Nota de Crédito/Débito
  │   ├── E7: Campos de Nota de Remisión
  │   └── E8: Campos de items/detalle
  │       ├── E8.1: Datos del item
  │       ├── E8.2: IVA del item
  │       └── E8.5: Sector automotor (si aplica)
  ├── Grupo F: Campos de condición de pago
  │   ├── F1: Contado (entregas)
  │   └── F2: Crédito (cuotas)
  ├── Grupo G: Campos complementarios (transporte, etc.)
  └── Grupo H: Campos de totales y subtotales
      ├── H1: Subtotales por IVA
      └── H2: Total general
</DE>
```

### Namespace XML:
```xml
xmlns="http://ekuatia.set.gov.py/sifen/xsd"
```

### Reglas de formato XML
- Codificación: **UTF-8**
- Sin espacios en blanco al inicio/final de campos
- Sin comentarios ni anotaciones
- Sin caracteres de formato (LF, CR, tab entre etiquetas)
- **Sin prefijos en namespace**
- NO incluir etiquetas de campos vacíos (excepto campos obligatorios)
- Sin valores negativos en campos numéricos
- Fechas formato: `YYYY-MM-DDThh:mm:ss` (ISO 8601, sin zona horaria)

## 6. Web Services SIFEN (SOAP 1.2)

### Protocolo
- Estándar: **SOAP 1.2**
- Encoding: **Document/Literal**
- Autenticación: **mutual TLS** con certificado digital CCFE
- Compresión: contenido del lote debe **comprimirse y codificarse en Base64**

### Servicios disponibles

| Web Service | Tipo | Descripción |
|------------|------|-------------|
| `siRecepDE` | Síncrono | Recepción de UN DE individual |
| `siRecepLoteDE` | Asíncrono | Recepción de lote (hasta 50 DE del mismo tipo) |
| `siResultLoteDE` | Síncrono | Consulta resultado de procesamiento de lote |
| `siConsDE` | Síncrono | Consulta DE por CDC |
| `siRecepEvento` | Síncrono | Recepción de eventos (cancelación, inutilización) |
| `siConsRUC` | Síncrono | Consulta datos de RUC |

### URLs

**Test:**
```
Base: https://sifen-test.set.gov.py/de/ws/
siRecepDE:       /de/ws/sync/recibe.wsdl
siRecepLoteDE:   /de/ws/async/recibe-lote.wsdl
siResultLoteDE:  /de/ws/consultas/consulta-lote.wsdl
siConsDE:        /de/ws/consultas/consulta.wsdl
siRecepEvento:   /de/ws/eventos/evento.wsdl
siConsRUC:       /de/ws/consultas/consulta-ruc.wsdl
```

**Producción:**
```
Base: https://sifen.set.gov.py/de/ws/
(misma estructura de paths que test)
```

### Schemas XSD
```
https://ekuatia.set.gov.py/sifen/xsd/
```

### Flujo de envío de lote
1. Crear estructura `<rLoteDE>` con hasta 50 DE firmados.
2. Comprimir el contenido XML del lote.
3. Codificar en Base64.
4. Enviar via SOAP envelope a `siRecepLoteDE`.
5. Recibir número de lote en respuesta.
6. Consultar resultado con `siResultLoteDE` (intervalo mínimo: 10 minutos).
7. Si lote en procesamiento (código 0361): consultar de nuevo.
8. Plazo de consulta de lote: hasta 48 horas post-envío.
9. Después de 48 horas: consultar cada CDC individual con `siConsDE`.

### Códigos de respuesta importantes
```
0260 - DE aprobado
0261 - DE rechazado / aprobado con observación
0360 - Número de lote inexistente
0361 - Lote en procesamiento (consultar de nuevo)
0362 - Procesamiento de lote concluido
0364 - Consulta extemporánea de lote (>48 horas)
```

## 7. Firma Digital

### Requisitos
- Certificado emitido por Prestador de Servicios de Certificación autorizado por la
  Autoridad Certificadora Raíz del Paraguay
- Tipo **F110** (persona jurídica) o **F211** (persona física)
- El RUC del contribuyente debe estar en el campo `SerialNumber` (jurídica) o
  `SubjectAlternativeName` (física)
- El certificado firma Y autentica la conexión TLS

### Estándar de firma
- **XML Digital Signature (XMLDSig)**
- El CDC precedido por `#` va en el atributo `URI` del tag `Reference`
- Cada DE individual debe estar firmado antes de incluirlo en un lote

### Almacenamiento del certificado
- **NUNCA** en texto plano
- Encriptar el archivo PKCS#12 (.p12/.pfx) en la base de datos
- La contraseña del certificado debe manejarse como secreto

## 8. KuDE (Representación Gráfica)

### Definición
Representación gráfica del DE/DTE en formato físico o digital visible. Se entrega
al receptor que no es facturador electrónico.

### Formatos soportados
1. Papel carta (formato completo)
2. Cinta de papel (formato ticket/POS)
3. Cinta resumen (versión reducida)

### Campos obligatorios del KuDE
- **Encabezado:** RUC, razón social, nombre fantasía, timbrado, establecimiento,
  punto expedición, número, fecha emisión, CDC
- **Items:** código, descripción, cantidad, precio unitario, subtotal
- **Totales:** subtotal gravado 10%, subtotal gravado 5%, subtotal exento,
  total IVA 10%, total IVA 5%, total general
- **QR Code:** código bidimensional para verificación en SIFEN
- **Información de consulta:** URL de verificación en e-Kuatia

### Regla importante
NO puede existir información en el KuDE que NO forme parte del XML del DE firmado
(excepto campos específicos del Manual Técnico como el QR).

## 9. Código QR

### Generación
1. Tomar el CDC del DE.
2. Concatenar con el CSC (32 caracteres alfanuméricos).
3. Generar hash (según metodología del Manual Técnico).
4. Construir URL con parámetros.
5. Generar imagen QR.

### URL de consulta
```
https://ekuatia.set.gov.py/consultas/qr?nVersion=150&Id={CDC}&dFeEmiDE={fechaEmision}&dRucRec={rucReceptor}&dTotGralOpe={totalGeneral}&dTotIVA={totalIVA}&cItems={cantidadItems}&DigestValue={digestValue}&IdCSC={idCSC}&cHashQR={hashQR}
```

## 10. Gestión de Eventos

### Eventos del emisor (MVP)

| Evento | Descripción | Cuándo usar |
|--------|-------------|------------|
| **Cancelación** | Cancelar un DTE aprobado | Cuando la operación no se concretó |
| **Inutilización** | Inutilizar rango de numeración | Cuando se saltearon números de DE |

### Eventos del emisor (fase futura)
| Evento | Descripción |
|--------|-------------|
| Anulación/Ajuste | Anular o ajustar un DTE (usa Nota de Crédito/Débito) |

### Eventos del receptor (futuros, NO implementar):
Conformidad, Disconformidad, Desconocimiento, Acuse.

### Estructura de evento de cancelación
```xml
<rEnvioEvento>
  <dId>{identificador}</dId>
  <dEvReg>
    <Id>{CDC del DTE a cancelar}</Id>
    <mOtEve>{motivo de cancelación}</mOtEve>
  </dEvReg>
</rEnvioEvento>
```

## 11. Proceso de Homologación

### Requisitos previos
1. RUC activo y al día con obligaciones tributarias.
2. Certificado digital CCFE (comprar a prestador autorizado).
3. Sistema informático de facturación funcional.

### Pasos
1. **Obtener acceso a ambiente de pruebas:** solicitar en Marangatú.
2. **Obtener timbrado de prueba:** via Marangatú (sin valor fiscal).
3. **Obtener CSC de prueba:** via portal e-Kuatia.
4. **Ejecutar pruebas:** emitir DE, firmar, enviar, consultar, eventos.
5. **Declarar cumplimiento:** manifestación con carácter de DDJJ.
6. **Solicitar habilitación:** en Marangatú, obtener timbrado de producción.
7. **Obtener CSC de producción:** para generar QR válidos.

### Ambiente de pruebas
- Disponible 24/7 (salvo mantenimientos)
- DE emitidos en test NO tienen valor jurídico
- Valida todo el flujo: conexión TLS, firma, XML, envío, consulta, eventos

## 12. Librerías TIPS-SA (npm) — REFERENCIA

> En `l10n-paraguay` NO usamos estas librerías (son Node). Se mantienen como
> referencia conceptual del shape de datos esperado por SIFEN.

### Paquetes
```
facturacionelectronicapy-xmlgen    → Generación de XML del DE
facturacionelectronicapy-xmlsign   → Firma digital del XML
facturacionelectronicapy-setapi    → Comunicación con Web Services SIFEN
facturacionelectronicapy-qrgen     → Generación del código QR
facturacionelectronicapy-kude      → Generación del KuDE (PDF)
```

### Equivalentes Python (lo que usaremos en `l10n_py_edi`)
| TIPS-SA (npm) | Equivalente Python |
|---------------|---------------------|
| `xmlgen` | `lxml` + templates Jinja2 (o `xmlschema` para validar) |
| `xmlsign` | `signxml` o `cryptography` + `xmlsec` |
| `setapi` | `zeep` (cliente SOAP) + `requests` con mutual TLS |
| `qrgen` | `qrcode` (con PIL) |
| `kude` | Reporte QWeb de Odoo (no librería externa) |

Ver detalles en [`40_PYTHON_LIBRARIES.md`](40_PYTHON_LIBRARIES.md).

### Estructura del `params` (emisor) — referencia del shape
```json
{
  "version": 150,
  "ruc": "80069563-1",
  "razonSocial": "Nombre del contribuyente",
  "nombreFantasia": "Nombre comercial",
  "actividadesEconomicas": [{ "codigo": "1254", "descripcion": "Venta al por menor" }],
  "timbradoNumero": "12558946",
  "timbradoFecha": "2022-08-25",
  "tipoContribuyente": 1,
  "tipoRegimen": 8,
  "establecimientos": [{
    "codigo": "001",
    "direccion": "Dirección del local",
    "numeroCasa": "123",
    "departamento": 11,
    "departamentoDescripcion": "ALTO PARANA",
    "distrito": 145,
    "distritoDescripcion": "CIUDAD DEL ESTE",
    "ciudad": 3432,
    "ciudadDescripcion": "CIUDAD DEL ESTE",
    "telefono": "0973-XXXXXX",
    "email": "email@dominio.com"
  }]
}
```

### Estructura del `data` (documento) — referencia del shape
```json
{
  "tipoDocumento": 1,
  "establecimiento": "001",
  "codigoSeguridadAleatorio": "298398",
  "punto": "001",
  "numero": "0000001",
  "fecha": "2022-08-14T10:11:00",
  "tipoEmision": 1,
  "tipoTransaccion": 1,
  "tipoImpuesto": 1,
  "moneda": "PYG",
  "cliente": {
    "contribuyente": true,
    "ruc": "2005001-1",
    "razonSocial": "Nombre cliente",
    "tipoOperacion": 1,
    "direccion": "Dirección",
    "departamento": 11, "distrito": 143, "ciudad": 3344,
    "pais": "PRY",
    "tipoContribuyente": 1,
    "documentoTipo": 1,
    "documentoNumero": "2324234",
    "telefono": "061-XXXXXX",
    "email": "cliente@email.com"
  },
  "factura": { "presencia": 1 },
  "condicion": {
    "tipo": 1,
    "entregas": [{ "tipo": 1, "monto": "150000", "moneda": "PYG", "cambio": 0 }]
  },
  "items": [{
    "codigo": "A-001",
    "descripcion": "Producto ejemplo",
    "unidadMedida": 77,
    "cantidad": 10.5,
    "precioUnitario": 10800,
    "ivaTipo": 1,
    "ivaProporcion": 100,
    "iva": 10
  }]
}
```

## 13. Codificaciones importantes

### Tipos de documento del receptor
```
1 = Cédula de Identidad paraguaya
2 = Pasaporte
3 = Cédula de Identidad extranjera
4 = Carnet de residencia
5 = Innominado (sin documento)
6 = Tarjeta Diplomática de exoneración fiscal
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
3 = Tarjeta de crédito            8 = Tarjeta que no sea crédito ni débito
4 = Tarjeta de débito             9 = Otro
5 = Transferencia
```

### Presencia del comprador
```
1 = Operación presencial          4 = Venta a domicilio
2 = Operación electrónica         5 = Operación bancaria
3 = Operación telemarketing       6 = Operación cíclica         9 = Otro
```

### Monedas
```
PYG = Guaraní Paraguayo
USD = Dólar Americano
BRL = Real Brasileño
ARS = Peso Argentino
EUR = Euro
(ver tabla completa en Manual Técnico)
```

### Unidades de medida comunes
```
77 = Unidad (UNI)
83 = Kilogramo (KG)
87 = Litro (LT)
(ver tabla completa en Manual Técnico)
```

## 14. Validaciones críticas (errores frecuentes)

### Del certificado y conexión
- Certificado vencido o revocado
- RUC del certificado no coincide con RUC del emisor
- TLS handshake fallido

### Del formato XML
- Schema inválido (no cumple XSD)
- Campos obligatorios faltantes
- Tipos de datos incorrectos
- Valores fuera de rango

### Del negocio
- Timbrado vencido o no vigente
- Número de DE duplicado (CDC ya existe)
- RUC del emisor cancelado
- RUC del receptor cancelado (B2B)
- Fecha de emisión fuera de rango permitido
- Total no cuadra con suma de items
- IVA no cuadra con base gravada
- CDC malformado o dígito verificador incorrecto

### Regla de reenvío
Si el DE es rechazado pero la corrección **NO altera campos que componen el CDC**,
se puede **reutilizar el MISMO CDC** y reenviar.

## 15. Plazos SIFEN

| Plazo | Descripción |
|-------|-------------|
| 72 horas | Tiempo máximo para transmitir DE a SIFEN después de firma digital |
| 48 horas | Tiempo máximo para consultar resultado de lote post-envío |
| 10 minutos | Intervalo mínimo sugerido entre consultas de resultado de lote |
| 5 años | Tiempo obligatorio de conservación de DTE (emisor y receptor) |
| 24 horas | Tiempo máximo de procesamiento de lote en alta carga |

## 16. Consideraciones generales para diseño

### Scope inicial recomendado
- Solo Factura Electrónica (tipo 1) + Nota de Crédito (tipo 5)
- Solo moneda PYG (Guaraníes, sin decimales) — multi-moneda fase 2
- Solo condición contado (tipo 1) inicial — crédito fase 2
- Solo presencia presencial (tipo 1) — otros tipos según necesidad
- Eventos: cancelación + inutilización
- Receptor: CI, RUC, o innominado

### Decisión: firma en servidor vs cliente
La firma se hace **en el servidor** (Odoo backend con CCFE almacenado encriptado):
- Simplifica enormemente el manejo de certificados
- Evita tener el `.p12` en cada dispositivo (relevante para POS móvil)
- Permite rotación centralizada de certificados
- Compatible con multi-empresa: cada `res.company` con su CCFE

### Flujo conceptual completo
1. Usuario crea factura en Odoo (puede ser POS, sale.order, account.move directo)
2. Odoo `account.move.action_post()` dispara validaciones locales
3. `account.edi.format` para Paraguay genera CDC, calcula IVA, valida
4. `account.edi.format._post_invoice_edi()` construye XML
5. Servicio Python firma XML con CCFE del `res.company`
6. Servicio Python envía a SIFEN (siRecepDE o siRecepLoteDE)
7. Respuesta SIFEN procesada → `edi_state` actualizado en `account.edi.document`
8. Si aprobada → reporte QWeb genera KuDE PDF como `ir.attachment`
9. (Opcional) Email/WhatsApp al cliente con KuDE adjunto
10. Auditoría completa en chatter de `account.move` y logs

---

*Documento heredado de ÑandeFact (2026-02-07). Fuentes: Manual Técnico SIFEN v150,
DNIT, TIPS-SA, portal e-Kuatia.*

*Para mapeo conceptual a entidades Odoo, ver [`01_SIFEN_KNOWLEDGE_BASE.md`](01_SIFEN_KNOWLEDGE_BASE.md)
sección "Mapeo conceptual a Odoo".*
