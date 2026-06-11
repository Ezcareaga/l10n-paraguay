# PR-2 `l10n_py_edi` — Generador CDC: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** generador de CDC (Código de Control de 44 dígitos) para los DE SIFEN:
helper puro `services/cdc.py` + asignación automática en `account.move._post()`
con regla de reutilización y constraint de unicidad.

**Architecture:** mismo patrón que PR-1 — helper Python puro en `services/`
(testeable sin registry) + modelo delgado que extrae los componentes del move y
delega la composición. El DV reusa `modulo11.calculate_dv` de `l10n_py_base`
(su docstring ya anticipa este uso).

**Tech Stack:** Odoo 18, Python 3.11, stdlib `secrets` (código de seguridad).

**Branch:** `feature/l10n_py_edi-cdc` (desde `main`). PR a `main`.

---

## HALLAZGO DE RESEARCH (bloqueante, ya resuelto — NO re-investigar)

docs/01:72, docs/02:75 y docs/66:97 dicen que el DV del CDC usa "factores 2-9
cíclicos". **Eso es incorrecto.** Verificación hecha el 2026-06-11:

1. El ejemplo oficial del Manual v150 (`01800695631001003000013712022010619364760029`)
   solo valida con **basemax=11** (pesos 2-11 cíclicos): resto=2, DV=9.
   Con pesos 2-9 da resto=0 → DV=0 ≠ 9.
2. `facturacionelectronicapy-xmlgen` (TIPS-SA, producción):
   `calcularDigitoVerificador(cdc, 11)` — pesos 2-11, `resto > 1 ? 11 - resto : 0`.
3. `rshk-jsifenlib` (Roshka, producción): `generateDv` con `baseMax = 11`,
   mismo mapping `(total % 11) > 1 ? 11 - (total % 11) : 0`.

**Consecuencias en este PR:**

- `cdc.py` llama `modulo11.calculate_dv(base43, basemax=11)` (NO 9).
- `modulo11.calculate_dv` tiene un bug latente: cuando `resto == 1` devuelve 1,
  pero la rutina oficial SET devuelve **0** (ambas referencias coinciden).
  Se corrige acá (Task 1) porque el CDC depende de ese mapping.
- `references/nandefact` (CDC.ts) usa pesos 2-9 — **arrastra el bug**; sus tests
  son auto-referenciales y nunca validaron el ejemplo del manual. NO usarlo
  como referencia del algoritmo.
- docs/01, docs/02 y docs/66 se corrigen en Task 1 (documentación viva).

**Decisiones tomadas en planning (no re-decidir):**

1. **DV del CDC = `modulo11.calculate_dv(base43, basemax=11)`** con el fix de
   mapping `resto <= 1 → 0`. DRY: no duplicar el algoritmo en `cdc.py`.
2. `services/cdc.py` importa `from odoo.addons.l10n_py_base.models import modulo11`.
   No rompe la pureza práctica: no necesita registry (igual que los tests puros
   de PR-1 que ya importan vía `odoo.addons.*`). `l10n_py_edi` ya depende
   transitivamente de `l10n_py_base`.
3. Código de seguridad: 9 dígitos con `secrets.randbelow(1_000_000_000)`
   zero-padded (CSPRNG — el manual exige que no sea predecible).
4. Generación del CDC en `_post()` **después** de `super()._post()` (el name
   definitivo `EEE-PPP-NNNNNNN` y el `invoice_date` se asignan al postear).
5. Alcance de generación: moves de journal `sale`, país fiscal PY,
   `l10n_latam_use_documents`, doc type code en `("1", "5", "6")` (FE/NC/ND).
   Autofactura (4) es purchase-side y Nota de Remisión (7) no sale de
   `account.move` — fuera del MVP.
6. **Regla de reutilización** (docs/02:80-85): si el move ya tiene
   `l10n_py_security_code`, se recompone el CDC con ese código; si ningún campo
   componente cambió, el resultado es idéntico y no se escribe nada. Si algún
   campo cambió (p.ej. corrección post-rechazo que SÍ toca el CDC), se
   recompone con el mismo security code y se actualiza.
7. Unicidad: `_sql_constraints` `unique(l10n_py_cdc)` — Postgres permite
   múltiples NULL, no hace falta partial index.
8. Sin vistas en este PR (docs/66 PR-2 no las lista — el CDC se muestra en
   KuDE/portal en PRs posteriores). YAGNI.
9. Versiones: `l10n_py_base` 18.0.1.1.0 → **18.0.1.1.1** (bugfix),
   `l10n_py_edi` 18.0.1.0.0 → **18.0.1.1.0** (feature).

**Comandos de test (desde repo root, container `l10n_py_odoo` corriendo):**

```bash
# Tests de un módulo:
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079

# Suite completa (Task final):
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_base,l10n_py_account,l10n_py_edi --test-tags=l10n_py --http-port=8079
```

El exit code de odoo puede ser 0 aun con tests fallados — **siempre** grepear
el log: debe aparecer `0 failed, 0 error(s)` y no debe haber `ERROR`/`FAIL`.

---

## File Structure

