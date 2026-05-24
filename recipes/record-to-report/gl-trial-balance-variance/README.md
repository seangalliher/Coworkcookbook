# GL Trial Balance Variance Report

Compares the current-period trial balance to the prior period and highlights GL accounts with material variances.

> ℹ **Tenant data caveat.** Validated end-to-end against a live Cowork tenant on 2026-05-23 with USMF demo data. Cowork executed the full 5-step plan (find trial balance entity → query March/February 2017 → compute variances → build workbook → draft email), produced 'TB-variance-2017-03.xlsx' with 8 material accounts and an 'All' sheet of 9 posting accounts, and saved a controller email draft summarizing the top 5 by absolute variance. Because USMF has no saved trial-balance snapshots for 2017, Cowork honestly derived the comparison from posted LedgerJournalLines activity rather than running balances — see the screenshot for the agent's note on this. For a tenant with running trial-balance snapshots you'll get period-end positions instead of period activity; both shapes are useful for variance review.

## Business value

Cuts month-end review time by focusing the controller on the GL accounts with material variances instead of every line in the trial balance.

## What it does

Pulls the trial balance for two consecutive periods, computes variance, flags material lines, and produces a workbook + email draft.

## Prerequisites

- Dynamics 365 F&SCM access with the General ledger user role
- Cowork D365 ERP plugin enabled

## Step-by-step

1. Open Cowork and paste the prompt.
2. Approve the read-only data access when prompted.
3. Review the produced workbook in the side panel.
4. Edit the email draft recipients before sending.

## Expected output

An Excel workbook with Material/All sheets and a draft email summarizing the top variances.

![Cowork output for GL Trial Balance Variance Report](screenshots/01-cowork-output.png "Captured against a live Cowork tenant on 2026-05-23.")

## Skills used

OOTB: Excel, Email
Plugin actions: dynamics-365-erp/data_find_entity_type, dynamics-365-erp/data_find_entities_sql

## License

CC-BY-4.0 — see repo `LICENSE`.
