---
name: vendor-invoice-capture
description: >-
  Capture vendor invoices from email PDF attachments into Dynamics 365 USMF as
  pending vendor invoices, including sales-tax application. Use when the user
  says "capture vendor invoices", "process invoice emails", "intake invoices
  from my inbox", "enter this invoice in D365", "create a pending vendor
  invoice", "add tax to that invoice", or runs the recurring invoice-intake
  task. Do NOT use for customer/AR invoices, posting/settling invoices, or
  purchase-order creation.
cowork:
  category: automation
  icon: DocumentText
---

# vendor-invoice-capture

## When to Use

Activate when the user wants to turn vendor invoices (usually PDF attachments in
email) into **pending vendor invoices** in Dynamics 365 F&O, legal entity
**USMF** — or to apply **sales tax** to an invoice already created. Trigger
phrases: "capture/process/intake vendor invoices", "invoice from my inbox",
"enter this invoice in D365", "create a pending vendor invoice", "add tax to
that invoice".

## When NOT to Use

- Customer / accounts-receivable invoices (this is AP only).
- Posting, settling, or paying an invoice — capture creates a *pending* invoice only.
- Creating purchase orders or product receipts.
- Non-USMF legal entities without confirming scope first.

## Email → D365 Intake Workflow

1. **Find candidate emails.** Look in the inbox for messages with PDF
   attachments that look like vendor invoices. Download each PDF.
2. **Extract every field** from the PDF — do not invent any:
   - Header: vendor name, vendor account, invoice number, invoice date, due
     date, currency, PO reference.
   - Lines: item number/SKU, description, qty, unit, unit price, line amount.
   - Totals: subtotal, tax, freight, invoice total.
3. **Match the vendor** against USMF vendors — by vendor account first, else by
   name (query `VendVendorV2` / vendor master). If no confident match, **skip**
   and record the reason. Never guess a vendor account.
4. **Dedup before creating.** Query `VendorInvoiceHeaders` by the
   **`InvoiceNumber` column** (and confirm `InvoiceAccount` = the matched
   vendor) — do **not** dedup by reconstructing the expected `HeaderReference`.
   Real USMF data shows `HeaderReference` naming is inconsistent (e.g.
   `INV-2026-04857` carried no vendor suffix while `INV-2026-05193-US111` did),
   so a HeaderReference-existence check misses live duplicates. Track processed
   message IDs so the same email is never captured twice (one invoice often
   arrives as several near-identical emails).

   Working dedup query:

   ```sql
   SELECT TOP 20 h.HeaderReference, h.InvoiceNumber, h.InvoiceAccount, h.InvoiceDate
   FROM VendorInvoiceHeaders h
   WHERE h.InvoiceNumber = 'INV-2026-04857'
   ```
5. **Create the header** in `VendorInvoiceHeaders` (keys `dataAreaId` +
   `HeaderReference`). Use a stable `HeaderReference` like
   `{InvoiceNumber}-{VendorAcct}` (e.g. `INV-2026-05193-US111`).
6. **Create the lines** in `VendorInvoiceLines` (see Line Shape below).
7. **Apply sales tax** (see Tax section).
8. **Summarize** counts: found / created / skipped (with reasons). If nothing
   qualifies, exit quietly with "no new vendor invoices".

## D365 data-tool discipline (mandatory)

- Sequence every entity interaction: `data_find_entity_type` →
  `data_get_entity_metadata` → CRUD. Never guess entity or field names.
- Plural `EntitySetName` in OData paths. No deep insert (create header, then
  lines separately).
- Reads via `data_find_entities_sql`: always `SELECT TOP N`, table + column
  aliases, never `SELECT *`. `companyId="USMF"`.

## Vendor invoice LINE shape

Key fields on `VendorInvoiceLines` (keys `dataAreaId` + `HeaderReference` +
`InvoiceLineNumber`):

- `LineType` = `"Standard"` (enum PurchInvoiceLineType).
- Quantity field is **`ReceiveNow`** (NOT `Quantity`).
- Price field is **`UnitPrice`**.
- **Never set `Amount`** — D365 derives the extended amount.
- `LineDescription` — put the human description here, and **always append the
  vendor SKU** in parentheses so it survives even when the item can't be matched.

### Item vs. procurement category (KEY LEARNING)

USMF generally does **not** carry external vendor SKUs (e.g. `OFC-*`) as released
products. Before using `ItemNumber`, verify it exists in **`ReleasedProductsV2`**
(field `ItemNumber`). If it does **not** resolve, the create will fail with
*"...is not found in the related table 'Items'."*

**Fallback:** omit `ItemNumber` and set **`ProcurementCategoryName`** instead,
choosing the closest leaf category from `ProcurementProductCategories` (field
`CategoryName`). Keep the original SKU inside `LineDescription`.

Working example payload (procurement-category shape that succeeds):

```json
[{"dataAreaId":"USMF","HeaderReference":"INV-2026-05193-US111","InvoiceLineNumber":1,
  "LineType":"Standard","ProcurementCategoryName":"Pen or pencil sets",
  "LineDescription":"Ballpoint pens, black, box of 12 (OFC-PEN-BLK-12)",
  "ReceiveNow":15,"UnitPrice":5.99}]
```

## Sales tax (KEY LEARNING)

D365 **calculates** sales tax from the combination of a **sales tax group** and
an **item sales tax group** on each line — you do **not** enter a flat tax
amount. After lines exist, set on each `VendorInvoiceLine`:

- `SalesTaxGroup` — a code from **`TaxGroups`** (field `TaxGroupCode`). Choose by
  the bill-to state, e.g. `TX` (Texas) for a Houston bill-to, `CO` (Colorado).
- `ItemSalesTax` — a code from **`TaxItemGroups`** (field `TaxItemGroupCode`),
  e.g. `ALL` (All sales tax codes).

Working update payload:

```json
[{"ODataPath":"VendorInvoiceLines(dataAreaId='usmf',HeaderReference='INV-2026-05193-US111',InvoiceLineNumber=1)",
  "UpdatedFieldValues":{"SalesTaxGroup":"TX","ItemSalesTax":"ALL"}}]
```

**Tell the user** the D365-computed tax may differ from the tax printed on the
PDF, because it derives from USMF tax-rate setup rather than the vendor's rate.

## Field-name gotchas (memorize)

| Need | Entity | Field |
|------|--------|-------|
| Dedup / invoice number | `VendorInvoiceHeaders` | `InvoiceNumber` |
| Vendor on the header | `VendorInvoiceHeaders` | `InvoiceAccount` |
| Item existence check | `ReleasedProductsV2` | `ItemNumber` |
| Procurement category | `ProcurementProductCategories` | `CategoryName` |
| Sales tax group code | `TaxGroups` | `TaxGroupCode` |
| Item sales tax code | `TaxItemGroups` | `TaxItemGroupCode` |
| Line quantity | `VendorInvoiceLines` | `ReceiveNow` |

Discover code fields via `data_get_entity_metadata` — a naive `SELECT TaxGroup`
returns only Description + RecId with the code blank.

## Guardrails

- Never invent vendor accounts, item numbers, tax codes, or amounts.
- Capture creates *pending* invoices only — never post or pay.
- Dedup on vendor + invoice number before every create.
- If extraction is incomplete, capture what's certain and flag the gaps; don't
  fabricate the missing fields.