```
addons/l10n_py_base/
├── __manifest__.py                       (bump 18.0.1.1.1)
├── models/modulo11.py                    (fix mapping resto==1)
└── tests/test_modulo11.py                (casos nuevos: resto==1, ejemplo CDC oficial)
addons/l10n_py_edi/
├── __manifest__.py                       (bump 18.0.1.1.0)
├── models/
│   ├── __init__.py                       (+ account_move)
│   └── account_move.py                   (NUEVO — campos CDC + hook _post)
├── services/cdc.py                       (NUEVO — puro)
└── tests/
    ├── __init__.py                       (+ test_cdc, test_account_move_cdc)
    ├── test_cdc.py                       (NUEVO — puro)
    └── test_account_move_cdc.py          (NUEVO — TransactionCase)
docs/01_SIFEN_KNOWLEDGE_BASE.md           (corregir algoritmo DV)
docs/02_SIFEN_REFERENCIA_COMPLETA.md      (corregir algoritmo DV)
docs/66_FASE_2_EDI_PLAN.md                (corregir brief PR-2 + research note)
```

---

### Task 0: Branch + plan doc

- [ ] **Step 1: Crear branch desde main actualizado**

```bash
git checkout main && git pull && git checkout -b feature/l10n_py_edi-cdc
```

- [ ] **Step 2: Commitear este plan**

```bash
git add docs/superpowers/plans/2026-06-11-l10n-py-edi-pr2-cdc.md
git commit -m "docs(edi): PR-2 CDC generator implementation plan"
```

---

### Task 1: Fix `modulo11` mapping resto==1 + corrección de docs (TDD)

**Files:**

- Modify: `addons/l10n_py_base/models/modulo11.py:39-42`
- Modify: `addons/l10n_py_base/tests/test_modulo11.py`
- Modify: `addons/l10n_py_base/__manifest__.py:5` (version 18.0.1.1.1)
- Modify: `docs/01_SIFEN_KNOWLEDGE_BASE.md:72`
- Modify: `docs/02_SIFEN_REFERENCIA_COMPLETA.md:75-78`
- Modify: `docs/66_FASE_2_EDI_PLAN.md:95-106` (sección PR-2)

- [ ] **Step 1: Escribir los tests que fallan**

En `addons/l10n_py_base/tests/test_modulo11.py`, **reemplazar** el test
`test_calculate_dv_basemax_9_for_cdc` (líneas 40-47, su docstring quedó
obsoleto) por estos dos tests:

```python
    def test_calculate_dv_cdc_official_example(self):
        """Ejemplo oficial del Manual Técnico SIFEN v150 (sección CDC).

        CDC completo: 01800695631001003000013712022010619364760029
        Los primeros 43 dígitos producen DV=9 con basemax=11 (verificado
        contra facturacionelectronicapy-xmlgen y rshk-jsifenlib, 2026-06-11).
        """
        base43 = "0180069563100100300001371202201061936476002"
        self.assertEqual(len(base43), 43)
        self.assertEqual(modulo11.calculate_dv(base43, basemax=11), 9)

    def test_calculate_dv_remainder_one_maps_to_zero(self):
        """Rutina oficial SET: resto 0 y resto 1 mapean ambos a DV 0.

        '6' con basemax=11: 6*2=12, 12%11=1 -> DV 0 (no 1).
        """
        self.assertEqual(modulo11.calculate_dv("6", basemax=11), 0)
        # resto == 0 también da 0: '0' -> suma 0
        self.assertEqual(modulo11.calculate_dv("0", basemax=11), 0)
```

- [ ] **Step 2: Correr y verificar que falla**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_base --test-tags=l10n_py --http-port=8079 2>&1 | grep -E "test_calculate_dv|failed|FAIL"
```

Expected: `test_calculate_dv_remainder_one_maps_to_zero` FAIL (devuelve 1, no 0).
`test_calculate_dv_cdc_official_example` debe pasar ya (resto=2 no toca el edge).

- [ ] **Step 3: Implementar el fix en `modulo11.py`**

Reemplazar las líneas 39-42:

```python
    remainder = total % 11
    if remainder <= 1:
        return remainder
    return 11 - remainder
```

por:

```python
    remainder = total % 11
    if remainder <= 1:
        # Rutina oficial SET (y las dos implementaciones de producción del
        # ecosistema: facturacionelectronicapy-xmlgen y rshk-jsifenlib):
        # resto 0 y resto 1 mapean ambos a DV 0.
        return 0
    return 11 - remainder
```

Y actualizar el docstring del módulo (líneas 9-10), reemplazando:

```python
Algoritmo según Manual Técnico SIFEN v150, sección 3 (CDC) y práctica estándar
DNIT para RUC (basemax=11).
```

por:

```python
Algoritmo según Manual Técnico SIFEN v150 y rutina oficial módulo 11 de la SET:
pesos cíclicos 2..basemax de derecha a izquierda; resto <= 1 -> DV 0, si no
DV = 11 - resto. Tanto el RUC como el DV del CDC usan basemax=11 (verificado
contra el ejemplo oficial del manual y las libs de producción del ecosistema;
la mención "factores 2-9" que circula en resúmenes del manual es incorrecta).
```

Y en el docstring de `calculate_dv`, reemplazar la línea:

```python
    :param basemax: peso máximo cíclico. Por convención SIFEN: ``11`` para RUC,
        ``9`` para CDC.
```

por:

```python
    :param basemax: peso máximo cíclico. SIFEN usa ``11`` tanto para el DV
        del RUC como para el DV del CDC.
```

- [ ] **Step 4: Bump version `l10n_py_base`**

En `addons/l10n_py_base/__manifest__.py` línea 5: `"version": "18.0.1.1.1",`

- [ ] **Step 5: Correr y verificar verde**

Mismo comando del Step 2 (sin grep, ver resumen final). Expected: toda la suite
de `l10n_py_base` verde, `0 failed, 0 error(s)`.

- [ ] **Step 6: Corregir docs/01 línea 72**

Reemplazar:

```
2. Aplicar módulo 11 con factores 2-9 cíclicos de derecha a izquierda.
```

por:

```
2. Aplicar módulo 11 con factores 2-11 cíclicos de derecha a izquierda
   (misma rutina que el DV del RUC; la mención "factores 2-9" de algunos
   resúmenes del manual es incorrecta — verificado contra el ejemplo oficial
   y las libs de producción xmlgen/jsifenlib, 2026-06-11).
