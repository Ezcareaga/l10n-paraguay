#!/usr/bin/env python3
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later
"""Extrae el Plan de Cuentas paraguayo desde el XLS oficial DNIT RG 49/14.

Genera 2 CSVs en formato Odoo 18:
  - addons/l10n_py_account/data/template/account.group-py.csv
  - addons/l10n_py_account/data/template/account.account-py.csv

Schema de salida (account.account):
    id,code,name,account_type,reconcile,non_trade

Convención de XML IDs: ``py_<código_sin_puntos>``.

Subset activo por default (~80 cuentas): definido en ACTIVE_CODES abajo.
Resto: ``active=False`` por default (las crea el chart template).

Uso:
    python scripts/extract_puc_rg49.py
"""
import csv
import re
import sys
from pathlib import Path

import xlrd

ROOT = Path(__file__).resolve().parents[1]
XLS_PATH = ROOT / "data" / "catalogs" / "_verification" / "dnit_rg_49_14_anexos.xls"
OUT_DIR = ROOT / "addons" / "l10n_py_account" / "data" / "template"

# Códigos RG 49/14 (sin puntos) que mapeamos a account_type Odoo.
# Reglas: Activo (1.x) → asset_*, Pasivo (2.x) → liability_*, Patrimonio (3.x) → equity,
# Ingresos (4.x, 7.x, 8.x, 17.x) → income, Costos+Gastos (5.x, 10.x-15.x) → expense.


def infer_account_type(code: str, name: str) -> str:
    """Mapea código RG 49/14 → account_type Odoo 18."""
    n = name.upper()
    if (
        code.startswith("1010101")
        or "RECAUDACIONES" in n
        or "CAJA" in n
        or "FONDOS" in n
        or "BANCOS" in n
    ):
        return "asset_cash"
    # Deudores por ventas / cuentas por cobrar → receivable
    # (independiente del prefix porque RG 49/14 varía: 1010301, 1010103, etc.)
    if "DEUDORES" in n or "CUENTAS POR COBRAR" in n:
        return "asset_receivable"
    if "INVENTARIO" in n or "MERCADER" in n or code.startswith("1010104"):
        return "asset_current"
    if "PAGADOS POR ADELANTADO" in n or "PAGAR POR ADELANTADO" in n:
        return "asset_prepayments"
    if code.startswith("10204"):
        return "asset_fixed"
    if code.startswith("1") and "DEPRECIACION" in n:
        return "asset_fixed"
    if code.startswith("1"):
        return "asset_current" if code.startswith("101") else "asset_non_current"
    if "PROVEEDORES" in n and code.startswith("201"):
        return "liability_payable"
    if code.startswith("2"):
        return (
            "liability_current" if code.startswith("201") else "liability_non_current"
        )
    if code.startswith("3"):
        return "equity"
    if code.startswith("4") and "DESCUENTOS CONCEDIDOS" in n:
        return "income_other"
    if code.startswith("4") or code.startswith("8"):
        return "income"
    if (
        code.startswith("5")
        or code.startswith("10")
        or code.startswith("11")
        or code.startswith("13")
    ):
        return "expense"
    if code.startswith("15"):
        return "expense_depreciation"
    return "expense"  # fallback


