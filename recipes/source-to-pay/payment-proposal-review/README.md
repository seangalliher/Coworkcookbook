# Payment Proposal Review

Reviews the current payment proposal for accuracy and flags lines that need attention before release.

> ⚠ **Draft recipe — not yet verified.** The prompt, OOTB skill list, and plugin actions named below are starter content. No one has run this against a live Cowork tenant with the Dynamics 365 ERP plugin yet. Validate before relying on it.

## Business value

Stops payment-run mistakes - duplicates, blocked vendors, missed discounts - at the review stage instead of after the wire clears.

## What it does

Sanity-checks a payment proposal before release.

## Prerequisites

- Dynamics 365 F&SCM access with the Accounts payable role

## Step-by-step

1. Paste the prompt.
2. Review the workbook with the AP manager before releasing the proposal in D365.

## Expected output

Workbook with flagged proposal lines by category.

![Placeholder screenshot for Payment Proposal Review](screenshots/01-placeholder.svg "Placeholder — replace with a real screenshot captured against your tenant.")

## Skills used

OOTB: Excel
Plugin actions: dynamics-365-erp/data_find_entity_type, dynamics-365-erp/data_find_entities_sql

## License

CC-BY-4.0 — see repo `LICENSE`.