```

- [ ] **Step 7: Corregir docs/02 líneas 75-78**

Reemplazar:

```
2. Aplicar módulo 11 con factores multiplicadores del 2 al 9 (derecha a izquierda, cíclico).
3. Sumar todos los productos parciales.
4. Calcular `resto = suma % 11`.
5. Si `resto == 0` → DV = 0; si `resto == 1` → DV = 1; sino → DV = 11 - resto.
```

por:

```
2. Aplicar módulo 11 con factores multiplicadores del 2 al 11 (derecha a izquierda, cíclico).
3. Sumar todos los productos parciales.
4. Calcular `resto = suma % 11`.
5. Si `resto <= 1` → DV = 0; sino → DV = 11 - resto.

> Verificado 2026-06-11: el ejemplo oficial de abajo solo valida con factores
> 2-11. `facturacionelectronicapy-xmlgen` (TIPS-SA) y `rshk-jsifenlib` (Roshka)
> implementan exactamente esta rutina (`basemax=11`, `resto > 1 ? 11 - resto : 0`).
```

- [ ] **Step 8: Corregir docs/66 sección PR-2**

En `docs/66_FASE_2_EDI_PLAN.md` líneas 95-98, reemplazar:

```
- [ ] `services/cdc.py` puro: `compose_cdc(...)` (43 dígitos desde tipo DE,
      RUC+DV, est, punto, número, tipo contribuyente, fecha YYYYMMDD, tipo
      emisión, código seguridad) + `cdc_check_digit()` módulo 11 pesos cíclicos
      2-9 derecha→izquierda + `generate_security_code()` (9 dígitos, `secrets`)
```

por:

```
- [ ] `services/cdc.py` puro: `compose_cdc(...)` (43 dígitos desde tipo DE,
      RUC+DV, est, punto, número, tipo contribuyente, fecha YYYYMMDD, tipo
      emisión, código seguridad) + `cdc_check_digit()` = `modulo11.calculate_dv`
      con basemax=11 (pesos 2-11 — la mención "2-9" era un error de docs,
      corregido) + `generate_security_code()` (9 dígitos, `secrets`)
