---
source: Research bloqueante PR-4 (firma XAdES SIFEN) — fuentes locales (ejemplo oficial DNIT + docs/40) corroboradas con implementaciones de referencia (rshk-jsifenlib Java, TIPS-SA Node) y docs de librerías Python (signxml, cryptography).
fetched_at: 2026-06-16
summary: Respuestas con evidencia citada a las 6 preguntas críticas de la firma XAdES-BES del DE SIFEN — C14N exclusiva, transforms, rsa-sha256, enveloped, signxml xmlns, PKCS#12.
priority: blocker
---

# Research bloqueante — Firma XAdES del DE SIFEN (PR-4)

> **Estado:** RESUELTO. Las 6 preguntas tienen respuesta con evidencia. Una sola
> tiene riesgo residual (Q5, edge de namespace en signxml) que se mitiga con un
> test de round-trip contra el ejemplo oficial.
>
> **NO escribir código de producción con este doc todavía** — es input del plan
> de PR-4. Ver acciones al final.

## Método

Per instrucción: **fuentes locales primero, web solo para los gaps.** El
artefacto local más autoritativo resultó ser el **ejemplo de estructura oficial
DNIT** `docs/original/xsd/Extructura_xml_DE.xml` (línea 177 contiene el bloque
`<Signature>` real completo). Q1–Q4 se resolvieron ahí y se
**corroboraron verbatim** contra dos implementaciones de referencia en
producción. Q5–Q6 (librería) se cerraron con docs de signxml/cryptography.

## Resumen ejecutivo (tabla de decisión)

