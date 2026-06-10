# PR-1 `l10n_py_edi` — Scaffold + Certificado CCFE: Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** módulo `l10n_py_edi` instalable sobre `l10n_py_account` + `account_edi`, con gestión segura del certificado CCFE (PKCS#12 encriptado Fernet en `res.company`, key fuera de la BD) y helpers puros `services/crypto.py` + `services/certificate.py` testeables sin registry.

**Architecture:** módulo OCA-style. Secretos (p12, password, CSC) viven en `res.company` como **tokens Fernet en campos Text** nunca expuestos en vistas; la UI escribe vía campos compute/inverse write-only. La Fernet key se resuelve desde env var `L10N_PY_EDI_CCFE_KEY` o archivo apuntado por la opción de config `l10n_py_edi_ccfe_key_file` — **nunca desde la BD** (blueprint docs/60 §5). Helpers en `services/` son Python puro (sin imports de `odoo`), precedente `modulo11.py`.

**Tech Stack:** Odoo 18, Python 3.11, `cryptography` (Fernet + PKCS#12 + x509). `signxml`/`zeep`/`requests_pkcs12`/`qrcode`/`lxml` se declaran en manifest (los exige docs/66) pero PR-1 solo usa `cryptography`.

**Branch:** `feature/l10n_py_edi-scaffold` (desde `main`). PR a `main`.

**Decisiones tomadas en planning (no re-decidir):**

1. **Sin `security/ir.model.access.csv`** — PR-1 no crea modelos nuevos (solo campos en `res.company`). Deviation consciente vs. la lista de files de docs/66; un CSV vacío rompe pre-commit OCA.
2. Tokens Fernet en `fields.Text` con `groups="base.group_system"` (no `Binary`): el token ya es base64 URL-safe text.
3. Upload de certificado: campos `l10n_py_ccfe_certificate` (Binary no-stored) + `l10n_py_ccfe_password` (Char no-stored) con inverse compartido que **exige ambos en el mismo write**, valida el p12 (password correcta + vigencia), encripta y persiste tokens + metadata (`valid_from/valid_until/ruc`). Rotación de password = re-subir el p12.
4. CSC encriptado igual que el password (es secreto del hash QR). `l10n_py_csc_id` plano (no es secreto).
5. Certificado vencido se **rechaza al subir** (UserError). La validación de vigencia en runtime (al firmar) llega en PR-4/PR-6 vía `_check_move_configuration`.
6. Tests puros (`test_crypto`, `test_certificate`) usan `unittest.TestCase` + `@tagged("standard", "l10n_py")` para que el filtro CI `ODOO_TEST_TAGS=l10n_py` los seleccione (bug colateral detectado: `test_modulo11.py` no está tagueado y el CI probablemente no lo corre — NO arreglarlo en este PR, anotarlo en `BUGS_BACKLOG.md`).
7. `requirements.txt` nuevo en raíz del repo — la imagen OCA CI (`oca_install_addons`) lo instala automáticamente; `signxml`/`requests-pkcs12`/`zeep` no están en el mapping de setuptools-odoo.

**Comandos de test (desde repo root, container `l10n_py_odoo` corriendo):**

```bash
# Instalar deps python nuevas en el container dev (una vez por rebuild):
docker exec -u root l10n_py_odoo pip3 install --break-system-packages signxml zeep requests-pkcs12

# Primera instalación del módulo:
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -i l10n_py_edi --http-port=8079

# Correr tests del módulo:
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079
```

`--http-port=8079` evita el conflicto con la instancia dev viva en 8069. El exit code de odoo es 0 aun con tests fallados en algunos setups — **siempre** grepear el log: `failed`, `ERROR`, `FAIL` deben estar ausentes y debe aparecer `0 failed, 0 error(s)`.

---

## File Structure

```
requirements.txt                                  (NUEVO — raíz repo)
addons/l10n_py_edi/
├── __init__.py                                   (imports models; services NO se importa acá)
├── __manifest__.py
├── models/
│   ├── __init__.py
│   └── res_company.py                            (campos EDI + Fernet + getters/setters)
├── services/
│   ├── __init__.py                               (vacío con docstring — paquete puro, sin imports odoo)
│   ├── crypto.py                                 (Fernet helpers puros — blueprint docs/60 §5)
│   └── certificate.py                            (PKCS#12 load/validez/RUC — puro)
├── views/
│   └── res_company_views.xml                     (página SIFEN en form de company)
└── tests/
    ├── __init__.py
    ├── fixtures.py                               (generador de p12 self-signed — NUNCA commitear un .p12 real)
    ├── common.py                                 (L10nPyEdiTestCase)
    ├── test_crypto.py                            (puro)
    ├── test_certificate.py                       (puro)
    └── test_company_edi.py                       (TransactionCase post_install)
```

---

### Task 0: Branch + requirements.txt + docs del plan

**Files:**

- Create: `requirements.txt`
- Commit (ya existen, untracked): `docs/66_FASE_2_EDI_PLAN.md`, `docs/superpowers/plans/2026-06-10-l10n-py-edi-pr1-scaffold.md`
- Modify: `BUGS_BACKLOG.md` (agregar nota del bug colateral de tagging)

- [ ] **Step 1: Crear branch desde main actualizado**

```bash
git checkout main && git pull && git checkout -b feature/l10n_py_edi-scaffold
```

- [ ] **Step 2: Crear `requirements.txt` en la raíz del repo**

```text
# Python deps de los addons l10n_py_* que no están en el mapping de
# setuptools-odoo ni en los requirements de Odoo core.
# La imagen OCA CI (oca_install_addons) instala este archivo automáticamente.
signxml>=3.2
zeep>=4.2
requests-pkcs12>=1.25
```

(`lxml`, `cryptography`, `qrcode` ya vienen con Odoo 18 core — no duplicar.)

- [ ] **Step 3: Agregar nota a `BUGS_BACKLOG.md`** (al final de la lista existente, respetar formato del archivo):

```markdown
## test_modulo11.py sin @tagged("l10n_py") — probablemente excluido del CI

- **Detectado:** 2026-06-10, planning PR-1 l10n_py_edi.
- **Síntoma:** `addons/l10n_py_base/tests/test_modulo11.py` define
  `TestModulo11(unittest.TestCase)` sin decorator `@tagged`. Con
  `ODOO_TEST_TAGS="l10n_py"` en CI, el filtro selecciona solo tests con tag
  `l10n_py`, así que esta suite no corre en CI (sí corre localmente sin filtro).
- **Fix propuesto:** agregar `@tagged("standard", "l10n_py")` (import desde
  `odoo.tests`) y verificar en el log del CI que el conteo de tests sube.
- **Prioridad:** media — el algoritmo está cubierto indirectamente por
  test_ruc_validation, pero la suite directa quedó invisible.
```

- [ ] **Step 4: Commit**

```bash
git add requirements.txt docs/66_FASE_2_EDI_PLAN.md docs/superpowers/plans/2026-06-10-l10n-py-edi-pr1-scaffold.md BUGS_BACKLOG.md
git commit -m "chore(edi): add root requirements.txt + Fase 2 master plan + PR-1 plan"
```

---

### Task 1: Skeleton del módulo

**Files:**

- Create: `addons/l10n_py_edi/__manifest__.py`
- Create: `addons/l10n_py_edi/__init__.py`
- Create: `addons/l10n_py_edi/models/__init__.py`
- Create: `addons/l10n_py_edi/models/res_company.py` (stub)
- Create: `addons/l10n_py_edi/services/__init__.py`
- Create: `addons/l10n_py_edi/tests/__init__.py`
- Create: `addons/l10n_py_edi/views/res_company_views.xml` (placeholder)

- [ ] **Step 1: `__manifest__.py`**

```python
# Copyright 2026 Careaga Dev (Alberto Ezequiel Careaga <careagaezz@gmail.com>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0).
{
    "name": "Paraguay - EDI SIFEN",
    "version": "18.0.1.0.0",
    "category": "Accounting/Localizations/EDI",
    "license": "AGPL-3",
    "author": "Careaga Dev, Odoo Community Association (OCA)",
    "website": "https://github.com/Ezcareaga/l10n-paraguay",
    "countries": ["py"],
    "summary": (
        "Facturación electrónica SIFEN/e-Kuatia: CDC, XML firmado XAdES, "
        "envío a DNIT, KuDE y eventos."
    ),
    "depends": [
        "l10n_py_account",
        "account_edi",
    ],
    "external_dependencies": {
        "python": [
            "lxml",
            "cryptography",
            "signxml",
            "zeep",
            "qrcode",
            "requests_pkcs12",
        ],
    },
    "data": [
        "views/res_company_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
```

- [ ] **Step 2: `__init__.py` raíz del módulo**

```python
from . import models
```

(`services` NO se importa desde el `__init__` raíz: es un paquete puro importable on-demand — mismo patrón que permite usarlo sin registry.)

- [ ] **Step 3: `models/__init__.py`**

```python
from . import res_company
```

y el stub `models/res_company.py` (se reemplaza en Task 5):

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from odoo import models


class ResCompany(models.Model):
    _inherit = "res.company"
```

- [ ] **Step 4: `services/__init__.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Helpers Python puros (sin dependencias Odoo) para el EDI SIFEN.

Importables sin registry: ``from odoo.addons.l10n_py_edi.services import crypto``.
NO agregar imports de ``odoo`` en este paquete.
"""
```

- [ ] **Step 5: `tests/__init__.py`** — en este task queda **vacío** (solo header como comentario); los imports se agregan a medida que existan los test files (Tasks 2/4/5).

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
```

- [ ] **Step 6: `views/res_company_views.xml` placeholder mínimo válido** (se completa en Task 6):

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright 2026 Careaga Dev
     License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0). -->
<odoo>
</odoo>
```

- [ ] **Step 7: Instalar deps en el container e instalar el módulo limpio**

```bash
docker exec -u root l10n_py_odoo pip3 install --break-system-packages signxml zeep requests-pkcs12
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -i l10n_py_edi --http-port=8079
```

Expected: log termina con `Modules loaded` / sin `ERROR` ni `CRITICAL` ni warnings de manifest. Si falla `external_dependencies`, la dep falta en el container — reinstalar Step 7 línea 1.

- [ ] **Step 8: Commit**

```bash
git add addons/l10n_py_edi
git commit -m "feat(l10n_py_edi): module skeleton with manifest and deps"
```

---

### Task 2: `services/crypto.py` (TDD)

**Files:**

- Create: `addons/l10n_py_edi/services/crypto.py`
- Test: `addons/l10n_py_edi/tests/test_crypto.py`
- Modify: `addons/l10n_py_edi/tests/__init__.py`

- [ ] **Step 1: Escribir el test que falla**

`tests/__init__.py` pasa a contener:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from . import test_crypto
```

`tests/test_crypto.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de los helpers Fernet — Python puro, no requiere Odoo registry."""
import unittest

from odoo.tests import tagged

from odoo.addons.l10n_py_edi.services import crypto


@tagged("standard", "l10n_py")
class TestCrypto(unittest.TestCase):
    def test_generate_data_key_is_valid_fernet_key(self):
        key = crypto.generate_data_key()
        # Una key Fernet válida permite cifrar sin levantar excepción.
        token = crypto.encrypt_secret(b"payload", key)
        self.assertIsInstance(token, bytes)

    def test_roundtrip(self):
        key = crypto.generate_data_key()
        secret = b"\x00\x01binary p12 bytes\xff"
        token = crypto.encrypt_secret(secret, key)
        self.assertNotEqual(token, secret)
        self.assertEqual(crypto.decrypt_secret(token, key), secret)

    def test_decrypt_with_wrong_key_raises(self):
        token = crypto.encrypt_secret(b"data", crypto.generate_data_key())
        with self.assertRaises(crypto.DecryptionError):
            crypto.decrypt_secret(token, crypto.generate_data_key())

    def test_decrypt_garbage_token_raises(self):
        with self.assertRaises(crypto.DecryptionError):
            crypto.decrypt_secret(b"not-a-token", crypto.generate_data_key())

    def test_rotate_secret(self):
        old_key = crypto.generate_data_key()
        new_key = crypto.generate_data_key()
        token = crypto.encrypt_secret(b"ccfe", old_key)
        new_token = crypto.rotate_secret(token, old_key, new_key)
        self.assertEqual(crypto.decrypt_secret(new_token, new_key), b"ccfe")
        with self.assertRaises(crypto.DecryptionError):
            crypto.decrypt_secret(new_token, old_key)
```

- [ ] **Step 2: Correr y verificar que falla**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079 2>&1 | grep -E "test_crypto|ImportError|ModuleNotFound|failed|error"
```

Expected: FAIL/ImportError — `crypto` no existe todavía.

- [ ] **Step 3: Implementar `services/crypto.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Cifrado Fernet para secretos EDI (CCFE .p12, password, CSC).

Implementación del blueprint docs/60_SECURITY_BASELINE.md §5: los secretos se
almacenan en PostgreSQL solo como tokens Fernet; la data key vive FUERA de la
base de datos (env var o archivo — ver ``res.company._l10n_py_edi_get_fernet_key``).

Helper Python puro: no importa nada de ``odoo``.
"""
from cryptography.fernet import Fernet, InvalidToken, MultiFernet


class DecryptionError(Exception):
    """Token inválido o key incorrecta."""


def generate_data_key():
    """Genera una data key Fernet nueva (32 bytes URL-safe base64)."""
    return Fernet.generate_key()


def encrypt_secret(data, key):
    """Cifra ``data`` (bytes) con ``key``. Devuelve token Fernet (bytes)."""
    return Fernet(key).encrypt(data)


def decrypt_secret(token, key):
    """Descifra un token Fernet. Lanza :class:`DecryptionError` si no valida."""
    try:
        return Fernet(key).decrypt(token)
    except InvalidToken as exc:
        raise DecryptionError("Token Fernet inválido o key incorrecta") from exc


def rotate_secret(token, old_key, new_key):
    """Re-cifra ``token`` con ``new_key`` preservando el timestamp original.

    Patrón ``MultiFernet.rotate()`` del blueprint docs/60 para la rotación
    trimestral de data keys.
    """
    try:
        return MultiFernet([Fernet(new_key), Fernet(old_key)]).rotate(token)
    except InvalidToken as exc:
        raise DecryptionError("Token Fernet inválido o key incorrecta") from exc
```

- [ ] **Step 4: Correr y verificar verde**

Mismo comando del Step 2. Expected: las 5 pruebas de `TestCrypto` pasan, `0 failed`.

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_edi/services/crypto.py addons/l10n_py_edi/tests/test_crypto.py addons/l10n_py_edi/tests/__init__.py
git commit -m "feat(l10n_py_edi): Fernet crypto helpers per docs/60 blueprint"
```

---

### Task 3: Fixture generator de certificados (`tests/fixtures.py`)

**Files:**

- Create: `addons/l10n_py_edi/tests/fixtures.py`

No es código de producción — no lleva TDD propio; sus consumidores (Tasks 4-5) lo validan. **Nunca commitear un .p12 real**: todo certificado de test se genera en runtime con valores sintéticos (RUC de ejemplo del Manual SIFEN).

- [ ] **Step 1: Implementar `tests/fixtures.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Generación runtime de certificados PKCS#12 self-signed para tests.

NUNCA commitear un .p12 real al repo — los fixtures se generan acá.
"""
import datetime

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

DEFAULT_RUC = "80069563-1"


def make_test_p12(
    ruc=DEFAULT_RUC,
    password="test-password",
    not_before=None,
    not_after=None,
    serial_number_attr=True,
):
    """Genera un .p12 self-signed estilo CCFE paraguayo.

    :param ruc: RUC que se embebe como atributo serialNumber del subject
        con el prefijo ``RUC`` (formato usado por los PSC paraguayos).
    :param serial_number_attr: si es False, omite el atributo (para testear
        extracción fallida de RUC).
    :return: bytes del archivo PKCS#12.
    """
    now = datetime.datetime.now(datetime.timezone.utc)
    not_before = not_before or (now - datetime.timedelta(days=1))
    not_after = not_after or (now + datetime.timedelta(days=365))

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    attrs = [
        x509.NameAttribute(NameOID.COUNTRY_NAME, "PY"),
        x509.NameAttribute(NameOID.COMMON_NAME, "TEST CCFE l10n_py_edi"),
    ]
    if serial_number_attr:
        attrs.append(x509.NameAttribute(NameOID.SERIAL_NUMBER, "RUC" + ruc))
    subject = issuer = x509.Name(attrs)
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(not_before)
        .not_valid_after(not_after)
        .sign(key, hashes.SHA256())
    )
    return pkcs12.serialize_key_and_certificates(
        name=b"test-ccfe",
        key=key,
        cert=cert,
        cas=None,
        encryption_algorithm=serialization.BestAvailableEncryption(
            password.encode()
        ),
    )


def make_expired_p12(password="test-password"):
    """p12 cuyo certificado venció hace 30 días."""
    now = datetime.datetime.now(datetime.timezone.utc)
    return make_test_p12(
        password=password,
        not_before=now - datetime.timedelta(days=395),
        not_after=now - datetime.timedelta(days=30),
    )
```

- [ ] **Step 2: Commit** — junto con Task 4 (su primer consumidor), ver Task 4 Step 5.

---

### Task 4: `services/certificate.py` (TDD)

**Files:**

- Create: `addons/l10n_py_edi/services/certificate.py`
- Test: `addons/l10n_py_edi/tests/test_certificate.py`
- Modify: `addons/l10n_py_edi/tests/__init__.py`

- [ ] **Step 1: Escribir el test que falla**

`tests/__init__.py` pasa a:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from . import test_crypto
from . import test_certificate
```

`tests/test_certificate.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests del loader PKCS#12 — Python puro, no requiere Odoo registry."""
import datetime
import unittest

from odoo.tests import tagged

from odoo.addons.l10n_py_edi.services import certificate
from odoo.addons.l10n_py_edi.tests import fixtures


@tagged("standard", "l10n_py")
class TestCertificate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.password = "test-password"
        cls.p12 = fixtures.make_test_p12(password=cls.password)

    def test_load_pkcs12_ok(self):
        info = certificate.load_pkcs12(self.p12, self.password)
        self.assertIsNotNone(info.certificate)
        self.assertIsNotNone(info.private_key)
        self.assertEqual(info.ruc, "80069563-1")
        self.assertLess(info.not_valid_before, info.not_valid_after)

    def test_load_pkcs12_wrong_password(self):
        with self.assertRaises(certificate.CertificateLoadError):
            certificate.load_pkcs12(self.p12, "wrong")

    def test_load_pkcs12_garbage(self):
        with self.assertRaises(certificate.CertificateLoadError):
            certificate.load_pkcs12(b"garbage-not-a-p12", self.password)

    def test_ruc_missing_serial_number(self):
        p12 = fixtures.make_test_p12(
            password=self.password, serial_number_attr=False
        )
        info = certificate.load_pkcs12(p12, self.password)
        self.assertIsNone(info.ruc)

    def test_check_validity_ok(self):
        info = certificate.load_pkcs12(self.p12, self.password)
        # No debe lanzar:
        certificate.check_validity(info)
        self.assertTrue(certificate.is_valid(info))

    def test_check_validity_expired(self):
        p12 = fixtures.make_expired_p12(password=self.password)
        info = certificate.load_pkcs12(p12, self.password)
        with self.assertRaises(certificate.CertificateExpiredError):
            certificate.check_validity(info)
        self.assertFalse(certificate.is_valid(info))

    def test_check_validity_not_yet_valid(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        p12 = fixtures.make_test_p12(
            password=self.password,
            not_before=now + datetime.timedelta(days=10),
            not_after=now + datetime.timedelta(days=375),
        )
        info = certificate.load_pkcs12(p12, self.password)
        with self.assertRaises(certificate.CertificateNotYetValidError):
            certificate.check_validity(info)

    def test_check_validity_at_explicit_date(self):
        info = certificate.load_pkcs12(self.p12, self.password)
        future = datetime.datetime.now(
            datetime.timezone.utc
        ) + datetime.timedelta(days=400)
        with self.assertRaises(certificate.CertificateExpiredError):
            certificate.check_validity(info, at=future)
```

- [ ] **Step 2: Correr y verificar que falla**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079 2>&1 | grep -E "test_certificate|ImportError|failed|error"
```

Expected: ImportError — `certificate` no existe.

- [ ] **Step 3: Implementar `services/certificate.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Carga y validación del certificado CCFE (PKCS#12).

Helper Python puro (sin dependencias Odoo). Expone cert + private key para la
firma XAdES (PR-4) y para el canal mTLS con SIFEN (PR-5).

El RUC del titular se extrae del atributo ``serialNumber`` del subject
(formato PSC paraguayo: ``RUC80012345-7`` — campos F110/F211 del Manual
Técnico SIFEN).
"""
import datetime
import re
from dataclasses import dataclass

from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

RUC_IN_SUBJECT = re.compile(r"RUC\s*([0-9]{1,8}-?[0-9])", re.IGNORECASE)


class CertificateError(Exception):
    """Error genérico de certificado CCFE."""


class CertificateLoadError(CertificateError):
    """El .p12 no se pudo abrir (corrupto o password incorrecta)."""


class CertificateExpiredError(CertificateError):
    """El certificado está vencido."""


class CertificateNotYetValidError(CertificateError):
    """El certificado aún no entró en vigencia."""


@dataclass
class CertificateInfo:
    """Certificado CCFE cargado y listo para firmar."""

    certificate: x509.Certificate
    private_key: object
    not_valid_before: datetime.datetime
    not_valid_after: datetime.datetime
    ruc: str  # None si el subject no trae serialNumber RUC


def load_pkcs12(p12_bytes, password):
    """Abre un PKCS#12 y devuelve :class:`CertificateInfo`.

    :param p12_bytes: contenido binario del archivo .p12.
    :param password: password del archivo (str).
    :raises CertificateLoadError: archivo corrupto o password incorrecta.
    """
    try:
        key, cert, _additional = pkcs12.load_key_and_certificates(
            p12_bytes, password.encode() if password else None
        )
    except (ValueError, TypeError) as exc:
        raise CertificateLoadError(
            "No se pudo abrir el .p12: archivo inválido o password incorrecta"
        ) from exc
    if cert is None or key is None:
        raise CertificateLoadError("El .p12 no contiene certificado y clave")
    return CertificateInfo(
        certificate=cert,
        private_key=key,
        not_valid_before=cert.not_valid_before_utc,
        not_valid_after=cert.not_valid_after_utc,
        ruc=extract_ruc(cert),
    )


def extract_ruc(cert):
    """Extrae el RUC del atributo serialNumber del subject, o None."""
    attrs = cert.subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
    for attr in attrs:
        match = RUC_IN_SUBJECT.search(attr.value)
        if match:
            return match.group(1)
    return None


def check_validity(info, at=None):
    """Valida vigencia del certificado a la fecha ``at`` (default: ahora UTC).

    :raises CertificateExpiredError: vencido.
    :raises CertificateNotYetValidError: aún no vigente.
    """
    at = at or datetime.datetime.now(datetime.timezone.utc)
    if at > info.not_valid_after:
        raise CertificateExpiredError(
            "Certificado CCFE vencido el %s" % info.not_valid_after.date()
        )
    if at < info.not_valid_before:
        raise CertificateNotYetValidError(
            "Certificado CCFE vigente recién desde %s"
            % info.not_valid_before.date()
        )


def is_valid(info, at=None):
    """True si el certificado está vigente a la fecha ``at``."""
    try:
        check_validity(info, at=at)
    except CertificateError:
        return False
    return True
```

- [ ] **Step 4: Correr y verificar verde**

Mismo comando del Step 2. Expected: 8 tests de `TestCertificate` PASS, `0 failed`.

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_edi/services/certificate.py addons/l10n_py_edi/tests/test_certificate.py addons/l10n_py_edi/tests/fixtures.py addons/l10n_py_edi/tests/__init__.py
git commit -m "feat(l10n_py_edi): PKCS#12 certificate service with runtime test fixtures"
```

---

### Task 5: Campos EDI en `res.company` (TDD)

**Files:**

- Modify: `addons/l10n_py_edi/models/res_company.py` (reemplaza el stub de Task 1)
- Test: `addons/l10n_py_edi/tests/test_company_edi.py`
- Modify: `addons/l10n_py_edi/tests/__init__.py`

- [ ] **Step 1: Escribir el test que falla**

`tests/__init__.py` pasa a:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
from . import test_crypto
from . import test_certificate
from . import test_company_edi
```

`tests/test_company_edi.py`:

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Tests de los campos EDI encriptados en res.company."""
import base64
from unittest.mock import patch

from odoo.exceptions import UserError
from odoo.tests import tagged

from odoo.addons.l10n_py_account.tests.common import L10nPyAccountTestCase
from odoo.addons.l10n_py_edi.services import certificate, crypto
from odoo.addons.l10n_py_edi.tests import fixtures

KEY_ENV = "L10N_PY_EDI_CCFE_KEY"
TEST_CSC = "ABCD0000000000000000000000000000"


@tagged("post_install", "-at_install", "l10n_py")
class TestCompanyEdi(L10nPyAccountTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fernet_key = crypto.generate_data_key()
        env_patcher = patch.dict(
            "os.environ", {KEY_ENV: cls.fernet_key.decode()}
        )
        env_patcher.start()
        cls.addClassCleanup(env_patcher.stop)
        cls.password = "test-password"
        cls.p12 = fixtures.make_test_p12(password=cls.password)

    def _upload_cert(self, p12=None, password=None):
        self.company.write(
            {
                "l10n_py_ccfe_certificate": base64.b64encode(p12 or self.p12),
                "l10n_py_ccfe_password": password or self.password,
            }
        )

    def test_environment_default_test(self):
        self.assertEqual(self.company.l10n_py_edi_environment, "test")

    def test_upload_certificate_stores_encrypted(self):
        self._upload_cert()
        token = self.company.l10n_py_ccfe_certificate_token
        self.assertTrue(token)
        # El token NO es el p12 plano ni su base64:
        self.assertNotIn(base64.b64encode(self.p12).decode(), token)
        # Pero descifra al p12 original:
        self.assertEqual(
            crypto.decrypt_secret(token.encode(), self.fernet_key), self.p12
        )
        # Password también encriptada:
        self.assertEqual(
            crypto.decrypt_secret(
                self.company.l10n_py_ccfe_password_token.encode(),
                self.fernet_key,
            ).decode(),
            self.password,
        )

    def test_upload_certificate_sets_metadata(self):
        self._upload_cert()
        self.assertEqual(self.company.l10n_py_ccfe_ruc, "80069563-1")
        self.assertTrue(self.company.l10n_py_ccfe_valid_from)
        self.assertTrue(self.company.l10n_py_ccfe_valid_until)
        self.assertTrue(self.company.l10n_py_ccfe_loaded)

    def test_upload_without_password_raises(self):
        with self.assertRaises(UserError):
            self.company.write(
                {"l10n_py_ccfe_certificate": base64.b64encode(self.p12)}
            )

    def test_upload_wrong_password_raises(self):
        with self.assertRaises(UserError):
            self._upload_cert(password="wrong")

    def test_upload_expired_certificate_raises(self):
        expired = fixtures.make_expired_p12(password=self.password)
        with self.assertRaises(UserError):
            self._upload_cert(p12=expired)

    def test_upload_without_fernet_key_raises(self):
        with patch.dict("os.environ", {KEY_ENV: ""}):
            with self.assertRaises(UserError):
                self._upload_cert()

    def test_get_certificate_roundtrip(self):
        self._upload_cert()
        p12_bytes, password = self.company._l10n_py_edi_get_certificate()
        self.assertEqual(p12_bytes, self.p12)
        self.assertEqual(password, self.password)
        info = self.company._l10n_py_edi_get_certificate_info()
        self.assertIsInstance(info, certificate.CertificateInfo)
        self.assertEqual(info.ruc, "80069563-1")

    def test_get_certificate_without_upload_raises(self):
        with self.assertRaises(UserError):
            self.company._l10n_py_edi_get_certificate()

    def test_csc_encrypted_roundtrip(self):
        self.company.write({"l10n_py_csc": TEST_CSC, "l10n_py_csc_id": "0001"})
        self.assertTrue(self.company.l10n_py_csc_token)
        self.assertNotIn(TEST_CSC, self.company.l10n_py_csc_token)
        self.assertEqual(self.company._l10n_py_edi_get_csc(), TEST_CSC)
        self.assertEqual(self.company.l10n_py_csc_id, "0001")

    def test_inputs_are_write_only(self):
        self._upload_cert()
        # Los campos de input no persisten el secreto en claro:
        self.assertFalse(self.company.l10n_py_ccfe_certificate)
        self.assertFalse(self.company.l10n_py_ccfe_password)
        self.assertFalse(self.company.l10n_py_csc)

    def test_tokens_not_copied_on_duplicate(self):
        self._upload_cert()
        copy = self.company.copy({"name": "Copia PY"})
        self.assertFalse(copy.l10n_py_ccfe_certificate_token)
        self.assertFalse(copy.l10n_py_ccfe_loaded)
```

- [ ] **Step 2: Correr y verificar que falla**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079 2>&1 | grep -E "test_company_edi|failed|error"
```

Expected: FAIL — campos inexistentes.

- [ ] **Step 3: Implementar `models/res_company.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Campos EDI SIFEN en res.company: certificado CCFE encriptado + CSC.

Diseño de seguridad (docs/60 §5): los secretos se persisten SOLO como tokens
Fernet (campos *_token, groups system, nunca en vistas). La data key vive
fuera de la BD: env var L10N_PY_EDI_CCFE_KEY o archivo apuntado por la opción
de config l10n_py_edi_ccfe_key_file. Los campos visibles de upload son
compute/inverse write-only.
"""
import base64
import binascii
import os

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import config

from ..services import certificate, crypto

KEY_ENV_VAR = "L10N_PY_EDI_CCFE_KEY"
KEY_FILE_OPTION = "l10n_py_edi_ccfe_key_file"


class ResCompany(models.Model):
    _inherit = "res.company"

    l10n_py_edi_environment = fields.Selection(
        selection=[("test", "Test"), ("prod", "Producción")],
        string="Ambiente SIFEN",
        default="test",
        required=True,
    )
    # --- Inputs write-only (no almacenan el secreto en claro) -------------
    l10n_py_ccfe_certificate = fields.Binary(
        string="Certificado CCFE (.p12)",
        compute="_compute_ccfe_inputs",
        inverse="_inverse_l10n_py_ccfe",
        attachment=False,
        help="Subir junto con la contraseña. Se almacena encriptado (Fernet); "
        "el archivo nunca queda en claro en la base de datos.",
    )
    l10n_py_ccfe_password = fields.Char(
        string="Contraseña del CCFE",
        compute="_compute_ccfe_inputs",
        inverse="_inverse_l10n_py_ccfe",
    )
    l10n_py_csc = fields.Char(
        string="CSC (Código Secreto)",
        compute="_compute_csc_input",
        inverse="_inverse_l10n_py_csc",
        help="Código de Seguridad del Contribuyente para el QR del KuDE. "
        "Se almacena encriptado.",
    )
    l10n_py_csc_id = fields.Char(string="ID del CSC", size=4)
    # --- Tokens Fernet persistidos (nunca exponer en vistas) ---------------
    l10n_py_ccfe_certificate_token = fields.Text(
        readonly=True, copy=False, groups="base.group_system"
    )
    l10n_py_ccfe_password_token = fields.Text(
        readonly=True, copy=False, groups="base.group_system"
    )
    l10n_py_csc_token = fields.Text(
        readonly=True, copy=False, groups="base.group_system"
    )
    # --- Metadata visible (no sensible) ------------------------------------
    l10n_py_ccfe_valid_from = fields.Datetime(
        string="CCFE vigente desde", readonly=True, copy=False
    )
    l10n_py_ccfe_valid_until = fields.Datetime(
        string="CCFE vigente hasta", readonly=True, copy=False
    )
    l10n_py_ccfe_ruc = fields.Char(
        string="RUC del CCFE", readonly=True, copy=False
    )
    l10n_py_ccfe_loaded = fields.Boolean(
        string="CCFE cargado", compute="_compute_ccfe_loaded"
    )

    # ------------------------------------------------------------------
    # Computes / inverses
    # ------------------------------------------------------------------
    def _compute_ccfe_inputs(self):
        # Write-only: nunca devolver el secreto a la UI.
        for company in self:
            company.l10n_py_ccfe_certificate = False
            company.l10n_py_ccfe_password = False

    def _compute_csc_input(self):
        for company in self:
            company.l10n_py_csc = False

    @api.depends("l10n_py_ccfe_certificate_token")
    def _compute_ccfe_loaded(self):
        for company in self:
            # sudo: el token tiene groups system pero el flag es informativo.
            company.l10n_py_ccfe_loaded = bool(
                company.sudo().l10n_py_ccfe_certificate_token
            )

    def _inverse_l10n_py_ccfe(self):
        for company in self:
            cert_b64 = company.l10n_py_ccfe_certificate
            password = company.l10n_py_ccfe_password
            if not cert_b64 and not password:
                continue
            if not cert_b64 or not password:
                raise UserError(
                    _("Cargá el certificado .p12 y su contraseña juntos.")
                )
            try:
                p12_bytes = base64.b64decode(cert_b64)
            except (binascii.Error, ValueError) as exc:
                raise UserError(_("El archivo subido no es válido.")) from exc
            company.l10n_py_edi_set_certificate(p12_bytes, password)

    def _inverse_l10n_py_csc(self):
        for company in self:
            if company.l10n_py_csc:
                company.l10n_py_edi_set_csc(company.l10n_py_csc)

    # ------------------------------------------------------------------
    # Key management
    # ------------------------------------------------------------------
    @api.model
    def _l10n_py_edi_get_fernet_key(self):
        """Resuelve la data key Fernet desde fuera de la BD (docs/60 §5).

        Orden: env var L10N_PY_EDI_CCFE_KEY, después el archivo apuntado por
        la opción de config l10n_py_edi_ccfe_key_file.
        """
        key = os.environ.get(KEY_ENV_VAR)
        if not key:
            key_file = config.get(KEY_FILE_OPTION)
            if key_file and os.path.exists(key_file):
                with open(key_file, "rb") as handle:
                    key = handle.read().strip()
        if not key:
            raise UserError(
                _(
                    "No hay clave de cifrado configurada para el CCFE. "
                    "Definí la variable de entorno %(env)s o la opción "
                    "%(opt)s en el archivo de configuración de Odoo.",
                    env=KEY_ENV_VAR,
                    opt=KEY_FILE_OPTION,
                )
            )
        return key.encode() if isinstance(key, str) else key

    # ------------------------------------------------------------------
    # Setters / getters de secretos
    # ------------------------------------------------------------------
    def l10n_py_edi_set_certificate(self, p12_bytes, password):
        """Valida el .p12 y persiste cert + password encriptados."""
        self.ensure_one()
        key = self._l10n_py_edi_get_fernet_key()
        try:
            info = certificate.load_pkcs12(p12_bytes, password)
            certificate.check_validity(info)
        except certificate.CertificateLoadError as exc:
            raise UserError(
                _(
                    "No se pudo abrir el certificado: archivo inválido o "
                    "contraseña incorrecta."
                )
            ) from exc
        except certificate.CertificateError as exc:
            raise UserError(str(exc)) from exc
        self.sudo().write(
            {
                "l10n_py_ccfe_certificate_token": crypto.encrypt_secret(
                    p12_bytes, key
                ).decode(),
                "l10n_py_ccfe_password_token": crypto.encrypt_secret(
                    password.encode(), key
                ).decode(),
                "l10n_py_ccfe_valid_from": info.not_valid_before.replace(
                    tzinfo=None
                ),
                "l10n_py_ccfe_valid_until": info.not_valid_after.replace(
                    tzinfo=None
                ),
                "l10n_py_ccfe_ruc": info.ruc,
            }
        )

    def _l10n_py_edi_get_certificate(self):
        """Devuelve (p12_bytes, password) descifrados. Solo uso interno."""
        self.ensure_one()
        sudo_self = self.sudo()
        if not sudo_self.l10n_py_ccfe_certificate_token:
            raise UserError(
                _(
                    "La compañía %s no tiene certificado CCFE cargado.",
                    self.display_name,
                )
            )
        key = self._l10n_py_edi_get_fernet_key()
        try:
            p12_bytes = crypto.decrypt_secret(
                sudo_self.l10n_py_ccfe_certificate_token.encode(), key
            )
            password = crypto.decrypt_secret(
                sudo_self.l10n_py_ccfe_password_token.encode(), key
            ).decode()
        except crypto.DecryptionError as exc:
            raise UserError(
                _(
                    "No se pudo descifrar el CCFE: la clave de cifrado "
                    "configurada no corresponde al certificado almacenado."
                )
            ) from exc
        return p12_bytes, password

    def _l10n_py_edi_get_certificate_info(self):
        """Carga el CCFE almacenado y devuelve CertificateInfo listo para firmar."""
        p12_bytes, password = self._l10n_py_edi_get_certificate()
        return certificate.load_pkcs12(p12_bytes, password)

    def l10n_py_edi_set_csc(self, csc):
        self.ensure_one()
        key = self._l10n_py_edi_get_fernet_key()
        self.sudo().l10n_py_csc_token = crypto.encrypt_secret(
            csc.encode(), key
        ).decode()

    def _l10n_py_edi_get_csc(self):
        self.ensure_one()
        sudo_self = self.sudo()
        if not sudo_self.l10n_py_csc_token:
            raise UserError(
                _("La compañía %s no tiene CSC cargado.", self.display_name)
            )
        key = self._l10n_py_edi_get_fernet_key()
        try:
            return crypto.decrypt_secret(
                sudo_self.l10n_py_csc_token.encode(), key
            ).decode()
        except crypto.DecryptionError as exc:
            raise UserError(
                _(
                    "No se pudo descifrar el CSC: la clave de cifrado "
                    "configurada no corresponde al valor almacenado."
                )
            ) from exc
```

Nota para el implementador: verificar el patrón de `_()` con placeholders nombrados contra el uso existente en `l10n_py_account` (Odoo 18 acepta `_("... %(x)s", x=val)`); mantener consistencia con el repo. `config.get(...)` para opciones custom: si la opción no está en el config file devuelve None — comportamiento esperado.

- [ ] **Step 4: Correr y verificar verde**

Mismo comando del Step 2. Expected: 12 tests de `TestCompanyEdi` PASS, suites previas siguen verdes, `0 failed`.

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_edi/models/res_company.py addons/l10n_py_edi/tests/test_company_edi.py addons/l10n_py_edi/tests/__init__.py
git commit -m "feat(l10n_py_edi): encrypted CCFE certificate + CSC fields on res.company"
```

---

### Task 6: Vista de company + `tests/common.py`

**Files:**

- Modify: `addons/l10n_py_edi/views/res_company_views.xml` (reemplaza placeholder de Task 1)
- Create: `addons/l10n_py_edi/tests/common.py`
- Modify: `addons/l10n_py_edi/tests/test_company_edi.py` (smoke test del common)

- [ ] **Step 1: Completar `views/res_company_views.xml`**

```xml
<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright 2026 Careaga Dev
     License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0). -->
<odoo>
    <record id="view_company_form_l10n_py_edi" model="ir.ui.view">
        <field name="name">res.company.form.l10n.py.edi</field>
        <field name="model">res.company</field>
        <field name="inherit_id" ref="base.view_company_form"/>
        <field name="arch" type="xml">
            <xpath expr="//notebook" position="inside">
                <page string="SIFEN (EDI)" name="l10n_py_edi">
                    <group>
                        <group string="Ambiente">
                            <field name="l10n_py_edi_environment"/>
                        </group>
                        <group string="Certificado CCFE">
                            <field name="l10n_py_ccfe_loaded"/>
                            <field name="l10n_py_ccfe_certificate"/>
                            <field name="l10n_py_ccfe_password"
                                   password="True"/>
                            <field name="l10n_py_ccfe_ruc"/>
                            <field name="l10n_py_ccfe_valid_from"/>
                            <field name="l10n_py_ccfe_valid_until"/>
                        </group>
                        <group string="CSC (QR del KuDE)">
                            <field name="l10n_py_csc" password="True"/>
                            <field name="l10n_py_csc_id"/>
                        </group>
                    </group>
                </page>
            </xpath>
        </field>
    </record>
</odoo>
```

(Los campos `*_token` NO van en ninguna vista — regla de seguridad del plan.)

- [ ] **Step 2: Crear `tests/common.py`**

```python
# Copyright 2026 Careaga Dev
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
"""Fixture compartido para tests EDI: company PY + CCFE de prueba cargado."""
from unittest.mock import patch

from odoo.addons.l10n_py_account.tests.common import L10nPyAccountTestCase
from odoo.addons.l10n_py_edi.services import crypto
from odoo.addons.l10n_py_edi.tests import fixtures

TEST_CSC = "ABCD0000000000000000000000000000"


class L10nPyEdiTestCase(L10nPyAccountTestCase):
    """Company PY + chart + timbrado + PoE + certificado CCFE self-signed.

    El certificado se genera en runtime (tests/fixtures.py) — nunca hay un
    .p12 real en el repo. La Fernet key se inyecta por env var parcheada.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.fernet_key = crypto.generate_data_key()
        env_patcher = patch.dict(
            "os.environ", {"L10N_PY_EDI_CCFE_KEY": cls.fernet_key.decode()}
        )
        env_patcher.start()
        cls.addClassCleanup(env_patcher.stop)
        cls.ccfe_password = "test-password"
        cls.ccfe_p12 = fixtures.make_test_p12(password=cls.ccfe_password)
        cls.company.l10n_py_edi_set_certificate(cls.ccfe_p12, cls.ccfe_password)
        cls.company.l10n_py_edi_set_csc(TEST_CSC)
        cls.company.l10n_py_csc_id = "0001"
```

- [ ] **Step 3: Smoke-test del common — agregar al final de `tests/test_company_edi.py`:**

```python
@tagged("post_install", "-at_install", "l10n_py")
class TestEdiCommon(L10nPyEdiTestCase):
    def test_common_fixture_ready(self):
        self.assertTrue(self.company.l10n_py_ccfe_loaded)
        info = self.company._l10n_py_edi_get_certificate_info()
        self.assertEqual(info.ruc, "80069563-1")
        self.assertEqual(self.company._l10n_py_edi_get_csc(), COMMON_TEST_CSC)
```

con los imports correspondientes al tope del archivo:

```python
from odoo.addons.l10n_py_edi.tests.common import (
    TEST_CSC as COMMON_TEST_CSC,
    L10nPyEdiTestCase,
)
```

- [ ] **Step 4: Reinstalar con la vista + correr toda la suite**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_edi --test-tags=l10n_py --http-port=8079
```

Expected: instalación sin warnings de vista (xpath resuelve), todos los tests `l10n_py` verdes (los 97 previos + los nuevos), `0 failed`.

- [ ] **Step 5: Commit**

```bash
git add addons/l10n_py_edi/views/res_company_views.xml addons/l10n_py_edi/tests/common.py addons/l10n_py_edi/tests/test_company_edi.py
git commit -m "feat(l10n_py_edi): company SIFEN settings view + shared EDI test fixture"
```

---

### Task 7: Verificación final + pre-commit + PR

- [ ] **Step 1: Instalación limpia desde cero** (gate del paquete: "instalación limpia en l10n_py_dev sin warnings")

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -i l10n_py_edi --http-port=8079 2>&1 | grep -iE "warning|error|critical" || echo "CLEAN"
```

Expected: `CLEAN` (o solo warnings pre-existentes no atribuibles al módulo — anotar cuáles).

- [ ] **Step 2: Suite completa de los 3 módulos**

```bash
docker exec l10n_py_odoo odoo --stop-after-init -d l10n_py_dev -u l10n_py_base,l10n_py_account,l10n_py_edi --test-tags=l10n_py --http-port=8079
```

Expected: `0 failed, 0 error(s)` en el log final.

- [ ] **Step 3: Pre-commit sobre todo el repo**

```bash
pre-commit run --all-files
```

Expected: todo verde (oca-gen-addon-readme corre con `--keep-source-digest` ya configurado). Si pylint-odoo pide `readme/` fragments para el módulo nuevo, crear:

`addons/l10n_py_edi/readme/DESCRIPTION.md`:

```markdown
Facturación electrónica paraguaya (SIFEN / e-Kuatia) para Odoo 18:

- Gestión segura del certificado CCFE (PKCS#12 encriptado en reposo con
  Fernet; la clave de cifrado vive fuera de la base de datos).
- Configuración de ambiente (test/producción) y CSC por compañía.
- Base para CDC, XML firmado XAdES, envío a DNIT, KuDE y eventos
  (siguientes etapas de la Fase 2).
```

`addons/l10n_py_edi/readme/CONTRIBUTORS.md`:

```markdown
- Alberto Ezequiel Careaga \<careagaezz@gmail.com\>
```

y commitear el README.rst generado.

- [ ] **Step 4: Commit de ajustes de pre-commit (si los hay)**

```bash
git add -A addons/l10n_py_edi
git commit -m "chore(l10n_py_edi): pre-commit fixes + OCA readme fragments"
```

- [ ] **Step 5: Push + PR**

```bash
git push -u origin feature/l10n_py_edi-scaffold
gh pr create --base main --title "feat(l10n_py_edi): module scaffold + encrypted CCFE certificate management" --body "<resumen: scope PR-1 de docs/66_FASE_2_EDI_PLAN.md — scaffold, Fernet crypto per docs/60 §5, certificate service, company fields+view, L10nPyEdiTestCase. Tests nuevos: ~26. Sin tocar módulos existentes.>"
```

**Recordatorios de PR (memoria del proyecto):** no escribir `PR #N` en el body en posición de footer (commitlint trap); el repo exige conversation resolution antes de merge. **El merge lo aprueba el owner — no mergear.**

---

## Self-review checklist (ejecutada al escribir este plan)

- Spec coverage vs docs/66 PR-1: manifest ✅ (Task 1), campos company encriptados ✅ (Task 5), certificate service con vigencia + RUC + cert/key ✅ (Task 4), tests/common con cert self-signed runtime ✅ (Task 6), instalación limpia ✅ (Tasks 1/7), requests-pkcs12 en CI ✅ (Task 0 requirements.txt). `ir.model.access.csv` omitido a propósito (sin modelos nuevos — ver Decisión 1).
- Sin placeholders: todo step de código tiene el código completo.
- Consistencia de nombres verificada: `crypto.{generate_data_key,encrypt_secret,decrypt_secret,rotate_secret,DecryptionError}`, `certificate.{load_pkcs12,extract_ruc,check_validity,is_valid,CertificateInfo,CertificateLoadError,CertificateExpiredError,CertificateNotYetValidError,CertificateError}`, campos `l10n_py_*` idénticos entre modelo, tests y vista, `TEST_CSC` compartido entre common y tests.