```

y la línea 106:

```
**Research pendiente:** ninguno — algoritmo completo en docs/01:48-85 y docs/02:72-78.
```

por:

```
**Research cerrado 2026-06-11:** el DV del CDC usa basemax=11 (no 2-9 como
decían docs/01-02 — corregidos). Fix de mapping resto==1 aplicado a
`modulo11.calculate_dv` en l10n_py_base 18.0.1.1.1.
```

- [ ] **Step 9: Commit (dos commits atómicos)**

```bash
git add addons/l10n_py_base/models/modulo11.py addons/l10n_py_base/tests/test_modulo11.py addons/l10n_py_base/__manifest__.py
git commit -m "fix(l10n_py_base): align modulo11 DV mapping with official SET routine (resto<=1 -> 0)"
git add docs/01_SIFEN_KNOWLEDGE_BASE.md docs/02_SIFEN_REFERENCIA_COMPLETA.md docs/66_FASE_2_EDI_PLAN.md
git commit -m "docs(sifen): correct CDC check-digit algorithm (basemax 11, not 2-9)"
```

---

### Task 2: `services/cdc.py` (TDD, puro)

**Files:**

- Create: `addons/l10n_py_edi/services/cdc.py`
- Test: `addons/l10n_py_edi/tests/test_cdc.py`
- Modify: `addons/l10n_py_edi/tests/__init__.py`

- [ ] **Step 1: Escribir el test que falla**

`tests/__init__.py` — agregar al final:

```python
from . import test_cdc
```

`tests/test_cdc.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del generador CDC — Python puro, no requiere Odoo registry."""
import datetime
import unittest

from odoo.tests import tagged

from odoo.addons.l10n_py_edi.services import cdc

# Ejemplo oficial del Manual Técnico SIFEN v150 (docs/02 sección 3).
OFFICIAL_CDC = "01800695631001003000013712022010619364760029"


@tagged("standard", "l10n_py")
class TestCdc(unittest.TestCase):
    def _official_kwargs(self, **overrides):
        kwargs = {
            "document_type": "1",
            "ruc": "80069563",
            "ruc_dv": 1,
            "establishment": "1",
            "expedition_point": "3",
            "document_number": "137",
            "taxpayer_type": "1",
            "issue_date": datetime.date(2022, 1, 6),
            "emission_type": "1",
            "security_code": "936476002",
        }
        kwargs.update(overrides)
        return kwargs

    # ------------------------------------------------------------------
    # cdc_check_digit
    # ------------------------------------------------------------------
    def test_check_digit_official_example(self):
        self.assertEqual(cdc.cdc_check_digit(OFFICIAL_CDC[:43]), 9)

    def test_check_digit_wrong_length_raises(self):
        with self.assertRaises(cdc.CdcError):
            cdc.cdc_check_digit("123")
        with self.assertRaises(cdc.CdcError):
            cdc.cdc_check_digit(OFFICIAL_CDC)  # 44 != 43

    def test_check_digit_non_digits_raises(self):
        with self.assertRaises(cdc.CdcError):
            cdc.cdc_check_digit("a" * 43)

    # ------------------------------------------------------------------
    # compose_cdc
    # ------------------------------------------------------------------
    def test_compose_official_example(self):
        self.assertEqual(cdc.compose_cdc(**self._official_kwargs()), OFFICIAL_CDC)

    def test_compose_accepts_padded_inputs(self):
        """Los componentes pueden venir ya zero-padded o sin pad."""
        result = cdc.compose_cdc(
            **self._official_kwargs(
                document_type="01",
                establishment="001",
                expedition_point="003",
                document_number="0000137",
            )
        )
        self.assertEqual(result, OFFICIAL_CDC)

    def test_compose_generates_security_code_when_missing(self):
        result = cdc.compose_cdc(**self._official_kwargs(security_code=None))
        self.assertEqual(len(result), 44)
        self.assertTrue(result.isdigit())
        self.assertTrue(cdc.validate_cdc(result))

    def test_compose_datetime_accepted(self):
        """datetime.datetime también sirve como issue_date (usa .date())."""
        result = cdc.compose_cdc(
            **self._official_kwargs(
                issue_date=datetime.datetime(2022, 1, 6, 14, 30)
            )
        )
        self.assertEqual(result, OFFICIAL_CDC)

    def test_compose_invalid_inputs_raise(self):
        bad_cases = [
            {"document_type": "100"},       # > 2 dígitos
            {"document_type": "x"},
            {"ruc": "123456789"},           # > 8 dígitos
            {"ruc": ""},
            {"ruc_dv": 12},                 # > 1 dígito
            {"establishment": "1234"},      # > 3 dígitos
            {"expedition_point": ""},
            {"document_number": "12345678"},  # > 7 dígitos
            {"taxpayer_type": "3"},         # solo 1/2
            {"emission_type": "9"},         # solo 1/2
            {"security_code": "12345"},     # != 9 dígitos
            {"security_code": "12345678a"},
            {"issue_date": "2022-01-06"},   # str no aceptado
        ]
        for overrides in bad_cases:
            with self.subTest(overrides=overrides):
                with self.assertRaises(cdc.CdcError):
                    cdc.compose_cdc(**self._official_kwargs(**overrides))

    # ------------------------------------------------------------------
    # generate_security_code
    # ------------------------------------------------------------------
    def test_generate_security_code_format(self):
        for _ in range(20):
            code = cdc.generate_security_code()
            self.assertEqual(len(code), 9)
            self.assertTrue(code.isdigit())

    def test_generate_security_code_varies(self):
        codes = {cdc.generate_security_code() for _ in range(10)}
        self.assertGreater(len(codes), 1)

    # ------------------------------------------------------------------
    # parse_cdc / validate_cdc
    # ------------------------------------------------------------------
    def test_parse_official_example(self):
        parsed = cdc.parse_cdc(OFFICIAL_CDC)
        self.assertEqual(parsed["document_type"], "01")
        self.assertEqual(parsed["ruc"], "80069563")
        self.assertEqual(parsed["ruc_dv"], "1")
        self.assertEqual(parsed["establishment"], "001")
        self.assertEqual(parsed["expedition_point"], "003")
        self.assertEqual(parsed["document_number"], "0000137")
        self.assertEqual(parsed["taxpayer_type"], "1")
        self.assertEqual(parsed["issue_date"], datetime.date(2022, 1, 6))
        self.assertEqual(parsed["emission_type"], "1")
        self.assertEqual(parsed["security_code"], "936476002")
        self.assertEqual(parsed["check_digit"], "9")

    def test_parse_invalid_raises(self):
        with self.assertRaises(cdc.CdcError):
            cdc.parse_cdc("123")  # largo incorrecto
        # DV adulterado:
        with self.assertRaises(cdc.CdcError):
            cdc.parse_cdc(OFFICIAL_CDC[:43] + "5")

    def test_validate_cdc(self):
        self.assertTrue(cdc.validate_cdc(OFFICIAL_CDC))
        self.assertFalse(cdc.validate_cdc(OFFICIAL_CDC[:43] + "5"))
        self.assertFalse(cdc.validate_cdc("abc"))
        self.assertFalse(cdc.validate_cdc(""))
        self.assertFalse(cdc.validate_cdc(None))
```

- [ ] **Step 2: Correr y verificar que falla**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079 2>&1 | grep -E "test_cdc|ImportError|ModuleNotFound|failed|error"
```

Expected: ImportError — `cdc` no existe todavía.

- [ ] **Step 3: Implementar `services/cdc.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Generador del CDC — Código de Control de 44 dígitos (Manual SIFEN v150 §3).

Estructura (posiciones 1-based):
    01-02  tipo de DE          26-33  fecha emisión YYYYMMDD
    03-10  RUC emisor (sin DV) 34     tipo de emisión (1=normal, 2=contingencia)
    11     DV del RUC          35-43  código de seguridad (9 dígitos aleatorios)
    12-14  establecimiento     44     DV del CDC (módulo 11, basemax=11)
    15-17  punto de expedición
    18-24  número del documento
    25     tipo de contribuyente (1=PF, 2=PJ)

El DV usa la rutina oficial SET vía ``modulo11.calculate_dv(base43, basemax=11)``
(misma que el RUC — verificado contra el ejemplo oficial del manual y las libs
de producción xmlgen/jsifenlib; NO son "pesos 2-9").

Helper Python puro: no requiere registry. El import de ``modulo11`` solo carga
definiciones de módulo, no levanta Odoo.
"""
import datetime
import secrets

from odoo.addons.l10n_py_base.models import modulo11

