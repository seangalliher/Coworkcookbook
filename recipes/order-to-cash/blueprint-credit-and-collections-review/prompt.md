The attached image is a workflow blueprint. Build and run it as an automated task using the Dynamics 365 ERP plugin. Follow the diagram exactly: execute each phase in the order shown, honour every decision diamond, and stop at a red halt node if its condition is met.

Do not ask me clarifying questions — every input is bound below.

## Input variables

- legalEntity: USMF
- asOfDate: 2023-11-30
- riskThreshold: 80

## Trigger

Trigger: weekly, Monday morning

## Outputs

- credit-collections-review.xlsx — At-risk, On-hold, Aging, and Worklist sheets

## Notification

Email the collections worklist to me

## Guardrails

- Read only. Do not place or release credit holds, do not post interest, do not contact customers.
- Produce the workbook in this run — do not return a plan or a methodology document instead.
- Rank and recommend; leave every collections decision to me.

If credit limits or aging buckets are not available from the plugin, report exactly which check you could not run and why, list what you did complete, and stop. Do not estimate balances you could not read.
