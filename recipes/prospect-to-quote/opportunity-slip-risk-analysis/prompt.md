Using the Dynamics 365 Sales plugin, analyze my open opportunities and identify the ones at
risk of slipping.

First, use search and describe to confirm the opportunity table and the columns for estimated
close date, estimated value, sales stage, owner, status, and last modified date. Do not guess
column names.

Then run a read_query to find the range of estimated close dates across my open opportunities
and report that range before you filter on it.

Scope to opportunities where I am the owner and the status is open. For each one, compute days
since last modified and days until estimated close. Flag an opportunity as at risk when any of
these hold:
- the estimated close date is already in the past
- there has been no modification in more than 30 days
- the estimated close is within 30 days but the sales stage is still an early one

Produce an Excel workbook 'opportunity-slip-risk.xlsx' with:
- a Summary sheet showing counts and total estimated value by risk reason
- an At Risk sheet sorted by estimated value descending, one row per opportunity, with the risk
  reasons that fired
- a Notes sheet listing which tables and columns you used and the date range you found

Do not modify any data. If I own no open opportunities, say so plainly and stop.