EMISSION_NORMAL = "1"
EMISSION_CONTINGENCY = "2"
TAXPAYER_TYPES = ("1", "2")  # 1=Persona Física, 2=Persona Jurídica
EMISSION_TYPES = (EMISSION_NORMAL, EMISSION_CONTINGENCY)
SECURITY_CODE_LENGTH = 9
CDC_LENGTH = 44


class CdcError(ValueError):
    """Componente inválido para componer o parsear un CDC."""


def _digits(value, length, label, pad=True):
    """Normaliza un componente numérico a ``length`` dígitos zero-padded.

    :raises CdcError: si no es numérico o excede el largo.
    """
    text = str(value if value is not None else "").strip()
    if not text or not text.isdigit():
        raise CdcError("%s inválido: %r (se esperan dígitos)" % (label, value))
    if pad:
        text = text.zfill(length)
    if len(text) != length:
        raise CdcError(
            "%s inválido: %r (largo esperado %d)" % (label, value, length)
        )
    return text


def generate_security_code():
    """Código de seguridad aleatorio de 9 dígitos (CSPRNG, módulo ``secrets``)."""
    return str(secrets.randbelow(10**SECURITY_CODE_LENGTH)).zfill(
        SECURITY_CODE_LENGTH
    )


def cdc_check_digit(base43):
    """DV del CDC: módulo 11 con basemax=11 sobre los primeros 43 dígitos.

    :raises CdcError: si ``base43`` no son exactamente 43 dígitos.
    """
    base43 = str(base43 or "")
    if len(base43) != CDC_LENGTH - 1 or not base43.isdigit():
        raise CdcError(
            "Base del CDC inválida: se esperan 43 dígitos, llegó %r" % base43
        )
    return modulo11.calculate_dv(base43, basemax=11)


def compose_cdc(
    document_type,
    ruc,
    ruc_dv,
    establishment,
    expedition_point,
    document_number,
    taxpayer_type,
    issue_date,
    emission_type=EMISSION_NORMAL,
    security_code=None,
):
    """Compone el CDC completo de 44 dígitos (43 componentes + DV).

    :param document_type: código del tipo de DE (1=FE, 5=NC, 6=ND...).
    :param ruc: RUC del emisor sin DV (1-8 dígitos).
    :param ruc_dv: dígito verificador del RUC.
    :param establishment: código de establecimiento (1-3 dígitos).
    :param expedition_point: punto de expedición (1-3 dígitos).
    :param document_number: número del documento (1-7 dígitos).
    :param taxpayer_type: "1" (PF) o "2" (PJ).
    :param issue_date: :class:`datetime.date` o :class:`datetime.datetime`.
    :param emission_type: "1" normal (default) o "2" contingencia.
    :param security_code: 9 dígitos; si es None se genera uno aleatorio.
    :return: CDC de 44 dígitos (str).
    :raises CdcError: ante cualquier componente inválido.
    """
    if isinstance(issue_date, datetime.datetime):
        issue_date = issue_date.date()
    if not isinstance(issue_date, datetime.date):
        raise CdcError(
            "issue_date debe ser datetime.date, llegó %r" % (issue_date,)
        )
    taxpayer = str(taxpayer_type or "").strip()
    if taxpayer not in TAXPAYER_TYPES:
        raise CdcError(
            "Tipo de contribuyente inválido: %r (solo 1/2)" % (taxpayer_type,)
        )
    emission = str(emission_type or "").strip()
    if emission not in EMISSION_TYPES:
        raise CdcError(
            "Tipo de emisión inválido: %r (solo 1/2)" % (emission_type,)
        )
    if security_code is None:
        security_code = generate_security_code()

    base43 = "".join(
        (
            _digits(document_type, 2, "Tipo de DE"),
            _digits(ruc, 8, "RUC"),
            _digits(ruc_dv, 1, "DV del RUC"),
            _digits(establishment, 3, "Establecimiento"),
            _digits(expedition_point, 3, "Punto de expedición"),
            _digits(document_number, 7, "Número de documento"),
            taxpayer,
            issue_date.strftime("%Y%m%d"),
            emission,
            _digits(security_code, 9, "Código de seguridad", pad=False),
        )
    )
    return base43 + str(cdc_check_digit(base43))


def parse_cdc(cdc_str):
    """Descompone un CDC de 44 dígitos en sus componentes y valida el DV.

    :return: dict con document_type, ruc, ruc_dv, establishment,
        expedition_point, document_number, taxpayer_type, issue_date
        (:class:`datetime.date`), emission_type, security_code, check_digit.
    :raises CdcError: largo/formato/DV inválidos.
    """
    cdc_str = str(cdc_str or "")
    if len(cdc_str) != CDC_LENGTH or not cdc_str.isdigit():
        raise CdcError(
            "CDC inválido: se esperan 44 dígitos, llegó %r" % cdc_str
        )
    if int(cdc_str[43]) != cdc_check_digit(cdc_str[:43]):
        raise CdcError("CDC inválido: dígito verificador incorrecto")
    try:
        issue_date = datetime.datetime.strptime(cdc_str[25:33], "%Y%m%d").date()
    except ValueError as exc:
        raise CdcError(
            "CDC inválido: fecha de emisión %r" % cdc_str[25:33]
        ) from exc
    return {
        "document_type": cdc_str[0:2],
        "ruc": cdc_str[2:10],
        "ruc_dv": cdc_str[10:11],
        "establishment": cdc_str[11:14],
        "expedition_point": cdc_str[14:17],
        "document_number": cdc_str[17:24],
        "taxpayer_type": cdc_str[24:25],
        "issue_date": issue_date,
        "emission_type": cdc_str[33:34],
        "security_code": cdc_str[34:43],
        "check_digit": cdc_str[43:44],
    }


