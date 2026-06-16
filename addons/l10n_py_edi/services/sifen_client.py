# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Cliente SOAP para los Web Services SIFEN — Manual Técnico v150 §6.

Helper Python puro (sin dependencias Odoo). El cliente usa ``zeep`` con
``requests_pkcs12`` para autenticación mTLS requerida por el CCFE paraguayo.

Operaciones implementadas:
    - ``send_de``: ``siRecepDE`` — envío síncrono de un DE firmado.
    - ``send_lote``: ``siRecepLoteDE`` — lote asíncrono de hasta 50 DE.
    - ``query_lote``: ``siResultLoteDE`` — consulta resultado de lote.
    - ``query_de``: ``siConsDE`` — consulta DE individual por CDC.

Jerarquía de excepciones::

    SifenError
    ├── SifenConnectionError   (red / TLS / timeout)
    └── SifenSOAPError         (SOAP fault del servidor)

Respuestas exitosas se parsean a :class:`SifenResponse`.

TODO (abierto, ver issue #38):
    - Versionar WSDLs reales de sifen-test en ``wsdl/`` una vez obtenidos
      del servidor (actualmente el cliente depende del WSDL en runtime).
    - Confirmar si ``siRecepDE`` espera el XML firmado como string o como
      nodo embebido dentro del envelope SOAP (puede variar entre operaciones).
    - Integración con ``account_edi`` framework (es el scope de PR-6).
"""
import base64
import gzip
import socket
from dataclasses import dataclass, field
from typing import Any

import requests
import zeep
import zeep.exceptions
from requests_pkcs12 import Pkcs12Adapter

from .sifen_endpoints import ENVIRONMENT_TEST, get_wsdl_url

# ── Constantes de respuesta ───────────────────────────────────────────────────

# DE aprobado por SIFEN
CODE_DE_APROBADO = "0260"

# DE aprobado con observación (también considerado aprobado)
CODE_DE_APROBADO_CON_OBS = "0261"

# Número de lote no existe en SIFEN
CODE_LOTE_INEXISTENTE = "0360"

# Lote todavía en procesamiento — reintentar después de 10 minutos
CODE_LOTE_EN_PROCESO = "0361"

# Procesamiento del lote concluido
CODE_LOTE_CONCLUIDO = "0362"

# Consulta de lote extemporánea (superó las 48 horas)
CODE_LOTE_EXTEMPORANEO = "0364"

# Códigos 03xx de rechazo (prefijo)
_REJECTION_PREFIX = "03"

# Máximo de DE por lote (Manual SIFEN §6)
MAX_DE_POR_LOTE = 50

# Timeout por defecto (segundos)
DEFAULT_CONNECT_TIMEOUT = 10
DEFAULT_READ_TIMEOUT = 60


# ── Excepciones ───────────────────────────────────────────────────────────────


class SifenError(Exception):
    """Excepción base del cliente SIFEN."""


class SifenConnectionError(SifenError):
    """Error de red, TLS o timeout al conectar con SIFEN."""


class SifenSOAPError(SifenError):
    """SOAP Fault devuelto por el servidor SIFEN."""


# ── Respuesta parseada ────────────────────────────────────────────────────────


@dataclass
class SifenResponse:
    """Respuesta de SIFEN parseada a campos tipados.

    Attributes:
        code: código de respuesta SIFEN (``"0260"``, ``"03xx"``, etc.).
        message: mensaje descriptivo del servidor.
        approved: True si el código indica aprobación (0260 o 0261).
        observations: lista de observaciones del servidor (si las hay).
        raw: payload completo devuelto por zeep (para debug/auditoría).
    """

    code: str
    message: str
    approved: bool
    observations: list[str] = field(default_factory=list)
    raw: Any = field(default=None, repr=False)

    @classmethod
    def from_soap_response(cls, soap_result: Any) -> "SifenResponse":
        """Construye un :class:`SifenResponse` desde la respuesta zeep.

        La estructura real depende del WSDL — este método es el punto de
        adaptación cuando los WSDLs estén disponibles. Por ahora acepta tanto
        dict-like como objetos con atributos.

        Args:
            soap_result: objeto devuelto por ``zeep`` (zeep.xsd.CompoundValue
                u objeto con atributos ``dCodRes``, ``dMsgRes``, ``xObsEnt``).

        Returns:
            SifenResponse con los campos parseados.
        """
        # Intenta acceso por atributo; si falla, intenta __getitem__ (dict-like)
        def _get(obj, *keys, default=""):
            for key in keys:
                try:
                    val = getattr(obj, key, None)
                    if val is None:
                        val = obj[key] if hasattr(obj, "__getitem__") else None
                    if val is not None:
                        return str(val).strip()
                except (KeyError, TypeError, AttributeError):
                    continue
            return default

        code = _get(soap_result, "dCodRes", "cod_res", "code")
        message = _get(soap_result, "dMsgRes", "msg_res", "message")

        # Observaciones: xObsEnt puede ser lista o nodo simple.
        # Solo usamos el atributo canónico SIFEN (xObsEnt) para evitar
        # colisiones con atributos auto-generados por MagicMock en los tests.
        observations: list[str] = []
        raw_obs = getattr(soap_result, "xObsEnt", None)
        if raw_obs is None and hasattr(soap_result, "__getitem__"):
            try:
                raw_obs = soap_result["xObsEnt"]
            except (KeyError, TypeError):
                raw_obs = None
        if raw_obs is not None:
            if isinstance(raw_obs, (list, tuple)):
                observations = [str(o).strip() for o in raw_obs if o]
            else:
                obs_str = str(raw_obs).strip()
                if obs_str:
                    observations = [obs_str]

        approved = code in (CODE_DE_APROBADO, CODE_DE_APROBADO_CON_OBS)
        return cls(
            code=code,
            message=message,
            approved=approved,
            observations=observations,
            raw=soap_result,
        )

    @property
    def is_rejection(self) -> bool:
        """True si el código es un rechazo (03xx)."""
        return self.code.startswith(_REJECTION_PREFIX)

    @property
    def is_lote_in_progress(self) -> bool:
        """True si el lote todavía está siendo procesado."""
        return self.code == CODE_LOTE_EN_PROCESO

    @property
    def is_lote_concluded(self) -> bool:
        """True si el procesamiento del lote concluyó."""
        return self.code == CODE_LOTE_CONCLUIDO

    @property
    def is_lote_extemporaneo(self) -> bool:
        """True si la consulta del lote superó el plazo de 48h."""
        return self.code == CODE_LOTE_EXTEMPORANEO


# ── Cliente SOAP ──────────────────────────────────────────────────────────────


class SifenClient:
    """Cliente SOAP mTLS para los Web Services SIFEN.

    El cliente instancia un ``zeep.Client`` por operación (lazy, con caché)
    usando un ``Transport`` respaldado por una sesión ``requests`` con mTLS
    vía ``requests_pkcs12``.

    Args:
        p12_bytes: contenido binario del certificado CCFE (.p12/.pfx).
        p12_password: contraseña del .p12 (str).
        environment: entorno SIFEN — ``"test"`` (default) o ``"prod"``.
        connect_timeout: timeout de conexión en segundos (default 10).
        read_timeout: timeout de lectura en segundos (default 60).

    Example::

        with open("ccfe.p12", "rb") as f:
            client = SifenClient(f.read(), "mi-password", environment="test")
        response = client.send_de("<rDE>...</rDE>")
    """

    def __init__(
        self,
        p12_bytes: bytes,
        p12_password: str,
        environment: str = ENVIRONMENT_TEST,
        connect_timeout: int = DEFAULT_CONNECT_TIMEOUT,
        read_timeout: int = DEFAULT_READ_TIMEOUT,
    ) -> None:
        self._p12_bytes = p12_bytes
        self._p12_password = p12_password
        self._environment = environment
        self._timeout = (connect_timeout, read_timeout)
        self._session: requests.Session | None = None
        self._zeep_clients: dict[str, zeep.Client] = {}

    # ── Sesión mTLS ───────────────────────────────────────────────────────────

    def _build_session(self) -> requests.Session:
        """Construye la sesión requests con mTLS vía requests_pkcs12."""
        session = requests.Session()
        # Pkcs12Adapter maneja la autenticación mTLS con el .p12
        adapter = Pkcs12Adapter(
            pkcs12_data=self._p12_bytes,
            pkcs12_password=self._p12_password,
        )
        session.mount("https://", adapter)
        return session

    @property
    def session(self) -> requests.Session:
        """Sesión requests con mTLS (lazy init, reutilizable)."""
        if self._session is None:
            self._session = self._build_session()
        return self._session

    # ── Cliente zeep ─────────────────────────────────────────────────────────

    def _get_zeep_client(self, operation: str) -> zeep.Client:
        """Devuelve (y cachea) el cliente zeep para la operación dada.

        Args:
            operation: clave de operación (``recep_de``, ``recep_lote_de``,
                ``result_lote_de``, ``cons_de``).

        Returns:
            Instancia ``zeep.Client`` lista para usar.

        Raises:
            SifenConnectionError: si el WSDL no se pudo cargar (red o TLS).
        """
        if operation not in self._zeep_clients:
            wsdl_url = get_wsdl_url(operation, self._environment)
            transport = zeep.Transport(
                session=self.session,
                operation_timeout=self._timeout[1],
            )
            try:
                self._zeep_clients[operation] = zeep.Client(
                    wsdl_url, transport=transport
                )
            except (
                zeep.exceptions.Error,
                requests.exceptions.RequestException,
                OSError,
            ) as exc:
                raise SifenConnectionError(
                    "No se pudo cargar el WSDL '%s': %s" % (wsdl_url, exc)
                ) from exc
        return self._zeep_clients[operation]

    # ── Operaciones SOAP ──────────────────────────────────────────────────────

    def send_de(self, signed_xml: str) -> SifenResponse:
        """Envía un DE firmado a SIFEN vía ``siRecepDE`` (síncrono).

        Args:
            signed_xml: XML del DE firmado (string UTF-8 completo).

        Returns:
            :class:`SifenResponse` con el resultado del servidor.

        Raises:
            SifenConnectionError: error de red / TLS / timeout.
            SifenSOAPError: SOAP fault del servidor.

        TODO: confirmar si SIFEN espera el XML como string literal o como nodo
        embebido en el envelope (ver issue #38).
        """
        client = self._get_zeep_client("recep_de")
        try:
            result = client.service.siRecepDE(xmlDE=signed_xml)
        except (socket.timeout, requests.exceptions.Timeout) as exc:
            raise SifenConnectionError("Timeout al enviar DE: %s" % exc) from exc
        except requests.exceptions.RequestException as exc:
            raise SifenConnectionError("Error de red al enviar DE: %s" % exc) from exc
        except zeep.exceptions.Fault as exc:
            raise SifenSOAPError("SOAP Fault en siRecepDE: %s" % exc) from exc
        except zeep.exceptions.Error as exc:
            raise SifenConnectionError("Error zeep al enviar DE: %s" % exc) from exc
        return SifenResponse.from_soap_response(result)

    def send_lote(self, signed_xml_list: list[str]) -> SifenResponse:
        """Envía un lote de hasta 50 DE firmados vía ``siRecepLoteDE``.

        El contenido del lote se comprime con gzip y se codifica en Base64
        antes de enviarlo, como exige el Manual SIFEN v150 §6.

        Args:
            signed_xml_list: lista de strings XML firmados (máximo 50,
                todos del mismo tipo de documento).

        Returns:
            :class:`SifenResponse` con el número de lote asignado por SIFEN.

        Raises:
            ValueError: si la lista supera los 50 DE.
            SifenConnectionError: error de red / TLS / timeout.
            SifenSOAPError: SOAP fault del servidor.
        """
        if not signed_xml_list:
            raise ValueError("La lista de DE del lote no puede estar vacía")
        if len(signed_xml_list) > MAX_DE_POR_LOTE:
            raise ValueError(
                "El lote supera el máximo de %d DE (%d enviados)"
                % (MAX_DE_POR_LOTE, len(signed_xml_list))
            )
        lote_content = self._build_lote_payload(signed_xml_list)
        client = self._get_zeep_client("recep_lote_de")
        try:
            result = client.service.siRecepLoteDE(xmlLoteDE=lote_content)
        except (socket.timeout, requests.exceptions.Timeout) as exc:
            raise SifenConnectionError("Timeout al enviar lote: %s" % exc) from exc
        except requests.exceptions.RequestException as exc:
            raise SifenConnectionError("Error de red al enviar lote: %s" % exc) from exc
        except zeep.exceptions.Fault as exc:
            raise SifenSOAPError("SOAP Fault en siRecepLoteDE: %s" % exc) from exc
        except zeep.exceptions.Error as exc:
            raise SifenConnectionError("Error zeep al enviar lote: %s" % exc) from exc
        return SifenResponse.from_soap_response(result)

    def query_lote(self, lote_number: str) -> SifenResponse:
        """Consulta el resultado de un lote vía ``siResultLoteDE``.

        Args:
            lote_number: número de lote devuelto por :meth:`send_lote`.

        Returns:
            :class:`SifenResponse`. Verificar :attr:`SifenResponse.is_lote_in_progress`
            para determinar si hay que reintentar (mínimo 10 minutos entre consultas).

        Raises:
            SifenConnectionError: error de red / TLS / timeout.
            SifenSOAPError: SOAP fault del servidor.
        """
        client = self._get_zeep_client("result_lote_de")
        try:
            result = client.service.siResultLoteDE(nroLote=lote_number)
        except (socket.timeout, requests.exceptions.Timeout) as exc:
            raise SifenConnectionError("Timeout al consultar lote: %s" % exc) from exc
        except requests.exceptions.RequestException as exc:
            raise SifenConnectionError(
                "Error de red al consultar lote: %s" % exc
            ) from exc
        except zeep.exceptions.Fault as exc:
            raise SifenSOAPError("SOAP Fault en siResultLoteDE: %s" % exc) from exc
        except zeep.exceptions.Error as exc:
            raise SifenConnectionError(
                "Error zeep al consultar lote: %s" % exc
            ) from exc
        return SifenResponse.from_soap_response(result)

    def query_de(self, cdc: str) -> SifenResponse:
        """Consulta un DE individual por CDC vía ``siConsDE``.

        Usado como fallback tras vencer las 48h del plazo del lote.

        Args:
            cdc: Código de Control de 44 dígitos del DE a consultar.

        Returns:
            :class:`SifenResponse` con el estado del DE en SIFEN.

        Raises:
            SifenConnectionError: error de red / TLS / timeout.
            SifenSOAPError: SOAP fault del servidor.
        """
        client = self._get_zeep_client("cons_de")
        try:
            result = client.service.siConsDE(dCDC=cdc)
        except (socket.timeout, requests.exceptions.Timeout) as exc:
            raise SifenConnectionError("Timeout al consultar DE: %s" % exc) from exc
        except requests.exceptions.RequestException as exc:
            raise SifenConnectionError(
                "Error de red al consultar DE: %s" % exc
            ) from exc
        except zeep.exceptions.Fault as exc:
            raise SifenSOAPError("SOAP Fault en siConsDE: %s" % exc) from exc
        except zeep.exceptions.Error as exc:
            raise SifenConnectionError("Error zeep al consultar DE: %s" % exc) from exc
        return SifenResponse.from_soap_response(result)

    # ── Helpers internos ──────────────────────────────────────────────────────

    @staticmethod
    def _build_lote_payload(signed_xml_list: list[str]) -> str:
        """Construye el payload del lote: gzip + base64.

        Los DE firmados se concatenan en un ``<rLoteDE>`` mínimo, se comprimen
        con gzip y se codifica el resultado en Base64 (RFC 4648).

        TODO: la estructura exacta de ``<rLoteDE>`` depende del WSDL real —
        confirmar contra los esquemas XSD descargados de sifen-test.

        Args:
            signed_xml_list: lista de strings XML firmados.

        Returns:
            String Base64 del lote comprimido.
        """
        # Envoltura mínima — estructura definitiva se ajustará con WSDLs reales
        items = "".join(signed_xml_list)
        lote_xml = (
            '<?xml version="1.0" encoding="UTF-8"?>' f"<rLoteDE>{items}</rLoteDE>"
        ).encode("utf-8")
        compressed = gzip.compress(lote_xml)
        return base64.b64encode(compressed).decode("ascii")
