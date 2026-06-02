# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 18.0.x  | ✅        |
| < 18.0  | ❌        |

Only the latest minor release of the 18.0 series receives security fixes.

## Reporting a Vulnerability

**Preferred channel:** Use [GitHub Security Advisories](https://github.com/Ezcareaga/l10n-paraguay/security/advisories/new)
— this keeps the report private and triggers the native CVE workflow.

**Fallback (no GitHub account):** Email `careagaezz@gmail.com` with subject
`[SECURITY] <brief description>`. Note: email is plaintext; do not include
production secrets in the initial report.

**Response SLA:**

- Confirmation within **72 hours**.
- Fix or mitigation within **30 days** for critical/high severity.
- Best-effort for lower severity.

## Security Update Process

1. Vulnerability confirmed → private advisory created on GitHub.
2. Fix developed in a private fork or branch.
3. Fix merged and tagged as a patch release `18.0.x.y.z`.
4. Advisory published and CVE assigned (if applicable).
5. Upstream OCA notified if the issue affects OCA modules.

## Acknowledgements

Security researchers who responsibly disclose vulnerabilities are credited in the
published advisory. View acknowledged reports at:
<https://github.com/Ezcareaga/l10n-paraguay/security/advisories>
