# Production Cost Variance Report

Compares standard cost to actual cost on completed production orders and highlights material variances.

> ⚠ **Draft recipe — not yet verified.** The prompt, OOTB skill list, and plugin actions named below are starter content. No one has run this against a live Cowork tenant with the Dynamics 365 ERP plugin yet. Validate before relying on it.

## Business value

Identifies where standards are drifting from reality so engineering and cost accounting can fix the root cause, not just absorb the variance.

## What it does

Quantifies and flags production cost variance for completed orders.

## Prerequisites

- Dynamics 365 F&SCM access with the Production role

## Step-by-step

1. Paste the prompt.
2. Review with the production controller.

## Expected output

Workbook with variances by category.

![Placeholder screenshot for Production Cost Variance Report](screenshots/01-placeholder.svg "Placeholder — replace with a real screenshot captured against your tenant.")

## Skills used

OOTB: Excel
Plugin actions: dynamics-365-erp/data_find_entity_type, dynamics-365-erp/data_find_entities_sql

## License

CC-BY-4.0 — see repo `LICENSE`.
