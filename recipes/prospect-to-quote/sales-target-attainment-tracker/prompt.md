Using the Dynamics 365 Sales plugin, report attainment against sales targets.

Use search and describe to look for how targets are represented in this environment — that may
be a goal or quota table, a target field on the user or team record, or something custom.
Report exactly what you found. If this environment records no targets at all, say so plainly,
report actual performance on its own, and stop rather than inventing a target.

Confirm the opportunity table and the columns for status, actual or estimated value, close date,
and owner. Run a read_query to establish the range of close dates available and report it, then
pick the most recent complete period inside that range and state your choice.

For that period, and scoped to me and my team, report:
- closed-won value, against target where a target exists
- attainment percentage and absolute gap
- open pipeline value with a close date inside the period, and the resulting coverage ratio
- a per-owner breakdown of the same figures

Produce an Excel workbook 'target-attainment.xlsx' with a Summary sheet, a By Owner sheet, and a
Notes sheet naming where the target figures came from.

Do not modify any data.
