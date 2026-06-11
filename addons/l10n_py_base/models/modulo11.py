# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Algoritmo módulo 11 para identificadores fiscales paraguayos.

Helper Python puro (sin dependencias Odoo) para que pueda usarse desde tests
unitarios `tagged('-at_install')` sin levantar registry y desde otros módulos.

Algoritmo según Manual Técnico SIFEN v150 y rutina oficial módulo 11 de la SET:
pesos cíclicos 2..basemax de derecha a izquierda; resto <= 1 -> DV 0, si no
DV = 11 - resto. Tanto el RUC como el DV del CDC usan basemax=11 (verificado
contra el ejemplo oficial del manual y las libs de producción del ecosistema;
la mención "factores 2-9" que circula en resúmenes del manual es incorrecta).
"""
import re

DIGITS_ONLY = re.compile(r"\D+")


def calculate_dv(numero_str, basemax=11):
    """Calcula el dígito verificador módulo 11.

    :param numero_str: cadena de dígitos sin DV. Caracteres no numéricos se
        descartan antes de procesar.
    :param basemax: peso máximo cíclico. SIFEN usa ``11`` tanto para el DV
        del RUC como para el DV del CDC.
    :return: dígito verificador (entero 0-9).
    :raises ValueError: si la cadena no contiene dígitos.
    """
    digits_str = DIGITS_ONLY.sub("", str(numero_str))
    if not digits_str:
        raise ValueError("Número vacío o sin dígitos: %r" % numero_str)

    total = 0
    factor = 2
    for char in reversed(digits_str):
        total += int(char) * factor
        factor += 1
        if factor > basemax:
            factor = 2

    remainder = total % 11
    if remainder <= 1:
        # Rutina oficial SET (y las dos implementaciones de producción del
        # ecosistema: facturacionelectronicapy-xmlgen y rshk-jsifenlib):
        # resto 0 y resto 1 mapean ambos a DV 0.
        return 0
    return 11 - remainder


def split_ruc(ruc_raw):
    """Separa un RUC en (cuerpo, dv_declarado).

    Acepta formatos ``12345678-9``, ``12345678 9``, ``123456789`` (último dígito
    es el DV).  Caracteres no numéricos distintos del separador son ignorados.

    :return: ``(cuerpo_str, dv_int)`` o ``(None, None)`` si no se puede parsear.
    """
    if not ruc_raw:
        return None, None
    digits_str = DIGITS_ONLY.sub("", str(ruc_raw))
    if len(digits_str) < 2:
        return None, None
    return digits_str[:-1], int(digits_str[-1])


def validate_ruc(ruc_raw):
    """Valida un RUC paraguayo completo (cuerpo + DV).

    :param ruc_raw: RUC con o sin guión.
    :return: ``True`` si el DV coincide con el calculado, ``False`` en caso
        contrario o si el formato es inválido.
    """
    cuerpo, dv = split_ruc(ruc_raw)
    if cuerpo is None:
        return False
    try:
        return calculate_dv(cuerpo, basemax=11) == dv
    except ValueError:
        return False


def is_valid_cedula(cedula_raw):
    """Valida una Cédula de Identidad paraguaya.

    Solo verifica formato (1-9 dígitos numéricos); el DV de la cédula no se
    valida porque DNIT no publica el algoritmo y existen cédulas históricas
    sin DV.
    """
    if not cedula_raw:
        return False
    digits_str = DIGITS_ONLY.sub("", str(cedula_raw))
    return 1 <= len(digits_str) <= 9 and digits_str == str(cedula_raw).strip()
