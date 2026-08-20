The attached image is a workflow blueprint. Build and run it as an automated task using the Dynamics 365 ERP plugin. Follow the diagram exactly: execute each phase in the order shown, honour every decision diamond, and stop at a red halt node if its condition is met.

Do not ask me clarifying questions — every input is bound below.

## Input variables

- legalEntity: USMF
- fiscalYear: 2017
- concentrationThreshold: 20

## Trigger

Trigger: quarterly, first business day

## Outputs

- procurement-spend-review.xlsx — Spend, Concentration, Payables, and Risk sheets

## Notification

Email the spend summary to me

## Guardrails

- Read only. Do not create or modify vendors, purchase orders, or invoices.
- Produce the workbook in this run — do not return a plan or a methodology document instead.
- Report concentration and exposure; leave every sourcing decision to me.

USMF may have no vendor invoice records at all. If purchase or payable data is missing, say so explicitly, name the entity you queried, list what you could read from the vendor master, and stop. Do not infer spend from vendor records alone.
