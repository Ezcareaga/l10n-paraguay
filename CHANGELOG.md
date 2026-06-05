# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.1.0] - Unreleased (see Phase 4 REL-05 for tag date)

### Added

- `l10n_py_base 18.0.1.1.0` — Paraguayan localization base module: SIFEN/DNIT
  catalogs (departments, districts, cities, economic regimes, taxpayer types),
  `l10n_py.timbrado` model, `res.company` PY fiscal extension, RUC/CI validation
  (módulo 11 algorithm), 23 tests
- `l10n_py_account 18.0.1.0.0` — Chart of accounts, IVA taxes (10%/5%/exenta),
  `l10n_latam.document.type` records for Paraguay (FE/NC/ND/NR),
  `account.journal` timbrado extension, 74 tests
- CI/CD pipeline: GitHub Actions lint + test (OCA py3.10/PG12 matrix) +
  commitlint + dependabot
- Security workflow: gitleaks (secret scanning) + Bandit (SAST) +
  Dependency Review
- `SECURITY.md` — vulnerability reporting channel (GitHub Advisories + email)
- `docs/60_SECURITY_BASELINE.md` — 6-axis security blueprint
- `docs/61_COMPLIANCE_LEY_7593.md` — Ley 7593/2025 compliance framework

### Changed

- Branch protection on `main` — PR required, 6 status checks enforced
- `README.md` restructured to OCA-style evaluator-first format
- Initial CI sanity check established (Phase 1 of milestone Pre-Fase 2 Foundation)

[0.1.0]: https://github.com/Ezcareaga/l10n-paraguay/releases/tag/v0.1.0
