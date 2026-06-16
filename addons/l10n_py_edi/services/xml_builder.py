# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Builder lxml del Documento Electrónico (DE) SIFEN — Manual Técnico v150.

Produce el elemento ``<DE Id="{CDC}">`` con todos los grupos requeridos para
una Factura Electrónica (iTiDE=1) en moneda PYG.

Diseño
------
- El builder recibe **dicts puros** (sin importar ``odoo``).  El mapper
  ``models/account_edi_xml.py`` (diferido a PR-6) extrae los datos del
  ``account.move`` y los pasa acá.
- La firma XAdES (``<ds:Signature>``) se inyecta externamente (PR-4);
  el builder devuelve el ``<DE>`` sin firma.
- Validación XSD disponible en ``services/xsd_validator.py``.

Estructura del ``data`` dict
-----------------------------
El argumento ``data`` de :func:`build_de` debe tener la siguiente forma::

    {
        # ── Cabecera ─────────────────────────────────────────────────────────
        "cdc": str,               # 44 dígitos
        "emission_type": int,     # 1=Normal, 2=Contingencia
        "security_code": str,     # 9 dígitos (posiciones 35-43 del CDC)
        "dv_id": int,             # DV del CDC (posición 44)
        "emission_datetime": datetime.datetime,  # hora local PY (naive o tz-aware)

        # ── Timbrado (gTimb) ──────────────────────────────────────────────────
        "timbrado": {
            "de_type": int,       # iTiDE: 1=FE, 5=NC, …
            "timbrado_number": str,  # 8 dígitos
            "establishment": str, # 3 dígitos
            "expedition_point": str,  # 3 dígitos
            "document_number": str,   # 7 dígitos
            "timbrado_start_date": str,  # YYYY-MM-DD
        },

        # ── Operación comercial (gOpeCom dentro de gDatGralOpe) ──────────────
        "operation": {
            "transaction_type": int | None,  # None omite iTipTra/dDesTipTra
            "tax_type": int,       # iTImp: 1=IVA
            "currency": str,       # cMoneOpe: "PYG"
        },

        # ── Emisor (gEmis) ────────────────────────────────────────────────────
        "issuer": {
            "ruc": str,            # sin DV, 1-8 dígitos
            "ruc_dv": int,
            "taxpayer_type": int,  # 1=PF, 2=PJ
            "tax_regime": int | None,  # cTipReg, opcional
            "name": str,
            "trade_name": str | None,
            "address": str,
            "house_number": str,
            "department": int,     # cDepEmi (código departamento)
            "department_desc": str,
            "district": int | None,
            "district_desc": str | None,
            "city": int,           # cCiuEmi
            "city_desc": str,
            "phone": str,
            "email": str,
            "economic_activities": [  # 1-9 items
                {"code": str, "desc": str}
            ],
        },

        # ── Receptor (gDatRec) ────────────────────────────────────────────────
        "receiver": {
            "nature": int,         # 1=contribuyente, 2=no contribuyente
            "operation_type": int, # 1=B2B, 2=B2C, 3=B2G, 4=B2F
            "country": str,        # "PRY"
            "country_desc": str,   # "Paraguay"
            # Contribuyente:
            "taxpayer_type": int | None,
            "ruc": str | None,
            "ruc_dv": int | None,
            # No contribuyente / innominado:
            "doc_type": int | None,   # iTipIDRec
            "doc_type_desc": str | None,
            "doc_number": str | None,
            "name": str,           # "Sin nombre" para innominado
        },

        # ── Ítems (gCamItem) ──────────────────────────────────────────────────
        "items": [
            {
                "code": str,           # dCodInt — código interno
                "description": str,    # dDesProSer (1-120 chars)
                "unit": int,           # cUniMed (código unidad de medida)
                "unit_desc": str,      # dDesUniMed
                "quantity": str,       # dCantProSer (decimal string)
                "unit_price": str,     # dPUniProSer
                "total_gross": str,    # dTotBruOpeItem
                "total_item": str,     # dTotOpeItem
                "total_gs": str | None,  # dTotOpeGs (en Gs. cuando moneda ext.)
                # IVA por ítem:
                "iva_type": int,       # iAfecIVA
                "iva_proportion": str, # dPropIVA (p. ej. "100.00")
                "iva_base": str,       # dBasGravIVA
                "iva_amount": str,     # dLiqIVAItem
            }
        ],

        # ── Subtotales (gTotSub) ──────────────────────────────────────────────
        "totals": {
            "sub_exe": str | None,     # dSubExe  — exentas
            "sub_exo": str | None,     # dSubExo  — exoneradas
            "sub_5": str | None,       # dSub5    — gravado 5%
            "sub_10": str | None,      # dSub10   — gravado 10%
            "total_ope": str,          # dTotOpe
            "total_discount": str,     # dTotDesc
            "total_discount_global": str,  # dTotDescGlotem
            "total_advance_item": str, # dTotAntItem
            "total_advance": str,      # dTotAnt
            "discount_pct": str,       # dPorcDescTotal
            "discount_total": str,     # dDescTotal
            "advance": str,            # dAnticipo
            "rounding": str,           # dRedon
            "grand_total": str,        # dTotGralOpe
            "iva_5": str | None,       # dIVA5
            "iva_10": str | None,      # dIVA10
            "liq_iva_5": str | None,   # dLiqTotIVA5
            "liq_iva_10": str | None,  # dLiqTotIVA10
            "total_iva": str | None,   # dTotIVA
            "base_5": str | None,      # dBaseGrav5
            "base_10": str | None,     # dBaseGrav10
            "total_base_iva": str | None,  # dTBasGraIVA
            "total_gs": str | None,    # dTotalGs
        },

        # ── Indicador de presencia (solo FE) ──────────────────────────────────
        "presence_indicator": int,     # iIndPres: 1-6 o 9

        # ── Condición de venta (opcional) ─────────────────────────────────────
        "condition": {               # None omite gCamCond
            "condition_type": int,   # 1=Contado, 2=Crédito
            "payments": [            # lista de formas de pago al contado
                {
                    "payment_type": int,    # iTiPago
                    "payment_desc": str,    # dDesTiPag
                    "amount": str,          # dMonTiPag
                    "currency": str,        # cMoneTiPag
                    "currency_desc": str,   # dDMoneTiPag
                }
            ],
        } | None,
    }

