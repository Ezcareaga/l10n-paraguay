# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Validación de elementos lxml contra el XSD oficial SIFEN v150.

Importable sin registry: este módulo NO importa de ``odoo``.
"""
from __future__ import annotations

import os
from pathlib import Path

from lxml import etree

# Ruta canónica a los XSD oficiales (en el repo, bajo docs/original/xsd/).
# En producción se puede apuntar a una copia bundleada en el módulo; por ahora
# el path se resuelve relativo a este mismo archivo para tests de integración.
_XSD_DIR = Path(__file__).resolve().parents[4] / "docs" / "original" / "xsd"


class XsdValidationError(ValueError):
    """El XML no cumple el esquema XSD de SIFEN.

    :attr errors: lista de strings con los mensajes de error del schema validator.
    """

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("\n".join(errors))


def _xsd_dir() -> Path:
    """Retorna el directorio de XSDs, respetando la variable de entorno
    ``SIFEN_XSD_DIR`` si está seteada (útil en CI o deployment)."""
    env_dir = os.environ.get("SIFEN_XSD_DIR")
    if env_dir:
        return Path(env_dir)
    return _XSD_DIR


def load_schema(xsd_filename: str = "DE_v150.xsd") -> etree.XMLSchema:
    """Carga y compila el esquema XSD indicado desde el directorio canónico.

    :param xsd_filename: nombre del archivo XSD dentro del directorio de XSDs.
    :returns: :class:`lxml.etree.XMLSchema` compilado.
    :raises FileNotFoundError: si el archivo no existe.
    :raises etree.XMLSchemaParseError: si el XSD tiene errores de sintaxis.
    """
    xsd_path = _xsd_dir() / xsd_filename
    if not xsd_path.exists():
        raise FileNotFoundError(
            "XSD no encontrado: %s (SIFEN_XSD_DIR=%s)" % (xsd_path, _xsd_dir())
        )
    doc = etree.parse(str(xsd_path))
    return etree.XMLSchema(doc)


def validate_against_xsd(
    element: etree._Element,
    xsd_filename: str = "DE_v150.xsd",
) -> None:
    """Valida ``element`` contra el XSD SIFEN indicado.

    :param element: elemento lxml a validar (p. ej. el ``<rDE>`` completo o
        el ``<DE>`` si se valida antes de firmar).
    :param xsd_filename: nombre del archivo XSD (default ``DE_v150.xsd``).
    :raises XsdValidationError: si la validación falla; ``exc.errors`` contiene
        la lista de mensajes del schema validator lxml.
    """
    schema = load_schema(xsd_filename)
    if not schema.validate(element):
        errors = [str(e) for e in schema.error_log]
        raise XsdValidationError(errors)
