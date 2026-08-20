The attached image is a workflow blueprint. Build and run it as an automated task using the Dynamics 365 ERP plugin. Follow the diagram exactly: execute each phase in the order shown, honour every decision diamond, and stop at a red halt node if its condition is met.

Do not ask me clarifying questions — every input is bound below.

## Input variables

- periodName: 2017-12
- legalEntity: USMF
- materialityThreshold: 10000

## Trigger

Trigger: monthly, business day 3

## Outputs

- close-readiness.xlsx — Summary, Unposted, Reconciliation, and FX sheets

## Notification

Email the readiness summary to me

## Guardrails

- Read only. Do not post journals, do not lock or close any period, do not run consolidation.
- Produce the workbook in this run — do not return a plan or a methodology document instead.
- Report readiness and differences; leave every close decision to me.

If an entity is not exposed to the plugin or the period has no posted activity, report exactly which check you could not run and why, list what you did complete, and stop. Do not fabricate balances.
