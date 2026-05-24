# User Access Review & SoD Audit

Audits Dynamics 365 user accounts for segregation-of-duties conflicts, inactive accounts with active role assignments, and roles granted without recent login.

> ⚠ **Draft recipe — not yet verified.** The prompt, OOTB skill list, and plugin actions named below are starter content. No one has run this against a live Cowork tenant with the Dynamics 365 ERP plugin yet. Validate before relying on it.

## Business value

Reduces audit findings and insider-risk exposure by surfacing access drift (over-privileged accounts, ghost users, SoD conflicts) before the IT auditors do.

## What it does

Identifies user access risks (SoD conflicts, stale accounts, orphaned roles) and produces an auditor-ready workbook.

## Prerequisites

- Dynamics 365 F&SCM access with the System administrator or Security administrator role
- Cowork D365 ERP plugin enabled

## Step-by-step

1. Paste the prompt in Cowork.
2. Review the workbook with the IT security lead before remediating in D365.
3. (Optional) Schedule this task in Cowork to run weekly.

## Expected output

Workbook with categorized access findings and a draft summary email.

![Placeholder screenshot for User Access Review & SoD Audit](screenshots/01-placeholder.svg "Placeholder — replace with a real screenshot captured against your tenant.")

## Skills used

OOTB: Excel, Email
Plugin actions: dynamics-365-erp/data_find_entity_type, dynamics-365-erp/data_find_entities_sql

## License

CC-BY-4.0 — see repo `LICENSE`.
