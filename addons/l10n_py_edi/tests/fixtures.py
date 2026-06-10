# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Generación runtime de certificados PKCS#12 self-signed para tests.

NUNCA commitear un .p12 real al repo — los fixtures se generan acá.
"""
import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

DEFAULT_RUC = "80069563-1"


def make_test_p12(
    ruc=DEFAULT_RUC,
    password="test-password",
    not_before=None,
    not_after=None,
    serial_number_attr=True,
):
    """Genera un .p12 self-signed estilo CCFE paraguayo.

    :param ruc: RUC que se embebe como atributo serialNumber del subject
        con el prefijo ``RUC`` (formato usado por los PSC paraguayos).
    :param serial_number_attr: si es False, omite el atributo (para testear
        extracción fallida de RUC).
    :return: bytes del archivo PKCS#12.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    not_before = not_before or (now - datetime.timedelta(days=1))
    not_after = not_after or (now + datetime.timedelta(days=365))

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    attrs = [
        x509.NameAttribute(NameOID.COUNTRY_NAME, "PY"),
        x509.NameAttribute(NameOID.COMMON_NAME, "TEST CCFE l10n_py_edi"),
    ]
    if serial_number_attr:
        attrs.append(x509.NameAttribute(NameOID.SERIAL_NUMBER, "RUC" + ruc))
    subject = issuer = x509.Name(attrs)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .sign(key, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"test-ccfe",
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(password.encode()),
    )


def make_expired_p12(password="test-password"):
    """p12 cuyo certificado venció hace 30 días."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return make_test_p12(
        password=password,
        not_before=now - datetime.timedelta(days=395),
        not_after=now - datetime.timedelta(days=30),
    )
