# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Validación de elementos lxml contra los XSD oficiales SIFEN v150.

Enfoque wrapper-schema
----------------------
Los XSD de SIFEN declaran **tipos** (``tDE``, ``tiAfecIVA``, …) pero no
elementos globales, por lo que ``lxml.etree.XMLSchema.validate(<DE>)``
directo falla con "No matching global declaration available for the
validation root".

La solución es construir un mini-schema wrapper en memoria que:

1. Declara el namespace SIFEN como ``targetNamespace``.
2. Hace ``<xs:include>`` del XSD de tipos oficial (usando path absoluto).
3. Declara el elemento global raíz con el tipo correcto del XSD incluido.

lxml puede entonces anclar la validación al elemento real y validar el
subárbol completo.  El schema compilado se cachea por tipo de documento para
no recompilarlo en cada llamada.

Referencia: ``docs/research/xades_sifen.md`` §"Hallazgo de spike".

Importable sin registry: este módulo NO importa de ``odoo``.
"""
from __future__ import annotations

import os
from pathlib import Path

from lxml import etree

# Ruta canónica a los XSD oficiales (en el repo, bajo docs/original/xsd/).
# Se resuelve relativo a este archivo: services/ -> l10n_py_edi/ -> addons/ ->
# parents[3] == raíz del repo. (Antes parents[4], que sobrepasaba la raíz en CI
# y hacía que la validación XSD se saltara silenciosamente — ver TD-011.)
_XSD_DIR = Path(__file__).resolve().parents[3] / "docs" / "original" / "xsd"

# Namespace SIFEN — debe coincidir con targetNamespace de los XSD oficiales.
_SIFEN_NS = "http://ekuatia.set.gov.py/sifen/xsd"

# Cache de schemas compilados: (xsd_filename, root_type) → XMLSchema
_SCHEMA_CACHE: dict[tuple[str, str], etree.XMLSchema] = {}


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


def _build_wrapper_schema(
    xsd_filename: str, root_element: str, root_type: str
) -> etree.XMLSchema:
    """Construye y compila un schema wrapper que ancla la validación del DE.

    El wrapper declara un elemento global del tipo correcto e incluye el XSD
    de tipos oficial, permitiendo que lxml valide el elemento raíz del DE.

    :param xsd_filename: nombre del archivo XSD a incluir (p. ej. ``DE_v150.xsd``).
    :param root_element: nombre del elemento global a declarar (p. ej. ``DE``).
    :param root_type: tipo del elemento en el namespace SIFEN (p. ej. ``tDE``).
    :returns: :class:`lxml.etree.XMLSchema` compilado.
    :raises FileNotFoundError: si el XSD no existe en el directorio canónico.
    :raises etree.XMLSchemaParseError: si el XSD tiene errores de sintaxis.
    """
    xsd_path = _xsd_dir() / xsd_filename
    if not xsd_path.exists():
        raise FileNotFoundError("XSD no encontrado: %s" % xsd_filename)
    # Usar URI de archivo con barras hacia adelante para compatibilidad lxml
    xsd_uri = xsd_path.as_uri()

    wrapper_src = (
        '<?xml version="1.0" encoding="utf-8"?>'
        "<xs:schema"
        ' xmlns:xs="http://www.w3.org/2001/XMLSchema"'
        ' xmlns:sifen="{ns}"'
        ' targetNamespace="{ns}"'
        ' elementFormDefault="qualified">'
        '  <xs:include schemaLocation="{path}"/>'
        '  <xs:element name="{elem}" type="sifen:{typ}"/>'
        "</xs:schema>"
    ).format(ns=_SIFEN_NS, path=xsd_uri, elem=root_element, typ=root_type)

    wrapper_doc = etree.fromstring(wrapper_src.encode("utf-8"))
    return etree.XMLSchema(wrapper_doc)


def _get_schema(
    xsd_filename: str, root_element: str, root_type: str
) -> etree.XMLSchema:
    """Retorna el schema compilado desde caché o lo construye la primera vez."""
    key = (xsd_filename, root_type)
    if key not in _SCHEMA_CACHE:
        _SCHEMA_CACHE[key] = _build_wrapper_schema(
            xsd_filename, root_element, root_type
        )
    return _SCHEMA_CACHE[key]


def validate_de(xml_bytes: bytes) -> None:
    """Valida el bytes del elemento ``<DE>`` contra el XSD SIFEN DE_v150.xsd.

    Usa el enfoque wrapper-schema para anclar la validación al tipo ``tDE``
    del XSD oficial, que declara tipos pero no elementos globales.

    :param xml_bytes: bytes XML del elemento ``<DE>`` a validar.
    :raises XsdValidationError: si la validación falla; ``exc.errors`` contiene
        la lista de mensajes del schema validator lxml.
    :raises FileNotFoundError: si el XSD no está disponible.
    """
    schema = _get_schema("DE_v150.xsd", "DE", "tDE")
    de_element = etree.fromstring(xml_bytes)
    if not schema.validate(de_element):
        errors = [
            # Omitir paths del filesystem de los mensajes de error
            str(e).split("}")[-1] if "}" in str(e) else str(e)
            for e in schema.error_log
        ]
        raise XsdValidationError(errors)


def validate_evento(xml_bytes: bytes) -> None:
    """Valida el bytes de un evento SIFEN contra el XSD de eventos.

    :param xml_bytes: bytes XML del elemento de evento a validar.
    :raises XsdValidationError: si la validación falla.
    :raises FileNotFoundError: si el XSD no está disponible.

    .. note::
        El XSD de eventos aún no está disponible en el repo; esta función
        es un placeholder para cuando se agregue (PR-7 eventos).
    """
    raise NotImplementedError(
        "validate_evento: XSD de eventos SIFEN aún no integrado (PR-7)"
    )


def validate_against_xsd(
    element: etree._Element,
    xsd_filename: str = "DE_v150.xsd",
) -> None:
    """Valida ``element`` contra el XSD SIFEN indicado.

    Wrapper de compatibilidad hacia atrás — delega a :func:`validate_de`
    para el caso ``DE_v150.xsd``.

    :param element: elemento lxml a validar (el ``<DE>`` generado por el builder).
    :param xsd_filename: nombre del archivo XSD (default ``DE_v150.xsd``).
    :raises XsdValidationError: si la validación falla.
    :raises NotImplementedError: si se pasa un XSD distinto a ``DE_v150.xsd``
        que aún no tiene wrapper-schema configurado.
    """
    if xsd_filename == "DE_v150.xsd":
        validate_de(etree.tostring(element, encoding="unicode").encode("utf-8"))
    else:
        raise NotImplementedError(
            "validate_against_xsd: solo DE_v150.xsd está soportado vía wrapper-schema. "
            "Para otros XSD, usar _build_wrapper_schema() directamente."
        )
