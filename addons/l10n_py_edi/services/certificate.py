# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Carga y validación del certificado CCFE (PKCS#12).

Helper Python puro (sin dependencias Odoo). Expone cert + private key para la
firma XAdES (PR-4) y para el canal mTLS con SIFEN (PR-5).

El RUC del titular se extrae del atributo ``serialNumber`` del subject
(formato PSC paraguayo: ``RUC80012345-7`` — campos F110/F211 del Manual
Técnico SIFEN).
"""
import datetime
import re
from dataclasses import dataclass

from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

RUC_IN_SUBJECT = re.compile(r"RUC\s*([0-9]{1,8}-?[0-9])", re.IGNORECASE)


class CertificateError(Exception):
    """Error genérico de certificado CCFE."""


class CertificateLoadError(CertificateError):
    """El .p12 no se pudo abrir (corrupto o password incorrecta)."""


class CertificateExpiredError(CertificateError):
    """El certificado está vencido."""


class CertificateNotYetValidError(CertificateError):
    """El certificado aún no entró en vigencia."""


@dataclass
class CertificateInfo:
    """Certificado CCFE cargado y listo para firmar."""

    certificate: x509.Certificate
    private_key: object
    not_valid_before: datetime.datetime
    not_valid_after: datetime.datetime
    ruc: str  # None si el subject no trae serialNumber RUC


def load_pkcs12(p12_bytes, password):
    """Abre un PKCS#12 y devuelve :class:`CertificateInfo`.

    :param p12_bytes: contenido binario del archivo .p12.
    :param password: password del archivo (str).
    :raises CertificateLoadError: archivo corrupto o password incorrecta.
    """
    try:
        key, cert, _additional = pkcs12.load_key_and_certificates(
            p12_bytes, password.encode() if password else None
        )
    except (ValueError, TypeError) as exc:
        raise CertificateLoadError(
            "No se pudo abrir el .p12: archivo inválido o password incorrecta"
        ) from exc
    if cert is None or key is None:
        raise CertificateLoadError("El .p12 no contiene certificado y clave")
    return CertificateInfo(
        certificate=cert,
        private_key=key,
        not_valid_before=cert.not_valid_before_utc,
        not_valid_after=cert.not_valid_after_utc,
        ruc=extract_ruc(cert),
    )


def extract_ruc(cert):
    """Extrae el RUC del atributo serialNumber del subject, o None."""
    attrs = cert.subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
    for attr in attrs:
        match = RUC_IN_SUBJECT.search(attr.value)
        if match:
            return match.group(1)
    return None


def check_validity(info, at=None):
    """Valida vigencia del certificado a la fecha ``at`` (default: ahora UTC).

    :raises CertificateExpiredError: vencido.
    :raises CertificateNotYetValidError: aún no vigente.
    """
    at = at or datetime.datetime.now(datetime.timezone.utc)
    if at > info.not_valid_after:
        raise CertificateExpiredError(
            "Certificado CCFE vencido el %s" % info.not_valid_after.date()
        )
    if at < info.not_valid_before:
        raise CertificateNotYetValidError(
            "Certificado CCFE vigente recién desde %s" % info.not_valid_before.date()
        )


def is_valid(info, at=None):
    """True si el certificado está vigente a la fecha ``at``."""
    try:
        check_validity(info, at=at)
    except CertificateError:
        return False
    return True
