# Planned Order Summary by Resource

Summarizes planned production orders by resource for the next four weeks, including load vs capacity.

> ⚠ **Draft recipe — not yet verified.** The prompt, OOTB skill list, and plugin actions named below are starter content. No one has run this against a live Cowork tenant with the Dynamics 365 ERP plugin yet. Validate before relying on it.

## Business value

Gives production planning a one-page view of where capacity is overcommitted, so the team can rebalance before missed promise dates pile up.

## What it does

Capacity-and-load view of the planned production schedule.

## Prerequisites

- Dynamics 365 F&SCM access with the Production role

## Step-by-step

1. Paste the prompt.
2. Use the workbook in production planning meetings.

## Expected output

Workbook with data + summary sheet.

![Placeholder screenshot for Planned Order Summary by Resource](screenshots/01-placeholder.svg "Placeholder — replace with a real screenshot captured against your tenant.")

## Skills used

OOTB: Excel
Plugin actions: dynamics-365-erp/data_find_entity_type, dynamics-365-erp/data_find_entities_sql

## License

CC-BY-4.0 — see repo `LICENSE`.
