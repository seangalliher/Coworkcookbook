# Vendor Master Cleanup Report

Identifies duplicate, incomplete, or inactive vendors in the master record and proposes a cleanup plan.

> ⚠ **Draft recipe — not yet verified.** The prompt, OOTB skill list, and plugin actions named below are starter content. No one has run this against a live Cowork tenant with the Dynamics 365 ERP plugin yet. Validate before relying on it.

## Business value

Reduces duplicate payments and tax-reporting errors by tightening the vendor master before bad data propagates into invoicing and 1099s.

## What it does

Finds dirty vendor records and suggests a triage list.

## Prerequisites

- Dynamics 365 F&SCM access with the Accounts payable role

## Step-by-step

1. Paste the prompt in Cowork.
2. Review the workbook; merge or update vendors directly in D365 as needed.

## Expected output

Workbook with categorized vendor-master issues.

![Placeholder screenshot for Vendor Master Cleanup Report](screenshots/01-placeholder.svg "Placeholder — replace with a real screenshot captured against your tenant.")

## Skills used

OOTB: Excel
Plugin actions: dynamics-365-erp/data_find_entity_type, dynamics-365-erp/data_find_entities_sql

## License

CC-BY-4.0 — see repo `LICENSE`.
