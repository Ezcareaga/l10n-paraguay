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
import os

from cryptography.fernet import Fernet

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
    l10n_py_ccfe_ruc = fields.Char(string="RUC del CCFE", readonly=True, copy=False)
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
                raise UserError(_("Cargá el certificado .p12 y su contraseña juntos."))
            try:
                p12_bytes = base64.b64decode(cert_b64)
            except ValueError as exc:
                raise UserError(_("El archivo subido no es válido.")) from exc
            company.l10n_py_edi_set_certificate(p12_bytes, password)
            # Limpiar caché ORM: los campos de input son write-only, el compute
            # devuelve False; forzar la invalidación para que el ORM no sirva
            # el valor escrito en lugar del resultado del compute.
            company.invalidate_recordset(
                ["l10n_py_ccfe_certificate", "l10n_py_ccfe_password"]
            )

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
        key = key.encode() if isinstance(key, str) else key
        try:
            # Valida formato (32 bytes url-safe base64) sin cifrar nada.
            Fernet(key)
        except ValueError as exc:
            raise UserError(
                _(
                    "La clave de cifrado del CCFE configurada no es una key "
                    "Fernet válida (32 bytes url-safe base64)."
                )
            ) from exc
        return key

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
                "l10n_py_ccfe_valid_from": info.not_valid_before.replace(tzinfo=None),
                "l10n_py_ccfe_valid_until": info.not_valid_after.replace(tzinfo=None),
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
                    "La compañía %(name)s no tiene certificado CCFE cargado.",
                    name=self.display_name,
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
        """Persiste el CSC encriptado con Fernet."""
        self.ensure_one()
        key = self._l10n_py_edi_get_fernet_key()
        self.sudo().l10n_py_csc_token = crypto.encrypt_secret(
            csc.encode(), key
        ).decode()

    def _l10n_py_edi_get_csc(self):
        """Devuelve el CSC descifrado. Solo uso interno."""
        self.ensure_one()
        sudo_self = self.sudo()
        if not sudo_self.l10n_py_csc_token:
            raise UserError(
                _(
                    "La compañía %(name)s no tiene CSC cargado.",
                    name=self.display_name,
                )
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
