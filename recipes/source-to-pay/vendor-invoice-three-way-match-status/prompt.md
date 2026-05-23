Using the Dynamics 365 ERP plugin, pull all open vendor invoices posted in the last 30 days that
are NOT fully matched against a purchase order and goods receipt (i.e., where the three-way match
state is "partial" or "none"). For each, list:

- Vendor name and vendor account number
- Invoice number, invoice date, posting date
- Invoice total amount and currency
- Linked PO number (if any) and PO header total
- Linked goods-receipt status (received qty vs invoiced qty)
- Reason the three-way match is incomplete (missing PO, missing receipt, qty mismatch, price mismatch)

Group the results by vendor. Use the Excel skill to produce a workbook named
`AP-3way-match-status-<YYYY-MM-DD>.xlsx` with one sheet per vendor and a summary sheet.
Apply conditional formatting that highlights mismatches in red. Save the file to my
OneDrive Cowork output folder.

Then draft an email (do not send) to the AP team summarizing how many invoices are in each
mismatch reason, with the workbook attached.

Do not modify any data in Dynamics 365. This is a read-only validation report.
