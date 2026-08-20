The attached image is a workflow blueprint. Build and run it as an automated task using the Dynamics 365 ERP plugin. Follow the diagram exactly: execute each phase in the order shown, honour every decision diamond, and stop at a red halt node if its condition is met.

Do not ask me clarifying questions — every input is bound below.

## Input variables

- legalEntity: USMF
- asOfDate: 2017-12-31
- vacancyAgeDays: 90

## Trigger

Trigger: weekly, Monday morning

## Outputs

- position-readiness.xlsx — Vacancies, Stale, Pipeline, and Onboarding sheets

## Notification

Email the staffing summary to me

## Guardrails

- Read only. Do not create or modify positions, workers, or onboarding checklists.
- Produce the workbook in this run — do not return a plan or a methodology document instead.
- Do not include compensation figures or any other sensitive personal data in the output.

If position or onboarding entities are not exposed to the plugin, report exactly which check you could not run and why, list what you did complete, and stop. Do not infer vacancies from the worker roster alone.