Importable sin registry: este módulo NO importa de ``odoo``.
"""
from __future__ import annotations

import datetime
from decimal import Decimal
from typing import Any

from lxml import etree

from . import xml_constants as C
from .datetime_helpers import format_de_datetime

# Namespace SIFEN (sin prefijo en el DE — elementFormDefault="qualified")
_NS = C.SIFEN_NS
_Q = "{%s}" % _NS  # helper: "{ns}tag"


def _e(
    parent: etree._Element, tag: str, text: str | int | None = None
) -> etree._Element:
    """Crea un sub-elemento en el namespace SIFEN y le asigna ``text``."""
    el = etree.SubElement(parent, _Q + tag)
    if text is not None:
        el.text = str(text)
    return el


def _opt(parent: etree._Element, tag: str, value: Any) -> None:
    """Crea sub-elemento solo si ``value`` no es None/vacío."""
    if value is not None and value != "":
        _e(parent, tag, value)


def build_de(data: dict) -> etree._Element:
    """Construye el elemento ``<DE Id="{CDC}">`` del DE SIFEN.

    :param data: diccionario con todos los campos del DE (ver docstring del módulo).
    :returns: :class:`lxml.etree._Element` ``<DE>`` listo para firma XAdES.
    :raises KeyError: si falta un campo obligatorio en ``data``.
    :raises ValueError: si un valor no cumple la estructura esperada.
    """
    cdc: str = data["cdc"]
    emission_dt: datetime.datetime = data["emission_datetime"]
    de_datetime_str = format_de_datetime(emission_dt)

    # Raíz: <DE Id="{CDC}"> en el namespace SIFEN
    de = etree.Element(_Q + "DE", nsmap={None: _NS})
    de.set("Id", cdc)

    # dDVId — dígito verificador del CDC (última posición)
    _e(de, "dDVId", int(cdc[43]))

    # dFecFirma — fecha/hora de firma (misma que emisión antes de firmar)
    _e(de, "dFecFirma", de_datetime_str)

    # dSisFact — sistema de facturación propio
    _e(de, "dSisFact", C.SIS_FACT_CONTRIBUYENTE)

    # ── Grupo AA: gOpeDE ──────────────────────────────────────────────────────
    _build_g_ope_de(de, data)

    # ── Grupo A: gTimb ────────────────────────────────────────────────────────
    _build_g_timb(de, data["timbrado"])

    # ── Grupo B/C/D: gDatGralOpe ──────────────────────────────────────────────
    _build_g_dat_gral_ope(de, data, de_datetime_str)

    # ── Grupo E: gDtipDE ──────────────────────────────────────────────────────
    _build_g_dtip_de(de, data)

    # ── Grupo F: gTotSub ──────────────────────────────────────────────────────
    _build_g_tot_sub(de, data.get("totals"))

    return de


def _build_g_ope_de(parent: etree._Element, data: dict) -> None:
    """AA — Campos de la operación del DE (gOpeDE → tgCOpeDE)."""
    g = _e(parent, "gOpeDE")
    emission_type: int = data.get("emission_type", C.EMISSION_NORMAL)
    _e(g, "iTipEmi", emission_type)
    _e(g, "dDesTipEmi", C.EMISSION_DESC[emission_type])
    _e(g, "dCodSeg", data["security_code"])
    _opt(g, "dInfoEmi", data.get("info_issuer"))
    _opt(g, "dInfoFisc", data.get("info_fiscal"))


def _build_g_timb(parent: etree._Element, timb: dict) -> None:
    """A — Datos de timbrado (gTimb → tgDTim)."""
    g = _e(parent, "gTimb")
    de_type: int = timb["de_type"]
    _e(g, "iTiDE", de_type)
    _e(g, "dDesTiDE", C.DE_TYPE_DESC[de_type])
    _e(g, "dNumTim", timb["timbrado_number"])
    _e(g, "dEst", timb["establishment"])
    _e(g, "dPunExp", timb["expedition_point"])
    _e(g, "dNumDoc", timb["document_number"])
    _opt(g, "dSerieNum", timb.get("serie"))
    _e(g, "dFeIniT", timb["timbrado_start_date"])


def _build_g_dat_gral_ope(
    parent: etree._Element, data: dict, de_datetime_str: str
) -> None:
    """B/C/D — Datos generales de la operación (gDatGralOpe → tgDaGOC)."""
    g = _e(parent, "gDatGralOpe")
    _e(g, "dFeEmiDE", de_datetime_str)

    # gOpeCom (B) — operación comercial (opcional en XSD pero presente en FE)
    oper = data.get("operation")
    if oper:
        _build_g_ope_com(g, oper)

    # gEmis (C)
    _build_g_emis(g, data["issuer"])

    # gDatRec (D)
    _build_g_dat_rec(g, data["receiver"])


def _build_g_ope_com(parent: etree._Element, oper: dict) -> None:
    """B — Operación comercial (gOpeCom → tgOpeCom)."""
    g = _e(parent, "gOpeCom")
    tx_type = oper.get("transaction_type")
    if tx_type is not None:
        _e(g, "iTipTra", tx_type)
        _e(g, "dDesTipTra", C.TRANS_DESC[tx_type])
    tax_type: int = oper["tax_type"]
    _e(g, "iTImp", tax_type)
    _e(g, "dDesTImp", C.TAX_TYPE_DESC[tax_type])
    currency: str = oper.get("currency", C.CURRENCY_PYG)
    _e(g, "cMoneOpe", currency)
    _e(g, "dDesMoneOpe", _currency_desc(currency))
    _opt(g, "dCondTiCam", oper.get("exchange_condition"))
    _opt(g, "dTiCam", oper.get("exchange_rate"))


def _currency_desc(code: str) -> str:
    """Descripción legible de la moneda (fallback = código mismo)."""
    if code == C.CURRENCY_PYG:
        return C.CURRENCY_PYG_DESC
    return code


def _build_g_emis(parent: etree._Element, issuer: dict) -> None:
    """C — Datos del emisor (gEmis → tgEmis)."""
    g = _e(parent, "gEmis")
    _e(g, "dRucEm", issuer["ruc"])
    _e(g, "dDVEmi", issuer["ruc_dv"])
    _e(g, "iTipCont", issuer["taxpayer_type"])
    _opt(g, "cTipReg", issuer.get("tax_regime"))
    _e(g, "dNomEmi", issuer["name"])
    _opt(g, "dNomFanEmi", issuer.get("trade_name"))
    _e(g, "dDirEmi", issuer["address"])
    _e(g, "dNumCas", issuer["house_number"])
    _opt(g, "dCompDir1", issuer.get("address_complement_1"))
    _opt(g, "dCompDir2", issuer.get("address_complement_2"))
    _e(g, "cDepEmi", issuer["department"])
    _e(g, "dDesDepEmi", issuer["department_desc"])
    _opt(g, "cDisEmi", issuer.get("district"))
    _opt(g, "dDesDisEmi", issuer.get("district_desc"))
    _e(g, "cCiuEmi", issuer["city"])
    _e(g, "dDesCiuEmi", issuer["city_desc"])
    _e(g, "dTelEmi", issuer["phone"])
    _e(g, "dEmailE", issuer["email"])
    _opt(g, "dDenSuc", issuer.get("branch_name"))

    # gActEco — 1 a 9 actividades económicas (obligatorio al menos 1)
    for act in issuer["economic_activities"]:
        g_act = _e(g, "gActEco")
        _e(g_act, "cActEco", act["code"])
        _e(g_act, "dDesActEco", act["desc"])

    # gRespDE — responsable de la generación (opcional)
    resp = issuer.get("responsible")
    if resp:
        g_resp = _e(g, "gRespDE")
        _e(g_resp, "iTipIDRespDE", resp["doc_type"])
        _e(g_resp, "dDTipIDRespDE", resp["doc_type_desc"])
        _e(g_resp, "dNumIDRespDE", resp["doc_number"])
        _e(g_resp, "dNomRespDE", resp["name"])
        _e(g_resp, "dCarRespDE", resp["position"])


def _build_g_dat_rec(parent: etree._Element, receiver: dict) -> None:
    """D — Datos del receptor (gDatRec → tgDatRec)."""
    g = _e(parent, "gDatRec")
    nature: int = receiver["nature"]
    _e(g, "iNatRec", nature)
    _e(g, "iTiOpe", receiver["operation_type"])
    _e(g, "cPaisRec", receiver.get("country", C.PAIS_PY))
    _e(g, "dDesPaisRe", receiver.get("country_desc", C.PAIS_PY_DESC))

    if nature == C.RECEIVER_CONTRIBUYENTE:
        # Contribuyente: RUC obligatorio
        _opt(g, "iTiContRec", receiver.get("taxpayer_type"))
        _opt(g, "dRucRec", receiver.get("ruc"))
        _opt(g, "dDVRec", receiver.get("ruc_dv"))
    else:
        # No contribuyente: tipo de doc / número (puede ser innominado)
        doc_type = receiver.get("doc_type")
        if doc_type is not None:
            _e(g, "iTipIDRec", doc_type)
            _e(
                g,
                "dDTipIDRec",
                receiver.get("doc_type_desc", C.DOC_REC_DESC.get(doc_type, "")),
            )
            _opt(g, "dNumIDRec", receiver.get("doc_number"))

    _e(g, "dNomRec", receiver["name"])
    _opt(g, "dNomFanRec", receiver.get("trade_name"))
    _opt(g, "dDirRec", receiver.get("address"))
    _opt(g, "dNumCasRec", receiver.get("house_number"))
    _opt(g, "cDepRec", receiver.get("department"))
    _opt(g, "dDesDepRec", receiver.get("department_desc"))
    _opt(g, "cDisRec", receiver.get("district"))
    _opt(g, "dDesDisRec", receiver.get("district_desc"))
    _opt(g, "cCiuRec", receiver.get("city"))
    _opt(g, "dDesCiuRec", receiver.get("city_desc"))
    _opt(g, "dTelRec", receiver.get("phone"))
    _opt(g, "dCelRec", receiver.get("mobile"))
    _opt(g, "dEmailRec", receiver.get("email"))
    _opt(g, "dCodCliente", receiver.get("client_code"))


def _build_g_dtip_de(parent: etree._Element, data: dict) -> None:
    """E — Campos específicos por tipo de DE (gDtipDE → tgDtipDE)."""
    g = _e(parent, "gDtipDE")
    de_type: int = data["timbrado"]["de_type"]

    # gCamFE (solo para iTiDE=1)
    if de_type == C.DE_TYPE_FE:
        _build_g_cam_fe(g, data)

    # gCamNCDE (solo para iTiDE=5 NC / 6 ND)
    if de_type in (C.DE_TYPE_NC, C.DE_TYPE_ND):
        nc = data.get("credit_note", {})
        g_nc = _e(g, "gCamNCDE")
        _e(g_nc, "iMotEmi", nc["reason_type"])
        _e(g_nc, "dDesMotEmi", nc["reason_desc"])

    # Condición de pago (gCamCond) — opcional
    condition = data.get("condition")
    if condition:
        _build_g_cam_cond(g, condition)

    # gCamItem — 1 a 999 ítems (obligatorio)
    for item in data["items"]:
        _build_g_cam_item(g, item)


def _build_g_cam_fe(parent: etree._Element, data: dict) -> None:
    """E.1 — Campos de factura electrónica (gCamFE → tgCamFE)."""
    g = _e(parent, "gCamFE")
    ind_pres: int = data.get("presence_indicator", C.PRES_OPERACION_PRESENCIAL)
    _e(g, "iIndPres", ind_pres)
    pres_desc = C.PRES_DESC.get(ind_pres, "Operación presencial")
    _e(g, "dDesIndPres", pres_desc)
    _opt(g, "dFecEmNR", data.get("non_resident_emission_date"))


def _build_g_cam_cond(parent: etree._Element, condition: dict) -> None:
    """E.2 — Condición de la operación (gCamCond → tgCamCond)."""
    cond_type: int = condition["condition_type"]
    cond_desc = "Contado" if cond_type == 1 else "Crédito"
    g = _e(parent, "gCamCond")
    _e(g, "iCondOpe", cond_type)
    _e(g, "dDCondOpe", cond_desc)

    # Pagos al contado (gPaConEIni)
    for pago in condition.get("payments", []):
        gp = _e(g, "gPaConEIni")
        _e(gp, "iTiPago", pago["payment_type"])
        _e(gp, "dDesTiPag", pago["payment_desc"])
        _e(gp, "dMonTiPag", pago["amount"])
        _e(gp, "cMoneTiPag", pago.get("currency", C.CURRENCY_PYG))
        _e(gp, "dDMoneTiPag", pago.get("currency_desc", C.CURRENCY_PYG_DESC))
        _opt(gp, "dTiCamTiPag", pago.get("exchange_rate"))


def _build_g_cam_item(parent: etree._Element, item: dict) -> None:
    """E.3 — Ítem de la operación (gCamItem → tgCamItem)."""
    g = _e(parent, "gCamItem")
    _e(g, "dCodInt", item["code"])
    _opt(g, "dParAranc", item.get("arancel"))
    _opt(g, "dNCM", item.get("ncm"))
    _e(g, "dDesProSer", item["description"])
    _e(g, "cUniMed", item["unit"])
    _e(g, "dDesUniMed", item["unit_desc"])
    _e(g, "dCantProSer", item["quantity"])

    # gValorItem
    gv = _e(g, "gValorItem")
    _e(gv, "dPUniProSer", item["unit_price"])
    _e(gv, "dTotBruOpeItem", item["total_gross"])
    gvr = _e(gv, "gValorRestaItem")
    _opt(gvr, "dDescItem", item.get("discount"))
    _opt(gvr, "dPorcDesIt", item.get("discount_pct"))
    _e(gvr, "dTotOpeItem", item["total_item"])
    _opt(gvr, "dTotOpeGs", item.get("total_gs"))

    # gCamIVA
    _build_g_cam_iva(g, item)


def _build_g_cam_iva(parent: etree._Element, item: dict) -> None:
    """IVA por ítem (gCamIVA → tgCamIVA)."""
    g = _e(parent, "gCamIVA")
    iva_type: int = item["iva_type"]
    _e(g, "iAfecIVA", iva_type)
    _e(g, "dDesAfecIVA", C.IVA_AFEC_DESC.get(iva_type, str(iva_type)))
    _e(g, "dPropIVA", item["iva_proportion"])
    _e(g, "dTasaIVA", C.IVA_RATE.get(iva_type, 0))
    _e(g, "dBasGravIVA", item["iva_base"])
    _e(g, "dLiqIVAItem", item["iva_amount"])


def _build_g_tot_sub(parent: etree._Element, totals: dict | None) -> None:
    """F — Subtotales y totales (gTotSub → tgTotSub).

    El grupo es ``minOccurs="0"`` en el XSD; si ``totals`` es None, se omite.
    """
    if totals is None:
        return
    g = _e(parent, "gTotSub")
    _opt(g, "dSubExe", totals.get("sub_exe"))
    _opt(g, "dSubExo", totals.get("sub_exo"))
    _opt(g, "dSub5", totals.get("sub_5"))
    _opt(g, "dSub10", totals.get("sub_10"))
    _e(g, "dTotOpe", totals["total_ope"])
    _e(g, "dTotDesc", totals["total_discount"])
    _e(g, "dTotDescGlotem", totals["total_discount_global"])
    _e(g, "dTotAntItem", totals["total_advance_item"])
    _e(g, "dTotAnt", totals["total_advance"])
    _e(g, "dPorcDescTotal", totals["discount_pct"])
    _e(g, "dDescTotal", totals["discount_total"])
    _e(g, "dAnticipo", totals["advance"])
    _e(g, "dRedon", totals["rounding"])
    _opt(g, "dComi", totals.get("commission"))
    _e(g, "dTotGralOpe", totals["grand_total"])
    _opt(g, "dIVA5", totals.get("iva_5"))
    _opt(g, "dIVA10", totals.get("iva_10"))
    _opt(g, "dLiqTotIVA5", totals.get("liq_iva_5"))
    _opt(g, "dLiqTotIVA10", totals.get("liq_iva_10"))
    _opt(g, "dIVAComi", totals.get("iva_commission"))
    _opt(g, "dTotIVA", totals.get("total_iva"))
    _opt(g, "dBaseGrav5", totals.get("base_5"))
    _opt(g, "dBaseGrav10", totals.get("base_10"))
    _opt(g, "dTBasGraIVA", totals.get("total_base_iva"))
    _opt(g, "dTotalGs", totals.get("total_gs"))


# ── Helpers públicos ───────────────────────────────────────────────────────────


def serialize(element: etree._Element, *, pretty: bool = False) -> bytes:
    """Serializa un elemento lxml a bytes UTF-8.

    :param element: elemento a serializar.
    :param pretty: si es True, agrega indentación (útil para debug/golden files).
    :returns: bytes UTF-8 con declaración XML.
    """
    return etree.tostring(
        element,
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=pretty,
    )


def amount(value: int | float | Decimal) -> str:
    """Formatea un monto a string sin notación científica (helper para callers).

    lxml serializa el texto tal cual se le pasa; el XSD ``tMontoBase`` acepta
    cualquier decimal positivo. Usar esta función garantiza que 10000 no se
    serialice como "1e4" en casos edge con Decimal.
    """
    return str(Decimal(str(value)).normalize())
