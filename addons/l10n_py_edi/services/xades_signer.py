# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Firma XAdES-BES enveloped del DE SIFEN (PR-4a) — Manual Técnico v150.

Función pura (sin dependencias Odoo): recibe el ``<rDE>`` serializado con el
``<DE Id="{CDC}">`` adentro y el CCFE (PKCS#12), y devuelve el XML con el bloque
``<Signature>`` insertado como hermano del ``<DE>`` (después de él), según
docs/research/xades_sifen.md.

Decisiones de firma (research Q1-Q6, validadas por spike contra el ejemplo
oficial DNIT):
- CanonicalizationMethod / 2º Transform: exc-c14n (``xml-exc-c14n#``).
- SignatureMethod: rsa-sha256.  DigestMethod: sha256.
- Transforms de la Reference: [enveloped-signature, exc-c14n].
- Posición: ``<Signature>`` enveloped dentro de ``<rDE>``, tras ``<DE>`` y antes
  de ``<gCamFuFD>`` — se logra insertando un placeholder ``<ds:Signature>`` que
  signxml rellena in situ (no append al final).
- NO se agrega ``InclusiveNamespaces`` PrefixList (bug signxml #145).
- Serialización sin pretty-print.

El CCFE se carga con ``certificate.load_pkcs12`` (reúso) que usa
``pkcs12.load_key_and_certificates`` (research Q6).
"""
from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from lxml import etree
from signxml import XMLSigner, methods
from signxml.algorithms import CanonicalizationMethod, DigestAlgorithm, SignatureMethod

from . import certificate

SIFEN_NS = "http://ekuatia.set.gov.py/sifen/xsd"
DS_NS = "http://www.w3.org/2000/09/xmldsig#"
_EXC_C14N = CanonicalizationMethod.EXCLUSIVE_XML_CANONICALIZATION_1_0
_PLACEHOLDER_ID = "placeholder"


class SignatureError(Exception):
    """No se pudo firmar el DE (XML inválido, sin CDC, o fallo de signxml)."""


def sign_de(xml_bytes: bytes, p12_bytes: bytes, password: str) -> bytes:
    """Firma el ``<rDE>``/``<DE>`` y devuelve el XML firmado (bytes UTF-8).

    :param xml_bytes: ``<rDE>`` serializado (bytes) conteniendo
        ``<DE Id="{CDC}">``. El ``<gCamFuFD>`` (QR) se agrega DESPUÉS de firmar
        (PR-4b) porque contiene el DigestValue; si ya estuviera presente, la
        firma se inserta igualmente entre el ``<DE>`` y el ``<gCamFuFD>``.
    :param p12_bytes: contenido binario del CCFE (.p12).
    :param password: password del .p12.
    :returns: bytes UTF-8 del ``<rDE>`` firmado (sin pretty-print).
    :raises SignatureError: XML sin ``<DE Id>`` o fallo al firmar.
    :raises certificate.CertificateError: .p12 inválido o password incorrecta.
    """
    info = certificate.load_pkcs12(p12_bytes, password)

    # Parser endurecido: sin resolución de entidades, DTD ni red (anti-XXE,
    # billion-laughs, SSRF-vía-entidad) y sin árbol gigante. El input es la
    # salida de nuestro propio builder, pero se trata como trust boundary.
    parser = etree.XMLParser(
        resolve_entities=False, no_network=True, load_dtd=False, huge_tree=False
    )
    try:
        root = etree.fromstring(xml_bytes, parser=parser)
    except etree.XMLSyntaxError as exc:
        # No interpolar el texto de la excepción: puede arrastrar fragmentos del
        # XML (RUC, nombres, montos). El detalle queda en la traza (from exc).
        raise SignatureError("XML del DE mal formado") from exc
    # Un DE legítimo nunca trae DOCTYPE; rechazarlo elimina toda ambigüedad.
    if root.getroottree().docinfo.doctype:
        raise SignatureError("DOCTYPE no permitido en el DE")

    de = root.find("{%s}DE" % SIFEN_NS)
    if de is None:
        raise SignatureError("El XML no contiene un elemento <DE>")
    cdc = de.get("Id")
    if not cdc:
        raise SignatureError("El <DE> no tiene atributo Id (CDC)")
    # El Id del DE debe ser único en el documento: si otro elemento comparte el
    # mismo Id, el deref "#CDC" se vuelve ambiguo (XML Signature Wrapping).
    if len(root.xpath("//*[@Id=$value]", value=cdc)) != 1:
        raise SignatureError("El Id (CDC) no es único en el documento")

    # Placeholder ds:Signature inmediatamente después del <DE> para fijar la
    # posición (research #3); signxml lo rellena in situ con method=enveloped.
    placeholder = etree.Element("{%s}Signature" % DS_NS, nsmap={"ds": DS_NS})
    placeholder.set("Id", _PLACEHOLDER_ID)
    root.insert(list(root).index(de) + 1, placeholder)

    signer = XMLSigner(
        method=methods.enveloped,
        signature_algorithm=SignatureMethod.RSA_SHA256,
        digest_algorithm=DigestAlgorithm.SHA256,
        c14n_algorithm=_EXC_C14N,
    )
    cert_pem = info.certificate.public_bytes(serialization.Encoding.PEM)
    try:
        signed_root = signer.sign(
            root,
            key=info.private_key,
            cert=cert_pem,
            reference_uri="#" + cdc,
        )
    except SignatureError:
        raise
    except Exception as exc:  # signxml lanza varias excepciones internas
        # Mensaje estático: el texto de signxml/cryptography podría arrastrar
        # material de clave o XML/PII a logs/UI. El detalle va en la traza.
        raise SignatureError("No se pudo firmar el DE") from exc

    return etree.tostring(signed_root, encoding="UTF-8", xml_declaration=True)
