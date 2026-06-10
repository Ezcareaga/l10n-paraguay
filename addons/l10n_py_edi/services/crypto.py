# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Cifrado Fernet para secretos EDI (CCFE .p12, password, CSC).

Implementación del blueprint docs/60_SECURITY_BASELINE.md §5: los secretos se
almacenan en PostgreSQL solo como tokens Fernet; la data key vive FUERA de la
base de datos (env var o archivo — ver ``res.company._l10n_py_edi_get_fernet_key``).

Helper Python puro: no importa nada de ``odoo``.
"""
from cryptography.fernet import Fernet, InvalidToken, MultiFernet


class DecryptionError(Exception):
    """Token inválido o key incorrecta."""


def generate_data_key():
    """Genera una data key Fernet nueva (32 bytes URL-safe base64)."""
    return Fernet.generate_key()


def encrypt_secret(data, key):
    """Cifra ``data`` (bytes) con ``key``. Devuelve token Fernet (bytes)."""
    return Fernet(key).encrypt(data)


def decrypt_secret(token, key):
    """Descifra un token Fernet. Lanza :class:`DecryptionError` si no valida."""
    try:
        return Fernet(key).decrypt(token)
    except InvalidToken as exc:
        raise DecryptionError("Token Fernet inválido o key incorrecta") from exc


def rotate_secret(token, old_key, new_key):
    """Re-cifra ``token`` con ``new_key`` preservando el timestamp original.

    Patrón ``MultiFernet.rotate()`` del blueprint docs/60 para la rotación
    trimestral de data keys.
    """
    try:
        return MultiFernet([Fernet(new_key), Fernet(old_key)]).rotate(token)
    except InvalidToken as exc:
        raise DecryptionError("Token Fernet inválido o key incorrecta") from exc