# Subset activo por default: comercio + servicios típico PyME.
# Códigos sin puntos. Resto se carga como active=False.
ACTIVE_CODES = {
    # 1.01.01 Disponibilidades
    "1010101",
    "1010102",
    "1010103",
    "1010104",
    # 1.01.03 Créditos
    "1010301",
    "1010305",
    "10103050102",
    "10103050103",  # IVA Crédito + retenciones
    # 1.01.04 Mercaderías (excepto agro/regímenes especiales)
    "10104",
    "1010401",
    "101040101",
    "101040102",
    "101040103",
    # 1.02.04 PPyE
    "1020401",
    "1020402",
    "1020403",
    "1020404",
    "1020405",
    "10204099",  # depreciación acumulada
    # 2.01 Pasivo corriente
    "2010101",  # Proveedores locales
    "2010301",  # Deudas fiscales corrientes (padre)
    "201030101",
    "201030102",
    "201030103",  # IRACIS / IVA a Pagar / Retenciones
    "2010302",  # Obligaciones laborales
    # 3 Patrimonio
    "30101",
    "3010101",  # Capital
    "30201",  # Reserva legal
    "30301",  # Resultados acumulados
    # 4 Ingresos
    "401",
    "40101",
    "40102",  # Ventas mercaderías gravadas/exentas
    "4010101",
    "4010102",  # subniveles gravadas IVA 10/5%
    "409",  # Ventas servicios gravados
    "498",  # Descuentos concedidos
    "499",  # Devoluciones
    # 5 Costos
    "501",
    "50101",
    "50102",  # Costo mercaderías
    # 8 Otros ingresos
    "801",
    "802",
    "803",
    "805",  # intereses, comisiones, descuentos, dif. cambio
    # 10-11 Gastos
    "1001",
    "1002",
    "1004",
    "1005",  # Gastos de ventas
    "1101",
    "1105",
    "1106",
    "1107",
    "1108",
    "1109",
    "1110",
    "1111",
    "1117",
    # 13 Gastos bancarios
    "1301",
    "1303",
    "1304",
    # 15 Depreciaciones
    "1501",
    "1502",
    # 19 IR
    "19",
    # 20 Resultado neto
    "20",
}


def code_to_id(code_raw: str) -> str:
    """1.01.03.05.02 → py_10103050102"""
    return "py_" + code_raw.replace(".", "")


def extract_chart() -> tuple[list[dict], list[dict]]:
    """Retorna (groups, accounts) extraídos del XLS DNIT."""
    wb = xlrd.open_workbook(str(XLS_PATH))
    groups = []
    accounts = []
    seen_ids: set[str] = set()

    # Patrón de línea: código numérico con puntos separadores
    code_re = re.compile(r"^(\d+(?:\.\d+)*)$")

    for sheet_name in ["1_Balance General", "2_Estado de Resultados"]:
        sh = wb.sheet_by_name(sheet_name)
        for r in range(sh.nrows):
            row_vals = [str(sh.cell_value(r, c)).strip() for c in range(sh.ncols)]
            code_raw = row_vals[0] if row_vals else ""
            name = row_vals[1] if len(row_vals) > 1 else ""

            if not code_raw or not name or "(nuevas cuentas" in name.lower():
                continue
            m = code_re.match(code_raw)
            if not m:
                continue
            code_clean = code_raw.replace(".", "")
            xml_id = code_to_id(code_raw)

            # Heurística: códigos hasta nivel 3 (`1.01.01`) → group; nivel >=4 → account.
            depth = code_raw.count(".") + 1
            if depth <= 3:
                grp_id = xml_id + "_grp"
                if grp_id in seen_ids:
                    continue
                seen_ids.add(grp_id)
                groups.append(
                    {
                        "id": grp_id,
                        "code_prefix_start": code_clean,
                        "code_prefix_end": code_clean,
                        "name": name.title(),
                    }
                )
            else:
                if xml_id in seen_ids:
                    continue
                seen_ids.add(xml_id)
                acc_type = infer_account_type(code_clean, name)
                is_active = code_clean in ACTIVE_CODES or any(
                    code_clean.startswith(active) for active in ACTIVE_CODES
                )
                accounts.append(
                    {
                        "id": xml_id,
                        "code": code_clean,
                        "name": name.title(),
                        "account_type": acc_type,
                        "reconcile": "True"
                        if acc_type in ("asset_receivable", "liability_payable")
                        else "False",
                        "non_trade": "",
                        "active": "True" if is_active else "False",
                    }
                )

    return groups, accounts


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)
    print(f"wrote {path.relative_to(ROOT)} ({len(rows)} records)")


def main() -> int:
    if not XLS_PATH.is_file():
        print(f"ERROR: missing {XLS_PATH}", file=sys.stderr)
        return 1
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    groups, accounts = extract_chart()
    write_csv(
        OUT_DIR / "account.group-py.csv",
        groups,
        ["id", "code_prefix_start", "code_prefix_end", "name"],
    )
    write_csv(
        OUT_DIR / "account.account-py.csv",
        accounts,
        ["id", "code", "name", "account_type", "reconcile", "non_trade", "active"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