def validate_cdc(cdc_str):
    """True si ``cdc_str`` es un CDC bien formado con DV correcto."""
    try:
        parse_cdc(cdc_str)
    except CdcError:
        return False
    return True
```

- [ ] **Step 4: Correr y verificar verde**

Mismo comando del Step 2. Expected: todos los tests de `TestCdc` PASS, `0 failed`.

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_edi/services/cdc.py addons/l10n_py_edi/tests/test_cdc.py addons/l10n_py_edi/tests/__init__.py
git commit -m "feat(l10n_py_edi): pure CDC composer service per Manual SIFEN v150"
```

---

### Task 3: Campos CDC en `account.move` + generación en `_post()` (TDD)

**Files:**

- Create: `addons/l10n_py_edi/models/account_move.py`
- Modify: `addons/l10n_py_edi/models/__init__.py`
- Test: `addons/l10n_py_edi/tests/test_account_move_cdc.py`
- Modify: `addons/l10n_py_edi/tests/__init__.py`

- [ ] **Step 1: Escribir el test que falla**

`tests/__init__.py` — agregar al final:

```python
from . import test_account_move_cdc
```

`tests/test_account_move_cdc.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de la asignación de CDC al postear documentos SIFEN."""
import datetime

import psycopg2.errors

from odoo.exceptions import UserError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.l10n_py_account.tests.common import L10nPyAccountTestCase
from odoo.addons.l10n_py_edi.services import cdc as cdc_service


@tagged("post_install", "-at_install", "l10n_py")
class TestAccountMoveCdc(L10nPyAccountTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        partner = cls.company.partner_id
        partner.l10n_latam_identification_type_id = cls.env.ref(
            "l10n_py_base.id_type_py_ruc"
        )
        partner.vat = "80069563-1"
        cls.company.l10n_py_taxpayer_type_id = cls.env.ref(
            "l10n_py_base.taxpayer_type_2"
        )

    def _post_invoice(self, move_type="out_invoice", invoice_date=None):
        move = self.init_invoice(
            move_type,
            partner=self.partner_a,
            invoice_date=invoice_date or datetime.date(2026, 6, 11),
            products=self.product_a,
        )
        move.action_post()
        return move

    def test_cdc_assigned_on_post(self):
        move = self._post_invoice()
        self.assertTrue(move.l10n_py_cdc)
        self.assertEqual(len(move.l10n_py_cdc), 44)
        self.assertTrue(cdc_service.validate_cdc(move.l10n_py_cdc))
        parsed = cdc_service.parse_cdc(move.l10n_py_cdc)
        self.assertEqual(parsed["document_type"], "01")
        self.assertEqual(parsed["ruc"], "80069563")
        self.assertEqual(parsed["ruc_dv"], "1")
        self.assertEqual(parsed["establishment"], "001")
        self.assertEqual(parsed["expedition_point"], "001")
        self.assertEqual(parsed["taxpayer_type"], "2")
        self.assertEqual(parsed["issue_date"], move.invoice_date)
        self.assertEqual(parsed["emission_type"], "1")
        # El número del CDC sale del name EEE-PPP-NNNNNNN:
        self.assertEqual(parsed["document_number"], move.name.split("-")[2])
        # Security code persistido y consistente con el CDC:
        self.assertEqual(parsed["security_code"], move.l10n_py_security_code)

    def test_emission_type_default_normal(self):
        move = self._post_invoice()
        self.assertEqual(move.l10n_py_emission_type, "1")

    def test_credit_note_gets_doc_type_05(self):
        move = self._post_invoice("out_refund")
        parsed = cdc_service.parse_cdc(move.l10n_py_cdc)
        self.assertEqual(parsed["document_type"], "05")

    def test_cdc_reused_on_repost_without_changes(self):
        """Regla docs/02: corrección que no toca campos del CDC -> mismo CDC."""
        move = self._post_invoice()
        original_cdc = move.l10n_py_cdc
        original_code = move.l10n_py_security_code
        move.button_draft()
        move.action_post()
        self.assertEqual(move.l10n_py_cdc, original_cdc)
        self.assertEqual(move.l10n_py_security_code, original_code)

    def test_cdc_recomposed_when_component_changes(self):
        """Si cambia un componente (fecha), el CDC cambia pero el security
        code se conserva (la regla solo exige no regenerarlo)."""
        move = self._post_invoice(invoice_date=datetime.date(2026, 6, 1))
        original_cdc = move.l10n_py_cdc
        original_code = move.l10n_py_security_code
        move.button_draft()
        move.invoice_date = datetime.date(2026, 6, 10)
        move.action_post()
        self.assertNotEqual(move.l10n_py_cdc, original_cdc)
        self.assertEqual(move.l10n_py_security_code, original_code)
        parsed = cdc_service.parse_cdc(move.l10n_py_cdc)
        self.assertEqual(parsed["issue_date"], datetime.date(2026, 6, 10))

    def test_cdc_not_copied_on_duplicate(self):
        move = self._post_invoice()
        copy = move.copy()
        self.assertFalse(copy.l10n_py_cdc)
        self.assertFalse(copy.l10n_py_security_code)

    def test_cdc_unique_constraint(self):
        move = self._post_invoice()
        other = self.init_invoice(
            "out_invoice",
            partner=self.partner_a,
            invoice_date=datetime.date(2026, 6, 11),
            products=self.product_a,
        )
        with self.assertRaises(
            psycopg2.errors.UniqueViolation
        ), mute_logger("odoo.sql_db"), self.env.cr.savepoint():
            other.write({"l10n_py_cdc": move.l10n_py_cdc})
            self.env.cr.flush()

    def test_missing_taxpayer_type_raises(self):
        self.company.l10n_py_taxpayer_type_id = False
        with self.assertRaises(UserError):
            self._post_invoice()

    def test_invalid_company_ruc_raises(self):
        self.company.partner_id.vat = False
        with self.assertRaises(UserError):
            self._post_invoice()

    def test_no_cdc_for_purchase_documents(self):
        """Los documentos de compra (vendor bills) no generan CDC propio."""
        move = self.init_invoice(
            "in_invoice",
            partner=self.partner_a,
            invoice_date=datetime.date(2026, 6, 11),
            products=self.product_a,
        )
        if move.l10n_latam_document_type_id:
            move.l10n_latam_document_number = "001-001-0000001"
        move.action_post()
        self.assertFalse(move.l10n_py_cdc)
```

