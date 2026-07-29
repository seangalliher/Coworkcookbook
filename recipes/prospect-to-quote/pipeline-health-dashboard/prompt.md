Using the Dynamics 365 Sales plugin, build an interactive pipeline dashboard.

Use search and describe to confirm the opportunity table and the columns for sales stage,
estimated value, estimated close date, created date, owner, and status. Do not guess column
names.

Run a read_query to establish the range of estimated close dates present, report it, and base
the dashboard's time axis on that real range rather than on today's date.

Scope to open opportunities owned by me or my team. Then produce a single self-contained HTML
file 'pipeline-health.html' — all CSS and JavaScript inline, no external dependencies, so it
works offline — containing:
- a header with total open pipeline value, opportunity count, average deal size, and the data
  range the dashboard covers
- a funnel or bar chart of value by sales stage, drawn as inline SVG
- a distribution of opportunities by age since creation
- a breakdown by owner
- a sortable detail table beneath the charts
- a colour-coded indicator highlighting stages where value is concentrated or deals are aging

Use a readable, professional visual style. Make sure the file renders correctly when opened
directly from disk.

Do not modify any data. If there are no open opportunities, say so and stop.
