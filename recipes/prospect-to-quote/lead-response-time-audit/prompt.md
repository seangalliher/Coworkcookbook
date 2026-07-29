Using the Dynamics 365 Sales plugin, audit how quickly leads are being worked.

Use search and describe to confirm the lead table and the columns for created date, owner,
status, rating, and any first-contact or first-activity indicator available. Also check for a
related activity table that records the first touch. Do not guess column names — report what
you find and what you could not find.

Run a read_query to establish the range of lead creation dates present, report it, and choose an
analysis window inside that range — prefer the most recent three months of real data rather
than the current calendar date. State the window you chose.

Scope to leads owned by me or by my team. For each lead in the window, compute the elapsed time
from creation to first recorded activity. Where no activity exists, compute age since creation
and mark it untouched.

Produce an Excel workbook 'lead-response-audit.xlsx' with:
- a Summary sheet: median and 90th-percentile response time, plus a count of untouched leads
- a Response Times sheet, slowest first
- an Untouched sheet, oldest first
- a Notes sheet naming the tables and columns used and the window analyzed

Do not modify any data. If no leads exist in the window, report that and stop.