- [ ] **Step 2: Correr y verificar que falla**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079 2>&1 | grep -E "test_account_move_cdc|failed|error"
```

Expected: FAIL — campos `l10n_py_cdc` inexistentes.

- [ ] **Step 3: Implementar `models/account_move.py`**

`models/__init__.py` pasa a:

```python
from . import account_move
from . import res_company
```

`models/account_move.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""CDC (Código de Control SIFEN) en account.move.

El CDC se genera al postear, después de que el core asigne el name definitivo
(``EEE-PPP-NNNNNNN``) y el invoice_date. Regla de reutilización (docs/02 §3):
el security code se genera una sola vez por documento; si al re-postear ningún
componente cambió, el CDC resultante es idéntico y no se toca.
"""
import re

from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.l10n_py_base.models import modulo11

from ..services import cdc as cdc_service

# name paraguayo: establecimiento-punto-número (l10n_py_account
# _get_starting_sequence garantiza el formato EEE-PPP-NNNNNNN).
PY_DOCUMENT_NAME = re.compile(r"^(\d{3})-(\d{3})-(\d{7})$")
# Tipos de DE que emitimos desde account.move (FE / NC / ND). Autofactura (4)
# es purchase-side y Nota de Remisión (7) no nace de un asiento contable.
SIFEN_EDOC_CODES = ("1", "5", "6")


class AccountMove(models.Model):
    _inherit = "account.move"

    l10n_py_cdc = fields.Char(
        string="CDC",
        size=44,
        copy=False,
        readonly=True,
        index="btree_not_null",
        help="Código de Control SIFEN de 44 dígitos. Se genera al postear.",
    )
    l10n_py_security_code = fields.Char(
        string="Código de seguridad SIFEN",
        size=9,
        copy=False,
        readonly=True,
        help="Componente aleatorio del CDC (posiciones 35-43). Se genera una "
        "sola vez por documento para permitir reutilizar el CDC tras un "
        "rechazo que no altere sus componentes.",
    )
    l10n_py_emission_type = fields.Selection(
        selection=[("1", "Normal"), ("2", "Contingencia")],
        string="Tipo de emisión SIFEN",
        default="1",
        copy=False,
        help="Posición 34 del CDC. Contingencia solo cuando SIFEN está caído.",
    )

    _sql_constraints = [
        (
            "l10n_py_cdc_uniq",
            "unique(l10n_py_cdc)",
            "Ya existe un documento con ese CDC.",
        ),
    ]

    def _post(self, soft=True):
        posted = super()._post(soft=soft)
        for move in posted:
            if move._l10n_py_edi_is_sifen_document():
                move._l10n_py_edi_assign_cdc()
        return posted

    def _l10n_py_edi_is_sifen_document(self):
        """True si este move es un DE SIFEN que emitimos nosotros."""
        self.ensure_one()
        return (
            self.company_id.account_fiscal_country_id.code == "PY"
            and self.journal_id.type == "sale"
            and self.l10n_latam_use_documents
            and self.l10n_latam_document_type_id.code in SIFEN_EDOC_CODES
        )

    def _l10n_py_edi_cdc_components(self):
        """Componentes del CDC extraídos del move (sin security code).

        :raises UserError: configuración incompleta (RUC, tipo de
            contribuyente, PoE o name fuera de formato).
        """
        self.ensure_one()
        company = self.company_id
        ruc, ruc_dv = modulo11.split_ruc(company.partner_id.vat)
        if not ruc or not modulo11.validate_ruc(company.partner_id.vat):
            raise UserError(
                _(
                    "La compañía %(company)s no tiene un RUC válido configurado "
                    "en su contacto (campo NIF/RUC).",
                    company=company.display_name,
                )
            )
        taxpayer_type = company.l10n_py_taxpayer_type_id.code
        if not taxpayer_type:
            raise UserError(
                _(
                    "La compañía %(company)s no tiene Tipo de Contribuyente "
                    "(PF/PJ) configurado. Es necesario para el CDC.",
                    company=company.display_name,
                )
            )
        poe = self.journal_id.l10n_py_point_of_emission_id
        if not poe:
            raise UserError(
                _(
                    "El diario %(journal)s no tiene Punto de Emisión "
                    "configurado.",
                    journal=self.journal_id.display_name,
                )
            )
        match = PY_DOCUMENT_NAME.match(self.name or "")
        if not match:
            raise UserError(
                _(
                    "El número %(name)s no tiene el formato paraguayo "
                    "EEE-PPP-NNNNNNN; no se puede componer el CDC.",
                    name=self.name or "?",
                )
            )
        return {
            "document_type": self.l10n_latam_document_type_id.code,
            "ruc": ruc,
            "ruc_dv": ruc_dv,
            "establishment": poe.establishment_code,
            "expedition_point": poe.code,
            "document_number": match.group(3),
            "taxpayer_type": taxpayer_type,
            "issue_date": self.invoice_date or self.date,
            "emission_type": self.l10n_py_emission_type or "1",
        }

    def _l10n_py_edi_assign_cdc(self):
        """Compone y persiste el CDC, reutilizando el security code si existe."""
        self.ensure_one()
        components = self._l10n_py_edi_cdc_components()
        security_code = (
            self.l10n_py_security_code or cdc_service.generate_security_code()
        )
        try:
            new_cdc = cdc_service.compose_cdc(
                security_code=security_code, **components
            )
        except cdc_service.CdcError as exc:
            raise UserError(
                _("No se pudo generar el CDC: %(reason)s", reason=exc)
            ) from exc
        if new_cdc != self.l10n_py_cdc:
            self.write(
                {
                    "l10n_py_cdc": new_cdc,
                    "l10n_py_security_code": security_code,
                }
            )
```

- [ ] **Step 4: Correr y verificar verde**

Mismo comando del Step 2 (la primera corrida tras agregar campos requiere `-u`
para actualizar el schema — el comando ya lo hace). Expected: 11 tests de
`TestAccountMoveCdc` PASS, suites previas verdes, `0 failed`.

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_edi/models/account_move.py addons/l10n_py_edi/models/__init__.py addons/l10n_py_edi/tests/test_account_move_cdc.py addons/l10n_py_edi/tests/__init__.py
git commit -m "feat(l10n_py_edi): assign CDC on post with reuse rule and unique constraint"
```

---

### Task 4: Verificación final + pre-commit + PR

**Files:**

- Modify: `addons/l10n_py_edi/__manifest__.py:5` (version 18.0.1.1.0)
- Posibles ajustes de pre-commit (README.rst regenerado, etc.)

- [ ] **Step 1: Bump version `l10n_py_edi`**

En `addons/l10n_py_edi/__manifest__.py` línea 5: `"version": "18.0.1.1.0",`

- [ ] **Step 2: Suite completa de los 3 módulos**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_base,l10n_py_account,l10n_py_edi --test-tags=l10n_py --http-port=8079
```

Expected: `0 failed, 0 error(s)` en el log final (138 tests previos + ~26 nuevos).

- [ ] **Step 3: Instalación limpia desde cero**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -i l10n_py_edi --http-port=8079 2>&1 | grep -iE "warning|error|critical" || echo "CLEAN"
```

Expected: `CLEAN` (o solo warnings pre-existentes no atribuibles al módulo).

- [ ] **Step 4: Pre-commit sobre todo el repo**

```bash
pre-commit run --all-files
```

Expected: todo verde. Si oca-gen-addon-readme regenera README.rst (por el bump
de versión), incluir el archivo regenerado en el commit del Step 5.

- [ ] **Step 5: Commit de ajustes**

```bash
git add -A addons/
git commit -m "chore(l10n_py_edi): version bumps + pre-commit fixes for PR-2"
```

- [ ] **Step 6: Push + PR**

```bash
git push -u origin feature/l10n_py_edi-cdc
gh pr create --base main --title "feat(l10n_py_edi): CDC generator (PR-2 Fase 2 EDI)" --body "<resumen: scope PR-2 de docs/66 — services/cdc.py puro verificado contra el ejemplo oficial del Manual v150, asignación en _post() con regla de reutilización y constraint de unicidad. Incluye fix del mapping resto==1 en modulo11 (l10n_py_base 18.0.1.1.1) y corrección del algoritmo en docs/01-02-66: el DV del CDC usa basemax=11, no pesos 2-9.>"
```

**Recordatorios de PR (memoria del proyecto):** no escribir `PR #N` en el body
en posición de footer (commitlint trap); el repo exige conversation resolution
antes de merge. **El merge lo aprueba el owner — no mergear sin OK.**

---

## Self-review checklist (ejecutada al escribir este plan)

- Spec coverage vs docs/66 PR-2: `compose_cdc` + `cdc_check_digit` +
  `generate_security_code` ✅ (Task 2, con basemax corregido), verificación
  contra el CDC ejemplo de docs/01-02 ✅ (Tasks 1 y 2), campos
  `l10n_py_cdc`/`l10n_py_security_code`/`l10n_py_emission_type` con
  readonly/copy=False/index + generación en `_post()` solo doc types SIFEN +
  constraint unicidad ✅ (Task 3), regla de reutilización ✅ (Task 3,
  tests de repost).
- Sin placeholders: todo step tiene código completo.
- Consistencia de nombres: `cdc.{CdcError,compose_cdc,cdc_check_digit,parse_cdc,validate_cdc,generate_security_code,EMISSION_NORMAL}`,
  campos `l10n_py_{cdc,security_code,emission_type}` idénticos entre modelo y
  tests, kwargs de `compose_cdc` idénticos entre servicio, tests y
  `_l10n_py_edi_cdc_components()`.
- Riesgo conocido para el ejecutor: `init_invoice` y el flujo latam pueden
  requerir ajustes menores de fixture (p.ej. doc type auto-asignado en
  `in_invoice`). Si un test de Task 3 falla por fixture (no por lógica),
  ajustar el fixture y anotar la deviation en el reporte — no cambiar la
  lógica del modelo para acomodar el test.
