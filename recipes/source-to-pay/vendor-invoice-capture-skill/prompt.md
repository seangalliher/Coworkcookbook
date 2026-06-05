Trigger the packaged `vendor-invoice-capture` skill against the connected mailbox and Dynamics 365 (USMF). The skill encapsulates the full intake workflow: inbox scan, PDF extraction, USMF vendor match, duplicate guard, pending vendor invoice creation, and a summary report.

Example trigger phrases — any of these will hand off to the skill:

- capture vendor invoices from my inbox
- process invoice emails
- enter this invoice in D365
- create a pending vendor invoice
- add tax to that invoice

When invoked the skill will:

1. List unread mail with PDF attachments that look like invoices.
2. Extract every field present on each PDF.
3. Match the vendor against USMF vendors in D365 (by account, then by name).
4. Skip duplicates by checking pending invoices and processed message IDs.
5. Create a pending VendorInvoiceHeader plus VendorInvoiceLine rows for matched vendors.
6. Return a run summary: emails found, records created, skips with reasons.

If no qualifying invoice emails are present, the skill exits with a single-line "no new vendor invoices" note.
