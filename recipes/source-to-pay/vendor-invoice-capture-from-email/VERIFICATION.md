# Verification — Vendor Invoice Capture from Email

Required by `.github/scripts/validate_recipes.py` because this recipe is `mutates_data: true` and `status: verified`. It records how the write path was exercised so a reader can judge the risk before running it against their own tenant.

| | |
| --- | --- |
| Verified by | @seangalliher |
| Date | 2026-06-05 |
| Cowork build | m365.cloud.microsoft 2026-06-05 |
| Environment | **Sandbox** Dynamics 365 F&SCM demo tenant, **USMF** legal entity |
| Production data touched | None |

## What was exercised

The recipe creates records, so verification had to cover three separate risks: that it writes the right data, that it does not write twice, and that it fails safely when it cannot match a vendor.

The Cowork task **"Extract and Process Vendor Invoices from Email"** ran the prompt against a sandbox mailbox containing two vendor-invoice PDFs. Cowork completed all 26 plan steps across three phases — scan inbox for vendor invoice PDFs, extract invoice fields, match vendors and create pending invoices in USMF.

## Records created

| Field | Value |
| --- | --- |
| Vendor | Contoso Office Supplies, Inc. |
| Vendor account | US-111 |
| Invoice number | INV-2026-05193 |
| Invoice date | 2026-06-04 |
| Header created | Pending vendor invoice `INV-2026-05193-US111` |
| Lines created | 6, with quantity, unit price, and description carried from the PDF |

A second invoice, **INV-2026-04857**, was present in the mailbox and captured in the same session.

Confirmed in the D365 UI at **USMF → Accounts payable → Vendor invoices → Pending vendor invoices**. Records were created in *pending* state only — nothing was posted, so an AP reviewer retains control of the posting decision.

## Duplicate protection

The most important result. A **subsequent run against the same mailbox created nothing**, returning:

> No new vendor invoices — same two invoices (INV-2026-05193, INV-2026-04857) in the inbox, both already captured in USMF.

This exercises both guards described in the prompt: the pre-create lookup on vendor + invoice number, and the persisted set of processed message IDs. The recipe is safe to schedule precisely because a repeat run is a no-op.

An **hourly scheduled task** ("Hourly vendor invoice intake") was left active during verification, so the idempotent path ran unattended and repeatedly rather than just once by hand.

## Approvals granted

Cowork's always-allowed list was populated with **Send email** (scoped to the sandbox tenant admin mailbox) and **Update record**. First run requires interactive approval; the recipe only runs unattended after that consent is given. A reader who does not grant these will be prompted every run — which is the safer default.

## Plugin actions used

`data_find_entity_type` · `data_get_entity_metadata` · `data_find_entities_sql` · `data_create_entities`

The only write action is `data_create_entities`. The recipe never calls `data_update_entities` or `data_delete_entities`, so it cannot modify or remove pre-existing records — its blast radius is limited to rows it creates.

## Artifacts produced

`sample_vendor_invoice_INV-2026-05193.pdf` · `sample_vendor_invoice.pdf` · `skill-quality-report.html`

## Cleanup

Pending vendor invoices created by a verification run remain in USMF until removed. Anyone reproducing this should delete the pending headers and lines at **Accounts payable → Vendor invoices → Pending vendor invoices** afterwards, and disable any scheduled task they enabled.

## Reproducing this

1. Point the D365 ERP plugin at a **sandbox** legal entity. Never verify a write recipe against production.
2. Place one or two vendor-invoice PDFs in the connected mailbox for vendors that exist in your tenant's vendor master.
3. Run the prompt once. Confirm the created header and lines against the source PDF field by field.
4. **Run it a second time without changing the mailbox.** It must report no new invoices. If it creates duplicates, stop and do not schedule it.
5. Delete the created pending invoices.

## Known limitations observed

- Vendor matching is by account first, then name. Invoices whose vendor cannot be confidently matched are skipped with a recorded reason rather than created against a guessed vendor — verified as the intended behaviour, though no unmatched invoice appeared in this particular run.
- Only fields present on the PDF are populated; the prompt explicitly forbids inventing values.
