# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Constantes XML para el DE SIFEN (Manual Técnico v150).

Namespace, versión de formato y tablas de código → descripción extraídas
directamente de DE_Types_v150.xsd y DE_v150.xsd (verificados contra el XSD
oficial, no contra docs/01-02 que son resúmenes).

Importable sin registry: este módulo NO importa de ``odoo``.
"""

# ── Namespace / versión ────────────────────────────────────────────────────────

SIFEN_NS = "http://ekuatia.set.gov.py/sifen/xsd"
SIFEN_VER_FOR = "150"  # dVerFor — único valor válido en el XSD: pattern [1][5][0]

# ── Tipos de DE (iTiDE / dDesTiDE) ────────────────────────────────────────────
# XSD: tiTiDE pattern "1|[4-7]"

DE_TYPE_FE = 1  # Factura electrónica
DE_TYPE_AE = 4  # Autofactura electrónica
DE_TYPE_NC = 5  # Nota de crédito electrónica
DE_TYPE_ND = 6  # Nota de débito electrónica
DE_TYPE_NR = 7  # Nota de remisión electrónica

DE_TYPE_DESC: dict[int, str] = {
    DE_TYPE_FE: "Factura electrónica",
    DE_TYPE_AE: "Autofactura electrónica",
    DE_TYPE_NC: "Nota de crédito electrónica",
    DE_TYPE_ND: "Nota de débito electrónica",
    DE_TYPE_NR: "Nota de remisión electrónica",
}

# ── Tipo de emisión (iTipEmi / dDesTipEmi) ────────────────────────────────────
# XSD: tiTipEmi pattern "[1-2]"

EMISSION_NORMAL = 1  # Normal
EMISSION_CONTINGENCY = 2  # Contingencia

EMISSION_DESC: dict[int, str] = {
    EMISSION_NORMAL: "Normal",
    EMISSION_CONTINGENCY: "Contingencia",
}

# ── Tipo de impuesto (iTImp / dDesTImp) ───────────────────────────────────────
# XSD: tiTImp enumeration 1-5

TAX_TYPE_IVA = 1
TAX_TYPE_ISC = 2
TAX_TYPE_RENTA = 3
TAX_TYPE_NINGUNO = 4
TAX_TYPE_IVA_RENTA = 5

TAX_TYPE_DESC: dict[int, str] = {
    TAX_TYPE_IVA: "IVA",
    TAX_TYPE_ISC: "ISC",
    TAX_TYPE_RENTA: "Renta",
    TAX_TYPE_NINGUNO: "Ninguno",
    TAX_TYPE_IVA_RENTA: "IVA – Renta",  # "IVA – Renta" (guión largo)
}

# ── Moneda (cMoneOpe) ─────────────────────────────────────────────────────────
# XSD: cMondT — verificado en Monedas_v150.xsd (enumeración ISO 4217)

CURRENCY_PYG = "PYG"
CURRENCY_PYG_DESC = "Guaraní"

# ── Tipo de contribuyente (iTipCont) ──────────────────────────────────────────
# XSD: tiTipCont pattern "[1-2]"

TAXPAYER_PF = 1  # Persona Física
TAXPAYER_PJ = 2  # Persona Jurídica

TAXPAYER_DESC: dict[int, str] = {
    TAXPAYER_PF: "Persona física",
    TAXPAYER_PJ: "Persona jurídica",
}

# ── Naturaleza del receptor (iNatRec) ─────────────────────────────────────────
# XSD: tiNatRec pattern "[1-2]"

RECEIVER_CONTRIBUYENTE = 1  # Contribuyente
RECEIVER_NO_CONTRIBUYENTE = 2  # No Contribuyente

# ── Tipo de operación (iTiOpe) ────────────────────────────────────────────────
# XSD: tiTiOpe pattern "[1-4]"

OPER_B2B = 1
OPER_B2C = 2
OPER_B2G = 3
OPER_B2F = 4

# ── Indicador de presencia (iIndPres) ─────────────────────────────────────────
# XSD: tiIndPres pattern "[1-6]|9"

PRES_OPERACION_PRESENCIAL = 1
PRES_OPERACION_ELECTRONICA = 2
PRES_TELEMARKETING = 3
PRES_VENTA_DOMICILIO = 4
PRES_OPERACION_BANCARIA = 5
PRES_OPERACION_CICLICA = 6
PRES_OTRO = 9

PRES_DESC: dict[int, str] = {
    PRES_OPERACION_PRESENCIAL: "Operación presencial",
    PRES_OPERACION_ELECTRONICA: "Operación electrónica",
    PRES_TELEMARKETING: "Operación telemarketing",
    PRES_VENTA_DOMICILIO: "Venta a domicilio",
    PRES_OPERACION_BANCARIA: "Operación bancaria",
    PRES_OPERACION_CICLICA: "Operación cíclica",
}

# ── Tipo de transacción (iTipTra) ─────────────────────────────────────────────
# XSD: tiTipTra 1-13

TRANS_VENTA_MERCADERIA = 1
TRANS_PRESTACION_SERVICIOS = 2
TRANS_MIXTO = 3

TRANS_DESC: dict[int, str] = {
    1: "Venta de mercadería",
    2: "Prestación de servicios",
    3: "Mixto (Venta de mercadería y servicios)",
    4: "Venta de activo fijo",
    5: "Venta de divisas",
    6: "Compra de divisas",
    7: "Promoción o entrega de muestras",
    8: "Donación",
    9: "Anticipo",
    10: "Compra de productos",
    11: "Compra de servicios",
    12: "Venta de crédito fiscal",
    13: "Muestras médicas (Art. 3 RG 24/2014)",
}

# ── Afectación IVA por ítem (iAfecIVA) ───────────────────────────────────────
# Verificar con DE_Types_v150.xsd tiAfecIVA

IVA_GRAVADO_PARCIAL = 1  # Gravado parcial (Ley 125/91 Art. 43 num 2)
IVA_EXONERADO = 2  # Exonerado (Art. 100 Ley 6380/19)
IVA_EXENTO = 3  # Exento
IVA_GRAVADO_10 = 4  # Gravado al 10%
IVA_GRAVADO_5 = 5  # Gravado al 5%

IVA_AFEC_DESC: dict[int, str] = {
    IVA_GRAVADO_PARCIAL: "Gravado parcial",
    IVA_EXONERADO: "Exonerado",
    IVA_EXENTO: "Exento",
    IVA_GRAVADO_10: "Gravado IVA 10%",
    IVA_GRAVADO_5: "Gravado IVA 5%",
}

# Tasa IVA por código de afectación
IVA_RATE: dict[int, int] = {
    IVA_GRAVADO_PARCIAL: 0,
    IVA_EXONERADO: 0,
    IVA_EXENTO: 0,
    IVA_GRAVADO_10: 10,
    IVA_GRAVADO_5: 5,
}

# ── Sistema de facturación (dSisFact) ─────────────────────────────────────────
SIS_FACT_CONTRIBUYENTE = 1  # Sistema propio del contribuyente
SIS_FACT_SIFEN_GRATUITO = 2  # SIFEN solución gratuita

# ── País PY ───────────────────────────────────────────────────────────────────
PAIS_PY = "PRY"
PAIS_PY_DESC = "Paraguay"

# ── Tipo de documento de identidad del receptor (iTipIDRec) ───────────────────
# XSD: tiTipDocRec pattern "[1-6]|9"

DOC_REC_CEDULA_PY = 1
DOC_REC_PASAPORTE = 2
DOC_REC_CEDULA_EXT = 3
DOC_REC_CARNET_RES = 4
DOC_REC_INNOMINADO = 5
DOC_REC_TARJ_DIPLOM = 6
DOC_REC_OTRO = 9

DOC_REC_DESC: dict[int, str] = {
    DOC_REC_CEDULA_PY: "Cédula paraguaya",
    DOC_REC_PASAPORTE: "Pasaporte",
    DOC_REC_CEDULA_EXT: "Cédula extranjera",
    DOC_REC_CARNET_RES: "Carnet de residencia",
    DOC_REC_INNOMINADO: "Innominado",
    DOC_REC_TARJ_DIPLOM: "Tarjeta Diplomática de exoneración fiscal",
}
