# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la firma XAdES-BES del DE SIFEN (PR-4a).

BaseCase (sin DB) — el signer es Python puro. El CCFE se genera en runtime
(tests/fixtures.py); nunca hay un .p12 real en el repo.

El ejemplo oficial DNIT (docs/original/xsd/Extructura_xml_DE.xml) se usa SOLO
para validar estructura/orden/URIs del bloque <Signature> — NO para comparar
DigestValue/SignatureValue byte-a-byte: el archivo es ilustrativo (cert
redactado, valores criptográficos no reproducibles). Ver
docs/research/xades_sifen.md §"Hallazgo de spike".
"""
from __future__ import annotations

import base64
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from lxml import etree
from signxml import XMLVerifier
from signxml.exceptions import InvalidSignature

from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_edi.services import certificate, xades_signer
from odoo.addons.l10n_py_edi.tests import fixtures

_SIFEN_NS = "http://ekuatia.set.gov.py/sifen/xsd"
_DS = "http://www.w3.org/2000/09/xmldsig#"
_CDC = "01000000019001001100005022020050710000000231"
_PWD = "test-password"
# Ejemplo oficial DNIT resuelto desde la raíz del repo: el test está en
# <repo>/addons/l10n_py_edi/tests/ → parents[3] == <repo>. El _xsd_dir() de
# xsd_validator ya usa parents[3] (corregido en este PR; antes parents[4]
# sobrepasaba la raíz — ver TD-011).
_OFFICIAL_DE = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "original"
    / "xsd"
    / "Extructura_xml_DE.xml"
)


def _q(local, ns=_DS):
    return "{%s}%s" % (ns, local)


@tagged("standard", "l10n_py")
class TestXadesSigner(BaseCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.p12 = fixtures.make_test_p12(password=_PWD)
        info = certificate.load_pkcs12(cls.p12, _PWD)
        cls.cert_pem = info.certificate.public_bytes(serialization.Encoding.PEM)

    def _official_rde_bytes(self, keep_gcamfufd=True):
        """``<rDE>`` oficial con [dVerFor, DE(, gCamFuFD)] — sin ``<Signature>``."""
        parser = etree.XMLParser(remove_blank_text=True)
        rde = etree.parse(str(_OFFICIAL_DE), parser).getroot()
        for el in rde.findall(_q("Signature")):
            rde.remove(el)
        if not keep_gcamfufd:
            for el in rde.findall(_q("gCamFuFD", _SIFEN_NS)):
                rde.remove(el)
        return etree.tostring(rde, encoding="UTF-8", xml_declaration=True)

    def _sign_official(self, keep_gcamfufd=True):
        signed = xades_signer.sign_de(
            self._official_rde_bytes(keep_gcamfufd), self.p12, _PWD
        )
        return signed, etree.fromstring(signed)

    def test_signed_de_uses_official_algorithm_uris(self):
        """URIs de algoritmos/transforms verbatim contra el bloque oficial SIFEN."""
        _, root = self._sign_official()
        self.assertEqual(
            root.find(".//" + _q("CanonicalizationMethod")).get("Algorithm"),
            "http://www.w3.org/2001/10/xml-exc-c14n#",
        )
        self.assertEqual(
            root.find(".//" + _q("SignatureMethod")).get("Algorithm"),
            "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        )
        self.assertEqual(
            root.find(".//" + _q("DigestMethod")).get("Algorithm"),
            "http://www.w3.org/2001/04/xmlenc#sha256",
        )
        transforms = [t.get("Algorithm") for t in root.findall(".//" + _q("Transform"))]
        self.assertEqual(
            transforms,
            [
                "http://www.w3.org/2000/09/xmldsig#enveloped-signature",
                "http://www.w3.org/2001/10/xml-exc-c14n#",
            ],
        )

    def test_signature_positioned_after_de_before_gcamfufd(self):
        """``<Signature>`` queda tras ``<DE>`` y antes de ``<gCamFuFD>``; URI=#CDC."""
        _, root = self._sign_official(keep_gcamfufd=True)
        order = [etree.QName(c).localname for c in root]
        self.assertEqual(order, ["dVerFor", "DE", "Signature", "gCamFuFD"])
        self.assertEqual(root.find(".//" + _q("Reference")).get("URI"), "#" + _CDC)

    def test_digest_value_derived_from_exclusive_c14n(self):
        """DigestValue == base64(sha256(exc_c14n(DE))) — prueba exclusiva, no inclusiva."""
        _, root = self._sign_official()
        de = root.find(_q("DE", _SIFEN_NS))
        emitted = root.find(".//" + _q("DigestValue")).text
        excl = base64.b64encode(
            hashlib.sha256(etree.tostring(de, method="c14n", exclusive=True)).digest()
        ).decode()
        incl = base64.b64encode(
            hashlib.sha256(etree.tostring(de, method="c14n", exclusive=False)).digest()
        ).decode()
        self.assertEqual(emitted, excl)
        # Discrimina el bug docs/40: con c14n inclusiva el digest NO coincide.
        self.assertNotEqual(emitted, incl)

    def test_signed_de_verifies_with_certificate(self):
        """La firma valida end-to-end contra nuestro cert de test."""
        signed, _ = self._sign_official()
        XMLVerifier().verify(signed, x509_cert=self.cert_pem, expect_references=1)

    def test_tampered_de_fails_verification(self):
        """Modificar el DE tras firmar invalida la firma (tamper detection)."""
        signed, root = self._sign_official()
        dv = root.find(_q("DE", _SIFEN_NS) + "/" + _q("dDVId", _SIFEN_NS))
        dv.text = "9" if dv.text != "9" else "8"
        tampered = etree.tostring(root, encoding="UTF-8", xml_declaration=True)
        with self.assertRaises(InvalidSignature):
            XMLVerifier().verify(tampered, x509_cert=self.cert_pem, expect_references=1)

    def test_wrong_password_raises(self):
        with self.assertRaises(certificate.CertificateError):
            xades_signer.sign_de(self._official_rde_bytes(), self.p12, "wrong-pwd")

    def test_missing_de_raises(self):
        no_de = (
            '<?xml version="1.0"?><rDE xmlns="%s"><dVerFor>150</dVerFor></rDE>'
            % _SIFEN_NS
        ).encode()
        with self.assertRaises(xades_signer.SignatureError):
            xades_signer.sign_de(no_de, self.p12, _PWD)

    def test_duplicate_id_raises(self):
        """Id repetido en el documento (XML Signature Wrapping) → rechazado."""
        rde = etree.fromstring(self._official_rde_bytes())
        rde.find(_q("dVerFor", _SIFEN_NS)).set("Id", _CDC)
        dup = etree.tostring(rde, encoding="UTF-8", xml_declaration=True)
        with self.assertRaises(xades_signer.SignatureError):
            xades_signer.sign_de(dup, self.p12, _PWD)

    def test_doctype_rejected(self):
        """Un DE con DOCTYPE (defensa anti-XXE) → rechazado."""
        doctype = self._official_rde_bytes().replace(b"?>", b"?><!DOCTYPE rDE>", 1)
        with self.assertRaises(xades_signer.SignatureError):
            xades_signer.sign_de(doctype, self.p12, _PWD)
