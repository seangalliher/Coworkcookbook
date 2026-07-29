Using the Dynamics 365 Sales plugin, track my outstanding quotes and their follow-up status.

Use search and describe to confirm the quote table and the columns for status, effective or
expiry dates, total amount, owner, related account, and related opportunity. Do not guess column
names.

Run a read_query to find the range of quote dates present and report it. Choose your analysis
window from inside that range and state it.

Scope to quotes I own that are still open or active. For each, report age in days, days until
or past expiry, total value, the account, and the related opportunity stage if there is one.

Group them into: expired, expiring within 14 days, and comfortably open. Within each group,
order by value descending.

Produce an Excel workbook 'quote-aging.xlsx' with a Summary sheet showing count and total value
per group, a Detail sheet with one row per quote, and a Notes sheet listing the tables and
columns used.

Do not modify any data, and do not send anything to any customer. If I have no open quotes, say
so and stop.
