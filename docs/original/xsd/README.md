# XSDs oficiales SIFEN

Esquemas XML del Sistema Integrado de Facturación Electrónica Nacional (SIFEN)
publicados por la DNIT (Dirección Nacional de Ingresos Tributarios) del Paraguay.

- **Versión:** Manual Técnico v150 (release de esquemas DNIT `20190910_XSD_v150`,
  fechado 2019-09-10).
- **Fecha de descarga:** 2026-06-15.
- **Fuente directa:** repositorio open source `rshk-jsifenlib` de Roshka
  (<https://github.com/roshkadev/rshk-jsifenlib>), carpeta
  `docs/set/20190910_XSD_v150/`, que reempaqueta sin modificar el ZIP oficial
  de la DNIT. El `xmldsig-core-schema.xsd` (estándar W3C XML-DSig, requerido por
  `DE_v150.xsd` y `Evento_v150.xsd` para la firma) proviene del mirror del sitio
  oficial incluido en el mismo repo (`docs/set/ekuatia.set.gov.py/sifen/xsd/`).
- **Origen canónico DNIT:** <https://ekuatia.set.gov.py/sifen/xsd/> y el paquete
  `Estructura_DE xsd.rar` publicado en
  <https://www.dnit.gov.py/web/e-kuatia/documentacion-tecnica> (no se usó como
  fuente directa por venir en formato RAR no extraíble en el entorno actual; el
  contenido es idéntico al de jsifenlib).
- **Licencia:** documentación oficial pública de la DNIT. `xmldsig-core-schema.xsd`
  es el esquema estándar W3C XML Signature (recomendación pública).

## Archivos

Set completo y autocontenido (cierre de dependencias verificado: ningún
`schemaLocation` apunta a un archivo ausente).

| Archivo                    | Tamaño | Propósito                                                      |
| -------------------------- | ------ | -------------------------------------------------------------- |
| `DE_v150.xsd`              | 80 KB  | Estructura raíz del Documento Electrónico (`rDE` → `DE`)       |
| `DE_Types_v150.xsd`        | 65 KB  | Tipos auxiliares del DE (grupos A-H, ítems, IVA, totales)      |
| `Evento_v150.xsd`          | 13 KB  | Estructura de eventos (cancelación, inutilización, etc.)       |
| `Evento_Types_v150.xsd`    | 12 KB  | Tipos auxiliares de los eventos                                |
| `Paises_v100.xsd`          | 52 KB  | Catálogo de países (ISO) referenciado por el DE                |
| `Departamentos_v141.xsd`   | 6 KB   | Catálogo de departamentos del Paraguay                         |
| `Monedas_v150.xsd`         | 56 KB  | Catálogo de monedas referenciado por el DE                     |
| `Unidades_Medida_v141.xsd` | 15 KB  | Catálogo de unidades de medida de los ítems                    |
| `xmldsig-core-schema.xsd`  | 10 KB  | Esquema W3C XML-DSig para la firma `<Signature>` del DE/evento |

Cierre de dependencias (de los `import`/`include` reales):

- `DE_v150.xsd` → `DE_Types_v150`, `Paises_v100`, `Departamentos_v141`,
  `Monedas_v150`, `Unidades_Medida_v141`, `xmldsig-core-schema`.
- `Evento_v150.xsd` → `Evento_Types_v150`, `xmldsig-core-schema`.
- Los `*_Types`, catálogos y `xmldsig` no tienen dependencias locales.

> Nota: el brief de PR-3 mencionaba un `siTypes_v150.xsd`; en la distribución
> oficial los tipos viven en `DE_Types_v150.xsd` y `Evento_Types_v150.xsd` (no
> existe un archivo con ese nombre exacto).

Los archivos `Estructura_DE_xsd.xml` y `Extructura_xml_DE.xml` (preexistentes en
esta carpeta) son **ejemplos** de estructura de documento, no esquemas — se
conservan como referencia.

## Validación

Verificado el 2026-06-15:

- Los 9 XSD parsean como XML válido (`xml.etree.ElementTree`).
- `DE_v150.xsd` y `Evento_v150.xsd` compilan como `lxml.etree.XMLSchema` con
  todos los `import` resueltos — listos para validar instancias.

## Uso

Estos XSDs son consultados (no embebidos como recurso del módulo) por
`l10n_py_edi` (Fase 2) para:

1. Validar el XML del DE generado **antes de firmar**, en tests y CI.
2. Validación defensiva opcional pre-envío a SIFEN en runtime.

El proyecto NO los redistribuye como `data/` del addon Odoo — viven en `docs/`
como referencia técnica oficial.
