18.0.1.0.0 (2026-05-25)
~~~~~~~~~~~~~~~~~~~~~~~~

* Initial release.
* PUC RG 49/14 (~140 cuentas leaf, ~80 activas default + 164 grupos jerárquicos
  para comercio/servicios)
* 6 taxes IVA + 1 tax group + modelo ``l10n_py.afectacion_iva``
* 5 records ``l10n_latam.document.type`` (códigos 1, 4, 5, 6, 7)
* Modelos ``l10n_py.timbrado`` y ``l10n_py.point_of_emission``
* Extensiones ``res.company``, ``account.journal``, ``account.move``,
  ``account.move.line``, ``account.tax``, ``l10n_latam.document.type``
* Sequence independiente por (journal, document_type) vía
  ``_get_last_sequence_domain`` override + custom unique index sin colisión
  entre doc_types con mismo formato de número
* Defensive checks: ``_get_starting_sequence`` y ``_post`` raise UserError
  claro si falta PoE en journal de ventas
* ``_post_init_hook`` defensivo para DBs preexistentes (desactiva
  use_documents en journals sin PoE y crea activity de seguimiento)
* Wizard de migración 3 modos (clean / assisted / coexist)
* Override ``_format_document_number`` para validar/normalizar PY a
  ``EEE-PPP-NNNNNNN``
* 74 tests (incluye smoke test E2E: compra + venta + cuadre IVA)
