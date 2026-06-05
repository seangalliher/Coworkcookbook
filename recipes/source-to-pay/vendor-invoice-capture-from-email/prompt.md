Check the inbox for emails that have PDF attachments and look like vendor invoices. For each invoice PDF:

1. Download the PDF attachment.
2. Extract every available field from the invoice — vendor name, vendor account, invoice number, invoice date, due date, currency, PO reference, line items (item, description, quantity, unit price, line amount), subtotal, tax, freight/charges, and invoice total.
3. Match the vendor against existing USMF vendors in Dynamics 365 (by vendor account if present, otherwise by name). If no confident match exists, skip the create for that invoice and record the reason.
4. When the vendor is matched, create a pending vendor invoice record in the USMF legal entity in Dynamics 365 F&O using the D365 ERP data tools. Populate the header and lines with every value captured from the PDF — do not invent fields that are not present on the invoice.
5. Avoid duplicates: before creating, check whether a pending vendor invoice already exists in USMF for that vendor + invoice number, and skip if so. Also track processed message IDs across runs so the same email is not handled twice.
6. At the end of the run, summarize: how many invoice emails were found, how many records were created, and how many were skipped (with the reason).

If no invoice emails with PDF attachments are found, exit quietly with a one-line "no new vendor invoices" note.
