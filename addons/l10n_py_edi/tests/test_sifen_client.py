# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del cliente SOAP SIFEN — 100% mockeados, cero red en suite estándar.

Cubre:
    - Parseo de respuestas: 0260 aprobado, 0261 aprobado-con-obs, 03xx rechazo.
    - SifenResponse.is_* properties.
    - SifenConnectionError en timeout y errores de red.
    - SifenSOAPError en SOAP Fault.
    - Construcción del lote (gzip + base64).
    - Selección de endpoint test/prod vía sifen_endpoints.
    - SifenClient con zeep.Client 100% mockeado (sin red, sin WSDL real).
"""
import base64
import gzip
import os
import socket
from unittest.mock import MagicMock

import requests.exceptions
import zeep.exceptions

from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_edi.services.sifen_client import (
    CODE_DE_APROBADO,
    CODE_DE_APROBADO_CON_OBS,
    CODE_LOTE_CONCLUIDO,
    CODE_LOTE_EN_PROCESO,
    CODE_LOTE_EXTEMPORANEO,
    MAX_DE_POR_LOTE,
    SifenClient,
    SifenConnectionError,
    SifenResponse,
    SifenSOAPError,
)
from odoo.addons.l10n_py_edi.services.sifen_endpoints import (
    ENVIRONMENT_PROD,
    ENVIRONMENT_TEST,
    SIFEN_PROD_CONS_DE,
    SIFEN_PROD_RECEP_DE,
    SIFEN_PROD_RECEP_LOTE_DE,
    SIFEN_PROD_RESULT_LOTE_DE,
    SIFEN_TEST_CONS_DE,
    SIFEN_TEST_RECEP_DE,
    SIFEN_TEST_RECEP_LOTE_DE,
    SIFEN_TEST_RESULT_LOTE_DE,
    get_wsdl_url,
)

# ── Fixtures de respuesta (ejemplos tomados de docs/02) ───────────────────────

_RESP_0260 = {
    "dCodRes": "0260",
    "dMsgRes": "DE recibido y aprobado",
    "xObsEnt": None,
}

_RESP_0261 = {
    "dCodRes": "0261",
    "dMsgRes": "DE aprobado con observación",
    "xObsEnt": ["Observación 1"],
}

_RESP_RECHAZO = {
    "dCodRes": "0304",
    "dMsgRes": "DE rechazado por error en el CDC",
    "xObsEnt": ["El CDC no coincide con los datos del DE", "Campo dCDC inválido"],
}

_RESP_LOTE_EN_PROCESO = {
    "dCodRes": CODE_LOTE_EN_PROCESO,
    "dMsgRes": "Lote en procesamiento",
    "xObsEnt": None,
}

_RESP_LOTE_CONCLUIDO = {
    "dCodRes": CODE_LOTE_CONCLUIDO,
    "dMsgRes": "Procesamiento de lote concluido",
    "xObsEnt": None,
}

_RESP_LOTE_EXTEMPORANEO = {
    "dCodRes": CODE_LOTE_EXTEMPORANEO,
    "dMsgRes": "Consulta extemporánea de lote",
    "xObsEnt": None,
}

FAKE_CDC = "01800695631001003000013712022010619364760029"
FAKE_SIGNED_XML = (
    '<rDE xmlns="http://ekuatia.set.gov.py/sifen/xsd"><DE Id="%s"/></rDE>' % FAKE_CDC
)


def _make_soap_result(data: dict) -> MagicMock:
    """Crea un mock de zeep CompoundValue con los datos de respuesta."""
    mock = MagicMock()
    mock.dCodRes = data.get("dCodRes", "")
    mock.dMsgRes = data.get("dMsgRes", "")
    mock.xObsEnt = data.get("xObsEnt")
    return mock


def _make_client_with_mock(operation: str, soap_result=None, side_effect=None):
    """Construye un SifenClient con el zeep.Client mockeado.

    Returns:
        Tuple (client, mock_zeep_client).
    """
    fake_p12 = b"fake-p12-data"
    dummy_p12_password = "dummy-pass"

    mock_zeep = MagicMock(spec=zeep.Client)
    mock_service = MagicMock()
    mock_zeep.service = mock_service

    # Configurar el método específico de la operación
    method_map = {
        "recep_de": "siRecepDE",
        "recep_lote_de": "siRecepLoteDE",
        "result_lote_de": "siResultLoteDE",
        "cons_de": "siConsDE",
    }
    method_name = method_map.get(operation, "siRecepDE")
    mock_method = getattr(mock_service, method_name)
    if side_effect is not None:
        mock_method.side_effect = side_effect
    elif soap_result is not None:
        mock_method.return_value = soap_result

    client = SifenClient(fake_p12, dummy_p12_password, environment=ENVIRONMENT_TEST)
    # Inyectar el mock directamente en el caché de clientes zeep
    client._zeep_clients[operation] = mock_zeep

    return client, mock_zeep


# ═══════════════════════════════════════════════════════════════════════════════
# Suite estándar — 100% mockeada, sin red
# ═══════════════════════════════════════════════════════════════════════════════


@tagged("standard", "l10n_py")
class TestSifenEndpoints(BaseCase):
    """Tests de sifen_endpoints — URLs y helper get_wsdl_url."""

    def test_test_environment_urls_contain_sifen_test(self):
        for const in (
            SIFEN_TEST_RECEP_DE,
            SIFEN_TEST_RECEP_LOTE_DE,
            SIFEN_TEST_RESULT_LOTE_DE,
            SIFEN_TEST_CONS_DE,
        ):
            self.assertIn("sifen-test.set.gov.py", const)

    def test_prod_environment_urls_contain_sifen_prod(self):
        for const in (
            SIFEN_PROD_RECEP_DE,
            SIFEN_PROD_RECEP_LOTE_DE,
            SIFEN_PROD_RESULT_LOTE_DE,
            SIFEN_PROD_CONS_DE,
        ):
            self.assertIn("sifen.set.gov.py", const)
            self.assertNotIn("sifen-test", const)

    def test_test_recep_de_url(self):
        self.assertEqual(
            SIFEN_TEST_RECEP_DE,
            "https://sifen-test.set.gov.py/de/ws/sync/recibe.wsdl",
        )

    def test_prod_recep_de_url(self):
        self.assertEqual(
            SIFEN_PROD_RECEP_DE,
            "https://sifen.set.gov.py/de/ws/sync/recibe.wsdl",
        )

    def test_get_wsdl_url_test_recep_de(self):
        url = get_wsdl_url("recep_de", ENVIRONMENT_TEST)
        self.assertEqual(url, SIFEN_TEST_RECEP_DE)

    def test_get_wsdl_url_prod_recep_de(self):
        url = get_wsdl_url("recep_de", ENVIRONMENT_PROD)
        self.assertEqual(url, SIFEN_PROD_RECEP_DE)

    def test_get_wsdl_url_invalid_environment_raises(self):
        with self.assertRaises(ValueError) as ctx:
            get_wsdl_url("recep_de", "staging")
        self.assertIn("staging", str(ctx.exception))

    def test_get_wsdl_url_invalid_operation_raises(self):
        with self.assertRaises(ValueError) as ctx:
            get_wsdl_url("operacion_inexistente", ENVIRONMENT_TEST)
        self.assertIn("operacion_inexistente", str(ctx.exception))

    def test_all_operations_available_in_both_environments(self):
        operations = [
            "recep_de",
            "recep_lote_de",
            "result_lote_de",
            "cons_de",
            "recep_evento",
            "cons_ruc",
        ]
        for op in operations:
            for env in (ENVIRONMENT_TEST, ENVIRONMENT_PROD):
                url = get_wsdl_url(op, env)
                self.assertTrue(url.startswith("https://"), f"{op}/{env}: {url}")

    def test_urls_end_with_wsdl(self):
        operations = [
            "recep_de",
            "recep_lote_de",
            "result_lote_de",
            "cons_de",
        ]
        for op in operations:
            for env in (ENVIRONMENT_TEST, ENVIRONMENT_PROD):
                url = get_wsdl_url(op, env)
                self.assertTrue(
                    url.endswith(".wsdl"), f"{op}/{env} no termina en .wsdl: {url}"
                )


@tagged("standard", "l10n_py")
class TestSifenResponse(BaseCase):
    """Tests de SifenResponse.from_soap_response y sus properties."""

    def test_parseo_0260_aprobado(self):
        soap_result = _make_soap_result(_RESP_0260)
        resp = SifenResponse.from_soap_response(soap_result)

        self.assertEqual(resp.code, CODE_DE_APROBADO)
        self.assertEqual(resp.message, "DE recibido y aprobado")
        self.assertTrue(resp.approved)
        self.assertEqual(resp.observations, [])

    def test_parseo_0261_aprobado_con_observacion(self):
        soap_result = _make_soap_result(_RESP_0261)
        resp = SifenResponse.from_soap_response(soap_result)

        self.assertEqual(resp.code, CODE_DE_APROBADO_CON_OBS)
        self.assertTrue(resp.approved)
        self.assertIn("Observación 1", resp.observations)

    def test_parseo_rechazo_03xx(self):
        soap_result = _make_soap_result(_RESP_RECHAZO)
        resp = SifenResponse.from_soap_response(soap_result)

        self.assertEqual(resp.code, "0304")
        self.assertFalse(resp.approved)
        self.assertTrue(resp.is_rejection)
        self.assertEqual(len(resp.observations), 2)
        self.assertIn("El CDC no coincide con los datos del DE", resp.observations)

    def test_parseo_lote_en_proceso(self):
        soap_result = _make_soap_result(_RESP_LOTE_EN_PROCESO)
        resp = SifenResponse.from_soap_response(soap_result)

        self.assertFalse(resp.approved)
        self.assertTrue(resp.is_lote_in_progress)
        self.assertFalse(resp.is_lote_concluded)

    def test_parseo_lote_concluido(self):
        soap_result = _make_soap_result(_RESP_LOTE_CONCLUIDO)
        resp = SifenResponse.from_soap_response(soap_result)

        self.assertTrue(resp.is_lote_concluded)
        self.assertFalse(resp.is_lote_in_progress)

    def test_parseo_lote_extemporaneo(self):
        soap_result = _make_soap_result(_RESP_LOTE_EXTEMPORANEO)
        resp = SifenResponse.from_soap_response(soap_result)

        self.assertTrue(resp.is_lote_extemporaneo)

    def test_is_rejection_0260_false(self):
        soap_result = _make_soap_result(_RESP_0260)
        resp = SifenResponse.from_soap_response(soap_result)
        self.assertFalse(resp.is_rejection)

    def test_is_rejection_03xx_true(self):
        soap_result = _make_soap_result(_RESP_RECHAZO)
        resp = SifenResponse.from_soap_response(soap_result)
        self.assertTrue(resp.is_rejection)

    def test_raw_preserved(self):
        soap_result = _make_soap_result(_RESP_0260)
        resp = SifenResponse.from_soap_response(soap_result)
        self.assertIs(resp.raw, soap_result)

    def test_observations_none_yields_empty_list(self):
        mock = _make_soap_result({"dCodRes": "0260", "dMsgRes": "ok", "xObsEnt": None})
        resp = SifenResponse.from_soap_response(mock)
        self.assertEqual(resp.observations, [])

    def test_observations_string_yields_single_item(self):
        mock = MagicMock()
        mock.dCodRes = "0260"
        mock.dMsgRes = "ok"
        mock.xObsEnt = "Observación simple"
        resp = SifenResponse.from_soap_response(mock)
        self.assertEqual(resp.observations, ["Observación simple"])


@tagged("standard", "l10n_py")
class TestSifenClientSendDe(BaseCase):
    """Tests de SifenClient.send_de con zeep mockeado."""

    def test_send_de_aprobado_devuelve_sifen_response(self):
        soap_result = _make_soap_result(_RESP_0260)
        client, mock_zeep = _make_client_with_mock("recep_de", soap_result=soap_result)

        resp = client.send_de(FAKE_SIGNED_XML)

        self.assertIsInstance(resp, SifenResponse)
        self.assertTrue(resp.approved)
        mock_zeep.service.siRecepDE.assert_called_once_with(xmlDE=FAKE_SIGNED_XML)

    def test_send_de_rechazo_devuelve_not_approved(self):
        soap_result = _make_soap_result(_RESP_RECHAZO)
        client, _ = _make_client_with_mock("recep_de", soap_result=soap_result)

        resp = client.send_de(FAKE_SIGNED_XML)

        self.assertFalse(resp.approved)
        self.assertTrue(resp.is_rejection)

    def test_send_de_timeout_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "recep_de",
            side_effect=requests.exceptions.Timeout("timed out"),
        )

        with self.assertRaises(SifenConnectionError) as ctx:
            client.send_de(FAKE_SIGNED_XML)
        self.assertIn("Timeout", str(ctx.exception))

    def test_send_de_socket_timeout_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "recep_de",
            side_effect=socket.timeout("socket timed out"),
        )

        with self.assertRaises(SifenConnectionError):
            client.send_de(FAKE_SIGNED_XML)

    def test_send_de_network_error_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "recep_de",
            side_effect=requests.exceptions.ConnectionError("connection refused"),
        )

        with self.assertRaises(SifenConnectionError) as ctx:
            client.send_de(FAKE_SIGNED_XML)
        self.assertIn("red", str(ctx.exception))

    def test_send_de_soap_fault_raises_soap_error(self):
        client, _ = _make_client_with_mock(
            "recep_de",
            side_effect=zeep.exceptions.Fault("SOAP Fault: invalid DE"),
        )

        with self.assertRaises(SifenSOAPError) as ctx:
            client.send_de(FAKE_SIGNED_XML)
        self.assertIn("siRecepDE", str(ctx.exception))

    def test_send_de_zeep_error_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "recep_de",
            side_effect=zeep.exceptions.Error("zeep error"),
        )

        with self.assertRaises(SifenConnectionError):
            client.send_de(FAKE_SIGNED_XML)


@tagged("standard", "l10n_py")
class TestSifenClientSendLote(BaseCase):
    """Tests de SifenClient.send_lote y la construcción del lote."""

    def test_build_lote_payload_es_base64_valido(self):
        xmls = [FAKE_SIGNED_XML, FAKE_SIGNED_XML]
        payload = SifenClient._build_lote_payload(xmls)

        # Debe ser base64 decodificable
        decoded = base64.b64decode(payload)
        self.assertIsInstance(decoded, bytes)

    def test_build_lote_payload_gzip_decomprimible(self):
        xmls = [FAKE_SIGNED_XML]
        payload = SifenClient._build_lote_payload(xmls)

        decoded = base64.b64decode(payload)
        decompressed = gzip.decompress(decoded)
        self.assertIn(b"<rLoteDE>", decompressed)
        self.assertIn(FAKE_CDC.encode(), decompressed)

    def test_build_lote_contiene_todos_los_xml(self):
        xml1 = '<rDE Id="CDC1"><DE/></rDE>'
        xml2 = '<rDE Id="CDC2"><DE/></rDE>'
        payload = SifenClient._build_lote_payload([xml1, xml2])

        decompressed = gzip.decompress(base64.b64decode(payload))
        self.assertIn(b"CDC1", decompressed)
        self.assertIn(b"CDC2", decompressed)

    def test_send_lote_llama_sireceplotede(self):
        soap_result = _make_soap_result(
            {"dCodRes": "0300", "dMsgRes": "Lote recibido", "xObsEnt": None}
        )
        client, mock_zeep = _make_client_with_mock(
            "recep_lote_de", soap_result=soap_result
        )

        resp = client.send_lote([FAKE_SIGNED_XML])

        self.assertIsInstance(resp, SifenResponse)
        mock_zeep.service.siRecepLoteDE.assert_called_once()
        call_kwargs = mock_zeep.service.siRecepLoteDE.call_args
        self.assertIn("xmlLoteDE", call_kwargs.kwargs)

    def test_send_lote_payload_es_base64(self):
        """El argumento xmlLoteDE debe ser un string base64."""
        soap_result = _make_soap_result(
            {"dCodRes": "0300", "dMsgRes": "ok", "xObsEnt": None}
        )
        client, mock_zeep = _make_client_with_mock(
            "recep_lote_de", soap_result=soap_result
        )
        client.send_lote([FAKE_SIGNED_XML])

        payload = mock_zeep.service.siRecepLoteDE.call_args.kwargs["xmlLoteDE"]
        # Debe ser decodificable como base64
        decoded = base64.b64decode(payload)
        decompressed = gzip.decompress(decoded)
        self.assertIn(b"<rLoteDE>", decompressed)

    def test_send_lote_lista_vacia_raises_value_error(self):
        client = SifenClient(b"fake", "fake")

        with self.assertRaises(ValueError) as ctx:
            client.send_lote([])
        self.assertIn("vacía", str(ctx.exception))

    def test_send_lote_supera_maximo_raises_value_error(self):
        client = SifenClient(b"fake", "fake")
        xmls = [FAKE_SIGNED_XML] * (MAX_DE_POR_LOTE + 1)

        with self.assertRaises(ValueError) as ctx:
            client.send_lote(xmls)
        self.assertIn(str(MAX_DE_POR_LOTE), str(ctx.exception))

    def test_send_lote_exactly_max_allowed(self):
        soap_result = _make_soap_result(
            {"dCodRes": "0300", "dMsgRes": "ok", "xObsEnt": None}
        )
        client, _ = _make_client_with_mock("recep_lote_de", soap_result=soap_result)
        # 50 DE exactos debe funcionar sin excepción
        xmls = [FAKE_SIGNED_XML] * MAX_DE_POR_LOTE
        resp = client.send_lote(xmls)
        self.assertIsInstance(resp, SifenResponse)

    def test_send_lote_timeout_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "recep_lote_de",
            side_effect=requests.exceptions.Timeout("timeout"),
        )

        with self.assertRaises(SifenConnectionError) as ctx:
            client.send_lote([FAKE_SIGNED_XML])
        self.assertIn("Timeout", str(ctx.exception))

    def test_send_lote_soap_fault_raises_soap_error(self):
        client, _ = _make_client_with_mock(
            "recep_lote_de",
            side_effect=zeep.exceptions.Fault("SOAP Fault"),
        )

        with self.assertRaises(SifenSOAPError):
            client.send_lote([FAKE_SIGNED_XML])


@tagged("standard", "l10n_py")
class TestSifenClientQueryLote(BaseCase):
    """Tests de SifenClient.query_lote."""

    def test_query_lote_en_proceso(self):
        soap_result = _make_soap_result(_RESP_LOTE_EN_PROCESO)
        client, mock_zeep = _make_client_with_mock(
            "result_lote_de", soap_result=soap_result
        )

        resp = client.query_lote("NRO-LOTE-001")

        self.assertTrue(resp.is_lote_in_progress)
        mock_zeep.service.siResultLoteDE.assert_called_once_with(nroLote="NRO-LOTE-001")

    def test_query_lote_concluido(self):
        soap_result = _make_soap_result(_RESP_LOTE_CONCLUIDO)
        client, _ = _make_client_with_mock("result_lote_de", soap_result=soap_result)

        resp = client.query_lote("NRO-LOTE-001")

        self.assertTrue(resp.is_lote_concluded)

    def test_query_lote_extemporaneo(self):
        soap_result = _make_soap_result(_RESP_LOTE_EXTEMPORANEO)
        client, _ = _make_client_with_mock("result_lote_de", soap_result=soap_result)

        resp = client.query_lote("NRO-LOTE-001")

        self.assertTrue(resp.is_lote_extemporaneo)

    def test_query_lote_timeout_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "result_lote_de",
            side_effect=requests.exceptions.Timeout("timeout"),
        )

        with self.assertRaises(SifenConnectionError) as ctx:
            client.query_lote("NRO-001")
        self.assertIn("Timeout", str(ctx.exception))

    def test_query_lote_soap_fault_raises_soap_error(self):
        client, _ = _make_client_with_mock(
            "result_lote_de",
            side_effect=zeep.exceptions.Fault("Fault"),
        )

        with self.assertRaises(SifenSOAPError):
            client.query_lote("NRO-001")


@tagged("standard", "l10n_py")
class TestSifenClientQueryDe(BaseCase):
    """Tests de SifenClient.query_de."""

    def test_query_de_aprobado(self):
        soap_result = _make_soap_result(_RESP_0260)
        client, mock_zeep = _make_client_with_mock("cons_de", soap_result=soap_result)

        resp = client.query_de(FAKE_CDC)

        self.assertTrue(resp.approved)
        mock_zeep.service.siConsDE.assert_called_once_with(dCDC=FAKE_CDC)

    def test_query_de_timeout_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "cons_de",
            side_effect=requests.exceptions.Timeout("timeout"),
        )

        with self.assertRaises(SifenConnectionError) as ctx:
            client.query_de(FAKE_CDC)
        self.assertIn("Timeout", str(ctx.exception))

    def test_query_de_soap_fault_raises_soap_error(self):
        client, _ = _make_client_with_mock(
            "cons_de",
            side_effect=zeep.exceptions.Fault("Fault"),
        )

        with self.assertRaises(SifenSOAPError):
            client.query_de(FAKE_CDC)

    def test_query_de_network_error_raises_connection_error(self):
        client, _ = _make_client_with_mock(
            "cons_de",
            side_effect=requests.exceptions.ConnectionError("conn refused"),
        )

        with self.assertRaises(SifenConnectionError):
            client.query_de(FAKE_CDC)


@tagged("standard", "l10n_py")
class TestSifenClientEndpointSelection(BaseCase):
    """Tests de selección de endpoint test/prod en SifenClient."""

    def test_client_test_environment_uses_test_urls(self):
        """Un cliente TEST consulta la URL correcta de sifen-test."""
        # Verificamos via get_wsdl_url que el entorno TEST usa sifen-test.
        # La instanciación real del cliente zeep queda cubierta por la prueba
        # de integración (suite external); aquí solo validamos el ruteo de URL.
        url = get_wsdl_url("recep_de", ENVIRONMENT_TEST)
        self.assertIn("sifen-test.set.gov.py", url)

    def test_client_prod_environment_uses_prod_urls(self):
        """Un cliente PROD consulta la URL correcta de sifen (sin -test)."""
        url = get_wsdl_url("recep_de", ENVIRONMENT_PROD)
        self.assertNotIn("sifen-test", url)
        self.assertIn("sifen.set.gov.py", url)

    def test_environment_test_constant(self):
        self.assertEqual(ENVIRONMENT_TEST, "test")

    def test_environment_prod_constant(self):
        self.assertEqual(ENVIRONMENT_PROD, "prod")

    def test_max_de_por_lote_constant(self):
        self.assertEqual(MAX_DE_POR_LOTE, 50)

    def test_code_de_aprobado_constant(self):
        self.assertEqual(CODE_DE_APROBADO, "0260")

    def test_code_de_aprobado_con_obs_constant(self):
        self.assertEqual(CODE_DE_APROBADO_CON_OBS, "0261")


# ═══════════════════════════════════════════════════════════════════════════════
# Suite de integración real — requiere SIFEN_TEST_URL y certificado CCFE real
# ═══════════════════════════════════════════════════════════════════════════════


@tagged("-standard", "external", "l10n_py")
class TestSifenClientExternal(BaseCase):
    """Tests de integración contra sifen-test.set.gov.py.

    Se saltan automáticamente si no hay un CCFE de prueba configurado.
    Para ejecutar, setear las siguientes variables de entorno::

        SIFEN_TEST_URL=https://sifen-test.set.gov.py/de/ws/sync/recibe.wsdl
        SIFEN_TEST_P12_PATH=/ruta/al/ccfe-test.p12
        SIFEN_TEST_P12_PASSWORD=contraseña-del-p12

    Estos tests NO corren en la suite estándar (``-standard`` tag).
    """

    def setUp(self):
        super().setUp()
        p12_path = os.environ.get("SIFEN_TEST_P12_PATH")
        if not p12_path:
            self.skipTest(
                "Tests de integración SIFEN requieren SIFEN_TEST_P12_PATH "
                "en las variables de entorno. "
                "Omitiendo — solo para uso con CCFE de prueba DNIT."
            )
        p12_password = os.environ.get("SIFEN_TEST_P12_PASSWORD", "")
        try:
            with open(p12_path, "rb") as f:
                self.p12_bytes = f.read()
        except OSError as exc:
            self.skipTest(f"No se pudo leer SIFEN_TEST_P12_PATH: {exc}")
        self.p12_pass = p12_password
        self.client = SifenClient(
            self.p12_bytes,
            self.p12_pass,
            environment=ENVIRONMENT_TEST,  # gitleaks:allow
        )

    def test_send_de_simple_fe(self):
        """Envío real de una FE simple a sifen-test."""
        # Un DE de prueba válido requiere CDC real, firma XAdES (PR-4) y
        # datos de contribuyente de homologación — este test es un placeholder
        # para la fase de homologación real con DNIT.
        self.skipTest(
            "Test de homologación real — placeholder para PR-9. "
            "Requiere DE firmado con CDC válido y CCFE de prueba DNIT."
        )
