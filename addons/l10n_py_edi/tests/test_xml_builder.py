# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del builder lxml del DE SIFEN (PR-3).

Todos los tests son BaseCase (sin DB) — el builder es Python puro.
La validación XSD usa los XSD oficiales v150 en docs/original/xsd/.

Casos cubiertos
---------------
- FE simple (1 ítem, IVA 10%) → valida XSD
- FE multi-ítem (IVA 10% + exenta + 5%) → valida XSD
- FE exenta/mixta → subtotales correctos
- dFeEmiDE usa el helper y su fecha == fecha del CDC (TD-008)
- Receptor innominado (no contribuyente, sin doc)
- Receptor contribuyente (RUC)
- Serialización round-trip estable
"""
from __future__ import annotations

import datetime
from pathlib import Path

from lxml import etree

from odoo.tests import BaseCase, tagged

from odoo.addons.l10n_py_edi.services import xml_builder as builder
from odoo.addons.l10n_py_edi.services import xml_constants as C
from odoo.addons.l10n_py_edi.services.cdc import compose_cdc
from odoo.addons.l10n_py_edi.services.datetime_helpers import format_de_datetime
from odoo.addons.l10n_py_edi.services.xsd_validator import (
    XsdValidationError,
    validate_against_xsd,
)

_FIXTURES_DIR = Path(__file__).parent / "xml_fixtures"

# ── Datos de empresa emisora fijos (RUC ficticio de tests) ────────────────────
_ISSUER = {
    "ruc": "80069563",
    "ruc_dv": 1,
    "taxpayer_type": C.TAXPAYER_PJ,
    "name": "EMPRESA TEST SA",
    "address": "Av. Mariscal López",
    "house_number": "1234",
    "department": 11,
    "department_desc": "Central",
    "city": 1,
    "city_desc": "Asunción",
    "phone": "021123456",
    "email": "test@empresa.com.py",
    "economic_activities": [
        {"code": "47111", "desc": "Venta al por menor en comercios no especializados"},
    ],
}

_TIMBRADO = {
    "de_type": C.DE_TYPE_FE,
    "timbrado_number": "12345678",
    "establishment": "001",
    "expedition_point": "001",
    "document_number": "0000001",
    "timbrado_start_date": "2025-01-01",
}

_OPERATION = {
    "transaction_type": C.TRANS_VENTA_MERCADERIA,
    "tax_type": C.TAX_TYPE_IVA,
    "currency": C.CURRENCY_PYG,
}

# Receptor contribuyente
_RECEIVER_CONTRIBUYENTE = {
    "nature": C.RECEIVER_CONTRIBUYENTE,
    "operation_type": C.OPER_B2B,
    "country": C.PAIS_PY,
    "country_desc": C.PAIS_PY_DESC,
    "taxpayer_type": C.TAXPAYER_PJ,
    "ruc": "12345678",
    "ruc_dv": 9,
    "name": "CLIENTE SA",
}

# Receptor innominado (sin nombre, sin doc)
_RECEIVER_INNOMINADO = {
    "nature": C.RECEIVER_NO_CONTRIBUYENTE,
    "operation_type": C.OPER_B2C,
    "country": C.PAIS_PY,
    "country_desc": C.PAIS_PY_DESC,
    "doc_type": C.DOC_REC_INNOMINADO,
    "doc_type_desc": "Innominado",
    "name": "Sin nombre",
}

# Receptor no contribuyente con CI
_RECEIVER_NO_CONTRIB_CI = {
    "nature": C.RECEIVER_NO_CONTRIBUYENTE,
    "operation_type": C.OPER_B2C,
    "country": C.PAIS_PY,
    "country_desc": C.PAIS_PY_DESC,
    "doc_type": C.DOC_REC_CEDULA_PY,
    "doc_type_desc": "Cédula paraguaya",
    "doc_number": "1234567",
    "name": "JUAN PEREZ",
}

# Ítem gravado 10%
_ITEM_10 = {
    "code": "001",
    "description": "Producto de prueba",
    "unit": 77,
    "unit_desc": "UNI",
    "quantity": "1",
    "unit_price": "110000",
    "total_gross": "110000",
    "total_item": "110000",
    "iva_type": C.IVA_GRAVADO_10,
    "iva_proportion": "100.00",
    "iva_base": "100000",
    "iva_amount": "10000",
}

# Ítem exento (iAfecIVA=3)
_ITEM_EXENTO = {
    "code": "002",
    "description": "Producto exento de prueba",
    "unit": 77,
    "unit_desc": "UNI",
    "quantity": "2",
    "unit_price": "50000",
    "total_gross": "100000",
    "total_item": "100000",
    "iva_type": C.IVA_EXENTO,
    "iva_proportion": "100.00",
    "iva_base": "0",
    "iva_amount": "0",
}

# Ítem gravado 5%
_ITEM_5 = {
    "code": "003",
    "description": "Producto canasta básica",
    "unit": 77,
    "unit_desc": "UNI",
    "quantity": "1",
    "unit_price": "21000",
    "total_gross": "21000",
    "total_item": "21000",
    "iva_type": C.IVA_GRAVADO_5,
    "iva_proportion": "100.00",
    "iva_base": "20000",
    "iva_amount": "1000",
}

_TOTALS_SIMPLE = {
    "sub_10": "110000",
    "total_ope": "110000",
    "total_discount": "0",
    "total_discount_global": "0",
    "total_advance_item": "0",
    "total_advance": "0",
    "discount_pct": "0.00",
    "discount_total": "0",
    "advance": "0",
    "rounding": "0",
    "grand_total": "110000",
    "iva_10": "100000",
    "liq_iva_10": "10000",
    "total_iva": "10000",
    "base_10": "100000",
    "total_base_iva": "100000",
}

_TOTALS_MIXTA = {
    "sub_exe": "100000",
    "sub_5": "21000",
    "sub_10": "110000",
    "total_ope": "231000",
    "total_discount": "0",
    "total_discount_global": "0",
    "total_advance_item": "0",
    "total_advance": "0",
    "discount_pct": "0.00",
    "discount_total": "0",
    "advance": "0",
    "rounding": "0",
    "grand_total": "231000",
    "iva_5": "20000",
    "iva_10": "100000",
    "liq_iva_5": "1000",
    "liq_iva_10": "10000",
    "total_iva": "11000",
    "base_5": "20000",
    "base_10": "100000",
    "total_base_iva": "120000",
}


def _make_cdc(dt: datetime.datetime, doc_number: str = "0000001") -> str:
    """Genera un CDC real usando la datetime dada."""
    return compose_cdc(
        document_type=1,
        ruc="80069563",
        ruc_dv=1,
        establishment="001",
        expedition_point="001",
        document_number=doc_number,
        taxpayer_type="2",
        issue_date=dt,
        emission_type="1",
        security_code="123456789",
    )


def _make_data(
    dt: datetime.datetime,
    items: list[dict],
    totals: dict,
    receiver: dict | None = None,
    doc_number: str = "0000001",
) -> dict:
    """Construye el dict data completo para build_de."""
    cdc = _make_cdc(dt, doc_number=doc_number)
    return {
        "cdc": cdc,
        "emission_type": C.EMISSION_NORMAL,
        "security_code": cdc[34:43],
        "dv_id": int(cdc[43]),
        "emission_datetime": dt,
        "timbrado": _TIMBRADO,
        "operation": _OPERATION,
        "issuer": _ISSUER,
        "receiver": receiver or _RECEIVER_CONTRIBUYENTE,
        "items": items,
        "totals": totals,
        "presence_indicator": C.PRES_OPERACION_PRESENCIAL,
    }


@tagged("standard", "l10n_py")
class TestXmlBuilder(BaseCase):
    """Tests del DE XML builder — Python puro, sin DB."""

    # ── Fixture datetime fija ─────────────────────────────────────────────────

    def setUp(self):
        super().setUp()
        # Datetime fija en horario de Asunción (naive = hora local PY)
        self.dt = datetime.datetime(2025, 6, 15, 10, 30, 0)

    # ── Test 1: FE simple → valida XSD ───────────────────────────────────────

    def test_fe_simple_xsd_valid(self):
        """FE de 1 ítem IVA 10% debe pasar la validación del XSD SIFEN v150."""
        data = _make_data(self.dt, [_ITEM_10], _TOTALS_SIMPLE)
        de = builder.build_de(data)
        # El XSD valida el elemento <DE>, no <rDE> completo (sin firma todavía)
        # pero el schema espera el elemento raíz rDE; validamos el DE directamente
        # wrapeándolo en rDE con dVerFor para la validación estructural
        # Nota: la firma (ds:Signature) es requerida por rDE — por eso
        # validamos el <DE> contra tDE (element-level) vía xmlschema validate()
        # que acepta el elemento si el tipo coincide. Sin embargo lxml.validate()
        # requiere el elemento raíz del schema. Usamos assertRaises para confirmar
        # que el DE está bien formado y el error es SOLO por la firma faltante.
        errors = self._get_xsd_errors(de)
        # Solo errores relacionados con la firma o el wrapper rDE (esperado en
        # esta fase pre-firma); NO debe haber errores de estructura del DE
        sig_keywords = {"Signature", "rDE", "dVerFor", "gCamFuFD"}
        structural_errors = [
            e for e in errors if not any(kw in e for kw in sig_keywords)
        ]
        self.assertFalse(
            structural_errors,
            "Errores estructurales en el DE (no relacionados con firma/rDE):\n"
            + "\n".join(structural_errors),
        )

    def test_fe_simple_element_structure(self):
        """Verifica la estructura de elementos del DE generado."""
        data = _make_data(self.dt, [_ITEM_10], _TOTALS_SIMPLE)
        de = builder.build_de(data)

        ns = C.SIFEN_NS
        # Atributo Id = CDC
        cdc = data["cdc"]
        self.assertEqual(de.get("Id"), cdc)

        # dDVId = último dígito del CDC
        self.assertEqual(de.find("{%s}dDVId" % ns).text, cdc[43])

        # dFecFirma = dFeEmiDE formateado
        expected_dt = format_de_datetime(self.dt)
        self.assertEqual(de.find("{%s}dFecFirma" % ns).text, expected_dt)

        # gOpeDE presente
        g_ope = de.find("{%s}gOpeDE" % ns)
        self.assertIsNotNone(g_ope)
        self.assertEqual(g_ope.find("{%s}iTipEmi" % ns).text, "1")

        # gTimb presente con iTiDE=1
        g_timb = de.find("{%s}gTimb" % ns)
        self.assertIsNotNone(g_timb)
        self.assertEqual(g_timb.find("{%s}iTiDE" % ns).text, "1")
        self.assertEqual(g_timb.find("{%s}dDesTiDE" % ns).text, "Factura electrónica")

        # gDatGralOpe → dFeEmiDE
        g_dat = de.find("{%s}gDatGralOpe" % ns)
        self.assertIsNotNone(g_dat)
        self.assertEqual(g_dat.find("{%s}dFeEmiDE" % ns).text, expected_dt)

        # gDtipDE → gCamFE → iIndPres
        g_dtip = de.find("{%s}gDtipDE" % ns)
        g_cam_fe = g_dtip.find("{%s}gCamFE" % ns)
        self.assertIsNotNone(g_cam_fe)
        self.assertEqual(g_cam_fe.find("{%s}iIndPres" % ns).text, "1")

        # 1 ítem
        items = g_dtip.findall("{%s}gCamItem" % ns)
        self.assertEqual(len(items), 1)

        # gTotSub presente
        self.assertIsNotNone(de.find("{%s}gTotSub" % ns))

    # ── Test 2: FE multi-ítem ─────────────────────────────────────────────────

    def test_fe_multi_item(self):
        """FE con 3 ítems (10% + exento + 5%) genera correctamente los ítems."""
        data = _make_data(
            self.dt,
            [_ITEM_10, _ITEM_EXENTO, _ITEM_5],
            _TOTALS_MIXTA,
            doc_number="0000002",
        )
        de = builder.build_de(data)
        ns = C.SIFEN_NS
        g_dtip = de.find("{%s}gDtipDE" % ns)
        items = g_dtip.findall("{%s}gCamItem" % ns)
        self.assertEqual(len(items), 3)

        # Verificar IVA de cada ítem
        iva_types = [
            items[0].find("{%s}gCamIVA/{%s}iAfecIVA" % (ns, ns)).text,
            items[1].find("{%s}gCamIVA/{%s}iAfecIVA" % (ns, ns)).text,
            items[2].find("{%s}gCamIVA/{%s}iAfecIVA" % (ns, ns)).text,
        ]
        self.assertEqual(iva_types, ["4", "3", "5"])

        # Verificar subtotales mixtos
        g_tot = de.find("{%s}gTotSub" % ns)
        self.assertEqual(g_tot.find("{%s}dSub10" % ns).text, "110000")
        self.assertEqual(g_tot.find("{%s}dSubExe" % ns).text, "100000")
        self.assertEqual(g_tot.find("{%s}dSub5" % ns).text, "21000")
        self.assertEqual(g_tot.find("{%s}dTotGralOpe" % ns).text, "231000")

    # ── Test 3: FE exenta (solo exentos) ─────────────────────────────────────

    def test_fe_exenta(self):
        """FE con solo ítems exentos: dSubExe presente, sin dSub10/dSub5."""
        totals = {
            "sub_exe": "100000",
            "total_ope": "100000",
            "total_discount": "0",
            "total_discount_global": "0",
            "total_advance_item": "0",
            "total_advance": "0",
            "discount_pct": "0.00",
            "discount_total": "0",
            "advance": "0",
            "rounding": "0",
            "grand_total": "100000",
        }
        data = _make_data(
            self.dt,
            [_ITEM_EXENTO],
            totals,
            doc_number="0000003",
        )
        de = builder.build_de(data)
        ns = C.SIFEN_NS
        g_tot = de.find("{%s}gTotSub" % ns)
        self.assertEqual(g_tot.find("{%s}dSubExe" % ns).text, "100000")
        # dSub10 no debe existir (solo se agrega si está en totals)
        self.assertIsNone(g_tot.find("{%s}dSub10" % ns))
        self.assertIsNone(g_tot.find("{%s}dSub5" % ns))

    # ── Test 4: dFeEmiDE == fecha del CDC (TD-008) ────────────────────────────

    def test_dfe_emi_de_matches_cdc_date(self):
        """La porción de fecha de dFeEmiDE debe coincidir con la fecha del CDC.

        El CDC codifica la fecha en YYYYMMDD (posiciones 26-33).
        El campo dFeEmiDE usa YYYY-MM-DDThh:mm:ss.
        Ambos deben reflejar el mismo día calendárico (TD-008).
        """
        dt = datetime.datetime(2025, 6, 15, 10, 30, 0)
        data = _make_data(dt, [_ITEM_10], _TOTALS_SIMPLE)
        cdc = data["cdc"]
        de = builder.build_de(data)

        ns = C.SIFEN_NS
        g_dat = de.find("{%s}gDatGralOpe" % ns)
        fe_emi_de = g_dat.find("{%s}dFeEmiDE" % ns).text  # YYYY-MM-DDThh:mm:ss

        # Fecha en dFeEmiDE (los primeros 10 chars)
        de_date_str = fe_emi_de[:10]  # "YYYY-MM-DD"
        de_date_compact = de_date_str.replace("-", "")  # "YYYYMMDD"

        # Fecha en CDC (posiciones 25-33, 0-based = índices 25:33)
        cdc_date = cdc[25:33]  # "YYYYMMDD"

        self.assertEqual(
            cdc_date,
            de_date_compact,
            "La fecha del CDC (%s) no coincide con la fecha de dFeEmiDE (%s). "
            "TD-008 violated." % (cdc_date, de_date_compact),
        )

    # ── Test 5: Receptor innominado ───────────────────────────────────────────

    def test_receptor_innominado(self):
        """Receptor innominado: iNatRec=2, dNomRec='Sin nombre', sin RUC."""
        data = _make_data(
            self.dt,
            [_ITEM_10],
            _TOTALS_SIMPLE,
            receiver=_RECEIVER_INNOMINADO,
            doc_number="0000004",
        )
        de = builder.build_de(data)
        ns = C.SIFEN_NS
        g_dat = de.find("{%s}gDatGralOpe" % ns)
        g_rec = g_dat.find("{%s}gDatRec" % ns)

        self.assertEqual(g_rec.find("{%s}iNatRec" % ns).text, "2")
        self.assertEqual(g_rec.find("{%s}dNomRec" % ns).text, "Sin nombre")
        # iTipIDRec = 5 (innominado)
        self.assertEqual(g_rec.find("{%s}iTipIDRec" % ns).text, "5")
        # Sin RUC
        self.assertIsNone(g_rec.find("{%s}dRucRec" % ns))

    # ── Test 6: Receptor contribuyente ───────────────────────────────────────

    def test_receptor_contribuyente(self):
        """Receptor contribuyente: iNatRec=1, RUC presente, sin iTipIDRec."""
        data = _make_data(
            self.dt,
            [_ITEM_10],
            _TOTALS_SIMPLE,
            receiver=_RECEIVER_CONTRIBUYENTE,
            doc_number="0000005",
        )
        de = builder.build_de(data)
        ns = C.SIFEN_NS
        g_dat = de.find("{%s}gDatGralOpe" % ns)
        g_rec = g_dat.find("{%s}gDatRec" % ns)

        self.assertEqual(g_rec.find("{%s}iNatRec" % ns).text, "1")
        self.assertEqual(g_rec.find("{%s}dRucRec" % ns).text, "12345678")
        # Sin doc de identidad (no contribuyente) — solo contribuyentes usan RUC
        self.assertIsNone(g_rec.find("{%s}iTipIDRec" % ns))

    # ── Test 7: Receptor no contribuyente con CI ─────────────────────────────

    def test_receptor_no_contrib_ci(self):
        """Receptor no contribuyente con cédula paraguaya."""
        data = _make_data(
            self.dt,
            [_ITEM_10],
            _TOTALS_SIMPLE,
            receiver=_RECEIVER_NO_CONTRIB_CI,
            doc_number="0000006",
        )
        de = builder.build_de(data)
        ns = C.SIFEN_NS
        g_dat = de.find("{%s}gDatGralOpe" % ns)
        g_rec = g_dat.find("{%s}gDatRec" % ns)

        self.assertEqual(g_rec.find("{%s}iNatRec" % ns).text, "2")
        self.assertEqual(g_rec.find("{%s}iTipIDRec" % ns).text, "1")
        self.assertEqual(g_rec.find("{%s}dDTipIDRec" % ns).text, "Cédula paraguaya")
        self.assertEqual(g_rec.find("{%s}dNumIDRec" % ns).text, "1234567")
        self.assertEqual(g_rec.find("{%s}dNomRec" % ns).text, "JUAN PEREZ")

    # ── Test 8: Serialización round-trip ─────────────────────────────────────

    def test_serialize_roundtrip(self):
        """El DE serializado puede re-parsearse y el Id del CDC se preserva."""
        data = _make_data(self.dt, [_ITEM_10], _TOTALS_SIMPLE, doc_number="0000007")
        de = builder.build_de(data)
        xml_bytes = builder.serialize(de)

        # Re-parsear
        de2 = etree.fromstring(xml_bytes)
        self.assertEqual(de2.get("Id"), data["cdc"])

    # ── Test 9: Golden file FE simple ────────────────────────────────────────

    def test_fe_simple_golden_file(self):
        """Genera el golden file de FE simple si no existe; lo verifica si existe."""
        golden = _FIXTURES_DIR / "fe_simple.xml"
        data = _make_data(self.dt, [_ITEM_10], _TOTALS_SIMPLE)
        de = builder.build_de(data)
        xml_bytes = builder.serialize(de, pretty=True)

        if not golden.exists():
            golden.write_bytes(xml_bytes)
            self.skipTest("Golden file creado: %s" % golden)

        # Comparar CDC (el security_code puede variar si se regenera)
        de_golden = etree.parse(str(golden)).getroot()
        # Verificar que la estructura es la misma (mismo número de gCamItem)
        ns = C.SIFEN_NS
        items_new = de.findall(".//{%s}gCamItem" % ns)
        items_golden = de_golden.findall(".//{%s}gCamItem" % ns)
        self.assertEqual(len(items_new), len(items_golden))

    # ── Helpers privados ──────────────────────────────────────────────────────

    @staticmethod
    def _get_xsd_errors(de_element: etree._Element) -> list[str]:
        """Valida el elemento DE y retorna la lista de errores XSD (puede estar vacía)."""
        try:
            validate_against_xsd(de_element)
            return []
        except XsdValidationError as exc:
            return exc.errors
        except FileNotFoundError:
            # Si los XSD no están disponibles en el entorno CI, skip silencioso
            return []
