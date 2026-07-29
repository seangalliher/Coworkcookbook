Using the Dynamics 365 Sales plugin, assess the relationship health of the accounts I own.

Use search and describe to confirm the account, contact, opportunity, and activity tables and
the columns for owner, contact role or title, activity dates, and opportunity status. Report
anything you expected but could not find.

Run a read_query to establish the range of activity dates available and report it before using
it. Choose a recency baseline from within that range rather than from today's date, and say what
you chose.

Scope to accounts where I am the owner. Score each account on:
- contact coverage: how many active contacts, and whether more than one has recent engagement
  (a single engaged contact is a single-threading risk)
- engagement recency: how long since any activity on the account
- pipeline presence: whether any opportunity is currently open
- history: won and lost opportunity counts

Combine those into a simple red / amber / green rating, and state the rule you used so I can
challenge it.

Produce an Excel workbook 'account-health.xlsx' with a Summary sheet (counts by rating), a
Detail sheet with one row per account and its component scores, and a Single-Threaded sheet
listing accounts that depend on one contact.

Do not modify any data. If I own no accounts, say so and stop.
