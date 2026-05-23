# Security Policy

## Reporting a Vulnerability

If you discover a security issue, **please do not file a public GitHub issue**.

Instead, report it privately via GitHub's "Report a vulnerability" feature:
https://github.com/seangalliher/Coworkcookbook/security/advisories/new

Or email **security@cowork-cookbook.example** (replace with the operator's real address before public launch).

We will:
- Acknowledge your report within 3 business days.
- Provide an estimated remediation timeline within 7 business days.
- Credit you in the advisory once the fix is published (unless you prefer to remain anonymous).

## Supported versions

This is a content repository; the most recent state of `main` is the only supported version.

## Scope

In-scope:
- Malicious content in recipes (e.g., prompt injection patterns aimed at harming users, leaking secrets, or attacking Cowork's host environment).
- Skill packages that exfiltrate data or execute hidden code.
- Issues with the CI workflows that could allow privilege escalation in this repo.

Out-of-scope:
- Vulnerabilities in Microsoft Cowork, Microsoft 365, or Dynamics 365 — please report those to Microsoft via https://msrc.microsoft.com/.
- Vulnerabilities in the web app or its hosting — those belong in https://github.com/seangalliher/CoworkCookBookWebApp.