| #   | Pregunta                      | Respuesta                                                                                                  | Confianza                |
| --- | ----------------------------- | ---------------------------------------------------------------------------------------------------------- | ------------------------ |
| Q1  | ¿Qué C14N?                    | **Exclusiva** — `http://www.w3.org/2001/10/xml-exc-c14n#` (NO inclusiva)                                   | ALTA (3 fuentes)         |
| Q2  | ¿Transforms y orden?          | `[enveloped-signature, xml-exc-c14n#]`; DigestMethod `xmlenc#sha256`                                       | ALTA (3 fuentes)         |
| Q3  | ¿SignatureMethod?             | **rsa-sha256** — `http://www.w3.org/2001/04/xmldsig-more#rsa-sha256` (NO sha1)                             | ALTA (3 fuentes)         |
| Q4  | ¿Posición de Signature?       | **Enveloped** dentro de `<rDE>`, después de `<DE>`; `Reference URI="#<CDC>"` → `Id` del DE                 | ALTA (3 fuentes)         |
| Q5  | ¿signxml preserva xmlns?      | Sí con exc-c14n explícita; **NO usar `InclusiveNamespaces`** (bug verify #145); riesgo real = pretty-print | MEDIA (test obligatorio) |
| Q6  | ¿PKCS#12 unwrap Python 3.11+? | `cryptography...pkcs12.load_key_and_certificates(data, pwd_bytes)` → `(key, cert, extras)`                 | ALTA                     |

> ⚠️ **HALLAZGO CRÍTICO:** `docs/40_PYTHON_LIBRARIES.md` línea 85 documenta la
> C14N **INCORRECTA** — usa
> `c14n_algorithm='http://www.w3.org/TR/2001/REC-xml-c14n-20010315'` que es
> **canonicalización inclusiva**, pero SIFEN exige **exclusiva** (`xml-exc-c14n#`).
> Firmar con inclusiva produce un DigestValue que SIFEN rechaza. Corregir el
> snippet en PR-4 (ver acciones).

---

## Q1 — ¿Qué C14N usa SIFEN? exc-c14n o inclusive?

**Respuesta: canonicalización EXCLUSIVA**, URI `http://www.w3.org/2001/10/xml-exc-c14n#`
(sin comentarios). Aplica tanto al `CanonicalizationMethod` del `SignedInfo`
como al segundo `Transform` de la `Reference`.

**Evidencia:**

1. **Ejemplo oficial DNIT (fuente primaria local)** —
   `docs/original/xsd/Extructura_xml_DE.xml:177`:

   ```
   Algorithm="http://www.w3.org/2001/10/xml-exc-c14n#"
   ```

   (aparece dos veces: como `CanonicalizationMethod` de `SignedInfo` y como
   `Transform` de la `Reference`).

2. **rshk-jsifenlib (Roshka, Java)** — `SignatureHelper.java:69`:

   ```java
   _xmlSignatureFactory.newCanonicalizationMethod(CanonicalizationMethod.EXCLUSIVE, ...)
   ```

   (`javax.xml.crypto.dsig.CanonicalizationMethod.EXCLUSIVE` = `xml-exc-c14n#`).
   Fuente: <https://github.com/roshkadev/rshk-jsifenlib/blob/master/src/main/java/com/roshka/sifen/internal/helpers/SignatureHelper.java>

3. **TIPS-SA `facturacionelectronicapy-xmlsign` (Node, wraps xml-crypto)** —
   `src/XMLDsigNode.ts`:
   ```js
   sig.canonicalizationAlgorithm = "http://www.w3.org/2001/10/xml-exc-c14n#";
   ```
   Fuente: <https://github.com/marcosjara/facturacionelectronicapy-xmlsign/blob/master/src/XMLDsigNode.ts>

**Contradicción detectada:** `docs/40_PYTHON_LIBRARIES.md:85` usa inclusiva →
**bug de doc, corregir.**

---

## Q2 — ¿Qué transformaciones acepta? Orden exacto.

**Respuesta:** dos transforms en la `Reference`, en este orden:

1. `http://www.w3.org/2000/09/xmldsig#enveloped-signature`
2. `http://www.w3.org/2001/10/xml-exc-c14n#` (exclusiva)

`DigestMethod` de la `Reference` = `http://www.w3.org/2001/04/xmlenc#sha256`.

**Evidencia:**

1. **Ejemplo oficial DNIT** — `Extructura_xml_DE.xml:177`, secuencia verbatim de
   URIs en el bloque `<Signature>`:

   ```
   CanonicalizationMethod  → xml-exc-c14n#
   SignatureMethod         → xmldsig-more#rsa-sha256
   Reference URI           → "#01000000019001001100005022020050710000000231"  (= CDC)
   Transform[0]            → xmldsig#enveloped-signature
   Transform[1]            → xml-exc-c14n#
   DigestMethod            → xmlenc#sha256
   ```

2. **rshk-jsifenlib** — `SignatureHelper.java:54-55` (orden exacto):

   ```java
   transforms.add(... newTransform(Transform.ENVELOPED, null));   // 1°
   transforms.add(... newTransform(CanonicalizationMethod.EXCLUSIVE, null)); // 2°
   ```

   y `:64` `newReference("#"+signedNodeId, ... DigestMethod.SHA256 ...)`.

3. **TIPS-SA** — `XMLDsigNode.ts`:
   ```js
   transforms: [
     "http://www.w3.org/2000/09/xmldsig#enveloped-signature",
     "http://www.w3.org/2001/10/xml-exc-c14n#",
   ],
   digestAlgorithm: "http://www.w3.org/2001/04/xmlenc#sha256",
   ```

Las tres fuentes coinciden en orden y URIs.

---

## Q3 — SignatureMethod: rsa-sha256 o rsa-sha1?

**Respuesta: rsa-sha256** — `http://www.w3.org/2001/04/xmldsig-more#rsa-sha256`.
**No** rsa-sha1.

**Evidencia:**

1. **Ejemplo oficial DNIT** — `Extructura_xml_DE.xml:177`:
   ```
   Algorithm="http://www.w3.org/2001/04/xmldsig-more#rsa-sha256"
   ```
2. **rshk-jsifenlib** — `SignatureHelper.java:70`:
   ```java
   _xmlSignatureFactory.newSignatureMethod(Constants.RSA_SHA256, null)
   ```
3. **TIPS-SA** — `XMLDsigNode.ts`:
   ```js
   sig.signatureAlgorithm = "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256";
   ```

(Coherente con el DigestMethod SHA-256 de Q2: SIFEN v150 es full SHA-256.)

---

## Q4 — Posición de Signature: enveloped / enveloping / detached?

**Respuesta: ENVELOPED.** El `<Signature>` (prefijo `ds:`) va **dentro de
`<rDE>`, como hermano del `<DE>`, ubicado después de `</DE>`** (y antes de
`<gCamFuFD>`). La `Reference URI="#<CDC>"` apunta al atributo `Id` del nodo
`<DE>` (cuyo valor es el CDC de 44 dígitos).

**Evidencia:**

1. **Ejemplo oficial DNIT** — `Extructura_xml_DE.xml` líneas 176-178: el orden es
   `</DE>` → `<Signature …>` → `<gCamFuFD>`, con
   `Reference URI="#01000000019001001100005022020050710000000231"` (CDC).
   Confirma firma enveloped que referencia al DE por su `Id`.

2. **rshk-jsifenlib** — `SignatureHelper.java:64` `newReference("#"+signedNodeId, …)`
   y `:144` (lado verify) `valContext.setIdAttributeNS((Element) DENodes.item(0), null, "Id")`
   → la referencia targetea el atributo `Id` del nodo DE.

3. **signxml (cómo se hace enveloped)** — se inserta un placeholder
   `<ds:Signature Id="placeholder"></ds:Signature>` dentro del data en la posición
   deseada antes de firmar. Fuente: <https://xml-security.github.io/signxml/>
   > "To specify the location of an enveloped signature within data, insert a
   > `<ds:Signature Id="placeholder"></ds:Signature>` element in data".

**Implicancia PR-4:** insertar el placeholder `ds:Signature` dentro de `rDE`
después del `DE`, NO al final de `rDE` (respetar el orden del XSD: DE, Signature,
gCamFuFD). El `<Signature>` usa **prefijo `ds:`** (como el ejemplo oficial), no
namespace por defecto.

---

## Q5 — xmlns ordering: ¿signxml preserva correctamente?

**Respuesta: Sí, con exc-c14n configurada explícitamente**, PERO con dos
precauciones que son la causa real de los digest-mismatch en la práctica.

**Cómo seleccionar exc-c14n en signxml (API actual ≥3.2):**

- `XMLSigner(c14n_algorithm=CanonicalizationMethod.EXCLUSIVE_XML_CANONICALIZATION_1_0)`
  cuyo string es exactamente `http://www.w3.org/2001/10/xml-exc-c14n#`.
- El **default de signxml NO es exclusiva** (`CANONICAL_XML_1_1`) → hay que
  setearlo sí o sí.
- La C14N del `Transform` de la `Reference` se puede setear aparte con
  `SignatureReference.c14n_method`; **verificar en el XML emitido que exc-c14n
  aparezca en AMBOS** (SignedInfo y el 2° Transform).
- Fuente: <https://xml-security.github.io/signxml/>
  > "**c14n_algorithm** … Algorithm that will be used to canonicalize … the XML
  > that is signed." / "`EXCLUSIVE_XML_CANONICALIZATION_1_0` =
  > `'http://www.w3.org/2001/10/xml-exc-c14n#'`".

**Precaución 1 — NO usar `InclusiveNamespaces` PrefixList.** El `<DE>` SIFEN usa
un único namespace por defecto (sin prefijo); no necesita PrefixList. Agregarlo
dispara el bug de verificación de signxml (issue #145, cerrado): el verificador
de signxml no busca los inclusive-prefixes y produce mismatch.
Fuente: <https://github.com/XML-Security/signxml/issues/145>

**Precaución 2 (la causa #1 real) — serializar SIN pretty-print/reformateo**
entre firmar y transportar. Coincide con el gotcha ya anotado en
`docs/40_PYTHON_LIBRARIES.md:100-101` ("diff de canonicalization suele ser la
causa") y con el requisito SIFEN de XML sin whitespace entre tags
(`docs/40:58`, `etree.tostring(..., pretty_print=False)`).

**Riesgo residual / confianza MEDIA:** no se encontró un bug confirmado de
signxml que mis-canonicalice un namespace-por-defecto sin prefijo en el lado de
_firma_ (lxml exclusiva emite la declaración del default-ns en el ápex según el
spec exc-c14n). PERO esto **debe probarse con un test de round-trip**: firmar el
`<DE>` de ejemplo y verificar el `DigestValue`/`SignatureValue` contra el bloque
`<Signature>` del archivo oficial `Extructura_xml_DE.xml`. Si no matchea →
considerar `cryptography` + `xmlsec` (más bajo nivel) como fallback (ya listado
como alternativa en `docs/40:67`).

---

## Q6 — PKCS#12 unwrap en Python 3.11+: API recomendada

**Respuesta:** `cryptography` (no stdlib). Recomendado:

```python
from cryptography.hazmat.primitives.serialization.pkcs12 import load_key_and_certificates
key, cert, additional = load_key_and_certificates(p12_bytes, password.encode())
# key  -> private key (o None)
# cert -> x509.Certificate CRUDO (sin .certificate extra)
# password DEBE ser bytes o None
```

**Por qué `load_key_and_certificates` y no `load_pkcs12`:** ambas vigentes y NO
deprecadas (mismo import path `…serialization.pkcs12`), pero:

- `load_key_and_certificates(data, pwd)` → tupla `(key, cert, additional_certs)`
  con el `x509.Certificate` **directo** (más ergonómico para el flujo de firma).
- `load_pkcs12(data, pwd)` → objeto `PKCS12KeyAndCertificates`; el cert viene
  envuelto y se accede vía `.cert.certificate` (hop extra). Útil solo si se
  necesitan friendly-names.
- Fuente: <https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/>
  > load_key_and_certificates: "A tuple of three elements:
  > `(private_key, certificate, additional_certificates)`".

**Nota local:** `docs/40:74,162` ya importa de `…serialization.pkcs12` (usa
`load_pkcs12` con `.cert.certificate`). Para el **transporte mTLS** (PR-5, ya
mergeado) se usa `requests-pkcs12` directo; para la **firma** (PR-4) hace falta
el `key` + `cert` crudos → `load_key_and_certificates` es el camino correcto.
Gotcha confirmado (`docs/40:189`): password incorrecta lanza error críptico →
envolver en try/except con mensaje user-friendly.

---

## Acciones para el plan de PR-4 (derivadas del research)

1. **Configurar exc-c14n explícita** en `XMLSigner`
   (`EXCLUSIVE_XML_CANONICALIZATION_1_0`) y verificar que aparezca en SignedInfo
   **y** en el 2° Transform de la Reference.
2. `signature_algorithm="rsa-sha256"`, `digest_algorithm="sha256"`.
3. **Insertar placeholder `ds:Signature`** dentro de `rDE` después del `DE`
   (orden XSD: DE → Signature → gCamFuFD); prefijo `ds:`.
4. **NO agregar `InclusiveNamespaces` PrefixList.**
5. **Serializar sin pretty-print** entre firma y transporte.
6. **Cargar CCFE** con `pkcs12.load_key_and_certificates(p12_bytes, pwd.encode())`.
7. **Test de regresión obligatorio (Nyquist de PR-4):** round-trip firmar el DE
   y matchear `DigestValue`/`SignatureValue` contra el bloque `<Signature>` del
   `docs/original/xsd/Extructura_xml_DE.xml` (o un DE de prueba aprobado por
   SIFEN). Es la única forma de cerrar el riesgo MEDIA de Q5.
8. **Corregir `docs/40_PYTHON_LIBRARIES.md:85`**: cambiar el `c14n_algorithm`
   inclusivo por exc-c14n (doc bug; hacerlo en el PR-4, no es código de prod).
9. **Pendiente fuera de scope:** citar el Manual Técnico SIFEN v150 (texto
   verbatim de canonicalización) — NO se obtuvo en este research; el ejemplo
   oficial + las dos implementaciones de referencia ya corroboran la decisión,
   pero si OCA/PR pide la cita del manual, bajar el PDF v150 del portal ekuatia.

## Fuentes consultadas

**Locales:**

- `docs/original/xsd/Extructura_xml_DE.xml:176-178` — ejemplo oficial DNIT del DE firmado (fuente primaria).
- `docs/40_PYTHON_LIBRARIES.md` — snippets signxml/cryptography (con el bug de C14N a corregir).

**Web (corroboración y librerías):**

- signxml — <https://xml-security.github.io/signxml/> · issue #145 <https://github.com/XML-Security/signxml/issues/145>
- cryptography — <https://cryptography.io/en/latest/hazmat/primitives/asymmetric/serialization/>
- rshk-jsifenlib (Java, Roshka) — `SignatureHelper.java` <https://github.com/roshkadev/rshk-jsifenlib>
- TIPS-SA `facturacionelectronicapy-xmlsign` (Node) — `XMLDsigNode.ts` <https://github.com/marcosjara/facturacionelectronicapy-xmlsign>

Ver [[fase2-edi-pr3-pr5]] (XML builder + SOAP ya en main) y [[fase2-edi-pr2-cdc]].
